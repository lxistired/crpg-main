# 开源模型广泛测试总结 — 2026-04-18

Key: `sk-or-v1-3d3e...b18` | 12 模型 × 2 任务 = 24 并发 | 全部成功，0 refusal

## Tier 分类修正

- **Tier 1（2026 最新）**: glm-5.1 (04-08), qwen3.6-plus (04-02), nemotron-3-super-120b (03-12), qwen3.5-397b-a17b (02-16), qwen3-max-thinking (02-10), minimax-m2.5 (02-12), **kimi-k2.5 (01-27)**, step-3.5-flash (01-30)
- **Tier 2（2025-Q4）**: mistral-large-2512 (12-02), mistral-small-creative (12-17), deepseek-v3.2-speciale (12-01), **kimi-k2-thinking (11-06)**

## Director 排名（VGAI 合规 + 成本 + 延迟）

| 排名 | 模型 | VGAI issues | 成本 | 延迟 | 备注 |
|-----|------|------------|------|------|------|
| 1 | **nvidia/nemotron-3-super-120b-a12b** | 0 真issue | $0.0008 | 78s | 白菜价 + 极清晰 drop 原因 |
| 2 | **moonshotai/kimi-k2.5** | 0 真issue | **FREE** | 117s | 免费且合规 |
| 3 | **qwen/qwen3-max-thinking** | 0 真issue | $0.008 | 61s | thinking 模式助推 schema |
| 4 | z-ai/glm-5.1 | 0 真issue | $0.018 | 65s | 中文原生 |
| 5 | qwen/qwen3.6-plus | 0 真issue | $0.015 | 136s | 最新 qwen，1M ctx |
| 6 | qwen/qwen3.5-397b-a17b | 0 真issue | $0.026 | 71s | 大 MoE |
| 7 | stepfun/step-3.5-flash | 0 真issue | $0.002 | 107s | — |
| 8 | moonshotai/kimi-k2-thinking | 0 真issue | $0.017 | 359s | 极慢（thinking 耗时） |
| ✗ | minimax/minimax-m2.5 | **3 真违规** | $0.0016 | 41s | ms_waist_up 注入腿/脚 attr |
| ✗ | mistralai/mistral-large-2512 | **4 真违规** | $0.003 | 21s | ws_establishing 误注入 |
| ✗ | mistralai/mistral-small-creative | schema 失败 | $0.0004 | 9s | JSON 截断 |
| ✗ | deepseek/deepseek-v3.2-speciale | schema 失败 | $0.010 | 342s | 超长失控，未返 JSON |

**审计假阳性说明**: 10 个模型在 `back_reveal_walking` 注入 `black_pencil_skirt` 被我的审计脚本标 violation——但裙子绕身，`torso_back` 确实可见。真实 VGAI 应承认 torso_back 继承 torso。已从上表真违规中剔除。

## Script 排名（长度 2200-2800 字 + 克制感性 + 双支线）

| 排名 | 模型 | 字数 | 质量读样 | 成本 | 延迟 |
|-----|------|------|---------|------|------|
| 1 | **z-ai/glm-5.1** | 2353 | **顶级中文文学感**，意象最稠，改称 "苏晚" | $0.036 | 58s |
| 2 | **mistralai/mistral-large-2512** | 2673 | 扎实叙事，双支线结构清晰 | $0.004 | 66s |
| 3 | **minimax/minimax-m2.5** | 2380 | 对话自然，节奏沉稳 | $0.002 | 28s |
| 4 | moonshotai/kimi-k2.5 | 1625 | **质量极高但偏短** | FREE | 41s |
| 5 | stepfun/step-3.5-flash | 2979 | 略超长 | $0.001 | 133s |
| 6 | mistralai/mistral-small-creative | 2082 | 创意性 deviation（自己加中文名） | $0.0007 | 17s |
| 超长 | nemotron-3-super-120b-a12b | 14105 | thinking 泄漏到正文 | $0.004 | 37s |
| 超长 | deepseek-v3.2-speciale | 12422 | 延续 V3.2 verbose 问题 | $0.010 | 366s |
| 过短 | qwen3.6-plus | 1939 | 够但未到目标 | $0.014 | 130s |
| 过短 | qwen3-max-thinking | 1736 | 偏短 | $0.006 | 43s |
| 失败 | qwen/qwen3.5-397b-a17b | 461 | 几乎空回 | $0.019 | 274s |

**禁用话术命中**:
- nemotron-3-super-120b-a12b: 3 命中（她的签名款 / 她一贯的 / 如往常般）
- deepseek-v3.2-speciale: 同 3 命中
- 其余模型: 0 命中 ✓

## 推荐架构（基于广泛测试 + 先前测试）

```
Director 主力:  nvidia/nemotron-3-super-120b-a12b    # $0.0008, 78s, VGAI 干净
Director 备用:  moonshotai/kimi-k2.5                   # FREE, 117s, 中文原生
Director 高端:  qwen/qwen3-max-thinking                # $0.008, thinking 可溯源

Script 主力:    z-ai/glm-5.1                           # 2353 字, 文学感最强（但偏贵）
Script 经济:    mistralai/mistral-large-2512           # 2673 字, $0.004/篇
Script 白菜:    minimax/minimax-m2.5                   # 2380 字, $0.002/篇

Script 露骨:    (尚未广泛测)                          # 先前 Grok 4.20 + DS V3.2 方案备案
```

## 关键发现

1. **开源里 Director 角色合格者极多**: 8/12 通过 VGAI 合规（扣除假阳性）；原本担心 "只有 DS V3.2 能做" 不成立。
2. **Thinking 模式利 schema**: qwen3-max-thinking / kimi-k2-thinking 即便输出长链，JSON 结构依然严格。
3. **超长 verbose 是 DS 系 + nemotron 共性**: 32K / 14K / 12K 字全部来自这两家，其他模型 controllable。
4. **Mistral 系 schema 控制弱**: creative 版 JSON 截断、large 版 ws_establishing 误注入。
5. **qwen3.5-397b script 几乎空回**: 不稳定，弃选。

## 真违规细节

### minimax/minimax-m2.5（3 真违规，Director 弃）
- shot#1 `ms_waist_up` 注入 `sheer_black_tights` (leg)
- shot#1 `ms_waist_up` 注入 `black_ankle_boots` (foot)
- shot#5 `back_reveal_walking` 注入 `black_pencil_skirt` ← 假阳性

### mistralai/mistral-large-2512（4 真违规，Director 弃）
- shot#0 `ws_establishing`（人物太小）注入全套 wardrobe 3 项
- shot#5 同上假阳性

### 其他 8 模型仅触发假阳性（Director 均通过）

## 下一步待验证（脱离本次范围）

- [ ] 露骨度路由：纯 open-source 替代 Grok 4.20 的候选（需另测）
- [ ] Nemotron Director 路线的 "中文思维" 问题：drop reason 全是英文，可能影响 crpg 调试体验
- [ ] glm-5.1 Director + Script 双角色重叠 → 单模型方案可行性
- [ ] free tier kimi-k2.5 的 rate limit / sla 稳定性（长期可用否）

---

测试脚本: `/tmp/broad_opensource_test.py`
审计脚本: `/tmp/broad_vgai_audit.py`
明细: `_meta.json`, `_audit.md`
