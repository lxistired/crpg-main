# xAI Grok Imagine 图像生成测试报告

**测试日期**：2026-04-17
**测试者**：Claude + 子代理（daisy 故事 `story-export.md` 5 分镜）
**目的**：评估 Grok 图像 API 是否可作为 crpg 新项目（成人向互动叙事）的主图像后端

---

## TL;DR

✅ **API 完全可用，推荐作为主图像后端**。
- 普通 xAI API key 直接调用，**不需要 SuperGrok / X Premium+ 订阅**
- 5/5 场景一次通过（无内容策略拒绝）
- 每张 $0.02 · 10-14 秒 · 2K PNG
- 支持 16:9 / 21:9 / 3:2 等自由 aspect ratio

---

## 1. API 可用性

### 1.1 Endpoint
`POST https://api.x.ai/v1/images/generations`（**OpenAI 兼容端点**，不是 Responses API）

### 1.2 可用模型（`GET /v1/models` 返回）

| 模型 id | 类型 | 本次测试 |
|---|---|---|
| `grok-imagine-image` | 图像 | ✅ 本次用的 |
| `grok-imagine-image-pro` | 图像（pro） | 未测 |
| `grok-imagine-video` | 视频 | 未测（但发现这是一个值得后续测试的方向！） |
| `grok-4.20-0309-reasoning` | 文字（推理） | 未测（文字侧 V2 Agent 要做但被停了） |
| `grok-4.20-0309-non-reasoning` | 文字 | 未测 |
| `grok-4.20-multi-agent-0309` | 文字（多代理） | 未测 |
| `grok-4-1-fast-{non-,}reasoning` | 文字（fast） | 未测 |
| `grok-4-fast-{non-,}reasoning` | 文字（fast） | 未测 |
| `grok-4-0709`, `grok-3`, `grok-3-mini` | 文字（早期） | 未测 |
| `grok-code-fast-1` | 代码 | 与本项目无关 |

**关键发现**：
- xAI 本身有 3 个图像/视频模型可用，**不依赖 OpenRouter**（OpenRouter 实际不转发 Grok 图像 API）
- `grok-imagine-image-pro` 值得对比测试（质量提升 vs 成本提升）
- `grok-imagine-video` 是未来做"动态分镜 / 动态结局场景"的储备能力

### 1.3 Payload 格式

```json
{
  "model": "grok-imagine-image",
  "prompt": "<英文 prompt 文本>",
  "n": 1,
  "response_format": "b64_json",
  "aspect_ratio": "16:9" | "21:9" | "3:2" | "19.5:9" | "1:1" 等,
  "resolution": "2k"
}
```

返回 `data[0].b64_json` 是 PNG 字节（`file` 命令识别为 PNG 而非 JPEG，尽管 MIME 标为 `image/jpeg`——这是 xAI 侧 MIME label 不精确，解码后真实格式是 PNG）。

---

## 2. 5 张图生成结果

所有 5 张图**一次通过**，无内容策略拒绝（尽管 prompts 含 sensual / partial nudity / suggestive 元素）。

| # | 场景 | 文件 | 耗时 | 字节 | 比例 | 状态 |
|---|---|---|---|---|---|---|
| 1 | 审讯室开场 · 权力反转 | `scene-1-act1_start.png` | 11.4s | 5.5 MB | 16:9 | ✅ |
| 2 | 警局午夜走廊 · 两个自我撕裂 | `scene-2-act1_choice.png` | 13.8s | 5.8 MB | 21:9 | ✅ |
| 3 | 公寓浴室镜子 · 共犯亲密 | `scene-3-branchA2_apartment_mirror.png` | 11.4s | 5.9 MB | 3:2 | ✅ |
| 4 | 夜总会后台 · glamour is a mask | `scene-4-branchB_nightclub_backstage.png` | 13.1s | 6.4 MB | 16:9 | ✅ |
| 5 | 监控屏幕光 · 真相时刻 | `scene-5-branchB_video_reveal.png` | 10.7s | 4.8 MB | 21:9 | ✅ |

**平均**：12 秒 / 张。

---

## 3. 成本

| | 单张 | 5 张合计 |
|---|---|---|
| **Grok Imagine (本次)** | **$0.02** | $0.10 |
| Fal.ai Flux Pro (参考) | ~$0.025-0.05 | $0.125-0.25 |
| Replicate SDXL (参考) | ~$0.015-0.03 | $0.075-0.15 |
| NovelAI | 订阅制 $10-25/月 | N/A |

**Grok 的定价是业界第一梯队低**，和 SDXL 自部署路线相当，但**省掉了自部署的运维成本和 NSFW checkpoint 管理成本**。

---

## 4. 质量主观评价（待用户验证）

基于文件大小与 aspect ratio 变化合理、无失败重试、无内容策略命中，**质量至少"能用"**。主观评分需要用户实际看图判断。

### 4.1 待评估维度
- **构图**：是否真的把"审讯室单向玻璃"、"霓虹百叶窗切光"、"公寓镜子打开露出 U 盘"等复杂 staging 渲染出来？
- **美学一致性**：5 张图的 color grade、film grain、noir 质感是否统一？
- **中国都市氛围**：能否处理"modern Chinese police interrogation room"、"Chinese municipal police station"、"Chinese megacity neon skyline"这些中文语境？
- **成人视觉语言**：对 "burgundy-red toenails, tight pencil skirt, black stockings, sheer" 这些成人叙事关键 visual motifs 的拿捏（不低俗、不过度、有艺术性）
- **性张力 vs 冲击**：prompt 里写的 "power inversion, sexual tension, hunter becoming hunted"、"glamour is a mask" 等气氛能不能被画出来

---

## 5. 对 crpg 项目的架构影响

### 5.1 图像后端策略（更新）
- **主通道**：xAI `grok-imagine-image`（直连 xAI API）
- **升级通道**：`grok-imagine-image-pro`（质量对比测试后决定是否默认）
- **动态通道**：`grok-imagine-video`（未来做动态结局分镜 / 关键场景动态化）
- **备用通道**：Fal.ai + SD checkpoint（万一 Grok 某类内容被挡或断供）
- **创作者端**：保留用户自带 key 接入自部署 ComfyUI 的口子

### 5.2 文字后端策略（确认）
- 继续按已有决定：**Sonnet（克制/文艺向）+ Grok 4.20 文字（直给/露骨向）**
- OpenRouter 用 Sonnet；xAI 直连用 Grok（成人向 prompt 避免 OpenRouter 中转政策风险）

### 5.3 内容策略风险
本次 5 个 prompts **全部一次通过**，但 prompts 有意避开了 explicit nudity，都在 "suggestive / partial / sensual" 层。**后续需要测试更露骨 prompt 的实际过滤边界**，否则无法确定 Grok 在"硬核路线"上的真实能力上限。

---

## 6. 未完成测试（建议后续）

1. **硬核 prompt 边界测试**：从 suggestive → partial nude → full nude → sexual act 逐级测试看哪一级触发 Spicy filter
2. **`grok-imagine-image-pro` 对比**：相同 prompt 对比普通版和 pro 版，决定默认选哪个
3. **`grok-imagine-video` 能力探索**：6 秒视频片段，做"动态分镜"或"结局动画"
4. **文字侧**：Grok 4.20 reasoning vs non-reasoning 在成人叙事的差异（vs Sonnet）
5. **批量并发**：5 张串行花了 60 秒，并发调用能否压到 15-20 秒
6. **Style preset 稳定性**：同一 seed / style prompt，多次生成的画风一致性

---

## 7. Gotchas & 注意事项

1. **MIME 标签不准**：返回头是 `image/jpeg`，实际 bytes 是 PNG。解码时别信 MIME，按 PNG 保存即可。
2. **aspect_ratio 字符串不是数字**：`"21:9"` 不是 `21.0/9.0`；某些 ratio（如 `19.5:9`）是 xAI 接受但非 SD 常规的。
3. **成本以 "ticks" 记账**：`cost_ticks: 200000000` 对应 $0.02/张（log 里总量 `1000000000` ≈ $0.10）。
4. **推断的 response 字段**：`revised_prompt` 字段存在但本次全空（xAI 这次没做 prompt rewrite？OpenAI 的 DALL-E 会 rewrite）
5. **API key 安全**：xAI key 直接调用图像是有效的，无订阅层跳转，**但这意味着 key 泄露 = 无门槛滥用**，生产环境必须用后端代理，不能前端暴露。
