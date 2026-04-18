"""Topological scheduling for beat execution."""
from crpg.types import Beat

class CycleError(Exception):
    pass

def topological_layers(beats: list[Beat]) -> list[list[Beat]]:
    """Group beats into concurrency layers: each layer's beats have no unresolved deps.

    Beats within a layer can run in parallel. Layers run sequentially.
    Raises CycleError on cycles, ValueError on missing deps.
    """
    by_id = {b.id: b for b in beats}
    for b in beats:
        for dep in b.depends_on:
            if dep not in by_id:
                raise ValueError(f"beat {b.id!r} depends on unknown beat {dep!r}")

    remaining = {b.id for b in beats}
    satisfied: set[str] = set()
    layers: list[list[Beat]] = []
    while remaining:
        ready = [b for b in beats if b.id in remaining
                 and all(d in satisfied for d in b.depends_on)]
        if not ready:
            raise CycleError(f"cycle detected; unresolved beats: {sorted(remaining)}")
        layers.append(ready)
        for b in ready:
            remaining.discard(b.id)
            satisfied.add(b.id)
    return layers
