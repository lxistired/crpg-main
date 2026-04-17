# Shot Design System —— Scene → Shot 的电影语法层

crpg 视觉 pipeline 的**第九层**（并列于 Visual DNA 1–8 层）。研究时间：2026-04-17。

---

## 0. TL;DR（给没时间读的决策者）

**问题**：我们当前的视觉 pipeline 把小说一个 scene = 一张图。人全挤进去，主次平分，结果是"旅游合影"而不是"电影"。

**诊断**：电影不是这样工作的。一个 scene 在电影里被拆成 **6–30 个 shot**，每个 shot 只服务一个**叙事任务**（建立空间 / 推进动作 / 揭示反应 / 放大细节 / 驳斥之前信息）。主次由"图像在画面中的尺寸 = 此刻在故事中的重要性"决定（**Hitchcock's Rule**），不由场上人数决定。

**解决**：Visual DNA 增加 **Shot Design Layer（第九层）**。每个 daisy 叙事节点不再映射为 1 张图，而是**一个 shot list（推荐 3–6 shots）**。前端展示选一张"主镜头封面"，其余作为可展开故事板或可轮播的分镜序列。

**三条最硬的方法论收获**：

1. **McKee**：一个 scene 必须有 **value shift**（正↔负）。先找 turning point，再围绕它设计 shot list。没有 turn 的 scene 不值得一张图，更不值得一个 list。
2. **Hitchcock**：画面中物体的**尺寸 = 该物体此刻在故事中的重要性**。多人场面里，ONE person 被放大，others 往往是散焦 / OTS / 只见肩背 / 干脆不在画面里。
3. **Mamet**：**uninflected shots + 剪辑**，而不是一张信息密度爆炸的巨图。每个 shot 只干一件事。观众的脑子通过**并置**（juxtaposition）把 story 拼起来——这是电影感的根。

---

## 1. 核心命题：为什么 "一 beat = 一张图塞所有元素" 是错的

### 1.1 电影不是这样工作的

一个 scene（场）≠ 一个 shot（镜头）。**scene 是叙事单位，shot 是视觉单位**。

典型比例：
- 对话戏（2 人）：scene 平均 ~8–20 个 shots
- 对抗戏 / 动作戏：scene 可达 40–100+ shots
- Tarkovsky 式长镜：1 个 shot 撑 1 个 scene（极少数例外）

即使是李安这种以"含蓄 / 长镜"闻名的导演，《色戒》单一 scene 也动辄十几到几十个 shot。珠宝店高潮那段有多次 POV 切换（刺客视角 / Yee 的视角 / Chia Chi 的视角）、多次 shot/reverse、多次 insert（戒指、钟、眼神）。**绝不是"把店里所有人塞进一张 wide"**。

### 1.2 为什么"塞所有人"在扩散模型里尤其糟糕

- 扩散模型在多人场景的**脸部特征保真度**随人数平方级下降（这是已知的扩散模型失败模式）
- 观众视线无引导，**谁都看不到"重点"**
- 所有人被迫"面对镜头摆拍"，破坏 Direction Layer 的 candid 原则
- 关键 micro-expression tell 在 full-body wide shot 里太小看不见
- 关键道具（戒指、信、手机屏）在 wide shot 里像素不够，无叙事力

### 1.3 方法论级缺陷

**我们把"描述小说场景"错当成了"描述电影画面"**。小说里"审讯室里三个人对峙"是一句**概念**——读者脑内自动切 shot。电影里这不是一个 shot，是**一组 coverage**。我们的 prompt 相当于让模型同时渲染整组 coverage 的平均值——得到的就是"合影"。

---

## 2. Shot Type Vocabulary（Shot 分类学 + 每种的叙事任务）

这是可以直接放进 prompt 的词汇表，每个 shot type 有**明确的 storytelling job**。

### 2.1 空间建立类

| Shot Type | 定义 | Storytelling Job | 在 scene 中的位置 |
|---|---|---|---|
| **Establishing Shot** | 极远景，建立地点 / 时间 / 氛围 | "这是哪里，什么时候，什么氛围" | Scene 开头 1–2 次，后段若空间切换需要 re-establish |
| **Master Shot / Wide** | 全景，覆盖整场动作 | 建立人物空间关系、block 位置 | Scene 开头 1 次；中段遇到重大位移后再用一次 |

### 2.2 主体 / 交互类

| Shot Type | 定义 | Storytelling Job |
|---|---|---|
| **Two-Shot** | 两个人同框（常为腰部以上） | 建立/确认二人关系强度；身体距离即心理距离 |
| **Over-the-Shoulder (OTS)** | 从一人肩后拍另一人 | 对话中的"听者视角"；表明 POV 归属 |
| **Single / Medium Close-Up (MCU)** | 单人胸部以上 | 承担对话 / 反应的主体 |
| **Close-Up (CU)** | 脸部 + 微少身体 | **重要情绪瞬间**；Hitchcock rule 触发 |
| **Extreme Close-Up (ECU)** | 眼睛 / 唇 / 手指 | **精神上的放大镜**；强烈压迫感或亲密 |

### 2.3 信息 / 细节类

| Shot Type | 定义 | Storytelling Job |
|---|---|---|
| **Insert** | 同一空间内的物件特写（手上的戒指、桌上的信） | 让观众"读到"关键物件；绝不要把这个信息交给 wide shot |
| **Cutaway** | 离开主动作的补充画面（钟、窗外、远处的狗） | subtext / 主题性 / 节奏调节 |
| **POV** | 主观视角，"我看到的" | 让观众短暂变成角色；Hitchcock 常用来切悬念 |
| **Reaction Shot** | 听者 / 观察者对某事件的表情反应 | **叙事核心之一**——Scarface 很多暴力通过 Tony 的反应而不是正面拍摄建立的 |

### 2.4 特殊类

| Shot Type | 定义 | Storytelling Job |
|---|---|---|
| **Detail / Body Fragmentation** | 手、颈、腿、丝袜、指甲等局部（非脸） | 亲密戏 / 欲望戏 的主力；也可压迫感（手被铐的特写） |
| **Mirror / Reflection Shot** | 通过镜面看主体 | 分裂 / 自我观察 / 双重性 |
| **Silhouette / Profile** | 侧影 / 剪影 | 权力关系中的"不可读"；压迫或距离 |
| **Through-the-Gap** | 从门缝 / 百叶 / 窗花 / 人影之间看主体 | 观察 / 偷窥 / 张力——Wong Kar-wai + Chris Doyle 标志性手法 |

---

## 3. Scene → Shot Breakdown 方法论（五步）

把 McKee + Mamet + Hitchcock 综合成一个**可操作流程**：

### Step 1: 找 Scene 的 Value Shift（McKee）

- 开始时角色处境的**值**（e.g. Su Wan："权力掌控 +" / "尊严 -"）
- 结束时的值
- **turning point**：导致值翻转的那个精确瞬间（一句台词？一个眼神？一个动作？一个揭露？）
- McKee 的硬检验：**如果开场值 = 收场值，这个 scene 是 nonevent，不要给它图**

### Step 2: 按 Beat 拆分（McKee 的 beat = action/reaction exchange）

一个 scene 通常 **3–7 个 beat**。每个 beat 是一次 action/reaction：
- Beat 1：A 提出问题（action）/ B 避而不答（reaction）
- Beat 2：A 加压（action）/ B 让步一步（reaction）
- Beat 3：A 给出关键信息（action）/ B 崩溃（reaction）← 这里很可能就是 turning point
- ...

### Step 3: 每个 Beat 指派视觉 Focal Point（Hitchcock）

每个 beat 问三个问题：
1. **此刻最重要的是什么**（人？表情？物件？空间？）
2. **图像尺寸应该多大**（Hitchcock: 尺寸 = 重要性）
3. **观众应该在看谁的反应**（action 的发出者？还是承受者？）

### Step 4: 选 Shot Type 配套（本文 §2 表格）

**典型 coverage pattern**（每种 scene 类型的常见骨架）：

#### 审讯 / 对峙 scene（2 人）
1. Establishing：房间 + 百叶光柱（1 shot）
2. Master：两人同框（1 shot，scene 前 10%，之后不再回）
3. OTS → 单人 MCU on Character A 说话
4. Reverse OTS → 单人 MCU on Character B 反应
5. Insert：桌上的物件（茶杯 / 证据 / 戒指 / 烟灰）
6. 关键 turning point 来临时 → **CU on 主角关键情绪**（Hitchcock rule 触发）
7. ECU on 眼睛 / 手（高亮 tell）
8. Master 回切一次作 closure / 回归现实

**典型 6–9 个 shot 的完整 coverage**。

#### 3 人场（审讯 + 观察者，或三角关系）
规则变化：**不要三人同框作为主力 shot**。把三人拆成：
- 1 个 establishing two-shot（主角 + 对手）
- 1 个 single 反应 shot（第三方在门口 / 窗边观察）
- 之后全部 single / OTS 切换

**第三人不靠画面空间维持存在，而靠 reaction shot + cutaway 维持**。

#### 亲密 / 欲望 scene
- 永远不要 wide shot "全身展示"
- **fragment**：手、唇、肩胛、脖颈、丝袜边缘、指甲、眼睛各拍一张
- 1 张 two-shot 不是整张床的俯拍而是"脸贴脸" MCU
- 插入 reaction shot（一方的脸 vs 另一方的无声反应）
- 参考色戒：李安把性爱拆成**身体碎片 + 脸部反应 + 阴影**，从不"全身展示"

### Step 5: 留白（哪些 beat 不给图）

**不是每个 beat 都值得图**。原则：
- 过渡性 beat（仅推进不 turn 的） → 纯文字，省图像预算
- 重要但**不可见**的 beat（内心 flashback / 信息回忆） → 纯文字
- 图像会破坏想象空间的 beat（极端暴力 / 性高潮的正面） → 让文字做，让 cutaway 做 subtext
- **Tarkovsky 原则**：不是所有瞬间都需要可视化，"沉默"和"省略"也是叙事

---

## 4. Coverage 设计的硬原则（5 条）

### 原则 1：Hitchcock's Rule —— 尺寸 = 重要性

> "The size of the image must equal the importance of the subject at that moment."

实操：
- 此刻 Su Wan 拒绝律师团的提议 → **CU on Su Wan**（不是 wide shot of 律师 + Su Wan + 秘书 + 办公室）
- 此刻 Lin Ze 看到她的红趾甲 → **ECU on toenails**，然后 **ECU on Lin Ze's eyes**（不是 wide shot of 整个审讯室）
- 关键道具揭示 → **insert shot**（不是背景里偶然出现）

### 原则 2：不要多人平分视觉权重

> 默认错：3 人平均分布在画面三等分。
> 正确：1 主 + 1 背影 / OTS + 1 完全不在画面（靠 cutaway 或 reaction shot 出现）

**人数越多，越要靠剪辑而不是构图来维持存在。**

### 原则 3：关键反应永远给独立 CU

> Walter Murch 的 Rule of Six 第一条：**emotion** 是剪辑的最高优先级。

如果一个 beat 里有一个"被改变"的角色——他的反应**必须**独占一张 close-up。不要把它埋在 two-shot 或 master 的背景里。

### 原则 4：对话遵守 shot-reverse-shot + 180° rule

- A 说话 → OTS or single MCU on A
- B 反应 → OTS or single MCU on B（**同一侧**，180° rule）
- 若要打破 180°，必须是**心理断裂时刻**（e.g. 身份反转、背叛揭露）——参考《闪灵》

### 原则 5：重要物体 → Insert

不要把"桌上有一枚戒指"写进 wide shot 的 prompt。这在图像里毫无视觉力。
- **写一个独立的 insert shot**，专门给戒指一个 ECU 画面
- 插入 shot 相对于主动作位置可以是任何地方，但**叙事上它锚定在此 beat**
- 扩散模型的道具特写**命中率远高于**"wide shot 里正确渲染戒指"

---

## 5. 导演方法论 —— 三位大师的具体用法

### 5.1 Alfred Hitchcock —— 尺寸即重要性

Hitchcock 的《精神病患者》浴室谋杀有 **78 个 shot 撑 45 秒**。每个 shot 只干一件事（一把刀、一个尖叫、一道水流、一只眼睛）。观众感受到的暴力完全来自**剪辑的叠加**，从不见一次正面刺入。

**可迁移到 crpg 的 takeaway**：
- **性 / 暴力的"不可视"部分**通过 ECU + reaction + cutaway 建构
- **空间压迫**通过 insert 蚕食建立（先看表，再看手，再看门把）

### 5.2 Ang Lee（色戒）—— Fragment + Withholding

**色戒珠宝店高潮 shot 分析**（基于 ShotDeck 和多篇分析）：

这场戏（约 3 分钟）结构大致如下：

| # | Shot 类型 | 内容 | 叙事任务 |
|---|---|---|---|
| 1 | Wide (rare) | 珠宝店全景 + 路人 | Establishing + **埋伏的刺客混在人群里（观众也要"找"）** |
| 2–5 | POV + reverse | Chia Chi 扫视店内 / 窗外 | 观众代入她的侦查视角 |
| 6 | MCU | Yee 看戒指 | 他进入"专注"状态（脆弱的窗口） |
| 7 | ECU | 戒指 | 核心道具建立—— 她的"信物"vs 他的"告白" |
| 8 | CU | Chia Chi 的脸 | **turning point 的面部反应**——她犹豫了 |
| 9 | Reverse CU | Yee 看她 | 他发现她的犹豫 |
| 10 | High angle wide | 模拟"刺客 POV" | 观众被**实装进刺客位**（共谋感） |
| 11 | ECU | Chia Chi 的嘴唇，"快走" | 关键台词的 visual 高亮 |
| 12+ | Cross-cut Yee 上车 + 刺客未能开枪 + Chia Chi 被捕 | 平行剪辑 | 命运宣判 |

**关键观察**：
- 整场戏**只有 1–2 个 wide shot**。全部信息靠 CU + ECU + POV 建构。
- **Chia Chi 和 Yee 从不平分视觉权重**——此刻谁的命运在旋转，镜头就给谁。
- 戒指作为物件**独立拥有一个 shot**，而不是"背景里出现"。

### 5.3 色戒海报的构图智慧

Lust, Caution 亚版海报（主打亚洲市场）和美版海报都遵循同一原则：**不是合影**。

- **亚版**：Tony Leung（Yee）脸部占据**主视觉**（foreground dominant），Tang Wei（Chia Chi）**被遮脸 / 只显身体 + 绿旗袍轮廓**（背景位置但色彩鲜明）。两人不平分画面。对角线 + 绿色调 + 旗袍轮廓让"lust"与"caution"分别落在两个人身上。
- **美版**：双人同尺寸但**有手臂切开**两人的身体——物理上并置但情感上隔开。

**海报的方法论投射到我们的问题**：
> "压缩一个故事到一张图" ≠ "塞所有角色进画面"。
> 海报选择**遮蔽**、**不平分**、**用色彩和姿态建立层次**，而不是平铺。

**如果我们的 pipeline 只能给一张图做节点封面 → 应该按海报构图思路来**：**一个主角占主要视觉重量，其他角色用符号/局部/色彩存在，而不是平分画面**。

### 5.4 Wong Kar-wai + Christopher Doyle —— 碎片化与犹豫

Doyle 标志性手法：
- **从缝隙里看主体**（门缝、百叶、帘子、人影之间）——建立"偷窥感" / 隔离感
- **ECU 感情图像**（affection-image, Deleuze 术语）——脸部特写成为情绪的本体
- **片段化空间**：角色在同一物理空间里因为光影和景别被割开，**心理上无法沟通**

**crpg 的直接应用**：
- 审讯室戏：Su Wan 和 Lin Ze 绝不用平视双人构图——靠百叶窗光柱、桌面反光、玻璃窗分割，让每张图都有"隔一道什么"的层次
- 亲密戏：Doyle 的 fragmentation 直接可用（手在肩上、唇近耳、眼角余光）

### 5.5 Walter Murch —— Rule of Six（剪辑视角）

六条标准（重要性从高到低，emotion 单独压顶）：

1. **Emotion**（~51%）：这个 shot 传达的情感 right？
2. **Story**（~23%）：推进叙事？
3. **Rhythm**（~10%）：节奏对不对？
4. **Eye-trace**（~7%）：观众视线能流畅过渡？
5. **Planarity**（~5%）：2D 画面内的几何一致？
6. **Spatial continuity / 180°**（~4%）：3D 空间一致？

**Murch 原则**：**可以从下往上放弃**。先放弃空间连续，再放弃 planarity，再放弃 eye-trace… 但**永远不要牺牲 emotion**。

**crpg 的应用**：我们的节点封面选择算法要按这个优先级——"哪张图 emotion 最强 → 就是封面"，不看它是否"最全信息"。

### 5.6 David Mamet —— Uninflected Shots + 并置

Mamet 的极简主义：
- **每个 shot 只做一件事**（uninflected image）
- 不要在一个 shot 里塞情感 + 情节 + 表演 + 道具
- 观众在两个 shot 之间**脑内合成**叙事（Eisenstein 的蒙太奇）

**crpg 的直接应用**：
- 我们的 prompt 每张图的 action moment 段落应该**只写一件事**
- 不要一张图同时"Su Wan 坐着 + Lin Ze 点烟 + Meijie 进门 + 桌上摆着证据"——这是 4 件事
- 拆成 4 张 shot，每张只描述**此刻的视觉焦点**

### 5.7 Tarkovsky —— 沉默即叙事

Tarkovsky 的长镜头哲学提醒我们：**不是所有 beat 都需要图**。
- 如果此 beat 的情绪来自"**时间**"而非"**事件**"——它可能不需要图，或者只需要一张**几乎静止的长镜氛围图**（远景、空间、光、几乎无人）

**crpg 的应用**：
- 允许 daisy 节点标记为 `imageMode: silent`——不生成图，让文字独立叙事
- 这是一种**设计选择**，不是失败

---

## 6. 色戒案例拆解：一整场 scene-to-shot 演示

以《色戒》中 **Yee 第一次独自见 Mrs. Mai（咖啡馆/西餐厅前奏戏）** 为原型，示范 shot breakdown。

### Scene 概述
- **空间**：上海西餐厅，1942
- **人物**：Yee（已婚情报头子）、Chia Chi（伪装成 Mrs. Mai）
- **McKee value shift**：Yee 从"警惕 / 冷" → "动摇 / 被吸引"（价值：控制 → 松动）
- **Turning point**：Chia Chi 点烟时故意让指尖擦过 Yee 的手

### Beat 分解
1. Chia Chi 进入，Yee 已在（Beat 1: 建立两人存在）
2. 寒暄 + 点餐（Beat 2: 表层社交，隐藏张力）
3. Yee 试探性观察她（Beat 3: 他开始怀疑 / 被吸引的双重）
4. 她请求点烟，指尖擦过（Beat 4: **turning point**）
5. Yee 的反应——不动声色但眼神变了（Beat 5: 价值翻转确认）
6. 她的余光捕捉到他的反应（Beat 6: 她知道自己成功了）

### Shot List（李安可能的 coverage，推断 + 可泛化到 crpg）

| # | Shot | 描述 | Beat | Job |
|---|---|---|---|---|
| 1 | Establishing | 西餐厅全景，1942 装饰，冷色调 | 0 | 时空建立 |
| 2 | MCU OTS on Yee | 从 Chia Chi 肩后看 Yee 抬头 | 1 | 他看到她 |
| 3 | Reverse MCU OTS on Chia Chi | 从 Yee 肩后看她走近 | 1 | 她被他看到 |
| 4 | Two-shot MCU | 两人落座，桌面茶杯前 | 1 | 空间 block 确认 |
| 5 | MCU Yee | 点餐中，眼神打量她 | 2 | 他在评估 |
| 6 | MCU Chia Chi | 微笑，视线下垂 | 2 | 她的表演 |
| 7 | Insert | 她的手放在桌面，指甲 | 3 | Visual motif 植入 |
| 8 | CU Yee's eyes | 眼神从她脸到她手 | 3 | 欲望的开始（**Hitchcock 触发**） |
| 9 | Insert | 烟盒被推过桌面 | 4 | 关键道具 |
| 10 | ECU | 她的指尖**擦过**他的手背 | 4 | **turning point 的视觉**：全片关键 |
| 11 | CU Yee | 微一震（jaw tension, 眨眼 hold） | 5 | 价值翻转的反应 |
| 12 | CU Chia Chi | 捕捉到他的反应，嘴角极微上扬 | 6 | 她赢了这一回合 |
| 13 | Two-shot wide | 恢复平静外表，侍者入画 | closure | 回到 status quo 的伪装 |

**总计 13 shots 撑 ~2 分钟 scene**。平均 scene density 很典型。

**如果映射到 crpg 的一个节点**（假设此 scene 是一个 daisy 节点）：
- **Shot list 选 4–6 张**作为节点分镜（不是 13 张，预算有限）
- **必选**：#7 手 insert、#10 ECU 指尖擦过、#11 Yee reaction、#12 Chia Chi reaction
- **可选封面**：#10（turning point 视觉）— 最高 emotion 值

---

## 7. 给 crpg 项目的落地建议

### 7.1 Visual DNA 哪几层需要改

| 层 | 当前状态 | 需要改 |
|---|---|---|
| 1. Style Preamble | OK | **无改动** |
| 2. Aesthetic Axis | OK | **无改动** |
| 3. Character Sheets | OK | **改动**：增加"partial presence sheet"—— 当角色只以手/背影/OTS 出现时的简化 sheet |
| 4. Recurring Motifs | OK | 无改动 |
| 5. Positive Framing | OK | 无改动 |
| 6. Technical Lock | OK | 无改动 |
| 7. Anchor Strategy | OK | 无改动 |
| 8. Direction Layer | OK | 无改动 |
| **9. Shot Design Layer（新）** | **缺失** | **增加**——见 §8 |

### 7.2 数据模型改动

daisy 的每个叙事节点从：

```yaml
node:
  content: "<叙事文本>"
  image_prompt: "<single prompt, 180 words>"
  image_url: "<generated>"
```

改为：

```yaml
node:
  content: "<叙事文本>"
  scene_analysis:                        # McKee step 1–2
    value_shift: "control+ → control-"
    turning_point_beat: 4
    beats: [<beat descriptions>]
  shot_list:                             # McKee step 3, Hitchcock step 3
    - shot_id: 1
      type: "establishing"
      primary_subject: "interrogation room"
      composition: "<brief>"
      beat: 0
      narrative_purpose: "time/place establishment"
      emotion_weight: 0.2
      is_cover_candidate: false
      prompt: "<full prompt composed per §8>"
    - shot_id: 2
      type: "ecu"
      primary_subject: "Su Wan toenails"
      beat: 4
      narrative_purpose: "turning point visual"
      emotion_weight: 0.9
      is_cover_candidate: true
      prompt: "<full prompt>"
    # ... 3–6 shots total per node
  cover_shot_id: 2                       # Murch rule of six: highest emotion
  images: {shot_id: url}
```

### 7.3 生成流程改动

```
daisy 生成节点文本 content
    │
    ▼
Scene Analyst（LLM pass）：
  - 找 value shift + turning point（McKee step 1）
  - 拆 beat（McKee step 2）
    │
    ▼
Shot Designer（LLM pass）：
  - 为每个 beat 指派 focal point + shot type
  - 输出 3–6 个 shot 的 structured list
  - 每个 shot 附 emotion_weight
    │
    ▼
Prompt Composer（现有 Visual DNA stage 2 机制）：
  - 每个 shot 独立调用 Grok Imagine
  - Visual DNA 1–8 层完全复用（字节级共享）
  - 只有"action moment"部分换成**当前 shot 的 focal point + shot type 词汇**
    │
    ▼
Cover Selector：argmax(emotion_weight) → 节点封面
```

### 7.4 前端展示建议

**节点封面**：shot_list 中 `emotion_weight` 最高的那张

**点进去**：显示完整 shot list（类似"故事板视图"）：
- 横向滚动的分镜序列
- 每张 shot 下方标注 shot type（CU / ECU / OTS / Insert）+ narrative purpose
- 鼠标 hover 可见对应 beat 的文本片段

**播放模式**（可选）：把 shot list 当作**纸片动画**——2 秒/张自动切，配合 daisy 的文本 typewriter 效果

### 7.5 一个立即可做的 Action

**本周可落地**：

1. **不改 image model**，不改 prompt 结构骨架（1–8 层全保留）
2. **在节点生成流程中插入"Shot Designer" LLM pass**，输入 content，输出 3–6 个 shot spec
3. **修改 image 调用**：从 `n=1 per node` 变成 `n=3–5 per node`
4. **前端加一个简单的"多图 carousel"组件**，先用最简版展示 shot list
5. **Cover 选择**：先硬编码为 "shot #2 或 #3"（通常是 turning point），下一迭代再接 emotion 打分

**预期效果**：同一个节点从"一张试图讲完一切的图"变成"3–5 张各司其职的分镜"。视觉密度降低，叙事密度提升。

---

## 8. Shot Design Layer 的 Visual DNA §9（YAML schema）

见配套文件 `shot-types-vocabulary.yaml`。以下是注入 visual-dna-system.md 的层定义：

```yaml
# Layer 9: Shot Design Layer （新增）
shot_design_layer:
  scene_analysis:
    value_shift: "<opening value → closing value>"
    turning_point_beat: <int>  # 1-indexed
    beats:
      - beat_id: 1
        description: "<brief action/reaction>"
        is_turning_point: false

  shot_list:  # 3-6 shots per beat group
    - shot_id: 1
      type: "establishing | master | two_shot | ots | mcu | cu | ecu | insert | cutaway | pov | reaction | detail | mirror | through_gap"
      primary_subject: "<who or what>"
      composition: "<brief composition directive>"
      beat_ids: [<which beats this shot serves>]
      narrative_purpose: "<why this shot exists>"
      emotion_weight: 0.0-1.0  # Murch Rule of Six priority
      focal_hierarchy:  # Hitchcock's rule
        primary: "<dominant element>"
        secondary: "<support>"
        absent: "<characters/elements intentionally NOT in frame>"
      gaze_direction: "<where primary subject looks>"
      is_cover_candidate: bool

  selection_rules:
    - "Never show all present characters in one frame unless physical clustering IS the story point"
    - "Key reaction to a revelation = independent close-up (Hitchcock)"
    - "Important object = insert shot (never background)"
    - "Maintain 180° line across shot-reverse-shot sequences"
    - "Allocate 2-3 micro-expression tells per face, not the full list"
    - "Fragmentation over full-body display in intimate scenes"
    - "Cover shot = argmax(emotion_weight), not argmax(information density)"

  director_philosophy:
    reference: "Ang Lee Lust, Caution jewelry-store aesthetic"
    principles:
      - "Withholding: key information lives in ECU + reaction, not wide"
      - "Fragmentation: body as parts not whole"
      - "Through-the-gap compositions for tension"
      - "1 wide per scene max; rest is close/medium/insert"
```

---

## 9. 术语对照（给 prompt writer）

Prompt 里可以直接抄的 shot type 英文词：

- Establishing shot / wide establishing shot
- Master shot / full shot
- Two-shot / cowboy shot
- Over-the-shoulder (OTS)
- Medium close-up (MCU)
- Close-up (CU)
- Extreme close-up (ECU)
- Insert shot / insert close-up
- Cutaway shot
- POV shot / point-of-view shot / subjective shot
- Reaction shot
- Eye-line match
- High angle / low angle / dutch tilt / worm's eye / bird's eye
- Through-the-gap / between blinds / through the doorway
- Mirror shot / reflection shot
- Silhouette / profile
- Body fragment / detail shot

---

## 10. 参考来源

核心研究原始材料（本文档的依据）：

- **Hitchcock 的 Rule**：[No Film School 解析](https://nofilmschool.com/2015/11/hitchcock-rule-help-you-tell-better-visual-stories) —— "size of the image must equal the importance of the subject"
- **Murch 的 Rule of Six**：[StudioBinder 完整解析](https://www.studiobinder.com/blog/walter-murch-rule-of-six/) —— emotion > story > rhythm > eye-trace > planarity > 3D continuity
- **Mamet 的 Uninflected Shots**：*On Directing Film*（书）+ [PremiumBeat 解析](https://www.premiumbeat.com/blog/gutter-editing-and-the-uninflected-shot/)
- **McKee 的 Scene Turn / Beat**：[McKee 官方博客](https://mckeestory.com/do-your-scenes-turn/) + 多篇《Story》书评
- **Shot Coverage 方法**：[StudioBinder Coverage Guide](https://www.studiobinder.com/blog/film-coverage/) + [Shot Reverse Shot Guide](https://www.studiobinder.com/blog/shot-reverse-shot-cutaways-coverage/)
- **Lust, Caution 珠宝店场景分析**：[ShotDeck Blog](https://blog.shotdeck.com/new-shots/building-tension-with-just-a-look-lust-caution/)（搜索索引）
- **Lust, Caution Tony Leung 眼神分析**：[UCLA APC article](https://www.international.ucla.edu/apc/article/79221)
- **色戒海报对比分析**：[Film Experience blog](http://filmexperience.blogspot.com/2007/08/this-or-that-lust-caution.html)
- **Lust, Caution 灯光 / 视觉风格**：[Aithor lighting essay](https://aithor.com/essay-examples/lighting-in-lust-caution-film-by-ang-lee)
- **Wong Kar-wai / Christopher Doyle 视觉哲学**：[Robert Morton cinematographer profile](https://www.robertcmorton.com/cinematographer-christopher-doyle/) + [Film Alert 101](http://filmalert101.blogspot.com/2021/02/love-and-distance-art-of-wong-kar-wai.html)
- **Tarkovsky Sculpting in Time**：[Wikipedia 原书条目](https://en.wikipedia.org/wiki/Sculpting_in_Time) + [Monoskop 全本 PDF](https://monoskop.org/images/d/dd/Tarkovsky_Andrey_Sculpting_in_Time_Reflections_on_the_Cinema.pdf)
- **180° / 30° / Eyeline Match**：[MasterClass](https://www.masterclass.com/articles/understanding-the-180-degree-rule-in-cinematography) + [Learn About Film](https://www.learnaboutfilm.com/film-language/sequence/180-degree-rule/)

---

**研究完成时间**：2026-04-17
**下一步**：实现 Shot Designer LLM pass，前端 carousel 组件，并用"审讯室权力差"故事做 Round 4 测试——同一个节点用旧单图方案 vs 新 shot list 方案对比出图效果。
