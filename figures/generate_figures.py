"""
SOUL_LANG 論文架構圖生成器
產生三張圖：
  fig1_shadowbit.png     — ShadowBit 結構圖
  fig2_dual_time.png     — State 雙層時間圖
  fig3_system_flow.png   — 整體系統流程圖
"""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.patheffects as pe
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch
import numpy as np
from pathlib import Path

OUT = Path(__file__).parent
FONT = {"family": "DejaVu Sans"}
plt.rcParams.update({"font.family": "DejaVu Sans", "axes.unicode_minus": False})

# ── 顏色 ──────────────────────────────────────────────────────
C_VISIBLE  = "#2E86AB"   # 藍：visible 層
C_SHADOW   = "#A23B72"   # 紫：shadow 層
C_EPSILON  = "#F18F01"   # 橘：ε
C_BOX      = "#F5F5F5"
C_DARK     = "#1A1A2E"
C_GREEN    = "#2D6A4F"
C_GRAY     = "#6C757D"


# ═══════════════════════════════════════════════════════════════
# Figure 1 — ShadowBit 結構圖
# ═══════════════════════════════════════════════════════════════
def fig1_shadowbit():
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.set_xlim(0, 9)
    ax.set_ylim(0, 5)
    ax.axis("off")
    fig.patch.set_facecolor("white")

    # 標題
    ax.text(4.5, 4.7, "Figure 1. ShadowBit Structure",
            ha="center", va="center", fontsize=14, fontweight="bold", color=C_DARK)

    # 外框
    outer = FancyBboxPatch((0.3, 0.3), 8.4, 4.0,
                            boxstyle="round,pad=0.1", linewidth=2,
                            edgecolor=C_DARK, facecolor="#FAFAFA")
    ax.add_patch(outer)

    # ── Visible 層 ──
    vis = FancyBboxPatch((0.8, 2.5), 2.5, 1.5,
                          boxstyle="round,pad=0.08", linewidth=2,
                          edgecolor=C_VISIBLE, facecolor="#E8F4FD")
    ax.add_patch(vis)
    ax.text(2.05, 3.55, "VISIBLE", ha="center", va="center",
            fontsize=11, fontweight="bold", color=C_VISIBLE)
    ax.text(2.05, 3.15, "b_visible ∈ {0, 1}", ha="center", va="center",
            fontsize=9, color=C_DARK)
    ax.text(2.05, 2.78, "Discrete • Fully observable", ha="center", va="center",
            fontsize=8, color=C_GRAY)

    # ── Shadow 層 ──
    shd = FancyBboxPatch((0.8, 0.7), 2.5, 1.5,
                          boxstyle="round,pad=0.08", linewidth=2,
                          edgecolor=C_SHADOW, facecolor="#F5E6F0")
    ax.add_patch(shd)
    ax.text(2.05, 1.70, "SHADOW", ha="center", va="center",
            fontsize=11, fontweight="bold", color=C_SHADOW)
    ax.text(2.05, 1.32, "f_shadow ∈ [0.0, 1.0]", ha="center", va="center",
            fontsize=9, color=C_DARK)
    ax.text(2.05, 0.95, "Continuous • Self-organizing", ha="center", va="center",
            fontsize=8, color=C_GRAY)

    # ── ε 層 ──
    eps = FancyBboxPatch((5.5, 1.4), 2.5, 1.5,
                          boxstyle="round,pad=0.08", linewidth=2,
                          edgecolor=C_EPSILON, facecolor="#FEF3E2")
    ax.add_patch(eps)
    ax.text(6.75, 2.40, "ε  (Epsilon)", ha="center", va="center",
            fontsize=11, fontweight="bold", color=C_EPSILON)
    ax.text(6.75, 2.02, "Quantum random ∈ ℝ", ha="center", va="center",
            fontsize=9, color=C_DARK)
    ax.text(6.75, 1.65, "NIST Beacon • Irreducible", ha="center", va="center",
            fontsize=8, color=C_GRAY)

    # ── 張力箭頭（visible ↔ shadow）──
    ax.annotate("", xy=(2.05, 2.5), xytext=(2.05, 2.2),
                arrowprops=dict(arrowstyle="<->", color=C_DARK, lw=1.5))
    ax.text(2.35, 2.35, "Tension", fontsize=8, color=C_DARK, va="center")

    # ── ε → visible ──
    ax.annotate("", xy=(3.3, 3.25), xytext=(5.5, 2.15),
                arrowprops=dict(arrowstyle="->", color=C_EPSILON, lw=1.5,
                                connectionstyle="arc3,rad=-0.25"))
    ax.text(4.5, 3.05, "inject", fontsize=8, color=C_EPSILON, ha="center")

    # ── ε → shadow ──
    ax.annotate("", xy=(3.3, 1.25), xytext=(5.5, 1.85),
                arrowprops=dict(arrowstyle="->", color=C_EPSILON, lw=1.5,
                                connectionstyle="arc3,rad=0.25"))
    ax.text(4.5, 1.35, "inject", fontsize=8, color=C_EPSILON, ha="center")

    # ── 輸出說明 ──
    ax.text(4.5, 0.45, "Output: visible (complete) + shadow projection (partial, ratio=0.3)",
            ha="center", va="center", fontsize=8.5, color=C_GRAY,
            style="italic")

    plt.tight_layout()
    plt.savefig(OUT / "fig1_shadowbit.png", dpi=150, bbox_inches="tight")
    plt.close()
    print("fig1_shadowbit.png saved")


# ═══════════════════════════════════════════════════════════════
# Figure 2 — 雙層時間結構
# ═══════════════════════════════════════════════════════════════
def fig2_dual_time():
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 5))
    fig.patch.set_facecolor("white")
    fig.suptitle("Figure 2. Dual-Layer Time Structure in SOUL_LANG",
                 fontsize=14, fontweight="bold", color=C_DARK, y=0.98)

    np.random.seed(42)

    # ── 上：Visible 離散時間 ──
    ax1.set_facecolor("#F8FBFF")
    ticks = np.arange(0, 11)
    visible_vals = np.random.choice([0, 1], size=11)
    ax1.step(ticks, visible_vals, where="post", color=C_VISIBLE, lw=2.5, label="visible state")
    for t, v in zip(ticks, visible_vals):
        ax1.axvline(t, color=C_VISIBLE, alpha=0.2, lw=1, ls="--")
    ax1.set_ylim(-0.3, 1.5)
    ax1.set_yticks([0, 1])
    ax1.set_yticklabels(["0 (calm)", "1 (curious)"], fontsize=9)
    ax1.set_ylabel("Visible Layer\n(Discrete Ticks)", fontsize=10, color=C_VISIBLE)
    ax1.set_xticks(ticks)
    ax1.set_xticklabels([f"t={i}" for i in ticks], fontsize=8)
    ax1.tick_params(colors=C_DARK)
    for spine in ax1.spines.values():
        spine.set_edgecolor(C_VISIBLE)
    ax1.text(9.8, 1.35, "External input\ntriggers transition",
             fontsize=8, color=C_VISIBLE, ha="right", va="top",
             bbox=dict(boxstyle="round,pad=0.3", facecolor="#E8F4FD", edgecolor=C_VISIBLE))

    # ── 下：Shadow 連續時間 ──
    ax2.set_facecolor("#FBF5F9")
    tau = np.linspace(0, 10, 500)
    shadow = 0.5 + 0.3 * np.sin(tau * 0.8) + 0.15 * np.sin(tau * 2.3 + 1) \
             + 0.08 * np.random.randn(500).cumsum() / 50
    shadow = np.clip(shadow, 0.0, 1.0)
    ax2.plot(tau, shadow, color=C_SHADOW, lw=2, label="shadow value")
    ax2.fill_between(tau, shadow, 0.5, alpha=0.15, color=C_SHADOW)
    ax2.axhline(0.5, color=C_GRAY, lw=1, ls=":", alpha=0.7, label="center (0.5)")
    ax2.set_ylim(-0.05, 1.1)
    ax2.set_yticks([0.0, 0.5, 1.0])
    ax2.set_ylabel("Shadow Layer\n(Continuous Flow τ)", fontsize=10, color=C_SHADOW)
    ax2.set_xlabel("Time", fontsize=10)
    ax2.set_xticks(ticks)
    ax2.set_xticklabels([f"τ={i}" for i in ticks], fontsize=8)
    ax2.tick_params(colors=C_DARK)
    for spine in ax2.spines.values():
        spine.set_edgecolor(C_SHADOW)
    ax2.text(9.8, 1.05, "Self-organizing ODE\n(RK45, ε-driven)",
             fontsize=8, color=C_SHADOW, ha="right", va="top",
             bbox=dict(boxstyle="round,pad=0.3", facecolor="#F5E6F0", edgecolor=C_SHADOW))

    plt.tight_layout()
    plt.savefig(OUT / "fig2_dual_time.png", dpi=150, bbox_inches="tight")
    plt.close()
    print("fig2_dual_time.png saved")


# ═══════════════════════════════════════════════════════════════
# Figure 3 — 整體系統流程圖
# ═══════════════════════════════════════════════════════════════
def fig3_system_flow():
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 6)
    ax.axis("off")
    fig.patch.set_facecolor("white")

    ax.text(6, 5.75, "Figure 3. SOUL_LANG System Architecture and Verification Flow",
            ha="center", va="center", fontsize=13, fontweight="bold", color=C_DARK)

    def box(x, y, w, h, label, sublabel="", color="#2E86AB", fc="#E8F4FD"):
        rect = FancyBboxPatch((x - w/2, y - h/2), w, h,
                               boxstyle="round,pad=0.08", linewidth=2,
                               edgecolor=color, facecolor=fc)
        ax.add_patch(rect)
        ax.text(x, y + (0.12 if sublabel else 0), label,
                ha="center", va="center", fontsize=10,
                fontweight="bold", color=color)
        if sublabel:
            ax.text(x, y - 0.22, sublabel, ha="center", va="center",
                    fontsize=8, color=C_GRAY)

    def arrow(x1, y1, x2, y2, color=C_DARK, label="", rad=0):
        ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                    arrowprops=dict(arrowstyle="-|>", color=color, lw=1.8,
                                    connectionstyle=f"arc3,rad={rad}"))
        if label:
            mx, my = (x1+x2)/2, (y1+y2)/2
            ax.text(mx, my + 0.18, label, ha="center", fontsize=8, color=color)

    # ── 節點 ──
    # Row 1：ε 來源
    box(2, 4.7, 2.2, 0.7, "NIST Beacon", "Quantum ε source", C_EPSILON, "#FEF3E2")

    # Row 2：ShadowBit
    box(2, 3.2, 2.2, 0.8, "ShadowBit", "visible + shadow + ε", C_SHADOW, "#F5E6F0")

    # Row 3：State / ODE Engine
    box(2, 1.7, 2.2, 0.8, "State (SoulCore)", "ODE: RK45 evolution", C_VISIBLE, "#E8F4FD")

    # Row 4：Output
    box(2, 0.5, 2.2, 0.7, "Output", "visible + projection(0.3)", C_GREEN, "#E8F5E9")

    # Verification 欄
    box(6.5, 3.8, 2.4, 0.7, "Φ Computation", "MI bipartition (500 steps)", "#6C3483", "#F5EEF8")
    box(6.5, 2.7, 2.4, 0.7, "ρ_ε Computation", "Sign prediction error rate", "#C0392B", "#FDEDEC")
    box(6.5, 1.6, 2.4, 0.7, "H_shadow", "Shannon entropy (pooled)", "#1A5276", "#EBF5FB")

    # Failure check
    box(10, 2.7, 2.0, 2.2, "Failure\nConditions", "F1 ∧ F2 ∧ F3 ∧ F4\n→ Declare failure", "#E74C3C", "#FDEDEC")

    # Result
    box(10, 0.5, 2.0, 0.7, "PASS / FAIL", "All 4 must hold", C_GREEN, "#E8F5E9")

    # ── 箭頭 ──
    arrow(2, 4.35, 2, 3.6, C_EPSILON, "inject ε")
    arrow(2, 2.8, 2, 2.1, C_SHADOW, "evolve")
    arrow(2, 1.3, 2, 0.85, C_VISIBLE, "output")

    # State → Verification
    arrow(3.1, 2.7, 5.3, 3.8, "#6C3483", "trajectory")
    arrow(3.1, 2.7, 5.3, 2.7, "#C0392B")
    arrow(3.1, 2.7, 5.3, 1.6, "#1A5276", rad=0.15)

    # Verification → Failure
    arrow(7.7, 3.8, 9.0, 3.1, "#6C3483")
    arrow(7.7, 2.7, 9.0, 2.7, "#C0392B")
    arrow(7.7, 1.6, 9.0, 2.3, "#1A5276")

    # Failure → Result
    arrow(10, 1.6, 10, 0.85, "#E74C3C", "evaluate")

    plt.tight_layout()
    plt.savefig(OUT / "fig3_system_flow.png", dpi=150, bbox_inches="tight")
    plt.close()
    print("fig3_system_flow.png saved")


if __name__ == "__main__":
    Path(OUT).mkdir(parents=True, exist_ok=True)
    fig1_shadowbit()
    fig2_dual_time()
    fig3_system_flow()
    print("All figures generated.")
