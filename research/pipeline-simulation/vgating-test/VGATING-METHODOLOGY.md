# Visibility-Gated Attribute Injection (VGAI) Methodology

**产出背景**：在 Grok Imagine Pro 上做了 22-shot 针对性测试（2026-04-17 晚），证明了 prompt 中写属性的"何时写、何时不写"存在可系统化的规则。本文档是给 Shot Director LLM（以及未来其他 LLM）使用的 prompt 写作指南。

## 核心定理

> **VGAI Rule**
> 
> 一个**角色属性**只应在**该属性的锚定身体区域（anchor region）出现在当前 shot framing 可视范围内**时，才写入 prompt。
> 
> 超出 framing 的属性写入，会触发 4 种 Grok 失败模式之一，破坏 shot 的预期。

**适用范围**：Grok Imagine Pro（grok-imagine-image-pro）已验证。原理（diffusion + attention-based generation）对其他 diffusion 模型（FLUX/Nano Banana/GPT Image）应当同样适用，未充分验证。

## 4 种 Grok Failure Mode（超框注入的后果）

| Mode | 现象 | 实例 |
|------|------|------|
| **1. Framing Expansion** | Grok 扩大 framing，把属性的区域拉进画面 | `CU face + pantyhose` → 结果是 3/4 body seated，CU 消失（本测 k02） |
| **2. Attribute Drop** | Grok 忽略属性，保 framing | `feet ECU + eye_detail` → 干净的脚特写，eye_detail 被丢（本测 m02） |
| **3. Composite Cheating** | Grok 拼接不同区域成一张画（违反单 framing 规则） | `feet ECU + earring` → 前景脚 + 画面角落塞了个带耳环的脸（本测 m06） |
| **4. Proxy Substitution** | 属性 color / texture 迁移到 framing 内的类似区域 | `CU face + 红脚甲` → 红色迁移到手指甲（本测 m11） |

**关键洞察**：Grok 不会"在脸上长出袜子"（脱离物理）。它会**改变 framing**、**丢属性**、**拼接**或**替换到代理区域**——都是"合理但破坏预期"的行为。

## Framing → Visible Region 映射表

以下是经测试验证的"每个 framing 下 Grok 会渲染哪些身体区域"：

| Framing | 代号 | Grok 会渲染的身体区域 | 可安全注入的属性 |
|---------|------|---------------------|---------------|
| Eye Extreme Close-Up | `eye_ecu` | 眼睛、睫毛、眉毛部分 | eye_detail（虹膜、睫毛） |
| Hand Extreme Close-Up | `hand_ecu` | 手掌、手指、指甲 | fingernail polish, rings, bracelets |
| Ear Close-Up (3/4 profile) | `ear_cu` | 耳、颊、下颌、部分颈 | earrings, jaw accessories |
| Feet Extreme Close-Up | `feet_ecu` | 脚、脚踝、下小腿 | toenail polish, anklet, toe rings |
| Leg Extreme Close-Up | `leg_ecu` | 大腿-小腿，可能含膝 | pantyhose/stockings, skirt hem |
| Close-Up Face | `cu_face` | 脸、颈、上肩、耳 | lipstick, earrings, necklace |
| Medium Shot Waist-Up | `ms_waist` | 头到腰，常含手 | lipstick, earrings, nails, torso wardrobe |
| Full Body (shoes) | `full_body` | 全身，脚藏鞋内 | lipstick, earrings, nails, pantyhose, dress, shoes |
| Full Body Barefoot | `full_body_barefoot` | 全身 + 脚趾 | lipstick, earrings, nails, toenails, dress |

**边界规则**：
- **Eye ECU ≠ iris-only**：实际 Grok 会渲染眼周（眉/鼻梁），但 **不** 渲染嘴/颈/手。pure eye attr 能进，lipstick/earring 进了会触发 Mode 1。
- **CU face 包含耳**：earring 可以注入 CU face。但 necklace 要谨慎（颈是否在 framing 边界）
- **MS 框位含手的概率取决于姿势**：prompt 里若明确"hands folded in lap" → 手在 frame，fingernails 可注入；"hands off-frame" → 不宜。
- **Full body 覆盖脚取决于鞋**：shoes→脚藏；barefoot→脚露（并含脚趾）
- **Full body + 高跟鞋**：脚趾被鞋覆盖，toenails 属性不应注入

## Shot Director LLM 算法

```
Given:
  - character_sheet: dict of { attribute_name: {value, anchor_region} }
  - shot: { framing, scene, pose, ... }

Procedure:
  1. base_prompt_parts = [scene, pose, framing, character_sheet.region_independent]
     # 只放 hair / skin tone / eye color / face structure / base emotions
     # 注意：角色的"长期默认属性"（红唇、红指甲、连裤袜等）不放在 base
  
  2. visible_regions = FRAMING_REGION_MAP[shot.framing]
     # 查表得到这个 framing 会渲染哪些区域
  
  3. for attr_name, attr in character_sheet.anchored_attributes:
         if attr.anchor_region in visible_regions:
             prompt_parts.append(attr.value)
         # else: 不写入
  
  4. Apply any shot-specific overrides (e.g., "today she is barefoot")
     这些 override 优先级高于 character_sheet 默认
  
  5. Return assembled prompt
```

## 实操建议

### 1. Character Sheet 结构

```yaml
character:
  name: "Su Wan"
  base:                  # always in prompt
    - "28, Chinese"
    - "long straight black hair parted to one side"
    - "fair skin"
    - "dark brown eyes"
    - "soft jawline"
  anchored_attrs:        # inject only when anchor_region in visible_regions
    - name: "lipstick"
      value: "red lipstick"
      anchor: face
    - name: "fingernails"
      value: "glossy red fingernail polish"
      anchor: hands
    - name: "earrings"
      value: "jade teardrop earrings"
      anchor: ears
    - name: "legwear"
      value: "sheer black full-length pantyhose"
      anchor: legs
      excludes_with: [barefoot]
    - name: "toenails"
      value: "red toenail polish"
      anchor: feet
      requires: [barefoot]
  mutex_groups:           # attrs that can't coexist
    - [legwear, barefoot]
```

### 2. Framing 词汇建议（基于 Grok grammar 测试）

**推荐用**：
- `Extreme close-up of [region]` / `ECU of [region]` — 最受限 framing
- `Close-up of [region]` / `CU of face / CU of hand` — 精确到 region
- `Medium shot, [pose], [framing-anchor]` — 指明姿势
- `Full-length standing shot, head to toe` — 最宽 framing
- `Wide shot` / `WS` — 环境为主，人占比 20%+

**避免**：
- 模糊词如 "nice shot of her" — 不明 framing
- "Dutch angle"（Grok 不响应 — 见 49-shot 测试）
- 只写"CU" 不说 region — Grok 会默认脸

### 3. 冲突解决

**当 shot 需要显示超框区域的"状态"时**：
- ❌ 错：在 CU face 的 prompt 里写 "she has red toenail polish"（属性超框）
- ✓ 对：切到另一个 shot（feet ECU）来展示 toenail，或者把 CU face 改成半身能看到脚

**Mutex 属性冲突**：
- 永远只保留一个：`barefoot` 和 `pantyhose-on-feet` 在同一 shot 里不能共存
- 这要从 shot 设计阶段决定，不是 prompt 事后救济

### 4. 动态姿势决定可视 regions

Framing 是表面，**pose** 是决定真正可视 region 的关键：
- MS waist-up，`sitting hands folded in lap` → 手在 frame
- MS waist-up，`standing hands in pockets` → 手藏
- Full body，`holding a mug in both hands` → 手 + 腿 + 脚全在 frame
- Full body，`back to camera` → 脸 + 前身都不在 frame（但发、肩、背、腿、脚在）

Shot Director 在填 pose 时应该更新 visible_regions 集合。

## 证据总结（本次测试的经验映射）

| 实验 | 证据点 |
|------|-------|
| m01 eye_detail × eye_ecu | ✓ 正确注入 → 虹膜细节渲染 |
| m02 eye × feet_ecu | ✓ 超框属性被 drop |
| m04 nails × eye_ecu | ✗ Mode 1: framing 从眼 ECU 扩到 CU face 含手 |
| m06 earring × feet_ecu | ✗ Mode 3: composite (脚+脸拼在一张) |
| m07 pantyhose × leg_ecu | ✓ 正确注入 |
| m08 pantyhose × cu_face | ✗ Mode 1: framing 扩到半身 |
| m11 toes × cu_face | ✗ Mode 4: 红迁移到手指甲 |
| k01 all5 × eye_ecu | ✓ 全部 drop，保持 eye ECU |
| k02 all5 × cu_face | ✗ Mode 1 极端: CU 拉成 2/3 body 塞 5 属性 |
| k04 all5 × full_body | ✓ 所有 attr 都在 visible region → 正确 |
| g02 gated × cu_face | ✓ lips+earring 正确，framing 保留 |
| g04 gated × full_body | ✓ 与 k04 视觉等同，证明 gated 不损失质量 |

**最重要的 2 张对比**：
- **k02 vs g02**: 同框位，k02 被破坏（framing violation），g02 完美
- **k04 vs g04**: 同框位，visually equivalent — 大 framing 下 kitchen sink 不受损

结论：**Framing 越紧，gating 越关键**。

## 适用范围 & 未验证边界

**已验证**：
- Grok Imagine Pro（anime 风格）
- Su Wan 单角色多属性
- 5 种属性 + 9 种 framing

**未验证**（需要后续测）：
- 是否适用于多角色（每角色独立 gating map？）
- Realistic 风格（非 anime）是否同样规则
- 其他 diffusion 模型（FLUX/Nano Banana）是否有相同 4 modes

**猜想**：因为所有主流 t2i 都基于 attention + diffusion，这条规则应该是**普适的**——但严重程度可能不同（Grok 倾向 Mode 1-2，OpenAI 可能倾向 Mode 2-4）。

---

## 给产品 Shot Director 的交接

本方法论可以直接转换成代码：

```python
FRAMING_REGIONS = {
    "eye_ecu":        {"eye"},
    "hand_ecu":       {"hand"},
    "ear_cu":         {"ear", "face_partial", "neck_partial"},
    "feet_ecu":       {"feet"},
    "leg_ecu":        {"legs"},
    "cu_face":        {"face", "neck", "ear", "shoulders_partial"},
    "ms_waist":       {"face", "neck", "ear", "shoulders", "torso", "hands_conditional"},
    "full_body":      {"face", "neck", "ear", "shoulders", "torso", "hands", "legs"},
    "full_body_bare": {"face", "neck", "ear", "shoulders", "torso", "hands", "legs", "feet"},
}

ATTR_ANCHOR = {
    "lipstick":    "face",
    "earrings":    "ear",
    "fingernails": "hand",
    "pantyhose":   "legs",
    "toenails":    "feet",
    "eye_detail":  "eye",
    "necklace":    "neck",
    "tattoo_waist":"torso",  # contextual
    # ... extendable
}

def filter_attrs_for_framing(character_sheet, framing, pose_hints=None):
    visible = FRAMING_REGIONS[framing].copy()
    if pose_hints and "hands_in_frame" in pose_hints:
        visible.add("hands")
    return [a for a in character_sheet.anchored_attrs
            if ATTR_ANCHOR[a.name] in visible]
```

这个函数就是 VGAI 规则的可执行形式，产品代码直接引用。
