# Session Handoff —— 2026-04-17 晚场（compact 后 → 结束）

接本文件 + `SESSION-HANDOFF-2026-04-17-PM.md` + `MEMORY.md` 恢复上下文。

---

## 今晚到底做了什么

从"图像方法论还没形成"→"Director skill 成熟可用"的全过程，~6 小时，$12 累计 API 花费，200+ shots。

### 关键里程碑

1. **VGAI 方法论正式建立**（5 轮实证，113 shots，$6.30）
   - v1 (22) 单角色 × 框位矩阵，发现 4 种 failure mode
   - v2 (21) 多角色 + 新属性 + 姿势，发现 Modes 5-7
   - v3 (28) 环境/光照/场景多样性，发现 Modes 8-9
   - v4 (18) 叙事时刻 + 特写泛化
   - v5 (6) 腿边界（leg-foot 跨 anchor）

2. **9 种 Grok Failure Mode 全部捕获并有图像证据**
   - Mode 1 Framing Expansion
   - Mode 2 Attribute Drop
   - Mode 3 Composite Cheating
   - Mode 4 Proxy Substitution
   - Mode 5 Anatomical Relocation
   - Mode 6 Wardrobe Modification
   - Mode 7 Pose Rewrite
   - Mode 8 Lighting Rewrite
   - Mode 9 Mutex Split

3. **Director skill 打包完成**（`skills/director/`）
   - SKILL.md <500 words 10 原则
   - 7 references（vgai / framing-map / shot-grammar / grok-constraints / schema / heuristics / rationalization-counters）
   - 2 examples（worked-example + Kai 最小 character sheet）
   - 项目数据与 skill 解耦（`projects/crpg-noir/character-sheets/su_wan.yaml`）

4. **通用性验证通过**
   - 镜廊 Mira（fresh character，子代理自己写 sheet）→ 8 shots 质量
   - Su Wan 信封 (8) + 长夜腿脚 (16) → 全部过 banned-phrasing lint
   - 子代理甚至主动抓到 sheet 里我留的隐藏违规

5. **v2.1 continuity-cue 规则**
   - 发现：feet_ecu + 只注入 stocking_toes → 渲染成短袜
   - 根因：跨 anchor 服装被 VGAI 切后，幸存 anchor 的 value 没有"延续"事实
   - 修复：加 `"continues seamlessly up past the ankle onto the leg above the frame"` 事实陈述
   - 推广：任何跨 ≥2 区域服装（pantyhose / 长手套 / 高领）都适用此 counter

---

## Skill 核心原则（10 条）

1. Base 永远写 — 区域独立身份
2. Grooming 跟角色走 — 持久，可被 state 显式 remove
3. Wardrobe 每 shot 挑一个 named state，无 default
4. VGAI gate — attr.anchor ∈ framing.visible_regions
5. 默认 KEEP 于不确定 pose — Grok 按 anatomy 决定
6. Fact over instruction — 正面事实，禁绝对否定
7. Pose 不抑制 — 想隐藏就不写
8. Mutex 二选一 — 组装时决，不留给渲染
9. Grok 硬约束 — 无 Dutch angle / ≤2 人 gaze / mirror 不靠 / aspect ratio 白名单
10. Shot 语法节奏 — WS/MS/CU/ECU 混排，情感 CU+reverse

---

## Banned phrasings（写进 counters）

永远不在 attr value 或 final_prompt 里写：
- `NOT X` / `never Y` / `without Z`
- `hidden` / `covered by` / `despite`
- `every toe` / `on each X` / `at the tips`
- `hint of red through` / `visible beneath` / `showing under`
- `her signature` / `her default`
- `Dutch angle` / `tilted camera`

---

## 重大方法论沉淀（未来跨 AI / 跨项目适用）

1. **Visibility-Gated Attribute Injection (VGAI)** —— 属性 anchor ∩ framing 可视 = 注入条件
2. **Grooming vs Wardrobe 分层** —— 持久身体标记 ≠ 情境穿搭
3. **Cross-anchor continuity cue** —— 跨区域服装在 ECU 幸存部分必须陈述画外延续
4. **"写属性 = 渲染承诺"** —— pose/cover/light 都不是抑制器
5. **Default-KEEP 优于保守 drop** —— 过注入代价可控，false-drop 静默丢信号
6. **Principle-first 优于 Example-first** —— skill 应编码原则，case 是原则的应用

---

## 今晚新增文件清单

```
skills/director/
  SKILL.md                                             ← <500w 主入口
  references/
    vgai.md                                            ← VGAI 规则 + 9 modes
    framing-region-map.yaml                            ← 可视区域查表
    shot-grammar.yaml                                  ← 分镜词汇 + 可靠度
    grok-constraints.md                                ← Grok 硬限 + 允许 aspect ratio
    character-sheet-schema.yaml                        ← 纯 schema
    narrative-heuristics.md                            ← 叙事→分镜启发式
    rationalization-counters.md                        ← 禁忌话术 + 通用 counter 表
  examples/
    character-sheet-example.yaml                       ← Kai bartender（generic，非项目角色）
    worked-example.md                                  ← Lian paragraph→3 shots

projects/crpg-noir/
  character-sheets/su_wan.yaml                        ← 项目数据（与 skill 解耦）

research/pipeline-simulation/
  vgating-test/                                        ← v1 22 shots
  vgating-v2-validation/                               ← v2 21
  vgating-v3-scenes/                                   ← v3 28
  vgating-v4-narrative/                                ← v4 18
  vgating-v5-legboundary/                              ← v5 6
  director-test/ director-skill-e2e/                   ← 导演 skill e2e 1+2
  director-legs-feet-e2e/ v2/ v12/                     ← 腿脚专项 3 轮
  final-story/                                         ← "The Informant" 18 shots
  skill-generalization-test/                           ← 今晚泛化：Mira 8 + SuWan 8 + SuWan 腿脚 16
```

---

## 下次进入的 next actions

**按优先级**（方法论稳了，现在是产品 / 架构）：

1. **进入产品代码阶段** —— fork daisy → crpg/app，加 3-pass pipeline（Story Architect + Director skill + Image Batch）。参照 `STRATEGIC-REVIEW-v2-2026-04-17.md` 路径 Y。

2. **文字侧方法论 pilot** —— 类比图像侧的实证路线，对 Sonnet/Grok 文字输出做方法论压力测试（McKee 应用 / Genre router / 诗意模式温度 0.8 / 露骨度路由）。

3. **Q4-1 ~ Q4-7 架构决策** —— 见 `memory/project_crpg_architecture_pending.md`
   - Shot Director LLM 模型选（Sonnet / Haiku / Grok）
   - 异步 vs 同步生成
   - Carousel 前端交互
   - 数据契约（story.md / shot_list.json / image bundle）
   - 定价（按 shot / 按 scene / 按 story / 订阅）
   - 合规层（18+ / GeoIP / 审计）
   - 发布流（创作者自发布 vs 平台审核）

4. **纯享版 CDN 数据格式** —— 预生成故事的 JSON schema

5. **BYOK 工程化** —— key 存储（客户端 or session） / 限额 / 用户 API 账单责任切割

---

## 累计成本

- 上午 session（PM 之前）: ~$1.4 (Grok R1-5 + retries)
- 下午 session: $3.8 (pipeline simulation v1 v2 + anime + fal 全套 SOTA + GPT)
- 晚上 session: ~$7（VGAI v1-v5 + Director skill e2e × 3 + generalization × 2 + 15/16 重测）
- **一日总计: ~$12.2 API + $0 其他 = 一天做出一套完整图像方法论**

---

## Git 状态

- Branch: `brainstorming`
- 最近 commits（倒序）:
  - `09f7949` Director skill v2.1: cross-anchor continuity cue rule
  - `552763b` Director skill v2 legs/feet validation
  - `a708e1e` Director skill v2 — principle-based refactor
  - `2dbd943` Director skill v1.3: flip sub-anchor gate default
  - `b2605b0` Director skill v1.2 full legs/feet retest
  - `51cdbf4` Director skill v1.2: no absolute negations
  - `dcad398` Director skill v1.2: fix sole-of-foot red pollution
  - `d8603be` legs/feet e2e surfaces Modes 8-9
  - `62479bd` VGAI round 3 Modes 8-9
  - `db3b99c` VGAI validation round 2
  - `7ac0a96` VGAI methodology test: 22 shots
  - 再往前是下午的 fal/gpt 测试

---

## 本文件落盘后

下一步新开 brainstorming session，讨论**产品代码启动路径或其他下一优先级**。本文件 + MEMORY.md 足以恢复上下文。
