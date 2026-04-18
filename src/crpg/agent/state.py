"""Shared run-time state for the main agent's tools."""
from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from crpg.bundle import BundleWriter
from crpg.llm.xai import XaiImageClient


@dataclass
class AgentState:
    """State injected into every tool call via RunContextWrapper."""

    project_root: Path           # used to resolve skills/<name>/SKILL.md paths
    bundle_writer: BundleWriter  # persists artifacts to the output bundle
    xai_client: XaiImageClient | None  # set only after image gen is reached
    brief: str                    # the user's original brief (whatever format)

    # Progress state written by the agent as it works
    story_emitted: bool = False
    characters_emitted: bool = False
    beats_with_prose: set[str] = field(default_factory=set)
    beats_with_shots: set[str] = field(default_factory=set)
    images_rendered: int = 0
    finished: bool = False
    finish_summary: str = ""

    # Last-seen story / characters data, cached for validate_vgai cross-lookups
    story_data: dict[str, Any] | None = None
    characters_data: dict[str, Any] | None = None
