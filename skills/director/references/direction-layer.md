# Direction Layer — Visual DNA Layer 8

> **Rule**: Every shot's `final_prompt` MUST include a Direction section that frames the image as a candid mid-action moment, not a staged portrait. Without this, Grok Imagine defaults to stock-photo composition — subject facing camera, symmetric pose, frozen expression. That's the single biggest reason images feel "lifeless" even when identity and wardrobe are correct.

## Five rules for the Direction section

### R1 — Mid-action framing

Every frame is a candid documentary still captured mid-action, not a staged portrait. Subjects are DOING something with hands, bodies, or environment. No subject faces camera unless confrontation itself is the scene.

- Bad: "Su Wan stands under the subway entrance holding a rose."
- Good: "Mid-moment: Su Wan's fingers have just closed around the rose stem; her other hand is still half-raised from the handoff, thumb and forefinger lingering in the air."

### R2 — Micro-expression tells (specific muscle, not interpretation)

Use **specific physical tells**, never emotion adjectives. Each shot picks 2–3 tells max.

**Approved tell vocabulary:**
- half-raised brow
- pressed lips
- dilated pupils
- corner-of-eye glance
- jaw tension
- lower lip caught between teeth (inside the mouth, lips still sealed)
- lower lip pressing inward
- faint smile fading
- nostril flare
- chin drop
- single Adam's apple swallow
- shoulder drop / micro-exhale
- hand pausing mid-reach
- weight shift from one foot to the other

**Forbidden tells** (these break image generation by being rendered literally):
- tongue wetting lips / tongue visible / tongue tip
- teeth bared / mouth open wide
- any tell that forces the mouth open and exposes interior

Always specify "mouth closed" or "lips sealed" when emphasizing facial muscles, to prevent the model's default to open-mouth.

**Per-character signature tell** (assign one per named character, reuse across their shots for consistency):
- Protagonists / POV: pick one of {corner-of-eye glance, half-lidded eyes, jaw tension}
- Antagonists / opposite-party: pick one of {slow blink hold, single nostril flare, pressed lips}

### R3 — Body language four constraints

Every shot with a visible body MUST express:

1. **Weight shift** — one leg bearing more, slight lean, not symmetric.
2. **Hands doing something** — holding / mid-gesture / fingers tensed / resting on surface / pausing mid-reach.
3. **Gaze direction** — rarely at camera; prefer at object, at another character, at middle distance, past the lens, at floor.
4. **Asymmetry** — one shoulder lower, one brow higher, weight off-center, head tilted.

### R4 — Verb bias (present continuous)

Prompt verbs should be present continuous, implying action caught in progress:
- lighting / reaching / pausing / glancing / tensing / swallowing / clenching / fading / hesitating / withdrawing

**Avoid static nouns** that freeze the model into stock-photo mode:
- "pose", "portrait", "stance", "look", "expression"

### R5 — Photographic reference grammar

Invoke documentary / photojournalism / cinema by NAME rather than generic style keywords. Stronger style signal than "noir" or "cinematic" alone.

**Approved references for crpg noir (pick 1 per shot):**
- "in the style of Nan Goldin's intimacy"
- "Wong Kar-wai's temporal hesitation"
- "Saul Leiter's compositional looseness"
- "Gregory Crewdson suspended cinematic moment"
- "Jim Goldberg documentary tension"
- "Philip-Lorca diCorcia constructed-documentary framing"
- "Daidō Moriyama street grain"

These steer the model toward candid/intimate/hesitant rather than glossy/staged.

## Assembly into final_prompt

Direction section template:

```
Direction: mid-moment — {what is happening right NOW, present continuous, per character};
{gaze for each visible character}; {1–2 tells per visible face, from vocabulary above};
{1 body-language constraint per visible body}; captured like {photographic reference}.
```

Example assembled:

```
Direction: mid-moment — Su Wan's fingers are just closing around the rose stem,
her other hand still half-raised; her gaze drops from Kai's mouth to the rose
to his knuckles; one brow half-raised, lower lip pressing inward (mouth closed);
weight shifted onto her left heel, right shoulder lower than left; captured
like Nan Goldin's intimacy, grainy, caught mid-breath.
```

## Self-check before emitting final_prompt

- Is there a "mid-moment:" phrase, or equivalent present-continuous framing?
- Did I pick 2–3 specific muscle-level tells (not emotion names)?
- Did I specify gaze direction for every visible character's face?
- Did I cite ONE photographic reference by name?
- No forbidden tells (tongue / open mouth / bared teeth)?
- No static-noun verbs (pose / portrait / stance)?

If any answer is no, rewrite the Direction section before calling `render_image`.
