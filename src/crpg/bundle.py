"""BundleWriter — writes story.json / characters.json / shots/ / meta.json."""
import json
import re
from dataclasses import dataclass, field, asdict
from pathlib import Path
from crpg.types import Story, Character

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
