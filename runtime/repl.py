"""
SOUL_LANG REPL — Phase 1a 互動介面

用法：
    python -m soul_lang.runtime.repl
"""

from __future__ import annotations
from .state import State
from .shadow_bit import ShadowBit
from .epsilon import epsilon, epsilon_stream


BANNER = """
╔══════════════════════════════════════════╗
║         S O U L _ L A N G               ║
║    Phase 1a Runtime — Interactive REPL  ║
║    © 2026 許碩文 (Shuo-Wen Hsu)          ║
╚══════════════════════════════════════════╝

內建物件：
  ε()            — 產生一個量子隨機值 [-1, 1]
  ShadowBit()    — 建立一個 ShadowBit
  State("name")  — 建立一個 State

輸入 'demo' 執行示範，'exit' 離開。
"""

DEMO_CODE = '''
# ── SOUL_LANG Phase 1a 示範 ──────────────────────────

# 1. 建立一個 ShadowBit
bit = ShadowBit(visible=False, shadow=0.5)
print("初始 ShadowBit：", bit)

# 2. 推進 5 個連續時間步驟，觀察 shadow 自組織
print("\\n連續演化 5 步：")
for i in range(5):
    bit.tick(dt=0.1)
    print(f"  步驟 {i+1}: shadow={bit.shadow:.4f}, projection={bit.project_shadow():.4f}")

# 3. 建立一個 State（情緒核心示範）
core = State("EmotionalCore")
core.define_visible("active", False)
core.define_visible("mood", "calm")
core.define_shadow("resonance", initial=0.5)
core.define_shadow("depth", initial=0.3)

# 自訂 shadow 演化規則
def mood_evolve(state, dt):
    depth = state.shadow_value("depth")
    if depth > 0.7:
        state.write_visible("mood", "curious")
    elif depth < 0.3:
        state.write_visible("mood", "calm")
    else:
        state.write_visible("mood", "uncertain")

core.add_evolve_rule(mood_evolve)

# 4. 送入外部輸入
print("\\n處理外部輸入 'hello'：")
core.on_input("hello")
print(core.output())

print("\\n自由演化 50 步：")
core.evolve(dt=0.05, steps=50)
print(core.output())

# 5. ε 共振示範
print("\\n兩個 ShadowBit 的共振強度：")
bit_a = ShadowBit(shadow=0.4)
bit_b = ShadowBit(shadow=0.6)
bit_a.inject_epsilon()
bit_b.inject_epsilon()
print(f"  bit_a ε={bit_a._epsilon:.4f}, bit_b ε={bit_b._epsilon:.4f}")
print(f"  共振強度 C_ab = {bit_a.resonance(bit_b):.4f}")
'''


def run_repl():
    local_ns = {
        "epsilon": epsilon,
        "epsilon_stream": epsilon_stream,
        "ShadowBit": ShadowBit,
        "State": State,
    }

    print(BANNER)

    while True:
        try:
            line = input("soul> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n離開 SOUL_LANG REPL。")
            break

        if not line:
            continue
        if line in ("exit", "quit", "q"):
            print("離開 SOUL_LANG REPL。")
            break
        if line == "demo":
            exec(DEMO_CODE, local_ns)
            continue

        try:
            # 先嘗試 eval（表達式）
            result = eval(line, local_ns)
            if result is not None:
                print(repr(result))
        except SyntaxError:
            # 嘗試 exec（語句）
            try:
                exec(line, local_ns)
            except Exception as e:
                print(f"錯誤：{e}")
        except Exception as e:
            print(f"錯誤：{e}")


if __name__ == "__main__":
    run_repl()
