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

    # Character anchors: {char_name: {"body": Path, "face": Path}} — populated
    # via render_anchor before any shot renders; render_image consults this
    # map when a Shot has anchor_ref="<char>:<body|face>".
    anchors: dict[str, dict[str, Path]] = field(default_factory=dict)

    # Shots that could not be rendered (e.g. Grok moderation blocked after
    # all retries). Each entry: {beat_id, shot_id, reason}. Surfaced in
    # finish_bundle's summary so the user knows what's missing.
    failed_shots: list[dict[str, str]] = field(default_factory=list)
