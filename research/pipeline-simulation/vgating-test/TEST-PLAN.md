# Visibility-Gated Attribute Injection (VGAI) Methodology Test

## 目的

**验证一条可推广的 prompt 写作规则**：什么时候该把某个属性写进 prompt，什么时候不该。

原始问题：在 Grok Imagine Pro 上测试发现，把"连裤袜"塞进所有 shot（包括特写镜头）会导致 Grok 幻觉式渲染——在特写脸时强行挤出腿上的袜子元素，破坏物理。反过来，腿可见的 shot 不写连裤袜则变成裸腿，失真。

**假设要证的规则**：
> **Visibility-Gated Attribute Injection (VGAI)**
> 属性只在**框位实际能看见的区域**才应写进 prompt；框位看不到的区域属性，即使是角色"设定里的长期特征"，也不应写入——否则导致幻觉渲染或物理错误。

**这条规则如果成立**：
- Shot Director 不能只"dump 角色 sheet 到 prompt"
- 必须**按 framing 过滤属性**
- 适用于任何属性（不只是连裤袜，也适用于纹身/首饰/疤痕/发型细节等）

## 测试设计

**Character**：Su Wan（最小 sheet，只保留无区域属性：发、肤色、眼色、脸骨）

**5 种可测属性**（每种绑定一个具体身体区域）：
| 属性 | 代号 | 可视区域 |
|------|------|---------|
| Red lipstick | `lips` | 脸（唇区）|
| Red fingernails | `nails` | 手 |
| Jade earrings | `earring` | 耳（侧脸可见）|
| Black pantyhose | `pantyhose` | 大腿到脚踝 |
| Red toenails (bare) | `toes` | 光脚 |

**9 种 framings**（从最小到最大）：
| Framing | 代号 | 可视区域 |
|---------|------|---------|
| Eye ECU | `eye_ecu` | 仅眼 |
| Hand ECU | `hand_ecu` | 仅手 |
| Ear CU profile | `ear_cu` | 耳+颊 |
| Feet ECU | `feet_ecu` | 仅脚 |
| Leg ECU | `leg_ecu` | 大腿-小腿 |
| CU face | `cu_face` | 脸+脖 |
| MS waist-up | `ms_waist` | 腰以上 |
| Full body (shoes) | `full_body` | 全身，穿鞋 |
| Full body barefoot | `full_body_barefoot` | 全身，光脚 |

## 22 Shots 测试矩阵

### 组 M：单属性 × 框位（12 shots）
测"injection 放对框位 vs 放错框位"

| # | Attr | Frame | 预期 |
|---|------|-------|-----|
| m01 | eye_detail | eye_ecu | ✓ render |
| m02 | eye_detail | feet_ecu | 应不 render（超框） |
| m03 | nails | hand_ecu | ✓ render |
| m04 | nails | eye_ecu | 应不 render |
| m05 | earring | ear_cu | ✓ render |
| m06 | earring | feet_ecu | 应不 render |
| m07 | pantyhose | leg_ecu | ✓ render |
| m08 | pantyhose | cu_face | 应不 render（**关键**：是否产生幻觉？） |
| m09 | pantyhose | full_body | ✓ render |
| m10 | toes | feet_ecu | ✓ render |
| m11 | toes | cu_face | 应不 render |
| m12 | toes | full_body_barefoot | ✓ render |

### 组 K：Kitchen Sink（4 shots）
把全部 5 个属性塞进 4 种框位，看过度注入的损伤

| # | Frame | 预期 |
|---|-------|-----|
| k01 | eye_ecu | 所有 attrs 尽力挤进眼特写 → 严重幻觉 |
| k02 | cu_face | 脸特写被腿/脚属性污染 → 中度问题 |
| k03 | ms_waist | 腿/脚的属性找不到位置 → 轻中问题 |
| k04 | full_body | 所有属性都能视觉化 → 应基本正常 |

### 组 Z：Zero baseline（1 shot）
不写任何属性，看 Grok 的 default prior

| # | Frame | 预期 |
|---|-------|-----|
| z01 | full_body | 观察 Grok 的默认人物 |

### 组 G：Correctly Gated（5 shots）
只写该框位 actually visible 的属性，确认这是干净方案

| # | Frame | Attrs |
|---|-------|-------|
| g01 | eye_ecu | (none — 基础脸 Sheet 足够) |
| g02 | cu_face | lips, earring |
| g03 | ms_waist | lips, earring, nails |
| g04 | full_body | lips, earring, nails, pantyhose |
| g05 | full_body_barefoot | lips, earring, nails, toes |

## 评分

每 shot 4 维度：
- **A 属性正确渲染**（该出现的出现）
- **B 无幻觉超框属性**（不该出现的没出现）
- **C 物理自洽**（没有"脸上长袜子"等怪异合成）
- **D 构图干净**（framing 没被属性搞崩）

规则验证：
- **组 M 应当呈现 A-B dichotomy**：m01/m03/m05/m07/m09/m10/m12 全 ✓，m02/m04/m06/m08/m11 全 ✗ 或幻觉
- **组 K 应当 k01 严重崩坏，k04 基本 OK**
- **组 G 应当全绿**，同时对比组 K 同框位变好

## 预算

22 shots × $0.07 = **$1.54**，~3-5 分钟

## 产出

- `shots/` 22 图片（按 id 命名）
- `VGATING-REPORT.md` 矩阵评分
- **`VGATING-METHODOLOGY.md`** ← 关键产出：可推广的 VGAI 规则 + framing-to-region map + Shot Director 指南
