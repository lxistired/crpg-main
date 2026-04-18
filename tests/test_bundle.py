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

def test_bundle_shot_dir_sanitizes_beat_id(tmp_path):
    writer = BundleWriter(out_dir=tmp_path / "bundle")
    d = writer.shots_dir(beat_id="../../etc/passwd")
    assert d.parent == tmp_path / "bundle" / "shots"
    # Path must stay inside shots dir
    assert str(d.resolve()).startswith(str((tmp_path / "bundle" / "shots").resolve()))


def test_write_beat_prose(tmp_path):
    writer = BundleWriter(out_dir=tmp_path / "bundle")
    path = writer.write_beat_prose(beat_id="b1", prose="这是主段内容。")
    assert path == tmp_path / "bundle" / "prose" / "b1.md"
    assert path.read_text(encoding="utf-8") == "这是主段内容。"


def test_write_beat_prose_sanitizes_id(tmp_path):
    writer = BundleWriter(out_dir=tmp_path / "bundle")
    path = writer.write_beat_prose(beat_id="../hack", prose="x")
    assert str(path.resolve()).startswith(str((tmp_path / "bundle" / "prose").resolve()))


def test_write_story_md_includes_prose(tmp_path):
    story = Story(
        meta=StoryMeta(title="雨夜", genre="noir", contentLength="short",
                       detailRichness="detailed", structure="bifurcating"),
        beats=[Beat(id="b1", type="narrative", synopsis="开场",
                    valueBefore="calm", valueAfter="alert",
                    targetWordCount=200, targetShotCount=2,
                    wardrobe_state="office_exit")],
        edges=[],
    )
    writer = BundleWriter(out_dir=tmp_path / "bundle")
    writer.write_beat_prose(beat_id="b1", prose="主段内容包含 Su Wan")
    path = writer.write_story_md(story=story)
    content = path.read_text(encoding="utf-8")
    assert "# 雨夜" in content
    assert "b1 · 开场" in content
    assert "主段内容包含 Su Wan" in content


def test_write_story_md_missing_prose_placeholder(tmp_path):
    story = Story(
        meta=StoryMeta(title="t", genre="n", contentLength="short",
                       detailRichness="standard", structure="linear"),
        beats=[Beat(id="b1", type="narrative", synopsis="s",
                    valueBefore="x", valueAfter="y",
                    targetWordCount=100, targetShotCount=1)],
        edges=[],
    )
    writer = BundleWriter(out_dir=tmp_path / "bundle")
    writer.write_story_md(story=story)
    content = (tmp_path / "bundle" / "story.md").read_text(encoding="utf-8")
    assert "(prose not yet generated)" in content
