# Session Handoff — 2026-04-18 Evening

接这份 + `SESSION-HANDOFF-2026-04-18-MIDDAY.md` + `SESSION-HANDOFF-2026-04-17-*.md` + `MEMORY.md` + `docs/superpowers/specs/2026-04-18-crpg-milestone-1-design.md` + `docs/superpowers/plans/2026-04-18-crpg-milestone-1-plan.md` 恢复上下文。

## 今天 session 做了什么

从 "设计 spec + plan 完成" → "M1 实施 21 任务全绿 + 7 轮 live E2E 迭代"。约 $7 烧图 + 文本。发现一堆方法论层 bug——**Director skill 单独测没问题，但 M1 pipeline（Skeleton → Director → Image）引入新 bug，skill 方法论需要进一步扩展**。

## Milestone 1 当前状态（branch `milestone-1-impl`）

- **21 plan tasks 全绿**：实施 plan 在 `docs/superpowers/plans/2026-04-18-crpg-milestone-1-plan.md`
- **单元测试**：65 passed + 1 skipped（live E2E opt-in，`CRPG_LIVE=1`）
- **pre-existing 失败**: `tests/test_config.py::test_missing_key_raises`——因为我们创建了真 `.env`，`load_dotenv()` 覆盖了 monkeypatch。可修（用 `monkeypatch.chdir(tmp_path)`）。
- **CLI 跑通**: `crpg generate --brief demo.md --out bundle/`
- **Bundle 结构**:
  ```
  bundle/
    story.json       骨架 + edges + meta
    characters.json  角色卡 + mutex + wardrobe_states
    prose/<beat>.md  每 beat 散文（落盘，不进 context）
    story.md         人读版（synopsis + 完整 prose 汇编）
    shots/<beat>/
      shots.json     Director 输出的 final_prompt + VGAI 审计
      shot-NNN.png   真图像
    meta.json        生成时间 / LLM 版本 / suffix 版本
  ```

## 关键 commits（新→旧）

```
c27c789  feat(director): base identity 2-tier gating + pose disambiguation + layer template
dcae489  feat(skeleton): generalization validated across 5 adult briefs (mutex physicality)
89dfc65  fixture: swap ankle boots for high heels in demo brief
b16fd6a  fix(skeleton,bundle): principle-based mutex guidance + persist shot lists
66746cb  feat(bundle): persist per-beat prose + auto-generated story.md
a9b7547  fix(xai): retry with exponential backoff on 429/5xx transient errors
e9144c9  fix(llm): json_object mode + retry-once for Skeleton/Director robustness
cccd275  fix(review): apply M1 review findings (xAI params, endpoint wiring, detail routing, sanitization)
[21 Phase tasks...] — 完整 M1 骨架
```

## 本 session 7 次 live E2E 迭代

| # | 失败点 | 修复 |
|---|-------|------|
| 1 | Skeleton 输出 char 3430 处 JSON 少逗号 | 加 `response_format=json_object` + retry |
| 2 | xAI 返 503 "model temporarily unavailable" | xAI client 加 exponential backoff retry |
| 3 | ✓ PASS (~8:01) — 首个完整 bundle | 但发现多个 bug (见下) |
| 4 | ✓ PASS (~6:44) — 无 prose 落盘 | 加 `write_beat_prose` + `write_story_md` |
| 5 | ✓ PASS (~4:45) — Skeleton 给 `[sheer_black_tights, black_ankle_boots]` 错 mutex | 改 SKELETON_SYSTEM 为原则式 mutex，用户指出我的 prompt 里的错示例是根因 |
| 6 | ✓ PASS (~5:14) — 踝靴款式丑 + 光腿 bug | brief 改 `高跟鞋`；加 shots.json 落盘可审；Skeleton 泛化 harness 5/5 clean |
| 7 | ✓ PASS — **feet_ecu 图里有脸 + 露趾 + 趾甲可见硬编码** | 加 Principle 1 2-tier base + layer template。**但 template 本身硬编码了"visible through"假设** |

## 未完待续的 **真 bug**（用户今晚指出，未修）

### Bug A — Layer template 隐含 "open-toe" 硬编码

`src/crpg/llm/prompts.py` DIRECTOR_SYSTEM 里我加的 layer template：
```
"feet wrapped in sheer tights fabric, red_toenails visible through the fabric"
```
**"visible through"** 这句假设趾甲必须可见 → 反推鞋必须 open-toe → Grok 画成 peep-toe。

但 brief 要的是 **closed stilettos**。闭合 pump + 丝袜 → 趾甲被鞋完全遮挡 → 实际**看不见**。

**修复方向（真方法论）**：
- 区分 **full occlusion → DROP attr**（不是 "visible through"）
- 区分 **partial occlusion → "visible on [non-occluded part]"**
- 区分 **no occlusion → 直接 inject**

### Bug B — Character schema 缺 `covers` 字段

```json
"black_stilettos": {"name": "black_stilettos", "anchor": "foot"}
```
只说 anchor=foot，**没说遮挡哪些 sub-anchor**。所以 Director 不知道趾甲被完全遮挡应 drop。

**修复方向**：扩展 `WardrobeItem`:
```python
class WardrobeItem(BaseModel):
    name: str
    anchor: Anchor
    covers: list[str] = []  # fully-occluded sub-anchors
```

例：
- `closed_pumps` covers=[toes, foot_top_inner]
- `peep_toe_pumps` covers=[foot_top_inner]
- `sandals` covers=[]
- `ankle_boots` covers=[toes, foot_top, ankle]
- `thigh_highs` covers=[leg_lower]

### Bug C — Skeleton 没生成 coverage

即使 schema 加了 `covers` 字段，Skeleton prompt 现在没教它怎么填。需要给 SKELETON_SYSTEM 加 footwear/wardrobe coverage 教学。

### Bug D — Director VGAI 没处理 occlusion

`src/crpg/validation/vgai.py` 只检查 `anchor ∈ visible_regions`，没检查 `attr.sub_anchor ∈ any_wardrobe_item.covers`。需要加一条：若 attr 的 sub-anchor 被某 wardrobe item 完全 occlude → drop。

### Bug E — Grok 两条腿渲染不一致

用户截图显示：一条腿有丝袜 + 泥点，另一条腿是肉色光腿。**这是 Grok 渲染的 limitation**，不是方法论 bug。可在 final_prompt 加 `"both legs wrapped in identical tights material"` 降低概率但无法根治。

### Bug F — Grok "stepping out of" 文字诱导错误脱鞋（已修）

但潜在的"自然语言诱导 Grok 行为错误"的问题仍存在。其他短语（"slipping off" / "undoing" / "loosening"）可能也有类似问题。`rationalization-counters.md` 的短语字典需要持续扩展。

### Bug G — Anime 鞋款细节差

brief 给 `黑色踝靴` 或 `黑色高跟鞋`——Grok 默认款式可能丑/粗糙。需要**style dictionary**：
- `黑色高跟鞋` → 具体展开为 `black patent leather pointed-toe closed pumps with 10cm stiletto heel, red sole`
- 不在 brief 层做，在 Director 或 Skeleton 层加 default style bank

这是 Director skill 的 M2 增强方向。

### Bug H — Principle 1 今天才发现 face-leak 问题

为什么 yesterday 测 Director 4/4 clean 但今天 feet_ecu 出脸？
**答**：昨天的 empirical 测试全是 `ms_waist_up / cu_face / hand_ecu` 等框位组合，**feet_ecu 的独立完整 prompt 假设下没跑过**。Director skill 的 empirical 验证覆盖不全。

修复方向：把 feet_ecu / hand_ecu / back_reveal_walking 加到 Director skill 的标准 empirical 回归测试里。

## 实施方法论 debt（skill 本身需扩展）

1. **`skills/director/references/wardrobe-coverage.md`**（新文件）——通用 footwear / hosiery / garment 的 `covers` 分类表
2. **`skills/director/references/character-sheet-schema.yaml`**——加 `covers` 字段定义
3. **SKILL.md Principle 1**——今天已细化 2-tier base，但**还需补**"occlusion drop"原则
4. **`skills/director/references/vgai.md`**——加 "occlusion branch" 规则（full / partial / none）
5. **`skills/director/references/rationalization-counters.md`**——持续扩充短语字典
6. **Director empirical regression**——必须覆盖 feet_ecu / hand_ecu / back_reveal 的完整基线
7. **Skeleton 泛化 regression**——harness 已经写好在 `research/skeleton-generalization/harness.py`，5/5 clean。后续新增方法论时必须 re-run 保证 regression。

## 当前对方法论的诚实评估

- **Director skill 在手写 character sheet + 正面框位下稳定**（昨天 4/4 clean 不是幻觉）
- **但 skill 没覆盖的边界**：
  - feet_ecu / hand_ecu 的 base 身份 gate
  - wardrobe 之间的 occlusion 层级
  - closed vs open-toe 鞋款的趾甲可见性
  - 两腿/两手对称渲染
- **M1 pipeline 把 Skeleton 加进来后**：Skeleton 的 character sheet 质量直接影响 Director。Skeleton prompt 原来有错示例（已修）。现在 Skeleton 没生成 `covers` 字段（待修）。

**用户的评价（原话）"完全没有按照 skill 来，昨天测导演 skill 都没有这些问题的"** 是对的。我今天加的 Layer template "visible through" 是硬编码，不应该出现在一个 principle-based skill 里。同样，`covers` 字段缺失意味着 Director 缺了一条重要的 occlusion gate 原则。

## 下次 session 第一步

1. **扩展 Character schema 加 `covers` 字段**（types.py + characters-sheet-schema.yaml）
2. **写通用 footwear coverage 表**（`skills/director/references/wardrobe-coverage.md`）
3. **Director VGAI 增加 occlusion gate**（validation/vgai.py + DIRECTOR_SYSTEM 规则）
4. **Skeleton 教学 coverage**（SKELETON_SYSTEM + 泛化 harness 加 coverage 校验）
5. **移除 Layer template 的 "visible through" 硬编码**，改为由 occlusion 分支决定
6. **扩展 Director empirical regression**（加 feet_ecu / hand_ecu 的独立基线测试）
7. **然后再烧 1 次 E2E 验证**（M1 真正 shippable）

之后才算 M1 完整。

## 如果你要直接试 live E2E

```bash
# env 已配好 (.env 存在, OpenRouter + xAI keys)
cd /Users/lxxxxxx/个人项目/crpg
source .venv/bin/activate
CRPG_LIVE=1 pytest tests/test_e2e.py -v -s
```

## 用户偏好（本 session 强调的）

- **严禁硬编码**："visible through" 级别的隐含视觉假设都算硬编码
- **prose/story/shots 落盘不进上下文**——数据保护一致
- **方法论问题不能拖 M2**——M1 必须"满意"才能 ship
- **"垃圾"不接受**——图质量/渲染一致性都要过关
- **测试覆盖要真实**——Director skill 不能只测 ms/cu/hand_ecu 就声称过关

## 产出文件路径

- Spec: `docs/superpowers/specs/2026-04-18-crpg-milestone-1-design.md`
- Plan: `docs/superpowers/plans/2026-04-18-crpg-milestone-1-plan.md`
- 实施: `src/crpg/` + `tests/`
- 7 次 E2E bundles: `bundles/e2e-2026-04-18{,-v2-with-prose,-v3-final,-v4-after-3fixes}/`
- 泛化 harness: `research/skeleton-generalization/harness.py` + `round_*/`
- Director skill: `skills/director/SKILL.md` + `references/*`

---

**compact 后第一步**：读这份 handoff + MIDDAY handoff + MEMORY.md + 那两个 doc。然后按上面"下次 session 第一步"的清单开始修 Bug A-D。
