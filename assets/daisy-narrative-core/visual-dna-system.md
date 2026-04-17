# Visual DNA 系统 —— 图像侧"叙事核心"

这是 crpg 项目**图像生成**的核心机制，与 daisy 文字侧的 `MCKEE_BASE + controllingIdea` 同构。

## 1. 动机 —— 为什么需要 Visual DNA

### 1.1 失败案例（2026-04-17 Round 1 测试）
用 `story-export.md` 生成 5 张 Grok Imagine 分镜，每张独立调用，无 anchor。结果：
- 主角 Su Wan 在 Scene 1 是白人欧美脸，在 Scene 4 是东方人——**角色没锁定**
- Scene 1 prompt 写"Chinese police interrogation room"，出来是"CAFE 咖啡馆"——**关键 setting 被 noir neon 的默认模板吃掉**
- 酒红趾甲 / 黑丝 / 包臀裙 这三个**故事核心视觉意象**在 5 张里命中率近 0
- 5 张的 color grade / film grain 各异，没有"同一部片"的连续感

### 1.2 根因
每张图是一次**冷启动独立调用**，Grok Imagine 无 seed / cfg_scale / negative_prompt / style_reference。模型在 180+ 词 prompt 里按自己的"电影感 noir"先验生成，具体视觉 motif 被淹没。

### 1.3 解决思路（对 daisy 的借鉴）
daisy 文字生成解决了"多个 scene 之间叙事连贯"的同类问题——方案是：
- `MCKEE_BASE`：所有 scene 共享的硬约束骨架
- `controllingIdea`：单故事级的主题句，贯穿所有 scene
- 两步生成：先骨架再填充（结构脆弱的部分先保护）

**Visual DNA 是它的图像同构**。

---

## 2. Visual DNA 的五层结构

每个故事生成一份 Visual DNA（JSON/YAML），所有分镜调用共享。

```yaml
# Visual DNA for story "审讯室权力差" (story-export.md)
story_id: "su_wan_interrogation_noir"

# Layer 1: Style Preamble （类比 MCKEE_BASE，每张图 prompt 开头固定注入）
style_preamble: |
  Shot on 35mm Kodak Portra film with moderate organic grain.
  Cinematic color grade: teal shadows and crimson highlights, rich blacks.
  Anamorphic 2.39:1 lens philosophy with subtle horizontal flare.
  Shallow depth of field. Volumetric haze from neon-lit Chinese nightscape.
  Single warm key light + cool ambient fill. Mid-2020s mainland Chinese
  urban noir atmosphere. Photorealistic. Cinematic composition.

# Layer 2: Visual Aesthetic Axis (from visual-aesthetics.yaml)
aesthetic_axis_primary: jpr_urban_ol          # 日系都市 OL 写实
aesthetic_axis_secondary: wr_noir_cinematic   # 辅以西方 noir 电影感

# Layer 3: Character Sheets （每个主要角色的外观常量，出现在哪张就复制到该张 prompt）
characters:
  - code: "su_wan"
    sheet: |
      Chinese woman, 28 years old, shoulder-length straight black hair
      parted on the side, thin sharp eyebrows, almond-shaped eyes with
      dark irises, pale fair skin with cool undertone, slender 170cm frame,
      long legs, red lipstick, minimal makeup, predatory composed posture.
      Signature outfit: tight black knee-length pencil skirt prominently
      shaping hips and thighs, sheer black seamed stockings clearly
      visible, burgundy-red glossy nail polish on toenails, strappy black
      high heels or bare feet where called for.
  - code: "lin_ze"
    sheet: |
      Chinese man, mid 30s, short slightly unruly black hair, visible
      stubble, tired dark-circled eyes, square jaw, lean athletic build,
      rumpled off-white dress shirt with loosened charcoal tie, dark trousers,
      exhausted insomniac demeanor.
  - code: "meijie"
    sheet: |
      Severe Chinese woman, early 50s, black hair lacquered into tight
      chignon with faint silver streaks, sharp cheekbones, long thin
      fingers, emerald silk cheongsam slit to thigh, always holding a
      slender cigarette, tired watchful eyes.

# Layer 4: Recurring Motifs （故事级视觉 signature，每张图 prompt 都嵌入一条提示）
recurring_motifs:
  required_in_every_frame:
    - "neon light spilling through venetian blinds, casting long diagonal shadow bars"
    - "reflective surface somewhere in frame (mirror / glass / polished steel / puddle)"
    - "Chinese typography or signage visible somewhere"
  required_when_character_present:
    su_wan:
      - "burgundy-red toenail polish visible (even partially through heels or bare)"
      - "sheer black seamed stockings distinctly visible, never plain bare legs"
      - "tight black pencil skirt shape prominent, never A-line or loose"

# Layer 5: Positive-framed Forbidden Zones （因为 Grok 无 negative_prompt，用正向描述硬挤出空间）
positive_framing_of_exclusions:
  instead_of_no_cafe:
    use: "interrogation room with steel table, one-way observation mirror, concrete floor"
  instead_of_no_western_face:
    use: "clearly East Asian features, double eyelids rare, epicanthic fold subtle"
  instead_of_no_casual_clothing:
    use: "formal professional attire, tailored fit, dark palette"
  instead_of_no_bare_legs:
    use: "stockings or tights explicitly visible, fabric texture readable"
  instead_of_no_bright_daylight:
    use: "night scene, artificial light sources only, deep shadows"

# Layer 6: Technical Lock （锁死技术参数避免 ratio 混用破坏视觉连续）
technical_lock:
  aspect_ratio: "16:9"              # 全片锁定 16:9，不混用
  resolution: "2k"
  model: "grok-imagine-image"        # 全片同一模型（pro 版只做对比测试）
  n_per_scene: 1

# Layer 7: Image-to-image Anchor Strategy （利用 Grok 的 image_url 能力做 style transfer）
anchor_strategy:
  stage_1_generate_anchor:
    description: "先生成一张 style anchor 图，只含视觉 DNA，不含具体场景"
    prompt_template: |
      {style_preamble}
      Character: {su_wan.sheet}
      Scene: medium portrait of Su Wan seated in a nondescript Chinese
      urban interior at night, neon light through venetian blinds,
      mood of power and restraint.
    purpose: "作为后续所有分镜的 image_url 参考，让 style 和人物脸部特征跨帧对齐"
  stage_2_generate_scene:
    description: "每张分镜用 stage 1 的 anchor 作为 image_url 参考"
    prompt_structure: |
      [Style Preamble — identical across frames]
      [Character Sheets for characters in this scene]
      [Recurring Motifs — always embedded]
      [Positive-framed Exclusions — relevant ones for this scene]
      [Scene-specific setting, action, composition, mood — the ONLY varying section]
    payload_hint: |
      {
        "model": "grok-imagine-image",
        "prompt": "<composed above>",
        "image_url": "<path to stage-1 anchor as base64 data URI>",
        "aspect_ratio": "16:9",
        "resolution": "2k"
      }
```

---

## 3. Prompt 结构模板（Stage 2 每张分镜）

```
{{style_preamble}}

Characters in this scene:
{{for each character: character.sheet}}

Recurring visual signatures (always present):
{{motifs.required_in_every_frame}}
{{for each character: motifs.required_when_character_present[character]}}

Setting specifics (positive-framed to exclude drift):
{{relevant_positive_framings}}

Scene: {{scene_specific_prompt}}
```

**原则**：前 4 段在 5 张图中**字节级相同**；只有 "Scene:" 部分变化。这是让模型"这是同一部片的第 N 个镜头"的最强信号。

---

## 4. 和 daisy MCKEE_BASE 的映射关系

| Visual DNA 层 | Daisy 文字对应 |
|---|---|
| Style Preamble | MCKEE_BASE 的六条硬约束 |
| Aesthetic Axis | daisy 的 detailRichness + poeticMode |
| Character Sheets | daisy 的 characters 字段 + {{playerName}} 占位符机制 |
| Recurring Motifs | daisy 的 controllingIdea（但具象化为视觉元素） |
| Positive Framing | daisy 的 ANTI-MELODRAMA（封堵默认坏习惯） |
| Technical Lock | daisy 的 preset + contentLength + detailRichness |
| Anchor Strategy | daisy 的两步生成（骨架→填充） |

---

## 5. Visual DNA 如何生成 —— pipeline 位置

在整个 crpg 故事生成流程里的位置：

```
用户输入 keywords
    │
    ▼
Sonnet/Grok 文字模型生成故事骨架 (daisy 继承)
    │
    ├── 推断 Visual Aesthetic Axis (从 keywords + genre → 对 visual-aesthetics.yaml 做检索)
    ├── 推断 Characters (从骨架文本提取) → 生成 character sheets
    ├── 推断 Recurring Motifs (从 keywords + controllingIdea → 提取关键视觉信号)
    ├── 推断 Technical Lock (ratio / resolution / 固定模型)
    │
    ▼
Visual DNA 对象（一次生成，全故事复用）
    │
    ▼
Stage 1: 生成 Style Anchor 图 (1 张)
    │
    ▼
Stage 2: 对每个节点生成分镜图 (N 张，每张 image_url = anchor)
```

---

## 6. 针对本次测试故事（审讯室权力差）的具体 Visual DNA

### Aesthetic Axis 选择
- 主：`jpr_urban_ol`（日系都市 OL 写实）—— 匹配权力差/禁忌/职业女性核心
- 辅：`wr_noir_cinematic`（西方 noir 电影感）—— 强化 visual grammar

### Recurring Motifs 优先级
必现：
- burgundy-red toenails
- sheer black seamed stockings
- tight black pencil skirt
- neon through venetian blinds → diagonal shadow bars
- Chinese typography in background

### Aspect Ratio
**全部 16:9** （Round 1 混用了 16:9 / 21:9 / 3:2 是错误）

### Anchor 策略
先生成 1 张"Su Wan 定调肖像"作为 anchor，后续 5 张用 `image_url=anchor` 做 style transfer。

---

## 7. Direction Layer —— Visual DNA 的第八层（2026-04-17 增补）

### 7.1 增补动机
Round 2 验证了前七层后，用户反馈："一致性是不错了，但图还是差点 vibe，感觉僵硬、表情呆滞，没有像 md 里描写得那么自然"。

诊断：前七层解决的是**身份 + setting + 风格 + 技术**，但 Grok Imagine（和大多数扩散模型）的默认倾向是生成 stock photo 式的"portrait pose"——**主体面向镜头、中心构图、静态定格**。这让每张图看起来像被摆了拍，不像正在发生的瞬间。

这和 daisy V6 的"GAME WRITING RULES"（解决文字侧"写成小说不写成游戏"）是**同构问题**。Visual DNA 需要对应的"导演层"来打破扩散模型的默认肌肉记忆。

### 7.2 Direction Layer 的五条规则

```yaml
direction_layer:
  # R1: 取景哲学
  framing: |
    Each frame is a candid documentary still captured mid-action,
    not a staged portrait. Subjects are DOING something with hands,
    bodies, or environment. No subject faces camera unless
    confrontation itself is the scene.
  
  # R2: 微表情词汇（要求"具体 tell"而非"情绪形容词"）
  # ⚠️ 2026-04-17 修正：移除 "tongue briefly wetting lips" —— Round 3 发现扩散模型
  # 会字面把这个 tell 渲染成"舌头伸出嘴外"，导致 5/5 张图人物吐舌头。
  # 凡是可能被模型字面图像化为"身体部位外露"的 tell 一律避免（舌头 / 牙齿 / 嘴巴张开）。
  micro_expression_vocabulary: |
    Use specific physical tells only: half-raised brow, pressed lips,
    dilated pupils, corner-of-eye glance, jaw tension, lower lip
    caught between teeth inside the mouth, lower lip pressing inward,
    faint smile fading, nostril flare, chin drop, Adam's apple
    swallowing once.
    
    Never write "smiles happily" / "looks mysterious" / "composed" —
    describe the muscle, not the interpretation.
    
    ⚠️ Forbidden tells (these break image generation by being taken
    literally as visible anatomy):
    - tongue wetting lips / tongue visible / tongue tip
    - teeth bared / mouth wide open
    - any tell that draws the mouth open and exposes interior
    
    Always specify "mouth closed" or "lips sealed" if emphasizing
    facial muscles, to prevent the diffusion model from defaulting
    to open-mouth pose.
  
  # R2b: Tell 分配规则 —— 不要每张图堆全套 tell
  tell_allocation: |
    Each scene prompt picks **2–3 tells maximum**, not the full list.
    Each character has ONE signature tell reused across their scenes
    (for facial consistency):
      Su Wan:   corner-of-mouth twitch, half-lidded eyes at critical moments
      Lin Ze:   jaw tension + Adam's apple swallowing (never tongue)
      Meijie:   cigarette smoke curling past her eye, slow blink hold
    Plus 1 situational tell from the vocabulary list for the specific
    action moment. Do NOT copy the full tell vocabulary into every
    scene — that confuses the diffusion model and causes every face
    to perform every tell at once.
  
  # R3: 身体语言四约束
  body_language: |
    1. Weight shift — one leg bearing more, slight lean, not symmetric
    2. Hands always doing something — holding / mid-gesture / fingers
       tensed / resting on something / pausing mid-reach
    3. Gaze direction — rarely at camera; at object, at another
       character, at middle distance, past the lens, at floor
    4. Asymmetry — one shoulder lower, one brow higher, weight
       off-center, head tilted

  # R4: 动词偏好（present continuous 取代名词化）
  verb_bias: |
    Prompt verbs should be present continuous, implying an action
    caught in progress: lighting / reaching / pausing / glancing /
    tensing / wetting / swallowing / clenching / fading.
    Avoid static nouns: "pose", "portrait", "stance", "look",
    "expression" — these freeze the model into stock-photo mode.
  
  # R5: 摄影参考语法（比类型词更强的风格信号）
  photographic_reference_grammar: |
    Invoke documentary / photojournalism / cinema by name rather
    than style keyword. Examples that work for this story:
    - "in the style of Nan Goldin's intimacy"
    - "Wong Kar-wai's temporal hesitation"
    - "Saul Leiter's compositional looseness"
    - "Jim Goldberg documentary tension"
    - "Gregory Crewdson suspended cinematic moment"
    These steer the model toward candid/intimate/hesitant rather
    than glossy/staged.
```

### 7.3 Direction Layer 在 prompt 结构中的位置

更新 Stage 2 的 prompt 模板：

```
{{style_preamble}}

{{direction_layer (NEW, fixed across frames)}}

Characters in this scene:
{{for each character: character.sheet}}

Recurring visual signatures:
{{motifs}}

Setting specifics (positive-framed):
{{positive_framings}}

**Action moment** (replace the old "Scene:" section):
{{what is happening RIGHT NOW — one present-continuous sentence per character,
   plus one environment interaction, plus explicit gaze direction for each person,
   plus one micro-expression tell per face visible in frame,
   plus one photographic reference by name}}
```

### 7.4 Scene prompt 改写示例（Round 2 → Round 3）

**Round 2 的 Scene 1（僵硬）**：
> "In the foreground, a woman in her late twenties sits with her legs elegantly crossed... Her posture is composed, predatory, amused."

**Round 3（活）**：
> "Mid-moment: Su Wan has just finished crossing her legs, one heel still half-off, toes pressed against the floor — she is mid-sentence, lips slightly parted, eyes locked not on the detective but on his wedding ring finger, her right hand pausing halfway to the table as if reconsidering. Lin Ze is leaning back, Adam's apple swallowing, gaze flickering from her face down to her stockinged knee and forcing itself back up. Captured as if shot by Nan Goldin — grainy, intimate, caught mid-breath."

### 7.5 完整 Visual DNA 现在是八层

| 层 | 作用 | 固定 or 变化 |
|---|---|---|
| 1. Style Preamble | 技术美学底座 | 字节级固定 |
| 2. Aesthetic Axis | 美学流派选择 | 故事级固定 |
| 3. Character Sheets | 角色外观锁定 | 故事级固定，按场景选择 |
| 4. Recurring Motifs | 故事级视觉 signature | 每帧注入 |
| 5. Positive Framing | 禁忌转正向描述 | 每帧注入 |
| 6. Technical Lock | aspect/resolution/model | 故事级固定 |
| 7. Anchor Strategy | image_url 机制 | 全故事一张 anchor |
| **8. Direction Layer** | **行动瞬间 + 身体语言 + 摄影参考** | **字节级固定** |

---

## 8. Layer 10 —— Layered Garment Visibility Rule（2026-04-17 Round 5 Shot 2 暴露后增补）

### 8.1 增补动机
Round 5 Shot 2 连续 5 版打磨才修好"长筒丝袜不被误画成短袜/裤子/过膝袜"的 bug。根因是 **Bug Class D: Default-Prior Override**（见 `text-to-image-bug-taxonomy.md`）——扩散模型对某些服装类型有极强的训练先验，prompt 指令被吸附到最相近的 training distribution peak。

### 8.2 Layered Garment Visibility Rule
对于有**强默认先验**的服装/配件类型，prompt 必须提供 **3+ 层独立视觉线索**在画面里同时可见，让模型无法滑回任何单一 peak。

#### High-Prior Garment List（初始）
- sheer hosiery / thigh-high stocking / over-the-knee sock / pantyhose（五个都是相近 peaks）
- qipao / cheongsam（vs 其他东亚礼服）
- school uniform JK（vs 普通连衣裙）
- lingerie with visible structure（vs 无结构内衣）
- period-specific costume（维多利亚 / 昭和 / 汉服等）

#### 消歧的"分层视觉语法"模板（以 thigh-high stocking 为例）
prompt 必须包含以下所有层级，按画面从上到下顺序：

1. **Upper boundary**（裙/底/腰带等服装的下缘）—— 显式画出 hem line
2. **Skin gap**（裙底和丝袜 band 之间）—— 显式说明 2-3cm 小 gap（不是 8-12cm 大 gap，那是过膝袜的 diagnostic）
3. **Garment-specific signifier**（丝袜的 top band + lace/silicone grip）—— 显式描述 band 的位置、宽度、材质
4. **Main garment body**（丝袜本体）—— 显式要求 sheer / translucent / "skin visible through fabric"
5. **Optional detail**（丝袜 seam line / 蕾丝纹理等）

+ **硬否定三重冗余**（"NOT pants. NOT over-the-knee. NOT knee-high"）
+ **具体尺寸 constraint**（"2-3cm"、"upper thigh, just below hem"），禁用模糊词（"mid-thigh"会被字面化为过膝袜位置）

### 8.3 Shot Director LLM 的义务
Shot Director 在生成 image prompt 时：
- **识别** shot 中是否涉及 High-Prior Garment
- 若涉及，强制启用 Layered Visibility 模板
- 若该 shot 的 crop 不足以容纳所有层级（比如 ECU 只看到脚），要么改 crop 扩大（3:4 或 2:3 竖幅），要么在 prompt 里用"out-of-frame context"明确补全层级
- 生成前做 "adversarial check"：列出模型最可能的 3-5 个误读（短袜 / 过膝袜 / 裤子 / tights），对每个增加硬否定

### 8.4 案例：thigh-high stocking 完整 prompt 模板

```
Layered garment grammar (top to bottom):
1. Pencil skirt hem — sharp horizontal cut line at mid-thigh (matte opaque cotton-blend fabric, clearly different texture from stocking below)
2. Bare skin gap — 2-3cm only (NOT 8+cm, which would diagnose over-the-knee sock)
3. Stocking top band — sits at UPPER thigh just 2-3cm below skirt hem, with visible lace-trim or silicone grip, 3-4cm band height
4. Sheer nylon stocking body — covers ENTIRE leg below band to toes (~60-65cm of leg length), translucent with skin tone glowing through black mesh, fine-denier, subtle gloss, NOT opaque solid black
5. Back seam — vertical line from top band down back of leg to heel

Hard negatives (triple redundant):
- NOT pants / trousers / leggings (those have no horizontal termination band)
- NOT over-the-knee sock (OTK ends mid-thigh or above knee, with 8-12cm skin gap)
- NOT knee-high stocking (ends below knee)
- NOT tights / pantyhose (those cover ENTIRE body, no band anywhere)

Anti-prior visual anchor: "skin tone clearly visible glowing through the translucent black nylon mesh"
```

### 8.5 Visual DNA 现在是 10 层

| 层 | 作用 | 固定粒度 |
|---|---|---|
| 1. Style Preamble | 技术美学底座 | **分故事阶段**（建置/冲突/余波各一套） |
| 2. Aesthetic Axis | 美学流派选择 | 故事级固定 |
| 3. Character Sheets | 角色外观 + 局部可见规则 | 故事级固定，按场景选取 |
| 4. Recurring Motifs | 分层 motif（every-frame / scene-level / shot-level） | 每帧按层级过滤注入 |
| 5. Positive Framing | 禁忌转正向描述 | 每帧注入 |
| 6. Technical Lock | aspect / resolution / model | 故事级固定 |
| 7. Anchor Strategy | image_url 机制 | 全故事 1 张 style anchor |
| 8. Direction Layer | 行动瞬间 + 身体语言 + 摄影参考 | 字节级固定 |
| 9. Shot Design Layer | 每 beat 可变 shot 数（0-N，Director LLM 自决） | 按节点 beat 决策 |
| **10. Layered Garment Visibility** | **High-Prior 服装的消歧层级** | **仅涉及 High-Prior 服装时触发** |

## 9. 后续演进空间

- **Genre-aware Visual DNA**：不同叙事 Genre 自动选配不同美学轴（forbidden_affair → jpr_urban_ol；isekai_erotic → ani_painterly_pixiv；等）
- **动态 Visual DNA**：长故事里，随着 value arc 演进，color grade 逐步漂移（开篇冷蓝 → 中段暖红 → 结局灰白）
- **Video DNA**：将来接入 `grok-imagine-video` 时，Visual DNA 升级为 Temporal DNA（加入 camera movement、cutting rhythm、scene-transition style）
- **Pro 版对比**：同一 Visual DNA 在 `grok-imagine-image` vs `grok-imagine-image-pro` 的效果对比，决定默认选哪个
