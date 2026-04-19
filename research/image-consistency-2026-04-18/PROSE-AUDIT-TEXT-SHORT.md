# Prose Audit — text-only short run (2026-04-18)

Audited against:
- SKILL.md (McKee soft constraints, self-check)
- references/game-writing-rules.md (R1–R7)
- references/anti-melodrama.md (Rules A–D)
- references/banned-phrases.md
- story.json beat metadata
- characters.json wardrobe/character sheets
- Baseline: bundles/e2e-agent-2026-04-18/prose/ (b1.md, b2.md, b3A.md, b3B.md)

---

## Executive summary

1. **Overall verdict: SHIPPABLE AS DEMO, NOT AS PRODUCTION.** The prose is competent Chinese noir atmosphere — controlled restraint, clean physical detail, no melodrama blow-outs, zero banned phrases. But two systemic defects block a clean ship: (a) every single beat undershoots its targetWordCount by 18–26%, and (b) the agent hallucinated a uniform "二千五百字" footnote on all 8 beats regardless of actual target.

2. **Top 3 concrete issues:**
   - **Length compliance failure (all 8 beats)**: every beat is outside the ±10% window. b1 should be ~2500 Chinese chars, landed at 2013 (-19%). Branch beats (b3–b5) should be 1500, landed at 1143–1236 (-18% to -24%). The write_beat_prose tool either did not enforce the window or was bypassed. The footnote "（二千五百字，共约二百五十字符）" is incorrect on every branch beat.
   - **b4b missing its key line**: Synopsis specifies `「你不想让我停。」` as the pivot line — the moment valueBefore (失控开始) turns to valueAfter (主动失控). The prose omits this line entirely. Instead the hand moves to the skirt hem and she grips the glass. The climax pivot is indirect and the value shift is implicit rather than explicit.
   - **b2 narrative inconsistency**: The choice beat resolves the choice inside the prose (line 111: `「走吧。」她说出声了。` — she says "let's go"), then reverses to present it as still open (line 121: `她需要做出选择。`). The prose can't decide whether it's executing the branch split or holding at the fork. The player receives a contradictory handoff.

3. **Best beat: b4a.** Clean concrete stakes (red delete button, three-millimeter gap, taxi paused at red light), tight value turn from "surface control" to "loss of control revealed," excellent physical grounding of her psychology through the phone UI action sequence. The three-pass press-and-cancel is genuinely good game-writing.

4. **Worst beat: b3b.** The bar scene is all atmosphere and no event. The B-branch pivot (面临抉择 → 失控开始) is supposed to show the first crack in control. Instead the prose loops: she drinks, she feels the distance between them, she drinks again, she doesn't stand up. `她没有站起来。` (line 53) is the best line in the beat, but it's surrounded by six paragraphs of sensory fog with no dramatic development. Kai says nothing of substance. The bar scene synopsis says she has "no intention of leaving" — the prose gets there but only through passive negation, not through any action she takes.

5. **Ship-or-not: DO NOT SHIP.** Fix the three defects above — length compliance, b4b dialogue pivot, b2 choice-beat architecture — then re-run. The prose quality is good enough to build on; the structural problems are addressable without full rewrites.

---

## Per-beat verdicts

### b1 (职业控制 → 控制感松动)

- **Chinese quotes**: PASS — no dialogue in this beat, which is appropriate for a solo walk-through-rain opening. No ASCII quote contamination.
- **Banned phrases found**: NONE. Clean sweep on every category.
- **Anti-melodrama:**
  - Rule A: PASS — emotion naming avoided. "她把手指攥紧，压在挎包带子上，指节发白" shows anxiety through action.
  - Rule B: VIOLATION. Last paragraph (line 49) stacks: heart rate ("心跳慢慢平复"), sweat ("掌心有一点汗"), trembling ("手指在微微发抖"), white knuckles ("指节发白"). That is four physical sensations in one paragraph. Rule B allows ONE.
  - Rule C: Low-frequency. Five `像` comparisons total across the beat, but none overwrought; they're concrete visual comparisons ("像一个烧灼过的痕迹", "像雨停之后留在手臂上的水渍"). The em-dash count is high (11), which anti-melodrama.md flags as overused.
  - Rule D: N/A for b1 — this is a setup beat, tone is appropriately low-intensity.
- **Game Writing Rules:**
  - R1 (player as agent): PARTIAL. Su Wan moves, acts, notices — but the beat has extended passages where she stands and internally processes. Line 49 is six consecutive "感觉到/注意到/能感觉到" sentences with no new physical action.
  - R2 (show world through interaction): PASS. She handles the umbrella, swipes the transit card, notices specific people on the platform.
  - R3 (punchy): PARTIAL. Line 49 (final paragraph) is 150+ characters of consecutive observation before any action — violates the 2-3 sentence description budget.
  - R4 (concrete game information): PASS. The paper napkin with the name written on it is a strong concrete object/clue. Kai's face at the platform is a clear actionable story element.
  - R5 (dialogue as gameplay): N/A — no dialogue.
  - R6 (tension through stakes): PASS. The paper napkin, the three-year gap, the face on the platform — all establish stakes concretely.
  - R7 (setup nodes still active): PASS. She walks, counts, swipes, notices.
- **Value shift**: REALIZED. The turn from "职业控制" to "控制感松动" is staged correctly: she arrives in full professional armor, then line 11 delivers the crack: `「今晚这套标配穿在身上像一套戏服，不是她自己的身体。」` The pivot line is `「她的心跳恢复了平稳。但那张脸还在她的视野边缘，像一个烧灼过的痕迹，挥之不去。」` — control is restored in form but pierced in content.
- **Rushed feel**: NO — at 2013 Chinese chars vs 2500 target, slightly short, but the beat breathes. The shortfall is in the final paragraph which could be tightened anyway.
- **Overall: OK**
- The best setup beat in either run: atmospheric without being inert, Su Wan is active, the napkin object is strong. The Rule B stacking in line 49 and the 11 em-dashes need surgical trimming.

---

### b2 (控制感松动 → 面临抉择)

- **Chinese quotes**: PASS — all dialogue in 「」. No ASCII quotes detected.
- **Banned phrases found**: NONE.
- **Anti-melodrama:**
  - Rule A: PASS — no bare emotion nouns.
  - Rule B: PASS — physical sensations kept discrete. Line 33: heartbeat noted once ("心跳加快了一拍") and not repeated.
  - Rule C: Seven `像` comparisons — two in close proximity (line 21: "像一根细针", line 27: "像是在核对一道答案"). Not quite overwrought but approaching the rate limit.
  - Rule D: PASS for a single beat. The escalation from recognition to the rose-exchange to the choice is correctly graduated.
- **Game Writing Rules:**
  - R1: PASS. Su Wan walks, stops, takes the rose, refuses verbally but doesn't return it.
  - R2: PASS. The flower store is discovered by entering it, the rose is handled.
  - R3: PASS. Dialogue exchanges are punchy, action moves.
  - R4: PASS. The rose detail (花茎刺, thumb impression) is the best concrete game-object in the run.
  - R5: PARTIAL. Kai's dialogue is minimal and declarative (`「你来了。」` `「你要吗？」` `「跟我走。」`). It creates tension via what he doesn't explain, which works for noir. But his best line from the baseline (`「你的事务所上周赢了三件民事……谁在背后付钱？」`) — with real information pressure — is absent.
  - R6: PASS. Stakes are concrete — she is holding the rose; she hasn't given it back; she says "不用了" but doesn't act on it.
- **Value shift**: REALIZED THEN BROKEN. The beat correctly turns 控制感松动 → 面临抉择. BUT the choice is then resolved prematurely: line 111 has Su Wan say `「走吧。」` (committing to following him), and the prose follows through to them exiting the store together. Then lines 117-121 attempt to re-open the choice at the lane entrance. This is architecturally broken — the player's agency in the branch is undercut by the protagonist choosing inside the beat that is supposed to present the choice. Either the prose must end at the rose-refusal impasse and hand the fork to the player, or lines 111-121 need to be cut and the beat must end differently.
- **Rushed feel**: NO — at 1851 Chinese chars vs 2500 target it's measurably short, but the scene feels full enough because the rose exchange is slow and deliberate.
- **Overall: WEAK (structural problem)**
- The prose writing is fine; the architecture is broken. The choice beat resolves its own choice, making the bifurcation seam visible. The narration on line 113 ("像是她做了一个他没有完全预料到的选择") explicitly states she chose — then the beat tries to walk it back. Fix: cut lines 111-121 and end on the rose-pressure moment, or restructure so the fork is a clean player hand-off.

---

### b3a (面临抉择 → 表面自控)

- **Chinese quotes**: PASS — `「静安寺。」` (line 7). Sole dialogue line, correct format.
- **Banned phrases found**: NONE.
- **Anti-melodrama:**
  - Rule A: PASS.
  - Rule B: PASS — no physical sensation stacking detected.
  - Rule C: PASS — three `像` uses, all earned: the radio voice described as "像是被什么东西过滤过" (concrete); the sound compared to platform sounds (continuity callback); the fingerprint trace on the window (visual).
  - Rule D: PASS — this is the low-intensity branch and it delivers genuine mundane texture: radio in the cab, driver humming, seat leather smell.
- **Game Writing Rules:**
  - R1: PARTIAL. Su Wan is passive for the bulk of the beat — she rides, she thinks, she looks. Her one active gesture is reaching for the napkin and then not opening it. That's a good game moment but everything around it is reactive.
  - R2: PASS. The cab interior is rendered through physical contact: sticky seat leather, damp umbrella in side pocket, rose drooping in paper bag.
  - R3: PASS. Paragraphs are short and concrete.
  - R4: PASS. The napkin remains the key game object; the phone in the bag (with Kai's number) is correctly implied without being stated.
  - R5: One dialogue line that does its job.
  - R6: PASS. Stakes are real — she knows the number is there; we know she won't delete it.
- **Value shift**: REALIZED. The beat's job is "表面自控" — she controls externally (goes home, puts the rose away, doesn't call) but the prose shows internal leak. Turning moment: `「三年了，那个号码一直在那里。她没有删过。不是忘了删，是不想删。」` — wait, that line is actually in b4a, not b3a. In b3a, the shift is softer: she reaches for the napkin three times and each time doesn't open it. The last lines (47-50) where she presses her finger to the cold window and withdraws it carry the value shift quietly. PASS, but barely — the shift is more atmospheric than dramatic.
- **Rushed feel**: YES — at 1236 chars vs 1500 target (-18%), the beat feels complete but slightly thin. The cab ride is compressed; there's room for one more concrete action beat (she could check the phone briefly, or the cab radio song could have a lyric that lands).
- **Overall: OK**
- Clean, restrained, correctly mundane. The repeated reach-for-napkin gesture is good psychological choreography. Needs ~15% more material to hit target.

---

### b3b (面临抉择 → 失控开始)

- **Chinese quotes**: PASS — nine dialogue exchanges all in 「」.
- **Banned phrases found**: NONE.
- **Anti-melodrama:**
  - Rule A: PASS.
  - Rule B: PASS — isolated physical sensations; the "温热的感觉从小腹蔓延开来" (line 47) is one.
  - Rule C: PASS — zero `仿佛/宛如/好像`, zero `像` comparisons. The prose is unusually bare of metaphor — slightly too bare for poeticMode=true.
  - Rule D: BORDERLINE VIOLATION. This beat is supposed to be the start of losing control, but it runs at the same emotional intensity as b3a. There is no escalation within the beat — she drinks, sits near him, drinks again, doesn't leave. The absence of drama is the drama, which is fine for noir, but there is no specific moment of escalation. Two beats in a row run flat.
- **Game Writing Rules:**
  - R1: WEAK. Su Wan orders a drink, sits, drinks again. Her physical actions are almost all reactive to the drinks being poured. Kai says the interesting things; Su Wan deflects. A player reading this would feel they're watching, not playing.
  - R2: PASS. The bar is rendered through physical contact with the space.
  - R3: PASS. Short paragraphs.
  - R4: PARTIAL. The bar has atmosphere but the one concrete detail that matters for the story (his signet ring) appears (line 23) and is noticed, which is good. But the story information Kai delivers (`「上次那个案子，你输了之后做了什么？」`) is immediately deflected by Su Wan and then the conversation is summarized away: `「他们在吧台边坐着，聊了一些什么——案子，城市，凌晨的地铁。她不记得具体说了什么」`. This is a writer telling us there was information delivered rather than showing it — a Rule 4 failure at the story level.
  - R5: VIOLATION. The conversation is explicitly summarized and discarded. The only surviving dialogue lines are: `「上次那个案子，你输了之后做了什么？」`/`「继续做下一个案子。」` and `「就这样？」`/`「就这样。」`. These are OK but the rest of the bar conversation, which should be the info/dilemma/tension engine of the scene, is swallowed by `「她不记得具体说了什么」` (line 43). This is the most significant game-writing failure in the run.
  - R6: PARTIAL. The stakes are the closeness of their bodies and the second drink — implied but not concrete.
  - R7: N/A.
- **Value shift**: WEAKLY REALIZED. The turn from 面临抉择 to 失控开始 is `「她没有站起来。她知道他也没有站起来的意思。」` (lines 53-55). This is the best writing in the beat — two lines of pure negation that carry the value shift through what doesn't happen. But it comes too late and is buried after six paragraphs of ambient texture.
- **Rushed feel**: YES — at 1146 chars vs 1500 target (-24%), and the prose feels thin despite that shortfall. The missing content should be dialogue, not description.
- **Overall: WEAK**
- The bar conversation is punted. This is the beat where Kai should reveal something about himself that makes Su Wan's choice feel informed and dangerous — instead the conversation is explicitly erased. Needs a full dialogue pass.

---

### b4a (表面自控 → 失控被揭示)

- **Chinese quotes**: PASS — `「确认删除联系人？」` and `「取消」` both in 「」 as UI-within-narrative.
- **Banned phrases found**: NONE.
- **Anti-melodrama:**
  - Rule A: PASS — no bare emotion nouns.
  - Rule B: PASS — line 45 has "指尖有一点发凉" but it's a single, brief physical note; no stacking.
  - Rule C: PASS — three `像` uses, all concrete: `「像是要把什么东西一起按掉」`, `「像是被什么东西磨掉了一层」`. The three-millimeter recalibration as a legal-precision metaphor is well-earned and not overwrought.
  - Rule D: PASS — this is properly the A-branch's emotional climax. The intensity is correct here.
- **Game Writing Rules:**
  - R1: STRONG. Su Wan is operating her phone — a completely specific, interactive gesture sequence. Press, see confirm dialog, cancel. Press again. Stop. This is genuinely game-prose.
  - R2: PASS. The phone UI is rendered as an interactive surface.
  - R3: PASS. Short paragraphs with constant micro-action.
  - R4: PASS. The delete button as a game object with a color (`红色的`) and a measured distance (`三毫米`) is excellent concrete detail.
  - R5: The UI dialogue (`「确认删除联系人？」`) functions as an NPC presenting a dilemma. Unusual, creative, works.
  - R6: PASS. The stakes are clear: she can delete his number and close this, or not.
- **Value shift**: REALIZED, strongly. Turning line: `「她没有删过。不是忘了删，是不想删。她从来没承认过这一点，但今晚，在这个出租车后座上，她没办法再骗自己了。她不想删。」` (line 51). This is the best value-shift delivery in the run — it's explicit but earns the directness through the built-up action sequence before it.
- **Rushed feel**: NO — the pacing is correct for a climax beat.
- **Overall: STRONG**
- Best-executed beat in the run. The delete-button sequence is the kind of concrete game-writing that justifies this genre. The value shift is clear, the protagonist is active, the stakes are physical and visible.

---

### b4b (失控开始 → 主动失控)

- **Chinese quotes**: PASS — `「你不应该来这里。」` (×2) and `「我知道。」` all correct.
- **Banned phrases found**: NONE.
- **Anti-melodrama:**
  - Rule A: PASS.
  - Rule B: BORDERLINE. Three physical signals in the beat: `「呼吸停顿了一拍」` (line 15), `「指节发白」` (line 37), `「掌心微微渗出的汗」` (line 49). Rule B says pick one. The beat has two-to-three.
  - Rule C: PASS — metaphors are sparse and concrete.
  - Rule D: PASS — this is the B-branch climax; intensity is warranted.
- **Game Writing Rules:**
  - R1: PARTIAL. Su Wan drinks and receives his hand. Her active choices are minimal — she doesn't move her leg away, she eventually grabs his hand. The emotional work is reactive.
  - R2: PASS.
  - R3: PASS.
  - R4: PASS. The tactile detail is well-grounded:丝袜纹理压痕, skirt-hem border, the wet patch from the rain.
  - R5: PARTIAL. `「你不应该来这里。」` said twice with her responding `「我知道。」` is the right tension structure (obligation acknowledged, ignored). But the synopsis's key line — `「你不想让我停。」` — is entirely absent. That line is the pivot of this climax: it is his reading of her and her failure to deny it. Without it, the scene's stated value pivot (失控开始 → 主动失控) happens physically but not verbally. The value turn is realized through action (she puts her hand on his) but the explicit verbal acknowledgment specified in the synopsis is missing.
  - R6: PASS.
- **Value shift**: PARTIALLY REALIZED. The physical value turn works — her hand covering his, the clasping of fingers, the red nails and the signet ring detail. But the synopsis's verbal pivot (`「你不想让我停。」` + no denial) was supposed to be the explicit language of the shift. Its absence makes the beat feel complete physically but incomplete narratively. The beat earns a value shift through action where the synopsis specified both action AND verbal acknowledgment.
- **Rushed feel**: SLIGHT — at 1143 chars vs 1500 target (-24%), the beat's climax moment (the hand-holding) is delivered but the aftermath is thin. The beat ends on `「她没有松手。」` which is fine as a closing line but the beat could use one more concrete beat to breathe.
- **Overall: OK (missing key line)**
- The physical choreography is good. The missing `「你不想让我停。」` is a direct spec violation. Add it.

---

### b5a (失控被揭示 → 克制而动摇)

- **Chinese quotes**: PASS — one dialogue line `「静安寺。」` implied from earlier beat's continuation; no new dialogue in b5a.
- **Banned phrases found**: NONE.
- **Anti-melodrama:**
  - Rule A: PASS.
  - Rule B: BORDERLINE. Three physical signals: foot ache (line 27: `「脚踝有一点酸」`), breathing sounds in dark (line 37: `「能听见自己的呼吸声」`), nails in palm (line 37: `「指甲压进掌心的肉里，留下几道浅浅的印子」`). Two would be max; three is stacking.
  - Rule C: PASS — no overwrought metaphors.
  - Rule D: PASS — this is a low-beat ending for the A-branch. The mundane texture (key ring with cartoon charm, old from college, worn) earns its place.
- **Game Writing Rules:**
  - R1: PASS. She plants the rose in the garden bed (specific, active). She navigates the apartment. She puts the phone face-down.
  - R2: PASS. Key chain charm as a character detail is rendered through touch.
  - R3: PASS.
  - R4: PARTIAL. The game-relevant information (she hasn't deleted the number; she's still thinking about him) is rendered through interiority rather than action. The phone placed face-down is a good concrete gesture but its stakes are implicit.
  - R5: No dialogue; appropriate for this ending beat.
  - R6: PASS. The stakes are internal but clearly established by the finger-clenching in the dark.
- **Value shift**: REALIZED. The turn from 失控被揭示 to 克制而动摇 is correctly ambivalent — she goes to bed without calling, which is control; but `「她的手指在被子里紧紧地攥着，指甲压进掌心的肉里」` is the body overriding the conscious restraint. Value shift line: `「黑暗中，她能听见自己的呼吸声，还有窗外偶尔驶过的车声。她的手指在被子里紧紧地攥着，指甲压进掌心的肉里，留下几道浅浅的印子。」`
- **Rushed feel**: SLIGHT — at 1164 chars vs 1500 target (-22%). The ending is emotionally complete but brief. One more paragraph of physical detail in the apartment (or a longer moment with the rose) would give it more weight.
- **Overall: OK**
- Correctly quiet. The A-branch ends in restraint that is visibly costing her something. The rose planted in the flower bed is the best concrete image in any ending beat.

---

### b5b (主动失控 → 完全失守)

- **Chinese quotes**: PASS — no dialogue. Appropriate for the climactic physical beat.
- **Banned phrases found**: NONE.
- **Anti-melodrama:**
  - Rule A: PASS.
  - Rule B: VIOLATION. Final paragraph (lines 45-51) stacks: rain on skin (凉), body heat contrast (`一种奇异的对比`), eyes closed feeling rain, lips cold with whiskey taste. Four distinct sensory tracks in one paragraph at the climax moment. This is the textbook Rule B violation — telegraphing the emotion by listing sensations.
  - Rule C: `「两种味道在接触的那一刻混在一起，变成了一种她无法命名的味道。」` — the `无法命名` phrasing appears twice in the run (also b1 line 35, b3b line 51). Repeated across the run it becomes a cliché. In b5b itself, the kiss-taste metaphor is not overwrought, but `无法命名` is a lazy exit from description.
  - Rule D: PASS — this is the B-branch climax; sustained peak is appropriate here.
- **Game Writing Rules:**
  - R1: Su Wan raises her face into the rain (active), grips his neck (active). This beat has her most active physical agency in the whole run.
  - R2: PASS. The taxi, the unfamiliar street, the梧桐 trees — all rendered through arrival and sensation.
  - R3: PASS. Short action units.
  - R4: PARTIAL. The beat is primarily sensory/atmospheric. There are no concrete game objects or clues — appropriate for an ending beat but worth noting.
  - R5: No dialogue. The kiss itself is the gameplay act.
  - R6: PASS. Stakes are the physical commitment; they're concrete.
- **Value shift**: REALIZED. `「他的嘴唇贴上了她的嘴唇。她没有退开。」` The beat's two-line climax is correctly minimalist. The `没有退开` echoes the beat's pattern of value shifts through negation of restraint.
- **Rushed feel**: SLIGHT — at 1166 chars vs 1500 target (-22%). The ending arrives quickly. The between-bar-and-street segment (cab ride, stopping, alighting) could use more breath.
- **Overall: OK (Rule B violation, repeated phrase)**
- The B-branch ending works as a conclusion. The sensory stacking in the final paragraph crosses Rule B. The `无法命名` repetition is a pattern-level issue to fix in the SKILL.md banned list.

---

## Story-level assessment

### Controlling idea clarity

No explicit controlling idea is stated in story.json. Implied from the beat structure: *"Control maintained through three years of suppression breaks in one night of rain."* The A-branch posits a quieter version: control maintained externally, revealed as illusion internally. The B-branch delivers complete surrender. Both arcs are coherent. The absence of a stated controlling idea in story.json is an upstream planning gap — the Skeleton skill didn't capture it.

### Bifurcating branch distinction (A vs B)

The distinction is thematic and genuine:
- **A-branch** (b3a/b4a/b5a): Su Wan's "control" is revealed as denial. She chooses correctly by her own rules (goes home, doesn't call) but cannot delete the number. The ending is ambivalent — she won and lost simultaneously. This branch is about the cost of control.
- **B-branch** (b3b/b4b/b5b): Su Wan abandons control actively, in stages. Each beat advances the physical proximity. The ending delivers 完全失守 cleanly. This branch is about the pleasure of surrender.

The distinction is present and meaningful. The weakness is b3b — the B-branch setup — which doesn't differentiate itself strongly enough from b3a in terms of what information Su Wan (and the player) gets from Kai. Both branches involve her passively processing what happened. The B-branch should feel more charged from the moment she enters the bar, and the bar scene's elided dialogue is the missed opportunity.

### Pacing / value arc

The eight-beat value arc:

```
职业控制 → 控制感松动 → 面临抉择 ──┬── 表面自控 → 失控被揭示 → 克制而动摇
                                   └── 失控开始 → 主动失控 → 完全失守
```

Pacing issue: b2's value is 面临抉择, but the prose resolves the choice before handing to the player. This means the player enters b3a/b3b having already watched Su Wan choose, not having chosen themselves. The branch seam is exposed as a narrative rather than a player decision.

b1 and b2 feel long relative to the branch beats — they're both at the same length (~1800-2000 Chinese chars) even though b1 is a setup beat and b2 is the choice pivot. The branch beats at 1143-1236 chars feel comparatively rushed, especially for the three climax beats (b4a, b4b) and endings (b5a, b5b) which carry the emotional weight.

### Anti-melodrama (Rule D — not every beat is crisis)

PASS at the story level. The A-branch is appropriately low-intensity post-choice. b3a (taxi ride) and b5a (going to bed) are mundane and earn that quality. b4a (the phone climax) is the only A-branch peak and it hits correctly. The B-branch peaks at b4b and b5b, which is correct. b3b (bar scene) should be a warm-up to the B-climax and mostly succeeds in staying below full intensity. No beat-every-beat crisis pattern detected.

---

## Compared to old baseline bundle (bundles/e2e-agent-2026-04-18/prose/)

The baseline contains only four files: b1.md, b2.md, b3A.md (branch A), b3B.md (branch B). No b4 or b5 equivalent.

### Quality shifts

**Improvements:**
- **Banned phrase hygiene**: Both runs are clean, but the new run's b1 and b3a are more disciplined — the baseline b3A opens with `「她伸出手，接过那枝玫瑰。」` and immediately delivers Kai's eye-color observation (`「你的眼睛，在这个灯光下是琥珀色的。」`), which has a slight 浮夸 quality the new run avoids.
- **Physical concreteness**: The new run's b4a (phone delete sequence) has no equivalent in the baseline — it's a structural addition that genuinely advances the game-writing quality.
- **Character voice**: The new Su Wan is quieter, more internally controlled. The baseline's Su Wan explicitly trembles and has `「她感觉到自己的指尖在发抖。不是因为冷。」` — which technically passes Rule A but is closer to the line than the new run's physical restraint.

**Regressions:**
- **Kai's dialogue density**: The baseline b2 gives Kai a more active information role (`「前面有一家花店……二十四小时营业。我刚订了一束玫瑰」` — he has a plan, a story, a reason). The new run's Kai is almost entirely declarative (`「三年了。」` `「你记得我。」` `「跟我走。」`). He's more menacing, less interesting. The baseline's Kai has more texture.
- **Baseline b3B** delivers a full scene in the flower shop with physical choreography (he cuts rose stems, she touches his hand across the counter, the shop clerk pretends not to look). This is better game-writing than new b3b's elided bar conversation. The new b3b discards the equivalent scene by summarizing the bar conversation: `「她不记得具体说了什么」`.
- **Choice beat architecture**: The baseline b2 ends cleanly at an explicit fork (`「两个选择。雨声填满了她不做声的那几秒。」`). The new b2 tries to resolve the choice AND re-open it, which is architecturally inferior.

**Sideways:**
- Atmosphere and setting quality is comparable.
- Both runs handle the napkin object well (new run introduces it earlier in b1, which is better continuity).
- The new run's wardrobe details are richer (consistent with the detailed character sheets) but feel slightly catalogued in b1 (line 11 lists every clothing item as a block, which reads as inventory not scene).

---

## Specific recommendations

### Prompt / skill changes for next run

1. **Add to SKILL.md self-check**: `「- Does the prose count Chinese characters and confirm within ±10% of beat.targetWordCount? (NOT a self-reported estimate — count them.)」` The footnote hallucination ("二千五百字" on all beats) indicates the agent is not actually counting. Add an explicit instruction to use `len([c for c in prose if '\u4e00' <= c <= '\u9fff'])` as the metric.

2. **Fix choice-beat instruction**: Add to SKILL.md under "The Gap": `「Choice beats (beat.type == 'choice') must END at the decision point, not resolve it. The prose builds to the choice; the player makes it. Do NOT have the protagonist choose inside the choice beat — stage the moment of maximum tension and stop.」`

3. **Require synopsis key lines**: Add to SKILL.md Workflow step 4: `「If the beat synopsis contains a specific line of dialogue (in 「」), that line MUST appear verbatim in the prose. It is the value-turn pivot designated by Skeleton.」` This would have caught the b4b missing `「你不想让我停。」`.

4. **Forbid conversation elision**: Add to game-writing-rules.md under R5: `「NEVER summarize a dialogue exchange with '她不记得具体说了什么' or equivalent. If the conversation happened, write it. If you can't write it, cut it from the synopsis.」`

5. **B-branch differentiation**: The Skeleton skill should be prompted to make the B-branch setup beat (b3b) distinct from A-branch (b3a) in kind, not just direction. The bar scene and the taxi scene are both "Su Wan sits with her thoughts" — they should be different in what new information is disclosed.

6. **B4a model for climax beats**: Use b4a as a positive exemplar in the SKILL.md reference. Specifically: the protagonist operating a UI (phone, app, physical button) as a proxy for psychological stakes is the kind of concrete game-writing that distinguishes this from novel prose. Should become a template.

### New banned-phrase additions

These patterns appeared in the new run and should be added to banned-phrases.md:

| Phrase | Category | Reason |
|--------|----------|--------|
| `一种她无法命名的` / `无法命名` | Vague-exit cliché | Appears 3× across the run (b1, b3b, b5b); functions as an escape hatch from having to actually describe the thing |
| `一种奇异的对比` | Stacked-contrast cliché | Appears in b4b and b5b; describes the temperature difference between hands as "奇异对比" rather than rendering the specific sensation |
| `她把手指收回来，放在膝盖上` | Repetitive gesture | This exact phrase or near-exact variant appears in b1, b3a, b4a — it's the agent's default "reset" gesture |
| `一下，两下，三下——然后停下来` | Enumerated nervous gesture | Used verbatim in both b3a and b4a; a recycled beat |
| `不知道是X的作用，还是别的什么` | Vague interior cliché | Appears in b3b (`不知道是酒精的作用，还是别的什么`) and b4b — equivalent phrasing. Emotion-naming under disguise |
