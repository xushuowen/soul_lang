"""
SOUL_LANG Phase 2 驗證實驗
- 軌跡長度: 1000 步（Phase 1: 500）
- 量測次數: 200（Phase 1: 20）
- 多組 SoulCore 設定
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

# Phase 2 改用 os.urandom，避免 NIST Beacon rate limit
# （Phase 1 已確認 NIST quantum ε；Phase 2 分析兩者差異）
import runtime.epsilon as _eps
_eps._USE_QUANTUM = False

from runtime.state import State
from runtime.experiment import VerificationExperiment


def make_soulcore(name: str, r: float, d: float, m: float) -> State:
    s = State(name, use_ode=True)
    s.define_shadow("resonance", r)
    s.define_shadow("depth", d)
    s.define_shadow("memory", m)
    s.define_visible("mood", "calm")
    s.define_visible("active", False)

    def coupling(bits, _dt):
        res = bits["resonance"].shadow
        dep = bits["depth"].shadow
        bits["memory"].shadow = round(0.4 * res + 0.4 * dep + 0.2 * bits["memory"].shadow, 6)

    def visible_rule(bits, visible):
        dep = bits["depth"].shadow
        if dep > 0.65:
            visible["mood"] = "curious"
        elif dep < 0.35:
            visible["mood"] = "calm"
        else:
            visible["mood"] = "uncertain"

    s.coupling_rule = coupling
    s.visible_rule = visible_rule
    return s


CONFIGS = [
    ("SoulCore_A", 0.5, 0.4, 0.3),   # 標準（Phase 1 同設定）
    ("SoulCore_B", 0.8, 0.2, 0.5),   # 高共鳴，低深度
    ("SoulCore_C", 0.3, 0.7, 0.6),   # 低共鳴，高深度
    ("SoulCore_D", 0.5, 0.5, 0.5),   # 中性對稱
]

if __name__ == "__main__":
    print("SOUL_LANG Phase 2 — 開始\n")
    for name, r, d, m in CONFIGS:
        print(f"{'='*55}")
        print(f"設定: {name}  (resonance={r}, depth={d}, memory={m})")
        state = make_soulcore(name, r, d, m)
        exp = VerificationExperiment(state, session_id=f"phase2_{name}")
        # n_steps=200, measure_interval=1 → 200 次量測
        # trajectory_steps=1000 在 measure() 中指定
        exp.run(
            n_steps=200,
            evolve_per_step=50,
            measure_interval=1,
            dt=0.1,
            trajectory_steps=1000,
            verbose=True,
        )
        print(exp.report())

    print("\nPhase 2 完成。結果存於 data/experiment.db")
