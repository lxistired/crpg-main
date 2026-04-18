"""crpg CLI entry point.

Usage:
  crpg generate --brief <file_or_inline> --out <bundle_dir>

--brief may be either a path to a file OR raw text (keywords, a sentence,
 a paragraph). If the arg resolves to an existing file, we read it;
 otherwise we treat it as the brief itself.
"""
import asyncio
from pathlib import Path

import click

from crpg.agent.runner import run_agent
from crpg.config import load_config


@click.group()
@click.version_option()
def main() -> None:
    """crpg — creator CLI for interactive noir fiction with anime images."""


@main.command()
@click.option("--brief", "brief_input", required=True,
              help="Brief as a path to a file OR raw text (keywords / sentence / paragraph).")
@click.option("--out", "out_dir", type=click.Path(file_okay=False, path_type=Path),
              required=True, help="Output directory for the story bundle.")
@click.option("--max-turns", type=int, default=200,
              help="Safety cap on agent iterations (default 200).")
def generate(brief_input: str, out_dir: Path, max_turns: int) -> None:
    """Dispatch the main agent to generate a bundle from a brief."""
    cfg = load_config()
    brief_path = Path(brief_input)
    if brief_path.exists() and brief_path.is_file():
        brief_text = brief_path.read_text(encoding="utf-8")
        click.echo(f"▶ Brief from file: {brief_path}")
    else:
        brief_text = brief_input
        click.echo(f"▶ Brief from inline text: {brief_text[:80]}{'...' if len(brief_text) > 80 else ''}")
    click.echo(f"▶ Agent: {cfg.minimax_model} @ {cfg.minimax_endpoint}")
    click.echo(f"▶ Bundle: {out_dir}")
    result = asyncio.run(run_agent(brief_text, out_dir, cfg=cfg, max_turns=max_turns))
    click.echo(
        f"✓ finished={result.finished}  beats_prose={result.beats_with_prose}  "
        f"beats_shots={result.beats_with_shots}  images={result.images_rendered}  "
        f"turns={result.turns_used}"
    )
    if result.finish_summary:
        click.echo(f"  summary: {result.finish_summary}")
