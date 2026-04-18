"""BundleWriter — writes story.json / characters.json / shots/ / prose/ / meta.json."""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import TYPE_CHECKING
from crpg.types import Story, Character

if TYPE_CHECKING:
    pass

@dataclass
class BundleMeta:
    generated_at: str
    text_model: str
    text_provider: str
    image_model: str
    suffix_versions: dict[str, str] = field(default_factory=dict)
    git_sha: str | None = None

class BundleWriter:
    def __init__(self, out_dir: Path) -> None:
        self.out_dir = Path(out_dir)
        self.out_dir.mkdir(parents=True, exist_ok=True)
        (self.out_dir / "shots").mkdir(exist_ok=True)

    def shots_dir(self, *, beat_id: str) -> Path:
        # Sanitize: strip any path-traversal or separators; only alphanumerics + underscore/hyphen
        safe = re.sub(r"[^A-Za-z0-9_-]", "_", beat_id)
        d = self.out_dir / "shots" / safe
        d.mkdir(parents=True, exist_ok=True)
        return d

    def write_beat_shots(self, *, beat_id: str, shots: list) -> Path:
        """Write Director's shot list to bundle/shots/<beat_id>/shots.json.

        `shots` is a list of Shot pydantic models. Returns the written path.
        Co-located with the PNG files for that beat so debugging is trivial:
          cat bundle/shots/<beat>/shots.json  → see every final_prompt + VGAI info
        """
        safe = re.sub(r"[^A-Za-z0-9_-]", "_", beat_id)
        d = self.out_dir / "shots" / safe
        d.mkdir(parents=True, exist_ok=True)
        # Serialize shots — use model_dump(mode="json") for pydantic v2 compatibility
        blob = [s.model_dump(mode="json") for s in shots]
        path = d / "shots.json"
        path.write_text(json.dumps(blob, ensure_ascii=False, indent=2), encoding="utf-8")
        return path

    def write_beat_prose(self, *, beat_id: str, prose: str) -> Path:
        """Write a beat's prose to bundle/prose/<beat_id>.md and return the path."""
        prose_dir = self.out_dir / "prose"
        prose_dir.mkdir(parents=True, exist_ok=True)
        safe = re.sub(r"[^A-Za-z0-9_-]", "_", beat_id)
        path = prose_dir / f"{safe}.md"
        path.write_text(prose, encoding="utf-8")
        return path

    def write_story_md(self, *, story: Story) -> Path:
        """Auto-generate human-readable story.md from story.json + prose files.

        Structure:
          # <title>
          **meta**: genre, length, detail, structure

          ## <beat.id>: <beat.synopsis> (<shot count> shots)
          *value: before → after*
          <full prose if prose/<beat.id>.md exists, else "(prose not yet generated)">
          ---
        """
        prose_dir = self.out_dir / "prose"
        lines: list[str] = []
        lines.append(f"# {story.meta.title}")
        lines.append("")
        lines.append(
            f"**Genre**: {story.meta.genre}  |  **Length**: {story.meta.content_length}  |  "
            f"**Detail**: {story.meta.detail_richness}  |  **Structure**: {story.meta.structure}"
        )
        lines.append("")
        lines.append("---")
        lines.append("")
        for beat in story.beats:
            lines.append(f"## {beat.id} · {beat.synopsis}")
            lines.append("")
            lines.append(
                f"*{beat.value_before} → {beat.value_after}*  ·  "
                f"{beat.target_shot_count} shots  ·  state: `{beat.wardrobe_state}`"
            )
            lines.append("")
            safe = re.sub(r"[^A-Za-z0-9_-]", "_", beat.id)
            prose_path = prose_dir / f"{safe}.md"
            if prose_path.exists():
                lines.append(prose_path.read_text(encoding="utf-8"))
            else:
                lines.append("*(prose not yet generated)*")
            lines.append("")
            lines.append("---")
            lines.append("")
        path = self.out_dir / "story.md"
        path.write_text("\n".join(lines), encoding="utf-8")
        return path

    def write(
        self,
        *,
        story: Story,
        characters: dict[str, Character],
        meta: BundleMeta,
    ) -> None:
        (self.out_dir / "story.json").write_text(
            story.model_dump_json(indent=2, by_alias=True), encoding="utf-8",
        )
        chars_blob = {name: c.model_dump(mode="json", by_alias=True) for name, c in characters.items()}
        (self.out_dir / "characters.json").write_text(
            json.dumps(chars_blob, ensure_ascii=False, indent=2), encoding="utf-8",
        )
        (self.out_dir / "meta.json").write_text(
            json.dumps(asdict(meta), ensure_ascii=False, indent=2), encoding="utf-8",
        )
