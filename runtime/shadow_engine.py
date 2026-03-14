"""
ShadowEngine — SOUL_LANG Shadow 層連續演化引擎

Phase 1c：使用 SciPy solve_ivp 取代 Euler 積分。

Shadow 演化方程（白皮書 §3.2）：

  dS_i/dt = -α(S_i - 0.5) + β·ε_i(t) + γ·Σ_j C_ij·(S_j - S_i)

  其中：
    S_i    — 第 i 個 shadow 欄位的值 [0, 1]
    α      — 回歸中心係數（自組織穩定性）
    β      — ε 注入強度
    ε_i(t) — 量子隨機噪聲（離散步驟插值）
    γ      — 欄位間耦合強度
    C_ij   — 欄位 i 與 j 的共振係數
"""

from __future__ import annotations

import numpy as np
from scipy.integrate import solve_ivp
from typing import Callable

from .epsilon import epsilon_stream


class ShadowEngine:
    """
    多欄位 Shadow 層的連續 ODE 演化引擎。

    使用方式：
        engine = ShadowEngine(n_fields=3)
        t_end, y_end = engine.evolve(y0=[0.5, 0.3, 0.7], duration=1.0)
    """

    def __init__(
        self,
        n_fields: int = 1,
        alpha: float = 0.1,   # 回歸中心強度
        beta: float = 0.3,    # ε 注入強度
        gamma: float = 0.05,  # 欄位間耦合強度
    ):
        self.n_fields = n_fields
        self.alpha = alpha
        self.beta = beta
        self.gamma = gamma
        self._last_t = 0.0
        self._last_y: list[float] = [0.5] * n_fields

    def _build_ode(
        self, epsilon_values: np.ndarray, t_span: tuple[float, float]
    ) -> Callable:
        """
        建立 ODE 函數。
        epsilon_values: shape (n_fields, n_samples) — 預先取好的 ε 序列
        使用線性插值模擬連續的 ε(t)。
        """
        t0, t1 = t_span
        n_samples = epsilon_values.shape[1]
        t_samples = np.linspace(t0, t1, n_samples)
        alpha, beta, gamma = self.alpha, self.beta, self.gamma
        n = self.n_fields

        def ode(t: float, y: np.ndarray) -> np.ndarray:
            dy = np.zeros(n)
            for i in range(n):
                # ε 插值（線性）
                eps_i = float(np.interp(t, t_samples, epsilon_values[i]))

                # 自組織回歸項
                drift = -alpha * (y[i] - 0.5)

                # ε 注入
                noise = beta * eps_i

                # 欄位間耦合（共振）
                coupling = 0.0
                for j in range(n):
                    if i != j:
                        diff_eps = epsilon_values[i, -1] - epsilon_values[j, -1]
                        c_ij = np.exp(-(diff_eps ** 2) / 0.09)  # σ=0.3
                        coupling += gamma * c_ij * (y[j] - y[i])

                dy[i] = drift + noise + coupling

            return dy

        return ode

    def evolve(
        self,
        y0: list[float] | None = None,
        duration: float = 1.0,
        n_epsilon_samples: int = 50,
        method: str = "RK45",
    ) -> tuple[float, list[float]]:
        """
        演化 shadow 層 duration 秒。

        參數：
            y0        — 初始 shadow 值（None 使用上次結束的值）
            duration  — 演化時間長度（連續時間單位）
            n_epsilon_samples — 期間使用幾個 ε 採樣點
            method    — ODE 求解方法（RK45, DOP853, Radau）

        返回：
            (t_end, y_end) — 結束時刻與 shadow 值列表
        """
        if y0 is None:
            y0 = self._last_y
        y0 = np.clip(y0, 0.0, 1.0)

        t0 = self._last_t
        t1 = t0 + duration
        t_span = (t0, t1)

        # 預取量子 ε 序列
        total_samples = self.n_fields * n_epsilon_samples
        eps_flat = epsilon_stream(total_samples)
        epsilon_values = np.array(eps_flat).reshape(self.n_fields, n_epsilon_samples)

        ode_func = self._build_ode(epsilon_values, t_span)

        sol = solve_ivp(
            ode_func,
            t_span,
            y0,
            method=method,
            dense_output=False,
            max_step=duration / 10,
        )

        if not sol.success:
            # 如果 ODE 失敗，退回手動 Euler
            y_end = list(y0)
            for i in range(self.n_fields):
                e = eps_flat[i]
                y_end[i] = float(np.clip(
                    y0[i] - self.alpha * (y0[i] - 0.5) * duration + self.beta * e * duration,
                    0.0, 1.0
                ))
        else:
            y_end = list(np.clip(sol.y[:, -1], 0.0, 1.0))

        self._last_t = t1
        self._last_y = y_end
        return t1, y_end

    def evolve_trajectory(
        self,
        y0: list[float] | None = None,
        duration: float = 1.0,
        n_points: int = 100,
    ) -> tuple[np.ndarray, np.ndarray]:
        """
        返回完整演化軌跡（用於視覺化和驗證實驗）。

        返回：
            (t_array, y_array) — 時間序列與對應 shadow 值矩陣
            y_array shape: (n_fields, n_points)
        """
        if y0 is None:
            y0 = self._last_y
        y0 = np.clip(y0, 0.0, 1.0)

        t0 = self._last_t
        t1 = t0 + duration
        t_span = (t0, t1)
        t_eval = np.linspace(t0, t1, n_points)

        eps_flat = epsilon_stream(self.n_fields * n_points)
        epsilon_values = np.array(eps_flat).reshape(self.n_fields, n_points)

        ode_func = self._build_ode(epsilon_values, t_span)

        sol = solve_ivp(
            ode_func,
            t_span,
            y0,
            method="RK45",
            t_eval=t_eval,
            dense_output=False,
        )

        self._last_t = t1
        if sol.success:
            y_clipped = np.clip(sol.y, 0.0, 1.0)
            self._last_y = list(y_clipped[:, -1])
            return sol.t, y_clipped
        else:
            # 備用：返回平坦軌跡
            t_arr = t_eval
            y_arr = np.tile(np.array(y0).reshape(-1, 1), (1, n_points))
            return t_arr, y_arr

    def reset(self, y0: list[float] | None = None) -> None:
        """重置引擎狀態。"""
        self._last_t = 0.0
        self._last_y = y0 if y0 is not None else [0.5] * self.n_fields
