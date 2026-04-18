"""Core data models for the crpg pipeline."""
from typing import Literal
from pydantic import BaseModel, Field

Anchor = Literal[
    "face", "ear", "neck",
    "hand", "torso", "torso_back",
    "leg", "leg_upper", "foot",
]

BeatType = Literal[
    "narrative", "choice", "check", "merge", "act_break", "climax", "ending",
]

DetailRichness = Literal["concise", "standard", "detailed", "extreme"]
ContentLength = Literal["short", "medium", "long"]
Structure = Literal["linear", "bifurcating", "funnel", "web"]

class Base(BaseModel):
    age: int
    ethnicity: str
    hair: str
    skin: str
    eyes: str
    jaw: str

class Grooming(BaseModel):
    name: str
    anchor: Anchor
    sub_anchor: str | None = None
    removable_by: str | None = None

class WardrobeItem(BaseModel):
    name: str
    anchor: Anchor
    covers: list[str] = Field(default_factory=list)
    # Verbatim visual description injected byte-for-byte into every shot prompt
    # that uses this item. Director MUST NOT paraphrase. See Visual DNA Layer 3
    # + Layer 10 (for high-prior garments, append disambiguation_layers too).
    visual_description: str = ""
    disambiguation_layers: list[str] = Field(default_factory=list)

class WardrobeState(BaseModel):
    items: list[WardrobeItem]
    removes: list[str] = Field(default_factory=list)

class Character(BaseModel):
    base: Base
    persistent_grooming: list[Grooming] = Field(default_factory=list)
    wardrobe_states: dict[str, WardrobeState] = Field(default_factory=dict)
    mutex_groups: list[list[str]] = Field(default_factory=list)

class Beat(BaseModel):
    id: str
    type: BeatType
    synopsis: str
    value_before: str = Field(alias="valueBefore")
    value_after: str = Field(alias="valueAfter")
    wardrobe_state: str | None = None
    target_word_count: int = Field(alias="targetWordCount")
    target_shot_count: int = Field(alias="targetShotCount")
    depends_on: list[str] = Field(default_factory=list)

    model_config = {"populate_by_name": True}

class Edge(BaseModel):
    from_: str = Field(alias="from")
    to: str
    condition: str | None = None

    model_config = {"populate_by_name": True}

class StoryMeta(BaseModel):
    title: str
    genre: str
    content_length: ContentLength = Field(alias="contentLength")
    detail_richness: DetailRichness = Field(alias="detailRichness")
    structure: Structure
    # poeticMode: keywords become atmospheric metaphors (default); when False,
    # Script treats keywords as literal plot elements. Temperature cap applies.
    poetic_mode: bool = Field(default=True, alias="poeticMode")

    model_config = {"populate_by_name": True}

class Story(BaseModel):
    meta: StoryMeta
    beats: list[Beat]
    edges: list[Edge]

class Shot(BaseModel):
    shot_id: str
    camera_framing: str
    pose: str
    wardrobe_state_used: str
    vgai_injected_attrs: list[str]
    # Different LLMs emit either list-of-strings or dict-of-string; Task 3.2 parser
    # normalizes for downstream consumers.
    vgai_dropped_attrs_with_reason: list[str] | dict[str, str]
    final_prompt: str
    # Optional per-shot aspect ratio. If None, render_image uses default "16:9".
    # Agent can set e.g. "9:16" for vertical story panels.
    aspect_ratio: str | None = None
    # Optional anchor reference. Format: "<character_name>:<body|face>". When set,
    # render_image loads the anchor PNG + passes it as image_url to Grok Imagine
    # for identity lock across the story. None = text-to-image (no reference).
    anchor_ref: str | None = None
    # Which characters appear in this shot (for multi-char VGAI validation).
    # If omitted, validator assumes single-char and uses the POV.
    characters_in_frame: list[str] = Field(default_factory=list)

class ShotList(BaseModel):
    beat_id: str
    shots: list[Shot]
