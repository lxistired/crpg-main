# Daisy 叙事核心 —— V3 / V4 / V6 三版 Pipeline 对比

目的：把 daisy 三个版本的"叙事核心"完整扒出来，理清楚每一条差异是**架构差异**（调用拓扑）还是**Prompt 内容差异**（注入给 Claude 的自然语言），为新项目 `crpg` 决定"继承哪些、重做哪些"提供事实基础。

原始文件已镜像到本目录：
- `prompts-v3.ts` (414 行) — 来自 `daisy-crpg` 仓库，端口 3003，V3
- `prompts-v4.ts` (597 行) — 来自 `daisy` 仓库，端口 3002，V4 对照实验
- `prompts-v6.ts` (799 行) — 来自 `daisy` 仓库，端口 3001，**当前生产**
- `design-rationale.md` — 原作者自己的设计拆解（internal-post）

---

## 1. Pipeline 调用拓扑对比

### V3 —— 单步生成
```
POST /api/generate
  └─ buildSkeletonPrompt({keywords, preset, complexity, poeticMode, detailRichness, contentLength, ...})
      └─ generateStory(messages) ─────► Claude Sonnet 4.6
         一次 API 调用：同时输出结构（节点+边）+ 所有正文
         失败即死：finish_reason='length' 或括号不平衡 → throw Error

POST /api/continue
  └─ buildContinuePrompt(...) → callAI(messages) → 单次调用重写下游节点
```

- **端点数**：2 个（generate + continue）
- **路由文件**：`daisy-crpg/packages/server/src/routes/ai.ts` (83 行)
- **失败模式**：长故事（long + detailed + bifurcating）JSON 截断 → 60% 失败率

### V4 —— 两步生成架构首次引入
```
POST /api/generate              ← 兼容 V3 单步（保留）
POST /api/generate/skeleton     ← NEW：只出结构（title + choices + value tags）
  └─ buildSkeletonOnlyPrompt → generateStory
POST /api/generate/content      ← NEW：批量填充正文
  └─ buildContentBatchPrompt(skeleton, nodeIds, detailRichness) → callAI
POST /api/continue              ← 同 V3
```

- **端点数**：4 个
- **路由文件**：`daisy/packages/server/src/routes/ai-v4.ts` (148 行)
- **失败模式**：消除 JSON 截断风险（骨架 < 4000 tokens 几乎不会被截），100% 成功率

### V6 —— 两步生成 + 截断救援 + 游戏体裁强化
```
（调用拓扑和 V4 完全一样，4 个端点）
POST /api/generate/skeleton     ← 骨架，V6 的 skeletonSystem 新增 ACT 1 SETUP + extreme 模式升级
POST /api/generate/content      ← 正文，V6 的 systemContent 新增 7 条游戏写作规则 + 反套路规则
POST /api/continue              ← 涟漪分析，用全量 MCKEE_SYSTEM_FULL
```

- **端点数**：4 个（同 V4）
- **路由文件**：`daisy/packages/server/src/routes/ai.ts` (162 行)
- **失败模式**：进一步加强——`callAI()` 遇到截断会尝试**自动闭合 JSON 结构**救援（V3/V4 直接抛错）
- **防线**：`ai.ts` 里新增 `normalizeEdges()` —— 对 Claude 输出的 sourceHandle 做服务器侧强制规范化（narrative/merge/act_break 一律设为 null，check 只接受 "success"/"fail"）

**结论**：调用拓扑只在 V3→V4 跳了一次（单步→两步）；V4→V6 不改拓扑，全是 prompt 内容与服务端防御层的升级。

---

## 2. 注入给 Claude 的 system prompt 逐段对比

所有版本的 system prompt 都由同一个 helper 组装：`buildSystemPrompt(poeticMode, locale)` → `MCKEE_BASE + (KEYWORD_POETIC | KEYWORD_LITERAL) + langInstruction(locale)`。
下面逐段对比三版本的 MCKEE_BASE 内容。

### 2.1 六条硬约束 + `{{playerName}}` —— **V3/V4/V6 完全一致**

```
1. Value Shift        — 每场景必须转换至少一个价值
2. Progressive Compl. — 每一拍都要加压，never plateau
3. Dilemma            — choice 必须是不可调和的两难
4. The Gap            — 行动 vs 结果之间必有落差
5. Controlling Idea   — 全篇一个主控思想
6. Three Levels       — inner / personal / extra-personal 三层冲突
+ {{playerName}} 占位符约定
```

**逐字相同**。这是 daisy 的"底盘"，从第一天就定下来了。

### 2.2 BRANCHING PHILOSOPHY —— **V3/V4/V6 完全一致**

```
- Delayed Convergence   — 选择后至少 3-5 个节点才能合流
- Distinct Branch Identity — 分支要有独立身份，不是同一情节的换皮
```

### 2.3 NODE TYPES —— **V3/V4/V6 完全一致**

六种：narrative / choice / check / merge / act_break / ending。

### 2.4 OUTPUT FORMAT —— V3/V4 一致，V6 新增

V3/V4 的 OUTPUT FORMAT 里 `sourceHandle` 只在字段注释里写"\<handle name or null\>"——靠模型自己猜。V6 在 OUTPUT FORMAT **之后独立增加一段 EDGE sourceHandle RULES**，把规则硬化：

```
### EDGE sourceHandle RULES (CRITICAL — wrong values break the graph!)
- narrative, merge, act_break → sourceHandle MUST be `null`
- ending                      → NEVER has outgoing edges
- choice                      → "0", "1", "2", ... (zero-based index)
- check                       → 严格 "success" 或 "fail"，不接受 pass/failure 等变体
```

这一段的出现是因为 V4 阶段观察到 Claude 会输出 "pass"/"failure" 等 sourceHandle 变体，破坏图谱。V6 两头堵：prompt 里硬规则 + `ai.ts` 里 `normalizeEdges()` 服务端再规范一次。

### 2.5 ACT 1 SETUP —— **V6 独有，V3/V4 没有**

```
### ACT 1 SETUP (建置) — MANDATORY
The story MUST begin with 1 narrative node that establishes the world and
protagonist through ACTIVE GAMEPLAY — the player exploring, talking to someone,
or doing a routine task that reveals the setting. NOT a passive description.
The inciting incident should come quickly (2nd or 3rd node) — this is a game,
not a novel. Players want to get into the action.
```

含义：V6 把"开头必须是主动游玩，第 2-3 个节点就进入激励事件"从隐性倾向变成了显性约束——这是从小说体裁向游戏体裁的决定性一步。

### 2.6 JSON SAFETY / DIALOGUE QUOTES —— **V6 独有**

```
### JSON SAFETY — DIALOGUE QUOTES
对话必须用中文「」（不是 ASCII "）
- 正确：「你也感觉到了吗？」她低声说。
- 错误："你也感觉到了吗？"她低声说。
```

V3/V4 没有这条，模型经常用 ASCII 双引号写对话，破坏 JSON。V6 同时在 prompt 里要求「」，并在服务端 `extractJSON()` 里加了一条正则：**检测到中文字符包围的 `"` 就替换成「**。双保险。

### 2.7 诗意 vs 字面（KEYWORD_POETIC / KEYWORD_LITERAL）—— **V3/V4/V6 完全一致**

两段独立文本，逐字相同：

```typescript
const KEYWORD_POETIC = ` You are also a poet — you find hidden connections,
sensory echoes, and emotional undercurrents in any set of keywords.

### KEYWORD INTERPRETATION
When given keywords, do NOT treat them as literal plot requirements.
Let them evoke atmosphere, mood, metaphor, sensory imagery.
A keyword like "glass" might become a fragile relationship, a mirror of the self.
A keyword like "rain" might become grief, renewal, a liminal space.
Weave them as poetic threads — sometimes explicit, sometimes as subtext.`

const KEYWORD_LITERAL = `
### KEYWORD INTERPRETATION
When given keywords, treat them as concrete plot elements.
Each keyword should appear directly in the narrative —
as a character, location, object, event, or central conflict.
"Glass" means there should be glass. "Rain" means rain plays a visible role.
Be direct and grounded.`
```

**组装逻辑**（`buildSystemPrompt`，三版本代码逻辑完全相同）：

```typescript
function buildSystemPrompt(poeticMode: boolean, locale?: string): string {
  const keywordSection = poeticMode ? KEYWORD_POETIC : KEYWORD_LITERAL
  return MCKEE_BASE.replace(
    "You are a CRPG narrative architect deeply versed in Robert McKee's *Story* principles.",
    "You are a CRPG narrative architect deeply versed in Robert McKee's *Story* principles." + keywordSection,
  ) + langInstruction(locale)
}
```

即：`KEYWORD_*` 段不是独立 system message，而是**被 splice 进 MCKEE_BASE 的第一句之后**，让"诗人身份"和"CRPG 叙事架构师身份"融合，紧接着六条硬约束。

配套副作用（在 `buildSkeletonPrompt` / `buildSkeletonOnlyPrompt` 里）：
- `temperature = poeticMode ? 0.9 : 0.7` —— 诗意模式同时提高 sampling 温度
- `poeticMode` 默认 `true`

`langInstruction(locale)` 默认空字符串；locale='zh' 时追加：
```
### LANGUAGE
All narrative content (...) MUST be written in **Chinese (中文)**.
Only structural fields (id, type, sourceHandle) remain in English.
```

**设计含义**：
- MCKEE_BASE 是**叙事逻辑底盘**，和语气无关
- POETIC/LITERAL 是**关键词解读口味**，影响"glass→玻璃"还是"glass→易碎的关系"
- langInstruction 是**输出语言锁**，只影响用户可见字段，保留结构字段英文以减少模型出错概率

---

## 3. DETAIL_CONFIG（写作规格）对比

四档 `concise / standard / detailed / extreme`。

### 3.1 concise / standard —— **V3/V4/V6 完全一致**

| | wordLimit | nodeFactor | style |
|-|-|-|-|
| concise | 60 | 1.0 | Tight prose. Action and value shifts only. No dialogue. |
| standard | 100 | 0.8 | Balanced prose. Brief dialogue, key sensory details. |

### 3.2 detailed —— **V3/V4 同，V6 重写**

V3/V4：
```
detailed: wordLimit 150, nodeFactor 0.55,
style: "Rich prose with dialogue (2-3 exchanges), sensory detail,
and internal reflection. Max 6-8 sentences per node."
```

V6：
```
detailed: wordLimit 150, nodeFactor 0.55,
style: "Game-quality prose: short action sentences, punchy dialogue,
concrete details the player can interact with. Show character through
what they DO and SAY. Max 6-8 sentences per node."
```

**差异定性**：V3/V4 的 detailed 仍是"小说"风（sensory detail + internal reflection）；V6 明确切到"游戏脚本"风（action + punchy dialogue + interactable details）。参数一样，指令逻辑完全重写。

### 3.3 extreme —— **V3/V4 同，V6 完全推倒**

V3/V4（"节点内 beats 数组"）：
```
extreme: wordLimit 200, nodeFactor 0.4, beats: true,
style: "Ultra-cinematic prose. Each narrative node MUST include a
'beats' array of 3-6 dramatic micro-moments. Each beat 40-60 words,
valueShift alternates (+ → - → +). The 'content' field contains the
FULL text of all beats concatenated."
```

V6（"beat 级独立节点 + sequences 分组"）：
```
extreme: wordLimit 80, nodeFactor 1.8,  ← 注意：参数反转，节点密度 ×4.5
style: "BEAT-LEVEL GRANULARITY: Each node represents a single BEAT —
McKee's smallest dramatic unit. 40-80 words. ONE action, ONE reaction,
ONE value shift. Beats are grouped into SEQUENCES (2-5 beats per seq).
Within a sequence, beats alternate value polarity."
```

**结构性差异**：
- V3/V4 extreme：一个 narrative 节点还是"一场戏"，内部用 `beats[]` 数组承载戏的分拍
- V6 extreme：把 beat 升格为独立节点，用 `sequenceId` 重新组织；JSON 输出多一个顶层 `sequences[]` 数组
- 结果：同一个故事在 V6 extreme 下节点数几乎翻倍，图谱视觉密度大增

---

## 4. 两步生成 Step 2（正文填充）对比

这一步的 system prompt 在三版本间差异最大（因为 V3 根本没有这一步）。

### 4.1 V3 —— 不存在
V3 是单步生成，没有独立的"填充正文"prompt。

### 4.2 V4 —— 有，但只是"骨干 + McKee"
V4 的 `buildContentBatchPrompt` 用了 `MCKEE_SYSTEM_FULL`（= `MCKEE_BASE + KEYWORD_POETIC`）作为 system，简单直接。没有专门的"写作风格"指令，只依赖 `detail.style`。

### 4.3 V6 —— 重写，新增两组规则

V6 的 `systemContent` 是**独立写的**，不复用 MCKEE_BASE，包含：

**A. GAME WRITING RULES（7 条，V6 独有）** —— 解决"LLM 默认写小说不写游戏脚本"：
1. Player as agent（主动语态、主角 DO things）
2. Show the world through interaction（不描述房间，让玩家发现）
3. Keep it punchy（最多 2-3 句描写，然后必须发生事件）
4. Concrete game information（输出可用物品/NPC/线索）
5. Dialogue is gameplay（对话推进信息/制造困境）
6. Tension through stakes, not prose（用事件制造张力，不用辞藻）
7. Setup nodes are active too（世界观建置也必须交互式）

**B. ANTI-MELODRAMA（V6 独有）** —— 封堵 LLM 的廉价叙事模式：
- 禁止直接命名情绪（改用行动/对话展示）
- 每个节点最多一个身体感觉描写（心跳、颤抖…）
- 禁止华丽隐喻，要求朴素精确
- 不是每个场景都是危机 —— 包含幽默、尴尬、日常质感

**C. 体裁一致性（非诗意模式追加）**：
```
Write like a game script, not poetry.
Concrete actions, specific objects, real dialogue.
```

**D. JSON SAFETY（V6 独有）**：
和 MCKEE_BASE 里那条一样，中文对话必须用「」——在填充阶段再强调一次。

---

## 5. 服务端防御层差异（`ai.ts`）

| | V3/V4 `ai.ts` | V6 `ai.ts` |
|-|-|-|
| 行数 | 164 | 247 |
| 截断检测 | finish_reason + bracket balance | 同左 |
| 截断救援 | 无（直接抛错） | `callAI()` 尝试自动闭合 JSON 结构并重新解析 |
| Edge 规范化 | 无 | `normalizeEdges()`：强制 narrative/merge/act_break 的 sourceHandle=null；check 的 sourceHandle 强制 "success"/"fail" |
| 中文对话引号 | 仅 extractJSON 基础清理 | 新增正则：中文字符夹着 ASCII `"` → 自动替换为「 |
| Model | `anthropic/claude-sonnet-4-6` | 同左（三版本都是同一模型） |

---

## 6. 关键洞察总结（新项目 crpg 设计参考）

### 必须继承的"硬核"（V3 就已定型，不可动）
1. **McKee 六条硬约束** —— daisy 的灵魂，所有版本都一致
2. **{{playerName}}** 占位符约定
3. **BRANCHING PHILOSOPHY** 两条（Delayed Convergence + Distinct Branch Identity）
4. **六种节点类型**（narrative/choice/check/merge/act_break/ending）
5. **KEYWORD_POETIC vs KEYWORD_LITERAL** 两种关键词解读模式（+ 对应的 temperature 切换）
6. **OUTPUT FORMAT JSON 契约**

### 强烈建议继承的"V4 架构"
7. **两步生成**（骨架 → 内容填充）—— 消灭 JSON 截断风险，是新项目接多模型的**刚需**（因为不同模型的输出 token 上限差异极大）

### 强烈建议继承的"V6 增强"
8. **ACT 1 SETUP** 显性约束 —— 游戏体裁和小说体裁的分水岭
9. **EDGE sourceHandle RULES** 硬规则（prompt + 服务端 normalizeEdges 双保险）
10. **JSON SAFETY / 中文「」引号**（prompt + 服务端正则双保险）
11. **7 条 GAME WRITING RULES** —— 这是"生成文字游戏"和"生成小说"的核心差别
12. **ANTI-MELODRAMA 4 条** —— 防止模型坍缩到廉价叙事模式
13. **extreme 模式的 beat 级独立节点 + sequences**（V6 的实现优于 V4）

### 需要重做的部分（新项目 crpg 方向）
- **模型抽象层**：V6 所有函数都硬编码 `MODEL = 'anthropic/claude-sonnet-4-6'`，需要替换成多模型路由
- **图像生成 pipeline**：完全不存在，要新建独立的 image-generation system prompt 和 pipeline（可能按节点触发、按场景触发或按 act 触发）
- **文字/图片双模型解耦**：两套 API adapter，两套 prompt 资产

### 可选重做
- **纯享版（玩家端）前端**：静态托管即可，不需要 AI 调用 pipeline（故事数据预生成并保存成 JSON）
- **创作者版前端**：可以延续 React Flow 架构，也可以换
- **存储层**：V6 用 SQLite + better-sqlite3 + Drizzle，新项目可以保留或换
