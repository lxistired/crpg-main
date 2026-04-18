"""crpg CLI entry point."""
import asyncio
from pathlib import Path
import click
from crpg.config import load_config
from crpg.orchestration.pipeline import run_pipeline, PipelineInputs


@click.group()
@click.version_option()
def main() -> None:
    """crpg — creator CLI for interactive noir fiction with anime images."""


@main.command()
@click.option("--brief", type=click.Path(exists=True, dir_okay=False, path_type=Path),
              required=True, help="Path to creator brief (markdown)")
@click.option("--out", "out_dir", type=click.Path(file_okay=False, path_type=Path),
              required=True, help="Output directory for story bundle")
def generate(brief: Path, out_dir: Path) -> None:
    """Generate a story bundle from a brief."""
    cfg = load_config()
    brief_text = brief.read_text(encoding="utf-8")
    inputs = PipelineInputs(brief=brief_text, out_dir=out_dir)
    click.echo(f"▶ Generating to {out_dir} (model={cfg.text_model} @ {cfg.text_provider})")
    result = asyncio.run(run_pipeline(cfg, inputs))
    click.echo(f"✓ Done. {result.shot_count} shots written to {result.bundle_path}")
