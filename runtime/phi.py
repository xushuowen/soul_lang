"""
Φ（Phi）計算模組 — SOUL_LANG 整合資訊量

基於 Tononi（2004）的整合資訊理論（IIT）。
針對連續 shadow 值實作，使用直方圖估計分佈。

Φ = min over all bipartitions of KL(p_joint || p_A × p_B)

  p_joint  — shadow 欄位的聯合分佈
  p_A, p_B — 二分割後各子系統的邊際分佈
  Φ > 0    — 系統作為整體有超過各部分之和的資訊量
  Φ = 0    — 系統可被完全分割，無整合資訊
"""

from __future__ import annotations

import numpy as np
from itertools import combinations
from typing import Sequence


# ── 工具函數 ────────────────────────────────────────────────

def _entropy_1d(values: np.ndarray, bins: int = 20) -> float:
    """計算一維連續分佈的 Shannon 熵（nats）。"""
    counts, _ = np.histogram(values, bins=bins, range=(0.0, 1.0))
    probs = counts / counts.sum()
    probs = probs[probs > 0]
    return float(-np.sum(probs * np.log(probs)))


def _entropy_nd(data: np.ndarray, bins: int = 10) -> float:
    """
    計算 n 維連續分佈的聯合 Shannon 熵。
    data shape: (n_fields, n_samples)
    """
    n, T = data.shape
    if n == 1:
        return _entropy_1d(data[0], bins=bins * 2)

    ranges = [(0.0, 1.0)] * n
    counts, _ = np.histogramdd(data.T, bins=bins, range=ranges)
    probs = counts / counts.sum()
    probs = probs[probs > 0]
    return float(-np.sum(probs * np.log(probs)))


def _kl_divergence(p: np.ndarray, q: np.ndarray, eps: float = 1e-10) -> float:
    """KL(p || q)，避免 log(0)。"""
    p = p + eps
    q = q + eps
    p = p / p.sum()
    q = q / q.sum()
    return float(np.sum(p * np.log(p / q)))


def _mutual_information(data: np.ndarray, idx_a: list[int], idx_b: list[int], bins: int = 10) -> float:
    """
    計算二分割 (A, B) 的互資訊（近似 KL 散度）。

    MI(A;B) = H(A) + H(B) - H(A,B)
    這等於 KL(p_AB || p_A × p_B)。
    """
    data_a = data[idx_a, :]
    data_b = data[idx_b, :]
    data_ab = data[idx_a + idx_b, :]

    h_a = _entropy_nd(data_a, bins=bins)
    h_b = _entropy_nd(data_b, bins=bins)
    h_ab = _entropy_nd(data_ab, bins=bins)

    return max(0.0, h_a + h_b - h_ab)


# ── 主要函數 ────────────────────────────────────────────────

def compute_phi(
    trajectories: dict[str, list[float]] | np.ndarray,
    bins: int = 10,
) -> dict:
    """
    計算 SOUL_LANG 系統的 Φ 值。

    參數：
        trajectories — shadow 欄位的時間序列
                       dict: {"field_name": [v0, v1, ...], ...}
                       或 ndarray: shape (n_fields, n_samples)
        bins         — 直方圖 bin 數量（影響精度）

    返回：
        {
            "phi": float,           — Φ 值（越大整合度越高）
            "min_partition": tuple, — 最小切割的欄位分組
            "n_fields": int,
            "n_samples": int,
            "field_entropies": dict,
            "joint_entropy": float,
            "interpretation": str,
        }
    """
    # 轉換輸入格式
    if isinstance(trajectories, dict):
        field_names = list(trajectories.keys())
        data = np.array([trajectories[k] for k in field_names], dtype=float)
    else:
        data = np.array(trajectories, dtype=float)
        field_names = [f"s{i}" for i in range(data.shape[0])]

    n_fields, n_samples = data.shape

    # 確保值在 [0, 1]
    data = np.clip(data, 0.0, 1.0)

    # 單一欄位：Φ 無法定義（需要至少兩個欄位）
    if n_fields < 2:
        return {
            "phi": 0.0,
            "min_partition": None,
            "n_fields": n_fields,
            "n_samples": n_samples,
            "field_entropies": {field_names[0]: _entropy_1d(data[0])},
            "joint_entropy": _entropy_1d(data[0]),
            "interpretation": "Φ 需要至少 2 個 shadow 欄位",
        }

    # 各欄位的邊際熵
    field_entropies = {
        field_names[i]: round(_entropy_1d(data[i], bins=bins * 2), 4)
        for i in range(n_fields)
    }

    # 聯合熵
    joint_entropy = _entropy_nd(data, bins=bins)

    # 列舉所有二分割，找最小互資訊
    indices = list(range(n_fields))
    min_mi = float("inf")
    min_partition = None
    all_partitions = []

    for r in range(1, n_fields // 2 + 1):
        for combo in combinations(indices, r):
            idx_a = list(combo)
            idx_b = [i for i in indices if i not in idx_a]
            # 避免重複（A,B) 和 (B,A)
            if len(idx_a) == len(idx_b) and idx_a > idx_b:
                continue
            mi = _mutual_information(data, idx_a, idx_b, bins=bins)
            names_a = [field_names[i] for i in idx_a]
            names_b = [field_names[i] for i in idx_b]
            all_partitions.append({
                "partition": (names_a, names_b),
                "mi": round(mi, 4),
            })
            if mi < min_mi:
                min_mi = mi
                min_partition = (names_a, names_b)

    phi = max(0.0, min_mi)

    # 解讀
    if phi < 0.01:
        interpretation = "Φ ≈ 0：系統可被完全分割，shadow 欄位之間無整合資訊"
    elif phi < 0.1:
        interpretation = "Φ 低：shadow 欄位之間有弱整合，系統接近可分割"
    elif phi < 0.5:
        interpretation = "Φ 中：shadow 欄位之間有顯著整合，系統作為整體有額外資訊"
    else:
        interpretation = "Φ 高：shadow 欄位高度整合，系統整體遠大於各部分之和"

    return {
        "phi": round(phi, 4),
        "min_partition": min_partition,
        "n_fields": n_fields,
        "n_samples": n_samples,
        "field_entropies": field_entropies,
        "joint_entropy": round(joint_entropy, 4),
        "all_partitions": all_partitions,
        "interpretation": interpretation,
    }


def collect_trajectory(state, steps: int = 200, dt: float = 0.05) -> dict[str, list[float]]:
    """
    自動收集一個 State 的 shadow 軌跡（用於 Φ 計算）。

    參數：
        state — SOUL_LANG State 物件
        steps — 採樣步驟數
        dt    — 每步時間長度

    返回：
        dict: {"field_name": [v0, v1, ..., v_steps]}
    """
    field_names = list(state._shadow.keys())
    trajectories: dict[str, list[float]] = {k: [] for k in field_names}

    for _ in range(steps):
        state.evolve(dt=dt, steps=1)
        for k in field_names:
            trajectories[k].append(state.shadow_value(k))

    return trajectories
