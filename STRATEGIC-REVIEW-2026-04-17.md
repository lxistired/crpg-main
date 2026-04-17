# crpg 战略审查 —— 2026-04-17

**审查人**: 独立 Review 角色（非之前参与过 brainstorming 的 Claude persona）
**审查范围**: 项目整体定位、路径、工程取舍、根本矛盾
**审查立场**: 对用户的自我怀疑做独立裁决，不复读、不讨好、不维护既有叙事
**材料**: SESSION-STATE-2026-04-17.md / MEMORY.md 7 条 / daisy-narrative-core 方法论资产 / R1-R5 测试图实证判断

---

## 0. Executive Summary（一页内）

**项目现状**：一个**方法论深度显著过剩、工程产出为零**的项目。用户原本想"从关键词生成游戏"（daisy 48 小时已证明可行），现在积木已经搭成"多模态电影级叙事产品 + 双模式 + 双模型 + 10 层 Visual DNA + Shot Director + 合规层"。方法论资产约 **300KB 文档 + 5 轮图像测试 + $1.37 成本**，代码产出 **0 行**。

**最致命的三个战略矛盾**：

1. **方法论产出速率 >> 工程产出速率**，并且方法论在自我膨胀（7 层 → 8 层 → 9 层 → 10 层，预计 11/12 层）。每一轮图像测试暴露新 bug 都被固化成"新的 Visual DNA 层"。这是**学术生产**而不是**产品工程**。
2. **图像质量的最后一公里不是 prompt 能解决的**——Round 5 Shot 2 v1-v5 的连续失败实证了这一点（用户判定 v5"还是过膝袜"，我独立判断 v5 几何上是 thigh-high 但**颜色太深没 sheer 到位**，所以"过膝袜感"是审美而非定义问题——也就是说连人都判不清楚模型到底哪里错了，这是更深的麻烦）。
3. **继承 daisy = sunk cost 心理**：daisy 是单一 Sonnet + 文字 + 48 小时原型。crpg 要做成人向、双模型、图像、双模式、画布编辑——继承的代码能复用的其实不到 30%，但"我在 daisy 基础上做"的心理让项目表面复杂度加了一层但 leverage 极少。

**方法论真实水平（独立评级）**：
- **真金**：Shot Design System（色戒 coverage 方法论 + Murch + Hitchcock + Mamet 综合）、McKee 补入（Genre/Antagonism/Climax）、Direction Layer（R2→R3 从 stock photo 到 candid 的跃迁是真实的）、Bug Taxonomy Class A/B/C/E（有实证）
- **水分**：10 层 Visual DNA 的层数通胀（真正独立的层就 4-5 个，剩下是子字段拔高成层）、"24 美学轴 × 12 Genre = 288 组合"的矩阵焦虑、"护城河" narrative（方法论可以被任何同级开发者在 1-2 周内复现）
- **待验证**：Bug Class D 的"机制化解法"到底能不能在新故事新服装上泛化（现在只有一个故事、一双丝袜的孤证）

**推荐战略路线**：**路线 X —— 砍掉一半，锁一半**。
- 砍：图像生成作为**产品核心价值**的地位 / Shot Director LLM 的"核心护城河"定位 / 10 层 Visual DNA 的继续膨胀
- 锁：文字叙事（daisy 继承 + McKee 三补丁）作为 **MVP 的唯一价值主张**；图像降为"创作者可选增强 + 纯享版最多一张 cover"；双模式锁住"纯享版完全静态 + 创作者版 BYOK"作为首版
- 动：**14 天内产出可用的文字 MVP**，把剩下一切图像 / Shot Director / 产品化 pipeline 全部推到 Phase 2

**立刻要做的三件事**（下面有详细展开）：
1. **停止所有图像轮次的继续测试**。R5 之后不要 R6。这是方法论自我娱乐。
2. **14 天内做出文字 MVP**：daisy 代码 + crpg 三补丁（Genre/Antagonism/Climax）+ 18+ 门 + 地区 soft-block + 最小 SQLite。**不碰图像**。
3. **把图像工程冻结在 R4 水平**：R4 证明"身份 + 一致性 + vibe"可达到产品 MVP 级（见 §9 视觉判断）。R5 是追求完美主义的时刻，不是追求 MVP 的时刻。

---

## 1. 项目是什么 vs 项目现在在做什么

### 用户最初的意图（种子层）
> "我和 daisy 原来的想法就是做一个关键词或者一段话生成游戏的"

这是一句话的产品：**输入 = 关键词，输出 = 可玩的互动叙事**。
- daisy 已经在文字层面做到了，48 小时内。
- "加图片"是**增强**而不是重定义。

### 现在项目实际的形态（膨胀层）
- 双模式前端（纯享版 + 创作者版）
- 双模型池（Sonnet + Grok，按露骨度路由）
- 10 层 Visual DNA + Shot Director LLM + Prompt Assembler + Image Batch Worker（3-pass + 2-engine pipeline）
- 24 美学子派分类 + Genre 推断子系统 + 6 大美学轴理论
- 5 类 Bug Taxonomy + 每类对应 Visual DNA 层 + 每次 iteration 自动回流
- Layered Garment Visibility Rule（仅为 thigh-high stocking 一个服装类专门开的层）
- 合规层：18+ / 禁区 / GeoIP / 审计 / 模型侧 ToS
- 成本分摊模型（平台付费 or BYOK）
- 创作者 → 纯享版发布流（Q4-7 未决）
- 视频扩展储备（Temporal DNA）

### 差距诊断
项目从"关键词 → 游戏"**膨胀**到"产品化的视觉-叙事-合规-多模态 AI 内容平台"。这是 **20-80 人公司 18-24 个月的 scope**。用户是单人开发者。

**问题不是"想得多"，是"把每一个延伸当成 MVP 的必要条件"**。双模式对 MVP 不必要。Shot Director LLM 对 MVP 不必要。10 层 Visual DNA 对 MVP 不必要。甚至"加图片"本身都可以推迟。

---

## 2. 十大战略矛盾（独立诊断）

### 矛盾 1：单人可执行性 vs 项目复杂度

**定义**：crpg 目前的 scope 是多个独立子系统的集合。

**证据**：
- 文字生成（daisy 继承，~30% 可复用，70% 需重写）
- 图像生成（10 层 Visual DNA，每一层都是独立工程）
- Shot Director LLM（用户自己定性为"核心护城河"，意味着不是几天能做完的模块）
- 双模式前端（静态 + 画布编辑，两套完全不同的 UX）
- 双模型路由层（温度等价表、露骨度路由）
- 合规层（18+ 门、GeoIP、审计、ToS 兼容）
- 发布流（Q4-7 未决）

**典型独立开发者的 6 个月产能基准**（基于行业经验）：
- 1 个有用户价值的核心功能 + 1 个支撑性后端 + 1 个基础前端 + 极基础的运维
- 例如："文字叙事生成 + SQLite + React 画布 + Vercel" — daisy 48 小时那部分的工程化版，扩展到 BYOK 和 McKee 三补丁

**严重程度**：⭐⭐⭐⭐⭐（致命）

**选项**：
- A. 维持 scope，接受 12-18 个月交付时间表（风险：用户放弃 / 市场变化 / API 收紧前做不完）
- B. 砍 scope 到 MVP 文字 + 18+ 门 + 基础发布，图像推到 v2（风险：差异化不足）
- C. 维持 scope 但招 1-2 个合伙人（风险：成人向定位找合伙人难，且 crpg 目前没有融资）

**我的推荐**：**B**。独立开发者能活下来的唯一方式是**狠狠地砍 scope 到一个能在 4-8 周内上线的版本**。产品活下来了才有资格谈护城河。6 个月的 scope 在独立开发者身上 = 12 个月 = 永远做不完。

---

### 矛盾 2：daisy v2 继承 vs 全新产品的张力

**定义**：用户把 crpg 定位为"daisy 的 v2 演进"，但 crpg 的需求几乎重写所有 daisy 代码。

**证据**：
- daisy 是单一 Sonnet → crpg 是双模型池（**模型路由层全新**）
- daisy 文字 only → crpg 文字 + 图像（**图像 pipeline 全新**）
- daisy 画布单用户 → crpg 双模式（**前端发布流程全新**）
- daisy 没合规层 → crpg 18+/GeoIP/审计（**合规层全新**）
- daisy SQLite 本地 → crpg 需要多用户 + 可能 CDN（**数据层重构**）
- daisy 没付费 → crpg 双路径成本（**账单层全新**）
- daisy 温度 0.9 → crpg 温度 0.8 + 等价表（**参数层重构**）

**唯一真正复用的是**：daisy 的 `MCKEE_BASE` 文字 prompt 结构 + 两步生成哲学 + 798 行 prompts.ts 的 system prompt。这约等于 **20-30 KB 可复用的文本资产**，不是代码。

**严重程度**：⭐⭐⭐⭐（高，但不致命）

**诊断**：这是典型的 **sunk cost fallacy**。用户在把"我熟悉 daisy" / "daisy 的想法继承感"包装成"技术继承"。实际上 crpg 的技术选型应该**从 0 开始按 crpg 自己的需求设计**，只在 prompt engineering 层把 daisy 的 prompts-v6.ts 作为**文本参考资料**引入。

**选项**：
- A. 当前路径："基于 daisy 魔改"——继续有"我在 daisy 基础上做"的心理安慰但实际 80% 重写
- B. 清晰切割：把 daisy 定位为**纯粹的 prompt engineering 参考**，crpg 从技术栈 / 架构 / 数据层重新设计
- C. 真正的继承：只做 daisy v2 =**不加图像，只加三个 McKee 补丁 + 成人向定位 + 合规层**。这是 2-4 周能做完的版本

**我的推荐**：**C**。"daisy v2 只加 McKee 三补丁 + 成人向 + 合规"是一个**真正可继承的版本**，而且是 MVP。然后在这个 MVP 之上 iterate 图像。用户现在混淆了"继承 daisy"（便宜）和"做 daisy 没做的事"（极贵）。

---

### 矛盾 3：成人向定位 vs 模型供应链风险

**定义**：crpg 的成人向定位使其**整个产品命脉依附于 Grok 的 NSFW 政策**。

**证据**：
- 文字：OpenAI / Gemini / Claude 的 API ToS 在 2024-2025 年都收紧了 NSFW 条款（Anthropic 对 Claude API 成人内容的限制比 claude.ai 更宽但仍有限）。Grok 是目前**唯一**官方对 NSFW "less restrictive" 的主流文字 API。
- 图像：OpenAI DALL-E / Imagen / Midjourney / Flux Pro（通过官方）全部拒绝 NSFW。Grok Imagine 是目前**唯一**直连 API 可出成人内容的主流商业模型。
- 政策风险：xAI 在 2026-01~03 已经收紧了 Imagine 的订阅向 NSFW 限制（见用户 session state）。**任何一次政策收紧都可能让 crpg 一夜死亡**。

**Plan B 评估**：
- 自部署 SD + LoRA：图像可行但**单人做不了**（GPU 运维 + LoRA 训练 + 画像质量调教是 3-6 个月全职工作，且不能被 Grok 替代——前者是基于 2-3 年老架构的审美，后者是 2024-2025 的最新模型）
- 自部署文字：LLaMA 3 / Mistral Large / DeepSeek-R1 的 NSFW 能力都 OK，但**产品体验和 GPT-4 / Sonnet 差 1 档**。daisy 方法论建立在 Sonnet 4.6 的行为之上，换到开源模型需要重新调教 prompts。
- 通过 OpenRouter 做 fallback：理论可行，但 OpenRouter 对成人内容本身有政策约束，不是银弹

**严重程度**：⭐⭐⭐⭐⭐（致命，且不可控）

**选项**：
- A. 接受平台风险，all-in Grok，不做 Plan B（当前路径）
- B. 从一开始就用**抽象化 provider 层**，在代码里把"所有 LLM / image 调用"抽象成 interface，实际 Grok，但替换成 SD/LLaMA 只需改配置（工程成本：+15-20% 代码量）
- C. 定位**转向**偏 soft NSFW / 暗示向，不依赖露骨图像——这样 Gemini / Claude / DALL-E / Imagen 都可以候补，供应链风险降低

**我的推荐**：**B + 准备 C**。一定要做 provider abstraction（任何多模型项目的基础卫生），并**在产品层面给自己留"向 soft 侧折返"的空间**。"一定要露骨图像"不应该是**战略硬约束**，而应该是**可调的默认值**。如果哪天 Grok 关门，产品还能活在"暗示向成人艺术叙事"的位置。

---

### 矛盾 4：方法论深度 vs 产品兑现速度

**定义**：方法论产出速率是代码产出速率的 ∞ 倍（后者是 0）。

**证据**：
- 2026-04-17 一天内产出：
  - visual-dna-system.md（21 KB，10 层）
  - shot-design-system.md（27 KB，Hitchcock/Mamet/色戒拆解）
  - text-to-image-bug-taxonomy.md（15 KB，5 类 bug）
  - mckee-full-framework.md（16 KB，22 McKee 原理对照）
  - visual-aesthetic-axes.md（23 KB，24 子派 × 6 轴）
  - visual-aesthetics.yaml（66 KB，24 子派完整定义）
  - shot-types-vocabulary.yaml（24 KB）
  - detail-and-poetic-modes.md（14 KB）
  - design-rationale.md（24 KB）
  - pipeline-comparison.md（16 KB）
- R5 Shot 2 做了 **5 版仍然用户判定不满意**
- 代码产出：**0 行**（除了 generate.py 实验脚本）

**严重程度**：⭐⭐⭐⭐⭐（项目性质病变）

**深度诊断**：这是典型的**方法论过度生产（methodology overproduction）**症状。症状特征：
- 每次遇到 bug → 产出一份文档
- 每次有灵感 → 新增一个层
- 越研究越发现"还有新的层要加"，永无止境
- **用文档产出代替代码产出带来的掌控感**

这和学术研究、和咨询报告的生产模式一样。**产品开发不能这样工作**。产品开发的第一原则是 "ship early ship often"，每一次 ship 检验方法论是否有效。crpg 现在方法论和代码之间**没有任何反馈回路**——方法论只在图像测试这个孤立的 playground 里自我验证。

**选项**：
- A. 继续当前路径：预计 2 周后发现第 11/12/13 层要加，4 周后发现新的 Bug Class F/G/H，永远不 ship
- B. **Hard freeze 方法论**：把 Visual DNA 锁在第 8 层（R4 水平），Bug Taxonomy 锁在 A/B/C/E 四类（去掉 D，因为 D 本身"prompt 工程解决不了"用户也认了），转战代码
- C. 方法论和代码并行但有纪律：每产出 1 份方法论文档，必须同时产出 1 个相应代码 module，否则不允许写下一份文档

**我的推荐**：**B**。"Hard freeze" 的心理优势巨大：从"永远在发现新问题"变成"我已经知道足够多，现在是执行时间"。方法论在产品 v2/v3 时可以继续迭代，但 v1 必须锁死。

---

### 矛盾 5："方法论是护城河"的真实性评估

**定义**：用户和之前的 Claude 多次把 "Shot Director + Bug Taxonomy + Visual DNA" 描述成"核心护城河"。这个判断是否站得住？

**证据**：
- **同级别 AI 开发者**（例如 Replicate / fal.ai / 各种 AI video / comic generator 项目的 developer）在 1-2 周内可以从头复现 crpg 现有的 10 层 Visual DNA
  - Style Preamble = 公开知识（StudioBinder / YouTube 教程）
  - Aesthetic Axis = 公开知识（任何 e621/danbooru tag 用户都懂）
  - Character Sheets = 公开知识（Stable Diffusion 社区基础）
  - Direction Layer = 公开的摄影师 reference 术语
  - Anchor Strategy (image-to-image) = Grok API 文档就写了
  - Shot Design = McKee + 公开电影理论
  - Layered Garment = 消歧 prompt 是 SD 社区人人都会的技巧（"pose reference" / "detailed clothing"）
- **真正的护城河**应该是以下之一：
  - 专有数据（crpg 没有）
  - 专有模型 / LoRA（crpg 没有）
  - 网络效应（crpg 还没用户）
  - 品牌（crpg 还没上线）
  - 独占分销渠道（crpg 没有）
  - 某种**不公开的** know-how（crpg 的方法论文档**一旦产品上线 prompt 被抓包就不是 know-how 了**）

**严重程度**：⭐⭐⭐（中等，但心态影响大）

**残酷判断**：**crpg 的方法论不是护城河**。它是**良好的产品开发纪律 + 工程品味**。这很有价值（大多数 AI 内容产品做得糟糕的原因就是没有这个纪律），但它不是"别人复制不了"的壁垒。

**真正能成为 crpg 护城河的**（如果项目成功）：
- **创作者社区**（纯享版播放的故事是创作者提供的）—— 这是唯一真实的护城河
- **创作者工作流体验**（画布 + Genre 推断 + 美学轴选择的 UX 优势）
- **内容审核历史积累**（哪些 prompt 触发了合规问题、内部 blocklist）
- **审美品牌定位**（如果用户记住 crpg = "艺术感的成人叙事"，而不是 "Grok 的另一个套壳"）

**我的推荐**：**停止称方法论为"护城河"**。方法论是**入场券**（没有就做不出好产品）但不是**壁垒**。把"护城河"叙事转移到**创作者社区 + 审美品牌**上，这才是长期 defensible 的资产。

---

### 矛盾 6：纯享版免费 vs 创作者版付费的商业模型

**定义**：纯享版**零生成、零付费、完全静态、免费播放他人作品**是硬约束。创作者版 BYOK 或平台付费。

**证据**：
- 纯享版相当于 AO3 / Wattpad 的"读者模式"
- 创作者版相当于 Midjourney / Runway 的"付费工具"
- 但 crpg 的生成成本高：20 节点故事 × 3 shots 平均 × $0.07 = **$4.20 生成成本** + 文字 LLM 成本 ≈ **$5-8/故事**
- 纯享版免费意味着**创作者付了 $5-8 生成费用后，必须有足够多的读者消费 ta 的作品才能回本 / 回报**

**对比类似商业模型**：
- **AO3**：免费读 + 免费写 + 非营利 + 捐赠维持（不适合 crpg 因为 AO3 没生成成本）
- **Wattpad Originals**：免费读 + 作者分成模式（Wattpad 从广告收入分成，crpg 成人向不能跑广告）
- **Patreon / SubscribeStar**：创作者付费墙（crpg 纯享版不允许付费，违背硬约束）
- **Civitai**：免费 checkpoint + 生成器订阅（最接近，但 Civitai 是工具不是叙事平台）
- **NovelAI**：订阅制写作工具 + 生成器（不完全对应，但最接近 crpg 创作者版）

**商业模型的根本问题**：
- 创作者**付费生成 $5-8**，得到的是"发布到免费纯享版池"的权利
- 创作者的激励**只能是**：
  - 虚荣（有人读我的作品）
  - 自用（我为自己生成这个故事）
  - 创作共享主义（AO3 模型）
- **创作者不可能从作品收益**（因为读者端绝对不付费）
- 这限制了创作者群体的规模：**只有 hobbyist 创作者会加入**，不会有职业创作者

**严重程度**：⭐⭐⭐⭐（商业可持续性受限）

**选项**：
- A. 维持硬约束，接受 hobbyist-only 创作者（规模受限，平台成本全靠创作者付费订阅）
- B. **放松纯享版硬约束**：允许某些作品收费（类似 Wattpad Premium），或者允许"捐赠给创作者"
- C. 放弃创作者端付费，改为平台广告/订阅的免费模型（但成人向没法跑广告，订阅读者又违背免费硬约束）
- D. **改变定位**：纯享版不是"免费读他人作品"而是"订阅所有作品"（类似 NovelAI / 起点月票）

**我的推荐**：**A + 重新思考创作者激励**。hobbyist-only 是可以的，但必须降低创作者付费门槛——关键是 BYOK 选项要足够好：用户用自己的 Grok/Sonnet key，几乎零边际成本，crpg 只收 SaaS 订阅（$5-10/月让我用平台）。**BYOK 路径比平台付费路径更贴合 hobbyist 成人创作者社区的经济学**，因为他们本来就有自己的 key 做别的事。

**长期看**，要保留 D 路线（订阅制纯享版）作为 v3 级选项。"完全免费纯享版"是用户当前的理想主义约束，现实里如果 CDN + 存储 + 合规运维成本上来了，这个约束会被迫打破。

---

### 矛盾 7：文转图 Bug Class D 的根本难度

**定义**：Bug Class D（Default-Prior Override）是**目前 prompt 工程可能无法根治**的 bug class。Round 5 Shot 2 v1-v5 是活证据。

**我的独立视觉判断**（看了 R5 Shot 2 v5）：
- **几何上**是 thigh-high stockings（长筒丝袜）：top band 位置在大腿上段紧贴裙摆下缘，而不是膝盖上方（过膝袜的 band 位置）
- **审美上**像过膝袜：因为颜色过深（不够 sheer）、织物纹理不够透明、没有 skin-tone-showing-through 的质感
- **用户判定 "还是过膝袜"**：在"审美上像"的维度成立，在"几何上是"的维度不成立
- **这是更深的问题**：连人类审美判断都无法清晰界定"什么是正确"——说明 prompt 工程永远追不上用户的审美漂移

**根因分析**：
- **扩散模型的训练分布本身**有"深色密织长筒袜 = 过膝袜感"的强 prior
- Grok Imagine 用户画像偏"sexy pro photography"而非"Vogue editorial sheer hosiery editorial"
- **要根治 Class D 需要**：
  1. 自部署 SD 1.5 / SDXL / Flux dev
  2. 训练专用 LoRA（训练数据：Wolford / Falke / Fogal 品牌的 sheer hosiery 专业产品图 + 时装摄影）
  3. 对每一类 High-Prior 服装都这样做一个 LoRA（qipao / JK / lingerie / period-specific...）

**单人做这个的可行性**：
- GPU 租金：A100 40GB 每月 $800-1500（RunPod/Vast.ai）
- 训练数据整理：每个 LoRA 需要 80-300 张高质量标注图，约 1-2 周/LoRA
- 质量调优：每个 LoRA 可能需要 3-5 轮训练，每轮 4-8 小时
- **单人 6 个月能做 2-3 个 LoRA**（严重乐观估计）
- crpg 需要的 LoRA 数量：至少 **5-10 个**（stocking / qipao / lingerie / JK / 西式礼服 / 旗袍 / 军装 / period-victorian / ...）

**严重程度**：⭐⭐⭐⭐（图像质量的根本天花板）

**残酷结论**：**如果 crpg 的价值主张是"电影级精确的图像一致性"，那这个项目用当前技术栈（单人 + 商业 API）做不出来**。需要是：
- 自部署 + LoRA 训练（6-12 个月工程）
- 或者接受"图像质量达不到电影级精确，只追求'整体氛围和一致性'"

**选项**：
- A. 不在 MVP 里承诺"精确复刻"。改成"AI 自主视觉 + 风格一致"。**降低对 Class D 的期望**
- B. 承诺精确复刻，投资自部署 SD + LoRA 训练（延期 12+ 月）
- C. 将精确复刻交给"创作者半手动环节"——创作者可以上传 reference image，AI 尝试匹配，不强求完美（Claude 辅助 Photoshop 模式）

**我的推荐**：**A + C 混合**。MVP 的图像宣传降级为"AI 视觉助手，风格与氛围一致"，不宣传"电影级精确"。Class D 的问题不让它成为阻塞发布的 blocker——创作者可以选择哪些 shot 用 AI、哪些 shot 自己 Photoshop / 找真人模特拍摄 / 用其他工具补。crpg 的差异化不是"图像完美"而是"叙事 + 视觉同构工作流"。

---

### 矛盾 8：与现有成人 AI 内容产品的差异化

**定义**：市场上已经有多个成人 AI 内容方向的产品，crpg 差异化到底是什么？

**主要竞品分析**：

| 竞品 | 形态 | 强项 | 弱项 | crpg 差异化空间 |
|---|---|---|---|---|
| AI Dungeon | 文字互动叙事 | 开放世界 / 自由度高 | 无结构性叙事 / 图像差 / 付费墙 | crpg: McKee 结构性叙事 + 图像一致 |
| NovelAI | 文字 + 图像生成 | 用户基础 / 订阅 / 日系审美 | 二次元 only / 非游戏化 | crpg: 真实系审美 + 游戏结构 |
| Replicate NSFW SD | 工具层 | 灵活 / 开源 | 无叙事 / 无结构 | crpg: 工具上面套结构 |
| Literotica | 纯文字社区 | 巨大用户基础 / 免费 | 无图像 / 无互动 | crpg: 互动 + 图像 |
| AO3 成人同人 | 纯文字社区 | 创作者社区强 / 免费 | 无生成 / 无图像 | crpg: 生成 + 图像 |
| AVN 视觉小说引擎 | Ren'Py 等 | 成熟工具链 / 社区 | 纯手动 / 无 AI | crpg: AI 驱动减少手工 |
| 各种 AI 角色聊天 APP (Replika / Character.AI / Soulkyn / 等) | 角色对话 | 情感连接 / 订阅强 | 无叙事 / 无图像 | crpg: 完整叙事 |

**crpg 的**理论**差异化**："AI 驱动的结构化互动叙事 + 图像同构 + 画布编辑"

**现实中的问题**：
- McKee 结构性叙事 → 用户感知的提升是否值得付费？（daisy 的用户反馈说不清）
- 画布编辑 → 大多数用户可能不会用（reactive flow UI 学习曲线陡）
- 图像同构 → R4 水平已经能做到 "OK 级"，R5 之后的提升可能是专业审美才能区分的

**严重程度**：⭐⭐⭐（需要验证）

**选项**：
- A. 三位一体差异化（McKee + 图像 + 画布），全都保留 —— 复杂度高、传达困难
- B. 单点差异化：**只做"电影级结构性成人叙事"**，画布和图像降级为**支撑元素**
- C. 反向定位：不和 AI Dungeon / NovelAI 竞争，而是和 Ren'Py 视觉小说社区竞争——定位为"AI 视觉小说引擎"

**我的推荐**：**B 或 C**。单点传达比三位一体容易。**如果我是 crpg**，会选 B：传播语句是 **"McKee 级结构化成人互动叙事，带配套视觉"**。画布和图像都是**体验的一部分**，但广告语不提。

---

### 矛盾 9：导演 LLM 和 Visual DNA 的工程负债

**定义**：产品化的 3-pass LLM pipeline + Shot Director 自动化 VDNA 组装 + 动态 shot budget + 按节点 quota 控制，工程量远超 daisy。

**证据**：
- daisy pipeline：1 个 LLM 调用（Sonnet）+ 1 个前端 + 1 个 SQLite
- crpg pipeline：3 个 LLM 调用（P1/P2/P3）+ 1 个 Prompt Assembler（pure）+ 1 个 Image Batch Worker + 2 个前端（纯享版 + 创作者版）+ CDN + 账单层 + 合规层 + 发布流
- **按 LOC 估算**：crpg ≈ daisy × 8-10 倍

**具体 Shot Director LLM 的工程负债**：
- 需要完整的 Bug Taxonomy 内置到 system prompt
- 需要实现 "High-Prior Garment 识别 → 强制启用 Layered Grammar"
- 需要 per-shot "adversarial check"（模拟模型最可能的误读并增加硬否定）
- 需要动态 shot budget（0-N 由 Director 自决）
- 需要 Character 隔离（不把 off-frame character 的 signature 注入 prompt）
- 需要 Emotion Weight 打分 → 选 Cover Shot
- 每个子模块都可能需要 1-2 周的打磨

**严重程度**：⭐⭐⭐⭐（严重拖累交付）

**选项**：
- A. 按当前计划建完整 Shot Director（预估 4-8 周全职）
- B. 先做 "dumb Director"：每个节点固定 1-3 张图，Prompt Assembler 拼 Visual DNA 模板，**没有 LLM pass**。等 v2 再引入 Director LLM 智能
- C. 完全跳过 Shot Director：创作者**手动**在画布上标记"这个节点要几张图"，AI 只负责生成

**我的推荐**：**B + C 混合**。v1 用 B：**固定每个节点生成 1 张 cover shot**（最简），不做 shot list、不做动态 budget、不做 Director LLM。创作者可以**手动**在某个节点点 "add more shots" 来触发追加生成。**这能把图像工程缩减 80% 并让 MVP 能 ship**。Shot Director LLM 是 v2/v3 的野心，现在放它是在扼杀 MVP。

---

### 矛盾 10："先方法论后实施"的路径选择

**定义**：当前状态是 brainstorming 阶段充分积累，正式 spec / 实施**为零**。

**证据**：
- brainstorming 分支：88 个文件，300KB 文档
- main 分支：空 baseline
- 代码产出：0 行（除 Python 实验脚本）
- 方法论 iteration 速度：每天 1-2 份新文档

**daisy 原作者对比**：**48 小时做出文字 MVP**。

**严重程度**：⭐⭐⭐⭐⭐（根本路径错误）

**诊断**：用户当前路径是 **"think deep first, then build"**。这在学术研究 / 政府规划 / 大企业战略里是正确的。在独立开发者做产品里是**致命错误**。

**独立开发者产品开发的核心节律**应该是：
```
Day 1: ship something ugly
Day 2-7: use it yourself, find 3 worst things
Day 8-14: fix those 3 things
Day 15: invite 3 friends to try
Day 16-30: fix what they complain about
Day 31: decide if this is worth continuing
```

crpg 现在在 Day 2 用了 40% 的精力在 brainstorm。这是 10x 的精力错配。

**辩护方**：crpg 确实有 daisy 没有的复杂度（成人向合规 / 双模式 / 图像 / 双模型）。这些"先想清楚"有道理。

**反驳**：
- 合规：照抄 Literotica / AO3 / Patreon 的合规条款 + 18+ 门 + GeoIP（2 天搞定）
- 双模式：**先不做**，只做创作者版自用
- 图像：**先不做**或只做 R4 水平 cover shot
- 双模型：**先只用 Sonnet**（daisy 已验证），Grok 推到 v2

**选项**：
- A. 当前路径，再做 2-4 周 brainstorming 到"全面设计完"，然后开始编码（预计 ship 到 2026-09）
- B. **Hard stop brainstorming**，14 天内 ship 文字 MVP，图像推到 v2
- C. 双线并行：一边写 code MVP 一边补 spec（容易两头不到岸）

**我的推荐**：**B，强烈**。硬停 brainstorming。接下来 14 天只做代码。v1 发布后再补充方法论。

---

## 3. 方法论真实水平评估（独立分级）

### 真金 ⭐⭐⭐⭐⭐（保留，核心资产）

| 方法论 | 为什么是真金 | 如何保留 |
|---|---|---|
| **daisy 原六条硬约束**（Value Shift, Complication, Dilemma, Gap, Controlling Idea, Three Levels） | daisy 48 小时产出文字质量的根因，McKee 叙事理论的工程化转译 | prompts.ts 逐字保留到 crpg |
| **两步生成（skeleton → content）** | McKee step outline 方法的天然工程映射，daisy 的杀手锏 | 保留 |
| **诗意模式 / 细节等级** | 文字质感的调控维度，daisy 原作 + 用户微调温度 0.8 | 保留 |
| **Shot Design 色戒拆解方法论** | Hitchcock's Rule + Murch Rule of Six + Mamet Uninflected + 李安 fragment 综合，这是罕见的高质量综合 | 固化为 Shot Director system prompt 候选 |
| **McKee 三补丁（Genre / Antagonism / Climax）** | 补入 daisy 漏的最重要三条 | 保留并加入 prompts |
| **Direction Layer（candid / photographer tether / micro-tell）** | R2→R3 从 stock photo 到 candid 的视觉跃迁是实证的 | 保留 |

### 中等价值 ⭐⭐⭐（有用，不是壁垒）

| 方法论 | 水分在哪 |
|---|---|
| **Visual DNA 7 层** | 其中 4-5 层是真正独立的（Style Preamble / Character Sheets / Positive Framing / Technical Lock），剩下 2-3 层是其他层的自然副产品或 trivia。可合并为 5 层。 |
| **24 视觉美学子派分类** | 分类粒度过细，hobbyist 创作者用不到 24 类。典型用户会用 3-5 类。简化为 "主流审美光谱"（日系写实 / 欧美写实 / 二次元 / 复古 / 极简）就够。 |
| **Bug Taxonomy A/B/C/E** | 有实证，是 good practice，但任何同级开发者碰到一次就能自己总结出。 |

### 水分 ⭐（产品 MVP 不需要，v2/v3 可选）

| 方法论 | 为什么是水分 |
|---|---|
| **Visual DNA 第 9 层 Shot Design Layer + 第 10 层 Layered Garment** | 方法论本身是真的，但**落实到产品化需要自部署 SD + LoRA**。用商业 Grok API，第 10 层的效果**无法验证为稳定可复现**（见 R5 Shot 2 证据）。在 v1 不值得投资。 |
| **Bug Class D 的 Layered Visibility Rule** | 上面同理。只有一个服装类（stocking）做了完整推演，泛化性未验证。 |
| **动态 Shot Budget / Shot Director LLM** | v1 的 MVP "每节点固定 1 张 cover shot" 就够了。动态 budget 是 v2 的事。 |
| **Temporal DNA / Video DNA** | 视频储备纯粹是未来野心，写进方法论是自我消耗。 |
| **等价温度表（Claude 0.8 ≈ GPT-5 1.0 ≈ Gemini top_p 0.92）** | v1 只用一个文字模型（推荐 Sonnet）就够了。多模型路由是 v2 的事。 |

---

## 4. 工程可行性评估（单人 6 / 12 个月真实产能）

### 如果全力投入 crpg 当前 scope，单人时间估算

| 组件 | 乐观 | 现实 | 悲观 |
|---|---|---|---|
| 文字生成（daisy 代码 + McKee 三补丁 + 前端适配）| 3 周 | 5 周 | 8 周 |
| 18+ 门 + GeoIP + 基础合规 | 1 周 | 2 周 | 3 周 |
| 图像 pipeline（Grok Imagine + Visual DNA 静态模板 + 1 张 cover shot per node）| 2 周 | 4 周 | 7 周 |
| Shot Director LLM 完整版 + 动态 budget | 4 周 | 8 周 | 16 周 |
| 双模式前端（纯享版静态 + 创作者版画布）| 6 周 | 12 周 | 20 周 |
| 双模型路由 + 等价温度表 | 2 周 | 3 周 | 5 周 |
| 发布流（创作者 → 纯享版）| 2 周 | 4 周 | 7 周 |
| 账单 / BYOK 层 | 2 周 | 4 周 | 7 周 |
| 审计 / 审核链 | 1 周 | 3 周 | 5 周 |
| 部署 / CDN / 运维 | 1 周 | 3 周 | 5 周 |
| Bug 修复 / 反馈迭代 / UX 打磨 | 3 周 | 6 周 | 12 周 |
| **合计** | **27 周 (6.3 月)** | **54 周 (12.5 月)** | **95 周 (22 月)** |

**诊断**：
- 6 个月版本 = **乐观 + 多项妥协**。更现实是 **12 个月**。
- 如果用户中途有分心（正常生活 / 其他项目 / 心态波动），**乘以 1.5-2**，到 18-24 个月。
- 成人向定位的项目通常**找外部协作者更难**（合规顾虑、家人朋友顾虑），所以"招合伙人"不太现实。

### 如果采用 MVP 砍 scope 版本

- 文字 + McKee 三补丁 + 18+ 门 + 简易前端 + BYOK + 基础合规 = **4-8 周**
- 然后根据用户反馈决定加什么

---

## 5. 三条可能路线 + 我的推荐

### 路线 A：维持当前 scope，All-in 做 12-18 个月

**内容**：按当前 brainstorming 结果做完整产品。6-18 个月后上线。

**风险**：
- 做不完（单人 12 个月 scope 几乎一定会滑）
- Grok 政策变（2026 内有概率收紧）
- 用户兴趣消耗（做 12 个月没反馈的项目心态极难维持）
- 市场变（2027 的成人 AI 赛道可能已经洗牌）

**收益**：
- 如果做完，差异化最强，方法论最深
- 融资 / 出售故事最完整

**胜率**：**10-20%**（独立开发者做 12 个月项目的 base rate）

---

### 路线 B：MVP 版本，文字优先 / 图像简化 / 双模式砍掉

**内容**：
- 4-8 周 ship 一个**只有创作者版 + 文字 + 可选图像（R4 水平静态模板）**的 MVP
- 没有 Shot Director LLM，没有动态 budget，图像用固定 1 张 cover shot
- 没有纯享版（v2 再做）
- 只支持 BYOK（v2 再做平台付费）
- McKee 三补丁 + 18+ 门 + GeoIP + SQLite 本地部署
- 2026-06 前上线

**风险**：
- 差异化不够强（和 daisy 差距不大）
- 图像质量 MVP 级，高级用户会失望
- 放弃了"完整愿景" narrative

**收益**：
- ship 了，拿到真实反馈
- 基于反馈决定 v2 投资方向（纯享版？更好图像？Shot Director？）
- 方法论不浪费（保留在文档里，未来迭代的起点）

**胜率**：**40-60%**

---

### 路线 C：图像砍掉，纯文字成人叙事（真正的 daisy v2）

**内容**：
- 4 周 ship daisy + 成人向改造 + McKee 三补丁 + 合规层
- **完全不做图像**
- 产品定位 = "McKee 级结构化成人互动叙事"
- 类比：AI Dungeon 的结构化版，或 Literotica 的生成版

**风险**：
- 图像差异化放弃 = 和竞品差距变小
- 用户可能觉得"没有图很无聊"

**收益**：
- 最快 ship，最快学到市场反馈
- 方法论资产（Visual DNA / Shot Design）**保留**，v2 再用
- 聚焦文字方法论的真正护城河（daisy 的 prompts 质量）

**胜率**：**60-70%**

---

### 路线 X（我的推荐）：**砍一半，锁一半**

路线 B 和 C 的混合，但有严格的纪律：

**第一阶段：14 天文字 MVP**（绝对优先）
- Day 1-3：把 daisy 代码搬过来 + 改 temperature 到 0.8 + 加 18+ 门 + 加 McKee 三补丁（Genre/Antagonism/Climax）
- Day 4-7：加最简的多用户账号 + SQLite + 部署
- Day 8-10：加 BYOK（创作者输入 OpenRouter/xAI key）
- Day 11-14：Polish + 发给 3-5 个信得过的朋友试玩

**第二阶段：图像降级注入**（21 天）
- Day 15-21：R4 水平的图像 pipeline（Visual DNA 1-8 层）**作为可选特性**注入到创作者版
- 每个节点固定 1 张 cover shot，创作者可以 regenerate
- **不做 Shot Director LLM**
- **不做 Layer 10（Layered Garment）**
- Day 22-28：测试图像 pipeline + 收反馈
- Day 29-35：Polish + 内部发布

**第三阶段：纯享版发布机制**（21 天）
- Day 36-42：纯享版前端（静态 SSG）
- Day 43-49：创作者发布流（简化：创作者在画布里点 "publish"，故事导出为 JSON + 图片打包到 CDN）
- Day 50-56：Polish + 公开 soft launch

**总计：56 天 = 8 周 = 2 个月公开 soft launch**

**然后再根据反馈决定**：
- v2：要不要做 Shot Director？要不要 Layer 10？要不要双模型？
- v3：要不要视频？要不要 Temporal DNA？

**为什么比 A/B/C 好**：
- 比 A 快 4-6 倍，风险降低 3-5 倍
- 比 B 有更明确的阶段门控（第二、第三阶段必须先完成第一阶段才启动）
- 比 C 保留了图像差异化，但不把它作为核心

**胜率**：**50-65%**（**阶段门控**是关键 —— 如果第一阶段 14 天没 ship，说明 scope 还是太大，必须再砍）

---

## 6. 如果是我做这个项目，明天开始做什么（周粒度）

### Week 1（2026-04-17 至 2026-04-23）：**砍 + 锁 + 动手**

**Day 1（明天 2026-04-18）**：
- 写一份 **DECISIONS-2026-04-18.md**，冷冻下列事项为 "v1 不做"：
  - 双模型路由
  - Shot Director LLM
  - Layer 9 Shot Design Layer
  - Layer 10 Layered Garment
  - 动态 shot budget
  - 纯享版前端
  - 平台付费路径（只做 BYOK）
  - 双模式架构
- 在 `main` 分支创建 `v1-scope.md`，明确写 v1 只包含什么
- 把所有方法论文档**移动到 `assets/research-archive/`**（让它们不再挡视线）

**Day 2-3**：
- 初始化 crpg 代码仓库（不是 daisy 的继承，是全新）
- 技术栈最保守选择：Next.js + SQLite + Hono + BetterAuth
- 把 daisy 的 prompts-v6.ts **作为 .ts 文件 import**，加 McKee 三补丁
- 配置 OpenRouter（用户用自己的 key）

**Day 4-5**：
- 最简的故事生成页面：关键词输入 → 调 Sonnet → 返回 JSON → 静态渲染
- 没有画布、没有图像、没有登录
- 这版的目标是 **自己用**

**Day 6-7**：
- 加 18+ 门（页面 modal + cookie）
- 加 GeoIP 封锁（Vercel Geo header 就行）
- 试玩 3 次自己生成的故事

### Week 2（2026-04-24 至 2026-04-30）：**用起来 + 加 BYOK + 简单多用户**

- 加用户登录（BetterAuth，email/password 即可）
- 加 BYOK 界面（用户输入 xAI 或 OpenRouter key，存到 db 加密）
- 加最简的故事列表页（用户自己生成的，不分享）
- 发给 3 个朋友试玩，收反馈
- **Milestone**：**Day 14 必须有人用过**。如果没有，说明路线 X 第一阶段也太大，需要再砍。

### Week 3（2026-05-01 至 2026-05-07）：**反馈分析 + 决定 v1.1**

- 根据 Week 2 反馈，分类 3 大类问题（内容质量 / UX / 功能缺失）
- 决定：这些问题用 v1.1 修（不加新 scope），还是 v1.0 就够了可以扩
- 如果决定扩，下一轮只扩一个东西（比如"加画布编辑"或"加图像"，二选一）

### Week 4（2026-05-08 至 2026-05-14）：**单一扩展**

- 做上一周决定扩的那一件事（画布**或**图像）
- 用 R4 水平的图像 pipeline（VDNA 1-8 层，手工模板，无 Director）
- 或用 daisy 原画布代码（react-flow）稍微改

### Week 5-8（2026-05-15 至 2026-06-11）：**两件事二选一 + 纯享版发布流**

- 上面没选的那件事做了
- 加纯享版发布流：创作者点 publish → 生成静态 JSON → 上传 CDN → 公开 URL
- 6 月前公开 soft launch

### Week 9+ ：根据反馈决定方向

- 如果有用户，加 Shot Director / 双模型 / Layer 9 / Layer 10
- 如果没用户，反思为什么——很可能是定位 / 分发问题，不是方法论深度问题

---

## 7. 最后的话

用户的**核心战略直觉是对的**：
> "我觉得值得保留的就是方法论，其他的我觉得就很乱了"

但**结论需要修正**：

- **不是因为方法论是护城河所以值得保留** —— 方法论是入场券不是护城河
- **是因为方法论是积累的 asset 可以在 v2 / v3 使用** —— 现在锁起来
- **是因为除了方法论，其他都是过早优化** —— 所有"产品化"的讨论（Shot Director / 动态 budget / 双模式发布流 / 等价温度表 / 成本分摊）都是**在没有用户的时候讨论如何服务用户**

**独立开发者的唯一战略是**：**先有用户，再谈架构**。crpg 现在是"没有一行产品代码的时候在讨论 Layer 10"，这是战略错位。

**如果用户只能做一件事**：**14 天内 ship 一个有朋友在用的文字 MVP**。其他一切，v2 再说。

---

## 附录 A：用户的原话与我的翻译

| 用户原话 | 我的翻译 |
|---|---|
| "我和 daisy 原来的想法就是做一个关键词或者一段话生成游戏的" | 核心愿景是 "关键词 → 游戏"，这很清晰 |
| "她已经做成了生成文字的" | daisy 已经是你愿景的 70% 实现，你应该基于它 |
| "我现在弄了半天加图片的" | 你把"加图片"搞成了"全面重设计" |
| "图片的效果也一直不好" | 图像确实很难，你应该降级期望 |
| "过膝袜也没做好" | 这是证据不是投诉 —— 证明 Class D bug 不好解 |
| "两个模型的架构，已经这个导演 llm 怎么设计，镜头的一致性" | 这些都是过早优化 |
| "我觉得值得保留的就是方法论" | **对** |
| "其他的我觉得就很乱了" | **因为 scope 太大** —— 砍 scope，"乱"会消失 |

---

## 附录 B：R5 Shot 2 v5 的独立视觉判断（截图证据）

我看了 `research/grok-image-test/round5/shot-2-ecu-insert-toenails-v5.png`。**独立判断**：

**几何判断**：是 thigh-high stockings（长筒丝袜）。
- Band 位置在大腿上段，紧贴裙摆下缘
- 两腿间能看到大腿肉色和 band 的对比
- Band 下方是整条腿的袜体
- **这不是过膝袜**：过膝袜的 band 在膝盖上方 5-10cm，会有很明显的大腿裸露段

**审美判断**：**但是显得像过膝袜感**。
- 袜体颜色过深（接近 opaque black）
- 不够 sheer（应该能透出 skin tone）
- 织物质感偏厚重，接近运动袜或足球袜
- 缺少 stocking seam 的 backline（虽然前缀写了）

**结论**：
- 用户"还是过膝袜"的判断**在审美层面对**（vibe 不对）
- 但在**几何层面错**（结构上已经是 thigh-high）
- **这说明连人类审美都难以清晰界定"正确" —— prompt 工程永远追不上**
- **这证实了矛盾 7 的诊断**：Class D 需要 SD + LoRA，不是 prompt 可根治的

---

## 附录 C：R1 → R4 的真实视觉跃迁（截图证据）

- **R1 Scene 1**: 白人/南欧女主角坐在 cafe 式房间，静态正面。Identity Drift + Setting Drift 明显。
- **R2 Scene 1**: 东亚脸了，背景有"夜宵面馆"中文霓虹，审讯室元素到位。一致性大幅改善。但两人都面朝镜头。
- **R4 Scene 1**: 东亚脸 + 审讯室中文招牌"审讯室" + OTS 对角构图 + Direction Layer 的 candid 感。视觉上已达到"能作为成人叙事产品的 cover shot"级别。**但**女主角嘴里叼烟（Meijie 的 signature 串场）—— Class E bug 清晰暴露。

**核心结论**：R4 水平**已经足够作为 MVP 级图像输出**。R5 的"完美主义"追求虽然方法论深刻，但工程边际收益骤降。R5 之后再优化，时机不对。

---

**审查完成时间**: 2026-04-17
**下一步**: 用户决定接受路线 X，立即进入 Week 1 Day 1 的决策冷冻动作
