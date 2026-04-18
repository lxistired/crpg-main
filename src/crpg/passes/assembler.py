"""Pass 4: Prompt Assembler — pure function from Shot → Grok image prompt string."""
from crpg.types import Shot

ANIME_PREAMBLE = (
    "anime illustration style, clean line art, cel-shaded, 2D rendering, "
    "soft bokeh background, high-detail foreground subject, "
)

def assemble_image_prompt(shot: Shot) -> str:
    """Prepend ANIME_PREAMBLE to the Director-generated final_prompt.

    This is deliberately minimal: Director already produced a complete prompt.
    Assembler only adds the anime-style preamble (once per shot).
    """
    return ANIME_PREAMBLE + shot.final_prompt
