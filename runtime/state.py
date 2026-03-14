"""
State — SOUL_LANG 的基本語意單位

每個 State 包含：
  - visible 層：命名欄位，離散值，外部完全可讀
  - shadow 層：命名欄位，連續 ShadowBit，外部只見投影
  - evolve()：shadow 層的自組織規則
  - on_input()：外部輸入處理
"""

from __future__ import annotations
from typing import Any, Callable
from .shadow_bit import ShadowBit
from .epsilon import epsilon
from .shadow_engine import ShadowEngine


class State:
    def __init__(self, name: str, use_ode: bool = True):
        self.name = name
        self._visible: dict[str, Any] = {}
        self._shadow: dict[str, ShadowBit] = {}
        self._evolve_rules: list[Callable] = []
        self._input_handlers: list[Callable] = []
        self._tick_count = 0       # 離散時間
        self._flow_time = 0.0      # 連續時間
        self._use_ode = use_ode
        self._engine: ShadowEngine | None = None  # 初始化後建立

    # ── 定義介面 ─────────────────────────────────────────────

    def define_visible(self, name: str, initial: Any) -> None:
        """定義一個 visible 欄位。"""
        self._visible[name] = initial

    def define_shadow(self, name: str, initial: float = 0.5) -> None:
        """定義一個 shadow 欄位（ShadowBit）。"""
        self._shadow[name] = ShadowBit(shadow=initial)
        # 重建 ODE 引擎（欄位數變了）
        if self._use_ode:
            n = len(self._shadow)
            y0 = [b.shadow for b in self._shadow.values()]
            self._engine = ShadowEngine(n_fields=n)
            self._engine.reset(y0)

    def add_evolve_rule(self, rule: Callable) -> None:
        """加入一條 shadow 自組織規則（在 evolve() 時執行）。"""
        self._evolve_rules.append(rule)

    def add_input_handler(self, handler: Callable) -> None:
        """加入一條外部輸入處理規則。"""
        self._input_handlers.append(handler)

    # ── 運行介面 ─────────────────────────────────────────────

    def evolve(self, dt: float = 0.01, steps: int = 10) -> None:
        """
        推進連續時間 steps 步（每步 dt）。
        使用 SciPy ODE solver 演化 shadow 層（Phase 1c）。
        """
        duration = dt * steps
        keys = list(self._shadow.keys())

        if self._use_ode and self._engine and keys:
            y0 = [self._shadow[k].shadow for k in keys]
            _, y_end = self._engine.evolve(y0=y0, duration=duration)
            for k, val in zip(keys, y_end):
                self._shadow[k].shadow = val
                self._shadow[k].inject_epsilon()
        else:
            # 備用：Euler 積分
            for _ in range(steps):
                for bit in self._shadow.values():
                    bit.tick(dt)

        # 自訂規則
        for rule in self._evolve_rules:
            rule(self, dt)
        self._flow_time += duration

    def on_input(self, stimulus: Any) -> None:
        """
        處理外部輸入，推進離散時間一步。
        """
        self._tick_count += 1
        for handler in self._input_handlers:
            handler(self, stimulus)
        # 輸入後也觸發一次 shadow 演化
        self.evolve(dt=0.01, steps=5)

    # ── 讀取介面 ─────────────────────────────────────────────

    def read_visible(self, name: str) -> Any:
        """完整讀取 visible 欄位。"""
        return self._visible.get(name)

    def write_visible(self, name: str, value: Any) -> None:
        """寫入 visible 欄位。"""
        self._visible[name] = value

    def read_shadow_projection(self, name: str, ratio: float = 0.3) -> float:
        """讀取 shadow 欄位的部分投影。"""
        bit = self._shadow.get(name)
        if bit is None:
            return 0.0
        return bit.project_shadow(ratio)

    def shadow_value(self, name: str) -> float:
        """直接讀取 shadow 的完整值（僅限系統內部使用）。"""
        bit = self._shadow.get(name)
        return bit.shadow if bit else 0.0

    def inject_epsilon_to_shadow(self, name: str, weight: float = 0.1) -> None:
        """手動向指定 shadow 欄位注入 ε。"""
        bit = self._shadow.get(name)
        if bit:
            e = epsilon()
            bit.shadow = max(0.0, min(1.0, bit.shadow + e * weight))
            bit._epsilon = e

    # ── 輸出 ─────────────────────────────────────────────────

    def output(self, shadow_projection_ratio: float = 0.3) -> dict:
        """
        輸出系統狀態：
          visible 完整輸出 + shadow 部分投影
        """
        result = {
            "tick": self._tick_count,
            "flow_time": round(self._flow_time, 4),
            "visible": dict(self._visible),
            "shadow_projection": {
                name: round(bit.project_shadow(shadow_projection_ratio), 4)
                for name, bit in self._shadow.items()
            },
        }
        return result

    def __repr__(self) -> str:
        return (
            f"State({self.name!r}, "
            f"tick={self._tick_count}, "
            f"visible={self._visible}, "
            f"shadow_keys={list(self._shadow.keys())})"
        )
