# Robert McKee《Story》完整框架 —— daisy 选用 vs 漏用

**书：** Robert McKee, *Story: Substance, Structure, Style and the Principles of Screenwriting* (1997)
**页数：** ~450 页，原书以好莱坞经典叙事理论为主，是当代编剧教科书的事实标准。
**用途：** 识别 daisy 在压缩六条硬约束时舍弃了什么，为新项目 `crpg` 决定是否补回。

图例：✅ daisy 已采用 &nbsp; 🟡 部分/隐式采用 &nbsp; ❌ daisy 未采用

---

## 一、故事三角（Story Triangle）—— 结构范式

McKee 把所有故事设计放到一个三角坐标里：

| 范式 | 特征 | 典型作品 |
|---|---|---|
| **Archplot（经典设计）** | 闭合结局 · 线性时间 · 主动主角 · 外部冲突为主 · 单一主角 · 因果连续 · 改变 | 好莱坞主流、《辛德勒的名单》 |
| **Miniplot（最小化）** | 开放结局 · 被动主角 · 内在冲突为主 · 多主角 · 较少动作 | 欧洲艺术片、《迷失东京》 |
| **Antiplot（反情节）** | 巧合取代因果 · 非线性/无时间 · 不连续 · 荒诞 · 内部矛盾 | 《暴力云与送子鹳》《记忆碎片》 |

**daisy 状态**：❌ 未显式引入
- daisy 的 `preset = linear/bifurcating/funnel/web` 描述的是图谱**拓扑形态**，不是 McKee 的**叙事范式**
- 用户选 "bifurcating web" 时，模型其实在无意识地选择 Archplot 还是 Miniplot——全靠 Claude 的默认倾向（偏 Archplot）
- **新项目可补**：增加一个 `plotParadigm` 维度，让用户显式选"主流娱乐/文艺内省/反叙事实验"

---

## 二、故事实质（Substance）

### 2.1 Setting（设定）
四维坐标：**Period（时代）· Duration（持续时间）· Location（地点）· Level of Conflict（冲突层级）**

- 🟡 daisy 的 `worldSetting` 字段对应这一维，但没有结构化拆分
- **新项目可补**：让 worldSetting 变成这 4 个字段的组合输入

### 2.2 Genre（类型约定）—— **McKee 强调最多的实操维度之一**
每个类型（动作/爱情/恐怖/战争/传记...）有：
- **Conventions**（约定元素，如恐怖片必有"威胁不可解释的源头"）
- **Obligatory Scenes**（必须场景，如爱情片必须有"The Kiss"那一刻）
- **观众期待**（不满足就会被视为"背叛类型"）

McKee：*"The writer who doesn't know his genre is a writer without a community."*

**daisy 状态**：❌ 完全未引入
- V6 的"ACT 1 SETUP 必须主动游玩"是一种隐性的**游戏类型**约定，但不是 McKee 意义上的 Genre
- **新项目应补**：这是和图片生成结合时极重要的维度——Genre 决定视觉风格（赛博朋克 vs 维多利亚 vs 日式恐怖 vs 中世纪奇幻），一个 Genre 维度同时驱动文字和图片 prompt

---

## 三、结构光谱（Structural Spectrum）—— **McKee 的根基之一**

从小到大 5 层：

| 层级 | 定义 | 功能 |
|---|---|---|
| **Beat（节拍）** | 一次 action-reaction exchange | 改变场景的瞬时价值极性 |
| **Scene（场）** | 一个连续动作，发生在一个地点一段时间 | 必须包含 Turning Point，产生场景级价值变化 |
| **Sequence（序列）** | 2-5 场构成，围绕一个次要目标 | 产生更大的价值变化（比场更强，比幕更弱） |
| **Act（幕）** | 多个序列组成，以主要转折点结束 | 产生主要价值变化 |
| **Story（故事）** | 所有幕的总和 | 表达 Controlling Idea |

**daisy 状态**：🟡 部分采用
- V4 的 extreme 模式首次引入 "beats" 数组
- V6 把 beat 升级为独立节点 + `sequences` 顶层数组，显式引入 **Beat / Sequence / Act** 三层
- ❌ 但 **"Scene" 层缺失**—— 在 V6 extreme 下，beat=node，没有中间的 scene 层；非 extreme 模式则 scene=node，又没 beat 层。**daisy 永远只有相邻两层，缺灵活性**
- **新项目可补**：让 scene 成为 first-class 抽象，beat 是 scene 的可折叠子层（类似 Figma 的组件实例化）

### Scene Turning Point（场景转折点）—— McKee 的硬规矩
*"Every scene must turn. If it doesn't turn, it's not a scene, it's exposition."*
每场必须有转折——价值从一极翻到另一极。

**daisy 状态**：✅ 通过 `valueBefore → valueAfter` 字段强制实现

---

## 四、故事的七个核心原理（McKee 的"Principles"章）

### 4.1 Inciting Incident（激励事件）
*故事真正开始的那一刻——平衡被打破，主角必须做某事*
- 必须在故事前 25% 内发生
- 必须激活故事的 Controlling Idea

**daisy 状态**：🟡 V6 在 ACT 1 SETUP 里加了"第 2-3 个节点就进入激励事件"—— 概念对，但没显式命名

### 4.2 Progressive Complications（递进复杂）✅
每一拍加压，never plateau。**daisy 六条之一**。

### 4.3 Crisis（危机）—— **daisy 压缩成了"Dilemma"**
McKee：危机 = **主角必须做出最后的、不可逆的决定**。是全故事最重要的一刻之一。
- **Dilemma**（两难）是 Crisis 的一种形式：两个善的选择 or 两个恶的选择
- daisy 的六条硬约束把 Crisis 压缩成"每个 choice 节点都是 Dilemma"——泛化了，但也淡化了"**主危机**"（the Crisis）的特殊地位

**新项目可补**：把"主危机点"标注为图谱上的一个特殊节点（区别于普通 choice），它必须在 Act 3 结束之前，且是整个故事最困难的选择

### 4.4 Climax（高潮）—— **daisy 未显式建模**
McKee：Climax 是故事的**最大的价值翻转**，是观众情感体验的顶点。
- 一个好故事的所有 beat/scene/sequence/act 的价值变化都导向这一刻
- 必须解决 Controlling Idea

**daisy 状态**：❌ 没有"climax node type"
- V6 的 ending 节点是"结局"，不是"高潮"——这是两回事
- 经典结构里：... → Climax（高潮决定）→ Resolution（余波/结局）
- **新项目可补**：在 ending 之前强制引入 `climax` 节点类型，或让 act_break 中的最后一个承担高潮语义

### 4.5 The Gap（落差）✅
*角色主观期望 vs 客观现实反应之间的落差是戏剧能量的来源*
**daisy 六条之一**。

### 4.6 Value Shift（价值转换）✅
带极性的**生/死、爱/恨、真/假、自由/奴役、信任/背叛、希望/绝望**等。每场必须转换至少一个。**daisy 六条之一**。

### 4.7 Controlling Idea（主控思想）✅
**Value + Cause**：最终的价值状态 + 为什么会这样。
- 例：*"Justice prevails when honest people outwit the corrupt."*（=正义胜 / 因为诚实人智胜腐败）
- 例：*"Love conquers all when lovers fight for each other against all odds."*
**daisy 六条之一**。但 daisy 的 `controllingIdea` 只要求一句话，没有强制 Value+Cause 的两部分结构。
- **新项目可补**：把 `controllingIdea` 拆成 `{ finalValue: string, cause: string }` 强制结构化

---

## 五、对抗原则（Principle of Antagonism）—— **daisy 漏掉的重要原理**

McKee 的原话：*"A protagonist and his story can only be as intellectually fascinating and emotionally compelling as the forces of antagonism make them."*

**对抗力量必须在所有层面都至少和主角一样强**：
- 肉体层面强（物理威胁）
- 社交层面强（关系、机构压力）
- 个人层面强（情感撕裂）
- 智力层面强（阴谋、真相）
- 道德层面强（诱惑、妥协）

**daisy 状态**：❌ 完全未引入
- daisy 的"Dilemma"只约束 choice 节点有两难，但没约束"反派/对抗力"的强度匹配主角
- 这是 V3/V4/V6 的生成经常塌掉的地方：AI 倾向写"强主角 + 弱敌人 + 快速胜利"
- **新项目应补**：生成时要求**每个主要对抗力量的 power level 必须 ≥ 主角**，在骨架阶段就强制

---

## 六、三层冲突（Three Levels of Conflict）✅
- **Inner Conflict**：内在（心理/情感）
- **Personal Conflict**：人际（关系/家庭/恋人）
- **Extra-personal Conflict**：超个人（社会/机构/环境/物理世界）

**daisy 六条之一**。

---

## 七、角色设计（Character）

### 7.1 Character vs Characterization —— **daisy 未采用**
- **Characterization**（外在特征）：年龄、外貌、服饰、口音、爱好——表层可观察
- **True Character**（真实本性）：**压力下做出的选择**，才揭示角色的真实自我
- McKee：角色是弧线，不是配置

**daisy 状态**：❌
- daisy 的 characters 输入只是一句话的 description，纯 characterization
- **新项目可补**：角色结构化为 `{ characterization, trueCharacterRevealedUnder: <某压力场景> }`，让 AI 在生成时主动设计"压力揭示时刻"

### 7.2 Character Arc（角色弧）—— **daisy 未采用**
- 主角从故事起点到终点，内在必须有变化
- 弧的方向：正面（觉醒）/ 负面（堕落）/ 平行（坚守但世界改变）

**daisy 状态**：❌（`controllingIdea` 隐含了价值弧，但没有显式角色弧）

### 7.3 True Character Revelation
**压力下的选择 > 压力外的声明**。角色的口头承诺不算，行动才算。
**daisy 状态**：🟡 V6 的"Dialogue is gameplay" 和 "Player as agent" 隐含推动——让角色 DO 而不是 SAY。

---

## 八、说明信息（Exposition）—— **daisy 完全未建模**

McKee 的原则：*"Convert exposition to ammunition."*
**把背景信息当弹药用**——在角色处于压力时被迫披露最深的秘密，此时信息既推动情节又揭示性格。

反例：开场大段旁白/内心独白交代背景 → **观众必逃**

**daisy 状态**：❌ 完全没涉及
- daisy 的 content 里，背景信息由 AI 自由安排，没有"弹药化"约束
- V6 "Show the world through interaction" 算是方向一致但不等同
- **新项目可补**：要求骨架阶段就标记 `expositionPayloads: Array<{ info, deliveredAtNodeId, underWhatPressure }>`，让世界观信息被"弹药化"分发

---

## 九、反套路章节（Writer at Work）—— daisy 的 ANTI-MELODRAMA 来源

McKee 花了整整一章讲**叙事中的"坏习惯"**，三个致命问题：

### 9.1 Cliché（陈词滥调）
- 根源：研究不足
- 解药：深入研究 setting/character/conflict 的真实质感

### 9.2 Melodrama（情节剧/煽情）
- 定义：**表达超过了事件引起的程度**（过度情绪/华丽辞藻/廉价反转）
- 症状：每场都是危机、每个角色都在哭、所有转折都是"突然"
- 解药：restraint（克制）——用具体动作和具体对话代替形容词

### 9.3 Coincidence（巧合）
- 偶然可以启动故事，但不能**解决**故事
- 巧合必须产生合理的后果，不是解构性的"deus ex machina"

**daisy 状态**：✅ V6 的 ANTI-MELODRAMA 四条规则几乎逐条对应 McKee 的 Melodrama 章：禁止命名情绪 / 最多一个身体感觉 / 禁止华丽隐喻 / 不是每场都是危机
- ❌ 但 Cliché 和 Coincidence 没处理

---

## 十、潜台词（Subtext）—— **daisy 未采用**

McKee：*"Life on the page"* 永远不等于*"words on the page"*。
- 每句台词**字面**说的是 A
- **下面**真正在说 B（人物实际意图/恐惧/欲望）
- **观众感知**的是 C（在当前情境下这句话真实的分量）

**daisy 状态**：❌
- V6 "Dialogue is gameplay" 鼓励对话推进信息 —— 方向对，但没强制潜台词
- **新项目可补**：对话生成时要求 `{ text, subtext, characterTruth }` 三层

---

## 十一、类型约定汇总（Genre Book 章节）—— daisy 完全未采用

McKee 列出了 25+ 种电影类型及其约定，部分重要的：

| 类型 | 必须元素 | Obligatory Scenes |
|---|---|---|
| Action/Adventure | 英雄 vs 恶徒 · 追逐 · 最终对决 | 训练蒙太奇、反派揭示动机、肉搏高潮 |
| Love Story | 两人相遇 · 障碍 · 团聚或分离 | The Meet, The Kiss, The Separation, The Reunion |
| Horror | 威胁不可解释 · 角色逐渐被孤立 | False Ending（虚假结束）、Final Girl 存活 |
| Crime | 罪犯视角 vs 侦探视角 | Investigation Scene, Confrontation Scene |
| Coming of Age | 纯真 → 经验的价值转换 | Loss of Innocence Moment |

**daisy 状态**：❌ 彻底未建模
- Genre 是游戏化叙事最重要的用户选择入口之一，也是图像生成的关键信号
- **新项目必补**：Genre 维度 + 每个 Genre 的 obligatory scenes 约束 + Genre → 视觉风格映射

---

## 十二、写作方法（Writer's Method）—— daisy 天然契合

McKee 主张**先结构后文字**：
1. idea → **step outline**（每场一句话）→ treatment → screenplay
2. step outline 阶段不写任何对话/散文，只写"这场干什么、价值怎么变"
3. 这能让结构问题在写作之前被发现

**daisy 状态**：✅ V4/V6 的两步生成就是这个方法的工程化：
- Step 1 `buildSkeletonOnlyPrompt` = McKee 的 step outline
- Step 2 `buildContentBatchPrompt` = McKee 的 treatment/screenplay 阶段
- 这是 daisy 对 McKee 最漂亮的方法论转译

---

## 总结：daisy 从 McKee 整套体系中的采用率

| McKee 原理 | daisy 状态 | 压缩理由（笔者推测） |
|---|---|---|
| ①②③ Story Triangle 三范式 | ❌ | 选择范式这件事交给 AI 默认（大多数生成会落在 Archplot） |
| ④ Setting 四维 | 🟡 | worldSetting 文本字段兜住 |
| ⑤ Genre 约定 | ❌ | **最大的缺口**，影响图像生成潜力 |
| ⑥ Beat/Scene/Seq/Act 光谱 | 🟡 | V6 有 beat+seq+act，缺 scene 层 |
| ⑦ Scene Turning Point | ✅ | valueBefore/valueAfter 字段 |
| ⑧ Inciting Incident | 🟡 | V6 的 ACT 1 SETUP 暗示 |
| ⑨ Progressive Complication | ✅ | 六条之一 |
| ⑩ Crisis/Dilemma | 🟡 | 压缩为"每个 choice 都是 Dilemma" |
| ⑪ Climax | ❌ | 合并进 ending，丢失主高潮特殊性 |
| ⑫ The Gap | ✅ | 六条之一 |
| ⑬ Value Shift | ✅ | 六条之一 |
| ⑭ Controlling Idea | ✅ | 六条之一（但没强制 Value+Cause 结构） |
| ⑮ Antagonism 对抗原则 | ❌ | **第二大缺口**，导致 AI 写弱敌 |
| ⑯ Three Levels of Conflict | ✅ | 六条之一 |
| ⑰ Characterization vs True Character | ❌ | 角色设计扁平化 |
| ⑱ Character Arc | ❌ | 靠 controllingIdea 隐含 |
| ⑲ Exposition as Ammunition | ❌ | 背景信息扁平化分发 |
| ⑳ Cliché | ❌ | 未处理 |
| ㉑ Melodrama | ✅ | V6 ANTI-MELODRAMA 四条 |
| ㉒ Coincidence | ❌ | 未处理 |
| ㉓ Subtext | ❌ | 对话扁平化 |
| ㉔ Writer's Method（step outline 先行） | ✅ | 两步生成就是工程化 step outline |

**采用**：6 条硬约束 + Anti-Melodrama + 两步生成 = **7.5 项**
**遗漏**：Genre · Antagonism · Climax · Character Arc · Exposition · Subtext · Cliché · Coincidence = **8 项**

---

## 给新项目 crpg 的战术建议

按"投入 vs 产出"排序，可补的 McKee 维度：

### 高优先（强烈建议补）
1. **Genre 类型系统** —— 既提升文字质感，又是图像生成的关键信号（赛博朋克 vs 维多利亚的视觉天差地别）
2. **Antagonism 强度约束** —— 骨架生成阶段就要求"对抗力 ≥ 主角"
3. **Climax 特殊节点类型** —— 区分于普通 ending，强制在 Act 末尾前出现

### 中优先（建议补）
4. **Controlling Idea 结构化** —— `{ finalValue, cause }` 两字段
5. **Character Arc** —— 每个主角一条明确的弧
6. **Scene 层补齐** —— 让 beat 和 act 中间有"场"的概念

### 低优先（看需求）
7. **Subtext 潜台词** —— 对话深化，对纯享版影响大
8. **Exposition as Ammunition** —— 把世界观信息"弹药化"分发
9. **Cliché / Coincidence 反套路扩展** —— 在 Anti-Melodrama 基础上加两条
