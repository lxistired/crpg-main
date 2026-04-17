# Stage 1 Global Planner — Shot List Skeleton

**Story:** `su_wan_interrogation_noir`
**Planner Version:** stage1-global-planner-v1
**Date:** 2026-04-17
**Scope:** 5 nodes · 19 shots total

---

## 全局 Visual DNA 概览

| 维度 | 决策 |
|---|---|
| 美学主轴 | `jpr_urban_ol`（日系都市 OL 写实） |
| 美学副轴 | `wr_noir_cinematic`（西方 noir 电影感） |
| Style Preamble 变体数 | 4（按 value arc 分段切换） |
| 全局 Anchor | 1 张（Su Wan 半身肖像，锁定人物身份） |
| Anchor 应用 shots | 5/19 shots（所有 Su Wan 面部可见的 shot） |
| 主 Aspect Ratio | 16:9（default）+ 2:3（vertical ECU/fragment）+ 1:1（insert）+ 21:9（establishing） |
| 模型 | grok-imagine-image-pro |

### Style Preamble 四变体

| 变体 ID | 应用节点 | 视觉特征 | 摄影师锚点 |
|---|---|---|---|
| `act1_noir_interrogation` | act1_start, act1_choice | 青色阴影 + 深红高光 + 35mm Portra 颗粒 + 霓虹晕 | Gregory Crewdson / Wong Kar-wai |
| `act2_intimate_morning` | branchA2_scene1 | 冷荧光 vs 暖琥珀分裂色调 + 浴室蒸汽 + 白瓷砖 | Nan Goldin / Saul Leiter |
| `act2_nightclub_backstage` | branchB_scene1 | 褪色玫瑰 + 廉价荧光 + 梳妆台球形灯泡 + 香烟烟气 | Nan Goldin backstage / Jim Goldberg |
| `act2_monitor_revelation` | branchB_scene2 | CRT 蓝白主光源 + 一切去饱和 + 扫描线纹理 | Gregory Crewdson / Saul Leiter |

**切换原则：** 每次 style preamble 切换对应一个叙事空间的不可逆转换。审讯室 → 走廊 → 逃亡公寓 / 后台，视觉底色的漂移是 value arc 的图像化。

---

## 角色身份常量（Character Sheets）

**苏晚（Su Wan）**
Chinese woman, 28 years old, shoulder-length straight black hair parted on the side, thin sharp eyebrows, almond-shaped eyes, pale fair skin cool undertone, 170cm, tight black knee-length pencil skirt, sheer black seamed stockings, strappy black high heels or bare feet, red lipstick, minimal makeup.
- 签名 tell：corner-of-mouth twitch + half-lidded eyes
- 无香烟，无宽松服装

**林泽（Lin Ze）**
Chinese man, mid 30s, short slightly unruly black hair, stubble, dark-circled eyes, square jaw, rumpled off-white shirt, loosened charcoal tie, dark trousers.
- 签名 tell：jaw tension + Adam's apple swallowing once（计作 1 个 compound tell）

**梅姐（Meijie）**
Severe Chinese woman, early 50s, lacquered black chignon with silver streaks, emerald cheongsam slit to thigh.
- 签名 tell：slow blink hold
- **香烟 signature：仅在梅姐出现的 shot 中激活**（Class E bug 防范：cigarette 绝不注入 Direction Layer）

### 高危 Motif 注册表

| Motif | 危险等级 | 防护机制 |
|---|---|---|
| 长筒丝袜/thigh-high stocking | Class D | Layer 10 Layered Visibility Rule 强制启用 |
| 香烟/cigarette | Class E | 仅梅姐 in-frame 时激活，其他 shot 硬隔离 |
| 舌头/tongue wetting | Class C | FORBIDDEN TELL，任何情况禁止写入 prompt |
| 隐喻性身体描述 | Class C | 改写为具体肌肉描述，禁用"like"/"as if" |
| 镜面反射 | 低风险 | 需显式说明镜子/玻璃材质，防止模型默认空白墙 |

---

## Shot List 详细表

### node: act1_start
**McKee Value Shift:** 审讯者权力 + → 猎物反转（被审）
**Style Preamble:** act1_noir_interrogation
**Shot 数量:** 5
**Cover Shot:** act1_start_04（emotion_weight = 0.93）

| Shot ID | Type | Primary Subject | Beat | EW | Ratio | Anchor | 高危 Motif |
|---|---|---|---|---|---|---|---|
| act1_start_01 | establishing | 审讯室空间 | 1 | 0.25 | 21:9 | no | 无 |
| act1_start_02 | ecu | 酒红趾甲 + 丝袜边缘 | 2 | 0.80 | 2:3 | no | thigh-high stocking (Class D) |
| act1_start_03 | ots | 从林泽肩后看苏晚 | 3 | 0.65 | 16:9 | yes | 无 |
| act1_start_04 | reaction | 林泽被捕获 CU ★封面 | 4 | 0.93 | 16:9 | no | 无 |
| act1_start_05 | two_shot | 双人新平衡 master | 5 | 0.55 | 16:9 | yes | 无 |

**Shot 决策理由：**
- `_01` 纯空间建立：审讯室是"制度笼子"，先看笼子再看里面的人。极宽 21:9 强调压迫空间。
- `_02` Hitchcock 焦点物件：趾甲不能出现在 wide shot 里（研究结论：宽景下道具像素不足、叙事力为零）。独立 ECU 让观众和林泽共享同一个凝视物件。**Layer 10 强制激活。**
- `_03` OTS 把观众放进林泽的观察者位置——这是 180° 轴线的建立，为 _04 的反转做准备。
- `_04` Turning point 专属 CU：苏晚开口，林泽被捕获。价值翻转必须在独立 CU 里（Hitchcock R2）。最高 EW = 封面。
- `_05` 两人 master 收尾：从 wide → close → wide 的经典括号结构。新的权力平衡。

---

### node: act1_choice
**McKee Value Shift:** 职业服从 + 个人渴望 → 不可逆抉择（撕裂）
**Style Preamble:** act1_noir_interrogation（延续，因为空间延续）
**Shot 数量:** 3
**Cover Shot:** act1_choice_03（emotion_weight = 0.88）

| Shot ID | Type | Primary Subject | Beat | EW | Ratio | Anchor | 高危 Motif |
|---|---|---|---|---|---|---|---|
| act1_choice_01 | through_gap | 苏晚走廊远处身影 | 1 | 0.55 | 16:9 | no | 无 |
| act1_choice_02 | insert | 震动的手机 | 2 | 0.72 | 1:1 | no | 无 |
| act1_choice_03 | cu | 林泽面孔——撕裂瞬间 ★封面 | 3 | 0.88 | 16:9 | no | 无 |

**Shot 决策理由（为什么只用 3 shots）：**
这是"幕间转折"节点，叙事功能是 decision point，不是 scene。McKee 原则：过渡性的 value shift 不需要完整 coverage。3 shots 精准服务于"等待-选择-承担"三个 beat：
- `_01` 苏晚的等待：through_gap 隔离感 = 选择的距离感。酒红色作为路标（cross-node motif echo from _02）。
- `_02` 选择的物质化：手机震动是选择本体。独立 insert 让这个物件拥有自己的叙事重量（Hitchcock R3）。
- `_03` 脸部的撕裂：分割光（一半暖一半冷）视觉化内心的两个自我。不需要看苏晚——她已经在 _01 里了。

---

### node: branchA2_scene1
**McKee Value Shift:** 制度框架内逃脱 → 共犯关系确立（无路可退）
**Style Preamble:** act2_intimate_morning（**切换**：进入私人空间，视觉语法翻新）
**Shot 数量:** 4
**Cover Shot:** branchA2_scene1_04（emotion_weight = 0.87）

| Shot ID | Type | Primary Subject | Beat | EW | Ratio | Anchor | 高危 Motif |
|---|---|---|---|---|---|---|---|
| branchA2_scene1_01 | mirror | 苏晚镜中取出 U 盘 | 1 | 0.68 | 2:3 | yes | 无 |
| branchA2_scene1_02 | insert | U 盘 + 酒红指尖 | 2 | 0.65 | 1:1 | no | 无 |
| branchA2_scene1_03 | detail | 丝袜在白瓷砖上的影子 | 2 | 0.78 | 2:3 | no | thigh-high stocking (Class D, shadow framing) |
| branchA2_scene1_04 | reaction | 林泽——无路可退 ★封面 | 3 | 0.87 | 16:9 | no | 无 |

**Shot 决策理由：**
- `_01` Mirror shot：浴室是 branchA2 的核心空间，镜子是"双重身份"的标志性构图。苏晚的 reflection 和真实同框——执行者与逃亡者是同一个人。竖幅 2:3 让镜面构图自然展开。
- `_02` Insert：U 盘是 turning point 道具。**酒红色指甲出现在 hands（cross-node echo Motif A：feet→hands，欲望物件→行动工具）**。
- `_03` Detail：这张是给"黑丝袜在白色地板上"的影子——不是正面展示，是体积感和光影感。白色瓷砖 vs 黑丝袜的高对比 = 私奔场景的视觉清冷。**Layer 10 即使在影子帧也必须写出分层描述。**
- `_04` Reaction：林泽的"无路可退"必须在独立 CU 里。冷荧光打在脸上（act2_intimate_morning 变体的 key）——没有审讯室的暖光保护，他没有"警察"的角色可以躲进去了。

---

### node: branchB_scene1
**McKee Value Shift:** 法律追查框架 → 权力根性揭露（赵明远是导演）
**Style Preamble:** act2_nightclub_backstage（**切换**：廉价后台 vs 台前奢华）
**Shot 数量:** 4
**Cover Shot:** branchB_scene1_03（emotion_weight = 0.89）

| Shot ID | Type | Primary Subject | Beat | EW | Ratio | Anchor | 高危 Motif |
|---|---|---|---|---|---|---|---|
| branchB_scene1_01 | through_gap | 从后台门缝看梅姐 | 1 | 0.60 | 16:9 | no | cigarette（Class E，梅姐 in-frame，激活） |
| branchB_scene1_02 | ots | 从苏晚肩后看梅姐打量林泽 | 2 | 0.62 | 16:9 | no | cigarette（梅姐 in-frame，激活） |
| branchB_scene1_03 | reaction | 林泽案子翻转 CU ★封面 | 3 | 0.89 | 16:9 | no | jaw-drop Class C（写法注意） |
| branchB_scene1_04 | cutaway | 化妆台烟灰缸 subtext | 3 | 0.40 | 1:1 | no | ashtray 香烟残根（Class C，写"熄灭的"） |

**Shot 决策理由：**
- `_01` Through-gap：梅姐是权力掮客，"她在门后"而观察者在门外——Wong Kar-wai 偷窥构图建立权力等级（被观察者并不在意观察者）。**这是本节点唯一合法激活 cigarette signature 的 shot。**
- `_02` OTS（苏晚肩后看梅姐）：三角关系 coverage。把林泽从画面中移除，让梅姐的"眼神评估林泽"完全靠她的 gaze direction 完成。遵循"3 人场不三人同框"规则。
- `_03` Lin Ze Reaction CU：案子的认知逆转（cross-node echo Motif C：与 act1_start_04 的反应 CU 对应——欲望开裂 vs 信念崩溃）。后台褪色玫瑰壁纸在背景里——空间身份的图像化。**下巴微开要写成肌肉描述而非字面"嘴巴张开"（Class C）。**
- `_04` Cutaway：给节奏呼吸空间。梅姐见过太多秘密，烟灰缸是她的 subtext。**香烟是残根、熄灭的——不是燃烧中的（Class C）。**

---

### node: branchB_scene2
**McKee Value Shift:** 老王死亡是意外（既成事实）→ 老王死亡是谋杀（认知框架崩塌）
**Style Preamble:** act2_monitor_revelation（**切换**：CRT 蓝白光是全局 style 的最大偏离，象征认知崩塌）
**Shot 数量:** 3
**Cover Shot:** branchB_scene2_03（emotion_weight = 0.82）

| Shot ID | Type | Primary Subject | Beat | EW | Ratio | Anchor | 高危 Motif |
|---|---|---|---|---|---|---|---|
| branchB_scene2_01 | pov | 林泽 POV 看监控屏 | 1 | 0.70 | 16:9 | no | 无 |
| branchB_scene2_02 | ecu | 林泽颤抖的手 | 2 | 0.85 | 2:3 | no | 无 |
| branchB_scene2_03 | reaction | 苏晚见证 CU ★封面 | 3 | 0.82 | 16:9 | yes | 无 |

**Shot 决策理由（为什么只用 3 shots）：**
这是揭露 scene（revelation_scene pattern）。3 shots 足够：看见→身体反应→见证者。压缩感本身就是情感设计——没有建立空间的喘息，直接进入认知崩塌。
- `_01` POV：观众代入林泽看见老王的主观视角。监控画面质量（有意模糊、时间戳）防止扩散模型试图正确渲染一个不存在的 named character。
- `_02` ECU（手）：情绪通过身体物理化。**cross-node echo Motif B：act1_choice_02（手握手机=准备选择）→ branchB_scene2_02（手颤抖=真相击穿）。** 竖幅 2:3。
- `_03` Su Wan Reaction：这是全故事里苏晚第一次作为"见证者"而不是"猎人"出现。CRT 蓝白光打在她脸上——她和林泽沐浴在同一个真相之光里。**cross-node echo Motif D：角色间的 watcher/watched 逆转。** Cover shot（虽然 EW 略低于 _02，但它承载了权力关系的语义反转，情感维度更复杂）。

---

## 跨节点视觉呼应（Cross-Node Echoes）

| Echo ID | From | To | Motif | 叙事功能 |
|---|---|---|---|---|
| Motif A | act1_start_02（酒红趾甲 ECU） | branchA2_scene1_02（酒红指尖 insert） | 同一颜色从足部到手部 | 苏晚从"欲望物件"变成"行动主体"——颜色不变，角色功能翻转 |
| Motif B | act1_choice_02（手机 insert） | branchB_scene2_02（颤抖的手 ECU） | 林泽的手：准备→崩溃 | 林泽的手作为情感地震仪——选择的张力 vs 真相的重量 |
| Motif C | act1_start_04（林泽被欲望捕获） | branchB_scene1_03（林泽被真相击穿） | 相同 CU 格式，不同情感内容 | 电影语法：观众无意识对比，感受人物弧——从欲望开裂到信念崩溃 |
| Motif D | act1_start_04（苏晚是主动的观察者） | branchB_scene2_03（苏晚是被动的见证者） | Watcher/watched 角色逆转 | 权力关系的第二次逆转：审讯室里苏晚掌控，后台里她放下武器关切林泽 |

---

## Shot Type 分布统计

| Shot Type | 数量 | 节点分布 |
|---|---|---|
| reaction | 5 | act1_start×1, branchA2×1, branchB_s1×1, branchB_s2×1, act1_start×cover |
| insert | 3 | act1_choice×1, branchA2×1, branchB_s1 cutaway implicit |
| ecu | 2 | act1_start×1, branchB_s2×1 |
| through_gap | 2 | act1_choice×1, branchB_s1×1 |
| ots | 2 | act1_start×1, branchB_s1×1 |
| detail | 1 | branchA2×1 |
| mirror | 1 | branchA2×1 |
| pov | 1 | branchB_s2×1 |
| two_shot | 1 | act1_start×1 |
| cu | 1 | act1_choice×1 |
| establishing | 1 | act1_start×1 |
| cutaway | 1 | branchB_s1×1 |
| **total** | **21** | 19 unique shots（部分 type 合并计） |

**设计原则验证：** 19 shots 里仅 1 个 establishing。rest 全是 close/medium/insert/reaction——符合方法论"R8: ≤1 wide per scene"。

---

## 预算汇总

| 项目 | 数量/成本 |
|---|---|
| 总 shots | 19 shots across 5 nodes |
| Anchor 生成 | 1 shot |
| use_anchor = true shots | 5 |
| Style preamble 变体 | 4 |
| 跨节点视觉呼应 | 4 |
| 预计图像成本 | 19 × $0.07 = **$1.33** |
| + Anchor 生成 | 1 × $0.07 = **$0.07** |
| 预计 Specifier 成本（Haiku） | 19 × ~$0.003 = **~$0.06** |
| **总预计成本** | **~$1.46** |

---

## 与 R5 的对比

| 维度 | R5 | Stage 1 Planner |
|---|---|---|
| 节点覆盖 | 1 node（act1_start） | 5 nodes |
| Shot 数量 | 5 shots | 19 shots |
| Style preamble 切换 | 隐式单一 | 4 显式变体，按 value arc 切换 |
| 跨节点 motif echo | 无（单节点） | 4 个系统性 motif echo |
| Aspect ratio 策略 | 3 个 ratio（ad hoc） | 5-ratio 系统，按 shot type 对应 |
| Meijie cigarette 防护 | 未显式规定 | 每张 shot 显式标注激活/不激活，Class E 硬隔离 |
| Layer 10 丝袜规则 | R5 才发现并修复 | 预装进骨架，所有涉及丝袜的 shot 标注 |
| 覆盖 branch | 仅主干 | branch A（私奔）+ branch B（后台/揭露）均覆盖 |

**进步核心：** R5 是单 scene 的实证测试，这份规划把方法论的所有经验教训系统性地预装到 19-shot、5-node 的更大 scope 里，并通过 4 个 cross-node echo 将孤立的 shots 连接成真正的"电影语法序列"。
