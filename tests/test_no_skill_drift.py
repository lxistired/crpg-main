"""Drift-detection: skill content must live in skill files, NOT Python source.

Project philosophy (see memory/feedback_crpg_agent_first.md):
The Director / Skeleton / Script passes are agents that execute skills.
Skill content is SKILL.md + references/* — the single source of truth.
Copying skill text into Python source is the exact failure mode we are
guarding against (past incident: DIRECTOR_SYSTEM string in prompts.py
inlined Principle 1 and a "visible through the fabric" layer template,
which directly violated the Director skill's own red-flag list).

This test fails if ANY banned skill fragment appears verbatim in src/.
"""
from __future__ import annotations
from pathlib import Path

ROOT = Path(__file__).parent.parent
SRC = ROOT / "src"

# Skill phrases that must not be inlined in source code. Each entry is a
# phrase that would signal skill content has been copied. Keep the list
# tight so grep stays O(seconds); expand when new drift patterns are seen.
BANNED_PHRASES: list[str] = [
    # Past incident: layer template that assumed open-toe footwear
    "visible through the fabric",
    "visible through",
    # Principle headers from SKILL.md (numbered list 1-10)
    "Base identity is region-gated",
    "Grooming travels",
    "Wardrobe is situational",
    "Default KEEP on uncertainty",
    "Fact over instruction",
    "Pose doesn't suppress",
    "Mutex picks one",
    "Grok hard limits",
    "Shot grammar for rhythm",
    # References file content hooks
    "9 failure modes",
    "Framing Expansion",
    "Proxy Substitution",
    "Anatomical Relocation",
    # Rationalization counter hooks
    "pose-dependent",
    "may not be primary focus",
]

# Paths to scan. Only Python source under src/ is subject to the ban.
# (Tests may legitimately reference these strings, e.g. to check skill docs.)
SCAN_DIRS = [SRC / "crpg"]


def _collect_python_files() -> list[Path]:
    files: list[Path] = []
    for d in SCAN_DIRS:
        files.extend(p for p in d.rglob("*.py") if "__pycache__" not in p.parts)
    return files


def test_no_skill_phrases_in_src() -> None:
    """Fail if any banned skill phrase appears verbatim in src/crpg/**.py."""
    violations: list[tuple[Path, str, int]] = []
    for py in _collect_python_files():
        text = py.read_text(encoding="utf-8")
        for phrase in BANNED_PHRASES:
            if phrase in text:
                # find first occurrence line number for helpful message
                idx = text.find(phrase)
                line_no = text[:idx].count("\n") + 1
                violations.append((py, phrase, line_no))
    if violations:
        msg_lines = [
            "Skill content was copied into Python source. Move it to",
            "skills/<skill>/SKILL.md or references/ and load at runtime.",
            "",
        ]
        for path, phrase, line in violations:
            rel = path.relative_to(ROOT)
            msg_lines.append(f"  {rel}:{line}  banned phrase: {phrase!r}")
        raise AssertionError("\n".join(msg_lines))


def test_skill_files_exist() -> None:
    """Sanity: the skill directory the agent loads from must exist."""
    skill_md = ROOT / "skills" / "director" / "SKILL.md"
    assert skill_md.exists(), (
        f"{skill_md} missing — Director agent cannot boot without it. "
        "Skill content lives in files, not in Python."
    )


def test_src_references_skill_at_runtime() -> None:
    """At least one src/ module must read skill files at runtime.

    This is the positive counterpart of the banned-phrase check: we need
    evidence the agents actually load skill docs (vs. having nothing and
    an empty banned list trivially passing).

    Looks for any of:
      - Path("skills/.../SKILL.md") style literals
      - .read_text() calls against a skills/ path
      - references to "skills/director" / "skills/skeleton" etc.

    This is a coarse check; the Agent SDK integration task tightens it.
    """
    src_files = _collect_python_files()
    loaders_found = False
    for py in src_files:
        text = py.read_text(encoding="utf-8")
        if "skills/" in text or 'skills"' in text or "skills'" in text:
            loaders_found = True
            break
    # During the agent re-architecture this will start passing. For now we
    # only warn: fail clearly so the agent integration task must fix it.
    assert loaders_found, (
        "No src/ module references the skills/ directory. Agents must load "
        "skill content at runtime; current code appears to not wire any skill "
        "files in. Add skill-loading in the Director/Skeleton agent init."
    )
