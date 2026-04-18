import json, pytest
from pathlib import Path
from crpg.bundle import BundleWriter, BundleMeta
from crpg.types import Story, StoryMeta, Beat, Character, Base

def test_bundle_writer_creates_files(tmp_path):
    story = Story(
        meta=StoryMeta(title="t", genre="n", contentLength="short",
                       detailRichness="detailed", structure="bifurcating"),
        beats=[Beat(id="intro", type="narrative", synopsis="s",
                    valueBefore="x", valueAfter="y",
                    targetWordCount=100, targetShotCount=1)],
        edges=[],
    )
    chars = {"Su Wan": Character(
        base=Base(age=28, ethnicity="Chinese", hair="h", skin="s", eyes="e", jaw="j"),
    )}
    meta = BundleMeta(
        generated_at="2026-04-18T15:00:00Z",
        text_model="kimi-k2-0905",
        text_provider="Groq",
        image_model="grok-imagine-pro",
        suffix_versions={"STRONG": "v1", "FEW_SHOT": "v1", "LENGTH_SHORT": "v1"},
    )
    writer = BundleWriter(out_dir=tmp_path / "bundle")
    writer.write(story=story, characters=chars, meta=meta)
    assert (tmp_path / "bundle" / "story.json").exists()
    assert (tmp_path / "bundle" / "characters.json").exists()
    assert (tmp_path / "bundle" / "meta.json").exists()
    assert (tmp_path / "bundle" / "shots").is_dir()

    # Reloadable
    loaded_story = json.loads((tmp_path / "bundle" / "story.json").read_text())
    assert loaded_story["meta"]["title"] == "t"
    loaded_chars = json.loads((tmp_path / "bundle" / "characters.json").read_text())
    assert "Su Wan" in loaded_chars
    loaded_meta = json.loads((tmp_path / "bundle" / "meta.json").read_text())
    assert loaded_meta["text_model"] == "kimi-k2-0905"

def test_bundle_shot_dir(tmp_path):
    writer = BundleWriter(out_dir=tmp_path / "bundle")
    d = writer.shots_dir(beat_id="intro")
    assert d == tmp_path / "bundle" / "shots" / "intro"
    assert d.exists()
