# crpg 竞争格局分析报告
**生成日期**：2026-04-17
**分析师角色**：竞品分析师（与内部架构审查 agent 并行）
**研究方法**：WebSearch + WebFetch，2026 年关键词检索，交叉验证

---

## 1. TL;DR — 市场全貌（3 段话）

**市场现状**：AI 互动叙事 + 成人内容市场在 2026 年已高度碎片化。文字角色扮演（Character.AI：20M MAU、CrushOn.AI：28M 月访问）、成人图像生成（SoulGen 估计 $420M 营收、Civitai 3.2M 用户）、AI 陪伴（Candy.ai：$25M ARR、11.6M 月访问、Replika：$25M 营收）各自形成了独立的用户池，且几乎没有重叠。没有单一平台真正做到了"高质量分支叙事 + 成人内容 + 配套图像 + 创作者 UGC 发布 + 免费阅读端"的完整闭环。

**主要断层**：最接近 crpg 定位的是 NovelAI（文字 + 图像，但图像仅 anime 风，分支弱）和 FictionLab（分支叙事，但无图像）。DeepFiction Studio 在 2025 年开始做文 + 图 + 视频的集成，是当前最直接的技术路线竞品，但无创作者 UGC 发布机制、无免费阅读端、叙事质量较弱。市场上最大的空位是：**电影级叙事质量 + 成人显式内容 + 每节点多帧图像 + 创作者发布 + 免费读者端**——这个五维组合确实没有单个产品覆盖。

**风险与机会**：最大风险来自支付处理合规压力（Visa/Mastercard 在 2025 年封锁了 Civitai，业界普遍向加密货币迁移）和 xAI Grok Imagine 在 2026 年 3 月收紧政策（免费图像生成已下线，SuperGrok $30/月 才能访问）。这直接影响 crpg 的后端成本结构。机会在于：AI Dungeon 流量已跌 60%，Character.AI 收紧了 18+ 内容，这释放了大量寻找替代品的用户。

---

## 2. 六类竞品分组总表

| # | 名称 | 类别 | 内容尺度 | 付费模式 | 用户规模（估计） | 与 crpg 重叠度 | 威胁等级 |
|---|------|------|----------|----------|----------------|--------------|--------|
| 1 | AI Dungeon | A 文字互动叙事 | SFW + 有限 NSFW | 免费 + $9.99-$49.99/月 | 38K WAU（2024），月访问大幅下滑 | 高（直接竞品） | 中（已衰退） |
| 2 | NovelAI | A 文字互动叙事 | Hardcore（无审查） | $10-$25/月 | 约 300K 订阅（估计） | 极高（最近似） | 高 |
| 3 | Sudowrite | A 文字互动叙事 | SFW（不含成人） | $10-$59/月 | 300K+ 用户 | 低（工具向，非成人） | 低 |
| 4 | Dreamily | A 文字互动叙事 | Soft NSFW（浪漫向） | 免费 + $4.99/月 | 未公开 | 中（移动优先，轻度） | 低 |
| 5 | NovelCrafter | A 文字互动叙事 | 依赖 BYOK 模型 | $4-$20/月（BYOK 自付 token） | 小众（创作者工具） | 中（创作者侧） | 低 |
| 6 | FictionLab | A 文字互动叙事 | Hardcore（无审查） | 免费 + $7.99/月 | 较小 | 高（分支叙事+成人） | 中 |
| 7 | DreamGen | A 文字互动叙事 | Hardcore | $6.26-$33.81/月 | 未公开，100K+ 场景 | 高 | 中 |
| 8 | Character.AI | C AI 角色陪伴 | SFW（已大幅收紧） | $9.99/月 | 20M MAU，$50M 营收 | 低（成人向被封） | 低 |
| 9 | CrushOn.AI | C AI 角色陪伴 | Hardcore（明确 NSFW） | $4.99-$50/月 | 28M 月访问（2026/2） | 高（成人向+剧情） | 高 |
| 10 | SpicyChat | C AI 角色陪伴 | Hardcore | $5-$24.95/月 | 2M 注册用户 | 高 | 中 |
| 11 | Candy.ai | C AI 角色陪伴 | Hardcore（NSFW + 图像） | $5.99-$12.99/月 | 11.6M 月访问，$25M ARR | 中（陪伴为主，弱叙事） | 中 |
| 12 | Replika | C AI 角色陪伴 | Soft NSFW（亲密但非显式） | $19.99/月 | 30M 注册，$25M 营收 | 低（情感陪伴，无叙事） | 低 |
| 13 | Muah.ai | C AI 角色陪伴 | Hardcore | $9.99-$99.99/月 | 未公开 | 中 | 低 |
| 14 | NovelAI 图像 | B 成人图像生成 | Hardcore（anime） | Anlas 按量（随订阅送） | 同上 NovelAI | 高（图像后端） | 高 |
| 15 | SoulGen | B 成人图像生成 | Hardcore | 未公开 | $420M 营收（估计，存疑） | 中（图像后端） | 中 |
| 16 | Civitai | B 成人图像生成 | Hardcore（UGC 模型） | $10-$50/月（现转加密货币） | 3.2M 用户，23M 月访问（2024） | 低（工具/模型市场） | 低 |
| 17 | Tensor Art | B 成人图像生成 | Hardcore（anime/hentai） | $5-$20/月 | 6M 月访问 | 低（独立图像工具） | 低 |
| 18 | Seduced.AI | B 成人图像生成 | Hardcore | $10-$150/月 | 高流量（估计），无公开数据 | 低（纯图像，无叙事） | 低 |
| 19 | Unstable Diffusion | B 成人图像生成 | Hardcore | $14.99-$59.99/月 | 500K 图/天，400K Discord 成员 | 低（纯图像） | 低 |
| 20 | DeepFiction Studio | F 新兴 AI 原生 | Hardcore（"Lustix"功能） | $5-$75/月 | 未公开 | 极高（文+图+视频集成） | 高（最直接） |
| 21 | RedQuill | F 新兴 AI 原生 | Hardcore | $12.69-$26.69/月 | 10M+ 故事，15K+ 角色 | 高（成人故事+社区） | 中 |
| 22 | Fanvue | E 内容平台/订阅 | Hardcore（AI 创作者主导） | 创作者端 15% 抽成，读者付费 | 17M MAU，$100M ARR | 中（订阅模式，非游戏叙事） | 中 |
| 23 | Literotica | E 传统成人文字平台 | Hardcore（无图像） | 免费（有广告） | 50M 月访问 | 中（读者端竞品） | 低 |
| 24 | AO3 | E 传统成人文字平台 | Hardcore（fan fiction） | 完全免费 | 17.2M 作品，超 5M 评论（2025） | 低（粉丝向，非互动游戏） | 低 |
| 25 | miku.gg | F 新兴 AI 原生 | Soft NSFW（可启用 NSFW 情绪） | 未公开 | 小型社区 | 中（视觉小说+角色+分支） | 低 |
| 26 | Endless Visual Novel | D 互动小说工具 | 未明确（无说明） | 免费 + €9/月 + €15/月 | 小型 | 中（视觉小说+创作者） | 低 |
| 27 | Ren'Py/Twine/Ink | D 传统工具 | 工具本身无限制 | 免费开源 | 大量（Ren'Py 是 VN 标准） | 低（工具层，非平台） | 低（工具参考价值高） |
| 28 | Talefy | F 新兴 AI 原生 | SFW（移动端家庭向） | $1.99 起 | Beta 阶段 | 低（无成人） | 低 |
| 29 | FableAI | A 文字互动叙事 | Soft（RPG+图像，无显式成人） | 免费 + 订阅 | 100K 用户 | 中（文字+图像 RPG） | 低 |
| 30 | Wattpad | E 传统文字平台 | Soft（无显式成人） | 免费 + $5.99/月 | 80M+ 用户 | 低（大众向，有读者端） | 低 |

---

## 3. 竞品卡片（按九维度，按类分组）

### A 类：AI 文字互动叙事

---

**A1. AI Dungeon（Latitude）**

- **产品形态**：文字 RPG + 无限生成分支叙事，基于 prompt 续写，轻量 UGC（创作世界并分享）
- **内容尺度**：历史上允许成人，2021 年内容过滤争议，2025 年因青少年关联死亡诉讼后大幅收紧，成人内容现已受限，NSFW toggle 存在但实质过滤严格
- **付费模式**：免费（Wanderer 免费基础模型）+ 订阅 $9.99-$49.99/月（Dragon 模型、更快速度）
- **用户规模**：峰值后大幅衰退。2024 年 Q1 WAU 约 38K，月访问跌超 60%，2024 年 3 月下架 Steam
- **技术堆栈**：GPT 系列（OpenAI API）+ 自研 Dragon 模型；前端 React；无图像
- **UGC 机制**：用户可创建并分享"世界"，但叙事连续性差，无固定分支结构
- **crpg 重叠度**：直接竞品（文字互动叙事），但已严重衰退
- **威胁等级**：中（品牌有历史，但失去成人用户基础）
- **差异化弱点**：叙事质量差（无 McKee 框架）、无图像、成人政策反复、平台用户流失

---

**A2. NovelAI（Anlatan）**

- **产品形态**：文字创作 + anime 图像生成，双引擎（Erato 70B 文字 + Anime V4 图像），支持互动小说但非分支游戏形态
- **内容尺度**：Hardcore。Erato 模型明确"无审查"，图像可生成显式 anime 内容，隐私优先（故事加密，不记录 prompt）
- **付费模式**：订阅制，Tablet $10/月 / Scroll $15/月 / Opus $25/月；图像用 Anlas 点数（随订阅赠送）
- **用户规模**：估计约 300K 订阅用户（未官方公开），全球排名约 6,664，月访问量中等规模（约 500K-1M 估计）
- **技术堆栈**：自研 Llama 3 70B 微调（Erato）+ 自研 Anime Diffusion V4；完全私有基础设施
- **UGC 机制**：无公开发布/分享机制，重度工具向，读者无法免费浏览他人作品
- **crpg 重叠度**：极高（文字+图像+成人，最近似 crpg 的现有产品）
- **威胁等级**：高（核心能力重叠最多）
- **差异化弱点**：图像局限 anime 风格（无写实向）；文字与图像两个引擎体验割裂，缺乏电影镜头语言；无分支游戏结构；无 UGC 发布平台

---

**A3. Sudowrite**

- **产品形态**：纯文字写作辅助工具，面向严肃小说作者，Muse 1.5 自研小说专用 LLM
- **内容尺度**：SFW（拒绝成人内容，用于文学创作）
- **付费模式**：$10-$59/月（年付折扣 45-50%）
- **用户规模**：300K+ 用户，主要为自助出版作者和专业作家
- **crpg 重叠度**：低（非成人，工具向非游戏平台）
- **威胁等级**：低
- **差异化弱点**：无互动/游戏化；无成人内容；无图像

---

**A4. Dreamily**

- **产品形态**：移动端 AI 故事生成 app，浪漫向，角色互动，轻度 UGC
- **内容尺度**：Soft NSFW（浪漫、爱情，有语音通话角色）
- **付费模式**：免费 + $4.99/月 Gold（100K 词/月）
- **用户规模**：iOS/Android，具体 MAU 未公开，用户群较轻度
- **crpg 重叠度**：中（轻叙事+角色，但无显式成人，无图像）
- **威胁等级**：低
- **差异化弱点**：无显式成人；无分支结构；无图像；移动端体验轻量

---

**A5. NovelCrafter**

- **产品形态**：长篇小说写作工具，有 Codex 世界构建系统，BYOK 接入多种模型
- **内容尺度**：依赖用户选择的 BYOK 模型（有专门的 NSFW models 文档）
- **付费模式**：$4-$20/月（仅平台费，AI token 自付）
- **用户规模**：创作者小众，无公开数据
- **crpg 重叠度**：中（创作者工具侧参照）
- **威胁等级**：低
- **差异化弱点**：无游戏/互动化；无读者端；无图像；重度工具

---

**A6. FictionLab**

- **产品形态**：协作分支叙事平台，角色卡系统，用户驱动分支（"Branch From Here"功能）
- **内容尺度**：Hardcore（无审查，支持露骨叙事和恐怖）
- **付费模式**：免费（无消息限制）+ FictionLab+ $7.99/月（解锁更快模型）
- **用户规模**：2024 年上线，规模较小，用户以成人叙事爱好者为主
- **crpg 重叠度**：高（分支叙事+成人，但无图像、无 UGC 发布平台）
- **威胁等级**：中
- **差异化弱点**：无图像；无 UGC 发布/浏览机制；叙事质量未系统化（无叙事框架）

---

**A7. DreamGen**

- **产品形态**：叙事优先的角色扮演平台，长上下文（30K tokens），多角色同时互动
- **内容尺度**：Hardcore（允许私人 18+ 内容，禁止 CSAM 和非自愿深度伪造）
- **付费模式**：$6.26-$33.81/月（按上下文和 token 配额区分）
- **用户规模**：100K+ 场景库，具体 MAU 未公开
- **crpg 重叠度**：高（叙事+成人，但无图像）
- **威胁等级**：中
- **差异化弱点**：无图像；无分支游戏结构（线性 chat 向）；无 UGC 发布平台

---

### B 类：AI 成人图像生成

---

**B1. NovelAI 图像（Anlatan）**

- **产品形态**：anime 风格图像生成器，与文字引擎集成，支持 vibe transfer（风格迁移）
- **内容尺度**：Hardcore（anime 显式内容合法合规）
- **付费模式**：Anlas 点数制，随订阅赠送（$10-$25/月），无 seed 控制但有较强风格一致性
- **技术堆栈**：自研 Anime V4 扩散模型，1024×1024 分辨率
- **crpg 重叠度**：高（图像后端，但 anime 风格限制了写实成人叙事场景）
- **威胁等级**：高（同时做文字+图像的最成熟竞品）

---

**B2. Civitai**

- **产品形态**：开源 SD 模型市场 + 云端生成平台，3.2M 用户，大量 UGC 成人 LoRA 模型
- **内容尺度**：Hardcore（UGC NSFW，包含写实向）
- **付费模式**：Buzz 虚拟货币制，$10-$50/月会员（2025 年 5 月 Visa/Mastercard 封锁后转加密货币）
- **用户规模**：23M 月访问（2024），3.2M 用户
- **crpg 重叠度**：低（工具/模型市场，非叙事平台），但关键参考：Civitai 解决了 crpg 需要解决的支付合规问题
- **威胁等级**：低（非直接竞品，但展示了支付合规风险）
- **差异化弱点**：无叙事引擎；支付合规危机（加密货币方案对普通用户摩擦大）

---

**B3. Tensor Art**

- **产品形态**：SD 云端生成平台，支持 anime/hentai 模型，有社区组件
- **内容尺度**：Hardcore（18+ NSFW 区）
- **付费模式**：免费（100 credits/天）+ $5-$20/月订阅
- **用户规模**：6M 月访问（峰值后下跌 70%，2025 年中崩落）
- **crpg 重叠度**：低（独立图像工具，无叙事）
- **威胁等级**：低

---

**B4. Seduced.AI**

- **产品形态**：专注成人图像+视频生成，纯粹图像工具，无叙事
- **内容尺度**：Hardcore
- **付费模式**：$10-$150/月（credits 制）
- **用户规模**："最高流量 NSFW AI 生成器之一"（无公开数据）
- **crpg 重叠度**：低（纯图像，无叙事）
- **威胁等级**：低（不同用例）

---

**B5. Unstable Diffusion**

- **产品形态**：NSFW Stable Diffusion 云端服务 + Discord 社区（400K 成员）
- **内容尺度**：Hardcore
- **付费模式**：$14.99-$59.99/月
- **用户规模**：500K 张/天生成量，400K Discord 成员
- **crpg 重叠度**：低（纯图像）
- **威胁等级**：低

---

### C 类：AI 角色陪伴

---

**C1. Character.AI**

- **产品形态**：角色 chat + Stories 模式（2025 年新增）替代开放对话，已推出 AI 角色预写冒险
- **内容尺度**：SFW + 有限 Soft NSFW（"Bolder Energy"限成人）；禁止显式内容
- **付费模式**：$9.99/月（c.ai+），免费基础版
- **用户规模**：20M MAU，$50M ARR（2025 年），180M 月访问
- **crpg 重叠度**：低（Stories 模式有部分叙事，但无成人图像，内容受限）
- **威胁等级**：低（内容政策不允许 crpg 的核心成人叙事）
- **差异化弱点**：2025 年起严格限制 18+ 内容；Stories 模式叙事质量弱；无图像生成

---

**C2. CrushOn.AI**

- **产品形态**：无审查成人角色 chat，群组 chat（多角色同时），长记忆，明确 NSFW 定位
- **内容尺度**：Hardcore（明确设计为 NSFW，无内容过滤）
- **付费模式**：免费（50 条/天）+ $4.99-$50/月
- **用户规模**：28M 月访问（2026/2，环比-14.87%），2024 年 12.4M，快速增长
- **技术堆栈**：GPT-4o、Claude 3.5 Sonnet、MythoMax（按计划）
- **UGC 机制**：用户创建角色，社区可访问
- **crpg 重叠度**：高（成人+剧情+角色，但纯 chat 向，无分支结构，无图像）
- **威胁等级**：高（抢夺同一批成人用户，增长最快）
- **差异化弱点**：纯 chat 无分支游戏结构；无配套图像生成；叙事质量无系统框架

---

**C3. Candy.ai**

- **产品形态**：AI 虚拟伴侣，文字 chat + 图像生成（角色写真），无叙事游戏结构
- **内容尺度**：Hardcore（NSFW 图像 + 显式对话）
- **付费模式**：$5.99-$12.99/月（年付折扣）+ token 购买
- **用户规模**：11.6M 月访问，$25M ARR（2024 年），2026/3 月增长 35.76%
- **crpg 重叠度**：中（成人+图像，但无叙事结构，角色陪伴而非分支故事）
- **威胁等级**：中（陪伴市场重叠，但用例不同）

---

**C4. SpicyChat**

- **产品形态**：NSFW 角色 chat，300K+ 角色库，声音+图像选项
- **内容尺度**：Hardcore
- **付费模式**：免费 + $5-$24.95/月
- **用户规模**：2M 注册用户（具体 MAU 未公开）
- **crpg 重叠度**：高（成人角色扮演），但缺分支结构和图像质量
- **威胁等级**：中

---

**C5. Replika**

- **产品形态**：AI 情感陪伴，亲密但非显式，心理健康定位
- **内容尺度**：Soft NSFW（亲密语言，非显式）
- **付费模式**：$19.99/月（Pro，含有限 NSFW 功能）
- **用户规模**：30M 注册，$25M 营收，10M+ 活跃
- **crpg 重叠度**：低（情感陪伴，无叙事游戏）
- **威胁等级**：低

---

### D 类：互动小说/Visual Novel 工具

---

**D1. Ren'Py**

- **产品形态**：开源 VN 引擎，Python 脚本，图像+音乐+分支，成千上万发布游戏
- **内容尺度**：引擎本身无限制，成人 VN 主流引擎
- **付费模式**：完全免费开源
- **crpg 重叠度**：低（传统工具，非 AI 生成平台），但作为对标参考价值高（crpg 的创作者端应达到类似的发布能力）
- **威胁等级**：低（工具而非平台竞争）
- **差异化弱点**：需要编程；无 AI 内容生成；学习曲线高

---

**D2. Twine/Ink/ChoiceScript**

- **产品形态**：纯文字分支叙事工具，无 AI，无图像
- **内容尺度**：工具无限制
- **付费模式**：免费
- **crpg 重叠度**：低（工具参考价值：分支结构设计）
- **威胁等级**：低

---

**D3. miku.gg**

- **产品形态**：AI 生成视觉小说，角色卡系统，支持 NSFW 情绪图包，分支对话，用户可创作并分享
- **内容尺度**：Soft NSFW（NSFW 情绪启用后），图像为 anime 风
- **付费模式**：未明确（Gumroad 页面存在，小规模）
- **UGC 机制**：用户创建并分享视觉小说，有公开 bot 数据库
- **crpg 重叠度**：中（VN+AI+UGC，但规模小，无成熟商业化）
- **威胁等级**：低（概念相似但规模和质量均差距大）

---

**D4. Endless Visual Novel**

- **产品形态**：AI 生成 VN 游戏，玩家可触发世界/角色生成，Creator 层可发布分享
- **内容尺度**：未明确（官网无声明，可能 SFW 主导）
- **付费模式**：免费 + €9/月 Voyager + €15/月 Creator
- **crpg 重叠度**：中（平台结构相似：免费读者+付费创作者）
- **威胁等级**：低（无明确成人定位，规模小）

---

### E 类：传统成人内容平台

---

**E1. Literotica**

- **产品形态**：成人文字小说投稿平台，无 AI 生成，无图像，无分支叙事
- **内容尺度**：Hardcore（成人文学全覆盖）
- **付费模式**：免费（广告支撑）
- **用户规模**：50M 月访问（2025 年 12 月）
- **crpg 重叠度**：中（纯享版的读者端对标）
- **威胁等级**：低（静态文字，无 AI，无游戏化），但展示了成人文字市场的巨大需求

---

**E2. AO3（Archive of Our Own）**

- **产品形态**：同人/原创故事投稿平台，无 AI，无图像，无互动
- **内容尺度**：Hardcore（18+ 区完整支持）
- **付费模式**：完全免费（OTW 非营利）
- **用户规模**：17.2M 作品，146M 周访问（2025/11），高度活跃
- **crpg 重叠度**：低（静态叙事，非互动游戏）
- **威胁等级**：低（用例不同），但用户基础是 crpg 的核心目标读者群

---

**E3. Wattpad**

- **产品形态**：移动端小说发布平台，80M+ 用户，有 Mature 标签（无显式成人）
- **内容尺度**：Soft（无显式成人，有成熟度标签）
- **付费模式**：免费 + $5.99/月 Premium（去广告）
- **crpg 重叠度**：低（非成人，非互动游戏）
- **威胁等级**：低

---

**E4. Fanvue**

- **产品形态**：类 OnlyFans 订阅平台，唯一明确允许 AI 生成成人内容的主流平台，AI 创作者占 15% 营收
- **内容尺度**：Hardcore（AI 全合成角色允许）
- **付费模式**：创作者保留 85%，读者订阅
- **用户规模**：17M MAU，$100M ARR（2025 年，同比增长 150%），2026/1 完成 $22M A 轮
- **crpg 重叠度**：中（AI 成人内容+UGC 发布，但非叙事游戏形态）
- **威胁等级**：中（Fanvue 的 AI 创作者经济可能分流 crpg 创作者）

---

### F 类：新兴 AI 原生成人创作平台

---

**F1. DeepFiction Studio**

- **产品形态**：文字+图像+视频三合一 AI 创作平台，"Lustix" 功能专用显式成人内容，故事+角色+图像在一个工作空间
- **内容尺度**：Hardcore（Lustix 为最高档，行业评为"2026 年最专业成人故事生成器"）
- **付费模式**：$5/月 Starter / $20/月 Pro / $75/月 Studio；免费每天 5 credits
- **用户规模**：未公开，成长期
- **UGC 机制**：无公开社区发布机制（付费订阅者保留版权，但无读者端）
- **crpg 重叠度**：极高（最接近 crpg 的技术定位）
- **威胁等级**：高（当前最直接技术路线竞品）
- **差异化弱点**：无读者端/社区发布（无"纯享版"）；叙事质量未系统化（无 McKee 框架）；图像与叙事结构脱节（非电影镜头语言设计）；无 BYOK

---

**F2. RedQuill**

- **产品形态**：成人故事生成+社区，用户可分享/remix 故事和角色，"RedQuillers" 社区
- **内容尺度**：Hardcore
- **付费模式**：$12.69-$26.69/月
- **用户规模**：10M+ 故事，15K+ 角色
- **UGC 机制**：有！用户分享、探索、remix 故事——但无免费读者端（需订阅）
- **crpg 重叠度**：高（成人故事+社区+UGC）
- **威胁等级**：中（有 UGC 但无图像，无分支游戏结构）
- **差异化弱点**：无图像；无分支叙事游戏化；读者不能免费访问（无"纯享版"）

---

**F3. StoryPlay X**

- **产品形态**：成人浪漫互动故事，分支路径（3-4 选项），玩家选择影响角色关系和情节走向
- **内容尺度**：Hardcore（AI 色情故事生成）
- **付费模式**：未明确（平台自述为成人互动浪漫冒险）
- **用户规模**："用户平均每次 3.2 小时，78% 回头探索不同路径"（自述数据，存疑）
- **crpg 重叠度**：高（分支叙事+成人），但无图像，叙事框架不明
- **威胁等级**：中
- **差异化弱点**：无配套图像；无创作者 UGC 发布机制；数据可信度低

---

**F4. CrushOn.AI（重复：见 C2）**

---

**F5. SpicyChat（重复：见 C4）**

---

## 4. crpg 的市场位置

### 最像 crpg 的 Top 3 竞品（如果他们做得好，crpg 还能存在吗？）

**第 1 名：DeepFiction Studio**
最近似。文字+图像+视频，成人定位，Lustix 成人功能，$5-$75/月。但：没有免费读者端（无"纯享版"），没有创作者 UGC 社区，叙事无系统化框架，图像和叙事是分开工作流而非电影化叙事单元。**crpg 存活理由**：电影镜头语言方法论 + McKee 叙事质量 + 纯享版读者端——这三点 DeepFiction 完全没有。

**第 2 名：NovelAI**
最成熟。文字+图像，无审查，隐私优先，有忠实订阅用户基础。但：图像严格限于 anime 风格，与写实向成人叙事不匹配；无分支游戏结构；无 UGC 发布平台；读者无法浏览他人作品。**crpg 存活理由**：写实向（Grok Imagine）而非 anime、分支游戏而非线性叙事工具、有读者端。

**第 3 名：CrushOn.AI**
用户规模最大（28M 月访问），成人无审查，增长最快。但：纯 chat 向，无分支游戏结构，无配套图像，无创作者发布平台。**crpg 存活理由**：游戏化分支叙事 + 电影图像 + 创作者发布生态。

---

### 现有产品中最大的差距（crpg 能填补什么空位？）

五维空位分析：

| 维度 | NovelAI | DeepFiction | CrushOn | AI Dungeon | 是否有人覆盖 |
|------|---------|-------------|---------|------------|------------|
| 高质量分支叙事 | 弱（线性写作工具） | 弱（无分支） | 无 | 有（但质量差） | 无（质量+分支二者兼有的没有） |
| 成人显式内容 | 有（anime） | 有 | 有 | 部分 | 有（各平台分散） |
| 高质量配套图像（写实/电影化） | 仅 anime | 有（一般质量） | 无 | 无 | 无（电影化镜头语言） |
| 创作者 UGC 发布 | 无 | 无 | 无 | 弱 | 无（成人叙事游戏发布平台） |
| 免费读者端 | 无 | 无 | 无 | 有（弱） | 无 |

**结论**：五维组合没有任何单一产品覆盖。这是真实的市场空位，不是幻觉。

---

## 5. 市场断层线

### 断层 1：高叙事质量 × 成人显式 × 电影化图像的交叉点

NovelAI 有文字质量+成人+图像，但图像是 anime 扩散模型，与写实向电影风格完全不同。没有任何平台在做"写实电影镜头语言 + 成人叙事 + per-shot 图像组合"这件事。

### 断层 2：成人叙事游戏的创作者发布平台

Ren'Py 游戏（传统工具）+ Itch.io（发布）是现有最接近的组合，但需要编码，无 AI 辅助。AI Dungeon 的"世界分享"功能弱，无正式发布机制。没有平台做到"AI 生成分支叙事成人游戏 → 创作者一键发布 → 读者免费游玩"的闭环。

### 断层 3：免费读者端 + 付费创作端的双模式在成人叙事领域

Literotica（50M 月访问）证明了免费成人文字平台的超大需求。AO3（146M 周访问）证明了非商业纯享读者的规模。但两者都是静态文字，无 AI，无游戏化。把这两个受众（自由创作者 + 免费享受读者）融合到 AI 生成分支叙事游戏平台，目前完全空白。

### 断层 4：支付合规后的 UGC 成人平台

Civitai 的支付危机（Visa/Mastercard 封锁）说明了这个市场的支付问题。Fanvue 是当前唯一解决了"AI 成人内容 + 合法支付"的主流平台，但它是订阅陪伴模式而非叙事游戏。crpg 的"纯享版零支付"结构绕开了这个问题。

---

## 6. crpg 差异化机会点（Top 5）

**机会 1：McKee 叙事框架作为叙事质量护城河**
没有任何现有 AI 互动叙事平台有系统化的叙事质量框架。NovelAI Erato 只是"无审查的写作助手"，不是"懂电影叙事的故事引擎"。这是 crpg 最可防御的护城河，且对用户不可见（无需营销，故事质量自然体现）。

**机会 2：电影镜头语言 + 写实图像的 per-shot 设计**
所有文字+图像平台（NovelAI、DeepFiction、Talefy）都是"生成一张配图"的逻辑，没有人在做"每个叙事节拍按电影剪辑方式配置 0-N 张特定构图的图像"。这是 Shot Director + Visual DNA 方法论的差异化。

**机会 3：双模式架构——零成本读者端 + 创作者付费端**
Endless Visual Novel（€9/€15）和 Literotica（免费）各做了一半。crpg 做完整的"零生成零付费纯享版 + 创作者版"，是成人 AI 叙事市场的第一个这个架构。

**机会 4：BYOK 降低创作者成本门槛**
NovelCrafter 的 BYOK 在非成人市场有用户基础。成人叙事创作者目前的选择是：NovelAI 固定订阅（无 BYOK）或 FictionLab/DreamGen 固定 token 包。crpg 的 BYOK 路径（xAI key 自带）在这个市场是差异化。

**机会 5：成人叙事游戏的 UGC 发布生态作为后期护城河**
一旦有足够创作者发布高质量游戏，平台的 UGC 库就成为竞争壁垒。Literotica 的 50M 用户来自数十年的内容积累。crpg 如果率先建立"AI 生成分支成人叙事游戏"的内容库，将成为该细分领域的 SEO 和自然流量核心。

---

## 7. crpg 战略红灯（Top 3）

**红灯 1：xAI Grok Imagine 后端成本结构恶化**
2026 年 3 月 19 日，Grok Imagine 取消免费层，SuperGrok 订阅（$30/月）才能访问图像生成。API 端 $0.02-$0.07/张的价格本身不高，但叠加 crpg 的"per-shot 多帧"设计（5-8 shots/高潮节点），创作者单次游戏生成成本可能达到数美元。如果 crpg 用平台 key 覆盖图像成本，商业模型需要仔细计算。如果强制 BYOK 图像，创作者需要 xAI API access，摩擦增加。

**红灯 2：支付处理合规风险（Visa/Mastercard 封锁成人 AI 平台）**
Civitai 被封锁是 2025 年的现实案例。crpg 的"纯享版零付费"架构实际上绕过了这个问题（读者不付钱），但创作者付费端（平台付费路径）仍面临同样风险。建议提前研究专门服务成人内容的支付处理商（CCBill、Epoch、NowPayments 加密方案）。

**红灯 3：CrushOn.AI + DeepFiction 双向夹击**
CrushOn.AI 有 28M 月访问和成人用户基础，如果它增加图像功能（现已有群组 chat），与 crpg 重叠度将剧增。DeepFiction Studio 如果增加 UGC 发布和读者端，将成为最直接的全面竞品。这两家都有商业化资金，动作可能快于 crpg 的开发周期。**应对**：crpg 需要在叙事质量和电影镜头语言上建立足够深的护城河，而非依赖"功能覆盖"。

---

## 8. 对 crpg 战略的 1 个关键建议

**如果 crpg 要赢，核心差异化不应该是"成人内容"（门槛过低，已有大量竞品），而应该是"叙事质量 × 电影美学体验"。**

具体路径：将 McKee + 电影镜头方法论作为产品的可感知差异——用户打开一个 crpg 故事，第一眼就感受到画面构图和叙事节奏明显优于 FictionLab 或 DeepFiction。然后用"免费读者端"快速获取读者口碑，再用"创作者端"获取内容生产者。这是一个不需要击败 CrushOn.AI（28M 用户）的策略，而是在一个更小但更有质量的赛道上建立品牌——类似 A24 之于好莱坞大厂。

成人内容 AI 市场的现状是"大量廉价内容，极少高质量叙事"。这个空位是真实的。

---

## 9. Cookie Crumb Trail — 完整来源

### A 类竞品来源
- AI Dungeon 定价：https://alternatives.co/software/ai-dungeon/pricing/
- AI Dungeon 2026 综述：https://inkwrit.com/ai-dungeon-review-2026-unlimited-stories/
- AI Dungeon Wikipedia：https://en.wikipedia.org/wiki/AI_Dungeon
- AI Dungeon 衰退数据：https://www.owler.com/company/aidungeon
- NovelAI 官网（WebFetch）：https://novelai.net/
- NovelAI 定价文档：https://docs.novelai.net/en/subscription/
- NovelAI Erato 发布（X）：https://x.com/novelaiofficial/status/1838314584408756447
- NovelAI 2026 综述：https://www.toolsforhumans.ai/ai-tools/novelai
- Sudowrite 定价：https://sudowrite.framer.website/pricing
- Sudowrite 综述：https://nerdynav.com/sudowrite-review/
- Sudowrite 用户数：https://aitoolsdevpro.com/ai-tools/sudowrite-guide/
- Dreamily 综述：https://powerusers.ai/ai-tool/dreamily/
- NovelCrafter 定价：https://www.novelcrafter.com/pricing
- NovelCrafter NSFW：https://www.novelcrafter.com/help/docs/models/nsfw-models
- FictionLab 综述：https://aimaghub.com/fictionlab-ai-guide-2026/
- DreamGen 官网（WebFetch）：https://dreamgen.com/
- DreamGen 综述：https://scribehow.com/page/DreamGen_AI_Review_2026
- StoryPlay X：https://www.storyplayx.com/blog/storyplay-x-ai-nsfw/

### B 类竞品来源
- Civitai Wikipedia：https://en.wikipedia.org/wiki/Civitai
- Civitai 支付封锁：https://decrypt.co/322197/civitai-crypto-credit-card-processor-ban-ai-explicit-content
- Civitai 政策压力：https://www.unite.ai/civitai-tightens-deepfake-rules-under-pressure-from-mastercard-and-visa/
- Civitai 加密货币：https://yellow.com/news/ai-art-platform-civitai-turns-to-usdt-eth-after-card-ban
- Tensor Art 综述：https://www.tooljunction.io/ai-tools/tensor-art
- Seduced AI 定价：https://appseducedai.com/pricing.html
- Seduced AI 综述：https://aihaven.com/aitools/seduced-ai/
- Unstable Diffusion 综述：https://genfindr.com/review/unstable-diffusion
- Unstable Diffusion 生成量：https://finance.yahoo.com/news/ai-image-generator-making-nsfw-180602058.html
- SoulGen 市场数据：https://companionguide.ai/news/soulgen-ai-adult-image-generation-guide-2026

### C 类竞品来源
- Character.AI Sacra（WebFetch）：https://sacra.com/c/character-ai/
- Character.AI 数据：https://completeaitraining.com/news/character-ai-2025-by-the-numbers-20m-maus-322m-revenue-1b/
- Character.AI Stories 模式：https://quasa.io/media/character-ai-bans-users-under-18-and-launches-stories
- CrushOn.AI 综述：https://companionguide.ai/companions/crushon-ai
- CrushOn.AI 流量：https://www.semrush.com/website/crushon.ai/overview/
- CrushOn.AI 统计：https://zipdo.co/crushon-ai-statistics/
- Candy.ai 营收：https://tripleminds.co/blogs/strategies/candy-ai-revenue-models/
- Candy.ai 流量：https://www.similarweb.com/website/candy.ai/
- SpicyChat 综述：https://aihaven.com/aitools/spicychat-ai/
- Replika 综述：https://weavai.app/blog/en/2026/04/10/replika-review-2026
- Replika 营收：https://angelapopo.com/p/what-replika-gets-right-wrong-and
- Muah.AI 综述：https://companionguide.ai/companions/muah-ai

### D 类竞品来源
- miku.gg 官网：https://miku.gg/
- Endless Visual Novel 官网（WebFetch）：https://endlessvn.io/
- Ren'Py 生态：https://alternativeto.net/software/renpy/

### E 类竞品来源
- Literotica Wikipedia：https://en.wikipedia.org/wiki/Literotica
- Literotica 流量：https://webrate.org/site/literotica.com/
- AO3 统计：https://archiveofourown.org/admin_posts/33966
- AO3 作品量：https://en.wikipedia.org/wiki/Archive_of_Our_Own
- Wattpad 政策：https://policies.wattpad.com/content/
- Fanvue 营收：https://sacra.com/c/fanvue/
- Fanvue 综述：https://mariavibe.com/blog/fanvue-review-2026-ai/
- Fanvue 融资：https://blog.fanvue.com/what-is-fanvue/

### F 类竞品来源
- DeepFiction 定价（WebFetch）：https://www.deepfiction.ai/pricing
- DeepFiction 综述：https://aichief.com/ai-image-generator/deepfiction-ai/
- RedQuill 综述：https://findmyaitool.com/tool/redquill
- RedQuill 统计：https://autogpt.net/redquill-and-ai-smut-why-are-they-so-popular/
- StoryPlay X 综述：https://www.storyplayx.com/blog/storyplay-x-spicy-ai-story-generator/

### 技术与合规来源
- xAI Grok NSFW 政策：https://yingtu.ai/en/blog/grok-xai-nsfw-image-generation-policy
- xAI Grok 图像付费门：https://www.aifreeapi.com/en/posts/grok-imagine-adult-content
- xAI 争议：https://www.cnbc.com/2026/01/14/musk-xai-blocks-grok-chatbot-from-creating-sexualized-images-of-people.html
- 成人支付合规：https://www.payconsults.com/post/payment-solutions-for-ai-adult-platforms-what-businesses-need-to-know-in-2026
- 成人内容支付处理：https://medium.com/coinmonks/adult-content-payment-processing-in-2026

### 市场数据来源
- 全球 AI 内容生成市场：https://www.storyplayx.com/blog/storyplay-x-ai-nsfw/
- 成人内容 AI 市场增长：https://companionguide.ai/news/soulgen-ai-adult-image-generation-guide-2026
- 视觉小说市场：https://nicholascarter.techraisal.com/blog/best-ai-text-adventure-games-for-fantasy-story-quality-vs-cost/

---

## 附录：数据可信度标注

- Character.AI $50M ARR：两家来源（Sacra + Business of Apps）交叉确认，可信
- Candy.ai $25M ARR：单一来源（TripleMinds 分析），标注"估计"
- SoulGen $420M 营收：单一来源（companionguide.ai），数字可疑（远超 Candy.ai $25M ARR），强烈标注"估计，存疑，可能夸大"
- CrushOn.AI 28M 月访问：Semrush 数据，可信
- Civitai 3.2M 用户：多次来源引用，可信
- Literotica 50M 月访问：单一 webrate 数据，标注"估计"
- AI Dungeon WAU 38K：SensorTower Q1 2024 数据，时效有限
- NovelAI 用户数：无官方公开数据，所有"300K 订阅"均为行业估计

---

*报告生成于 2026-04-17，数据截止 2026-04 月上旬。*
