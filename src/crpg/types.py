"""Core data models for the crpg pipeline."""
from typing import Literal
from pydantic import BaseModel, Field

Anchor = Literal[
    "face", "ear", "neck",
    "hand", "torso", "torso_back",
    "leg", "leg_upper", "foot",
]

BeatType = Literal[
    "narrative", "choice", "check", "merge", "act_break", "ending",
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

class ShotList(BaseModel):
    beat_id: str
    shots: list[Shot]
