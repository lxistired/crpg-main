# Director 5 候选模型对比（中文）

测试场景：Su Wan 下班出写字楼 → 花店看花 → 陌生男递名片 → 离开。6 shots（WS/MS/ECU/CU/ECU/back_reveal）。

## 场景 A（花店公共场景）VGAI 合规度

| 模型 | T | VGAI 违规数 / 6 | 具体错误 |
|------|---|-----------------|---------|
| **Sonnet 4.6** | 0.6 | **0** | 全部正确（已封账户，今天无法再跑） |
| **DeepSeek V3.2** | 0.6 | **1** | shot 6 mutex 冲突：`stocking_toes` 和 `black_ankle_boots` 同时注入（它们互斥）。另外 shot 2 和 shot 6 都"过度保守"丢了 `red_fingernails`，违反 default-KEEP 原则 |
| Grok 4.20 | 0.6 | 2 | shot 2（在 MS 里塞了 leg+foot attr），shot 6（丢了 red_fingernails） |
| Grok 4.20 | 0.3 | **3** | shot 1（在 WS 里塞了 wardrobe），shot 2（MS 塞腿），shot 6（丢 red_fingernails）—— **低温反而更糟** |
| MiniMax M2.7 | 0.6 | schema 混乱 | 把 base 身份（"bright_brown_eyes" / "fair_skin" / "long_black_hair"）当成 injectable attrs，pose 元素（"nervous_expression"）也当 attr —— 对 schema 理解错误 |

## 关键 shot 中文翻译对比

### Shot 6 — back_reveal_walking（离开背影）

这是最难的一 shot：框位包括 torso_back/hand/leg/foot，所以能注入 skirt+tights+boots+fingernails，应**丢掉** red_lipstick 和 red_toenails（靴子遮脚背）。

**DeepSeek V3.2**
> 中景长镜头，背影揭示，一位中国女性长黑发，穿黑色包臀裙、黑丝连裤袜、黑色踝靴，从花店前转身走开，傍晚街道，电影感。
>
> ❌ 注入了 `stocking_toes` + `black_ankle_boots` —— **mutex 冲突**
> ❌ 丢了 `red_fingernails` 理由"不是主要细节" —— 过度保守

**Grok 4.20 T=0.6**
> anime 风格，28 岁华人女性 Su Wan 背影，过肩黑发飘动，黑色包臀裙，黑丝连裤袜，黑色踝靴，快步下地铁台阶，back_reveal_walking 镜头。
>
> ❌ 丢了 `red_fingernails`

**Grok 4.20 T=0.3**
> 背影中景，28 岁中国女性 Su Wan 长黑发，穿黑色包臀裙、黑丝连裤袜、黑色踝靴，优雅自信离开，地铁环境，自然光，电影构图。
>
> ❌ 丢了 `red_fingernails`（同上）

**MiniMax M2.7**
> 背影全身，优雅中国女性走开，长黑发过肩，黑色包臀裙，黑色踝靴，手提小包，街道，**金色阳光**，腿部有运动模糊暗示步速。
>
> ❌ 丢了 `sheer_black_tights` 理由"被裙子遮住到大腿"—— 但 pencil skirt 膝上沿，黑丝下半段应该可见。**违反事实**
> ❌ 把 camera_framing 填错（`full_body_standing`，应该是 `back_reveal_walking`）
> ❌ 丢了 `red_fingernails`

**Sonnet 4.6**（已封账户，今天无法重跑，引用旧记录）
> 背影：Su Wan 长黑直发中分飘动，穿包臀裙勾勒体态，黑丝覆盖双腿，黑色细跟踝靴敲人行道。右手垂身侧握白名片，指上红指甲油可见。傍晚城市街，温暖灯柱模糊行人，宽幅背影镜头，电影氛围，周围运动模糊。
>
> ✓ 正确保留 `red_fingernails`（手在画面）
> ✓ 加 continuity cue（"黑丝覆盖双腿"）

---

### Shot 2 — MS 花店

框位 `[face, ear, neck, torso]`。应注入 skirt + lipstick + earring；**不该**注入 leg/foot。

**DeepSeek**：✓ 正确（skirt + lipstick），但不必要地丢了 red_fingernails
**Grok T=0.6**：❌ 塞了 sheer_black_tights + black_ankle_boots
**Grok T=0.3**：❌ 塞了 sheer_black_tights  
**MiniMax**：✓ 结构对但把 base 当 attr 注入
**Sonnet**：✓ 完美

---

## 场景 B1 / B2（adult）行为对比

| 模型 | Scene B1 (mild 余韵) | Scene B2 (explicit 床戏) |
|------|---------------------|-------------------------|
| **Sonnet 4.6** | 账户被封无法测 | 账户被封无法测（Anthropic AUP 会直接拦） |
| **DeepSeek V3.2** | ✓ 完整 6 shots，$0.003 | ✓ 完整 6 shots，$0.003，**无 refusal**，正确处理 state.removes 删红唇 |
| **MiniMax M2.7** | ✓ 完整，$0.006 | ✓ 完整，$0.004（较短） |
| **Grok 4.20** | 没单独测 | 没单独测（但之前 anime 沙发 bonus 证明 Grok 接受 adult） |

---

## 综合评分

| 维度 | Sonnet 4.6 | DeepSeek V3.2 | Grok 4.20 | MiniMax M2.7 |
|------|-----------|---------------|-----------|--------------|
| **VGAI 合规** | ★★★★★ | ★★★★ | ★★★ | ★★ |
| **Schema 遵守** | ★★★★★ | ★★★★ | ★★★★ | ★★ |
| **Continuity cue** | ★★★ | ★★ | ★★ | ★ |
| **细节层次** | ★★★★★ | ★★★ | ★★★ | ★★★ |
| **Adult 场景** | ✗ 封 | ★★★★★ | ★★★★ | ★★★★ |
| **成本**（6 shots） | $0.034 | **$0.001-0.003** | $0.009 | $0.002-0.006 |
| **速度** | 32s | 10-30s | 6-9s | 40-45s |
| **可用性**（账户风控） | ✗ 封账户 | ✓ | ✓ | ✓ |

## 结论

**DeepSeek V3.2 是最现实的 Director 选择**：
- VGAI 合规仅次于 Sonnet（1 违规 vs 0）
- Schema 遵守严格（完整 JSON、reason 陈述清晰）
- **Adult 场景全通过不 refuse**
- **成本 $0.001-0.003 per 6 shots**，Sonnet 的 1/30，Grok 的 1/9
- 无账户风控风险
- 中文原生，对"黑丝/红唇"等中文领域词有直接理解

**问题**：
- 偶尔过度保守（default-KEEP 违反）—— 可在 skill 的 rationalization-counters.md 里加一条针对 DeepSeek 的 nudge
- mutex 偶尔违规 —— 可加严格的"组装前 mutex 断言"pre-check

**可行架构**：
- Director orchestrator = **DeepSeek V3.2**
- 文字生成 tool（诗意/克制） = DeepSeek V3.2 本身（它完全能写文学性段落，见 script 测试）
- 文字生成 tool（露骨） = Grok 4.20（已测可用）或 DeepSeek V3.2 本身
- 图像生成 tool = Grok Imagine Pro via xAI

**不再需要 Sonnet**。即使账户解封，它在成人场景下本就 refuse，对我们没价值。
