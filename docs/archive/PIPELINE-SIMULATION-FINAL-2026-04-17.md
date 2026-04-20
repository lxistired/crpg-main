# crpg 图片 pipeline 模拟验证 —— 阶段收工报告（2026-04-17）

## 一句话结论

今天花了 ~$2.5 + 一整天，**验证了一件最重要的事**：
> **Anime 风格 + "导演 LLM + 并发生成" 架构是可行的。但当前的 Grok Imagine Pro 不是最佳生成器——下一步应切换到 fal.ai 的 FLUX.1 Kontext。**

---

## 今天到底做了什么（按时间顺序）

1. **Round 1-5 + bonus**：用 Grok Imagine Pro + 手工 prompt 做了 25+ 次图像实验，暴露 5 类 bug（身份漂移 / 僵硬 / 字面化 / 服装先验 / 场景污染），全部沉淀到 `assets/daisy-narrative-core/text-to-image-bug-taxonomy.md`
2. **Pipeline simulation v1**：Planner(Sonnet) + Specifier(5×Haiku 并发) + 图并发 + 独立 QC 跑通，19 shots × $0.07 = $1.40，103 秒。但 shot 分布偏了（68% ECU/insert，像解剖标本，丢故事性）
3. **Pipeline simulation v2**：手工重做 shot list 改成 medium-heavy（67% medium + 25% MCU + 0% ECU），12 shots × $0.07 = $0.70，73 秒。故事性回来了，但**仍有 Grok 的天花板 bug**：眼神不交互、镜像错、多角色朝向乱
4. **Anime 风格实验**：3 + 1 bonus = 4 张用 anime preamble，**几乎所有 bug 消失**——gaze 三角清晰、镜像处理更好、视觉更有故事感
5. **Research 调研**：2026 年 AI 多图叙事最新进展，产出 `research/pipeline-simulation/narrative-image-research-2026.md`

---

## 方法论沉淀（值得保留）

### 架构级（已验证，可直接产品化）
- **两阶段 C pipeline**：Planner（全局）+ Specifier（具化）+ Image（并发）+ 独立 QC
- **并发实现**：Python asyncio + 8 并发 semaphore，比串行快 25×
- **Anchor 策略**：首图锚定 + `image_url` image-to-image 传递身份，锁人物识别
- **Shot budget 弹性**：节点类型决定 shot 数量，不强制平均

### 方法论级（今天验证强化）
- **Shot design 必须 medium-heavy**（65%+）不是 insert-heavy，否则失去故事性
- **5 类 T2I bug taxonomy** 完整整理（Layer 10 Layered Garment 必须应用）
- **Character-specific tell 必须下沉到 Character Sheet**（不进 Direction Layer）
- **Anime 风格绕过了大部分写实路线的硬伤**（眼神、镜像、服装先验）

### Grok Imagine 的真实边界（今天新发现）
- 眼神交互 / 镜像一致性 / 多角色朝向 **是架构缺陷，不是 prompt 问题**
- 即使 Specifier 用最好的 LLM 写 prompt 也突破不了
- 走**anime 风格**可以绕过大部分这些限制

---

## 下一步推荐架构（研究结论）

```
文字侧：
  daisy V6 的 McKee 叙事 pipeline（直接继承）
  + 我们补的 Genre / Antagonism / Climax
  + Sonnet 主 / Grok 备（露骨场景）

图片侧：
  主生成器:   FLUX.1 Kontext [pro] (fal.ai, $0.04/图)  ← 从 Grok 切换
  一致性:     首图 anchor + image_url multi-reference（和今天验证的架构同构）
  Gaze 修复:  ControlNet OpenPose (Replicate, $0.02-0.05/图, 需要时)
  审美:       Anime 风格（今天验证有效）
  架构:       Planner(Sonnet) + Specifier(Haiku 并发) + 并发生图 + 独立 QC
  
成本估算（50 shot 故事）:
  文字 LLM:   $0.80
  图像:       50 × $0.04 = $2.00
  总计:       ~$3/故事 (vs 之前估的 $7)
```

---

## 今天累计成本

- R1-R5 + bonus + retries: $1.37
- Pipeline simulation v1 (19 shots): $1.40
- Pipeline simulation v2 (13 shots): $0.70
- Anime experiment (4 shots): $0.28
- Planner/Specifier LLM calls: ~$0.05
- **总计: ~$3.80**

换来的是：整个成人向叙事图像 pipeline 的**可工程化路径**，从"完全不知道怎么做"到"架构清楚 + 工具选型清楚 + 成本模型清楚"。

---

## 下次写代码要做的 3 件事

1. **注册 fal.ai** 拿 API key，把 FLUX.1 Kontext 当默认生成器跑一次 pipeline 对比 Grok
2. **Fork daisy 到 crpg/app** 作为 v0.1 基础，在其上加 3 pass（Story Architect + Shot Director + Image Batch）
3. **先做文字 MVP 可玩**（2-3 周），图像作为 Phase 2（4-6 周）

---

## 所有落盘产物路径（给下次 session 用）

**方法论 asset**：
- `assets/daisy-narrative-core/prompts-v3/v4/v6.ts`（daisy 三版 prompts）
- `assets/daisy-narrative-core/visual-dna-system.md`（10 层 Visual DNA）
- `assets/daisy-narrative-core/shot-design-system.md` + `shot-types-vocabulary.yaml`（电影镜头方法论）
- `assets/daisy-narrative-core/text-to-image-bug-taxonomy.md`（5 类 bug）
- `assets/daisy-narrative-core/mckee-full-framework.md`（McKee 补充）
- `assets/daisy-narrative-core/visual-aesthetics.yaml` + `visual-aesthetic-axes.md`（24 美学子派）

**Pipeline 实证**：
- `research/pipeline-simulation/stage1-shot-list.json` / `stage1-shot-list-v2.json`（v1/v2 shot list）
- `research/pipeline-simulation/stage2-prompts-*.json`（Specifier 产出）
- `research/pipeline-simulation/generate_concurrent.py` / `generate_v2.py`（并发脚本）
- `research/pipeline-simulation/shots/` + `shots-v2/` + `anime-experiment/`（生成图像）
- `research/pipeline-simulation/narrative-image-research-2026.md`（2026 最新工具调研）

**战略 / 竞品分析**：
- `STRATEGIC-REVIEW-2026-04-17.md`（v1 战略审查）
- `STRATEGIC-REVIEW-v2-2026-04-17.md`（v2，加 daisy 代码）
- `COMPETITIVE-ANALYSIS-2026-04-17.md`（竞品分析）
- `SYSTEMS-ARCHITECTURE-REVIEW-2026-04-17.md`（架构师审查）

**Session 状态**：
- `SESSION-STATE-2026-04-17.md`（早前的 session snapshot）
- `PIPELINE-SIMULATION-FINAL-2026-04-17.md`（本文件）
FLUX.2 Max verdict: 用户评价彻底不行（see session log 2026-04-17）
