# Text-to-Image Bug Taxonomy —— 文转图五类系统性 bug 分类学

**来源**：2026-04-17 crpg 项目图像生成测试 Round 1-5 的系统反思。每轮每个 bug 的反溯分析，分类归因，给出机制级解法。

**用途**：
1. 作为 **Shot Director LLM** 的 system prompt 训练料（让 LLM 在生成 shot prompts 时主动规避这些 bug）
2. 作为 **Visual DNA 演进的 TODO 库**（每一类 bug 对应 Visual DNA 的一层或子字段）
3. 作为 crpg 项目的**技术护城河 asset**（这些经验在公开社区/论文里几乎没有）

---

## 核心洞察

**文转图的难度不是"prompt 写得更细"能线性解决的**。每当 prompt 写得越详细，扩散模型的"字面化倾向 + 默认先验 + 训练分布吸附"会以新的方式出错。这是一个**对抗性多轮调优**的工程问题，不是"找到完美 prompt 模板"的问题。

五类 bug 覆盖了 Round 1-5 的所有失败案例：

```
A. Identity Drift           —— 角色/setting/物体身份漂移
B. Motion Stiffness         —— 人物 stock photo 静态
C. Literal Interpretation   —— 隐喻被字面化
D. Default-Prior Override   —— 模型默认先验压过 prompt
E. Cross-Scene Contamination —— 信号污染无关场景
```

每类有自己的解法机制和 Visual DNA 层归属。

---

## Bug Class A — Identity Drift（身份漂移）

### 症状
角色/setting/物体在不同帧之间不一致。

### 案例
- R1 Scene 1：Su Wan 是白人欧美脸，Scene 4 是东方人——**同一角色在 5 帧里是 5 个不同的人**
- R1 Scene 1：prompt 说"Chinese police interrogation room"，输出是"CAFE 咖啡馆"——**命名 setting 被默认 neon-noir 模板吃掉**
- R1 Scene 1：包臀裙变成普通 A 字短裙——**服装属性被泛化**

### 根因分析
扩散模型的每次独立调用都是**独立采样 from scratch**。prompt 里的命名 token（"Chinese"、"Su Wan"、"pencil skirt"）权重不足以压过模型训练分布的 dominant peak（西方脸 / noir cafe / A-line skirt）。没有跨帧"记忆"机制。

### 解法机制
1. **Character Sheet 详尽描述**（外貌常量 50+ 词），每张 prompt 完整复制
2. **Anchor Strategy（image-to-image）**：先生成一张"身份锚"，后续帧用 `image_url` 做 style/identity transfer
3. **高频关键词冗余**：关键身份信号（"Chinese"、"East Asian"、"burgundy toenails"）在同一 prompt 里出现 3+ 次
4. **Aspect ratio 锁定**：全故事同 ratio 族，避免 ratio 混用破坏"同一部片"的视觉 continuity

### Visual DNA 对应
- **Layer 3** (Character Sheets) + **Layer 7** (Anchor Strategy) + **Layer 6** (Technical Lock)

### Shot Director 检查点
- 每个 shot prompt 中，所有 named character 必须有 50+ 词 descriptor
- 每个 shot prompt 中，文化/种族信号（"Chinese"/"East Asian" 等）必须出现 ≥3 次
- 跨 shot 的同一故事必须共享 image_url anchor

---

## Bug Class B — Motion Stiffness（静态僵硬）

### 症状
人物像 stock photo 商业摄影的 "portrait pose"，不像"正在发生的瞬间"，没有戏剧张力。

### 案例
- R2 所有场景：Su Wan 面朝镜头静态微笑，像 studio portrait
- R2 Scene 4：三个人在化妆镜前"合影式"并排站立

### 根因分析
扩散模型的训练数据大多是商业摄影/stock photo，"portrait pose"是训练分布的 global maximum。不给显式对抗指令，模型默认滑向这个 peak。

### 解法机制
1. **Direction Layer**（Visual DNA 第 8 层）：
   - "candid documentary still, not staged portrait"
   - "subjects DOING something, not facing camera"
2. **Action Moments 使用 present continuous 动词**（lighting / reaching / pausing / glancing）
3. **Micro-expression 具体 tell**（jaw tension / pressed lips / Adam's apple swallowing），不用感性形容词（composed / predatory）
4. **Photographer tether**：引用具体纪实摄影师（Nan Goldin / Wong Kar-wai / Gregory Crewdson）作为风格锚
5. **身体语言四约束**：weight shift / hands doing something / gaze direction / asymmetry

### Visual DNA 对应
- **Layer 8** (Direction Layer)

### Shot Director 检查点
- 每 shot prompt 不得含感性形容词（composed/mysterious/sensual/seductive/predatory/amused/alluring）
- 每个在 frame 里的 character 必须有 ≥1 present-continuous 动词描述其当下动作
- 每 shot prompt 必须 tether 到 1 个摄影师名字

---

## Bug Class C — Literal Interpretation of Metaphor（隐喻字面化）

### 症状
prompt 里的诗化/隐喻描述被模型**字面渲染成可见物体/肢体外露**。

### 案例
- R3 所有场景：Direction Layer 里的 "tongue briefly wetting lips" 这个 tell → 5/5 张图里人物**真的吐舌头**
- R5 Shot 1：Action moment 里的 "cigarette burn in the steel edge"（意指钢桌上有烟灰烫痕）→ 图里**真的画出一根燃烧的烟**
- R3 Su Wan character sheet 里 "like a drop of blood" → 模型**真的画血滴**（如果用在某些场景）

### 根因分析
扩散模型把 prompt 里的 noun/verb 都当成 "things to render on canvas"。它**不区分"这个词是字面描述物体" vs "这个词是比喻/隐喻"**。人类读者能秒懂的比喻，对扩散模型而言都是 literal rendering instruction。

### 解法机制
1. **tell vocabulary 预清洗**：任何会被字面化成"可见肢体外露 / 可见物体"的词从词汇表里移除
   - 禁："tongue wetting"、"teeth bared"、"mouth open"
   - 允："lip caught between teeth inside mouth"、"jaw tension"、"Adam's apple swallow"
2. **隐喻 → 具象改写**：
   - 不写 "like a drop of blood"，直接写 "glossy burgundy-red"
   - 不写 "cigarette burn in the steel" (会误生成燃烧的烟)，改写 "small dark scorch mark on the steel edge"
3. **硬否定冗余**：
   - "no tongue visible, mouth closed, lips sealed"
   - "no cigarette, no smoke, no fire"（如果 prompt 不该有烟）

### Visual DNA 对应
- **Layer 8** 的 `micro_expression_vocabulary` 清洗规则
- **Direction Layer** 的 "forbidden literal-rendering tells" 段

### Shot Director 检查点
- 预生成时 scan prompt，识别所有隐喻性描述
- 自动将"like X"、"as if X"、"reminds of X" 模式的比喻改写为纯具象
- 对 tell vocabulary 做白名单校验（只允许预先验证过"字面化安全"的 tells）

---

## Bug Class D — Default-Prior Override（默认先验压过 prompt）⭐ 最难

### 症状
模型对某类服装/场景/姿态有**极强的训练先验**，prompt 的细节指令被先验"吸附"到最相近的 training distribution peak。

### 案例（Round 5 Shot 2 连续 5 版修复才根治）
- **v1**："sheer black stocking ending just above the ankle" → 模型字面化→**短袜**（ankle sock）
- **v2**：整腿沿伸到画面外 → 模型默认"整条腿黑色布料 = 裤子" → **变成裤子**
- **v3**：Crop 太紧 + 只到脚踝 → 避开裤子误解，但**构图苍白只剩一只脚**
- **v4**："top band at mid-thigh" → 模型默认"mid-thigh band = 过膝袜顶端" → **变成过膝袜**
- **v5**：才真正做对——"top band at UPPER thigh, 2-3cm skin gap below skirt hem, covers ENTIRE leg length"

### 根因分析
扩散模型的训练分布里，某些视觉 domain 的先验比其他 domain 强得多。服装尤其严重：
- "整条腿一种布料" → 裤子是 dominant peak，丝袜是 minor peak
- "band around thigh" → 过膝袜 / 足球袜 / 吊带袜 是几个相近的 peaks，模型倾向 snap to nearest
- prompt 里的指令词（"thigh-high"、"sheer"）不如"视觉分层结构"（skirt hem + skin gap + band + stocking）有效

### 解法机制（最关键）
1. **Layered Visual Grammar**：同时提供**多重冗余视觉线索**消歧
   - 案例：让 skirt hem + skin gap + stocking top band + sheer stocking + seam line 都在画面里同时可见，组合信号让模型无法滑回裤子/过膝袜 peak
2. **具体尺寸 constraint**：
   - 不说 "small gap"，说 "2-3cm gap"
   - 不说 "mid-thigh"（歧义），说 "upper thigh, just 2-3cm below skirt hem"
3. **硬否定三重冗余**：
   - "NOT pants" / "NOT over-the-knee" / "NOT knee-high" 并列
4. **反先验视觉锚点**：
   - 针对"stocking 被画成 opaque 裤子"，强调 "skin visibly glowing through translucent nylon mesh, underlying skin tone creating warm undertone through cool black weave"

### Visual DNA 对应
- **Layer 3** (Partial Presence) 加子字段 `body_fragment_rule`
- **Layer 10 新增** —— **Layered Garment Visibility Rule**：对有强默认先验的物体类型（stocking / dress / specific period costume / ethnic wear），prompt 必须提供 3+ 层独立视觉线索

### Shot Director 检查点
- 维护一个 **"High-Prior Garment List"**（stocking / thigh-high / lingerie / qipao / school uniform 等），prompt 涉及这些时强制启用 layered grammar + 3+ cue rule
- 自动 scan prompt 中的尺寸指令词（"mid-thigh"/"knee-high"/"ankle-high"），对模糊者强制换成具体 cm 数值
- 对关键服装，生成前做 "adversarial prompt check"：模拟模型最可能的误读（列 3-5 个可能的 peaks）并对每个增加硬否定

---

## Bug Class E — Cross-Scene Contamination（场景间污染）

### 症状
一个角色的 signature / feature 出现在**其他不包含该角色**的场景里。

### 案例
- R4：Meijie 的 character signature 是 "cigarette smoke curling past her eye"。但这个 signature 被写进 Direction Layer（字节级固定注入每张 prompt），结果：
  - Scene 1（只有 Su Wan + Lin Ze，**Meijie 不在场**）→ 苏晚嘴里叼烟 + 桌上一根烟
  - Scene 3（公寓浴室，**Meijie 不在场**）→ 林泽嘴边一根烟

### 根因分析
- Direction Layer 作为"通用层"被错误地注入了 character-specific 信号
- 扩散模型看到 prompt 里有 "cigarette smoke" → 不知道 Meijie 不在 frame → 把 cigarette 转移给 frame 里的任意 character

### 解法机制
1. **层级隔离**（hard rule）：
   - **Direction Layer** 只含**通用规则**（mouth hygiene / body language / present-continuous / photographer tether）
   - **Character Sheet** 含**该角色的 signature**（Meijie 的 cigarette signature 下沉到她的 sheet）
   - **Scene Prompt** 只引用**该 scene 实际出现的 character sheets**
2. **Shot Director 在组装 prompt 时严格过滤**：
   - Input：该 shot 中实际在 frame 的 character id list
   - Output：只把这些 character 的 sheet 加入 prompt，其他 character 的 signature 绝不出现

### Visual DNA 对应
- **Layer 3** 与 **Layer 8** 的隔离约束：
  - Direction Layer 的 vocabulary 必须是 character-agnostic
  - Character-specific tell/feature/accessory 只存在于 Character Sheet

### Shot Director 检查点
- Before 发送 prompt，运行一个 validator：
  - 提取 prompt 中出现的所有 character id
  - 验证 prompt 中不包含未出现 character 的 signature 词汇（如 Meijie 不在场时，"cigarette smoke"/"chignon"/"emerald cheongsam" 不应出现）
- 如果发现污染，自动移除相关词并告警

---

## 五类 Bug 的叠加与跨类关系

Round 5 Shot 2 的 "stocking bug" 实际是 **Class D 主因 + Class C 辅因** 的叠加：
- 主因 D：模型对"一整条腿黑布料"有强裤子先验
- 辅因 C：prompt 里 "ending just above the ankle" 被字面化（意图是"本 shot 只看到这段"，被读成"袜子真的在这里结束"）

R4 的 tongue bug 是 **Class C 纯净案例**；Meijie cigarette 串场是 **Class E 纯净案例**。多数真实 bug 是跨类组合。

## 每类 Bug 的成本 vs 解法机制

| Class | 单次出现的成本 | 机制级解法成本 | 是否可以"只靠 prompt 经验"解决 |
|---|---|---|---|
| A Identity Drift | 低（一张图偏） | 低（Character Sheet + Anchor） | ✅ 可以 |
| B Motion Stiffness | 中（整体 vibe 差） | 中（Direction Layer） | 部分可以 |
| C Literal Metaphor | 低-中（具体字面化 artifact） | 中（vocabulary 清洗） | ❌ 需要维护黑名单 |
| **D Default Prior** | **高（多次 iteration 才能修）** | **高（需要 Layered Grammar + 反先验锚）** | **❌ 必须机制化** |
| E Cross-Scene Contamination | 中（污染多帧） | 低（层级隔离就好） | ❌ 必须机制化 |

**核心结论**：Class D 和 E 是**必须机制化**的 bug 类型，不能靠 prompt 经验。crpg 的 Shot Director LLM 必须在 system prompt 里内置这两类 bug 的自动检测和预防机制。

---

## 对 crpg 架构的启示

### 1. Shot Director LLM 是核心护城河
- 不只是"把故事拆成 shot list"
- 而是"**带着五类 bug 预警系统把故事拆成 shot list**"
- 这个 LLM 的 system prompt 里要内置完整的 Bug Taxonomy + 对应检查规则

### 2. Visual DNA 要继续演进
- 当前 9 层机制解决了 A/B/C/E 类 bug
- **Layer 10 必须新增 Layered Garment Visibility Rule** 解决 D 类
- 未来还会发现 F 类、G 类（比如跨语言文化符号漂移 / 光影连续性 bug / 动作姿态的物理合理性 bug）

### 3. "每次 iteration 学到的 bug 都是 asset"
- 每发现一个新 bug → 更新 taxonomy → 固化进 Shot Director system prompt
- 这是一个**永不终结的 asset 积累**，像 daisy 的 799 行 prompts.ts 一样
- 谁积累的 Bug Taxonomy 最深，谁的产品视觉质量最高

### 4. 用户在 bug 诊断中不可替代
- 模型诊断自己的 bug 能力有限（它就是写 prompt 的那个模型）
- **人类审美 + 细节敏感（"这是过膝袜不是长丝袜"）是 bug 发现的唯一 source**
- 产品化时需要"创作者预览 → 人工标记 bug → 自动回流到 taxonomy" 的 feedback loop

---

## 附录：Round 1-5 的 Bug 归因汇总

| Round | 案例 | Bug Class | 解法 Visual DNA 层 |
|---|---|---|---|
| R1 | Su Wan 人种漂移 | A | Layer 3 Character Sheet |
| R1 | Chinese interrogation room → cafe | A | Layer 6 Technical Lock + Positive Framing |
| R1 | 5 张 color grade 不一 | A | Layer 1 Style Preamble |
| R2 | 人物 stock photo pose | B | Layer 8 Direction Layer |
| R3 | 所有场景都吐舌 | C | Layer 8 tell vocabulary 清洗 |
| R4 | Meijie cigarette 串场 Su Wan 嘴 | E | Layer 3 + Layer 8 隔离 |
| R4 | Scene 1 桌上生成烟 | C | Layer 8 隐喻改写（"cigarette burn" → "scorch mark"） |
| R4 | Scene 4 解剖错误 | B 变体（anatomy） | Layer 8 ECU anatomy hygiene |
| R5 Shot 2 v1 | 短袜 bug | A + C | Layer 3 body_fragment_rule |
| R5 Shot 2 v2 | 裤子 bug | **D** | Layer 10 Layered Garment Visibility |
| R5 Shot 2 v4 | 过膝袜 bug | **D** | Layer 10 + 具体尺寸 constraint |
| R5 Shot 2 v5 | （待验证） | — | — |
