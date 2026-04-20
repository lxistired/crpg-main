# crpg 系统架构审查 —— 2026-04-17

**角色**：系统架构师（不是战略顾问，不是代码 auditor）
**任务边界**：回答"架构是什么样、架构应该是什么样、从现在到应该是之间差距在哪、每条差距怎么在架构层面关掉"
**严格不做**：日级 action plan / 周级工期表 / "真金 vs 水分"评分 / "Fork daisy Day 1"之类的 tactical 指令 / 代码 bug 审查

**材料**：用户目的陈述 / daisy 10,279 行代码（全部模块）/ assets/daisy-narrative-core/ 的 15 份方法论 / R1-R5 测试实证 / MEMORY 7 条 / SESSION-STATE

---

## 目录

1. [目的的架构化表述 Purpose as Architecture](#1-目的的架构化表述)
2. [Canonical Architecture（理想架构）](#2-canonical-architecture理想架构)
3. [Current-State Mess Inventory（现状混乱清单）](#3-current-state-mess-inventory现状混乱清单)
4. [Architectural Cleanup Plan（架构级清理）](#4-architectural-cleanup-plan架构级清理)
5. [One-Page Mental Model（一张图看懂整个系统）](#5-one-page-mental-model)
6. [一段话总结](#6-一段话总结给朋友解释)

---

## 1. 目的的架构化表述

用户的原始陈述（反复多次）：

> "关键词或者一段话 → 生成文字 + 图片的互动叙事游戏。成人向（18+ 合法）。daisy 已经做了文字版。crpg = 在 daisy 基础上加图片。需要创作者 UGC 发布机制 + 免费玩家端。"

把这句话**压缩成架构契约**：

### 1.1 系统边界（System Contract）

| 维度 | 契约 |
|---|---|
| **INPUTS** | `{ keywords: string, genre_hints?: string, aesthetic_preference?: string, characters?: CharacterSpec[], explicitness_dial: 'suggest' \| 'direct' }` |
| **OUTPUTS** | 一份 `StoryBundle`（自包含 artifact）：`{ manifest, story_graph, visual_dna, shots_per_node: Record<NodeId, Shot[]>, asset_blobs: ImageBlob[] }` |
| **ACTORS** | 4 类：Creator（生成）/ Player（消费）/ Moderator（审核）/ Operator（平台） |
| **SLA** | Creator 端生成：≤ 5 min/ 20 节点故事，文字优先可见，图像渐进填充 ≤ 10 min。Player 端：**零 AI 调用、零图像 API 调用、≤ 1s 首帧** |

### 1.2 强制不变量（Hard Invariants）

这些是架构的**物理约束**（不是"feature"），一旦破坏，系统语义即崩溃：

- **I-1 纯享版零生成**：Player 端运行时绝不调用任何 LLM 或图像 API。Player 消费的**唯一**输入是 `StoryBundle`。
- **I-2 StoryBundle 可离线完整播放**：给定一份 bundle，不依赖任何外部服务即可从头玩到尾（因此 bundle 必须自包含所有图像、文字、图结构）。
- **I-3 18+ gate 是系统入口**：不在 feature 层，是 `Session` 层的 precondition。未通过 gate 的 Session 无法进入任何内容面（包括 Community feed）。
- **I-4 BYOK 和平台 key 是 Creator 端的运行时选择**：同一个 Creator 在同一个项目上可以切换，不是 account-level 绑定。
- **I-5 Audit 是 side effect，不在 happy path 上**：审计记录写入异步队列，不阻塞生成/发布/播放。

### 1.3 目的 → 架构的第一决策

**这份契约立刻决定了一件事：玩家端和创作者端不是"同一个应用的两个 mode"，它们是两个不同的应用**，共享的只有一份数据契约（`StoryBundle`）。

daisy 现在的架构是"Editor 模式 + PlayMode 模式"在**同一个 React 应用里**切换，共享同一个 `editorStore`（！）——PlayMode 从 `useEditorStore.nodes/edges` 读数据。这在 daisy 的单用户情境里合理，在 crpg 的"公开发布 + 免费玩家"情境里**架构上已经错了**。见 §3 Mess #1。

---

## 2. Canonical Architecture（理想架构）

### 2.1 顶层拓扑（5 个核心 component）

```
                    [PLATFORM RUNTIME]
┌──────────────────────────────────────────────────────────────┐
│                                                              │
│  ┌────────────────┐       ┌────────────────────────────┐    │
│  │                │       │                            │    │
│  │  CREATOR APP   │───────▶    CONTENT PIPELINE        │    │
│  │  (生成 + 编辑)  │       │  (3-pass LLM + Image Batch)│    │
│  │                │◀──────│                            │    │
│  └────────────────┘       └────────────────────────────┘    │
│          │                              │                   │
│          │  publish                     │  writes           │
│          ▼                              ▼                   │
│  ┌──────────────────────────────────────────────────┐      │
│  │           STORYBUNDLE STORE (CDN)                │      │
│  │    (immutable, versioned, signed artifacts)      │      │
│  └──────────────────────────────────────────────────┘      │
│          │                                                  │
│          │ read-only                                        │
│          ▼                                                  │
│  ┌────────────────┐                                        │
│  │   PLAYER APP   │                                        │
│  │   (纯享版)      │                                        │
│  └────────────────┘                                        │
│                                                              │
│  ┌─────────────────────────────────────┐                   │
│  │      COMPLIANCE & IDENTITY LAYER    │  (wraps all above) │
│  │  age-gate / geo / audit / key-vault │                   │
│  └─────────────────────────────────────┘                   │
└──────────────────────────────────────────────────────────────┘
```

**5 个 component 的唯一职责**：

| # | Component | 唯一职责 | 绝对不做 |
|---|---|---|---|
| 1 | **Creator App** | 画布编辑 / 触发生成 / 审视生成结果 / 触发发布 | 不运行图像模型、不存储公开内容、不鉴权玩家 |
| 2 | **Content Pipeline** | 把 `keywords + preferences` 变成 `StoryBundle` 的 pure 流程（3-pass LLM + image batch） | 不持有用户状态、不管 UI、不做合规判断（合规作为 middleware 注入） |
| 3 | **StoryBundle Store** | 持久化 + 分发已签名的 bundle 到 CDN | 不生成内容、不运行 JS、不持有 secret |
| 4 | **Player App** | 静态加载 bundle，按图游玩 | 不调用任何 API、不生成任何内容、不付费 |
| 5 | **Compliance & Identity Layer** | age-gate / geo-gate / BYOK vault / audit writer | 不做产品功能、不 serialize 业务语义 |

### 2.2 Content Pipeline 展开（架构级，不是工程级）

这是用户最混乱的地方，所以展开细节。Pipeline 是**一串 pure stages**，每个 stage 有明确的 input/output contract：

```
 Creator 输入
   │
   │  { keywords, aesthetic_preference?, characters?,
   │    genre_hints?, explicitness_dial, preset, complexity,
   │    detailRichness, contentLength }
   │
   ▼
┌───────────────────────────────────────────────────────────┐
│ STAGE P1: Story Architect                                 │
│                                                           │
│ LLM pass (text model) — derives:                          │
│   • controllingIdea                                       │
│   • skeleton nodes + edges (no prose yet)                 │
│   • inferred genre                                        │
│   • inferred aesthetic_axis                               │
│   • antagonism profile                                    │
│   • climax node id                                        │
│   • value-shift labels per node                           │
│                                                           │
│ Output: StorySkeleton (JSON)                              │
└───────────────────────────────────────────────────────────┘
   │
   ▼
┌───────────────────────────────────────────────────────────┐
│ STAGE P2: Visual DNA Synthesis                            │
│                                                           │
│ LLM pass (text model) + rule engine — derives:            │
│   • style_preamble                                        │
│   • character_sheets (extracted from skeleton)            │
│   • recurring_motifs (layered: every_frame / scene / shot)│
│   • positive_framings                                     │
│   • technical_lock (ratio / model / resolution)           │
│   • direction_layer (fixed)                               │
│   • garment_high_prior_list (flag only)                   │
│                                                           │
│ Output: VisualDNA (JSON, story-scoped)                    │
│                                                           │
│ ※ 这一步现在在方法论文档里是"Layer 1-8 + 10"，但它是 LLM   │
│   pass + YAML 模板，不是独立模块。                        │
└───────────────────────────────────────────────────────────┘
   │
   ├─────────────────────────┐
   │                         │
   ▼                         ▼
┌──────────────┐     ┌────────────────────────────┐
│ P3: Content  │     │ P4: Shot Director          │
│ Filler       │     │                            │
│              │     │ LLM pass (text model):     │
│ LLM pass     │     │   • iterate nodes          │
│ (text model):│     │   • 0-N shots/node (弹性)  │
│   • prose    │     │   • each shot: type + beat │
│     per node │     │     + focal_subject        │
│   • batch of │     │     + composition_hint     │
│     5 nodes  │     │     + bug-taxonomy flags   │
│              │     │                            │
│ Output:      │     │ Output: ShotPlan           │
│ NodeContents │     │ (list per node)            │
└──────┬───────┘     └──────────────┬─────────────┘
       │                            │
       │       merge (pure)         │
       └──────────────┬─────────────┘
                      │
                      ▼
        ┌──────────────────────────────────────┐
        │ STAGE P5: Prompt Assembler           │
        │                                      │
        │ Pure function (NO LLM) — composes:   │
        │   • per shot, stitch together        │
        │     VDNA layers + shot spec          │
        │     + garment_disambig (if flagged)  │
        │     + character_sheet (filtered:     │
        │       only characters in this shot)  │
        │                                      │
        │ Output: ImagePromptSpec per shot     │
        │                                      │
        │ ※ 这里必须 pure，因为合规 validator  │
        │   要在这层插入。                     │
        └──────────────────────────────────────┘
                      │
                      ▼
        ┌──────────────────────────────────────┐
        │ STAGE P6: Image Batch Worker         │
        │                                      │
        │ • pull ImagePromptSpec               │
        │ • call Grok Imagine Pro              │
        │ • Stage-1: anchor (1 per story)      │
        │ • Stage-2: shots (use image_url=anchor)│
        │ • retry / cost accounting            │
        │                                      │
        │ Output: ImageBlobs                   │
        └──────────────────────────────────────┘
                      │
                      ▼
        ┌──────────────────────────────────────┐
        │ STAGE P7: Bundle Packer              │
        │                                      │
        │ Pure function — emits:               │
        │   StoryBundle {                      │
        │     manifest, graph, VDNA,           │
        │     content, shots_by_node,          │
        │     assets, signatures               │
        │   }                                  │
        └──────────────────────────────────────┘
                      │
                      ▼
                 [publish → Store]
```

**关键观察**：
- **P1 / P2 / P3 / P4 都是 LLM pass，但责任不同**。它们不应该合成一个 pass（Sonnet 一次写 5KB 的 output 会导致截断，daisy V3→V4 的教训已经证明）。
- **P5 必须是 pure function**。因为合规 validator（scan for forbidden keywords / scan for minor-implication / scan cross-scene contamination）必须在这里插入，而 LLM pass 内部的 validator 是不可控的。
- **P2 的 output 是整部故事的 VisualDNA object，不是"embedded in prompt"**。它是 pipeline 的 first-class data，存进 bundle、可被 Creator review 和编辑、可被 P5 引用。

### 2.3 双模型路由（Sonnet + Grok）的架构位置

这是用户明确说混乱的地方之一。架构答案：

**路由不放在 service 层、不放在 prompt 层——放在 "LLM call site" 的 decorator 层**。

```
ai.ts (existing daisy service)
    │
    ├── 改造为：
    │
    ▼
LLMRouter (new decorator)
    │
    ├── 参数：{ pass: 'P1'|'P2'|'P3'|'P4', explicitness: 'suggest'|'direct', locale, tokens_target }
    │
    ├── 决策逻辑（简化）：
    │     P1/P2 (骨架 + VDNA) → 永远 Sonnet（需要方法论遵守）
    │     P3/P4 (content + shots) → if explicitness='direct' → Grok, else Sonnet
    │
    ├── 温度等价表（内置）：
    │     { sonnet: { poetic: 0.8, literal: 0.7 },
    │       grok:   { poetic: 0.9, literal: 0.75 } }  // 行为等价，不是数值等价
    │
    ▼
Provider adapters:
    ├── SonnetAdapter (existing OpenRouter client)
    ├── GrokAdapter   (new, xAI direct or OpenRouter)
    │
    ▼
底层 HTTP
```

**不要**把"按 explicitness 路由"写进 prompts.ts（会让 prompts 和 router 耦合）。
**不要**把"按 explicitness 路由"写进 React hook（会让前端知道模型策略）。
**要**在一个 `LLMRouter` 模块里集中所有路由决策，service 层对所有 pass 只调一个 `llmCall(passId, params)`。

### 2.4 数据契约（最关键的三份）

用户要的是 contract。三份：

#### Contract A: `StorySkeleton` （P1 output）

```ts
interface StorySkeleton {
  meta: {
    skeleton_id: string
    created_by: CreatorId
    controllingIdea: string
    inferred_genre: string
    inferred_aesthetic_axis: string       // 从 24 子派里选 1-2
    antagonism_profile: string
    climax_node_id: string
    explicitness_dial: 'suggest' | 'direct'
    compliance_flags: string[]            // e.g. ["contains_power_dynamic", "contains_alcohol"]
  }
  nodes: Array<{
    id: string
    type: 'narrative'|'choice'|'check'|'merge'|'act_break'|'ending'
    actIndex: number
    sequenceIndex: number
    data: {
      title: string
      valueBefore: string
      valueAfter: string
      choices?: string[]
      check?: { attribute: string; dc: number }
    }
    // 注意：没有 content/image_url 字段，骨架里只有结构
  }>
  edges: Array<{
    id: string
    source: string
    target: string
    sourceHandle: string | null
    label?: string
  }>
}
```

#### Contract B: `VisualDNA` （P2 output）

```ts
interface VisualDNA {
  story_id: string
  style_preamble: {
    default: string
    act_1?: string    // 可按故事阶段切换（bonus 晨光图证明可用）
    act_2?: string
    act_3?: string
  }
  aesthetic_axis: { primary: AxisId; secondary?: AxisId }
  characters: Record<CharacterCode, {
    full_sheet: string            // 详细描述 50+ 词
    partial_presence_rule: string // 只露手/背影/OTS 时的简化 sheet
    signature_tells: string[]     // character-specific, 只在该 character 在帧中时注入
    high_prior_garments: string[] // 触发 Layered Garment Visibility 的服装
  }>
  recurring_motifs: {
    every_frame: string[]
    scene_level: Record<SceneId, string[]>
    shot_level: Record<ShotId, string[]>
  }
  positive_framings: Record<string, string>   // e.g. "instead_of_cafe" → "interrogation room..."
  technical_lock: { aspect_ratio: string; resolution: string; model: string }
  direction_layer: {
    framing: string
    micro_expression_vocabulary: string
    body_language: string
    verb_bias: string
    photographic_references: string[]
  }
  anchor: {
    anchor_prompt: string       // 用于生成 Stage-1 anchor
    anchor_asset_url: string    // Stage-1 生成后回填
  }
}
```

#### Contract C: `StoryBundle` （P7 output，Player 的唯一输入）

```ts
interface StoryBundle {
  schema_version: '1.0'
  bundle_id: string
  signature: string                     // platform signs bundle for tamper detection

  manifest: {
    title: string
    description: string
    author: { id: CreatorId; display_name: string }
    published_at: ISO8601
    content_rating: '18+'
    content_warnings: string[]          // ["sexual_content","power_dynamic",...]
    geo_restrictions: string[]          // ["KR","DE-BY","SA",...]
    estimated_play_minutes: number
    cover_asset_id: string
  }

  story: {
    controllingIdea: string
    graph: {
      nodes: PlayableNode[]             // node.content 已填充（P3 的 output）
      edges: PlayableEdge[]
    }
  }

  visual: {
    visual_dna_snapshot: VisualDNA      // 存档用，给 remix / analytics
    shots_by_node: Record<NodeId, ShotBundleEntry[]>
    assets: Record<AssetId, { url: string; sha256: string; bytes: number }>
  }

  audit: {
    generation_model_map: Record<PassId, ModelVersion>   // 审计追溯
    prompt_digests: Record<PassId, string>               // SHA-256, not raw prompts
    generated_at: ISO8601
  }
}
```

**重要**：
- `StoryBundle` 是 **immutable**。Creator 想改 → 发布新 bundle 版本（新 bundle_id），旧 bundle 继续存活直到 unlist。
- Player 端**只读 StoryBundle**，不读 daisy 的 `projects / nodes / edges` 表。这三张表是 Creator 端的编辑态，和 Player 无关。

### 2.5 合规层（Compliance Layer）的插入位置

用户问合规层在哪。答：**4 个固定插入点，每一点有明确语义**：

| 插入点 | 角色 | 实现形态 |
|---|---|---|
| **CP-1 Session Entry** | 18+ / geo 检查 | 在 Player App 和 Creator App 的 root route guard，拒绝通过则渲染 gate 页面 |
| **CP-2 Pipeline Input Validator** | 输入 keywords 预扫描（禁未成年 / 禁真人名 / 禁仇恨符号） | 在 Creator → Pipeline 的 API gateway，调用 P1 前执行 |
| **CP-3 Prompt Assembler Validator** | 扫描已组装的 image prompt 最终字符串（强制正向描述、去除未成年 trigger） | 在 P5 output 到 P6 input 之间，pure function |
| **CP-4 Bundle Publish Gate** | 最终 bundle 发布前的人工 or 自动审核 | 在 Creator 触发 publish 到 Bundle Store 写入之间 |

**不要**把合规分散到 prompts / service / routes 各处。它是**一条可独立 deploy 的 middleware pipeline**。

---

## 3. Current-State Mess Inventory（现状混乱清单）

这是用户最需要的部分。每条混乱是**架构级**问题，不是 bug、不是代码质量、不是战略选择。

### Mess #1: daisy 的"单应用双模式"架构与 crpg 的"公开平台"语义冲突

**是什么**：daisy 的 Editor 和 PlayMode 共享同一个 React 应用 + 同一个 `editorStore`。`App.tsx` 里用 `appMode: 'editor'|'play'|'community'` 切换视图，Play 直接从 Editor 的 store 读 nodes/edges。Community mode 里选一个故事 → 走 `setNodes(story.nodes)` 塞进 Editor store → 再进 Play。

**代码证据**：
- `/tmp/crpg-research/daisy/packages/web/src/App.tsx:106-127`
- `/tmp/crpg-research/daisy/packages/web/src/hooks/useGameLoop.ts:47-48`（从 `useEditorStore` 读）
- `/tmp/crpg-research/daisy/packages/web/src/stores/editorStore.ts`（所有 mutation 都在这个 store）

**为什么乱（架构视角）**：
- Invariant I-2（Player 端离线可玩）和 I-1（Player 端零生成）在这个架构里**无法表达**——Editor store 里的 action 全是 "writer" 语义（setNodes, updateNodeData, addNode, ...），Player 却在消费它。语义混乱 = 权限混乱。
- 在 crpg 的公开平台语义下，Player 和 Creator 是**不同的 principal**，不同的 security boundary，不同的 data surface。把它们缝进同一个 store 意味着任何未来的"玩家不能看到创作者编辑态字段"之类的合规要求**都需要横跨所有 store action 打补丁**。

**影响**：一旦做发布/审核，Editor store 和 Player store 的 partial rehydrate 规则、permission scope、data version 要分别维护。目前所有 daisy 的 test case 都是单用户 local 场景，这个架构从来没被跨 principal 压力测试过。

**架构层面的清理** → 见 §4 Cleanup #1。

---

### Mess #2: Visual DNA "10 层"在方法论里是文档概念，在架构里没有对应 module

**是什么**：`visual-dna-system.md` 定义了 10 层 Visual DNA，并说"每张图 prompt 都要注入这些层"。但在任何代码路径里，Visual DNA 不是一个**数据结构**——它是散落在方法论文档、YAML 示例、sample prompt 里的**人类可读设计稿**。没有一个 `visual_dna.json` 文件被任何代码读取，没有一个 `VisualDNASchema` 类型定义。

**证据**：
- `/Users/lxxxxxx/个人项目/crpg/assets/daisy-narrative-core/visual-dna-system.md`（10 层，21KB 文档）
- 方法论文档 §6 给了一份具体 YAML 但这份 YAML 从未被任何 code 引用
- daisy 的 `prompts.ts` 和 `ai.ts` 不知道 Visual DNA 的存在

**为什么乱**：方法论 doc 是"人类 Claude 会这样写 prompt"的**叙述性说明**，不是"机器代码会这样调度的 spec"。产品化要求 10 层被 reify 为 P2 pass 的具体输出 + P5 assembler 的具体输入。现在它悬空在纸面上。

**进一步问题**：10 层里，层 1/2/4/5/6/8 是**故事级常量**（生成一次，全故事复用），层 3 是**角色级常量+帧级选择**，层 7 是**物理 artifact**（anchor 图片），层 9 是**每节点的决策**，层 10 是**条件触发**。这些粒度不同的东西被平铺成"10 层"，掩盖了它们在架构中是**四种截然不同的角色**：
- 故事级配置（Layer 1,2,6 → `StyleConfig`）
- 角色级常量（Layer 3 → `CharacterRegistry`）
- 全局规则库（Layer 4,5,8,10 → `RuleLibrary`）
- 运行时决策（Layer 7,9 → Pipeline stage 输出）

**影响**：代码化时，开发者看"10 层"会以为这是 10 个并列的模块，写出 10 个 dict 字段平铺着拼 prompt，结果发现运行时根本不是这样工作。也会以为"新发现 bug 就加一层"，一路膨胀到 15 层、20 层，每层都得接进所有 pipeline stage。

**架构层面的清理** → 见 §4 Cleanup #2（把 10 层 re-cast 成 3 个架构 component）。

---

### Mess #3: Shot Director、Bug Taxonomy、Visual DNA 三者关系暧昧

**是什么**：三份方法论文档互相引用，但关系模糊：
- `shot-design-system.md` 说 "Visual DNA 增加第 9 层 Shot Design Layer"
- `text-to-image-bug-taxonomy.md` 说 "Bug Taxonomy 是 Shot Director LLM 的 system prompt 训练料"
- `visual-dna-system.md` 第 9 层是 Shot Design Layer，并且说"Director 自决 0-N shots"

所以 Shot Director 是：
- (a) Visual DNA 的一层？
- (b) Bug Taxonomy 的消费者？
- (c) Pipeline 的一个 stage（P4）？

答案是 (c)，但文档里混成 (a)+(b)+(c)。

**证据**：
- `shot-design-system.md` §7.1 把 Shot Design 列为 Visual DNA 第 9 层
- `text-to-image-bug-taxonomy.md` 最后"对 crpg 架构的启示"说 "Shot Director LLM 是核心护城河"
- `visual-dna-system.md` §8.5 表格把 Layer 9 和 Layer 10 也列进"Visual DNA"

**为什么乱**：
- **Visual DNA 是数据**（一份故事的视觉常量合集）
- **Shot Director 是 pipeline stage**（P4，对每个节点输出 shot list 的 LLM pass）
- **Bug Taxonomy 是规则 asset**（给 Shot Director 的 system prompt 用 + 给 P5 validator 用）

把 "数据 / stage / 规则" 三种角色塞进一个 flat 的 "Visual DNA 10 层" 层级系统，是概念 overloading。方法论笔记里这样写便于行文，但产品化时**必须拆**，否则代码里 `VisualDNA.layer9` 会是一个"每节点都要跑 LLM 的字段"，类型系统会爆炸。

**影响**：
- Shot Director 的模型选型（Q4-1）永远决定不了——因为它被混在 Visual DNA 里，讨论"哪个模型跑 Visual DNA"语义不通（Visual DNA 不是 LLM pass）。
- Bug Taxonomy 的演进路径不清：新 bug 是加到 Visual DNA 的新层（已在做），还是加到 Bug Taxonomy 的新 class，还是加到 Shot Director 的 system prompt？三个地方都有候选。

**架构层面的清理** → 见 §4 Cleanup #3（三元分离 + 明确 asset 血统）。

---

### Mess #4: Genre 子系统的位置完全未定

**是什么**：MEMORY 里明确 "Q3-1 = D：Genre 对用户透明，AI 从关键词推断"。但没说这个推断发生在哪个 pass、输出往哪里流：

- 它是 P1 Story Architect 的一个子任务？
- 还是 P1 之前的独立 Genre 推断 pass（P0）？
- 还是 P2 Visual DNA 阶段顺便推断（因为 Genre 也要影响视觉）？
- 推断结果是只改 prompt 的一段文本，还是写入 skeleton.meta.genre 成为 first-class data？

**证据**：
- `project_crpg_genre_decisions.md`：说 "Q3-2~Q3-6 全部未决"（Genre 知识库形态、Genre 是否同时驱动图像 prompt、推断时机、是否可见可覆盖）
- 代码层：daisy 的 `prompts.ts` 里完全没有 genre 概念，只有 `preset` (linear/bifurcating/funnel/web) 这种结构模板

**为什么乱**：Genre 在 McKee 理论里同时影响 **叙事 conventions**（→ P1 prompt）和 **视觉风格**（→ P2 Visual DNA）。如果不在架构里把 Genre 定位成 "skeleton.meta 的 first-class 字段，P1 产出，P2/P3/P4 消费"，它会在每个 pass 里被独立推断出不同答案（inconsistency），或者根本推不出来（P2 拿不到 P1 的上下文）。

**影响**：项目进入工程阶段时，Genre 会是第一个"发现方法论没法直接变成代码"的地方——因为 Q3-2~Q3-6 的每一个决策都影响不同 pipeline stage 的接口。

**架构层面的清理** → 见 §4 Cleanup #4。

---

### Mess #5: BYOK / 平台 key 的 handoff 架构缺失

**是什么**：MEMORY 明确 "创作者版二选一：平台 key 或 BYOK"。纯享版不涉及 key。但架构里没定义：

- key 存在哪？（Creator 账号上？Session 级？项目级？）
- 切换 key 的 UX 是什么？（页面刷新？对话框？全局开关？）
- 同一次生成过程中不同 stage 能不能用不同 key？（P1 用平台 key，P5 图像用 BYOK）
- BYOK 的账单和配额怎么可见？
- 平台 key 的 quota 在哪一层扣？（API gateway / router / Creator account）
- BYOK 的 key 泄露风险如何隔离？（server-side store / 每请求注入 / client-only）

**证据**：daisy 的 `services/ai.ts:7-18` 硬编码 `process.env.OPENROUTER_API_KEY`，只有一个 key。crpg 没有任何代码或文档定义 key 注入机制。

**为什么乱**：key 管理是 Compliance Layer 的**运行时责任**，也是 LLMRouter 的**每次调用的 precondition**。它不能推到"后面决定"——因为它决定 Router 的签名：`llmCall(passId, params, keyContext)` vs `llmCall(passId, params)`。

**影响**：工程启动时会卡在"第一次 API 调用如何拿到 key"，所有后续设计都被这个问题堵住。如果选错（例如把 BYOK key 存在 localStorage），整个安全模型崩盘（Creator key 被 XSS 偷），之后改回 server vault 要重构所有 call site。

**架构层面的清理** → 见 §4 Cleanup #5。

---

### Mess #6: daisy 的 published_stories 表不满足 StoryBundle 契约

**是什么**：daisy 有一张 `published_stories` 表（见 `db/schema.ts:44-60`），结构是：
```
id, title, description, authorName,
nodes (JSON), edges (JSON),
palette, moodCategory, worldSetting,
nodeCount, endingCount, playCount, likeCount,
publishedAt, updatedAt
```

这是 daisy "文字 + 氛围色"时代的 schema。crpg 的 StoryBundle 要求：Visual DNA + shots_by_node + assets blobs + compliance metadata + audit digest + signature。**缺失约 60% 的必要字段**。

**证据**：
- daisy `/tmp/crpg-research/daisy/packages/server/src/db/schema.ts:44-60`
- v2 reviewer 说 "纯享版 = daisy 已有 published_stories 表 + community feed 的成人改造"——**这句话在架构层面不成立**。daisy 的 published_stories 表记录的是"文字图 + 氛围色"，crpg 要记录的是一个含图像/审核/签名的 artifact。字段缺失 + 语义不同 + 版本化缺失 + 合规字段缺失。

**为什么乱**：v2 reviewer 把 "有一张叫 published_stories 的表" 等同于 "有发布机制"。架构上，发布机制 = StoryBundle contract 的持久化。daisy 的表是 "A 的持久化"，crpg 要的是 "B 的持久化"，A 和 B 结构不同数据不同。

**影响**：工程启动时如果按"小改 published_stories 表"的思路，会在加第 20 个字段时发现 schema 不对，要整表 migration。

**架构层面的清理** → 见 §4 Cleanup #6。

---

### Mess #7: 镜头一致性（image anchor）的存储和引用路径悬空

**是什么**：Visual DNA Layer 7 说"全故事一张 anchor 图，后续所有图用 image_url=anchor 做 style transfer"。但：

- anchor 图存在哪？（Creator 本地 blob？服务器 CDN？bundle 内？）
- anchor 的 URL 是 public 还是 signed？（如果 public，其他 Creator 能偷？）
- 生成 anchor 时如果质量不好，iterate 策略是什么？（重生成覆盖？保留多版本？）
- 多个 scene 的连续性：如果故事很长（50+ 节点，跨 act），一张 anchor 够吗？还是每 act 一张？方法论说"全故事 1 张"，但 §8.5 又说"Style Preamble 分故事阶段"——矛盾。

**证据**：
- `visual-dna-system.md` Layer 7 = "全故事 1 张 style anchor"
- `visual-dna-system.md` §8.5 表格 Layer 1 = "分故事阶段（建置/冲突/余波各一套）"
- Bonus 晨光图证明阶段化 preamble 有用

**为什么乱**：anchor 和 style preamble 都是"故事级视觉锚点"，但一个被定义为"全故事 1 个"，另一个被定义为"分 3-5 阶段"。粒度不一致意味着运行时无法 reconcile：如果 preamble 按阶段切换但 anchor 不变，后半段的 style transfer 会拉回前半段的视觉 → preamble 切换无效。

**影响**：生成 20+ 节点故事时，中后期镜头会被早期 anchor 拖回早期色调，value arc 的视觉演进做不出来。

**架构层面的清理** → 见 §4 Cleanup #7。

---

### Mess #8: Creator 端"3-pass LLM"和 daisy 现有"2-step pipeline"的接线未定

**是什么**：crpg 方法论说 pipeline 是 P1/P2/P3/P4 + P5/P6/P7。daisy 现有 pipeline 是 `POST /generate/skeleton` + `POST /generate/content`（2 步）。方法论没说：

- daisy 的 `/generate/skeleton` 对应 crpg 的 P1？还是 P1+P2 合体？
- daisy 的 `/generate/content` 对应 crpg 的 P3？
- 新的 P2 (Visual DNA) / P4 (Shot Director) 是在现有 batch loop 里并入，还是独立 endpoint？
- 前端 `useAIGenerate.ts` 的 progress 状态 `'idle'|'skeleton'|'content'|'done'` 够不够？还是要扩展成 `'idle'|'skeleton'|'vdna'|'content'|'shots'|'images'|'done'`？

**证据**：
- daisy `/tmp/crpg-research/daisy/packages/server/src/routes/ai.ts`（3 个 endpoints：generate/skeleton/content + continue）
- daisy `/tmp/crpg-research/daisy/packages/web/src/hooks/useAIGenerate.ts:22-26`
- crpg 方法论文档：没有 endpoint 级别的指定，只有 pipeline 图

**为什么乱**：daisy 的 2 步设计思想是"脆弱结构先保护"。crpg 的 4 步是"加视觉 + 加镜头"。两者在 architecture 级有继承关系，但**接线图**没画。

**影响**：前端状态机、后端 endpoint 组织、progress indication UX 都要依赖这个接线图。没有它，前端会先写一个"占位"的 `vdna` 阶段，后端 endpoint 按占位设计，3 个月后发现 P2 和 P1 其实应该合成一个 call 更经济（少一次 token），整套 state machine 重构。

**架构层面的清理** → 见 §4 Cleanup #8。

---

### Mess #9: 方法论文档散落 15 份，没有"canonical pipeline spec"

**是什么**：`assets/daisy-narrative-core/` 下有 15 份文档：
- `mckee-full-framework.md`
- `pipeline-comparison.md`
- `design-rationale.md`
- `detail-and-poetic-modes.md`
- `visual-dna-system.md`
- `shot-design-system.md`
- `shot-types-vocabulary.yaml`
- `text-to-image-bug-taxonomy.md`
- `visual-aesthetic-axes.md`
- `visual-aesthetics.yaml`
- `prompts-v3.ts` / `v4.ts` / `v6.ts`（daisy 原文）
- `example-story-镜廊杀局.md`
- `result_anti_melodrama.yml`

每份文档都在自己的 narrative 里完整，但**没有一份描述整个 system 的 canonical contract**。例如：如果开发者要实现 P2 Visual DNA Synthesis pass，他要读 visual-dna-system.md（10 层定义）+ shot-design-system.md（§7.1 说 VDNA 需要加第 9 层）+ text-to-image-bug-taxonomy.md（VDNA 要对应解决哪些 bug）+ visual-aesthetic-axes.md（VDNA.aesthetic_axis 候选集）——**读 4 份文档才能拼出一个 pass 的 spec**，而且这 4 份文档的说法不完全一致（见 Mess #2/#3/#7）。

**为什么乱**：这些文档是 brainstorm 过程的沉积，是"思考轨迹"而不是"产品规格"。用户想从这里去工程化，必然要再写一份 canonical spec。但**现在没有**。

**影响**：任何工程师（或新的 AI agent）进入项目都要花 1-2 天读这 15 份文档才能参与讨论，而且不同工程师对同一个概念的理解会不同（Shot Director 到底是 VDNA 的一层还是独立 stage？）。

**架构层面的清理** → 见 §4 Cleanup #9（整合成 3 份 spec）。

---

### Mess #10: daisy 的 `preset` + `complexity` + `contentLength` + `detailRichness` 四维参数和 crpg 的新参数的关系未清

**是什么**：daisy 有 4 个生成参数（`preset`/`complexity`/`contentLength`/`detailRichness`），每个有 4-5 个可选值，组合空间 4×5×3×4=240。这些参数直接影响 `buildSkeletonPrompt` 的输出节点数、每节点字数等。

crpg 要加：`explicitness_dial`（suggest/direct）、`aesthetic_axis_preference`（24 子派）、可能的 Genre 推断覆盖、`shot_budget_scale`（影响 Shot Director 每节点 shot 数）。

这些新参数是**扩展 daisy 参数集**还是**独立一组**？在 Generate UI 上一起露出还是分层露出？对 prompt 的影响是**相乘**还是**独立注入**？

**证据**：
- daisy `prompts.ts:5-27`（4 参数）
- daisy `/tmp/crpg-research/daisy/packages/web/src/components/editor/GenerateDialog.tsx`（UI 露出 4 参数）
- crpg MEMORY `project_crpg_mckee_additions.md`：Q3-1 Genre 对用户透明，`project_crpg_model_strategy.md`：按 Genre/露骨度路由

**为什么乱**：参数空间扩张从 240 到 ~1000+ 组合，每个组合能否产生有意义的结果没有定义。Generate UI 复杂度会失控。更根本的是：**daisy 的参数（preset/complexity/length/detail）是结构参数，crpg 的参数（genre/aesthetic/explicitness）是内容参数**——两种不同性质的东西平铺在一个 dialog 里会让 UX 和 prompt 组装都混乱。

**影响**：UX 设计、prompt 组装、路由决策都纠缠不清。

**架构层面的清理** → 见 §4 Cleanup #10。

---

### Mess #11: Compliance Layer 在架构里是"被应该有"而不是"已经被定位"

**是什么**：硬红线 5 条（18+ gate / 绝对禁区 / 地区合规 / 审计可追溯 / 模型侧合规）都被写在 SESSION-STATE 和 MEMORY 里。但没有任何文档定义：

- 它是 middleware（HTTP 层拦截）？还是 domain service（业务逻辑调用）？还是都有？
- 它的 data model 是什么？（audit_log 表？geo_policy 配置？age_gate session 状态？）
- 它和 Pipeline 的 5 个 stage 的关系：Pipeline 是"调用 compliance 函数"还是"被 compliance middleware 包裹"？

**证据**：SESSION-STATE §二 "工程硬红线"、MEMORY `project_crpg_model_strategy.md`。没有 compliance 相关的代码文件或数据 schema 文档。

**为什么乱**：合规不是 feature，是**横切关注点**。它应该在架构拓扑中是一层独立的 cross-cutting concern，每条硬红线 对应一个固定的 hook point（session / input / prompt / output / publish）。现在它是"一组待办的需求"。

**影响**：进入工程阶段时，每个开发者会在自己的模块里"顺手写"合规检查，结果合规规则分散 15 处，每次新增规则要改 15 处代码。这是经典的 "cross-cutting concern 没有抽象层" 反模式。

**架构层面的清理** → 见 §4 Cleanup #11。

---

### Mess #12: "纯享版 = 零生成" 这条硬约束与"daisy PlayMode 读 editorStore"的底层耦合

**是什么**：I-1 硬约束要求纯享版运行时零调用。但 daisy PlayMode 架构上还保留了 AmbientTheme 的"从文字提取关键词 → 映射调色板"过程（`useAmbientTheme.ts`），虽然不调 AI，但它是**内容 derivation**（虽然是纯 JS 的 derivation，但概念上等价）。

这不是 bug，是**架构语义**问题：纯享版应该只播放 bundle 里**已烘焙好的** visual 状态，还是允许某些轻量 derivation 在客户端发生？

**证据**：`/tmp/crpg-research/daisy/packages/web/src/hooks/useAmbientTheme.ts`（60 行，从 nodes 的 content 提取情绪关键词，纯前端 JS）

**为什么乱**：如果允许客户端 derivation，未来"纯享版从 bundle 的文字里抽关键词再去 CDN 查相关推荐"就可能被合理化，慢慢侵蚀"零调用"边界。如果不允许，所有 ambient palette 必须在 P7 Bundle Packer 里烘焙成静态值，写死进 bundle。

**影响**：这个决策影响 StoryBundle 的字段（palette 是否是 derived 字段）和 Player App 的架构（是否允许任何纯前端的 analytical derivation）。

**架构层面的清理** → 见 §4 Cleanup #12。

---

## 4. Architectural Cleanup Plan（架构级清理）

对应 §3 的每个 Mess。**这不是工期表，是架构决策**。

### Cleanup #1 (→ Mess #1): 创作者端和玩家端是两个独立应用

**决策**：
- **Creator App** = 现有 daisy 前端 + 扩展，路径 `/studio`，需要登录 + 18+ gate
- **Player App** = 独立的 React 应用（或同一 monorepo 不同 entry），路径 `/play`，只需 18+ gate，无登录
- 两个 app **绝对不共享 Zustand store**
- 共享**三样东西**：
  1. `StoryBundle` 类型定义（`packages/shared/types`）
  2. 若干 pure 渲染 component（节点类型的渲染 component 可以复用）
  3. D20 runtime（`useGameLoop` + `useDiceRoll` + `playerStore` 可复用）
- daisy 的 `useEditorStore` 保留在 Creator App 里，成为**纯编辑态 store**，不被 Player 使用
- Player App 有自己的 `usePlaybackStore`，从 `StoryBundle` rehydrate，只读

**这不是 "两套代码"**。共享部分提到 `packages/shared`，具体 separator 见 §5 的 module diagram。

**对方法论文档的影响**：无（方法论本来就假设两端分离，只是 daisy 代码实现把它们合并了）。

---

### Cleanup #2 (→ Mess #2): 把 "Visual DNA 10 层" re-cast 成 3 个架构 component

**决策**：删除"10 层 Visual DNA"这种 flat 列表，重新按**架构角色**分类：

```
原 Layer 1 (Style Preamble)         ─┐
原 Layer 2 (Aesthetic Axis)          ├──→ StoryStyleConfig (故事级 config)
原 Layer 6 (Technical Lock)         ─┘
原 Layer 4 (Recurring Motifs)       ─┐
原 Layer 5 (Positive Framing)        ├──→ RuleLibrary (全局规则库 + 故事级 binding)
原 Layer 8 (Direction Layer)        ─┘
原 Layer 3 (Character Sheets)         ──→ CharacterRegistry (角色表 + partial_presence)
原 Layer 7 (Anchor Strategy)          ──→ AnchorAsset (Pipeline P2 的 artifact)
原 Layer 9 (Shot Design Layer)        ──→ Pipeline Stage P4 (Shot Director LLM) ❌ 不是 VDNA
原 Layer 10 (Layered Garment)        ──→ RuleLibrary 的子 asset + P5 触发条件
```

**新 VisualDNA 数据结构**（简化版，见 §2.4 Contract B）：
```ts
VisualDNA = {
  style_config: StoryStyleConfig       // 从 layer 1/2/6 合成
  character_registry: CharacterRegistry // 从 layer 3 转化
  rule_binding: RuleBinding             // 指向 RuleLibrary 里选中的规则
  anchor: AnchorAsset                   // layer 7 的物理 asset 引用
}
```

Layer 9 (Shot Design) **从 VDNA 里剥出**，回到 Pipeline Stage P4 的独立身份。
Layer 10 (Layered Garment) **从 VDNA 里剥出**，成为 RuleLibrary 里的一条 rule，在 P5 Prompt Assembler 按条件触发。

**对方法论文档的影响**：`visual-dna-system.md` 需要 refactor，"10 层"表格改成"3 个 component + 1 个 pipeline stage + 1 个 conditional rule"。这个 refactor **不是 tactical 任务**，是**架构 clarity 的先决条件**。

---

### Cleanup #3 (→ Mess #3): 三元分离：Data / Stage / Asset

**决策**：明确三个概念的 asset 血统：

| 概念 | 角色 | 血统 | 生命周期 |
|---|---|---|---|
| **Visual DNA** | 数据对象 | 每个故事一份 | 与 Story 同生共死 |
| **Shot Director** | Pipeline stage（P4） | 代码+system prompt | 代码版本 + system prompt 版本 |
| **Bug Taxonomy** | 规则 asset（RuleLibrary 的一部分） | 全局 registry | 独立版本化，跨项目/跨故事复用 |

**Bug Taxonomy 的新定位**：
- 它是 `RuleLibrary.bug_guards` 的 canonical asset（不是 Shot Director 的私有 training 料）
- 每条 bug class（A/B/C/D/E/...）是一个**规则条目**，包含：
  ```ts
  BugGuard = {
    id: 'D_default_prior',
    detector_hint: string      // 给 Shot Director 的 system prompt 看
    assembler_validator: Fn    // 给 P5 的 pure validator
    remediation_template: string  // 被触发时插入的 positive-framing 片段
  }
  ```
- 这样 P4 (Shot Director) 和 P5 (Assembler) 都可以**按 id 引用同一条规则**，新发现的 bug 加到 RuleLibrary，两个 stage 自动适配

**对方法论文档的影响**：`text-to-image-bug-taxonomy.md` 的描述层级修正：不是"给 Shot Director 的 system prompt"，而是"RuleLibrary 的 canonical 条目，Shot Director 和 Assembler 共同消费"。

---

### Cleanup #4 (→ Mess #4): Genre 是 P1 的 first-class output

**决策**：
- **Genre 推断放在 P1 Story Architect 内部**（不是 P0，不是 P2）
- Genre 推断的结果写入 `StorySkeleton.meta.inferred_genre`（String），和 `aesthetic_axis_hint`（可选建议）
- P2 Visual DNA 读 `skeleton.meta.inferred_genre` 来决定 `aesthetic_axis` 的候选集
- P3/P4 读 `skeleton.meta.inferred_genre` 来决定 genre conventions（obligatory scenes 检查等）
- **Genre 不单独跑一个 LLM pass**——这样省 1 次 token 成本，避免 Genre 推断结果和 P1 骨架不一致
- 对用户**默认透明**（Q3-1 = D），但在 Creator App 的 "Advanced" 面板可以 override

**对方法论文档的影响**：`project_crpg_genre_decisions.md` 的 Q3-2~Q3-6 可以一次性回答：
- Q3-2（知识库形态）：prompt 内嵌 + 未来扩展为 YAML rule library
- Q3-3（是否同时驱动图像）：yes，通过 `skeleton.meta.inferred_genre` → VDNA 选 axis
- Q3-4（推断时机）：P1 内部，和骨架同一 call
- Q3-5（对用户可见可覆盖）：默认透明，Advanced 可覆盖
- Q3-6（混合 Genre）：P1 可输出 `primary + secondary`

---

### Cleanup #5 (→ Mess #5): BYOK/平台 key 的架构是 KeyVault + RequestContext

**决策**：
```
KeyVault (server-side, encrypted)
    │
    ├── Creator 账号下有 0-N 个 BYOK 条目：{ provider, key_encrypted, alias }
    ├── 平台 key 是 vault 的 "system" 条目，不属于任何 Creator
    │
    ▼
RequestContext (per-generation)
    │
    ├── 生成开始时，Creator UI 选择 "use platform key" or "use BYOK: <alias>"
    ├── Context 包含 { creator_id, key_ref: 'system' | 'byok:<alias>', pipeline_spec }
    ├── 同一次生成中的所有 pass (P1..P6) 共用同一个 key_ref（简化安全模型）
    │
    ▼
LLMRouter 每次 call 从 RequestContext 拿 key_ref → 向 KeyVault 拿实际 key → 注入 provider client
```

**关键约束**：
- BYOK key **绝不出现在前端代码或 HTTP response**（只存服务器 vault，以 id 引用）
- BYOK 和平台 key **二选一、不混用**（简化成本归属、简化审计）
- Quota 在 LLMRouter 拦截（平台 key 有月度预算，BYOK 不限量但做速率限制）

**对方法论文档的影响**：MEMORY `project_crpg_model_strategy.md` 里的 API Key 归属段可以升级为 "KeyVault + RequestContext" 模式。

---

### Cleanup #6 (→ Mess #6): StoryBundle 是 daisy published_stories 的 superset，不是 alias

**决策**：
- **不复用 daisy 的 `published_stories` 表** schema。crpg 新建 `story_bundles` 表，schema 对应 StoryBundle contract（见 §2.4 Contract C）。
- daisy 的 `published_stories` 可以保留作为 "legacy bundle" import 通路，但 crpg 核心是 `story_bundles`。
- **StoryBundle 是 artifact，不是 DB 记录**：表里存 manifest + 链接（到 CDN 上的 JSON + image blobs），不是把所有 node/edge/image 都塞在一行里。
- Bundle immutable：Creator 改 → 新 bundle_id，旧 bundle 继续存活。

**新 schema 概要**：
```
story_bundles:
  bundle_id, creator_id, title, manifest (JSON), 
  content_rating, geo_restrictions (JSON),
  bundle_manifest_url, bundle_signature,
  published_at, unlisted_at, parent_bundle_id

story_bundle_versions:
  version_id, bundle_id, manifest_url, published_at

play_events:
  event_id, bundle_id, session_id, node_id, event_type, ts
  (audit + analytics)
```

**对方法论文档的影响**：之前 v2 reviewer 说 "纯享版 = daisy community feed 成人改造" 在架构层面不成立，需要重写。

---

### Cleanup #7 (→ Mess #7): Anchor 和 Style Preamble 粒度对齐

**决策**：三选一，必须选一：

- **选项 A**：全故事 1 个 anchor + 1 个 preamble（最简单，视觉不随 value arc 演进）
- **选项 B**：按 act 切（3 个 anchor + 3 个 preamble，每个 act 一致）← 推荐
- **选项 C**：按 scene 切（每个 scene 一个 anchor，成本和一致性冲突）

**推荐 B**：
- P2 Visual DNA 输出 `style_config.preamble_per_act: { act_1: ..., act_2: ..., act_3: ... }`
- P6 Image Worker 生成 3 张 anchor（每 act 1 张）
- P5 Prompt Assembler 按 `node.actIndex` 选择 preamble + anchor_url
- bundle 里存 3 张 anchor

**理由**：McKee 故事结构就是 act 为单位，value arc 在 act 间 turn。视觉跟随 act 切换符合叙事逻辑。晨光图 bonus 已经证明可行。

**对方法论文档的影响**：`visual-dna-system.md` §8.5 表格 Layer 1 ("分故事阶段")和 Layer 7 ("全故事 1 张")改成 "分 act"，两者粒度统一。

---

### Cleanup #8 (→ Mess #8): Pipeline endpoint 映射表

**决策**：
```
crpg Pipeline stage     ←→     HTTP endpoint            ←→    Frontend state
P1 Story Architect             POST /api/pipeline/skeleton     'skeleton'
P2 Visual DNA                  POST /api/pipeline/vdna         'vdna'
P3 Content Filler              POST /api/pipeline/content      'content' (batch 5 nodes)
P4 Shot Director               POST /api/pipeline/shots        'shots'   (batch 5 nodes)
P5 Prompt Assembler            (server-side pure function)      —
P6 Image Batch Worker          POST /api/pipeline/images        'images'  (async job)
P7 Bundle Packer               POST /api/pipeline/publish       'publishing'
```

**关键约束**：
- P1 和 P2 **可以合并成一次 LLM call**（同一个 Sonnet call 同时输出 skeleton 和 VDNA seed），作为优化，但**endpoint 保持分离**（逻辑解耦、失败重试粒度可控）。
- P3 和 P4 **必须分离**（P3 产出 content 才能给 P4 用作 shot breakdown 的输入）。
- P6 是 **async job**，不阻塞前端（Q4-2 的答案：A 异步）。
- 前端 state machine 扩展为 `'idle' | 'skeleton' | 'vdna' | 'content' | 'shots' | 'images' | 'packing' | 'done' | 'error'`。

**对 daisy 代码的影响**：`useAIGenerate.ts:22-26` 的 GenerateProgress 扩展；`routes/ai.ts` 加 4 个新 endpoints（或把现有 2 个拆成 6 个）。

---

### Cleanup #9 (→ Mess #9): 方法论 15 份 → canonical 3 份

**决策**：方法论文档整合成 3 份 canonical spec + 若干 reference 附录：

**Spec 1: `PIPELINE-ARCHITECTURE.md`**（新写）
- 整个 content pipeline 的唯一权威 spec
- P1-P7 每个 stage 的 contract
- 数据契约 A/B/C（见 §2.4）
- LLMRouter 规格
- 合规插入点 CP-1~CP-4

**Spec 2: `VISUAL-SYSTEM.md`**（refactor from visual-dna + shot-design + bug-taxonomy + aesthetic-axes + aesthetics yaml）
- 新分类：StoryStyleConfig / CharacterRegistry / RuleLibrary / AnchorAsset
- Shot 词汇表（shot-types-vocabulary.yaml 作为附录）
- Bug Taxonomy（重新定位为 RuleLibrary.bug_guards）
- 24 美学轴 YAML（保留作为 reference）

**Spec 3: `NARRATIVE-SYSTEM.md`**（refactor from mckee + pipeline-comparison + detail-and-poetic + design-rationale）
- daisy 六条硬约束 + crpg 补三条（Genre/Antagonism/Climax）
- 两步生成哲学 → 在 crpg 里如何升级成 P1+P2+P3+P4
- 诗意/细腻/极致模式的粒度决策
- 节点类型规范

**保留**（作为 reference，不是主读文档）：
- `prompts-v3/v4/v6.ts`（daisy 原文 system prompts）
- `example-story-镜廊杀局.md`（实例参考）
- `visual-aesthetics.yaml`（24 子派库）
- `shot-types-vocabulary.yaml`（shot 词汇）

**对方法论文档的影响**：其余 15 份"合并或归档"。工程启动时只有 3 份 canonical spec 被引用，其他是深度研究时才读的背景料。

---

### Cleanup #10 (→ Mess #10): 参数分层：结构参数 / 内容参数 / 视觉参数

**决策**：Generate UI 的参数分成 3 组，UX 上分层：

**Layer 1 (Required)**：`keywords` + `explicitness_dial`（suggest/direct）
**Layer 2 (Story Shape)**：`preset` / `complexity` / `contentLength` / `detailRichness`（daisy 原参数）
**Layer 3 (Advanced, collapsed by default)**：`aesthetic_axis_override` / `genre_override` / `poeticMode` / `shot_budget_scale`

在 prompt 组装层，3 组参数进入不同 stage：
- Layer 1 → 所有 stage 都看到
- Layer 2 → P1 + P3 消费（结构和密度）
- Layer 3 → P2 + P4 消费（视觉和镜头）

**对代码的影响**：`GenerateDialog.tsx` 重构为 3 段式 UX；`buildSkeletonPrompt` 的入参拆成 `StructureParams` / `ContentParams` / `VisualParams` 三个 interface。

---

### Cleanup #11 (→ Mess #11): Compliance Layer 是 middleware + 4 个固定 hook

**决策**：Compliance Layer 实现为**独立 package**（`packages/compliance`），包含：

```
compliance/
  ├── age-gate/          (CP-1)
  │    ├── session-guard middleware (both apps)
  │    └── AgeGateModal component
  ├── geo-policy/         (CP-1)
  │    ├── policy.yaml (country → allowed/blocked/soft-block)
  │    └── geoGuard middleware
  ├── input-validator/    (CP-2)
  │    ├── blocklist.yaml (minor terms / real persons / etc.)
  │    └── validateInput function (pure)
  ├── prompt-validator/   (CP-3)
  │    ├── assembled-prompt scanner
  │    └── cross-scene contamination detector
  ├── publish-gate/       (CP-4)
  │    ├── auto-checks (contentRating, banned terms)
  │    └── manual-review queue hook
  └── audit-writer/       (side effect)
       └── async queue → audit log sink
```

每个 hook 暴露一个 pure function / middleware，Pipeline 和 App 按固定位置调用。

**对架构的影响**：项目根目录的 monorepo 结构里多一个 package，`Pipeline` 和 `Creator/Player App` 都声明依赖 `compliance`。

---

### Cleanup #12 (→ Mess #12): Player App 零 derivation 原则

**决策**：**所有 ambient / palette / analytic derivation 在 P7 Bundle Packer 里烘焙**。

- `useAmbientTheme` 的 derivation 逻辑从客户端移到 P7
- Bundle 里 `visual.palette` 是**静态字段**，不是 derived
- Player App 的 Zustand store 只有 playback 状态（current node / history / dice），没有 derivation effect

**例外**：玩家的**个人选择产生的 derivation**（比如 character name 注入到 content 里）允许在客户端发生——这是"个人化 rendering"，不是"内容 derivation"。

**对代码的影响**：
- Creator App 保留 `useAmbientTheme`（创作者 preview 时实时算）
- Player App 不引入 `useAmbientTheme`，直接读 bundle 的 palette

---

## 5. One-Page Mental Model

（用户读这一页应该能看到整个系统）

### 5.1 Canonical 架构图（清理后）

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         COMPLIANCE LAYER (cross-cutting)                    │
│  AgeGate │ GeoPolicy │ InputValidator │ PromptValidator │ PublishGate │ Audit│
└─────────────────────────────────────────────────────────────────────────────┘
       │          │            │              │               │          │
  [CP-1]     [CP-1]        [CP-2]         [CP-3]          [CP-4]    (async)
       │          │            │              │               │          │
┌──────▼──────────▼────┐ ┌─────▼─────────────┐▼───────────────▼──┐       │
│                      │ │                                       │       │
│   CREATOR APP        │ │         CONTENT PIPELINE              │       │
│   (/studio)          │ │                                       │       │
│                      │ │  P1 Architect ──┬──▶ P2 Visual DNA   │       │
│   • Canvas (RF)      │ │                 │                    │       │
│   • GenerateDialog   │ ├──submit────────▶│                    │       │
│   • NodeEditor       │ │                 ▼                    │       │
│   • PublishDialog    │ │       P3 Content ──┬── P4 Shot Dir   │       │
│   • editorStore ✓    │ │                    │                 │       │
│                      │ │                    ▼                 │       │
│   Stateful on client │ │         P5 Assembler (pure)          │       │
│   Zustand + persist  │ │                    │                 │       │
│                      │ │                    ▼                 │       │
│                      │ │         P6 Image Batch Worker        │       │
│                      │ │                    │                 │       │
│                      │ │                    ▼                 │       │
│                      │ │         P7 Bundle Packer             │       │
│                      │ │                                       │       │
│                      │ │  LLMRouter (Sonnet/Grok by pass)     │       │
│                      │ │  KeyVault (platform vs BYOK)         │       │
│                      │ └───────────────────┬───────────────────┘       │
│                      │                     │                           │
│                      ◀─────────preview─────┤                           │
│                      │─────────publish─────▶                           │
│                                            ▼                           │
│                            ┌────────────────────────────┐              │
│                            │  STORY BUNDLE STORE (CDN) │              │
│                            │  + story_bundles (SQLite) │◀─────────────┘
│                            │  immutable, signed        │              
│                            └───────────────────────────┘              
│                                            │                          
│                                    (read-only)                        
│                                            ▼                          
│                            ┌───────────────────────────┐              
│                            │      PLAYER APP (/play)   │              
│                            │                           │              
│                            │   • loadBundle(id)        │              
│                            │   • PlayScene/Choice/Check│              
│                            │   • playerStore (D20)     │              
│                            │   • playbackStore         │              
│                            │   • injectPlayerName      │              
│                            │                           │              
│                            │   ZERO LLM/image calls    │              
│                            │   ZERO billing            │              
│                            └───────────────────────────┘              
└─────────────────────────────────────────────────────────────────────────────┘
```

### 5.2 方法论文档 → 架构 component 映射表

| 方法论文档 | 归属 canonical 位置 |
|---|---|
| `mckee-full-framework.md` | `Spec 3: NARRATIVE-SYSTEM.md` |
| `pipeline-comparison.md` | 合并进 `Spec 1: PIPELINE-ARCHITECTURE.md` |
| `design-rationale.md` | 归档为 reference |
| `detail-and-poetic-modes.md` | 合并进 `Spec 3: NARRATIVE-SYSTEM.md` |
| `visual-dna-system.md` | **refactor** → `Spec 2: VISUAL-SYSTEM.md` + Cleanup #2 |
| `shot-design-system.md` | **refactor** → `Spec 2: VISUAL-SYSTEM.md` + 对应 P4 Shot Director |
| `shot-types-vocabulary.yaml` | `Spec 2` 附录 |
| `text-to-image-bug-taxonomy.md` | **reposition** → RuleLibrary.bug_guards（`Spec 2`） |
| `visual-aesthetic-axes.md` | `Spec 2` 附录 |
| `visual-aesthetics.yaml` | `Spec 2` 附录（24 子派数据） |
| `prompts-v3.ts / v4.ts / v6.ts` | reference only（daisy 原文 system prompts） |
| `example-story-镜廊杀局.md` | reference only |
| `result_anti_melodrama.yml` | reference only |

### 5.3 daisy 代码 → 架构 component 映射表

| daisy 代码 | 属于新架构的 |
|---|---|
| `services/ai.ts` (247 行) | **LLMRouter 的底层 Provider Adapter**（保留 JSON extraction、截断检测、edge normalization 逻辑） |
| `services/prompts.ts` (799 行) | **P1 + P3 Prompt Builder**（保留结构，加 McKee 三补丁和 genre 字段） |
| `routes/ai.ts` (162 行) | **Pipeline endpoints P1/P3**（+ 新加 P2/P4/P6/P7） |
| `routes/projects.ts` / `routes/nodes.ts` | **Creator App 的 editor state API**（仅服务创作者编辑态，和 Player App 无关） |
| `routes/community.ts` (145 行) | **部分归 Bundle Store** (feed API)、**部分弃用**（published_stories schema 不够用） |
| `db/schema.ts` 5 张表 | `projects/nodes/edges/characters` 保留作创作者编辑态；`published_stories` **弃用**，换为新的 `story_bundles` 表 |
| `stores/editorStore.ts` | **Creator App 专属** |
| `stores/playerStore.ts` | **Player App 专属**（D20 + 27 点） |
| `stores/communityStore.ts` | **Player App 的 bundle feed store**（schema 需升级） |
| `hooks/useAIGenerate.ts` | **Creator App 的 Pipeline 触发 hook**（扩 state machine 到 8 状态） |
| `hooks/useGameLoop.ts` / `useDiceRoll.ts` | **Player App 专属**，但也可给 Creator 的 preview 模式复用 |
| `hooks/useAmbientTheme.ts` | **移到 P7 Bundle Packer**（或保留作为 Creator preview 工具，Player 不用） |
| `components/editor/*` | **Creator App**（Canvas / GenerateDialog / Toolbar） |
| `components/play/*` | **Player App**（PlayMode / PlayScene / PlayChoice / PlayCheckScene / PlayEnding） |
| `components/community/*` | **Player App**（CommunityFeed = Bundle browser）+ Creator App（PublishDialog） |
| `components/nodes/*` | **共享 package**（两端都用的 React Flow node 渲染） |
| `lib/i18n.ts` | **共享 package** |
| `lib/moodEngine.ts` / `lib/paletteUtils.ts` | **P7 Bundle Packer 的 derivation 模块**（不在 Player App 运行时） |
| `lib/pathValidator.ts` | **P1 output validator**（Pipeline 内部） |
| `lib/exportUtils.ts` | **P7 Bundle Packer 的序列化模块** |

### 5.4 混乱点（红叉）vs 清理后（绿勾）

```
┌───────────────────────────────────────────────────────────────┐
│                   现状 (Red Cross)                            │
├───────────────────────────────────────────────────────────────┤
│                                                               │
│  ❌ Editor 和 Player 共用 store (Mess #1)                     │
│  ❌ Visual DNA 10 层平铺 (Mess #2)                            │
│  ❌ Shot Director = VDNA 一层 / Pipeline stage / 训练料       │
│     三位一体暧昧 (Mess #3)                                    │
│  ❌ Genre 悬空 (Mess #4)                                      │
│  ❌ BYOK 架构未定 (Mess #5)                                   │
│  ❌ published_stories 以为能直接用 (Mess #6)                  │
│  ❌ Anchor 粒度与 Preamble 粒度不一致 (Mess #7)               │
│  ❌ 新 pipeline 和 daisy 2 步未接线 (Mess #8)                 │
│  ❌ 15 份方法论文档散落 (Mess #9)                             │
│  ❌ 参数扁平膨胀 (Mess #10)                                   │
│  ❌ 合规层悬空 (Mess #11)                                     │
│  ❌ 纯享版 derivation 边界未定 (Mess #12)                     │
│                                                               │
└───────────────────────────────────────────────────────────────┘

┌───────────────────────────────────────────────────────────────┐
│                清理后 (Green Check)                           │
├───────────────────────────────────────────────────────────────┤
│                                                               │
│  ✓ Creator App + Player App = 两个独立应用，共享 contract    │
│  ✓ Visual DNA = StyleConfig + CharRegistry + RuleLibrary      │
│     + AnchorAsset（不再是 10 层）                             │
│  ✓ Shot Director = Pipeline P4 (LLM pass)                     │
│     Bug Taxonomy = RuleLibrary.bug_guards 的条目              │
│  ✓ Genre = skeleton.meta.inferred_genre（P1 输出）            │
│  ✓ BYOK = KeyVault + RequestContext.key_ref                   │
│  ✓ StoryBundle = 新的 story_bundles 表 + CDN blobs            │
│     （不是 daisy published_stories 的改造）                   │
│  ✓ Anchor 和 Preamble 都按 act 切                             │
│  ✓ Pipeline = P1..P7 + 7 个 endpoint（Cleanup #8 映射表）     │
│  ✓ 方法论 = 3 份 canonical spec + 若干附录                    │
│  ✓ 参数 = 3 层 UX (Required / Story / Advanced)               │
│  ✓ Compliance = 独立 package + 4 个固定 CP                    │
│  ✓ Player App = 零 derivation，所有视觉烘焙在 P7              │
│                                                               │
└───────────────────────────────────────────────────────────────┘
```

---

## 6. 一段话总结（给朋友解释）

> crpg 是"创作者用 AI 从一句话生成一份图文互动小游戏，然后免费分享给别人玩"的平台。系统有两端：**Creator 端**跑一条 7 段式的 AI 流水线（先骨架、再视觉 DNA、再填正文、再分镜、再拼 prompt、再出图、再打包），产出一份自包含的"故事 bundle"；**Player 端**只是一个零 AI 调用的播放器，加载 bundle 就能免费玩。关键是把"视觉一致性"的方法论（色戒式分镜 + 身份锚 + bug 预警库）固化成流水线里 3 个具体模块，不是散落在文档里。18+ / 审计 / 地区合规作为一层独立的 middleware 穿透两端。

---

## 附：这份审查的边界

这份文档回答的是：
- **现在的系统架构是什么样**（从目的倒推）
- **现有的方案文档和代码在架构图里位于哪里**
- **哪些地方的 concept 被错误地合并 / 错误地分离 / 粒度不一致 / 悬空**
- **在架构层面怎么把每条混乱关掉**

这份文档**不回答**：
- 应该先做哪一步（请看其他 reviewer 的 tactical 建议或自己决定）
- 项目能不能 12 周 ship（请看战略 reviewer）
- 哪份方法论文档"值得保留"（用户已经说过保留哪三件）
- 代码里哪些 bug 要修（请看代码 auditor）

如果读完这份文档你觉得"架构终于清楚了"，它达到了目的。如果你觉得"又来一个告诉我怎么做的"，请告诉作者失败在哪。
