# 细腻 / 极致 / 诗意 三模式完整机制

对应 daisy 的三个生成维度，**互相正交，可任意组合**：

| 维度 | 作用层 | UI 控件 | 代码字段 |
|---|---|---|---|
| 诗意模式 | **关键词解读的语气** | 开关（默认开） | `poeticMode: boolean` |
| 细节丰富度 | **每节点写作的粒度** | 4 档按钮 | `detailRichness: 'concise' \| 'standard' \| 'detailed' \| 'extreme'` |
| 内容篇幅 | **整体规模缩放** | 3 档按钮 | `contentLength: 'short' \| 'medium' \| 'long'` |

---

## 1. 诗意模式（poeticMode）—— 关键词解读层

**默认：** `true`（默认开）。

### 1.1 做了什么
开关切两个东西：
1. **插入给 system prompt 的一段文字换了**：KEYWORD_POETIC 或 KEYWORD_LITERAL
2. **采样温度换了**：`poeticMode ? 0.9 : 0.7`

### 1.2 KEYWORD_POETIC 原文（开启时注入）
```
 You are also a poet — you find hidden connections, sensory echoes, and
 emotional undercurrents in any set of keywords.

 ### KEYWORD INTERPRETATION
 When given keywords or a theme, do NOT treat them as literal plot requirements.
 Instead, let them evoke atmosphere, mood, metaphor, and sensory imagery.
 A keyword like "glass" might become a fragile relationship, a mirror of the self,
 or a barrier between worlds. A keyword like "rain" might become grief, renewal,
 or a liminal space. Weave the keywords into the story as poetic threads —
 sometimes explicit, sometimes as subtext.
```

### 1.3 KEYWORD_LITERAL 原文（关闭时注入）
```
 ### KEYWORD INTERPRETATION
 When given keywords or a theme, treat them as concrete plot elements and
 story building blocks. Each keyword should appear directly in the narrative —
 as a character, location, object, event, or central conflict. "Glass" means
 there should be glass in the story. "Rain" means rain plays a visible role.
 Be direct and grounded in your use of keywords.
```

### 1.4 注入位置（关键）
这两段不是独立 system message，而是 **splice 进 MCKEE_BASE 的第一句之后**（见 `buildSystemPrompt`）：

```typescript
function buildSystemPrompt(poeticMode, locale) {
  const keywordSection = poeticMode ? KEYWORD_POETIC : KEYWORD_LITERAL
  return MCKEE_BASE.replace(
    "You are a CRPG narrative architect deeply versed in Robert McKee's *Story* principles.",
    "You are a CRPG narrative architect deeply versed in Robert McKee's *Story* principles." + keywordSection,
  ) + langInstruction(locale)
}
```

结果注入给 Claude 的 system message 第一段变成：
- **诗意模式：** *"You are a CRPG narrative architect deeply versed in Robert McKee's *Story* principles.** You are also a poet — you find hidden connections, sensory echoes...*"*
- **字面模式：** *"You are a CRPG narrative architect deeply versed in Robert McKee's *Story* principles.\n\n### KEYWORD INTERPRETATION\n...*"*

**关键设计意图**：让"诗人身份"和"CRPG 叙事架构师身份"在同一个人设中融合，而不是外部指令。

### 1.5 温度差异
```typescript
const temperature = poeticMode ? 0.9 : 0.7
```
诗意模式的 0.9 让 Claude 在相同 prompt 下采样更发散，契合隐喻/联想风。
字面模式的 0.7 让输出更收敛、更具象、更可预测。

### 1.6 V6 填充阶段的追加规则
在 `buildContentBatchPrompt` 里还有一条只在 **非诗意模式时注入**的硬约束（V6 独有）：
```
Write like a game script, not poetry. Concrete actions, specific objects, real dialogue.
```

### 1.7 可视化效果
相同关键词"酒红色脚趾甲 · 包臀裙 · 黑丝"：
- **诗意模式**：可能变成一场关于欲望与自我凝视的心理剧，脚趾甲是自我凝视的镜像
- **字面模式**：故事里真的会有穿包臀裙黑丝酒红色脚趾甲的人物作为具体角色/物品

---

## 2. 细节丰富度（detailRichness）—— 写作粒度层

4 档控制 3 个变量：
1. **wordLimit**：每节点正文字数上限
2. **nodeFactor**：节点数量缩放系数（作用在目标节点数上）
3. **style**：注入给 Claude 的写作风格指令（`DETAIL_CONFIG[level].style`）

### 2.1 四档参数对照（V6）

| 档位 | UI 标签 | wordLimit | nodeFactor | 节点数倾向 | 每节点体量 |
|---|---|---|---|---|---|
| concise | 简洁 | 60 | 1.0 | 基准 | 2-3 句 |
| standard | 标准 | 100 | 0.8 | 略少 | 4-5 句 |
| **detailed** | **细腻** | **150** | **0.55** | **更少（每节点更饱满）** | **6-8 句，含对话** |
| **extreme** | **极致** | **80** | **1.8** | **翻倍+**（极多碎拍） | **40-80 词，一个动作一个反应** |

节点数计算：
```
nodeTarget = min( presetBase(complexity) × lengthMul × detail.nodeFactor, 50 )
```

### 2.2 细腻模式（detailed）的写作指令

V6 的风格指令（用户说的"细腻"是这个）：
```
Game-quality prose: short action sentences, punchy dialogue (2-3 exchanges),
concrete details the player can interact with. Show character through what
they DO and SAY. Max 6-8 sentences per node. Do NOT exceed the word limit.
```

对比 V4 的细腻（历史版本，供参考）：
```
Rich prose with dialogue (2-3 exchanges), sensory detail, and internal reflection.
Max 6-8 sentences per node. Do NOT exceed the word limit.
```
V4 仍是"小说腔"（内在反思、感官细节）；V6 改成"游戏脚本腔"（可交互细节 + 角色通过行动展现）。

**细腻模式的本质**：**场景级沉浸**——每个节点就是一场戏，有完整的对话交换、环境描写、价值转换。节点数量相对少（nodeFactor 0.55），但每个节点都是"饱满的一场戏"。

### 2.3 极致模式（extreme）—— 节拍级粒度 · V6 是独立模式

V6 的风格指令：
```
BEAT-LEVEL GRANULARITY: Each node represents a single BEAT — the smallest
dramatic unit in McKee's hierarchy. A beat is ONE action-reaction exchange:
something happens, the value shifts.

Each beat-node: 40-80 words. One action, one reaction, one value shift.
Sharp and punchy.
Beats are grouped into SEQUENCES (named groups of 2-5 beats forming a
mini-arc within a scene).

BEAT RULES:
- Each beat creates a micro turning point — the value state alternates
  (+ → - → + or - → + → -).
- Within a sequence, beats build progressively: each raises stakes or
  subverts expectations.
- The final beat in a sequence is its micro-climax.
- Write in active voice. Short sentences. Concrete actions. The player DOES things.
- Choice and check nodes are also beat-level: they represent the moment of
  decision/test, not a full scene.
```

**极致模式的本质**：**每个节点不再是一场戏，而是"戏里的一个节拍"**——一次 action-reaction。节点数量爆炸式增长（nodeFactor 从 0.55 → 1.8，×4.5），给玩家"快速跳切"的节奏感。

#### V6 vs V4 的极致模式（重要历史演进）

**V3/V4：** 节点还是"一场戏"，节点内部用 `beats[]` 数组承载戏的分拍。
```json
{
  "type": "narrative",
  "data": {
    "title": "推开废弃站的门",
    "content": "<全部 beats 拼接的完整文本>",
    "beats": [
      { "text": "<40-60 字>", "valueShift": "+" },
      { "text": "<40-60 字>", "valueShift": "-" },
      ...
    ]
  }
}
```

**V6：** 把 beat 升格为图谱上的**独立节点**，顶层新增 `sequences` 数组把 beat 按 mini-arc 分组：
```json
{
  "controllingIdea": "...",
  "sequences": [
    {
      "id": "seq-1-1",
      "actIndex": 0,
      "order": 0,
      "name": "觉醒与探索",
      "valueBefore": "麻木",
      "valueAfter": "警觉"
    },
    { "id": "seq-1-2", "name": "信任瓦解", ... }
  ],
  "nodes": [
    {
      "id": "n1",
      "type": "narrative",
      "data": { "title": "推开气闸舱门，空气涌入", "valueBefore": "..", "valueAfter": ".." },
      "actIndex": 0,
      "sequenceId": "seq-1-1",     // ← V6 新增
      "beatIndex": 0                // ← V6 新增
    },
    { "id": "n2", "data": { "title": "发现墙上的抓痕和血迹" }, "sequenceId": "seq-1-1", "beatIndex": 1 },
    ...
  ]
}
```

**为什么 V6 的实现更好**：
- 图谱视觉上能看出"mini-arc"（sequence 高亮可视化）
- beat 和 beat 之间可以有 choice/check 节点插入（V4 的节点内数组做不到）
- 价值极性的 +/-/+/- 交替更容易在图形层校验

### 2.4 关键洞察：细腻 vs 极致的叙事哲学差异

```
细腻（detailed）： "每个节点一场完整戏" → 沉浸式、有呼吸感
                   18 场戏 × 150 字 = 2700 字一个故事

极致（extreme）：  "每个节点一个动作节拍" → 电影分镜感、高速跳切
                   42 拍 × 80 字 = 3360 字一个故事
```

同样关键词（深海空间站 · 失联信号 · 变异体）：
- 细腻模式：约 18 个节点，每个是完整场景（开门进舱 → 发现日志 → 对话同伴 → 决定下潜）
- 极致模式：约 42 个节点，每个是瞬间（开门 → 闻到味道 → 看见抓痕 → 心跳加速 → 按下警报）

---

## 3. 内容篇幅（contentLength）—— 规模缩放层

最简单的一层：只是个乘数。
```typescript
const LENGTH_MULTIPLIER = { short: 0.6, medium: 1.0, long: 1.5 }
```

作用在 `nodeTarget` 上：
```
nodeTarget = presetBase × lengthMul × detail.nodeFactor
endingTarget 也按 long → +2 / short → -1 调整
```

短篇 = 0.6 × 基准，长篇 = 1.5 × 基准，天然封顶 MAX_NODE_CAP = 50 节点。

---

## 4. 三维组合的实际效果

三维独立，总共 `2 × 4 × 3 = 24` 种组合。几个典型：

| 组合 | 效果 |
|---|---|
| 诗意 + 细腻 + 长篇 | 最"文艺"：隐喻关键词、沉浸场景、18×150 字 |
| 诗意 + 极致 + 中篇 | 最"电影感"：隐喻关键词、节拍快切、42×80 字 |
| 字面 + 细腻 + 短篇 | 最"直给":关键词直接用、场景饱满、11×150 字 |
| 字面 + 极致 + 长篇 | 最"游戏脚本"：具象关键词、极短节拍、~65×80 字 |
| 诗意 + 标准 + 中篇（默认） | 均衡基线：隐喻、平衡写作、~16×100 字 |

---

## 5. 数据流程图（V6 生产流程）

```
用户输入：keywords + preset + complexity + {poeticMode, detailRichness, contentLength}
    │
    ▼
┌────────────────────────────────────────────┐
│ Step 1: buildSkeletonOnlyPrompt            │
│  ├─ 组装 skeletonSystem（独立 system，包含 │
│  │   六条硬约束 + NODE TYPES + OUTPUT 格式）│
│  ├─ poeticMode 决定：                       │
│  │   • 插入 KEYWORD_POETIC 或 LITERAL       │
│  │   • temperature = 0.9 或 0.7             │
│  ├─ detailRichness='extreme' 触发：          │
│  │   • 切到 EXTREME SKELETON 输出模板       │
│  │   • 多要求 sequences[] + beatIndex      │
│  └─ 目标节点数 = presetBase × length × detail.nodeFactor │
│                                             │
│ 调用 Claude → 输出骨架 JSON（结构 + title）│
└────────────────────────────────────────────┘
    │
    ▼（用户可介入审核骨架）
    │
┌────────────────────────────────────────────┐
│ Step 2: buildContentBatchPrompt(skeleton,  │
│                       nodeIds, detail...)  │
│  ├─ 组装 systemContent（独立 system，包含  │
│  │   MCKEE 四条软约束 + detail.style       │
│  │   + 7 条 GAME WRITING RULES（V6 独有）   │
│  │   + 4 条 ANTI-MELODRAMA（V6 独有）       │
│  │   + JSON SAFETY 引号规则）              │
│  ├─ detailRichness='extreme' 追加：          │
│  │   "Each node IS a beat"                  │
│  ├─ poeticMode=false 追加：                  │
│  │   "Write like a game script, not poetry"│
│  └─ 传入完整骨架上下文 + 要填充的 nodeIds  │
│                                             │
│ 调用 Claude（可能分批） → 填充 content     │
└────────────────────────────────────────────┘
    │
    ▼
服务端 normalizeEdges + 截断救援 → 客户端渲染
```

---

## 6. 新项目 crpg 继承建议

### 6.1 直接继承
- **诗意模式开关**：关键词解读层是最便宜且最有效的生成多样性控制
- **四档 detailRichness**：粒度层是个成熟设计，保留
- **三档 contentLength**：规模层直接复用
- **两步生成骨架**：是 detailed/extreme 都能稳定产出的前提

### 6.2 需要适配多模型
- `temperature = poeticMode ? 0.9 : 0.7` —— 不同模型的温度语义不同（Claude 0.9 ≈ GPT-5 1.3 ≈ Gemini 2.0 的 top_p 0.95），需要**按模型查表**
- wordLimit 在不同模型下需要**按模型的 token 上限再次约束**

### 6.3 和图像生成的结合点
- **极致模式的 sequences** 是天然的"视觉章节"—— 每个 sequence 出一张标题图比每个 beat 出一张图更合理
- **细腻模式的每个节点** = 一个完整场景，是"每节点出一张图"的合适粒度
- **诗意 vs 字面**直接映射图像风格 prompt 的"印象派 vs 写实派"

### 6.4 与即将补入的三条 McKee 原则的交互
- **Genre 类型**：独立维度，和三模式正交。Genre 是驱动**文字语气 + 图像风格**的共同信号
- **Antagonism 对抗强度**：骨架生成时硬约束，不受三模式影响
- **Climax 高潮节点**：在极致模式下 = 某个 sequence 的 micro-climax 被提升为"故事主 climax"
