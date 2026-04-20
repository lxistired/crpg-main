"""Pydantic schema for the Director Plan — the one-shot structured output
emitted by the director_planner agent in Path D (handoff-planner mode).

The planner agent has `output_type=DirectorPlan` and no tools. It produces
the complete anchor + shot list for the whole bundle in a single LLM turn.
Python code then iterates the plan with asyncio.gather to parallelise image
generation, skipping the per-shot tool-call round-trip that limits Grok's
throughput in the iterative Director loop.

xAI `response_format=json_schema` with strict=true does not support: allOf,
minItems, maxItems, minLength, maxLength. This schema therefore uses only
the supported subset; length / content correctness (Style Preamble
byte-lock, etc.) is enforced in Python after the plan is returned.
"""
from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field


class AnchorPlan(BaseModel):
    """One character anchor render (called before any shot that references it).

    Note: the `body` field does NOT include the 735-character Style Preamble.
    Python code prepends the canonical preamble (and the anchor-preamble
    variant) before calling the image API. This keeps the LLM's output JSON
    short enough to fit in one response without getting truncated.
    """
    model_config = ConfigDict(extra="forbid")

    character_name: str = Field(
        description="Character key used in anchor_ref ('<char>:body' / '<char>:face')."
    )
    anchor_type: Literal["body", "face"] = Field(
        description="'body' = 3/4 or full outfit, 9:16 aspect. 'face' = tight CU portrait, 3:4 aspect."
    )
    body: str = Field(
        description=(
            "The CHARACTER-SPECIFIC portion of the anchor prompt: base "
            "identity + every wardrobe item's visual_description verbatim. "
            "Do NOT repeat the Style Preamble here — Python prepends it. "
            "No scene-specific cues. Neutral pose only."
        )
    )


class ShotPlan(BaseModel):
    """One shot to be saved and rendered.

    Like AnchorPlan, `body` excludes the Style Preamble. Python prepends the
    canonical preamble before persist + render.
    """
    model_config = ConfigDict(extra="forbid")

    beat_id: str = Field(description="Beat this shot belongs to (e.g. 'b1', 'b4a').")
    shot_id: str = Field(description="Unique shot id within the beat (e.g. 'b1-1', 's01').")
    body: str = Field(
        description=(
            "Shot body WITHOUT the Style Preamble. Concatenate four "
            "sections in order: Character (base + wardrobe visual_description "
            "verbatim) + Direction (mid-action tell per Direction Layer) + "
            "Scene (setting + props + weather + time) + Framing (camera_framing "
            "+ composition notes). Python prepends the Style Preamble."
        )
    )
    aspect_ratio: str = Field(
        default="16:9",
        description="One of xAI-supported: 1:1 / 3:2 / 4:3 / 16:9 / 19.5:9 / 9:16 / 3:4.",
    )
    anchor_ref: Optional[str] = Field(
        default=None,
        description=(
            "Reference to a pre-rendered anchor as '<character_name>:<body|face>'. "
            "Omit (null) for ws_establishing shots where the subject is too small "
            "for anchors to matter. For cu_face / ms_waist_up → '<char>:face'; for "
            "full_body / three_quarter_knee_up / back_reveal_walking → '<char>:body'."
        ),
    )


class BeatPlan(BaseModel):
    """One beat from the Skeleton output. Produced by skeleton_planner_agent.

    Python downstream uses this to construct each beat's worker_prompt for
    parallel prose generation (no SS-agent-in-the-loop ceremony)."""
    model_config = ConfigDict(extra="forbid")

    id: str = Field(description="Beat id (e.g. 'b1', 'b4a', 'e1').")
    synopsis: str = Field(
        description=(
            "Beat synopsis 2-4 sentences, Chinese. MUST include all "
            "mandated 「」/『』 dialogue lines verbatim — these appear in "
            "the prose. Do not paraphrase quoted text."
        )
    )
    value_before: str = Field(description="2-5 words, tag form (e.g. '职业警觉').")
    value_after: str = Field(description="2-5 words, tag form (e.g. '模糊失控').")
    target_word_count: int = Field(
        description="CJK char target for the prose worker (e.g. 2500)."
    )
    wardrobe_state: str = Field(
        description="snake_case wardrobe state id referenced by the character sheet."
    )
    prior_beat_cues: list[str] = Field(
        default_factory=list,
        description=(
            "0-3 short Chinese phrases about physical / emotional state "
            "carried over from the previous beat (e.g. '黑丝丝光在雨中微泛光')."
        ),
    )
    node_type: Literal["normal", "choice", "climax", "ending"] = Field(
        default="normal",
        description="Structural role; must have exactly one 'climax' per arc.",
    )
    tone: str = Field(
        default="",
        description="Tone / register hint for the worker (e.g. '克制, 压抑, 张力').",
    )


class WardrobeItem(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str = Field(description="snake_case item id.")
    visual_description: str = Field(
        description=(
            "30-80 words canonical string for the Director to paste verbatim. "
            "Includes fabric / cut / color / stockings-strap interaction etc."
        )
    )
    covers: list[str] = Field(
        default_factory=list,
        description="Body regions this item covers (e.g. ['torso', 'thighs']).",
    )


class CharacterPlan(BaseModel):
    """One character sheet from the Skeleton output."""
    model_config = ConfigDict(extra="forbid")

    name: str = Field(
        description=(
            "snake_case identifier used as anchor_ref key "
            "('<name>:body'/'<name>:face')."
        )
    )
    display_name: str = Field(
        description="Canonical Chinese / English display name (for prose)."
    )
    base: str = Field(
        description=(
            "Base identity line: age + ethnicity + build + hair + eyes "
            "+ jawline + skin tone + distinguishing marks (e.g. moles). "
            "Single-paragraph canonical string."
        )
    )
    persistent_grooming: str = Field(
        default="",
        description="Grooming never changes across beats (lipstick, nail polish, etc.).",
    )
    wardrobe_states: list[WardrobeItem] = Field(
        default_factory=list,
        description="All wardrobe items across the story, in any state.",
    )


class StoryMetaPlan(BaseModel):
    model_config = ConfigDict(extra="forbid")
    title: str
    genre: str
    content_length: Literal["short", "medium", "long"]
    detail_richness: Literal["concise", "standard", "detailed", "extreme"]
    structure: Literal["linear", "bifurcating", "funnel", "web"]
    poetic_mode: bool
    controlling_idea: str = Field(
        description="One sentence theme, form: '{finalValue, cause}'."
    )
    antagonism: str = Field(
        description=(
            "Opposing force profile: who/what + which dimension "
            "(physical/social/personal/intellectual/moral) it out-matches "
            "the protagonist on."
        )
    )


class StoryPlan(BaseModel):
    """Complete structured Skeleton output emitted by skeleton_planner_agent.

    Python iterates `beats` with asyncio.gather to fan out prose workers
    in parallel, replacing the SS-agent-in-the-loop cadence that made the
    prose phase the bottleneck in earlier Path D runs.
    """
    model_config = ConfigDict(extra="forbid")

    meta: StoryMetaPlan
    beats: list[BeatPlan] = Field(
        description="Beats in topological order (linear / bifurcating-aware)."
    )
    characters: list[CharacterPlan] = Field(
        description="All named characters appearing in any beat."
    )
    edges: list[str] = Field(
        default_factory=list,
        description=(
            "Optional: free-text descriptions of beat transitions, one per "
            "line, e.g. 'b3 -> b4a: A branch', 'b3 -> b4b: B branch'."
        ),
    )


class DirectorPlan(BaseModel):
    """Complete director plan produced in one LLM turn.

    Order contract:
    - every AnchorPlan is rendered BEFORE any ShotPlan that references it.
    - anchors should cover every character named in shot anchor_refs.
    - shots should cover every beat that has prose.
    """
    model_config = ConfigDict(extra="forbid")

    anchors: list[AnchorPlan] = Field(
        description=(
            "Two anchors per named character (one 'body' + one 'face'). "
            "Use character names matching characters_markdown exactly."
        )
    )
    shots: list[ShotPlan] = Field(
        description=(
            "All shots for all beats, in topological beat order then shot "
            "order. Every beat with prose MUST appear at least once."
        )
    )
