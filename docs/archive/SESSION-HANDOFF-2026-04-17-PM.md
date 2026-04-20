# Session Handoff —— 2026-04-17 下午（compact 前）

## 接本文件 + `PIPELINE-SIMULATION-FINAL-2026-04-17.md` + MEMORY.md 恢复上下文

---

## 今日下半段做了什么

1. **Pipeline simulation v1 & v2**：Planner(Sonnet) + 5×Haiku Specifier 并发 + Python asyncio 并发 Grok Imagine + 独立 QC 跑通。v1=19 shots insert 过多丢故事性；v2=12 shots medium-heavy 恢复故事性但仍有 Grok 天花板 bug（眼神不交互 / 镜像错 / 多角色朝向乱）
2. **Grok anime 实验**：4 张（3 scenes + bonus 沙发）**用户评价"绝了"**——anime 风格绕过了几乎所有写实路线硬伤
3. **Research agent**：产出 `research/pipeline-simulation/narrative-image-research-2026.md`，推荐 FLUX Kontext / OpenPose
4. **fal.ai 测试**（用户提供 key，已存 `.env.local` 变量 `FAL_KEY`）：
   - FLUX Pro v1.1 + FLUX Kontext t2i：**用户评价"完全不行，脚趾都乱了"**
   - Nano Banana Pro：gaze 好但分辨率低
   - FLUX.2 Max：gaze 好（最强候选之一），但**用户评价"彻底不行"**（commit 已记录）
   - FLUX.2 Max bonus 沙发：已生成
   - **SOTA 4 模型重测**（Nano Banana Pro v2 / Nano Banana 2 / Recraft V4 Pro / FLUX.2 Pro）：4/4 成功，**用户评价"都不行了属于是"**
   - Recraft V4 Pro 分辨率最大（9.3MB）

## 用户的最终判断（session 结束时 + compact 后补跑）

**Grok Imagine Pro + anime 风格**锁定为**产品默认图像方案**。
**fal.ai 上的所有 t2i SOTA 模型**（FLUX.2 pro/max、Nano Banana Pro/2、Recraft V4 Pro）**都"不行"**。

**GPT Image 1.5 补跑结果（compact 后）**：
- `fal-ai/gpt-image-1.5/edit`（3-person backstage，anime 锚图）：用户评价"五五开"
- `fal-ai/gpt-image-1.5/edit`（bonus sofa，anime 锚图）：用户评价"五五开"
- `fal-ai/gpt-image-1.5`（纯 t2i，bonus sofa）：**被 OpenAI moderation 拦**（`content_policy_violation` on 开口衬衫+丝袜+独居女黎明场景）
- **结论**：成人向走 OpenAI 系（含 fal 代理）是**死胡同**——moderation 永远会拦。放弃 GPT，聚焦 Grok。

## fal 上已确认的 endpoint 清单（备查）

- `fal-ai/flux-pro/v1.1` ← FLUX Pro v1.1
- `fal-ai/flux-pro/kontext/text-to-image` ← FLUX Kontext
- `fal-ai/flux-2-pro` ← FLUX.2 Pro
- `fal-ai/flux-2-max` ← FLUX.2 Max
- `fal-ai/nano-banana-pro` ← Nano Banana Pro (Gemini 3 Pro Image)
- `fal-ai/nano-banana-2` ← Nano Banana 2 (Gemini 3.1 Flash Image)
- `fal-ai/nano-banana-pro/edit`
- `fal-ai/recraft/v4/pro/text-to-image` ← Recraft V4 Pro
- `fal-ai/recraft/v3/text-to-image`
- `fal-ai/gpt-image-1.5/edit` ← **GPT Image 1.5（只有 edit 模式，待测）**
- `fal-ai/bytedance/seedream/v5/lite/edit` ← Seedream 5 Lite（edit 模式）
- `fal-ai/bytedance/seedream/v4.5/edit`
- `fal-ai/bytedance/seedream/v4/edit`
- `fal-ai/qwen-image`

## 已跑通的 pipeline 架构（可直接用于产品代码）

```python
# 顺序
1. Planner (Sonnet subagent) → stage1-shot-list.json (全局 shot 决策)
2. Specifier (Haiku 并发 subagent × N 或单次 Haiku) → stage2-prompts.json
3. Image Gen (Python asyncio + fal.ai API, 并发 8) → shots/*.png
4. QC (Claude orchestrator 独立看图，免费)

# 关键代码路径
research/pipeline-simulation/generate_concurrent.py  ← v1 Grok 并发
research/pipeline-simulation/generate_v2.py          ← v2 Grok 并发
/tmp/anime_experiment.py                             ← Grok anime 4 张
# fal 脚本是 inline heredoc，分散在 bash 历史里
```

## 5 类 T2I bug taxonomy（已固化到 assets）
A: Identity Drift / B: Motion Stiffness / C: Literal Metaphor / D: Default-Prior Override（过膝袜）/ E: Cross-Scene Contamination（烟污染）

## 下次 session 的 Next Action（GPT 放弃后更新）

**按优先级**：

1. **图像方案已锁定**：Grok Imagine Pro + anime 风格（不再测其他生图模型）
2. **进入产品代码阶段**：Fork daisy → crpg/app，按 `STRATEGIC-REVIEW-v2-2026-04-17.md` 的路径 Y 逐步叠加 3-pass pipeline + 18+ 门 + BYOK + 合规层
3. **图像作为 Phase 2**，先 ship 文字 MVP
4. **写产品 spec（via writing-plans skill）** 之前需要用户过一遍 design，确认核心边界

## 成本
今天累计 ~$4.5（Grok $3.8 + fal $0.7）

## 关键资产清单（给下次 session 读）
- `MEMORY.md` + 8 条 memory 文件（项目决策链）
- `SESSION-STATE-2026-04-17.md`（上午 session 全貌）
- `PIPELINE-SIMULATION-FINAL-2026-04-17.md`（pipeline 验证结论）
- `SYSTEMS-ARCHITECTURE-REVIEW-2026-04-17.md`（5 component + 7-stage pipeline 架构图）
- `STRATEGIC-REVIEW-v2-2026-04-17.md`（Fork daisy 路线建议）
- `COMPETITIVE-ANALYSIS-2026-04-17.md`（竞品格局）
- `assets/daisy-narrative-core/*.md`（完整方法论 asset 15 份）
- `research/pipeline-simulation/`（v1/v2/anime/fal-experiment 全部图和脚本）

## Git 状态
- Branch: `brainstorming`
- Remote: `origin = github.com/lxistired/crpg` (private)
- 最近 commit: "flux verdict + fal experiments"

## 本文件落盘后
立即 `git add -A && git commit -m "session handoff before compact"` 然后 compact 安全。
