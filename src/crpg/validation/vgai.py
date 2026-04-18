"""VGAI (Visibility-Gated Attribute Injection) compliance auditor."""
from dataclasses import dataclass
from crpg.types import Shot, Character

# Framing → visible regions. Keep in sync with STRONG_SUFFIX table.
# torso_back is treated as satisfying torso for wrap-around wardrobe items
# like pencil skirts that are visible both front and back.
REGION_MAP: dict[str, set[str]] = {
    "cu_face": {"face", "ear", "neck"},
    "ms_waist_up": {"face", "ear", "neck", "torso", "hand"},
    "three_quarter_knee_up": {"face", "ear", "neck", "torso", "hand", "leg_upper"},
    "full_body_standing": {"face", "ear", "neck", "torso", "hand", "leg", "foot"},
    "feet_ecu": {"foot"},
    "hand_ecu": {"hand"},
    "back_reveal_walking": {"torso", "torso_back", "hand", "leg", "foot"},
    "ws_establishing": set(),
}

@dataclass(slots=True)
class VgaiViolation:
    shot_id: str
    kind: str  # "vgai" | "mutex" | "ws_nonempty" | "unknown_framing" | "unknown_attr"
    attr: str | None
    reason: str

def _build_attr_map(character: Character, wardrobe_state: str) -> dict[str, str]:
    """Return {attr_name: anchor} combining persistent grooming + requested wardrobe state."""
    attrs: dict[str, str] = {g.name: g.anchor for g in character.persistent_grooming}
    ws = character.wardrobe_states.get(wardrobe_state)
    if ws:
        for item in ws.items:
            attrs[item.name] = item.anchor
        for removed in ws.removes:
            attrs.pop(removed, None)
    return attrs

def validate_shot(shot: Shot, character: Character) -> list[VgaiViolation]:
    violations: list[VgaiViolation] = []
    visible = REGION_MAP.get(shot.camera_framing)
    if visible is None:
        return [VgaiViolation(shot.shot_id, "unknown_framing", None,
                              f"unknown framing: {shot.camera_framing}")]
    attr_anchor = _build_attr_map(character, shot.wardrobe_state_used)

    # ws_establishing must have empty vgai_injected_attrs
    if shot.camera_framing == "ws_establishing" and shot.vgai_injected_attrs:
        for a in shot.vgai_injected_attrs:
            violations.append(VgaiViolation(
                shot.shot_id, "ws_nonempty", a,
                "ws_establishing visible_regions is empty; no attrs may inject"))

    # VGAI check: each injected attr's anchor must be in visible_regions
    for attr in shot.vgai_injected_attrs:
        anchor = attr_anchor.get(attr)
        if anchor is None:
            violations.append(VgaiViolation(
                shot.shot_id, "unknown_attr", attr,
                f"attr {attr!r} not in character_sheet"))
            continue
        if shot.camera_framing == "ws_establishing":
            continue  # already flagged above
        if anchor not in visible:
            violations.append(VgaiViolation(
                shot.shot_id, "vgai", attr,
                f"{attr} (anchor={anchor}) not in visible_regions {sorted(visible)}"))

    # Mutex check
    injected = set(shot.vgai_injected_attrs)
    for group in character.mutex_groups:
        common = set(group) & injected
        if len(common) >= 2:
            violations.append(VgaiViolation(
                shot.shot_id, "mutex", None,
                f"mutex pair {sorted(common)} both injected"))

    return violations

def validate_shot_list(shots: list[Shot], character: Character) -> list[VgaiViolation]:
    out: list[VgaiViolation] = []
    for s in shots:
        out.extend(validate_shot(s, character))
    return out
