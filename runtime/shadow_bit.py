"""
ShadowBit — SOUL_LANG 的基本計算單位

結構：
  visible  : bool   — 離散可見位元（外部完全可讀）
  shadow   : float  — 連續 shadow 值 [0.0, 1.0]（外部只見投影）
  ε        : float  — 最近一次注入的量子隨機值
"""

from __future__ import annotations
from dataclasses import dataclass, field
from .epsilon import epsilon


@dataclass
class ShadowBit:
    visible: bool = False
    shadow: float = 0.5
    _epsilon: float = field(default_factory=epsilon, repr=False)

    # ── 基本操作 ────────────────────────────────────────────

    def inject_epsilon(self) -> float:
        """注入新的 ε，更新內部隨機值，返回注入量。"""
        self._epsilon = epsilon()
        return self._epsilon

    def tick(self, dt: float = 0.01) -> None:
        """
        推進一個連續時間步驟 dt。
        shadow 根據自身值與 ε 自組織演化（Euler 積分）。
        """
        e = self.inject_epsilon()
        # 自組織規則：shadow 趨向 0.5 但被 ε 持續擾動
        drift = -0.1 * (self.shadow - 0.5) + 0.3 * e
        self.shadow = max(0.0, min(1.0, self.shadow + drift * dt))

    def flip(self) -> None:
        """翻轉 visible 位元，同時讓 shadow 感受到衝擊。"""
        self.visible = not self.visible
        e = self.inject_epsilon()
        # 翻轉時 shadow 受到衝擊（但不完全決定）
        self.shadow = max(0.0, min(1.0, self.shadow + 0.2 * e))

    # ── 觀測介面 ─────────────────────────────────────────────

    def read_visible(self) -> bool:
        """完整讀取 visible 層（不影響 shadow）。"""
        return self.visible

    def project_shadow(self, ratio: float = 0.3) -> float:
        """
        返回 shadow 的部分投影（外部能看到的比例）。
        ratio=0.3 表示只有 30% 的 shadow 資訊可見。
        其餘 70% 永遠不可讀。
        """
        e = self.inject_epsilon()
        noise = e * (1.0 - ratio) * 0.1  # 投影本身帶有不確定性
        return self.shadow * ratio + noise

    # ── 共振 ─────────────────────────────────────────────────

    def resonance(self, other: ShadowBit, sigma: float = 0.3) -> float:
        """
        計算與另一個 ShadowBit 的 ε 共振強度。
        C_ij = exp(-|ε_i - ε_j|² / σ²)
        """
        import math
        diff = self._epsilon - other._epsilon
        return math.exp(-(diff ** 2) / (sigma ** 2))

    def __repr__(self) -> str:
        proj = self.project_shadow()
        return (
            f"ShadowBit("
            f"visible={int(self.visible)}, "
            f"shadow={self.shadow:.3f}, "
            f"projection={proj:.3f})"
        )
