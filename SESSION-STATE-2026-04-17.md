# crpg Brainstorming Session State —— 2026-04-17

**生成时间**：2026-04-17
**用途**：本次 Claude Code session 的完整状态 snapshot。Session 因需重启跑 /ultrareview 而中断，重启后可用这份文件 + MEMORY.md 快速恢复上下文。

---

## 一、项目定位（已确认）

**crpg = daisy 的 v2 演进 + 独立新项目**
- 继承 daisy 的叙事方法论（McKee 六条硬约束 + 两步生成 + 诗意模式 + 三档细节等）
- 扩展为成人向（18+，Literotica/AO3 成人区路线，合法创作）
- 技术栈和产品形态重新设计（daisy 单一 Sonnet → crpg 双模型 + 图像）

**产品形态（Q2 = C 双模式）**：
- **纯享版**：**零生成、零付费、完全静态**，只加载创作者预生成的故事 bundle，CDN + SSG
- **创作者版**：继承 daisy 可视化画布，承担所有生成成本
  - **BYOK**（用户自备 xAI/OpenRouter key）或 **平台付费**（用我们的 key，定价形态待定）

---

## 二、工程硬红线（平台必须有）

1. 18+ 年龄门（首次进入显式确认）
2. 绝对禁区：未成年人 / 真人身份 / 非自愿
3. 地区合规（GeoIP soft-block）
4. 审计可追溯（prompt + model + 输出摘要入库）
5. 模型侧合规（只用 API 条款允许 NSFW 的模型）

---

## 三、模型策略（已确认）

### 文字模型池（双模型）
- **Sonnet**（Claude Sonnet 4.6，继承 daisy）：克制/文艺向、暗示路线
- **Grok**（xAI grok-4.20 系列）：露骨路线
- 通过 OpenRouter 或 xAI 直连
- **诗意模式温度**：daisy 原 0.9 → 新项目 **0.8**（用户明确）

### 图像模型（已测通）
- **主通道**：xAI Grok Imagine Pro（`grok-imagine-image-pro`）—— 已验证 API 直连可用，无订阅要求
- **基础版**：`grok-imagine-image`（便宜 3.5×，但细节差）
- **视频未来**：`grok-imagine-video`（储备）
- **价格**：Pro $0.07/张，Base $0.02/张
- **API**：`POST https://api.x.ai/v1/images/generations` OpenAI 兼容
- **能力边界**：无 seed / 无 negative_prompt / 无 cfg_scale，有 `image_url`（image-to-image）和 aspect_ratio（13+ 种）

---

## 四、已落盘的方法论资产（核心护城河）

### /Users/lxxxxxx/个人项目/crpg/assets/daisy-narrative-core/

**daisy 叙事核心（继承）**：
- `prompts-v3.ts / v4.ts / v6.ts` — 原文 daisy system prompts
- `pipeline-comparison.md` — V3/V4/V6 对比
- `mckee-full-framework.md` — McKee 22 项原理 vs daisy 采用率
- `detail-and-poetic-modes.md` — 诗意/细腻/极致/诗意模式机制
- `design-rationale.md` — daisy 原作者的设计拆解
- `result_anti_melodrama.yml` — V6 反套路样例
- `example-story-镜廊杀局.md` — daisy 生成故事示例

**补充的（在 daisy 之上）**：
- Genre / Antagonism / Climax 三条 McKee 原则补入（见 memory）
- `visual-aesthetics.yaml` — 24 子派视觉美学分类（Agent B 研究）
- `visual-aesthetic-axes.md` — 6 大类美学深度解析

**电影镜头方法论（全新）**：
- `shot-design-system.md` (27KB) — 色戒 + Hitchcock + Mamet
- `shot-types-vocabulary.yaml` (24KB) — shot type 词汇表
- `visual-dna-system.md` — **10 层 Visual DNA**（从 7 层演进到 10 层）
- `text-to-image-bug-taxonomy.md` — **5 类 T2I bug 分类学**

---

## 五、Visual DNA 10 层（已固化）

| Layer | 作用 | 状态 |
|---|---|---|
| 1. Style Preamble | 技术美学底座 | 按故事阶段可切换（bonus 晨光图证明） |
| 2. Aesthetic Axis | 从 24 派选 | 故事级固定 |
| 3. Character Sheets | 角色外观 + partial_presence_rule | 每场景按需注入 |
| 4. Recurring Motifs | 分层（every-frame / scene-level / shot-level） | 每帧按层级过滤 |
| 5. Positive Framing | 禁忌转正向（因无 negative_prompt） | 每帧注入 |
| 6. Technical Lock | aspect / resolution / model | 故事级固定 |
| 7. Anchor Strategy | image_url 做 style transfer | 全故事 1 张 anchor |
| 8. Direction Layer | 行动瞬间 + 微表情 + 摄影参考 | 字节级固定 |
| 9. Shot Design Layer | 每 beat 弹性 shot 数（0-N，Director 决定） | 按 beat 决策 |
| 10. Layered Garment Visibility | High-Prior 服装消歧 | 仅涉及 High-Prior 服装时触发 |

---

## 六、5 类 T2I Bug Taxonomy（已固化）

| Class | 症状 | 最难度 | 机制化层 |
|---|---|---|---|
| A. Identity Drift | 身份漂移 | 低 | Layer 3 + 7 |
| B. Motion Stiffness | stock photo 静态 | 中 | Layer 8 |
| C. Literal Metaphor | 隐喻字面化 | 中 | Layer 8 vocabulary 清洗 |
| **D. Default-Prior Override** | **模型默认先验压过 prompt** | **最难，必须机制化** | Layer 3 + 10 |
| E. Cross-Scene Contamination | 信号污染其他场景 | 低 | Layer 3 + 8 隔离 |

---

## 七、Round 1-5 图像生成测试总结

### 目录：`/Users/lxxxxxx/个人项目/crpg/research/grok-image-test/`

| Round | 主要任务 | 关键发现 | 成本 |
|---|---|---|---|
| **R1** | 基线 5 张独立 prompt | ❌ 角色身份漂移 / setting 漂移 / ratio 混用 | $0.10 |
| **R2** | Visual DNA 七层 + image-to-image anchor | ✅ 一致性修好（5/5 Su Wan 是同一个人） | $0.12 |
| **R3** | 加 Direction Layer（第 8 层） | ✅ vibe 从 stock photo 变为 candid documentary；⚠️ 5/5 吐舌头 | $0.10 |
| **R4** | 升级 grok-imagine-image-pro + 修 tongue bug | ✅ 吐舌头修复；⚠️ Meijie cigarette 串场（Su Wan 嘴里 + 林泽嘴旁） | $0.35 |
| **bonus** | 沙发晨光特写（Style Preamble 阶段化首次） | ✅ 完美，证明 preamble 可按 value arc 切换 | $0.07 |
| **R5** | Shot Design Layer（第 9 层）+ 烟 bug 清洗 + 单 scene 5 shots | ✅ 方法论级突破（color戒 fragmentation）；⚠️ Shot 2 过膝袜 bug 连续 5 版 | $0.35 |
| R5 Shot 2 v1 | 短袜 bug (Bug A+C) | — | — |
| R5 Shot 2 v2 | 裤子 bug (Bug D) | — | $0.07 |
| R5 Shot 2 v3 | 构图苍白，只剩一只脚 | — | $0.07 |
| R5 Shot 2 v4 | 过膝袜 bug (Bug D) | — | $0.07 |
| R5 Shot 2 v5 | "修复" 版，引入 Layer 10 | ⚠️ **用户判定：还是过膝袜** | $0.07 |

**累计成本**：$1.37

**核心结论**：
- **Bug Class D 可能不是 prompt 工程能根治的**，Grok Imagine 对 sheer / thigh-high / ethnic garment 等 High-Prior 服装的渲染先验极强
- Round 5 Shot 2 的 5 版迭代暴露出**文转图的工程化难度被严重低估**
- 真正的产品级解决可能需要：自部署 SD + LoRA 微调 / 或接受"AI 自主美学"不强求精确复刻 / 或作为创作者半手动环节

---

## 八、未决架构问题（Q4-1 ~ Q4-7）

### Q4-1: Shot Director LLM 用哪个模型？
- A. Sonnet（继承叙事层） / B. Grok（和图像同家族） / C. 分级

### Q4-2: 图像生成是同步阻塞还是异步渐进？
- A. 异步（玩家先读文字，图后台陆续填充） / B. 同步阻塞等全部完成

### Q4-3: 多 shot 前端展示方式？
- A. 手动 carousel / B. 自动 Ken Burns 切换 / C. 只显示 cover / D. 混合

### Q4-4: 数据契约形态？
- story.json + visual-dna.json + shots/*.png 的具体结构
- 懒加载 / 预加载 / CDN 策略

### Q4-5: 成本分摊机制（路径 A 平台付费 vs 路径 B BYOK 已确认二选一）
- 路径 A 的定价（订阅 / 按量 / 混合）
- 路径 A 的 quota 限额

### Q4-6: 内容审核链
- 前置 / 生成中 / 后置 / 发布 各层 filter 设计

### Q4-7: 创作者 → 纯享版发布流程
- 发布前 playtest 是否强制
- 发布后能否撤回/修改/分叉
- 元数据结构

---

## 九、产品化 Pipeline（3-pass LLM + Image Batch）

```
[P1] Story Architect LLM     — 骨架 + Visual DNA seed（文字模型）
[P2] Story Content LLM       — 填充节点正文（文字模型）
[P3] Shot Director LLM (新增)  — 每节点弹性 shot 数（0-N，Director 自决）（文字模型）
[P4] Prompt Assembler (pure)   — VDNA + Shot spec → image prompt
[P5] Image Batch Worker       — Grok Imagine Pro 批量生图
```

**Shot budget 弹性规则**（用户 2026-04-17 明确）：
- 不是每节点都要图
- Director LLM 自决 0-N shots，按 node type / value shift / 戏分量
- 示例：narrative 过渡 0-2 / 关键 beat 3-5 / 高潮 5-8 / merge 0-1 / act_break 0-1

---

## 十、最后讨论的话题（session 中断点）

用户的 `/ultrareview` 意图（完整原话）：
> "我和daisy原来的想法就是做一个关键词或者一段话生成游戏的，那她已经做成了生成文字的，我现在弄了半天加图片的，但是图片的效果也一直不好，包括最后这个过膝袜也没做好，他其实还是过膝袜，现在就已经有很多工程问题了，包括两个模型的架构，已经这个导演llm怎么设计，镜头的一致性等等，我觉得值得保留的就是方法论，比如说daisy原来指导模型写故事的方法，当然我们也补充丰富了几个点，然后电影镜头的方法论，也挺不错的，其他的我觉得就很乱了，你看看系统检查一下吧"

用户核心判断：
- 保留：daisy 叙事方法论 + 我们补的几点 + 电影镜头方法论
- 混乱：双模型架构 / 导演 LLM / 镜头一致性工程 / 过膝袜 bug 没真正解决

用户打算通过 `/ultrareview` 做一次系统性独立审查。session 重启后应重跑。

---

## 十一、Git 状态

- 已 init：`/Users/lxxxxxx/个人项目/crpg` 是 git 仓库
- 分支：
  - `main` — 空 baseline commit
  - `brainstorming` — 88 个文件，所有 brainstorming 产物（**当前分支**）
- Remote：`origin = https://github.com/lxistired/crpg`（**private**，已推送两个分支）
- `.gitignore` 已 exclude `.env.local`（API key 安全）

---

## 十二、重启 Claude Code 后的 Next Action 建议

1. **在 crpg 目录重新打开 Claude Code**
2. **第一条消息**：Read `MEMORY.md` + Read `SESSION-STATE-2026-04-17.md`（这份）
3. **第二步**：跑 `/ultrareview` 做独立系统审查
4. **第三步**：根据 ultrareview 结果，决定走哪条路：
   - 路线 A：收缩范围（先做文字 + 叙事 + 创作者画布，图像作为 Phase 2）
   - 路线 B：保持完整范围但降低图像要求
   - 路线 C：All-in 图像工程（3-6 个月，单人难做）
   - 路线 D：直接进入 spec 写作（用 writing-plans skill）

---

## 十三、MEMORY.md 索引（用户级持久）

```
/Users/lxxxxxx/.claude/projects/-Users-lxxxxxx------crpg/memory/MEMORY.md
```

内容条目：
- crpg 新项目已确认补入的 McKee 原则
- crpg 诗意模式温度上限（0.8）
- crpg Genre 子系统决定累积（Q3-1 = D）
- crpg 模型策略与内容定位
- crpg 图像系统决定累积
- crpg 架构未决问题清单（Q4-1 ~ Q4-7）
- crpg 文转图工程复杂度是项目核心难点

---

**Session 结束。重启 Claude Code 见。**
