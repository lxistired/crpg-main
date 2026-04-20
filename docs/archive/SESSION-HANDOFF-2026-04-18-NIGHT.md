# Session Handoff — 2026-04-18 Night (Agent-Based M1 First Live Run)

## 今天这一 session 从哪里到哪里

**起点**：老 M1（纯代码 pipeline + kimi）。SESSION-HANDOFF-2026-04-18-EVENING.md 列了 8 个 bug (A-H)、7 层方法论 debt，图像质量不稳（开放鞋、光腿、脸漏进 feet_ecu 等）。用户明确指出："我整个项目都是希望基于 agent 的，代码只是 agent 的工具啊"——老 M1 把 Director skill 的 principle/red-flags 抄进 Python 字符串，是有损压缩。

**终点**：
- 全新 agent-based M1 跑通 live E2E，出 4 beats + 18 真图 + 所有 prose 落盘。
- Drift-test 在 CI 里红着直到 Python 源码不再包含 skill 原文。
- 52/53 unit test 绿（1 个 `.env` monkeypatch 冲突的 pre-existing）。
- Director skill 加了 Principle 4b (occlusion gate) + `references/occlusion.md`。
- VGAI validator 有 `occlusion` kind + 9/9 tests。

---

## 架构终态（已定，别再改）

**一个 agent** (MiniMax-M2.7-HighSpeed @ `api.minimaxi.com/v1`)，拥有 3 个 skill：
```
skills/skeleton/SKILL.md  + 5 references (mckee-principles, structure-presets,
                                           mutex-coverage, node-types, three-modes)
skills/script/SKILL.md    + 5 references (game-writing-rules, anti-melodrama,
                                           three-modes-script, poetic-interpretation,
                                           banned-phrases)
skills/director/SKILL.md  + 9 references (vgai, framing-region-map, shot-grammar,
                                           grok-constraints, occlusion (new),
                                           rationalization-counters, narrative-heuristics,
                                           character-sheet-schema, provider-hardening-suffix)
```

**11 个 function_tool**（`src/crpg/agent/tools.py`）：
- read_brief
- read_skill(name), list_skill_references(skill), read_skill_reference(skill, ref)
- write_story(story), write_characters(chars)
- write_beat_prose(beat_id, prose), write_beat_shots(beat_id, shots)
- validate_vgai(shots, character_name)
- render_image(beat_id, shot_id, prompt, aspect_ratio)
- finish_bundle(summary)

**图像仍是纯 API** (Grok Imagine Pro @ xAI) — 不是 agent，是 agent 的工具。

**Runner loop**：`src/crpg/agent/runner.py` — Python 侧只做 config 加载、AgentState 构造、Runner.run、等 finish。不做业务决策。

## 今天已修 + 落盘的东西

| 提交 | 内容 |
|------|------|
| 3239881 | drift-detection test（4 个 phrase 命中旧 prompts.py 导致 RED，强制重构） |
| 5b63258 | `WardrobeItem.covers: list[str]` 字段 + 2 tests |
| e357d5d | skills/skeleton + skills/script 从 daisy V6 提炼（10 份 .md） |
| _agent 实施_ | src/crpg/agent/ 新建；删 llm/prompts.py llm/suffixes.py llm/openrouter.py 和 passes/skeleton|script|director.py 和 orchestration/pipeline.py；CLI 改 dispatch agent |
| 323ed4d | types.py: BeatType 加 "climax"（McKee Principle 9） |
| 0db3fd0 | vgai.py occlusion gate + 4 新 tests（sub_anchor 在 covers 里就 drop） |
| baa296a | Director SKILL.md 加 Principle 4b + references/occlusion.md + skeleton mutex-coverage.md 加 grooming→sub_anchor 标准库 |

## 今天 first-ever live E2E（brief = tests/fixtures/demo_brief.md）

**Bundle**: `bundles/e2e-agent-2026-04-18/` — **保留不要删**，作为 baseline 对照用。

- story.json 4 beats (b1, b2, b3A, b3B), bifurcating, 都市 noir
- characters.json: su_wan + kai（都带完整 covers）
- prose/*.md: 4 × 1100-1600 字（**ISSUE 1：目标 2500 字没达到**）
- shots/*/shots.json + 18 × PNG (4-6 MB/张)
- story.md 16.8 KB（auto-assembled）

**Agent wall time：12.5 分钟** · 约 60 次 tool call · max_turns=300 远远没到

**Live streaming harness**: `research/agent-streaming-debug/harness.py` 保留下次直接用
**Audit script**: `research/agent-streaming-debug/audit.py` 保留
**Stream log**: `research/agent-streaming-debug/stream-2026-04-18-22-00.log` 保留

**Audit 结果**：18 shots · 3 violations（全是 `unknown_attr`，因为 validate_vgai 只接受一个 character_name，在双人 shot 里 Kai 的衣物被误报）。**非 agent 错，是 validator 限制**（ISSUE 4）。

## 用户亲自指出的质量问题（今晚看图后，全部未修）

### ISSUE 1 — Prose 没达到 detailed 模式的 2500 字

每 beat 实际 1100-1600 字。daisy 的 detailRichness=detailed 目标是 **2500 字** (`skills/script/references/three-modes-script.md` 里明确写了)。agent 没照目标字数写。

**可能原因**：
- agent 可能按最省力的写法，不严格遵守 targetWordCount
- skill 里说"不超过 beat.targetWordCount ±5%"但没强调下限
- 或 agent 把字数算错了（中文字符 vs token）

**修复方向**：
- `write_beat_prose` tool 在 accept 前检查字数，低于目标 -10% 拒绝 + 返回"字数不足 XXXX/2500"让 agent 扩写
- 或 Script skill 改措辞从 "don't exceed" 变 "**must hit within ±10% of targetWordCount**"

### ISSUE 2 — 人物没有一致性

跨镜头 Su Wan 发型 / 五官 / 妆容 / 气质 有差异。Kai 也有差异。

**根因**：Grok Imagine 每张图独立 render，没有 character LoRA / reference image 支持。就算 prompt 一样，也会有随机。

**修复方向**（从轻到重）：
- 轻：把 base identity 写得更死板 + 每张图用完全相同的 base 字符串
- 中：用 Grok Imagine 的 reference image 参数（如果支持）—— 生完第一张"canonical"图后把它当参考
- 重：换模型（Seedream 4.5 / 其他有 identity lock 的）

### ISSUE 3 — 服装没有一致性

同一 wardrobe_state 下跨镜头服装看起来不一样。

**根因**：同上 + 服装描述在 prompt 里可能被模型"创作性理解"。

**修复方向**：
- 每个 wardrobe_state 配一个"canonical 描述串"，冻结措辞
- Director agent 组装 final_prompt 时把这个串原样 copy，而不是重述

### ISSUE 4 — validate_vgai 不支持多角色

当前 tool 签名 `validate_vgai(shots, character_name: str)`，双人镜头 Kai 的衣物被当 `unknown_attr`。

**修复方向**：
- `validate_vgai(shots, character_names: list[str])` 或
- shot 结构内加 `focus_character: str` 字段，validator 每 shot 查自己的 char

### ISSUE 5 — 三轴正交没体现

daisy 的 `poeticMode / detailRichness / contentLength` 是独立正交 3 轴。今天的 agent 虽然在 story.meta 写了 `detailRichness=detailed / contentLength=short / structure=bifurcating`，但：
- **poeticMode 字段缺失**（agent 没 emit）
- prose 质量看不出诗意/字面模式差异
- targetWordCount 被 agent 自己随意降级

**修复方向**：
- Skeleton skill 强制 emit `poeticMode: true|false` 字段
- Script agent 在写 prose 前必须显式声明当前 `(poeticMode, detailRichness)` 组合
- 可能需要把三轴写到 `story.meta` + 每 beat 继承

### ISSUE 6 — 以及上次提到过但还未修的自愈 bug

（agent 自己绕过去了，但不该让它每次都绕）

- **write_story 第一次传 JSON 字符串**：tool 应两种都接受
- **write_characters 两次调用**（第一次漏 Kai，第二次补上）：instructions 应明确"一次列全所有 named character"
- **write_beat_shots 3 次才对**：Shot schema 缺 `aspect_ratio` 字段

## 测试方法论（保留下来）

**这次用 `Runner.run_streamed()` + monitor tail grep** 的方式观察 agent，非常好用：
- 每个 tool call 实时打到 stderr
- 可以看到 agent 在哪一步卡
- 可以看到 agent 是否自愈 + 怎么自愈

`research/agent-streaming-debug/harness.py` 就是这个 harness 的可复用版本。下次改 tool / skill 后直接跑 `python research/agent-streaming-debug/harness.py` 即可看全流程。

**Audit 脚本** `research/agent-streaming-debug/audit.py` 可以对任何 bundle 跑 VGAI 合规检查。下次跑完也跑一遍 audit。

---

## 下次 session 第一步（按优先级）

1. **修 ISSUE 1**（prose 字数不达标）—— 最直接影响质量
2. **修 ISSUE 5**（三轴正交被吃）—— 方法论完整性
3. **修 ISSUE 6**（3 个自愈 bug）—— tool ergonomics
4. **修 ISSUE 4**（validator 多角色）—— 审计完整性
5. **修 ISSUE 2/3**（人物/服装一致性）—— 最难，可能要换模型或上 reference image 模式
6. **重跑 live E2E** 对照 `bundles/e2e-agent-2026-04-18/` 看改进

---

## 关键文件速查

```
src/crpg/agent/
  __init__.py
  main_agent.py         # build_main_agent(cfg) + INSTRUCTIONS
  runner.py             # run_agent(brief, out_dir, cfg)
  state.py              # AgentState dataclass
  tools.py              # 11 function_tool

skills/
  director/             # 今天加 occlusion.md + Principle 4b
  skeleton/             # 今天新建 (5 references)
  script/               # 今天新建 (5 references)

tests/test_no_skill_drift.py   # 3/3 绿 — skill 源码隔离保护
tests/validation/test_vgai.py  # 9/9 绿 — 含 4 个 occlusion 测试

research/agent-streaming-debug/   # 今晚刚存的测试 harness
  harness.py           # streaming + stderr tool-call trace
  audit.py             # bundle VGAI 合规审计
  stream-2026-04-18-22-00.log  # 这次 live run 的全 trace

bundles/e2e-agent-2026-04-18/     # 今晚的 baseline bundle — 不要动
```

## .env 布局

```
MINIMAX_API_KEY=sk-cp-...          # 主 agent
MINIMAX_ENDPOINT=https://api.minimaxi.com/v1
MINIMAX_MODEL=MiniMax-M2.7-HighSpeed
OPENROUTER_API_KEY=sk-or-v1-...    # script worker（M2 接入 kimi 时用）
XAI_API_KEY=xai-...                # 图像
```

## 如果要现在就再跑一次 live E2E

```bash
source .venv/bin/activate
.venv/bin/python research/agent-streaming-debug/harness.py 2>&1 | tee /tmp/run2.log
# 完了跑 audit
.venv/bin/python research/agent-streaming-debug/audit.py
```
