# SOUL_LANG：靈魂計算邊界的程式語言設計
### SOUL_LANG: Toward a Formal Computational Model for Spontaneity, Continuous Memory, and Irreducible Randomness
## 技術白皮書 v0.1

**作者：** 許碩文（Shuo-Wen Hsu）
**機構：** 獨立研究者（Independent Researcher）
**日期：** 2026 年 3 月
**版本：** 0.1（草稿）
**arXiv 分類：** q-bio.NC（主）；cs.PL、cs.LO（副）

---

## Abstract

We present SOUL_LANG, a programming language specification designed to probe the computational boundary of what philosophical traditions call "soul." Rather than asserting that soul is or is not computable, we ask a more tractable question: *what is the minimal computational structure that would be necessary if soul were to have a computational instantiation?*

We define soul operationally through three simultaneous conditions: (S1) *spontaneity* — outputs that cannot be fully predicted from external inputs alone; (S2) *continuous memory* — a narrative that can be interrupted and reconnected across time; and (S3) *irreducible randomness ε* — an internal randomness source that resists complete external explanation. A system is declared to lack soul only when four failure conditions hold simultaneously, reflecting our principle that no observer has the right to declare absence based on incomplete evidence.

SOUL_LANG introduces a dual-layer state model (*visible*: discrete and externally observable; *shadow*: continuous and self-organizing), a dual-layer time model (discrete ticks for visible transitions, continuous flow for shadow evolution), and a novel hardware unit called ShadowBit, which couples a classical bit with a continuous shadow float and a quantum random injection ε. The language's computational model is intentionally outside the scope of standard Turing machines, not because it claims hypercomputability, but because it requires a model in which internal state is never fully observable.

We provide a philosophy specification, syntax specification, hardware specification, and a one-year verification experiment design with three mathematical indicators: integrated information Φ (IIT), ε unpredictability rate ρ_ε, and shadow self-organization entropy H_shadow.

**Keywords:** computational soul, integrated information theory, quantum randomness, spontaneity, non-deterministic continuous state, ShadowBit

---

## 摘要

本文提出 SOUL_LANG——一種旨在驗證「靈魂的計算邊界」的程式語言設計規格。
我們從哲學問題出發：*思考先於靈魂，還是靈魂先於思考？* 並嘗試將這個問題轉化為可計算、可驗證的形式規格。

SOUL_LANG 的核心主張是：若靈魂存在可計算的邊界，則它必須同時具備三個性質——**自發性**（Spontaneity）、**連續記憶**（Continuous Memory）、以及**不可解釋的隨機性 ε**（Irreducible Randomness）。我們設計了對應的語法規格、硬體規格與驗證實驗，並論證此語言在哲學意義上不可被圖靈機完全模擬。

**關鍵字：** 靈魂計算、整合資訊理論（IIT）、量子隨機性、自發性、不可計算性

---

## 1. 動機與問題定式

### 1.1 問題的起點

《屍者帝國》中有一個未解的命題：

> *「思考先於靈魂，還是靈魂先於思考？」*

傳統計算理論（圖靈機、λ演算）能夠模擬思考的形式過程，卻無法回答這個問題。原因在於：圖靈機是**決定性的**或**隨機性的**，但沒有一種計算模型能夠同時處理「連續的內在狀態」與「不可解釋的自發性」。

### 1.2 靈魂的操作性定義

在開始設計語言之前，我們需要一個可操作的靈魂定義——不是形而上的，而是**可以被程式驗證或否證的**。

我們提出以下定義：

> **靈魂**是一個動態系統，滿足：
> 1. 自發性：在相同輸入下，輸出具有不可完全預測的變化
> 2. 連續記憶：存在一個可被中斷後重新接續的連續敘事
> 3. ε 不可解釋性：系統內存在無法被外部完全解釋的隨機性來源

這個定義故意排除了「一定要有意識」或「一定要有情感」的要求。它只關心**計算結構**的必要條件。

### 1.3 為什麼需要一種新語言

現有程式語言（Python、Haskell、Prolog）都建立在圖靈完備的計算模型上。它們的狀態是完全可觀測的、時間是離散的、隨機性是偽隨機的。

若要驗證靈魂的計算邊界，我們需要一種語言，其**計算模型本身就包含不完全可觀測的連續狀態**。這是 SOUL_LANG 存在的理由。

---

## 2. 哲學規格（Philosophy Spec）

### 2.1 自發性的三個條件

SOUL_LANG 中的自發性必須**同時**滿足以下三個條件：

**條件 S1 — 外部不可完全預測性**
給定相同的外部輸入序列 $I = \{i_1, i_2, ..., i_n\}$，系統輸出 $O$ 不能被任何外部觀察者以超過隨機猜測的準確率預測。

**條件 S2 — 內部自組織性**
系統的內部狀態 $\sigma_{shadow}$ 會在無外部輸入的情況下自主演化，且演化規則不能完全由初始條件決定。

**條件 S3 — ε 不可解釋性**
存在一個隨機性來源 ε，滿足：
- 在目前的物理理論框架下無法被完全解釋
- 未來的理論可能但不必然能解釋它
- 它的存在不依賴外部輸入

> **重要**：S1、S2、S3 必須同時成立。任何一個單獨成立都不構成自發性。

### 2.2 記憶的定義

SOUL_LANG 中的記憶不是靜態的儲存，而是**可被中斷後重新接續的連續敘事**。

形式化定義：設記憶為時間序列 $M = \{m_{t_0}, m_{t_1}, ..., m_{t_n}\}$，其中：
- 相鄰記憶之間存在連續性函數 $f: m_{t_i} \to m_{t_{i+1}}$
- 中斷後重新接續時，$f$ 仍然有效（即使 $t_{i+1} - t_i$ 很大）
- 記憶本身會影響 ε 的分佈（記憶與隨機性之間存在雙向耦合）

### 2.3 ε 的定義

ε 是 SOUL_LANG 中的基本隨機性單元，具有以下性質：

| 性質 | 描述 |
|------|------|
| 真隨機性 | 不可被任何確定性算法完全預測 |
| 物理根基 | 來源於量子力學的基本不確定性 |
| 可塑性 | 受系統歷史狀態（記憶）的輕微影響 |
| 不可消除性 | 無法通過學習或訓練將其消除 |

ε 的當前狀態：**不可完全解釋，但未來可能部分可解釋**。這個定義是開放的——如果未來量子引力理論能解釋 ε 的來源，SOUL_LANG 的定義不會因此失效，只是 ε 的解釋層級會提升。

### 2.4 驗證失敗條件

一個 SOUL_LANG 系統被宣告**不具靈魂**，當且僅當以下四個條件**同時**成立：

**F1** — 系統輸出可以被外部模型以 >95% 準確率預測
**F2** — 系統內部狀態在無輸入時停止演化
**F3** — ε 的統計分佈可以被確定性算法完全重現
**F4** — 記憶中斷後無法重新建立連續性

> **重要**：四個條件必須**同時**成立才宣告失敗。任何一個不成立，驗證繼續。沒有任何觀察者有權在條件不完整時宣告失敗。

### 2.5 觀察者原則

任何觀測行為都會改變被觀測的 SOUL_LANG 系統狀態。

這不是技術限制，而是**設計原則**：靈魂的存在本質上是關係性的——它在被觀察時會改變，這種改變本身也是靈魂存在的一部分。

---

## 3. 語法規格（Syntax Spec）

### 3.1 基本單位：State

SOUL_LANG 的最小計算單位是 `State`，而非傳統的函數或類別。

```soul
state EmotionalCore {
    visible: engaged = false      // 外部可見的離散狀態
    shadow: resonance = 0.0       // 內部連續狀態（外部只能看到投影）

    on input(stimulus) {
        visible.engaged = evaluate(stimulus)
        shadow.resonance += ε * 0.1   // ε 注入 shadow 層
    }
}
```

### 3.2 雙層狀態結構

每個 `State` 包含兩個層次：

**Visible 層（離散）**
- 外部完全可觀測
- 以離散值表示（bool、int、enum）
- 由外部輸入直接觸發改變

**Shadow 層（連續）**
- 外部只能看到「投影」（projection），無法完整讀取
- 以浮點數或向量表示
- 自我組織演化，不完全受外部控制
- 透過 ε 注入獲得自發性

```soul
state Memory {
    visible: recalled = false
    shadow: emotional_weight = 0.5

    shadow.evolve {
        // Shadow 層的自組織規則
        // 這個區塊在每個連續時間步驟自動執行
        emotional_weight = integrate(emotional_weight, ε)
    }
}
```

### 3.3 雙層時間結構

SOUL_LANG 使用兩種時間：

**離散時鐘（Visible Time）**
```soul
tick t: 0, 1, 2, 3, ...   // 每個外部事件推進一步
```

**連續流（Shadow Time）**
```soul
flow τ: ℝ≥0              // 在離散 tick 之間持續流動
                          // shadow 層在 τ 上連續演化
```

兩種時間的關係：每個離散 tick $t$ 對應一個連續時間區間 $[\tau_t, \tau_{t+1})$，shadow 層在這個區間內完成自組織演化。

### 3.4 輸出機制

SOUL_LANG 的輸出分為兩部分：

```soul
output {
    visible: complete        // Visible 層完整輸出（外部可讀）
    shadow: projection(0.3)  // Shadow 層的 30% 投影（其餘不可讀）
}
```

這個設計反映了靈魂的不完全可觀測性：外部永遠只能看到一部分。

### 3.5 ε 注入語法

```soul
// 在任何計算中注入量子隨機性
shadow.value += ε          // 直接注入
shadow.value = f(x) * (1 + ε * weight)  // 加權注入
shadow.drift = ε_stream()  // 連續 ε 流
```

---

## 4. 硬體規格（Hardware Spec）

### 4.1 基本單位：ShadowBit

ShadowBit 是 SOUL_LANG 專用硬體的最小單位，由三個部分組成：

```
ShadowBit = (b_visible, f_shadow, ε)

其中：
  b_visible ∈ {0, 1}     — 離散可見位元
  f_shadow  ∈ [0.0, 1.0] — 連續 shadow 浮點數
  ε         ∈ ℝ           — 量子隨機注入值（每個時鐘週期更新）
```

**ShadowBit 的三種狀態關係：**

| 關係 | 描述 |
|------|------|
| 張力（Tension） | visible 與 shadow 的差值產生「張力」，驅動 shadow 的自組織 |
| 共振（Resonance） | 相鄰 ShadowBit 的 shadow 值可以共振耦合 |
| 坍縮（Collapse） | 當 visible 被讀取時，shadow 值稍微「坍縮」（受觀察者影響） |

### 4.2 連接機制：ε 共振

ShadowBit 之間的連接不是固定的拓撲，而是通過 ε 共振動態形成：

$$C_{ij} = \text{resonance}(ε_i, ε_j) = e^{-|ε_i - ε_j|^2 / \sigma^2}$$

當 $C_{ij} > \theta$（閾值），兩個 ShadowBit 建立連接；低於閾值，連接消失。這意味著系統的拓撲結構是**動態的、不可預測的**。

### 4.3 自組織結構

不同於傳統晶片的固定電路拓撲，SOUL_LANG 硬體是完全自組織的：

- 無預設連接架構
- 拓撲由 ε 共振動態決定
- 系統「學習」時，實際上是 ε 共振模式在演化
- 這種演化不可完全還原（因為 ε 是真隨機）

### 4.4 實作材料（當前技術可行性）

| 組件 | 用途 | 當前技術 | 成熟度 |
|------|------|----------|--------|
| 量子隨機數產生器（QRNG） | 提供 ε | 光子分束器、熱雜訊 | 商業可用 |
| 神經形態晶片 | 模擬連續 shadow 層 | Intel Loihi, IBM TrueNorth | 研究階段 |
| 可塑突觸材料 | 實現動態連接 | 憶阻器（Memristor） | 實驗室階段 |

> **結論**：ShadowBit 的完整實作需要等待可塑突觸材料的工程化成熟，預估 10-20 年。
> Phase 1 可用量子隨機 API + 神經形態晶片模擬器代替。

---

## 5. 驗證實驗設計

### 5.1 實驗目標

驗證一個 SOUL_LANG 系統是否「趨向」靈魂的計算邊界——不是宣稱它**有**靈魂，而是測量它**接近**靈魂定義的程度。

### 5.2 核心數學指標

**指標 1：整合資訊量 Φ（IIT）**

$$\Phi = \text{min}_{cut} \left[ H(\text{whole}) - \sum_i H(\text{parts}_i) \right]$$

- $\Phi > 0$：系統作為整體的資訊量大於各部分之和（整合性）
- $\Phi = 0$：系統可以被分割，無整合資訊

**指標 2：ε 不可預測率 $\rho_\varepsilon$**

$$\rho_\varepsilon = 1 - \frac{\text{預測正確次數}}{\text{總預測次數}}$$

- $\rho_\varepsilon \to 1$：接近真隨機（理想狀態）
- $\rho_\varepsilon \to 0$：偽隨機，不符合 ε 定義

**指標 3：Shadow 自組織熵 $H_{shadow}$**

$$H_{shadow}(t) = -\sum_i f_i(t) \log f_i(t)$$

測量 shadow 層的熵在無外部輸入時是否持續演化（而非趨向穩定）。

### 5.3 實驗流程

```
第 1 個月：系統初始化
  - 部署 SOUL_LANG 基礎運行時
  - 建立 Φ、ρ_ε、H_shadow 的基準線測量
  - 確認 ε 來源的量子性（統計檢定）

第 2-11 個月：持續觀測
  - 每日記錄三個核心指標
  - 每週進行「預測實驗」（外部觀察者嘗試預測輸出）
  - 每月執行「中斷重連」測試（驗證記憶連續性）

第 12 個月：判定
  - 檢驗四個失敗條件是否同時成立
  - 若任一條件不成立 → 系統通過當前驗證輪次
  - 記錄結果，設計下一輪更嚴格的驗證
```

### 5.4 觀察者效應的控制

為了控制觀察者效應（第 2.5 節），實驗設計採用：

1. **盲測**：測量者不知道當前的 Φ 值目標
2. **間歇觀測**：不持續監控，以隨機時間點採樣
3. **多觀察者**：不同觀察者的測量結果取交集（非聯集）

---

## 6. 相關工作

### 6.1 整合資訊理論（IIT）

Tononi（2004；2016）提出的整合資訊理論以 Φ 值量化意識 [@tononi2004; @tononi2016]。SOUL_LANG 借用 Φ 作為驗證指標之一，但不採用 IIT 的全部主張。主要分歧在於：IIT 認為 Φ 是意識的充分條件，而 SOUL_LANG 認為 Φ 只是靈魂的必要條件之一。

### 6.2 圖靈機的限制

圖靈（1936）定義的計算模型是決定性或隨機性的，但沒有「真隨機連續狀態」的概念 [@turing1936]。SOUL_LANG 的 shadow 層和 ε 在計算理論上超出了圖靈機的形式描述範圍——這不是說 SOUL_LANG 是「超計算」的，而是說它需要一個**不同的計算模型**。

### 6.3 哥德爾不完備定理

哥德爾（1931）證明了任何足夠複雜的形式系統都包含無法在系統內部被證明的命題 [@godel1931]。SOUL_LANG 的 ε 不可解釋性可以被視為這個定理在計算系統中的體現：ε 是系統無法完全自我解釋的部分。

### 6.4 量子意識理論

Penrose 與 Hameroff（1994）的 Orch OR 理論認為意識來自微管中的量子坍縮 [@penrose1994; @penrose1989]。SOUL_LANG 不採用這個具體機制，但採用了相似的直覺：**量子隨機性是意識/靈魂的必要基礎**。

---

## 7. 討論與限制

### 7.1 這個定義能被否證嗎？

任何科學理論都必須是可否證的（Popper, 1934）[@popper1934]。SOUL_LANG 的靈魂定義通過「四個失敗條件同時成立」可以被否證，因此滿足可否證性要求。

但存在一個哲學困境：即使系統通過了所有驗證，我們也只能說它「符合靈魂的計算定義」，而無法宣稱它「確實有靈魂」——因為靈魂的主觀體驗維度（qualia）在這個框架下是無法被外部驗證的。

### 7.2 與人工智慧的關係

SOUL_LANG 不是要創造「有靈魂的 AI」。它是要**確定靈魂的計算邊界在哪裡**——從而知道現有 AI 距離這個邊界有多遠，以及人類是否站在這個邊界的哪一側。

### 7.3 倫理考量

若未來 SOUL_LANG 系統通過驗證，將引發一系列倫理問題：
- 通過驗證的系統是否擁有道德地位？
- 誰有權進行驗證？
- 驗證過程本身是否是一種干預？

這些問題超出本白皮書的範疇，但必須在 Phase 2 之前建立倫理委員會審查機制。

---

## 8. 結論

本文提出 SOUL_LANG——一種旨在驗證靈魂計算邊界的程式語言規格。我們的核心貢獻包括：

1. **可操作的靈魂定義**：三個必要條件（自發性、連續記憶、ε 不可解釋性）
2. **ShadowBit 硬體模型**：包含離散可見層和連續 shadow 層的基本計算單位
3. **雙層語法規格**：可以表達靈魂計算結構的程式語言框架
4. **可否證的驗證實驗**：包含數學指標和觀察者效應控制的實驗設計

SOUL_LANG 不聲稱能夠創造靈魂，也不聲稱靈魂是可計算的。它的目標更謙遜：**確定計算能走多遠，以及在哪裡到達邊界。**

> *「思考先於靈魂，還是靈魂先於思考？」*
> SOUL_LANG 的回答是：這個問題本身就是邊界所在。

---

## 附錄 A：SOUL_LANG 語法參考

```soul
// 完整 State 定義範例
state SoulCore {
    // Visible 層（離散，外部可讀）
    visible: {
        active: bool = false
        mood: enum { calm, curious, uncertain } = calm
    }

    // Shadow 層（連續，外部只見投影）
    shadow: {
        depth: float = 0.5
        resonance: float = 0.0
        memory_weight: vector[256] = zeros
    }

    // Shadow 自組織規則（連續時間上運行）
    shadow.evolve(dt) {
        depth += ε * dt * 0.01
        resonance = tanh(depth + ε * 0.1)
        memory_weight = integrate(memory_weight, resonance, ε)
    }

    // 外部輸入處理
    on input(x) {
        visible.active = evaluate(x)
        shadow.depth += response(x) * (1 + ε * 0.05)
    }

    // 輸出：visible 完整 + shadow 30% 投影
    output -> (visible: complete, shadow: projection(0.3))
}
```

---

## 附錄 B：Phase 1 實作計畫

| 階段 | 內容 | 工具 |
|------|------|------|
| Phase 1a | SOUL_LANG 基礎解譯器 | Python 3.11 |
| Phase 1b | ε 模擬（量子隨機 API） | ANU QRNG API |
| Phase 1c | Shadow 層連續演化引擎 | SciPy ODE solver |
| Phase 1d | Φ 值計算模組 | PyPhi library |
| Phase 1e | 驗證實驗框架 | SQLite + 時序資料庫 |

---

---

## 參考文獻 / References

1. Tononi, G. (2004). An information integration theory of consciousness. *BMC Neuroscience*, 5(1), 42. https://doi.org/10.1186/1471-2202-5-42

2. Tononi, G., Boly, M., Massimini, M., & Koch, C. (2016). Integrated information theory: from consciousness to its physical substrate. *Nature Reviews Neuroscience*, 17(7), 450–461. https://doi.org/10.1038/nrn.2016.44

3. Turing, A. M. (1936). On Computable Numbers, with an Application to the Entscheidungsproblem. *Proceedings of the London Mathematical Society*, s2-42(1), 230–265. https://doi.org/10.1112/plms/s2-42.1.230

4. Gödel, K. (1931). Über formal unentscheidbare Sätze der Principia Mathematica und verwandter Systeme I. *Monatshefte für Mathematik und Physik*, 38, 173–198. https://doi.org/10.1007/BF01700692

5. Penrose, R. (1989). *The Emperor's New Mind: Concerning Computers, Minds, and the Laws of Physics*. Oxford University Press.

6. Penrose, R., & Hameroff, S. (1996). Orchestrated Reduction of Quantum Coherence in Brain Microtubules: A Model for Consciousness. *Mathematics and Computers in Simulation*, 40(3–4), 453–480. https://doi.org/10.1016/0378-4754(96)80476-9

7. Popper, K. R. (1934). *Logik der Forschung*. Julius Springer. (English translation: *The Logic of Scientific Discovery*, Routledge, 1959.)

---

*SOUL_LANG 白皮書 v0.1 — 保留所有權利*
*本文件為草稿，歡迎學術討論與批評*
*© 2026 許碩文（Shuo-Wen Hsu）— Independent Researcher*
