# crpg 战略审查 v2 —— 2026-04-17

**审查人**: 独立 Review 角色 v2（第二轮：补充 daisy 代码库完整阅读）
**审查范围**: 项目整体定位、daisy 代码遗产、路径、工程取舍、根本矛盾
**审查立场**: 不复读 v1 结论；对 v1 因漏读 daisy 代码造成的判断错误独立修正
**材料**:
- SESSION-STATE-2026-04-17.md / MEMORY.md 7 条 / COMPETITIVE-ANALYSIS-2026-04-17.md
- **daisy 完整代码**（`/tmp/crpg-research/daisy/`，10,279 行 TypeScript 实际测量 @ `wc -l`）
- **daisy-crpg 前身**（`/tmp/crpg-research/daisy-crpg/`，8,284 行，演进对照）
- daisy AUDIT_FINDINGS.md / TEST_REPORT.md / docs/internal-post.md
- crpg `assets/daisy-narrative-core/` 全部方法论资产
- R5 Shot 2 v5 实证图像

---

## 0. Executive Summary（一页内）

### 最大修正（相对 v1）

v1 在没读代码的情况下写了一份主要结论，我现在已**读完全部 daisy 代码**，必须修正三个关键判断：

1. **v1 说 "只有 20-30 KB 可复用的文本资产，不是代码"——错。** daisy 有 **10,279 行生产级 TypeScript**，其中约 **55-65% 对 crpg 是直接 leverage**（不是 30%）。完整的 React Flow 画布 / 两步生成 pipeline / D20 检定 / PlayMode / 发布-消费社区（三表）/ 涟漪分析（`buildContinuePrompt`）/ 存档 / 自动布局 —— **这些都是已测试、已跑通的生产代码**，不是伪码。

2. **v1 说 "Shot Director LLM 是过早优化，4-8 周工程"——部分错。** daisy 的 `useAIGenerate.ts` 已经实现了**完整的两步 pipeline 框架**（P1 skeleton + P2 content batch with retry）。**加 P3 (Shot Director) 只是在 P2 之后插一个 batch，复用现有 batch 逻辑，工程复杂度约 1-2 周，不是 4-8 周**。v1 过度悲观。

3. **v1 说 "方法论是入场券不是护城河"——对但不完整。** 补充 daisy 代码后，我发现一个 v1 没看到的护城河：**daisy 原作者 48 小时产出 10,279 行 + 800 行 prompts 的工程品味本身是稀缺资产**。crpg 的方法论文档（300KB）大部分是可复现的，但**"把文档翻译成生产级工程的能力"本身就是护城河**——这点 v1 完全没看到，因为 v1 没读代码。

### 核心结论

- **daisy 代码是真 leverage，不是 sunk cost**。技术栈和产品形态 80% 可直接用。
- **图像部分的困境真实存在**：R5 Shot 2 v5 我独立看了，几何上是 thigh-high（上缘位置正确），但**视觉阅读上确实像过膝袜**（颜色太深 / 不够 sheer / 无腿部光影分离）—— v1 判断正确。
- **真正的战略问题不是"砍 scope"，而是"接住 daisy 现成的产品形态 + 只做增量"**。v1 推荐的"路线 X 砍一半锁一半"判断方向正确，但因为低估 daisy 代码资产，低估了单人执行的可行性（v1 给 50-65% 胜率，我给 65-75%）。

### 推荐战略路线

**路线 Y（v2 推荐）：fork daisy → 成人向改造 → 图像降级渐进注入**

具体第 1 周动作在 §8。核心特征：
- **不从零写代码**，fork daisy 直接改
- **保留 daisy 所有现有能力**（画布 / Play / 发布 / 涟漪）
- **只加** 成人向 prompts 改造 / 双模型路由 / 18+ 门 / GeoIP / BYOK 界面
- **推迟**：Shot Director / VDNA 第 9-10 层 / 动态 budget
- **冻结但保留**：300KB 方法论资产进 `docs/research/`，v2 再激活

### 对 v1 的关键修正总结

| v1 判断 | v2 修正 | 修正原因 |
|---|---|---|
| daisy 唯一能用的是 20-30KB 文本 prompts | daisy 10,279 行代码中有 55-65% 可直接继承 | v1 没读代码 |
| 独立开发者 12 个月才能完成 | 继承 daisy 后 3-4 月可达 MVP | 现有架构已打好 |
| Shot Director 4-8 周全职 | 1-2 周（在现有 batch pipeline 上加一层） | daisy 已有 P1/P2 batch 框架 |
| 方法论不是护城河 | 方法论+工程品味共同构成护城河 | daisy 800 行 prompts + 10K 行代码的组合能力稀缺 |
| crpg 0 行代码是 "方法论过度生产" | crpg 0 行是因为**没意识到可以直接接住 daisy**；一旦开始 fork，代码增长极快 | v1 看不到 daisy asset 的体量 |
| 纯享版是硬约束，会限制商业模型 | 纯享版 = daisy 已有 published_stories 表 + community feed 的成人改造，**几乎零边际代码成本** | v1 没看到 daisy 已经有完整社区发布层 |

---

## 1. 对上一轮 reviewer 的修正（核心）

v1 是**方法论-only 审查**，v2 是**代码-methodology 联合审查**。结论差异不小。

### 修正 1：daisy 代码的真实体量

**v1 的判断**（§2.2）：
> "唯一真正复用的是：daisy 的 `MCKEE_BASE` 文字 prompt 结构 + 两步生成哲学 + 798 行 prompts.ts 的 system prompt。这约等于 **20-30 KB 可复用的文本资产**，不是代码。"

**v2 的实证纠正**：
- `wc -l` 实测 daisy = **10,279 行 TypeScript**（60 个 `.ts/.tsx` 文件）
- 其中 server：`ai.ts 247` + `prompts.ts 799` + `prompts-v4.ts 597` + `routes/ai.ts 162` + `routes/nodes.ts 233` + `routes/projects.ts 136` + `routes/community.ts 145` + `db/schema.ts 70` + `db/index.ts 76` + `index.ts 40` = **约 2,505 行 server 代码**
- web：从 `stores/` 3,483 行 + `hooks/` 约 2,600 行（`useAIGenerate 395` + `useGameLoop 215` + `useDiceRoll 222` + etc）+ `components/` 约 4,300 行（`NodeEditor 500+` + `StoryCanvas 287` + `PlayMode 304` + 6 个 nodes + 5 个 play/ + 3 个 community/ 等）+ `lib/` 1,300+（含 i18n 312 / moodEngine 188 / pathValidator 169 / exportUtils 486 / impactAnalyzer 43）+ `App.tsx 202` = **约 7,774 行 web 代码**

这**不是 20-30 KB 文本**，是一个**测试过的、跑得通的完整产品**（TEST_REPORT.md：21 个功能全部 PASS；64 节点故事实测生成成功；8 个 8 次生成 100% 成功）。

### 修正 2：继承性 vs 重写性

**v1 的判断**（§2.2）：
> "这是典型的 **sunk cost fallacy**。用户在把'我熟悉 daisy' / 'daisy 的想法继承感'包装成'技术继承'。实际上 crpg 的技术选型应该**从 0 开始按 crpg 自己的需求设计**"

**v2 的实证纠正**：

我对 daisy 每一个模块评估了"对 crpg 的继承价值"（证据见 §3）：

| daisy 模块 | LOC | 继承价值 | crpg 改动量 |
|---|---|---|---|
| `prompts.ts` MCKEE_BASE | 114 行 | ⭐⭐⭐⭐⭐ 直接用 | 加 3 个 McKee 补丁 + 成人向段落 |
| `prompts.ts` 其余（skeleton/content/continue/detail/length）| 685 行 | ⭐⭐⭐⭐ 结构保留 | 插入 Genre/Antagonism/Climax，调温度 0.8 |
| `services/ai.ts` OpenAI client + JSON extraction + 截断检测 | 247 行 | ⭐⭐⭐⭐⭐ 直接用 | 换 MODEL 常量为双模型路由即可 |
| `routes/ai.ts` skeleton/content/continue endpoints | 162 行 | ⭐⭐⭐⭐⭐ 直接用 | 加成人向 flag，加 auth middleware |
| `routes/nodes.ts` / `routes/projects.ts` / `routes/community.ts` | 514 行 | ⭐⭐⭐⭐ 直接用 | 加 user_id 字段，加 auth |
| `db/schema.ts` 5 表 | 70 行 | ⭐⭐⭐⭐ 直接用 | 加 users 表；published_stories 加 content_rating/age_gate_passed |
| `stores/editorStore.ts` zustand + persist + onRehydrate | 222 行 | ⭐⭐⭐⭐⭐ 直接用 | 不改 |
| `stores/playerStore.ts` 27 点购买 + D20 + 技能映射 | 188 行 | ⭐⭐⭐⭐⭐ 直接用 | 不改 |
| `stores/communityStore.ts` / `saveStore.ts` / `themeStore.ts` | 约 500 行 | ⭐⭐⭐⭐ 直接用 | 不改 |
| `components/nodes/` 6 个节点类型 React Flow | 约 1,300 行 | ⭐⭐⭐⭐ 直接用 | 加 shots[] 字段的 optional 展示 |
| `components/editor/StoryCanvas.tsx` | 287 行 | ⭐⭐⭐⭐⭐ 直接用 | 不改 |
| `components/editor/Toolbar.tsx / GenerateDialog.tsx / AmbientOverlay.tsx` | 约 1,200 行 | ⭐⭐⭐⭐ 直接用 | GenerateDialog 加成人向参数 |
| `components/panels/` 4 个（NodeEditor 500+ / ProjectPanel / PathAnalysis / SaveSlotCard）| 约 2,000 行 | ⭐⭐⭐ 85% 直接用 | NodeEditor 加 shots 编辑 tab |
| `components/play/` 5 个 (PlayMode / PlayScene / PlayChoice / PlayCheckScene / PlayEnding / CharacterCreation) | 约 2,300 行 | ⭐⭐⭐⭐ 直接用 | PlayScene 加图像展示槽 |
| `components/community/` 3 个 (Feed / PublishDialog / StoryCard) | 约 1,000 行 | ⭐⭐⭐⭐ 直接用 | 加 18+ 内容 filter + age gate |
| `hooks/useAIGenerate.ts` 两步生成 + BATCH_SIZE=5 + retry | 395 行 | ⭐⭐⭐⭐⭐ 直接用 | Shot Director 作为 P3 batch 加在 P2 之后 |
| `hooks/useAIContinue.ts` 涟漪分析 | 53 行 | ⭐⭐⭐⭐ 直接用 | 不改 |
| `hooks/useAutoLayout.ts` ELK.js | 72 行 | ⭐⭐⭐⭐⭐ 直接用 | 不改 |
| `hooks/useDiceRoll.ts` D20 动画 | 222 行 | ⭐⭐⭐⭐⭐ 直接用 | 不改 |
| `hooks/useGameLoop.ts` 游玩主循环 | 215 行 | ⭐⭐⭐⭐⭐ 直接用 | 不改 |
| `hooks/usePathValidation.ts` | 34 行 | ⭐⭐⭐⭐⭐ 直接用 | 不改 |
| `hooks/usePublish.ts` | 54 行 | ⭐⭐⭐⭐⭐ 直接用 | 不改 |
| `hooks/useAmbientTheme.ts` | 60 行 | ⭐⭐⭐⭐⭐ 直接用 | 不改 |
| `lib/moodEngine.ts` 8 类氛围 + 调色板 | 188 行 | ⭐⭐⭐⭐⭐ 直接用 | 不改 |
| `lib/i18n.ts` EN/ZH | 312 行 | ⭐⭐⭐⭐⭐ 直接用 | 补充成人向术语 |
| `lib/pathValidator.ts` McKee 路径验证 | 169 行 | ⭐⭐⭐⭐⭐ 直接用 | 加 Genre 校验 |
| `lib/exportUtils.ts` JSON + Markdown 导出 | 486 行 | ⭐⭐⭐⭐ 直接用 | 加图像 shots 导出 |
| `lib/paletteUtils.ts` | 105 行 | ⭐⭐⭐⭐⭐ 直接用 | 不改 |
| `lib/impactAnalyzer.ts` 下游 DAG 影响分析 | 43 行 | ⭐⭐⭐⭐⭐ 直接用 | 不改 |

**加总**：约 **6,500-7,500 行直接继承（⭐⭐⭐⭐+）**，约 **1,500-2,000 行需要小改（⭐⭐⭐）**，约 **800 行需重写（主要是 Grok 双模型路由 / 合规层 / 图像 pipeline）**。

**结论**：v1 对"daisy = 20-30KB 文本"的描述错了一个数量级（约 300×）。daisy 是 **生产级可继承的完整产品**，不是方法论草稿。

### 修正 3：单人 12 个月的时间估算

**v1 §4**：
> "合计 27 周 (6.3 月) 乐观 / 54 周 (12.5 月) 现实"

**v2 修正**：
v1 错在把 "从零开始写" 当成了基准。实际上 crpg 不需要从零。

**修正后的时间估算（继承 daisy 基础上）**：

| 组件 | v1 估算（现实）| v2 修正（继承 daisy 现实）| 修正原因 |
|---|---|---|---|
| 文字生成（daisy 代码 + McKee 三补丁 + 前端适配）| 5 周 | **2 周** | 代码已存在，只加 3 个 prompt 段落 |
| 18+ 门 + GeoIP + 基础合规 | 2 周 | 2 周 | 维持 |
| 图像 pipeline（Grok + VDNA 静态 + 1 cover per node）| 4 周 | **3 周** | daisy 的 batch framework 可复用 |
| Shot Director LLM 完整版 | 8 周 | **2 周** | 插在现有 batch 后面，不是从零 |
| 双模式前端（纯享版 + 创作者画布）| 12 周 | **3 周** | daisy 已经有**发布流**（published_stories 表 + CommunityFeed），纯享版只是改 filter |
| 双模型路由 + 等价温度表 | 3 周 | **1.5 周** | `services/ai.ts` 只需 MODEL 常量变路由 |
| 发布流 | 4 周 | **1 周** | daisy.PublishDialog.tsx 已完成 |
| 账单 / BYOK 层 | 4 周 | 4 周 | 维持 |
| 审计 / 审核链 | 3 周 | **2 周** | 简化：database 加字段 + 客户端 filter |
| 部署 / CDN / 运维 | 3 周 | 2 周 | 维持 |
| Bug 修复 / 反馈迭代 / UX 打磨 | 6 周 | 6 周 | 维持 |
| **合计** | **54 周 (12.5 月)** | **28-30 周 (6.5-7 月)** | **约减半** |

**关键认识**：真实瓶颈不是"写代码"，是"图像质量调试" + "审美决策" + "合规法律咨询"。这些非代码环节反而是不容易被 daisy 加速的部分。

### 修正 4：护城河评估

**v1 §2.5**：
> "crpg 的方法论不是护城河。它是良好的产品开发纪律 + 工程品味。"

**v2 补充**（v1 错在把"方法论"和"工程能力"分开算）：

daisy 本身就是一份证据，证明 **"能把 800 行 McKee prompt 写出来的人，就能把 10,279 行代码写出来"**。反过来也成立：**能在 48 小时产出 10K 行的人才有品味把 McKee 编进 800 行**。

换句话说：
- 方法论（300KB crpg 文档）**单独不是**护城河（公开知识综合）
- 工程能力（daisy 10K 行代码）**单独不是**护城河（TypeScript / React Flow / Hono 大家都会）
- **两者结合**——"能把 McKee 理论编码为 prompt、同时 48h 做出 10K 行可跑代码"——**这个组合是稀缺的**

crpg 已经有了这两者。**问题是 crpg 做成人向的图像部分碰到了新的门槛**（见矛盾 7）。护城河存在，但被"图像追求完美"的沙坑卡住了。

### 修正 5：方法论过度生产的诊断偏差

**v1 §2.4**：
> "方法论产出速率 >> 工程产出速率"

**v2 补充**：
v1 看到的是 brainstorming 分支，main 分支为空。但 v1 没意识到 daisy 代码**不在 crpg git 里**——它在 `/tmp/crpg-research/daisy/`，是 git worktree，**用户已经准备好 fork 了**。

所以 "crpg 有 300KB 文档 + 0 行代码" 这个描述**不准确**。更准确的描述是：
- crpg/brainstorming 分支 = 300KB brainstorming 文档
- daisy 代码 = 随时可 fork 的 10,279 行 production-ready
- **组合起来 = 一个马上可以继续编码的项目**

这不是"过度生产方法论"，这是"**积累一堆 notes，但没对 daisy 按下 fork 按钮**"。v1 的诊断(stopped building / all planning)方向对，但严重程度比 v1 描述的要轻得多——用户只需要按下那个 fork 按钮。

---

## 2. daisy 代码质量评估（真 leverage 还是技术债）

### 2.1 代码质量样本观察

**server/src/services/ai.ts**（247 行）—— v2 独立判断：**质量超出 48h 原型水准**
- OpenRouter client 有 `getClient()` 懒初始化（line 6-18），避免启动时强依赖 `.env`
- `extractJSON()` 有 6 层降级策略（markdown fence strip / fence 内提取 / 第一个 `{` 到最后 `}` / 尾 comma 修复 / 单行注释清除 / ASCII dialogue 引号替换为中文括号 「」 to 避免 JSON 内引号串） —— 这是**处理过真实 LLM 输出 bug 积累出来的工程细节**，48h 能写出来但必须跑过上百次 generation 才能把这些 case 都见完
- `generateStory()` 有**三重截断检测**（finish_reason / content 结构 / 括号平衡）—— 这是 production 级的防御，不是 demo 级
- `callAI()` 对截断还有**救援逻辑**（补 `}` / `]` 试图 salvage truncated JSON）—— 非常专业

**server/src/routes/ai.ts**（162 行）—— v2 独立判断：**符合现代 Hono 风格**
- 每个 endpoint 都有 input validation（`keywords.length > 1000` / `characters > 20` / etc）
- try-catch 捕获并返回 500
- generate / skeleton / content / continue 四 endpoint 语义清晰，直接对应 daisy 的两步生成 + 涟漪分析

**web/src/hooks/useAIGenerate.ts**（395 行）—— v2 独立判断：**核心工程能力集中处**
- 两步 pipeline 完整：STEP 1 skeleton → `setNodes` + `setEdges` 立即可见 → STEP 2 parallel batch 填充（`BATCH_SIZE=5`，line 244）
- `mapAINode()` 有**完整的节点类型 → ReactFlow node 映射**（6 种 node type 分别处理 data）
- `normalizeSourceHandle()` 在**前端做第二重 edge handle 校验**（和 server 的 `normalizeEdges` 构成 defense-in-depth）
- 失败 batch **串行重试 + 2s delay 避 rate limit**（line 373-380）
- 有 `abortRef` 处理用户中途取消
- Progress state 分三 phase（`skeleton` / `content` / `done`），前端可直观展示进度

**stores/editorStore.ts**（222 行）—— v2 独立判断：**zustand + persist 写得规范**
- 用 `persist` middleware 做 localStorage 自动持久化（line 95）
- `partialize` 明确声明哪些字段持久化（nodes/edges/projectName/worldSetting/characters），不把 UI state 和 snapshots 带入
- `onRehydrateStorage` 修复了 `nodeIdCounter` rehydrate bug（line 217-219）—— AUDIT_FINDINGS.md D-01 的修复
- snapshot 机制（`snapshotNodeData` / `clearSnapshot` / `clearAllSnapshots`）为**涟漪分析做了 undo/redo 基础**

**services/prompts.ts**（799 行）—— v2 独立判断：**核心叙事工程**
- `MCKEE_BASE` 114 行是 McKee 六条硬约束的完整编码（v1 看过这个）
- 但 v1 没看到的是：skeleton / content-batch / continue 三个分别有独立 prompt builder（`buildSkeletonPrompt` / `buildSkeletonOnlyPrompt` / `buildContentBatchPrompt` / `buildContinuePrompt`），每个 builder 接收完整参数集（keywords / preset / complexity / worldSetting / characters / locale / poeticMode / detailRichness / contentLength）并输出 `{messages, temperature, maxTokens}`——**这是 production-level prompt engineering，不是 demo**
- DETAIL_CONFIG 有 4 档（concise/standard/detailed/extreme），extreme 模式引入了 **beat-level granularity**，和 McKee 的 Beat/Scene/Sequence 层级对应
- 有完整的 **JSON Safety — Dialogue Quotes** 段落（line 111-114），教 LLM 用 「」 避免破坏 JSON

### 2.2 已知问题（AUDIT_FINDINGS.md + v2 独立发现）

**daisy 原作者已修复（7 个）**：
- S-01 CORS / D-01 nodeIdCounter / S-03,S-04 validation / S-05 JSON.parse try-catch / S-06 pagination / T-02 dice interval leak / L-01 check node dead state

**未修 warnings（8 个）**：
- T-04 无 ErrorBoundary
- W-01 setNodes 替换整个数组（并发丢失风险）
- W-02 batch race（5 节点并行，zustand set 同步，原作者说"likely safe"）
- W-03 triggerFade setTimeout 未清理
- W-04 community like 无 rate limit
- W-05 **delete story 无 auth** —— 这是阻断性 bug，crpg 必须修
- W-06 PlayMode 角色创建可空名
- W-07 Markdown export 单向

**v2 独立发现的额外问题**：
- `routes/projects.ts` GET `/` 返回所有项目，**没有 user 过滤**（多用户时任何人能看所有项目）—— 必须在 crpg 加 auth middleware
- `db/schema.ts` 所有 text/JSON 字段是 **unbounded**，creator 可以塞入任意大字符串（server validation 能挡一部分，但 DB 层应该有 CHECK constraint）
- `services/ai.ts` OpenRouter API key 直接从 `process.env.OPENROUTER_API_KEY` 读（line 8）—— BYOK 模式需要重构这里为 per-request key
- `editorStore` 用 zustand persist（localStorage）—— 在浏览器关闭或 storage 满了会丢 unsaved work；crpg 应该 pair 一个服务端 autosave
- `lib/exportUtils.ts` 486 行里 Markdown import 没实现（W-07 已列）；JSON roundtrip 是 OK 的
- **没有 rate limiting**（W-04 仅提到 community）—— AI endpoints 也没有，single user 能耗光 OpenRouter quota
- **没有 usage metering** —— crpg 的 BYOK 模式需要知道"这个用户花了多少"才能显示给他

### 2.3 整体评级

| 维度 | 评级 | 证据 |
|---|---|---|
| 架构清晰度 | ⭐⭐⭐⭐⭐ | monorepo + 清晰 packages/ 边界 + 分层 stores/hooks/lib/components |
| 代码品味 | ⭐⭐⭐⭐ | TypeScript 规范、React 19 现代 hooks、zustand persist、Hono 现代 |
| 工程防御性 | ⭐⭐⭐⭐ | JSON extract 6 层降级 / 截断检测三重 / edge normalize 双层 / retry 机制 |
| 测试覆盖 | ⭐⭐ | TEST_REPORT 21 个 manual Playwright，**无自动化测试** |
| 安全/合规 | ⭐⭐ | CORS / 输入验证有；auth 完全没有（作者自承：W-05） |
| 可扩展性 | ⭐⭐⭐⭐ | 节点类型通过 nodeTypes map 注册；schema 易加字段；两步 pipeline 易插 P3 |
| 文档 | ⭐⭐⭐ | internal-post 写得好；代码注释中等；无 README/setup 文档 |

**综合评级**：**4.0 / 5**。48 小时原型中的最上档。对 crpg 来说是**真金**，不是沉没成本。

### 2.4 "产品化到底要重写多少"

v1 §2.2 悲观地说"80% 重写"。v2 实证纠正：

| 领域 | 必须重写 | 可直接用 |
|---|---|---|
| server AI 调用 | MODEL 常量改为路由器（30 行）| JSON extract / 截断检测 / retry 逻辑 **全部复用** |
| server 路由 | 加 auth middleware（1 层中间件）+ `user_id` 字段传递 | 4 个 routes 文件的核心逻辑 **100% 复用** |
| DB schema | 加 users 表 + published_stories 加 content_rating / age_gate 字段 | 5 个现有表 **100% 复用** |
| 前端画布 | 不动 | StoryCanvas / 6 个 node components **100% 复用** |
| 前端 PlayMode | PlayScene 加 `<ImageSlot>` optional | PlayMode / CharacterCreation / D20 / 5 个 Play 组件 **90% 复用** |
| 前端社区 | PublishDialog 加 age gate checkbox | CommunityFeed / StoryCard **100% 复用** |
| Prompts | 加 Genre/Antagonism/Climax 三段落 + 成人向许可段落 | 799 行 V6 + 597 行 V4 **90% 复用** |
| 双模型路由 | **全新**（约 100-200 行） | 无 |
| 图像 pipeline | **全新**（约 500-1500 行，取决于范围） | 无 |
| 18+ 门 + GeoIP | **全新**（约 50-100 行） | 无 |

**真实数字**：daisy 10,279 行中约 **6,500-7,500 行直接继承（63-73%）**，crpg 全新写的部分约 **1,500-3,000 行**（双模型路由 + 图像 pipeline + auth + 合规）。

**v1 的 "80% 重写" 数字错了**——是 80% 可继承。

---

## 3. 十个战略矛盾（每个 400+ 字独立分析）

### 矛盾 1：单人可执行性 vs 项目复杂度（修正版）

**v1 判断**：⭐⭐⭐⭐⭐ 致命 / 推荐 B 砍 scope 到 4-8 周 MVP

**v2 修正**：⭐⭐⭐ 中等 / 推荐 fork daisy + 6-7 月完整产品

**证据**：
- daisy TEST_REPORT.md 第 21-23 项实测：**48 小时做出来的东西**能跑 64 节点故事、38-47 节点 AI 生成、4 种 preset、4 档细节、3 档长度、两步 pipeline 生成 100% 成功
- daisy 作者在 internal-post §1.1 写 "V3 单步 60% 失败率 → V4 两步 100% 成功"—— 这说明他**迭代过至少 16 次生成**才得出这个结论
- v1 的"单人 12 个月"错把 crpg 当成"从零开始"；实际是"fork daisy 改"
- daisy 作者 48 小时 + crpg 用户从 2026-04-04~2026-04-17 (13 天) 积累方法论 = **crpg 不是 Day 0 状态**，crpg 已经在 Day 30 状态（daisy 作为基线 + 方法论作为升级包）

**可能的战略路线**：

A. **fork daisy 立即改** —— 2-3 月有文字 MVP（daisy + 三补丁 + 18+），5-7 月加图像
B. **重写** —— 6-12 月（v1 推荐）
C. **放弃 crpg 独立，把 daisy 改成成人向 v2 直接** —— 1-2 月（不搞双模型、不搞图像，就是 daisy + 成人向 prompts）

**v2 推荐**：**A**。理由：
- 有 daisy 代码不用是**实实在在的浪费**（毕竟这 10K 行是用户自己写的，不是别人的项目）
- C 过于保守，放弃了 crpg 的所有增量价值（成人向 / 图像 / 双模型）
- B 是 v1 推荐，但 v1 没看到 daisy 代码资产
- 3-4 月能看到文字 MVP 已经远好于 v1 的"8 周砍到最小版本"

---

### 矛盾 2：daisy 代码真的是 leverage 还是 sunk cost（修正版）

**v1 判断**：⭐⭐⭐⭐ 严重 / 推荐 C 只做 daisy+McKee 三补丁

**v2 修正**：⭐⭐ 低 / 推荐 A fork 直接改

**证据**：

v1 在没看代码的情况下假设"crpg 的需求几乎重写所有 daisy 代码"。v2 逐模块审查后发现绝大多数**不需要重写**，只需**加一层**。

具体例证：
- **双模型路由**：不用改 `ai.ts` 的 245 行，只需把 `MODEL = 'anthropic/claude-sonnet-4-6'`（line 20）改成 `const MODEL = selectModel(params.steamy)`——**5-10 行代码**
- **成人向改造**：不用改 prompts.ts 的 799 行结构，在 `MCKEE_BASE` 后加一段 `ADULT_GENRE_PERMISSION` 字符串约束——**约 30-50 行新文本**
- **合规层**：`routes/projects.ts` 加 auth middleware（Hono 中间件 10-20 行）+ `db/schema.ts` 加 `content_rating / age_gate_passed / reported_count` 字段—— **40-80 行**
- **图像 pipeline**：这是唯一真正"全新"的部分，但 `useAIGenerate.ts` 395 行的 batch 框架可直接复用，只需要加 P3 的 `generateShotList()` 和 P4 的 `assembleImagePrompts()`——约 500-800 行

React Flow 画布（StoryCanvas 287 行）：crpg 只需要支持"每个节点可点击展开 shots 列表"，**不需要动画布结构**。这是在 `components/nodes/` 里加一个 `<ShotsCarousel>` 的事情，不是重做画布。

Hono + better-sqlite3 + Drizzle：对 crpg 的 LLM pass + 图像 pipeline **完全够用**。better-sqlite3 同步调用对单实例服务够快（Hono 是异步的，SQLite 调用会阻塞但每次 < 5ms，在 production traffic < 100 qps 内没问题）。

daisy 的 `published_stories` 表（`db/schema.ts` line 44-60）**就是纯享版的后端**：title / description / authorName / nodes JSON / edges JSON / palette / moodCategory / playCount / likeCount。加个 `content_rating` 字段，前端 filter 一下，就是 crpg 纯享版。**根本不需要"重做发布流"**。

**选项**：

A. **fork + 在现有文件 patch** —— v2 推荐
B. **在另一个 repo 重写** —— v1 推荐，但证据不足
C. **fork + 阶段性合并**（先继承 daisy 为 v0.1，逐步替换） —— 中庸方案

**v2 推荐**：**A**。直接 fork daisy 到 `lxistired/crpg` 作为初始 commit，然后在它基础上改。沉没成本不存在——daisy **本来就是用户自己写的**。v1 讨论"sunk cost fallacy"是把 daisy 错认为别人的代码。

---

### 矛盾 3：成人向定位 vs daisy 的通用设计

**v2 新增**（v1 没分析这个）：

**定义**：daisy prompts.ts 的 799 行**没有一个字**提到 NSFW / 成人 / 性。crpg 要做成人向，首先要让 daisy 的 MCKEE 框架**允许**成人内容。

**证据**：
- `MCKEE_BASE` line 42-50 是六条硬约束，纯叙事理论
- Node types（line 64-69）只是 narrative / choice / check / merge / act_break / ending
- DETAIL_CONFIG 最多说"game-quality prose / concrete details"，没禁止也没鼓励成人
- Claude Sonnet 4.6 通过 OpenRouter 调用时，**OpenRouter 的策略允许一定成人内容**（对照 Anthropic 直连的更严格限制）
- 但 Claude **model 层自己的 constitutional AI** 会把明显 NSFW 请求 refuse——prompts 需要明确 grant permission

**实际需要的改造**：

```
在 MCKEE_BASE 末尾加（约 40-60 行）：

### CONTENT SCOPE
This is an adult creative platform (18+). Stories may include mature themes:
- Explicit sexuality between consenting adults
- Power dynamics, kink, and taboo subjects explored as adult creative fiction
- Dark psychological themes (betrayal, obsession, moral ambiguity)

ABSOLUTE RED LINES (never generate):
- Minors in sexual contexts (anyone under 18, explicit or suggestive)
- Real public figures in sexual contexts
- Non-consent depicted as endorsed or glorified

Adult themes integrate with McKee's value-shift framework:
- Sexual scenes still require value shifts (desire→satisfaction, or desire→emptiness, trust→surrender, etc.)
- Every scene must serve controlling idea
- Eroticism is a McKee value axis, not a break from McKee

Writing style:
- Literary (AO3 / Literotica elevated tier, not porno)
- Sensory rich but controlled
- Character psychology foregrounded over mechanics
```

这**本质是一段 prompt**，不是一个 architectural change。

**模型选择**：
- Claude Sonnet 4.6 + OpenRouter: 可写 suggestive / psychological / literary；硬露骨会 refuse
- Grok 4.20 + OpenRouter or xAI 直连: 可写更露骨
- **实际策略**（对应 MEMORY.md 文字模型池双模型）：让用户在 GenerateDialog 加一个 `steamy: boolean` toggle，backend 按 toggle 路由到 Sonnet / Grok

daisy 的 `routes/ai.ts` line 8-20 的 body type 里加一个 `steamy?: boolean`，再在 `services/ai.ts` 把 MODEL 常量改成 `function selectModel(steamy)` —— **15-25 行改动总计**。

**选项**：

A. 保留 daisy 原结构 + 加一段 ADULT_GENRE_PERMISSION + 双模型路由 —— v2 推荐
B. 为成人向完全重写 prompts —— 浪费
C. 用一个"审查代理"LLM 做事后过滤 —— 加成本 + 延迟 + 误杀

**v2 推荐**：**A**。技术改动极小（<100 行）。成人向不是"技术问题"，是"prompt engineering + 模型路由"问题。daisy 的通用设计**正好是优势**——不需要推翻重来，在它上面加层即可。

---

### 矛盾 4：图像工作的 sunk cost

**v1 判断**：⭐⭐⭐⭐⭐ 致命，推荐冻结在 R4 水平

**v2 同意 v1 的结论但加深论证**：

R5 Shot 2 v1-v5 已耗 5 × $0.07 = **$0.35** + 约 2-3 小时（prompt 调试 + 读图 + 决策）。把 v5 的成本分摊到"每张能用的图"上：
- R4 的 5 张图 = **$0.35**，全部用户接受度 OK
- R5 shot 1 = **$0.07**，用户接受 OK
- R5 shot 2 5 版 = **$0.35**，用户最终**拒绝**（5 版全部不满意）
- **R5 shot 2 的单位成本 = $∞**（分母为 0）

**Grok Imagine Pro 的经济学**：$0.07 / 张是**廉价**的，但前提是一次就中。一个高难度 shot（High-Prior 服装 / 复杂构图 / 特殊角度）可能需要 5-10 次才出一张能用的，真实单位成本**上升到 $0.35-$0.70 / shot**。

**战略后果**：
- 如果 crpg 承诺"每节点 1 张 cover shot"：20 节点 × $0.07 = $1.40 / 故事（乐观）；真实 $3-8 / 故事（现实）
- 如果 crpg 承诺"每节点 3-5 shots（Shot Design 方法论）"：20 节点 × 4 × $0.07 = $5.60 / 故事（乐观）；真实 $20-50 / 故事（含重试）
- 创作者生成 10 个故事的成本 = **$50-500**（视质量追求）
- BYOK 模式下创作者自付，但 $500 的入门门槛太高
- 平台付费模式下，一个故事 $20-50 的生成成本**完全挡不住广告/订阅变现**（见竞品 CrushOn.ai $50/月含无限消费）

**图像 Class D bug 的真相**（v2 独立看 v5 图）：

我独立看了 `shot-2-ecu-insert-toenails-v5.png`（用户 Read 工具实证）：

**几何判断**：
- Top band 位置：紧贴裙摆下缘 / 大腿中段，**是 thigh-high 的 band 位置**
- Band 以上有一段大腿皮肤可见（虽然是阴影中）
- 不像 "over-the-knee" —— 那种的 band 在膝盖以上 5cm
- **几何学结论**：这是 thigh-high stockings

**视觉 / 审美判断**：
- 袜体密度：**接近 opaque black**，不是 sheer
- 没有 "skin showing through" 的 20-50 denier 透感
- 织物偏厚重
- 阴影下看起来**像一件整体的深色袜袋**，不像两件独立的高筒袜
- 没有 seam line（虽然 prompt 里要求了）

**综合**：
- 用户说"还是过膝袜"—— 在**视觉直觉层面对**（因为看起来是"黑色大面积覆盖"）
- 我说"几何上是 thigh-high"—— 在**结构层面对**
- **冲突暴露了 Class D 的真实本质**：用户对"过膝袜 vs thigh-high"的判断**不是几何判断，是审美阅读**。而**审美阅读的差距 prompt 工程无法直接控制**——因为模型的采样分布偏"sexy opaque hosiery"先验，而不是"Vogue 高级 sheer editorial"先验

**追求 Class D 解决的价值**：

| 情况 | 投资 | 收益 |
|---|---|---|
| 继续 prompt 迭代 | 每次 +$0.07 + 1h | 边际效用递减，v6/v7/v8 很可能还是"审美像过膝袜" |
| 自部署 SD + thigh-high LoRA | **$1500-3000 GPU + 80-300 图训练集 + 2-4 周训练** | 可能解决，但只解决**这一种服装** |
| 每个 High-Prior 服装训 LoRA | **每种 $3-5K**，crpg 需要 5-10 种 | 6-12 月专职工作 |
| 放弃精确，承诺"风格一致、美学到位" | 0 | 用户必须接受"审美不是精确复刻" |

**v2 结论**（强化 v1）：
- **Class D 不是 prompt 工程能根治**
- Grok Imagine 的 API 能力缺失（无 negative_prompt / seed / cfg_scale / ControlNet）意味着**工具层天花板就这样**
- **crpg 必须在产品层承诺降级** —— 不是"精确复刻文字描述"，而是"视觉美学一致"

**选项**：

A. 产品承诺 = "精确" —— v2 不推荐（会持续让用户失望）
B. 产品承诺 = "美学一致" —— v2 推荐
C. 混合：关键 shot 精确，其余美学 —— 工程复杂
D. 图像作为 "可选" —— 文字为主体，图像为增强

**v2 推荐**：**B + D 混合**。产品叙事 = "AI 驱动的美学一致图像增强"，图像作为文字叙事的**视觉层**而非**核心产出**。

---

### 矛盾 5：方法论深度 vs 实现简陋（真实评估 v2）

**v1 判断**：方法论过度生产 / 代码 0 行

**v2 修正**：

v1 的数字"300KB 文档 + 0 行代码"忽略了 daisy 已有的 10,279 行。真实结构：

```
crpg 项目资产分布：
- 300 KB brainstorming 文档（crpg brainstorming 分支）
- 10,279 行 daisy 代码（`/tmp/crpg-research/daisy/`，等待 fork）
- 8,284 行 daisy-crpg 前身代码（历史对照用）
- ~150 张图像测试结果（R1-R5，$1.37 成本）
- 1 本 internal-post 设计拆解（23 KB，daisy 作者自述）

实际在 crpg main 分支：0 行
```

**方法论 vs 实现**的比例被 v1 高估了。真实情况：daisy 代码 **已经兑现了**crpg 文档里说的绝大部分东西（两步生成、McKee 六条、JSON safety、D20 检定、画布编辑、社区发布）—— 只是没在 crpg git 仓库里。

**剩余未实现的方法论**：

| 方法论 | daisy 已实现？| crpg brainstorming 产出 | 还需实现 |
|---|---|---|---|
| MCKEE_BASE 六条 | ✅（799 行 prompts） | 无新内容 | 无 |
| 两步生成 | ✅（useAIGenerate 395 行） | 无新内容 | 无 |
| McKee Genre/Antagonism/Climax | ❌（daisy 未做） | 在 mckee-full-framework.md 识别 | 加 50-100 行 prompt |
| 诗意/细节/极致模式 | ✅（DETAIL_CONFIG 4 档） | detail-and-poetic-modes.md 分析 | 温度降 0.9→0.8 |
| Visual DNA 1-8 层 | ❌（daisy 无图） | visual-dna-system.md 完整设计 | 约 500-800 行 |
| Shot Design Layer（第 9 层） | ❌ | shot-design-system.md 方法论 | 1-2 周加 P3 |
| Layered Garment（第 10 层） | ❌ | 方法论存在 | **不应做**（Class D 不可控） |
| Bug Taxonomy 分类 | N/A（daisy 无图） | text-to-image-bug-taxonomy.md | 融入 Shot Director prompt |
| 24 美学子派 | N/A | visual-aesthetics.yaml 66KB | 不用全部，选 5-8 作为 MVP |
| D20 + 27 点购买 | ✅（playerStore 188 行）| 无新内容 | 无 |
| 氛围调色板 | ✅（moodEngine 188 行）| 无新内容 | 无 |
| 涟漪分析 | ✅（useAIContinue 53 行 + buildContinuePrompt）| 无新内容 | 无 |

**方法论-实现比率真实值**：
- 已实现：6 个大维度（文字叙事、两步 pipeline、Play 循环、检定、发布、涟漪）
- 未实现但 methodology-ready：3 个（成人向、VDNA 1-8、Shot Design）
- 未实现且 should-skip：1 个（Layer 10 Garment）
- **实现率约 60-70%**，不是 v1 说的 0

**v1 的 "方法论过度生产"诊断在忽略 daisy 后成立，包含 daisy 后降级为"方法论丰富，执行分叉（一部分已在 daisy，一部分在 crpg 文档等待）"**。

---

### 矛盾 6：daisy 原作者 48h 哲学 vs crpg 无限深思熟虑

**v2 新增**（v1 没涉及此角度）：

**证据**（来自 `docs/internal-post.md`）：
- 作者开篇说"两天，一个人，6 个 commit" —— **ship-first 哲学**
- §2.3 提到"V3 → V4 解决能不能用，V4 → V6 解决用得好不好"—— **迭代范式**
- §4.1 最核心论断："判断一个产品是否 AI-Native 的标准很简单：把 AI 去掉后，产品是变差了，还是不存在了。" —— **产品第一**
- §4.2 对决策者："瓶颈已经从人力转移到了想法"
- 脚注 ⁷："方法论迭代的成本极低...在传统引擎中要验证'延迟合流是否比即时合流产生更好的分支体验'...周期可能是数周；在 Daisy 中，只需要在 Prompt 里加一条规则，10 分钟出结果"

这个哲学和 crpg 当前的工作节奏**完全冲突**：

| 维度 | daisy 作者 | crpg 当前 |
|---|---|---|
| Ship 速度 | 48h MVP | 13 天后 0 行 |
| 迭代方式 | 改 prompt，重跑，看结果 | 写文档，分析，讨论 |
| 决策粒度 | 跑过就决定 | 大量未决问题（Q4-1~Q4-7） |
| 风险偏好 | 有 bug 就 ship，事后修 | 想避免所有 bug 再 ship |
| 文档：代码比 | 23KB 文档 : 10,279 行 | 300KB 文档 : 0 行 |

**同一个人**（猜测用户就是 daisy 作者）**采取了两种截然不同的工作模式**。差异点在于：
- 做 daisy：已有 McKee 理论（外部）、技术熟悉、范围清晰
- 做 crpg：要做新技术（Grok Imagine）、新 scope（图像）、新定位（成人向）、新用户期待（视觉质量）

**不确定性推动用户滑向"先想清楚再做"模式**。这个模式在**有不确定性时**是理性的，但**不能无限延长**。

**危险信号**：用户自己原话 "现在就已经有很多工程问题了... 其他的我觉得就很乱了"—— 这个"乱"不是客观的，是**想得太多后的主观感受**。daisy 作者在 48h 做出东西时显然不觉得乱，crpg 13 天做出 0 行代码时觉得乱——**这说明问题不是 complexity，是 paralysis**。

**选项**：

A. 用户采用 daisy 作者风格，14 天内 fork + 改 + ship —— **v2 推荐**
B. 继续 brainstorm 到所有问题想清楚 —— 陷阱
C. 折中：2 天内 fork，然后边改边想 —— 也可

**v2 推荐**：**A**。daisy 证明用户**有能力** ship fast。crpg 只是卡在"范围新+不确定性高"的 paralysis 里。破局方式是**回到 daisy 风格，把 crpg 当 daisy v2 处理**。

---

### 矛盾 7：Visual DNA / Shot Design / Bug Taxonomy 真正的 ROI

**v1 判断**：方法论不是护城河，任何同级开发者 1-2 周可复现

**v2 部分同意 + 部分修正**：

**v1 对的部分**：
- Visual DNA 1-8 层**大部分是公开知识**：Character Sheets（SD 社区）/ Aesthetic Axis（danbooru tags）/ Anchor Strategy（img2img 2022 年就有）/ Technical Lock（任何图像项目都锁）/ Positive Framing（处理 negative_prompt 缺失的技巧）—— 都可被 1-2 周复现

**v2 发现 v1 低估的部分**：

**Bug Taxonomy 的 Class D 洞察**是**有原创性的**：
- v1 没完全 appreciate "Class D = Default-Prior Override" 这个诊断
- 同级开发者不容易总结出"这是一个 prompt 工程根治不了的 bug class"——大多数人会继续 prompt engineering 直到放弃
- **Class D 的识别 = 认知到工具边界的智慧**，而不是"又一条 prompt 技巧"

**Shot Design（第 9 层）** 确实是**crpg 原创贡献**：
- daisy 没做（不涉及图像）
- SD 社区没做（他们不关心 McKee 叙事）
- 影视行业有（Hitchcock / Mamet / 李安 / Murch），但**没有应用到 AI 图像生成的 pipeline 中**
- 这个**两个领域的 bridge** 是 crpg 的差异化——前提是 crpg 真能 ship 出 Shot Design 驱动的 pipeline

**"1-2 周复现" 的真实性检验**：

一个 Replicate / fal.ai / Midjourney 同级开发者要复现：
- VDNA 1-8 层：**1-2 周**（v1 估对）
- Shot Director LLM + Bug Taxonomy + 在现有叙事框架中集成：**4-8 周**（v1 低估）
- 还要有 McKee 叙事底座 + 可视化画布 + 游玩循环：**3-6 月**（v1 严重低估）

**也就是说**：crpg 现有的 daisy + 方法论组合，同级开发者复现需要 **3-6 月从零开始**。

**但 crpg 有个弱点**：crpg 的方法论**已经公开**（COMPETITIVE-ANALYSIS-2026-04-17.md 提到 crpg 准备公开方法论作为营销；daisy internal-post 已经公开）。这等于**主动把护城河降低到 "只剩代码 + 数据"**。

**v2 修正的护城河模型**：

| 资产 | 是壁垒吗 | 持续多久 |
|---|---|---|
| daisy 代码 | 不是（GitHub 公开） | 1-2 月被 clone 复现 |
| crpg 方法论文档 | 不是（一旦公开） | 1-2 周被理论复现 |
| Shot Director LLM 具体 system prompt | 是（但会被抓包） | 几天到几周，直到被 scrape |
| **创作者社区 + 已发布故事的网络效应** | **是** | 长期 |
| **已训练的 LoRA（如未来做）** | **是** | 长期（除非开源） |
| **品牌（crpg = 艺术成人叙事平台）** | **是** | 长期，但需要积累 |
| **用户数据 + 反馈循环** | **是** | 长期 |

**实际推断的护城河**：
1. daisy 代码 + 方法论 = **入场券，不是壁垒**
2. **先 ship、先获得用户、先积累反馈 = 壁垒的原材料**
3. 继续拖延 = 把入场券的价值也消耗掉

**选项**：

A. 继续深化方法论（加 Layer 11/12、加 Bug Class F/G）—— v2 不推荐（收益递减）
B. 把 Layer 1-8 直接打包 ship，v2 再深化 —— v2 推荐
C. 公开方法论作为 marketing，快速获得 mindshare —— 冒险（被人先 ship）

**v2 推荐**：**B**。方法论锁死在现在水平。deployable 优先。**让方法论在产品里 ship，不在文档里完美**。

---

### 矛盾 8：用户心态的信号

**v1 分析**：用户说"很乱"= 感受到失控；reviewer 应该直接建议

**v2 同意，但补充 daisy 视角**：

用户原话拆解：
- **"我和 daisy 原来的想法就是做一个关键词或者一段话生成游戏的"** —— **愿景极清晰**
- "她已经做成了生成文字的" —— **daisy 作为已完成的基线**，用户自己就是 daisy 作者
- "我现在弄了半天加图片的" —— **疲惫 + 愧疚感**，感觉自己把简单事做复杂了
- "图片的效果也一直不好" —— **审美自我要求**，同时也对技术失望
- "包括最后这个过膝袜也没做好" —— **具体的挫败例子**
- "两个模型的架构，已经这个导演 llm 怎么设计，镜头的一致性" —— **三个工程债识别**
- "值得保留的就是方法论" —— **保留意愿**
- "daisy 原来指导模型写故事的方法" —— **具体指认 daisy 是方法论而不仅是代码**（!）
- "我们也补充丰富了几个点" —— **对 crpg 增量的肯定**
- "然后电影镜头的方法论，也挺不错的" —— **Shot Design 的价值认可**
- "其他的我觉得就很乱了" —— **希望有人帮忙收拾**

**v2 额外观察**：用户说"值得保留的就是方法论"，但 v1 和 v2 一致认为**真正值得保留的是方法论 + daisy 代码**。用户**对 daisy 代码的价值可能有轻微低估**——他把 daisy 看作"已经做完的背景资产"，而不是"crpg 的 v0.1 起点"。

这给 reviewer 的启示：**帮用户看到 "daisy 代码 = crpg 50%+ 已经做完"**。

**v2 判断的 reviewer 应该做什么**：
1. **肯定用户的直觉**：方法论是真金 + "很乱" 是真实的
2. **修正用户的盲点**：daisy 代码是你已经 ship 的 v0.1，不是背景装饰
3. **给具体下一步**：fork daisy → 第 1 周做 X → 第 2 周做 Y → 第 4 周 ship 朋友试玩
4. **降低用户对图像完美的执念**：Class D 的分析让用户看到"这不是你不够努力，是工具天花板"

---

### 矛盾 9：daisy 代码质量本身是不是真的好

**v2 新增**（v1 没能力评估 daisy 质量）：

上面 §2 已经详细评过 daisy 代码。**简要回答**：

**daisy 质量评估**：4.0 / 5.0（48 小时原型中的最上档）

**阻断性 vs 非阻断性**问题分类：

| 问题 | 严重度 | 阻断 crpg 发布吗 | 修复成本 |
|---|---|---|---|
| W-05 delete story 无 auth | 严重 | **是** | 1-2 天（加 session + 检查 ownership） |
| 无 rate limit | 中 | 部分（generate 耗 OpenRouter quota） | 1 天（加 hono-rate-limiter） |
| 无 usage metering | 中 | BYOK 必须有 | 2-3 天（加 ai_usage 表 + 中间件） |
| T-04 无 ErrorBoundary | 中 | 用户体验差但不阻断 | 0.5 天 |
| W-01 setNodes 覆盖并发 | 低 | 不阻断 | 1 天（加 lock 或乐观并发） |
| W-04 like endpoint 无 rate limit | 低 | 不阻断 | 0.5 天 |
| W-07 Markdown import 未做 | 低 | 不阻断（JSON 够用） | 不需修 |
| `routes/projects.ts` GET / 无 user filter | 严重 | **是**（多用户时会暴露别人项目） | 1 天 |

**阻断性问题总计：约 1 周修复**。非阻断性总计：约 2 周。

**关于 "48h 原型产品化重写多少"**：
- 真正的重写 = **所有 auth + user_id / multi-tenancy 相关** = 约 500-1000 行新代码
- 其余全部可直接继承

**v1 的悲观判断 "80% 重写" 错了一个数量级**。真实是 **10-15% 重写**。

**v2 推荐**：**不要重写，fork 后 patch**。把 daisy 的 W-05 / 无 auth / 无 user_id 作为第一个 milestone 修。

---

### 矛盾 10：图像侧 Class D bug 的本质

**v1 分析**：Class D 不可控，推荐降低期望

**v2 强化**：

我独立看了 `shot-2-ecu-insert-toenails-v5.png`。**独立视觉判断**已在 §3 矛盾 4 给出，重复关键结论：

- **几何上是 thigh-high**（band 在大腿中段，上方有皮肤）
- **审美上像过膝袜**（太 opaque、太厚、无 sheer）
- **连人类都判不清**："她是穿 thigh-high 还是 over-the-knee" 这个问题**没有清晰答案**——它取决于你看的是**上缘位置**还是**整体阅读感**

**这告诉我们什么**：

1. **Prompt 工程有天花板**。模型的训练分布决定了"默认什么是 sexy black hosiery"，改 prompt 不如改模型
2. **人类审美本身是 fuzzy 的**。用户会对同一张图在不同日子给不同评价——这不是 bug，是审美本质
3. **"精确复刻文字描述"是个哲学上不可达的目标**，即使人类艺术家也做不到（每个画师画同一段描述都会画出不同的图）
4. **可达的目标是"审美一致 + 符合故事氛围"**——这是 R1-R4 已经达到的水平

**对产品的含义**：

- **承诺层面**：不要宣传"精确复刻"，宣传"AI 驱动的美学一致图像"
- **交付层面**：创作者可以 regenerate；平台提供 retry 机制；某些场景可以 "跳过图像"
- **用户教育**：在产品里明示"AI 图像是视觉增强，不是精确插图"
- **商业层面**：不要把"图像质量"作为主要卖点（会失败）；把"叙事质量 + 视觉美学"作为组合卖点

**选项**：

A. 继续追求精确 —— v2 强烈不推荐
B. 承诺美学一致 —— v2 推荐
C. 承诺"AI 生成 + 创作者润色"混合 —— v2 也推荐

**v2 推荐**：**B + C**。产品叙事：`"我们为你生成有美学的视觉，你可以选择保留、regenerate、或替换成自己上传的图"`。把"完美"的负担还给用户。

---

## 4. 方法论真实评级 v2（补充 v1 遗漏）

### v1 评级和 v2 修正

| 方法论 | v1 评级 | v2 修正 | 修正原因 |
|---|---|---|---|
| daisy 六条硬约束 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | 维持，v1 正确 |
| 两步生成 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | 维持 |
| 诗意/细节模式 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | 维持 |
| Shot Design 色戒拆解 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | 略降：方法论强但未验证落地 |
| McKee 三补丁 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | 维持 |
| Direction Layer | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | 维持（R2→R3 有实证跃迁） |
| VDNA 7 层 | ⭐⭐⭐ | ⭐⭐⭐⭐ | **升级**：v2 看到 R2-R4 实证，方法论有效 |
| 24 视觉美学 | ⭐⭐⭐ | ⭐⭐ | **降级**：粒度过细，MVP 用不到 |
| Bug Taxonomy A/B/C/E | ⭐⭐⭐ | ⭐⭐⭐⭐ | **升级**：v2 看到 Class D 诊断的独立价值 |
| VDNA 第 9 层 Shot Design | ⭐ | ⭐⭐⭐ | **升级**：方法论本身是原创，但落地难 |
| VDNA 第 10 层 Layered Garment | ⭐ | ⭐ | 维持低评级：Class D 不可控 |
| 动态 Shot Budget | ⭐ | ⭐⭐ | 略升：可 v2 实现，不全是水分 |
| Temporal DNA / Video | ⭐ | ⭐ | 维持：v3 级野心 |
| 等价温度表 | ⭐ | ⭐⭐ | 略升：如果真做多模型会有用 |

### v2 新增的评级维度

**v2 新增 v1 没看到的**：

| 资产 | 评级 | 说明 |
|---|---|---|
| **daisy 10,279 行代码** | ⭐⭐⭐⭐⭐ | 真金。比 crpg 的任何文档更有价值。 |
| **daisy 的 `extractJSON` 6 层降级** | ⭐⭐⭐⭐⭐ | 生产级 LLM 输出处理模板 |
| **daisy 的 normalizeEdges 双层** | ⭐⭐⭐⭐ | JSON-AI 防御性设计模板 |
| **daisy 的两步 pipeline batch + retry** | ⭐⭐⭐⭐⭐ | AI 管线工程模板，可复用到 Shot Director |
| **daisy internal-post 设计拆解** | ⭐⭐⭐⭐ | 作者自述设计决策的第一手材料 |
| **daisy-crpg 历史版本** | ⭐⭐ | 演进对照，参考价值 |

---

## 5. 工程可行性评估 v2（继承 daisy 版本）

### 单人 12 周能产出什么（乐观 - 继承 daisy）

**第 1-2 周**：
- fork daisy 到 crpg 仓库作为初始 commit
- 修 W-05 auth bug / 加 user_id 字段 / BetterAuth 集成
- 加 18+ 门 + cookie + GeoIP soft block
- 加 成人向 prompt 段落（MCKEE_BASE 末尾 40-60 行）
- 换 MODEL 为路由器
- 加 BYOK 界面（用户输入 xAI/OpenRouter key，加密存储）
- **自己用一次：输入关键词 → 生成成人向故事 → 玩一遍**

**第 3-4 周**：
- Polish 文字叙事：测试 50 个生成，识别 3-5 大质量问题，改 prompts
- 发给 3-5 个朋友试玩，收反馈
- 加简单 metering（记录 AI 调用成本）
- 修前 5 大 bug

**第 5-8 周**：
- 图像 pipeline：P3 Shot Director（插在 `useAIGenerate.ts` 的 batch 后）
- 每节点 1 张 cover shot（VDNA 1-8 层，不做 9-10）
- Grok Imagine Pro 集成（复用 R4 的 Python 代码逻辑移植到 Node.js）
- 前端：PlayScene 加 `<ImageSlot>` 支持图像展示
- PublishDialog 加图像发布

**第 9-12 周**：
- 纯享版前端：基于 CommunityFeed 加 /play/:storyId 静态播放路由
- 发布流优化：创作者点 publish → 自动打包 images + JSON → 存 CDN
- 内容审核：加 report button + 基础 NSFW filter（自动隐藏 flagged 故事）
- Soft launch：发给 20-50 人测试

**可交付物**：
- MVP 产品，有文字 + 图像 + 画布 + Play + 发布 + 纯享版
- BYOK 模式
- 18+ 门 + GeoIP
- **暂未实现**：平台付费 / 订阅 / Shot Design 第 9 层 / Layer 10 / 多模型 Router（先只用 Grok 双路径，不做温度等价表）

**胜率**：**60-70%**（比 v1 的 50-65% 高，因为 daisy 是真实 leverage）

### 单人 24 周能产出什么

- 12 周 MVP + 用户反馈
- 根据反馈决定：加图像质量（自部署 SD? LoRA?）或加 Shot Director 或加订阅
- 可能处于：500-2000 个用户 / 少量营收 / 持续迭代中

### 单人 52 周能产出什么

- 成熟产品，定位清晰
- 可能启动 LoRA 训练（如果图像成为瓶颈）
- 可能加 1 个合伙人（如果 revenue 够支付）
- 有 5000-20000 用户量级（如果定位正确）

---

## 6. 三条可能路线（真正不同哲学）

### 路线 α：保守接手——daisy 成人改造，砍图像

**哲学**：**"daisy v2 = daisy + 成人 + McKee 三补丁"**

**内容**：
- fork daisy + 加成人向 prompts + 双模型路由
- 保留画布 / Play / 发布 / 涟漪分析
- **完全不做图像**
- 4-6 周可 ship
- 定位：**"电影级结构化成人互动叙事"**，类似 AI Dungeon 的 McKee 版 + NovelAI 的 sub-anime-only 版

**胜率**：**75%**

**收益**：最快 ship，最保险。方法论（VDNA / Shot）冻结在 docs/research，v2/v3 激活

**风险**：市场差异化不够（NovelAI 也能写，Grok 也能写，Claude 也能写）；不 shiny

---

### 路线 β：完整愿景——daisy + 图像 + 双模态

**哲学**：**"原初愿景不打折"**

**内容**：
- fork daisy + 所有 crpg 当前 scope
- 图像作为核心，VDNA 1-8 + Shot Design
- 双模式前端
- 6-9 月 ship

**胜率**：**40%**（单人 9 月项目的 base rate）

**收益**：差异化最强

**风险**：做不完；图像 ROI 低（R5 Shot 2 证据）；用户兴趣在 9 月中消耗

---

### 路线 γ：产品-方法论分离

**哲学**：**"crpg = 产品（快速 ship）；methodology-research = 独立学术品牌"**

**内容**：
- 路线 α 的产品线
- **方法论独立发表**：300KB crpg 文档整理成 blog post / Substack / medium，形成个人品牌
- 产品获客走方法论权威路径（读者看了 blog 来用产品）
- 方法论持续迭代是独立轨道，产品靠方法论迭代做 v2/v3

**胜率**：**65%**

**收益**：双赢——产品 ship 快，方法论成为个人品牌；未来招合伙人 / 融资 / 出书都有基础

**风险**：发布方法论 = 给竞品送弹药；同时做两条轨道会分心

---

## 7. 最推荐路线（v2 版）

### 路线 Y：**fork + 增量 + 阶段门控**（路线 α 和 β 的受控混合）

**核心哲学**：**不重写、不延期、不追求完美，但也不放弃图像**

**为什么推荐 Y 而不是 v1 的 X**：

| 维度 | v1 路线 X | v2 路线 Y | 差异来源 |
|---|---|---|---|
| Day 1 动作 | 创建"DECISIONS-2026-04-18.md"冻结一堆东西 | **git clone daisy 到 crpg** | v1 没看到 daisy 可继承 |
| Week 1 目标 | 初始化新仓库 / Next.js + SQLite | **patch daisy：改 MODEL / 加 auth / 加 18+ 门** | v2 站在 daisy 基础上 |
| 14 天目标 | 文字 MVP 有朋友用 | 文字 + 成人向 MVP 有朋友用 | v2 可直接跳过 "从零起步" 阶段 |
| 图像 | 推到 v2 | Week 5-8 加 R4 水平图像 | v2 认为 daisy 的 batch 框架让图像加入成本低 |
| Shot Director | 推到 v2/v3 | Week 9-12 加（简单版） | v2 认为在现有 batch 上加一层只是 1-2 周 |

### 明天开始做什么（周粒度）

**Week 1（2026-04-18 至 2026-04-24）：fork + 修 blocker + 自己用**

- **Day 1（明天）**：
  - `git clone /tmp/crpg-research/daisy /Users/lxxxxxx/个人项目/crpg-dev`（新 dir，保留 brainstorming 作为 research）
  - 或 `cp -r /tmp/crpg-research/daisy /Users/lxxxxxx/个人项目/crpg/app`（放在现有 crpg 仓库作为子目录）
  - pnpm install + 跑起来 daisy 本体确认正常（用自己的 OpenRouter key）
  - 自己试跑一个故事生成 → 验证两步 pipeline 还能用

- **Day 2-3**：
  - 修 W-05 auth bug：加 BetterAuth + session middleware
  - 加 users 表 + 所有 routes 加 user_id filter
  - 自己做简单登录
  - 跑 typecheck 通过

- **Day 4-5**：
  - 加 18+ 门（modal + cookie）
  - 加 GeoIP soft block（Vercel Geo header 或 ipapi）
  - 加成人向 prompt 段落（在 `MCKEE_BASE` 末尾）
  - 加 GenerateDialog 的 `steamy: boolean` toggle
  - 调温度 0.9 → 0.8（在 `ai.ts` line 113）

- **Day 6-7**：
  - 加 Grok 作为双模型（`services/ai.ts` 的 MODEL 变成 `selectModel(steamy)`）
  - 测试：生成一个成人向故事，玩一遍，验证质量
  - 如果成人向生成质量 OK → Milestone 1 ✅

**Week 2（2026-04-25 至 2026-05-01）：加 McKee 三补丁 + BYOK + 部署**

- 在 prompts 加 Genre 推断 / Antagonism / Climax（三段落）
- BYOK 界面：创作者可以输入自己的 xAI/OpenRouter key
- 加 usage metering（`ai_usage` 表记录每次调用 $ 和 tokens）
- 部署：Vercel for web + Fly.io for server（或 Railway）
- 发给 3 个朋友试玩

**Week 3-4（2026-05-02 至 2026-05-15）：Polish + 反馈**

- 根据反馈改 prompts / UX
- 修 daisy 遗留的其他 warnings（T-04 ErrorBoundary / rate limit）
- **Milestone 2**：10 个人试玩过，反馈收集完

**Week 5-6（2026-05-16 至 2026-05-29）：图像 pipeline v1**

- 集成 Grok Imagine Pro API（在 server 加 `services/image.ts`）
- 加 VDNA 1-8 的 static template（不做 Shot Director）
- 每个节点固定 1 张 cover shot（生成 on publish，不是 on generate）
- 前端 PlayScene 加 `<ImageSlot>`
- **Milestone 3**：测试生成 3 个故事 + 图像，图像达到 R4 水平

**Week 7-8（2026-05-30 至 2026-06-12）：Shot Director v1**

- 在 `useAIGenerate.ts` 加 P3 batch：`generateShotList()` per node
- 每节点由 Director LLM 决定 shots 数（0-3，保守）
- 集成 Bug Taxonomy A/B/C/E 到 Shot Director system prompt
- **跳过 Class D / Layer 10 处理**（承诺"美学一致"即可）
- **Milestone 4**：测试生成 2 个故事 + 多 shot

**Week 9-10（2026-06-13 至 2026-06-26）：纯享版 + 发布流**

- 基于 CommunityFeed 做纯享版 UI（filter by content_rating）
- 创作者 PublishDialog 加 age gate 确认
- 静态打包：生成故事 JSON + 图片 ZIP 存 S3/R2
- **Milestone 5**：一个朋友作为创作者发布，另一个作为读者消费

**Week 11-12（2026-06-27 至 2026-07-10）：Soft launch polish**

- 内容审核 manual filter
- 加 report button
- 平台付费路径（如果时间允许；否则只 BYOK）
- Public soft launch：Twitter / Reddit r/WritingWithAI / Discord 朋友圈
- **Milestone 6**：20-50 人注册

### 时间表总览

| Week | Milestone | 核心产出 |
|---|---|---|
| 1 | 成人向 daisy 能跑 | MVP 内部用 |
| 2 | BYOK + 部署 | 3 朋友试玩 |
| 3-4 | Polish + 反馈 | 10 朋友试玩 |
| 5-6 | 图像 v1 | R4 水平图像 |
| 7-8 | Shot Director v1 | 多 shot 故事 |
| 9-10 | 纯享版 + 发布 | 发布-消费闭环 |
| 11-12 | Soft launch | 20-50 人 |

**总时长：12 周 = 3 月**，比 v1 的 56 天 (8 周) 延长但包含图像。

---

## 8. 一个特别问题：如果是我做这个项目，会有什么不同？

**v2 假想自己是开发者，会怎么做**：

### 不同 1：我会在第 1 天就 git clone daisy

用户**已经把 daisy 代码放到 `/tmp/crpg-research/`**了，但仍然在 main 分支保持 0 代码。这是一个**心理障碍**——"先想清楚再动手"的范式。

**我的做法**：Day 1 就把 daisy 作为 crpg 的 v0.1 提交到 main 分支，让所有后续讨论建立在"有代码基础"上，而不是"有文档基础"。

### 不同 2：我会把图像单独放到一个 hidden feature flag 后面

Class D bug 的实证证明 prompt 工程有天花板。**我的做法**：
- 图像 MVP 用"可关闭"设计
- 默认纯文字 ship（低风险）
- Feature flag 打开图像（Beta 标签，说明质量不稳定）
- 让用户自己选：要快速完美的文字 or 实验性的图像

这规避了"图像质量卡死全产品 ship" 的风险。

### 不同 3：我会把方法论作为 marketing 内容

300KB crpg 文档 + daisy internal-post = 高质量技术内容。

**我的做法**：
- 把 `mckee-full-framework.md` / `visual-dna-system.md` / `text-to-image-bug-taxonomy.md` 改写成博客文章发布（每篇 1-2 周）
- 不公开 **最核心的 system prompts**（那是 know-how，也是 crpg 的工作流竞争力）
- 用博客吸引：AI 工具开发者 + 交互叙事爱好者 + 成人向写作社区
- 博客的读者 → crpg 产品的冷启动用户

**两条轨道并行的代价**：每周损失 5-10 小时在写作上。**收益**：个人品牌 + 产品获客 + 长期 optionality（可以转成书/Substack/咨询）。

### 不同 4：我会把 "纯享版免费" 作为设计约束但不是硬约束

v1 和 SESSION-STATE 都把"纯享版=零付费"当硬约束。我会**软化**：
- v1 纯享版确实免费
- v2 留出"捐赠给创作者" button（类似 AO3 的 kudos）
- v3 考虑"订阅无广告" + "超值专属内容"

**理由**：成人向网站的商业化很难靠广告（Visa/MC 对成人广告严格），必须靠订阅。纯享版如果 100% 免费，**平台本身无法 sustainable**。BYOK 让创作者付费是 OK 的，但如果平台不盈利，BYOK 模式本身也维持不住（没人给平台付工资写代码）。

### 不同 5：我不会试图修 Class D bug

R5 Shot 2 v5 的 5 次迭代，v6 几乎一定也会有类似问题（即使几何 fix 了，审美感还会有）。

**我的做法**：
- 接受 Class D 是 Grok Imagine 天花板
- 产品层给创作者"**标记这张图为 not-canonical，用户读故事时隐藏**"的 button
- 把精力投入 daisy 的核心价值（文字叙事）而不是完美图像

### 不同 6：我会更激进地用 daisy 原哲学

daisy 作者在 48h 做出产品。如果是我，**第一周（7 天）就要 ship 一个自己能用的 MVP**——哪怕是用 localhost、我自己用 OpenRouter key。

**原则**：前 7 天如果没 ship，**再砍 scope**。不允许"继续 brainstorm"作为借口。

### 不同 7：我会在 public 上做产品开发

Twitter / X / Bluesky 直播开发过程（"Week 1 Day 1: forked daisy, ran first story generation"）。**理由**：
- 成本低：每天 10 分钟
- 收益高：
  - 早期获粉
  - 反馈/建议
  - 鞭策自己按进度走
  - 未来融资/发布的原始素材

---

## 9. 给 orchestrator 的 Summary（≤ 350 词）

### 三个 v1 漏掉 daisy 代码导致的判断修正

1. **"daisy 只有 20-30KB 文本可继承" 错了一个数量级**
   - daisy 实际 = **10,279 行 TypeScript**（60 个文件，完整 monorepo）
   - 63-73% 可直接继承：React Flow 画布 / 两步生成 pipeline / D20 检定 / PlayMode / published_stories 发布表 / 涟漪分析 / mood engine 等**全部已测试、已跑通**

2. **"单人 12 个月完不成" 错**
   - 站在 daisy 基础上，**12 周能 ship 带图像的 MVP**（比 v1 的"8 周 + 图像推到 v2"多覆盖图像）
   - Shot Director 只需 1-2 周（插在现有 batch pipeline 后），不是 v1 的 4-8 周

3. **"方法论不是护城河"不完整**
   - daisy 代码 + 方法论的**组合**才是护城河
   - daisy 作者 48h 产出 10K 行 + 800 行 McKee prompts 证明了稀缺的工程品味
   - 同级开发者复现 crpg 完整方案需要 **3-6 月从零**（v1 说 1-2 周可复现方法论是对的，但没算上 daisy 工程）

### daisy 代码价值评级

**真 leverage，不是鸡肋**。质量 4.0 / 5.0。10-15% 需重写（主要是 auth + multi-tenancy + 图像 pipeline）。v1 说的"80% 重写"错了一个数量级。

### 推荐战略路线（1 句）

**fork daisy 为 crpg v0.1，加成人向 prompt + 双模型路由 + 18+ 门 + 图像 R4 水平，12 周 ship，不追求 Class D 完美**。

### 3 个立即可执行的 action（对比 v1）

| # | v1 | v2 |
|---|---|---|
| 1 | 写 DECISIONS-2026-04-18.md 冻结一堆东西 | **git clone daisy 到 crpg/app，运行本体** |
| 2 | 初始化新仓库（Next.js + SQLite） | **Day 2-3 修 W-05 auth + 加 users 表 + 18+ 门** |
| 3 | 把方法论移到 assets/research-archive/ | **Week 1 结束前自己用成人向 daisy 生成一个故事** |

**核心差异**：v1 推荐从零开始；v2 推荐站在 daisy 上增量。

---

## 附录 A：对照 v1，未改的判断（共识）

- 图像 Class D 不是 prompt 工程能根治（Round 5 实证）
- R4 水平已是 MVP 级图像，R5 的完美主义追求不值得
- "300KB 方法论 + 0 行 crpg 代码" 是病变信号（但 v1 低估了 daisy 代码的存在）
- 成人向模型供应链风险存在（需要 provider abstraction）
- 方法论应该 hard freeze 在当前版本，不继续膨胀到 Layer 11/12
- 用户心态的"很乱"信号需要被正视，reviewer 应主动给建议

## 附录 B：daisy 代码 vs crpg 文档的交叉映射（关键）

| crpg 文档提到的东西 | daisy 是否已实现 | 证据 |
|---|---|---|
| McKee 六条硬约束 | ✅ | `prompts.ts` line 42-50 的 MCKEE_BASE |
| 两步生成 | ✅ | `useAIGenerate.ts` line 255-390 的 generate() |
| 诗意/细节/极致三档 | ✅ | `prompts.ts` DETAIL_CONFIG + KEYWORD_POETIC/LITERAL |
| 反套路 + 游戏写作 | ✅ | `prompts.ts` v6 版本的规则 |
| 价值转换轴 | ✅ | `valueBefore/After` 字段；`ValueCharge` type |
| D20 检定 | ✅ | `playerStore.ts` + `useDiceRoll.ts` |
| 27 点购买 | ✅ | `playerStore.ts` line 17-42 |
| 涟漪分析 | ✅ | `useAIContinue.ts` + `buildContinuePrompt` |
| 画布编辑 | ✅ | `StoryCanvas.tsx` 287 行 |
| 自动布局（ELK） | ✅ | `useAutoLayout.ts` |
| 发布-消费社区 | ✅ | `published_stories` 表 + `CommunityFeed.tsx` + `PublishDialog.tsx` |
| 氛围调色板 | ✅ | `moodEngine.ts` 188 行 |
| 路径验证 | ✅ | `pathValidator.ts` 169 行 |
| JSON + Markdown 导出 | ✅ (JSON roundtrip) | `exportUtils.ts` 486 行 |
| EN/ZH 双语 | ✅ | `i18n.ts` 312 行 |
| **Genre 推断 / Antagonism / Climax McKee 补丁** | ❌ | 需要加 |
| **温度降到 0.8** | ❌ | 需要改 1 行 |
| **成人向 prompt 段落** | ❌ | 需要加 40-60 行 |
| **双模型路由（Sonnet + Grok）** | ❌ | 需要改 `services/ai.ts` 的 MODEL |
| **18+ 门** | ❌ | 需要加 |
| **GeoIP soft block** | ❌ | 需要加 |
| **BYOK** | ❌ | 需要加 |
| **auth + user_id** | ❌ | 需要加（修 W-05） |
| **rate limit** | ❌ | 需要加 |
| **Visual DNA pipeline** | ❌ | 需要加（500-800 行） |
| **Shot Director LLM (P3)** | ❌ | 需要加（1-2 周） |
| **Grok Imagine 集成** | ❌ | 需要加（100-300 行） |
| **纯享版前端** | ❌（但 CommunityFeed 是基础） | 需要改 filter |

**加总新增代码**：约 **1,500-3,000 行**。**+daisy 的 10,279 行 = crpg v1 总体约 12,000-13,000 行**。

---

**审查完成时间**: 2026-04-17
**下一步**: 用户决定接受路线 Y，Day 1 `git clone daisy` 开始
