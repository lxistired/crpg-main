import pytest
from crpg.validation.schema import parse_skeleton_output, SchemaError

def test_parse_good_skeleton():
    raw = '''{"story": {
      "meta": {"title":"t","genre":"noir","contentLength":"short",
               "detailRichness":"detailed","structure":"bifurcating"},
      "beats": [{"id":"intro","type":"narrative","synopsis":"s",
                 "valueBefore":"calm","valueAfter":"alert",
                 "targetWordCount":2500,"targetShotCount":5,
                 "wardrobe_state":"public_formal","depends_on":[]}],
      "edges": []
    },
    "characters": {
      "Su Wan": {
        "base":{"age":28,"ethnicity":"汉","hair":"h","skin":"s","eyes":"e","jaw":"j"},
        "persistent_grooming":[{"name":"red_fingernails","anchor":"hand"}],
        "wardrobe_states":{"public_formal":{"items":[
          {"name":"black_pencil_skirt","anchor":"torso"}], "removes":[]}},
        "mutex_groups":[]
      }
    }}'''
    story, chars = parse_skeleton_output(raw)
    assert story.meta.title == "t"
    assert "Su Wan" in chars

def test_parse_code_fenced():
    raw = '```json\n{"story":{"meta":{"title":"t","genre":"n","contentLength":"short","detailRichness":"standard","structure":"linear"},"beats":[],"edges":[]},"characters":{}}\n```'
    story, chars = parse_skeleton_output(raw)
    assert story.meta.title == "t"

def test_parse_invalid_json_raises():
    with pytest.raises(SchemaError, match="JSON"):
        parse_skeleton_output("not json")

def test_parse_missing_top_keys():
    with pytest.raises(SchemaError, match="story"):
        parse_skeleton_output('{"characters":{}}')
