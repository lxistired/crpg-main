# Session Handoff — 2026-04-19 Late Night

接这份 + `SESSION-HANDOFF-2026-04-18-NIGHT.md` + `MEMORY.md` 恢复上下文。

## 这一 session 总览

起点：2026-04-18 晚的 agent-based M1 first live run（4 beats / 18 真图 / 12.5 min），用户发现**人物不一致、服装不一致、prose 没用细腻模式（1100-1600 字 vs 目标 2500）、三轴正交没体现**。

终点：
- **Agent 架构 + 11 skill 文档 + 12 tools**，能跑 end-to-end（目前 text-only stub 验过，真图未验）
- **Visual DNA 7-层**（Style Preamble Layer 1 + Anchor Strategy Layer 7 + Wardrobe visual_description Layer 3 + Direction Layer 8 + Layered Garment Visibility Layer 10）全部嵌入 skill + tool
- **Sonnet 做完 prose audit**，发现 4 个 root-cause 问题，tool 层 + skill 层抽象原则都已修
- **21 个 task 完成，7 个 pending**（最大的 pending 是 speed 问题）

## Agent 架构（已完全落地）

```
一个 Agent: MiniMax-M2.7-HighSpeed @ api.minimaxi.com/v1
  instructions: src/crpg/agent/main_agent.py (4500+ 字)
  tools (12 个):
    read_brief, read_skill, list_skill_references, read_skill_reference,
    write_story, write_characters, write_beat_prose, write_beat_shots,
    validate_vgai, render_anchor, render_image, finish_bundle
  context: AgentState (brief / bundle_writer / xai_client / anchors /
           story_data / characters_data / failed_shots / prose_retry_history)

3 个 skill 模块:
  skills/skeleton/  (5 references: mckee-principles, structure-presets,
                     mutex-coverage (含 grooming→sub_anchor 词表), node-types
                     (含 choice 结构契约), three-modes)
  skills/script/    (5 references: game-writing-rules (含 R8 对话必 render),
                     anti-melodrama, three-modes-script, poetic-interpretation,
                     banned-phrases)
  skills/director/  (9 references: style-preamble (Layer 1), direction-layer
                     (Layer 8), occlusion, vgai, framing-region-map,
                     shot-grammar, grok-constraints, character-sheet-schema,
                     narrative-heuristics, rationalization-counters,
                     provider-hardening-suffix)
```

## 今天修完的问题（按时间序，全绿）

### 基础设施
- **httpx timeout 修复** (src/crpg/agent/main_agent.py): `Runner.run_streamed()` 走 SSE，MiniMax "thinking" 60-180s 会超 httpx 默认 5s read timeout。改 `httpx.Timeout(connect=30, read=600, write=60, pool=30)`。

### Schema 扩展（tests/test_types.py 全绿）
- `Shot.aspect_ratio: str | None`（#72）
- `Shot.anchor_ref: str | None`（e.g. `"su_wan:body"` | `"su_wan:face"`）
- `Shot.characters_in_frame: list[str]`
- `WardrobeItem.visual_description: str`（#75，默认 ""，Skeleton 应必填）
- `WardrobeItem.disambiguation_layers: list[str]`（Layer 10 高先验服装才填）
- `StoryMeta.poetic_mode: bool`（#69，默认 True，alias=poeticMode）
- `BeatType` 加 `climax`

### Validator 扩展
- `validate_shot / validate_shot_list` 加 `extra_characters` 参数（#73）→ 双人镜头 Kai 的衣物不再 unknown_attr
- `REGION_MAP` 从 8 → 24 个框位（#85）：加 over_the_shoulder, ots, cu_chest_up, ecu_face, leg_ecu, two_shot_full, pov_first_person, low/high_angle_ms/full, back_reveal_standing 等

### Agent 工具层
- **#82** `write_story/characters/shots` 双重编码：coerce 接受 dict-or-string，失败时返回"RETRY with NATIVE JSON object, not stringified"
- **#83** `write_beat_prose` 字数 REJECT 消息中文化 directive + deficit + 具体扩展方向 + 震荡/多次检测
- **#68** `write_beat_prose` 强制 ±10% targetWordCount
- **#84** `write_beat_shots` 校验每 shot `final_prompt` 前 400 字符包含 Style Preamble 签名
- **render_anchor** 新 tool：每个 character × {body, face} × Visual DNA Layer 7 anchor（存 `_anchors/<char>_<type>.png`，Grok image_url 用）
- **render_image** 加 `anchor_ref` 参数 + moderation 自动重试 3 次（#79）→ 失败写 state.failed_shots 继续 bundle
- **validate_vgai** 加 `extra_character_names` 参数（#73）

### CJK 字数 + 对话 elision + mandated quote（根据 sonnet audit 发现）
- **_cjk_char_count()**: 只数 U+4E00–U+9FFF，剥离 self-report 括号（如 `（约2500字）`）
- **_DIALOGUE_ELISION_MARKERS**: 10 个具体中文短语（"她不记得具体说了什么" 等）正则拒
- **_WORD_COUNT_SELF_REPORT**: 幻觉字数脚注正则拒
- **_extract_mandated_quotes()**: 从 beat.synopsis 的 「」/『』 里提取必须 verbatim 出现的台词
- 10 个单元测试在 tests/agent/test_prose_checks.py 全绿

### Skill 抽象原则（刚才这一轮，非硬编码）
- **skills/script/SKILL.md**: 加 "Synopsis is a contract" 章——mandated 引号台词 verbatim，negative/positive 约束都绑定
- **skills/script/SKILL.md** self-check 加：CJK 字数 / synopsis quotes 齐全 / 交换必 render
- **skills/script/references/game-writing-rules.md**: 加 Rule 8 "Dialogue is rendered, never mentioned" — 纯原则，无具体短语
- **skills/skeleton/references/node-types.md** choice 节加 "Structural contract — choice beats end UNDECIDED" — 泛化到任何 genre，无具体角色/场景

## 今天 live text-only short run（bundles/e2e-agent-2026-04-18 基线 + /tmp/crpg-text-short）

- 26.6 min（主要时间在 prose 字数震荡 + shots 设计）
- 8 beats + 8 prose + 4 anchors + 28 shots + 28 stub PNGs
- Validate VGAI all CLEAN
- harness 自报 ✓ 全过，**但 sonnet audit 发现**：
  1. **字数作弊**：agent 在 prose 末尾贴 `（约二千五百字）` 脚注混 `len(prose)`，真 CJK 字符比 target 短 18-26%（b1 actual 2013 / target 2500）
  2. **b2 choice beat 里直接做了决定**（「走吧。」在 choice beat 中，branches 成既成事实）
  3. **b4b 漏写 synopsis mandated 台词**「你不想让我停。」
  4. **b3b 对话 elision**："她不记得具体说了什么" 跳过关键 Kai 对话
- **亮点**：b4a 手机删号 beat（三次按键 + 红色确认弹窗 + 3mm 间距的精度）获 sonnet "STRONG" 评

## 关键 commits（新→旧）

```
[pending]  feat(skills): abstract root-cause principles for sonnet-audit findings
52db6d8    fix(tools): directive errors for double-encode + prose reject + style byte-lock + region coverage
baa296a    feat(skills): occlusion principle + sub_anchor taxonomy lockdown
0db3fd0    feat(vgai): occlusion gate drops covered grooming attrs
323ed4d    feat(types): add 'climax' as distinct BeatType
8c64325    feat(schema): Shot aspect_ratio + WardrobeItem visual_description + StoryMeta poeticMode + multi-char VGAI
e357d5d    feat(skills): add skeleton + script skills extracted from daisy V6 + McKee
5b63258    feat(types): add WardrobeItem.covers for occlusion gating
3239881    test: drift-detection guards against skill-to-src copying
```

## 还未解决的问题（按优先级）

### P0 — 必须在下一轮 text-only run 前验证

**验证**：把 4 个 sonnet-audit 修复（1 tool + 3 skill 原则）放一起跑一次 text-only short，sonnet audit 第二次验。若通过 → 可进真 xAI。

具体命令：
```bash
cd /Users/lxxxxxx/个人项目/crpg
pkill -9 -f text_only_harness  # 清旧
rm -rf /tmp/crpg-text-short
.venv/bin/python -u research/agent-streaming-debug/text_only_harness.py \
  tests/fixtures/demo_brief.md /tmp/crpg-text-short \
  > /tmp/text_short_v2.log 2>&1 &
# 用 Monitor 工具 tail -f 跟踪 + grep
```

然后重派 sonnet audit：见 `a107c0ed1330ae296` agent prompt 模板，改成读 `/tmp/crpg-text-short/prose/`。

### P0 — 速度严重偏离目标

| 模式 | 现实 | 用户目标（不含生图） |
|------|------|---------------------|
| short | 14 min 文字 | **2 min** |
| medium | ~50-70 min 文字 | **5 min** |
| long | ~2-4 hr 文字 | **10 min** |

**根因**：MiniMax-M2.7 HighSpeed 是 thinking 模型，单 call 3-6s + 生成；8 beats × 5 retries × 20s 每 retry = 10 min 只在 prose 阶段。

**提速路径（待定）：**
- **档 2（推荐，~4 小时）**：task #67 kimi-0905 @Groq 做 Script worker + Director worker。Agent 只做 skeleton + 编排。Prose 8 个并发 kimi 调用 = ~10s 而不是 10 min。
- **档 3（激进）**：全 Groq pipeline（连 skeleton），short 可能到 2-3 min，但未验证 kimi 能稳定 McKee 结构化输出。

**用户原话**："速度不包括生图的我提的那几个预期"——所以上面目标都是**纯文字**时间，图像另算。

### P1 — 下次真 xAI run 才能发现的问题
- **MiniMax 的 `<think>...</think>` 块可能被写进 final_prompt**，流到 Grok。tool 应该 strip 再写。
- **anchor 机制 real xAI 未验**——stub 下 agent 正确调 render_anchor + image_url，但 Grok 真实 API 对 base64 data URI 行为未验（Sonnet research 说能用，但没跑过真调用）。
- **真 xAI 成人内容 moderation**：Grok 可能挡，有 auto-retry 兜底，但超过 15% 挡就需要换 fallback（Sonnet research 建议 Seedream 5.0 Lite）。

### P1 — 中篇/长篇还没跑过
- `tests/fixtures/medium_detailed_brief.md` 已写（民国谍战，林九薇+周时磊），没跑
- 长篇 brief 没写

### P2 — 低优 task
- **#52**：skills/director/references/wardrobe-coverage.md（其实 mutex-coverage.md 已经涵盖大部分）
- **#54**：research/skeleton-generalization/harness.py 加 covers 断言
- **#55**：Director 对 feet_ecu/hand_ecu/back_reveal 独立回归

## 开发纪律（硬约束，memory 里有）

1. **agent-first**（`feedback_crpg_agent_first.md`）：不把 skill 内容抄进 src/*.py，drift-test 强制
2. **skill vs tool 分工**（`feedback_crpg_skill_vs_tool_split.md`，刚加）：skill 陈述抽象原则 + PROTAGONIST 占位符；tool 做机械检测（含具体正则 OK）；禁止具体角色名/具体中文短语/具体场景例进 skill 文档
3. **数据落盘**（全局）：prose/shots/images 必须 write_*_tool 落 bundle，不灌 agent context

## 文件索引（下次 session 第一眼看哪）

```
SESSION-HANDOFF-2026-04-18-NIGHT.md       ← 前天的 baseline
SESSION-HANDOFF-2026-04-19-LATE-NIGHT.md  ← 这份
~/.claude/projects/-Users-lxxxxxx------crpg/memory/MEMORY.md  ← 记忆索引（已更新）

src/crpg/
  agent/
    main_agent.py        # build_main_agent + INSTRUCTIONS (4516 chars)
    tools.py             # 12 tools + _cjk_char_count + _extract_mandated_quotes 等
    state.py             # AgentState + anchors / failed_shots / prose_retry_history
    runner.py            # run_agent(brief, out_dir)
  validation/vgai.py     # REGION_MAP (24) + occlusion gate + multi-char
  types.py               # Shot/WardrobeItem/StoryMeta/BeatType 全新字段
skills/                  # 3 skills × SKILL.md + references/*.md 全
research/agent-streaming-debug/
  harness.py             # live streaming agent
  text_only_harness.py   # stub xAI text-only
  audit.py               # bundle VGAI 合规
research/image-consistency-2026-04-18/
  RESEARCH.md            # Sonnet 做的大型 image 一致性研究
  PROSE-AUDIT-TEXT-SHORT.md  # Sonnet 做的 prose audit（4 个 finding 的来源）

tests/
  test_no_skill_drift.py           # 3/3 绿 — agent-first 守门
  test_types.py                    # 14/14 绿 — schema
  validation/test_vgai.py          # 9/9 绿 — VGAI + occlusion
  agent/test_prose_checks.py       # 10/10 绿 — CJK/elision/mandated quote
  fixtures/
    demo_brief.md                  # 都市 noir (Su Wan + Kai)
    medium_detailed_brief.md       # 民国谍战 (林九薇 + 周时磊) — 没跑
```

## 下次 session 第一步

**若目标是跑出第一个高质量 image bundle**：
1. 跑 text-only short 验证 4 个 sonnet-audit 修复 → 派 sonnet 再 audit
2. 若 audit 通过 → 跑 full live E2E（真 xAI）对 demo_brief
3. 用 opus sub-agent 读图检查（人物一致性 + 服装一致性 + mid-action vibe）

**若目标是速度**：
1. 建 task #67 的 script_worker + director_worker（kimi @Groq 封装 + 预装 skill 内容作 system prompt）
2. agent instructions 改成"Script/Director 阶段 invoke_worker"模式
3. 预期 short 从 14 min → 3-5 min

**若目标是 medium/long 基线**：
1. 跑 text-only medium (tests/fixtures/medium_detailed_brief.md)，验 poeticMode 不同值差异
2. 写 long brief，跑 text-only long

## 环境与密钥（.env 已就位，不要重配）

```
MINIMAX_API_KEY=sk-cp-...       主 agent
MINIMAX_ENDPOINT=https://api.minimaxi.com/v1
MINIMAX_MODEL=MiniMax-M2.7-HighSpeed
OPENROUTER_API_KEY=sk-or-v1-... Script worker 用（task #67 未做，.env 已放好）
XAI_API_KEY=xai-...             图像
```

```bash
# 直接跑 text-only short
.venv/bin/python -u research/agent-streaming-debug/text_only_harness.py \
  tests/fixtures/demo_brief.md /tmp/crpg-text-short
# 直接跑真 xAI live E2E
.venv/bin/crpg generate --brief tests/fixtures/demo_brief.md \
  --out bundles/e2e-v3-$(date +%Y-%m-%d) --max-turns 300
```

---

**compact 后恢复顺序**：
1. 读这份 + `MEMORY.md`
2. 按"下次 session 第一步"选目标
3. 所有 agent bug 修复必须分清楚 **skill 原则 vs tool 机械**（memory `feedback_crpg_skill_vs_tool_split.md`）
