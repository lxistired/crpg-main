# 用户提供的 Grok API 补充信息

用户在 2026-04-17 提供的 xAI API 使用提示（供 Agent A 或后续调研参考）：

## 确认的 endpoint 和格式

xAI 支持 OpenAI **Responses API** 风格的 endpoint：

```bash
curl https://api.x.ai/v1/responses \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $XAI_API_KEY" \
  -d '{
    "model": "grok-4.20-reasoning",
    "input": "What is the meaning of life, the universe, and everything?"
  }'
```

关键点：
- Endpoint：**`/v1/responses`**（不是 `/v1/chat/completions`）
- Model 示例：**`grok-4.20-reasoning`**（Grok 4.20 的推理变体）
- Input 格式：**直接 `input` 字符串**，不是 `messages` 数组（Responses API 特征）
- 变量名：用户在他的 shell 里用的是 `$XAI_API_KEY`（我们的 .env.local 里存的变量名是 `GROK_API_KEY`，注意区分）

## 用户原话
> "grok api 好像还有一个 first query"

解读（待验证）：
- 可能指 `/v1/responses` 是 Grok 的 "first query" 入口（OpenAI Responses API 的特点是维持 conversation state，first query 会创建 response_id 供后续 turn 使用）
- 或者指 Grok 4.20 的某个 feature 叫 "first query"（需要查 docs）

## 对图像测试的暗示

这条信息明确的是**文字 endpoint**，不是图像 endpoint。图像 endpoint 仍需独立研究：
- 可能是 `/v1/images/generations`（OpenAI-compat 标准图像端点）
- 可能是 `/v1/responses` 配合 `modality: image` 参数（Responses API 的多模态能力）
- 可能是独立的 `/v1/imagine` 或 `/v1/images`

Agent A 应该优先抓 https://docs.x.ai/docs/api-reference 或类似 API 参考页确认图像端点。
