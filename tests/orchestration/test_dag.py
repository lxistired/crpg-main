import pytest
from crpg.orchestration.dag import topological_layers, CycleError
from crpg.types import Beat

def mk(id_, deps=()):
    return Beat(id=id_, type="narrative", synopsis="",
                valueBefore="x", valueAfter="y",
                targetWordCount=100, targetShotCount=1, depends_on=list(deps))

def test_linear_chain():
    beats = [mk("a"), mk("b", ["a"]), mk("c", ["b"])]
    layers = topological_layers(beats)
    assert [{x.id for x in L} for L in layers] == [{"a"}, {"b"}, {"c"}]

def test_bifurcation():
    beats = [mk("main"), mk("A", ["main"]), mk("B", ["main"])]
    layers = topological_layers(beats)
    assert [{x.id for x in L} for L in layers] == [{"main"}, {"A", "B"}]

def test_independent_beats_parallel():
    beats = [mk("x"), mk("y"), mk("z")]
    layers = topological_layers(beats)
    assert [{x.id for x in L} for L in layers] == [{"x", "y", "z"}]

def test_cycle_raises():
    beats = [mk("a", ["b"]), mk("b", ["a"])]
    with pytest.raises(CycleError):
        topological_layers(beats)

def test_unknown_dep_raises():
    beats = [mk("a", ["nonexistent"])]
    with pytest.raises(ValueError, match="nonexistent"):
        topological_layers(beats)
