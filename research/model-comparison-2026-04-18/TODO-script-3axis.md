# TODO: Script 3 层正交测试（后续）

用户指示（2026-04-18）："script 里面我们有 3 层正交要都要测试一下，后面再测"

推测 3 轴（从 daisy v6 prompt 结构看）：
- **detailRichness**: concise / standard / detailed / extreme
- **contentLength**: short / medium / long
- **structure preset**: linear / bifurcating / funnel / web

也可能是（另一分法）：
- **McKee 合规度**（6 条硬约束的遵守程度）
- **诗意 vs 细腻模式**（poeticMode）
- **露骨度路由**（tame / suggestive / explicit）

需在后续 brainstorm 或产品设计中与用户确认。

## 当前状态（今晚结束时）
- **DeepSeek V3.2** 已测长篇：16,578 字 / $0.0039 / "凑合能用"但**过长**
- **Sonnet 4.6** 已测：8,073 字 / $0.13 / 质量基线
- **Grok 4.20 T=0.8** 已测：8,196 字 / $0.034 / 接近 Sonnet

## 未做的测试
- DS3.2 在不同 detailRichness 下的表现
- DS3.2 在 bifurcating vs linear 不同 structure 下的表现
- DS3.2 在露骨度路由下（explicit 部分交给 Grok 时的协作）

## 结论（待验证）
- 架构换为 **DS3.2 + Grok 双模型**（去掉 Sonnet）
- DS3.2 verbose 问题需要在 daisy 框架里加一个 length-cap 约束
