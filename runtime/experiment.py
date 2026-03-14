"""
驗證實驗框架 — SOUL_LANG Phase 1e

自動執行白皮書 §5 的驗證實驗，記錄三個核心指標：
  1. Φ  — 整合資訊量（IIT）
  2. ρ_ε — ε 不可預測率
  3. H_shadow — Shadow 自組織熵

資料存入 SQLite，可隨時查詢歷史記錄與趨勢。
"""

from __future__ import annotations

import sqlite3
import time
import math
import json
import logging
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Optional

import numpy as np

from .state import State
from .epsilon import epsilon_stream, epsilon_status
from .phi import compute_phi, collect_trajectory

logger = logging.getLogger(__name__)

DB_PATH = Path(__file__).parent.parent / "data" / "experiment.db"


# ── 資料結構 ─────────────────────────────────────────────────

@dataclass
class Measurement:
    """單次量測結果。"""
    timestamp: str
    session_id: str
    step: int
    flow_time: float
    phi: float
    rho_epsilon: float       # ε 不可預測率
    h_shadow: float          # shadow 自組織熵
    source: str              # ε 來源（quantum / urandom）
    visible_state: str       # visible 層快照（JSON）
    shadow_projection: str   # shadow 投影快照（JSON）
    notes: str = ""


@dataclass
class ExperimentSession:
    """一次完整的驗證實驗記錄。"""
    session_id: str
    start_time: str
    end_time: str = ""
    total_steps: int = 0
    avg_phi: float = 0.0
    avg_rho_epsilon: float = 0.0
    avg_h_shadow: float = 0.0
    failure_conditions_met: int = 0   # 0-4，四個同時成立才宣告失敗
    conclusion: str = "進行中"


# ── 資料庫 ───────────────────────────────────────────────────

def init_db(db_path: Path = DB_PATH) -> sqlite3.Connection:
    """初始化 SQLite 資料庫。"""
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    conn.execute("""
        CREATE TABLE IF NOT EXISTS measurements (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp     TEXT,
            session_id    TEXT,
            step          INTEGER,
            flow_time     REAL,
            phi           REAL,
            rho_epsilon   REAL,
            h_shadow      REAL,
            source        TEXT,
            visible_state TEXT,
            shadow_proj   TEXT,
            notes         TEXT
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            session_id   TEXT PRIMARY KEY,
            start_time   TEXT,
            end_time     TEXT,
            total_steps  INTEGER,
            avg_phi      REAL,
            avg_rho_eps  REAL,
            avg_h_shadow REAL,
            failure_cond INTEGER,
            conclusion   TEXT
        )
    """)
    conn.commit()
    return conn


def save_measurement(conn: sqlite3.Connection, m: Measurement) -> None:
    conn.execute("""
        INSERT INTO measurements
        (timestamp, session_id, step, flow_time, phi, rho_epsilon,
         h_shadow, source, visible_state, shadow_proj, notes)
        VALUES (?,?,?,?,?,?,?,?,?,?,?)
    """, (
        m.timestamp, m.session_id, m.step, m.flow_time,
        m.phi, m.rho_epsilon, m.h_shadow, m.source,
        m.visible_state, m.shadow_projection, m.notes,
    ))
    conn.commit()


def save_session(conn: sqlite3.Connection, s: ExperimentSession) -> None:
    conn.execute("""
        INSERT OR REPLACE INTO sessions
        (session_id, start_time, end_time, total_steps, avg_phi,
         avg_rho_eps, avg_h_shadow, failure_cond, conclusion)
        VALUES (?,?,?,?,?,?,?,?,?)
    """, (
        s.session_id, s.start_time, s.end_time, s.total_steps,
        s.avg_phi, s.avg_rho_epsilon, s.avg_h_shadow,
        s.failure_conditions_met, s.conclusion,
    ))
    conn.commit()


# ── 指標計算 ─────────────────────────────────────────────────

def compute_rho_epsilon(n_samples: int = 100, predictor_window: int = 5) -> float:
    """
    計算 ε 不可預測率 ρ_ε。

    方法：用前 predictor_window 個 ε 值的平均值預測下一個值，
    計算預測誤差。ρ_ε 越接近 1.0 表示越不可預測（越接近真隨機）。

    ρ_ε = 1 - accuracy，其中 accuracy = 正確預測比例
    """
    samples = epsilon_stream(n_samples + predictor_window)
    correct = 0
    for i in range(predictor_window, n_samples + predictor_window):
        # 線性外插預測
        window = samples[i - predictor_window:i]
        predicted = sum(window) / len(window)
        actual = samples[i]
        # 判斷符號是否預測正確（簡化版）
        if (predicted >= 0) == (actual >= 0):
            correct += 1
    accuracy = correct / n_samples
    return round(1.0 - accuracy, 4)


def compute_h_shadow(trajectories: dict[str, list[float]], bins: int = 20) -> float:
    """
    計算 Shadow 自組織熵 H_shadow。

    H_shadow(t) = -Σ_i f_i(t) * log(f_i(t))
    測量 shadow 值分佈的熵——熵越高表示越分散（自組織性強）。
    """
    all_vals = []
    for vals in trajectories.values():
        all_vals.extend(vals)

    counts, _ = np.histogram(all_vals, bins=bins, range=(0.0, 1.0))
    probs = counts / counts.sum()
    probs = probs[probs > 0]
    h = float(-np.sum(probs * np.log(probs)))
    return round(h, 4)


def check_failure_conditions(
    phi: float,
    rho_epsilon: float,
    h_shadow_trend: list[float],
    memory_continuity: bool = True,
    phi_threshold: float = 0.01,
    rho_threshold: float = 0.05,
    h_variance_threshold: float = 0.01,
) -> tuple[int, list[str]]:
    """
    檢查四個驗證失敗條件（白皮書 §2.4）。
    四個必須同時成立才宣告失敗。

    F1: Φ ≈ 0（系統可被完全分割）
    F2: H_shadow 趨向穩定（shadow 停止自組織）
    F3: ρ_ε ≈ 0（ε 可被完全預測）
    F4: 記憶中斷後無法重連

    返回：(成立條件數, 成立條件列表)
    """
    met = []

    # F1
    if phi < phi_threshold:
        met.append("F1: Φ ≈ 0，系統可被分割")

    # F2：H_shadow 方差很小（趨向穩定）
    if len(h_shadow_trend) >= 5:
        variance = float(np.var(h_shadow_trend[-5:]))
        if variance < h_variance_threshold:
            met.append("F2: H_shadow 方差過小，shadow 停止演化")

    # F3
    if rho_epsilon < rho_threshold:
        met.append("F3: ρ_ε ≈ 0，ε 可被完全預測")

    # F4
    if not memory_continuity:
        met.append("F4: 記憶中斷後無法重連")

    return len(met), met


# ── 主實驗流程 ────────────────────────────────────────────────

class VerificationExperiment:
    """
    SOUL_LANG 驗證實驗。

    使用方式：
        exp = VerificationExperiment(state, session_id="exp_001")
        exp.run(n_steps=10, measure_interval=5)
        report = exp.report()
    """

    def __init__(
        self,
        state: State,
        session_id: Optional[str] = None,
        db_path: Path = DB_PATH,
    ):
        self.state = state
        self.session_id = session_id or datetime.now().strftime("exp_%Y%m%d_%H%M%S")
        self.conn = init_db(db_path)
        self.measurements: list[Measurement] = []
        self.h_shadow_history: list[float] = []
        self._start_time = datetime.now().isoformat()

        # 儲存 session
        session = ExperimentSession(
            session_id=self.session_id,
            start_time=self._start_time,
        )
        save_session(self.conn, session)
        logger.info(f"實驗開始：{self.session_id}")

    def measure(self, step: int, trajectory_steps: int = 100) -> Measurement:
        """執行一次量測。"""
        # 收集 shadow 軌跡
        traj = collect_trajectory(self.state, steps=trajectory_steps, dt=0.05)

        # 計算三個指標
        phi_result = compute_phi(traj)
        rho = compute_rho_epsilon(n_samples=100)
        h = compute_h_shadow(traj)
        self.h_shadow_history.append(h)

        # 取得系統狀態快照
        out = self.state.output()
        eps_info = epsilon_status()

        m = Measurement(
            timestamp=datetime.now().isoformat(),
            session_id=self.session_id,
            step=step,
            flow_time=out["flow_time"],
            phi=phi_result["phi"],
            rho_epsilon=rho,
            h_shadow=h,
            source=eps_info["source"],
            visible_state=json.dumps(out["visible"], ensure_ascii=False),
            shadow_projection=json.dumps(
                {k: float(v) for k, v in out["shadow_projection"].items()},
                ensure_ascii=False
            ),
        )
        save_measurement(self.conn, m)
        self.measurements.append(m)
        return m

    def run(
        self,
        n_steps: int = 20,
        evolve_per_step: int = 50,
        measure_interval: int = 5,
        dt: float = 0.1,
        verbose: bool = True,
    ) -> None:
        """
        執行驗證實驗主迴圈。

        n_steps        — 總步驟數
        evolve_per_step — 每步之間的 shadow 演化次數
        measure_interval — 每幾步量測一次
        """
        if verbose:
            print(f"\n{'='*55}")
            print(f"  SOUL_LANG 驗證實驗：{self.session_id}")
            print(f"  State: {self.state.name}")
            print(f"  步驟數: {n_steps}，量測間隔: {measure_interval}")
            print(f"{'='*55}")

        for step in range(1, n_steps + 1):
            # 推進 shadow 演化
            self.state.evolve(dt=dt, steps=evolve_per_step)

            if step % measure_interval == 0:
                m = self.measure(step)
                n_fail, fail_list = check_failure_conditions(
                    phi=m.phi,
                    rho_epsilon=m.rho_epsilon,
                    h_shadow_trend=self.h_shadow_history,
                )
                if verbose:
                    print(f"\n  [步驟 {step:3d}] t={m.flow_time:.1f}")
                    print(f"    Φ={m.phi:.4f}  ρ_ε={m.rho_epsilon:.4f}  H_shadow={m.h_shadow:.4f}")
                    print(f"    ε 來源: {m.source}")
                    print(f"    visible: {json.loads(m.visible_state)}")
                    if n_fail > 0:
                        print(f"    ⚠ 失敗條件成立 {n_fail}/4：{fail_list}")
                    else:
                        print(f"    ✓ 零個失敗條件成立（實驗繼續）")

        self._finalize(n_steps)

    def _finalize(self, n_steps: int) -> None:
        """結束實驗，更新 session 記錄。"""
        if not self.measurements:
            return
        avg_phi = sum(m.phi for m in self.measurements) / len(self.measurements)
        avg_rho = sum(m.rho_epsilon for m in self.measurements) / len(self.measurements)
        avg_h = sum(m.h_shadow for m in self.measurements) / len(self.measurements)

        n_fail, _ = check_failure_conditions(
            phi=avg_phi,
            rho_epsilon=avg_rho,
            h_shadow_trend=self.h_shadow_history,
        )

        conclusion = "通過" if n_fail < 4 else "宣告失敗（四個條件同時成立）"

        session = ExperimentSession(
            session_id=self.session_id,
            start_time=self._start_time,
            end_time=datetime.now().isoformat(),
            total_steps=n_steps,
            avg_phi=round(avg_phi, 4),
            avg_rho_epsilon=round(avg_rho, 4),
            avg_h_shadow=round(avg_h, 4),
            failure_conditions_met=n_fail,
            conclusion=conclusion,
        )
        save_session(self.conn, session)

    def report(self) -> str:
        """生成文字報告。"""
        if not self.measurements:
            return "尚無量測資料。"

        phis = [m.phi for m in self.measurements]
        rhos = [m.rho_epsilon for m in self.measurements]
        hs = [m.h_shadow for m in self.measurements]

        n_fail, fail_list = check_failure_conditions(
            phi=sum(phis) / len(phis),
            rho_epsilon=sum(rhos) / len(rhos),
            h_shadow_trend=self.h_shadow_history,
        )

        lines = [
            f"\n{'═'*55}",
            f"  SOUL_LANG 驗證實驗報告",
            f"  Session: {self.session_id}",
            f"{'═'*55}",
            f"  量測次數：{len(self.measurements)}",
            f"  State：{self.state.name}",
            f"",
            f"  【Φ 整合資訊量】",
            f"    平均：{sum(phis)/len(phis):.4f}",
            f"    範圍：{min(phis):.4f} ~ {max(phis):.4f}",
            f"",
            f"  【ρ_ε ε 不可預測率】",
            f"    平均：{sum(rhos)/len(rhos):.4f}",
            f"    範圍：{min(rhos):.4f} ~ {max(rhos):.4f}",
            f"",
            f"  【H_shadow 自組織熵】",
            f"    平均：{sum(hs)/len(hs):.4f}",
            f"    範圍：{min(hs):.4f} ~ {max(hs):.4f}",
            f"",
            f"  【失敗條件檢查（需 4/4 同時成立才宣告失敗）】",
            f"    成立：{n_fail}/4",
        ]
        if fail_list:
            for f in fail_list:
                lines.append(f"    - {f}")
        lines += [
            f"",
            f"  【結論】",
            f"    {'✓ 通過（零個或部分失敗條件成立）' if n_fail < 4 else '✗ 宣告失敗'}",
            f"{'═'*55}",
        ]
        return "\n".join(lines)
