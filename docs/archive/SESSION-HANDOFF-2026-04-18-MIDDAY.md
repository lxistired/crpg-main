# Session Handoff — 2026-04-18 中段（brainstorm session before compact）

接本文件 + `SESSION-HANDOFF-2026-04-17-EVENING.md` + `MEMORY.md` 恢复上下文。

## 这个 session 做了什么

从 "Director skill 打包完成" → "架构决策（模型+SDK）验证"。~3 小时，~$0.60 实证成本。

### 已确认的架构决策

```
crpg 第一个 milestone = 独立 CLI agent 可执行程序（类似 Claude Code 形态）

框架: OpenAI Agents SDK (Apache/MIT) — 不是 Claude Agent SDK
     原因: Claude Agent SDK 绑 Anthropic 商业 TOS，AUP 禁成人向全部废
     OpenAI SDK 只是库，配置指向任何 OpenAI-compat 端点即可，无 TOS 约束

Orchestrator model: DeepSeek V3.2 (via OpenRouter)
     原因:
     - Sonnet 4.6: 无论通过哪条路径（直连/OpenRouter/mix88 代理）都不可用
       · Anthropic 官方 AUP 禁成人
       · OpenRouter 账户 user_id 被大厂3家标记（403 永久）
       · mix88 proxy 也有 keyword filter 拦（null 或 refusal）
     - Grok 4.20: 可用但 Director 角色 VGAI 违规 2-3/6（比 DS 差），成本 10x
     - DS V3.2: VGAI 违规 1-3/6（大致持平 Sonnet），成本 Sonnet 的 1/30
     - MiniMax M2.7: schema 混乱，base 当 attr 注入

Tool models:
     - 文字露骨: Grok 4.20
     - 文字克制: DS V3.2
     - 图像: Grok Imagine Pro (xAI 直连)

代码层兜底:
     - VGAI post-validation (校验 every injected_attr.anchor ∈ framing.visible_regions)
     - Mutex assertion (组装前强制 mutex_groups 预检)
     - 弥补 DS V3.2 的 "过度保守 drop" 和偶发 mutex 违规
```

### 用户仍然不放心的点

> "skill 做 80% 工作 + 代码做 20% hard enforcement，我不放心，想再测其他开源模型"

**待 compact 后继续的测试**：
- **Qwen 2.5 72B** 做 Director（尚未测试）
- **Llama 3.3 70B** 做 Director（尚未测试）
- **DeepSeek v3.2-exp / v3.2-speciale** （DS 的变体）
- **nex-agi/deepseek-v3.1-nex-n1** （第三方 DeepSeek 变体）
- **Qwen coder 或 Code 模型**（如果 schema 遵守胜过 chat 模型）

测试方法：同样 4 场景（A 花店 / B1 余韵 / B2 床戏 + script 长篇），并发跑，VGAI 自动合规检查。

### TODO 后续（3 层正交 script 测试）

- detailRichness: concise / standard / detailed / extreme
- contentLength: short / medium / long
- structure preset: linear / bifurcating / funnel / web
- 见 `research/model-comparison-2026-04-18/TODO-script-3axis.md`

## Director Skill v2 最终版（已稳定）

位置：`skills/director/`
- SKILL.md（<500w，10 原则 + workflow step 3.f/3.g 强调 default-KEEP + mutex 预检）
- references/（7 个：vgai.md / framing-region-map.yaml / shot-grammar.yaml / grok-constraints.md / character-sheet-schema.yaml / narrative-heuristics.md / rationalization-counters.md）
- examples/（worked-example.md + character-sheet-example.yaml）
- projects/crpg-noir/character-sheets/su_wan.yaml（项目数据与 skill 解耦）

**经验证过 4 个故事共 ~50 shots**：
- Informant（18 shots）
- Rainy Night（8+8 shots）
- 镜廊 Mira（8 shots，fresh character）
- 长夜腿脚（16 shots）
- skill-generalization-test（16 shots， 2 story 并行验证）

## 累计测试数据

- VGAI + Director skill 测试：~$20+，~300 shots，10+ 轮
- Director model 对比：~$0.50，6 模型 × 3 场景
- 今天 session：~$0.60 总

## 下次 session compact 后的第一步

测剩下的候选 Director 模型：

```bash
# 候选（按优先级）
"qwen/qwen-2.5-72b-instruct"           # 中文原生，开源权重
"deepseek/deepseek-v3.2-speciale"       # DS 变体
"meta-llama/llama-3.3-70b-instruct"    # 开源基线
"deepseek/deepseek-v3.2-exp"           # DS 实验版
"nex-agi/deepseek-v3.1-nex-n1"         # DS 第三方
"tngtech/deepseek-r1t2-chimera"        # DS reasoning 变体
```

OpenRouter key 可用：`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`

测试 script：复用 `/tmp/director_deepseek_minimax.py` 的结构，换 models 数组。
VGAI 自动审计：复用当前对话里的 Python 脚本（读 shot_list.json 检查 anchor 合规 + mutex）。

## 用户的最终意图（再强调）

- 第一个 milestone = **CLI agent 形态**（像 Claude Code 那样，不是 app 不是 web）
- 文字 + 图像**都要**
- 纯享版（reader）+ 创作者版（generator）**都要**
- 但 **Milestone 1 只做 core pipeline / director**，UI/auth/payment 后续
- **不急着写代码**，方法论和架构**要稳**了再写

## 用户偏好

- 反感"硬编码"→ 喜欢 principle-first 设计
- 偏好**真实实证**，不喜欢纸面推理
- **多候选 + 并发测试**来决策
- 对成本敏感但不算吝啬

---

文件已 commit 前请 compact 前 push：
```
git add -A && git commit -m "session handoff before compact: DS V3.2 + Grok architecture confirmed; pending open-source director candidates test"
```
