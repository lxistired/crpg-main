# AI 多图叙事生成调研报告 — 2026-04

> 调研日期：2026-04-17 | 针对问题：Grok Imagine Pro 眼神交互差、镜像错、多角色朝向乱

---

## 一、2026 年活跃工具清单 + API 接入 + 价格

### 1. FLUX.1 Kontext / FLUX.2（Black Forest Labs）— **首推**

| 版本 | 用途 | 价格（fal.ai） | 限制 |
|---|---|---|---|
| Kontext [pro] | 单图编辑 + 角色锁定 | **$0.04/图** | 单参考图 |
| Kontext [max] multi | 多参考图融合编辑 | **$0.08/图** | 最多 10 张参考图 |
| FLUX.2 [pro] | 新一代多参考生成 | 见 BFL 定价页 | 最多 10 张，4MP 输出 |

**技术亮点：**
- FLUX.1 Kontext 是 flow matching 架构，原生支持图+文混合输入，跨多轮编辑保持角色一致性
- FLUX.2（2025-11 发布，32B 参数）集成 Mistral-3 视觉语言模型，多轮编辑角色漂移显著低于前代
- fal.ai API endpoint：`POST https://fal.run/fal-ai/flux-pro/kontext/multi`
- 参数：`image_urls`（数组）+ `prompt` + `guidance_scale`（1-20，默认 3.5）+ `num_images`（1-4）
- BFL 官方 API 文档：https://docs.bfl.ai | 定价：https://bfl.ai/pricing
- fal.ai 汇总入口：https://fal.ai/flux

**叙事工作流：** 先生成角色锚定图（character anchor），后续每场景以该图为 reference 输入，配合"Same facial features, proportions, and color palette"约束文字。

---

### 2. GPT Image 1.5（OpenAI）

| 模型 | 质量 | 价格 |
|---|---|---|
| gpt-image-1-mini | low/med/high | $0.005 / — / $0.036 |
| gpt-image-1.5 | low/med/high | $0.009 / $0.034 / $0.133 |

**API endpoints：**
- `POST /v1/images/generations` — 文生图
- `POST /v1/images/edits` — 图编辑（支持 `action` 参数：generate/edit）
- Responses API：`previous_response_id` 参数支持多轮对话式图像迭代

**叙事特性：**
- Responses API 支持跨 turn 图像上下文传递，适合"逐场景推进 + 保持角色一致"
- 官方 Cookbook 记录的"character anchor"模式：先建立角色锚定图，再以 image editing 逐场景推进
- gpt-image-1.5 引入可复用"character anchor"，显式支持多页插画流水线
- **无原生"markdown→多图"批量端点**，需调用方封装循环

文档：https://developers.openai.com/api/docs/guides/image-generation

---

### 3. Grok Imagine API（xAI）— 当前 crpg 在用

| 模型 | 价格 | 速率限制 |
|---|---|---|
| grok-imagine-image | **$0.02/图** | 300 RPM |
| grok-imagine-image-pro | **$0.07/图** | 30 RPM |

**API endpoints（2026-04 实测）：**
- `POST https://api.x.ai/v1/images/generations` — 文生图
- `POST https://api.x.ai/v1/images/edits` — 图编辑（最多 5 张输入图）
- 支持宽高比：1:1 / 16:9 / 9:16 等 12 种；分辨率：1k / 2k
- 批量：`n` 参数 + `AsyncClient.gather` 并发，最多 10 图/请求

**关键结论：Grok Imagine 无"narrative-to-images"专属端点。** 多图支持仅限于：
1. 单次生成多个变体（同一 prompt，n≤10）
2. 多轮 chain edit（每轮输出作为下轮输入）
3. 编辑时最多传入 5 张参考图

眼神交互、多角色朝向等问题 Grok Imagine Pro **无专项解法**，是架构层面限制而非参数问题。

文档：https://docs.x.ai/docs/guides/image-generation

---

### 4. Imagen 4（Google / Vertex AI + Gemini API）

| 层级 | 价格 |
|---|---|
| Fast | $0.02/图 |
| Standard | $0.04/图 |
| Ultra | $0.06/图 |
| Gemini 3 Pro（Nano Banana Pro） | $0.067~$0.24/图 |

**特性：**
- Nano Banana Pro（Gemini 3 Pro 内嵌图像模型）：最多 8 张参考图，支持角色一致性
- Seedream 4.5（ByteDance，通过 Gemini API 接入）：$0.04/图，最多 14 张参考图，跨风格角色转换
- 无原生叙事端点；Veo 4（视频端）支持 storyboard 分场景结构化输入

---

### 5. Ideogram v3 + Character API

- 文生图基础：约 $0.09/图
- Character 端点（含参考图）：另计费，具体询问 partnership@ideogram.ai
- 特性：从 1-3 张参考图提取面部结构/发色/肤色，跨场景保持一致
- Remix / Reframe / Edit 均支持 character reference
- fal.ai 代理：https://fal.ai/ideogram
- 文档：https://developer.ideogram.ai

---

### 6. Seedream 4.5（ByteDance）

- 价格：$0.04/图（OpenRouter / fal.ai）
- 最多 14 张参考图（为同类最高）
- 支持跨风格（写实→动漫→像素）保持角色 ID
- API：https://openrouter.ai/bytedance-seed/seedream-4.5

---

### 7. InfiniteYou（ByteDance，基于 FLUX）

- 零样本身份一致性保留模型，无需训练
- 基于 DiT（Diffusion Transformer）架构，FLUX 底座
- 适用场景：单角色跨场景图像，面部特征保留率高
- ComfyUI 工作流：https://www.runcomfy.com/comfyui-workflows/comfyui-infiniteyou-identity-preserving-face-generation-toolkit
- 暂无托管 API，需本地 / RunComfy 使用

---

### 8. ACE++（Alibaba，开源）

- 零训练角色一致性，单张参考图即可
- 基于 Flux Fill，context-aware content filling
- 支持 portrait-consistent generation + subject-driven generation
- GitHub：https://github.com/ali-vilab/ACE_plus
- ComfyUI 工作流：https://www.runcomfy.com/comfyui-workflows/ace-plus-plus-character-consistency

---

### 9. Scenario.gg（多角色场景，游戏资产向）

- Pro 计划：$45/月（5,000 compute units）
- 支持 Multi-LoRA（不同角色各自 LoRA 叠加）
- 推荐底模：Nano Banana Pro + Seedream 4.5
- Character Fusion app 专项解决多角色一致
- Runway Gen-4 References 集成：https://help.scenario.com/en/articles/runway-gen-4-the-essentials/
- API 定价：https://docs.scenario.com/page/api-pricing

---

### 10. Runway Gen-4 / 4.5

- 定位：AI 视频/多镜头一致性
- 单张参考图即可跨镜头保持角色一致（灯光/角度变化）
- Gen-4.5 新增：原生音频、多镜头序列、最长 1 分钟角色一致长片
- **限制：** 跨 clip 一致性需手动接力，不自动跨 session
- 价格：按订阅，API 接入需企业计划

---

### 11. NovelAI Diffusion v4.5（动漫/视觉小说）

- 订阅制：$10 / $15 / $25/月（无独立 API 定价）
- 专为动漫/漫画优化，V4.5 原生支持 6 角色同框
- 多角色通过 "+ Add Character" 独立 conditioning stream，避免 token 竞争
- 支持 Precise Reference（参考图锁定风格）
- 语音气泡/文字渲染原生支持
- 无公开 API；适合订阅制本地工作流

---

### 12. Anifusion（漫画/漫画多格）

- 专为漫画/视觉小说设计，角色一致性引擎 + 智能分格排版
- 内置 LoRA 训练（10-30 张参考图）
- 支持文字描述→分格漫画页（非批量 markdown 一键生成，仍需逐场景）
- 2026 年评选最佳 AI 漫画生成器
- 无公开 API；订阅制
- https://anifusion.ai

---

### 13. StoryDiffusion / Infinite-Story（开源学术）

- StoryDiffusion：Consistent Self-Attention，跨图 batch 共享 attention，角色/服装一致性
- Infinite-Story（AAAI 2026）：无需训练的多 prompt 故事一致生成，Identity Prompt Replacement + Adaptive Style Injection
- 适合本地 ComfyUI 工作流，非托管 SaaS
- Infinite-Story paper：https://arxiv.org/abs/2511.13002

---

## 二、"整个故事 markdown→自动多图"端点现状

**结论：2026-04 没有任何主流 API 提供原生 markdown 故事→多图批量生成的单一端点。**

| 方案 | 可行性 | 说明 |
|---|---|---|
| GPT Image 1.5 Responses API | 可行（需封装） | `previous_response_id` 链式调用，每场景一次 API call |
| Flux Kontext multi + 调用方循环 | 可行 | 解析 markdown 场景节点，每节点生成一张，参考图复用 |
| fal.ai Workflow endpoint | 可行 | 支持多步 pipeline 串联，可自定义 narrative→image DAG |
| Anifusion / Jenova | 产品内支持 | 非 API；在平台内逐场景生成 |
| Grok Imagine | 不支持 | 无序列化叙事功能 |
| OpenAI / Google / Anthropic | 无专属端点 | 需调用方封装 |

**推荐实现路径（crpg）：**
1. LLM（Claude / GPT-5）解析 markdown → 提取场景描述列表
2. 首场景生成角色锚定图（Flux Kontext pro）
3. 后续场景循环调用 Flux Kontext multi，传入锚定图 + 场景描述
4. fal.ai Workflow 可封装整个 DAG 为单一端点

---

## 三、核心痛点 SOTA 解法

### 3.1 眼神交互 / Gaze Direction

**根本原因：** 扩散模型无几何推理，无法从语义推断两人对视的空间关系。

**2026 可用解法（从工程可行到研究前沿排序）：**

1. **ControlNet Pose（OpenPose）+ Depth 叠加**（最实用）
   - 用 OpenPose 画出两角色的骨架，头部 keypoint 朝向对准
   - 同时叠 DepthControlNet 确保空间前后关系正确
   - FLUX.1-dev ControlNet Union Pro：`InstantX/FLUX.1-dev-Controlnet-Union`（HuggingFace）
   - Replicate ControlNet API：https://replicate.com/collections/control-net

2. **Prompt 工程技巧**
   - 明确写"Character A turns head toward Character B, eyes meeting, direct mutual gaze"
   - 加"from the front, facing each other, eye contact"
   - 避免"looking at camera"（会覆盖对视语义）
   - 指定角色位置："A on the left, B on the right, both turning inward"

3. **PersonaCraft（研究级）**
   - SMPLx-ControlNet：3D 人体建模 + 深度/法线 map 条件生成
   - 支持多角色遮挡感知，解决 2D pose 的几何歧义
   - GitHub：https://github.com/gwang-kim/PersonaCraft

4. **后处理方案（应急）**
   - AI Eye Contact 校正工具（Kaze.ai / PiktID）：对已生成图做眼神方向修正
   - 多人照片支持逐人调整
   - 适合 Grok Imagine Pro 现有输出的快速修复

---

### 3.2 镜像 / 反射一致性

**根本原因：** 扩散模型优化美学似然而非物理精度，镜像区域被注意力层"模糊化"以规避几何矛盾。

**SOTA 方法（2025-2026）：**

1. **MirrorFusion v2 / MirrorVerse**（CVPR 2025）
   - 训练集 SynMirrorV2：207K 样本，含深度图/法线图/分割 mask
   - depth-conditioned inpainting：以深度图为条件生成镜像区域
   - 比前代模型在物体朝向/位置随机化上泛化更好
   - Paper：https://arxiv.org/abs/2504.15397（MirrorVerse）
   - 暂无托管 API；可本地 / ComfyUI 运行

2. **工程回避策略（立即可用）**
   - **避开镜像**：分支叙事场景尽量不设计镜像场景
   - **遮挡代替反射**：用角色站在镜子旁但镜面不入画代替全镜射
   - **后合成**：生成角色图 + 单独生成场景，Photoshop/GIMP 手动合成镜像

3. **Prompt 技巧**
   - 明确写"no mirror visible"避免随机生成镜像
   - 如必须有镜："a small hand mirror reflecting only Character A's face, accurate reflection"比"镜子场景"更可控

---

### 3.3 多角色空间物理一致性

**核心技术组合（2026 工程实践）：**

1. **ControlNet Depth + Pose 叠加**
   - Depth map 确保前景/背景层次
   - Pose 确保角色骨架位置/朝向
   - FLUX.1 ControlNet Union 支持同时多控

2. **Prompt token 顺序**
   - 每个角色的 token 放在 prompt 最前，防止特征被稀释
   - 每角色描述独立，避免属性跨角色污染

3. **Multi-LoRA 方案（Scenario.gg）**
   - 每角色训练独立 LoRA（15-30 张参考图）
   - 多 LoRA 叠加生成，角色 ID 隔离，一致率 85-95%

4. **FLUX.2 多参考输入**
   - 传入 Character A 正面 + 侧面各 1 张 + Character B 正面 + 侧面各 1 张 + 场景参考图
   - 最多 10 张参考，空间布局由 prompt 控制

---

## 四、多图场景 SOTA 审美路线（非写实）

### Manga / Anime 多格

| 工具 | 特点 | 价格 | API |
|---|---|---|---|
| NovelAI v4.5 | 动漫专精，6 角色同框，气泡支持 | $10-25/月 | 无 |
| Anifusion | 完整漫画页生成，自动分格排版 | 订阅制 | 无 |
| Jenova | 故事→漫画，支持连载 | $20+/月 | 无 |
| FLUX.1 Kontext + 动漫 LoRA | 可控性最强，可接 API | $0.04/图 | 有 |

**Prompt 技巧（动漫风格）：**
- 指定流派："shonen manga style, dynamic panel, ink lines, screentone"
- 多格布局："4-panel comic strip layout, consistent character design"
- 风格锁定："flat cel shading, limited palette, manga line art"

---

### Graphic Novel 风格

- FLUX.1 Kontext [pro]：写实+漫画混合效果优
- GPT Image 1.5 high quality：文字渲染能力强，适合对话气泡场景
- 推荐 prompt："graphic novel illustration, heavy ink outline, cinematic composition, dramatic lighting"

---

### Watercolor / 插画风叙事图

- FLUX Kontext：watercolor 风格迁移一致性好
- Ideogram v3：审美自由度高，适合情绪化插画
- 推荐 prompt（FLUX Kontext）："watercolor illustration, loose wet-on-wet technique, limited earthy palette, impressionistic edges, soft paper texture"
- 参考：https://www.dreamfaceapp.com/blog/prompts-watercolor

---

## 五、crpg 下一步推荐切换/增加工具

### 推荐 1：FLUX.1 Kontext [pro] 作为主力图像生成器（立即切换）

**理由：**
- 价格：$0.04/图（vs Grok Imagine Pro $0.07/图，节省 43%）
- 原生多参考图支持（最多 10 张），角色一致性远优于 Grok Imagine
- 跨多轮编辑角色漂移极低（flow matching 架构优势）
- 通过 fal.ai 有稳定 API，与现有 pipeline 兼容
- 可处理分支叙事每个节点的独立场景图

**接入方式：**
```python
import fal_client

result = fal_client.run(
    "fal-ai/flux-pro/kontext",
    arguments={
        "prompt": "Scene description here. Same character, same face, same outfit.",
        "image_url": "CHARACTER_ANCHOR_IMAGE_URL",
        "guidance_scale": 3.5,
        "num_images": 1
    }
)
```

多参考图版本：endpoint `fal-ai/flux-pro/kontext/multi`，`image_urls` 传数组。

**文档：** https://fal.ai/models/fal-ai/flux-pro/kontext
**价格：** $0.04/图（单图）/ $0.08/图（多参考图 max 版）

---

### 推荐 2：ControlNet Pose + Depth 解决眼神交互/多角色朝向（即刻增加）

**理由：**
- 当前痛点（眼神差、朝向乱）是 prompt 无法解决的**空间推理缺陷**，需要几何约束
- ControlNet 是目前唯一工程上可行的解法
- 可通过 Replicate API 直接调用，无需本地部署

**接入方式：**
- Replicate ControlNet 集合：https://replicate.com/collections/control-net
- 工作流：OpenPose 图（指定两角色头部朝向互对）→ FLUX ControlNet → 生成场景图

**预算：** Replicate 按 GPU 秒计费，单图约 $0.02-$0.05

---

## 六、Summary（≤250 词，供 orchestrator）

**2026-04 调研结论：**

Grok Imagine Pro 的眼神交互差、镜像错、多角色朝向乱三个问题均属**架构层面缺陷**，非参数调优能解决。

**最优替代方案：FLUX.1 Kontext [pro]（$0.04/图，via fal.ai）**
- 价格比 Grok Pro 便宜 43%，多参考图支持（≤10 张），跨多轮编辑角色一致性 SOTA
- API endpoint：`fal-ai/flux-pro/kontext`（单图）/ `fal-ai/flux-pro/kontext/multi`（多参考）

**眼神交互/朝向问题唯一工程解：** ControlNet OpenPose + Depth 叠加，通过 Replicate API 调用，约 $0.02-0.05/图。PersonaCraft（开源）提供 3D-aware 更高精度方案但需本地部署。

**镜像问题：** MirrorFusion v2 学术 SOTA，无托管 API；工程建议直接在场景设计层面规避镜像。

**无任何 API 支持"markdown→多图"原生端点。** 需调用方封装：LLM 解析场景列表 → 循环调用 Flux Kontext，首图作角色锚定图，后续 reference 复用。fal.ai Workflow endpoint 可封装为单一 pipeline。

**动漫/漫画风格：** NovelAI v4.5（订阅制，无 API）最优；有 API 需求则 FLUX.1 + 动漫风格 LoRA。

**crpg 立即行动项：**
1. 替换 Grok Imagine Pro → FLUX.1 Kontext pro（cost down + 质量 up）
2. 多角色对视场景增加 ControlNet Pose 前处理步骤

---

## 参考来源

- FLUX.1 Kontext 官方：https://bfl.ai/models/flux-kontext
- FLUX.2 发布：https://bfl.ai/blog/flux-2
- fal.ai Kontext Multi：https://fal.ai/models/fal-ai/flux-pro/kontext/max/multi
- fal.ai Kontext API 文档：https://fal.ai/docs/model-api-reference/image-generation-api/flux-pro-kontext-multi
- xAI Grok Imagine API：https://docs.x.ai/docs/guides/image-generation
- xAI 定价：https://docs.x.ai/developers/models
- GPT Image 1.5 Cookbook：https://developers.openai.com/cookbook/examples/multimodal/image-gen-1.5-prompting_guide
- OpenAI 图像 API：https://developers.openai.com/api/docs/guides/image-generation
- AI 图像 API 价格对比：https://blog.laozhang.ai/en/posts/ai-image-api-pricing-comparison
- MirrorVerse CVPR 2025：https://arxiv.org/abs/2504.15397
- Infinite-Story AAAI 2026：https://arxiv.org/abs/2511.13002
- PersonaCraft：https://gwang-kim.github.io/persona_craft/
- ACE++：https://github.com/ali-vilab/ACE_plus
- InfiniteYou（ByteDance）：https://medium.com/data-science-in-your-pocket/bytedance-infiniteyou-ai-model-to-generate-character-consistent-images-12821f17ff6c
- Seedream 4.5：https://openrouter.ai/bytedance-seed/seedream-4.5
- Ideogram API：https://developer.ideogram.ai
- Scenario.gg：https://www.scenario.com
- NovelAI v4.5：https://novelai.net/v4
- Anifusion：https://anifusion.ai/features/ai-comic-creator
- Replicate ControlNet：https://replicate.com/collections/control-net
- FLUX ControlNet Union：https://huggingface.co/InstantX/FLUX.1-dev-Controlnet-Union
- Runway Gen-4：https://runwayml.com/research/introducing-runway-gen-4
