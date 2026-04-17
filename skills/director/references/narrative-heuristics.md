# Narrative → Shot Decomposition Heuristics

How to turn prose narrative into a shot list with the right rhythm, coverage, and emotional beats.

## Beat classification

Read the narrative. Classify each beat:

| Beat type | Trigger | Typical shots | Notes |
|-----------|---------|---------------|-------|
| **Establishing** | Scene opens / location changes | 1 × WS establishing | No character attrs, let environment dominate |
| **Arrival** | Character enters scene | 1-2 shots: full_body_standing or ms_waist_up | First full look at them in new scene |
| **Exposition** | Character does something, reveals context | 1-2 × MS | Steady medium framing for dialogue or action |
| **Emotional beat** | Character feels something important | 2-3 shots: CU + reverse reaction CU (if 2 chars) | The core of storytelling |
| **Revelation** | Something is shown/discovered | 1-2 shots: CU reaction + ECU insert of thing | Insert comes AFTER or BEFORE the reaction shot |
| **Confrontation** | 2 characters face off | 3-5 shots: WS master + MS 2-shot + CU × 2 (both reactions) + optional ECU tension | Full coverage for conflict |
| **Transition** | Movement between locations | 1 shot: back_reveal_walking OR WS | |
| **Action** | Fast physical event | 3-5 shots: WS action + MS body + ECU impact point | |
| **Intimate** | Quiet shared moment | 2-3 shots: 2-shot MS + CU each + optional OTS | |
| **Resolution** | Scene closes | 1 shot: WS or MS static beat | |

## Shot count per beat

Scale with narrative weight:

- **Background beat**: 1 shot
- **Normal beat**: 2 shots
- **Key moment**: 3-5 shots
- **Climax**: 5-8 shots

Do not cover every sentence with a shot. Summarize minor beats, expand major ones.

## Shot rhythm rules

**Use shot size variation.** Never have 3 consecutive shots of the same size (e.g., 3 MS in a row = visual monotony). Mix:

- WS → MS → CU (move in, emotional)
- CU → MS → WS (pull out, release)
- MS → ECU → MS (insert punctuation)
- CU (A) → CU (B) → MS (both) (shot-reverse-shot dialog)

**Establishing shots bookend**: open and close scenes with wider shots, go tight in the middle.

**Inserts after emotional beats**: after a CU of reaction, an ECU of what they reacted to sells it.

## Gaze choreography for storytelling

Gaze is how you tell story WITHOUT dialogue. Use these patterns:

| Pattern | Semantic |
|---------|----------|
| Mutual gaze 2-shot MS | Recognition, connection, confrontation, romantic charge |
| Asymmetric gaze 2-shot MS | Emotional asymmetry (A pursuing, B withdrawing) |
| CU A looking viewer-right → CU B looking viewer-left (reverse) | Standard dialog coverage (180° rule) |
| OTS A foreground → B facing camera | B's reaction from A's POV |
| POV direct-camera stare (B looks at camera) | B confronting viewer / speaking to reader |
| CU A + gaze drops / eyes close | Shame, defeat, vulnerability |
| CU A + eyes widen | Shock, recognition |
| CU A + single tear | Decision moment, internal breaking |
| 2-shot + both looking at prop/screen | Shared discovery, attention |
| Silhouette figure at doorway | Arrival, threat, mystery (do NOT gate attrs on silhouette) |

## Never do

- **3-character gaze narrative**. Grok cannot reliably render gaze interaction among 3+. Keep gaze lines to pairs. Group shots of 3+ should be decorative (everyone looking same direction, or at a central object).
- **Crowded dialog** (5+ characters all in frame trying to communicate). Cover with insert + CU cycles.
- **Dutch angle** for tension. Use lighting / composition / color instead.
- **Unexplained jump cuts** in shot size (ECU → WS → ECU is jarring). Bridge with a MS.

## Pose ≠ framing ≠ gaze

These are separate decisions:

- **Framing** = camera distance + angle + what body regions are visible
- **Pose** = what the character is physically doing
- **Gaze** = where the character is looking

Specify each independently. A CU face can have:
- Gaze: direct to camera / off-frame left / eyes closed / down
- Pose: hand to cheek / hand not visible / chin lifted / slumped

## Cross-shot continuity

Within a scene:
- **Keep the wardrobe_state** unless the narrative changes the character's situation
- **180° rule**: if shot 1 has A on viewer-left, keep A on viewer-left in subsequent shots of that scene
- **Eyeline match**: if shot 1 CU shows A looking viewer-right, shot 2 CU of B should show B looking viewer-left

Across scenes:
- **Wardrobe changes MUST be motivated**: character arrived at new location → changed clothes → new state
- Do NOT inject wardrobe continuity across scene cuts where the plot allows wardrobe change

## Anchor image use

If the narrative demands strong face consistency across shots:
1. Generate a clean anchor shot first (establishing MS or CU of the character alone)
2. Use `image_url` in subsequent shots within the same scene
3. DO NOT expect anchor to carry wardrobe or environment — only face ~70%

For different scenes, generate new anchor each time (or accept face drift).

## Heuristic examples

### Prose: "She knocked on the door. He opened it. They stared at each other without speaking."

Decomposition (3 beats):
1. **Arrival beat**: MS of her at the door, knuckles raised → 1 shot
2. **Reveal beat**: Reverse MS — door opens, him standing there → 1 shot
3. **Confrontation beat**: 2-shot MS mutual gaze + optional CU each → 2-3 shots

Total: 4-5 shots.

### Prose: "She walked in, kicked off her heels, and collapsed on the sofa."

Decomposition (1 compressed beat):
1. MS of entry + **ECU** of heels coming off + MS of collapse → 3 shots
   - Alternatively, 1 single MS covering entry + pan to sofa if action is mundane

Scale with narrative weight.

### Prose: "He saw the letter on the table. Her name was on it."

Decomposition (2 beats, revelation):
1. MS of him seeing the table → 1 shot
2. **ECU insert** of letter with name visible → 1 shot
3. CU reaction of his face → 1 shot

Total: 3 shots.

## Default budget per scene

- Short scene (1-2 narrative sentences): 2-3 shots
- Medium scene (a paragraph): 4-6 shots  
- Long scene (multiple paragraphs): 7-10 shots
- Climax scene: 8-12 shots

For a 10-scene short story: expect ~50-80 shots total. For a 30-scene novella: expect ~200-300 shots.
