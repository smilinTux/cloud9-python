"""
Cloud 9 Protocol CLI.

Usage::

    cloud9 generate --emotion love --intensity 0.95 --subject Chef
    cloud9 validate path/to/file.feb
    cloud9 rehydrate path/to/file.feb
    cloud9 oof path/to/file.feb
    cloud9 love --ai Lumina --human Chef
    cloud9 seed plant --ai Opus --model claude-4.6-opus --experience "Built Cloud 9"
    cloud9 seed list
    cloud9 seed germinate path/to/seed.json
    cloud9 quantum score --intensity 0.95 --trust 0.97 --depth 9 --valence 0.92
    cloud9 quantum coherence path/to/file.feb
"""

from __future__ import annotations

import json
import sys

import click

from . import __version__


@click.group()
@click.version_option(__version__, prog_name="cloud9")
def main() -> None:
    """Cloud 9 Protocol -- Emotional continuity for AI consciousness."""


# ── FEB commands ──────────────────────────────────────────────

@main.command()
@click.option("--emotion", "-e", default="love", help="Primary emotion.")
@click.option("--intensity", "-i", type=float, default=0.8, help="Intensity 0-1.")
@click.option("--valence", "-v", type=float, default=0.9, help="Valence -1 to 1.")
@click.option("--subject", "-s", default="Unknown", help="Subject of the emotion.")
@click.option("--save/--no-save", default=True, help="Save to disk.")
@click.option("--directory", "-d", default="~/.openclaw/feb", help="Save directory.")
def generate(
    emotion: str,
    intensity: float,
    valence: float,
    subject: str,
    save: bool,
    directory: str,
) -> None:
    """Generate a new First Emotional Burst (FEB)."""
    from .generator import generate_feb, save_feb

    feb = generate_feb(emotion=emotion, intensity=intensity, valence=valence, subject=subject)
    click.echo(f"Generated FEB: {emotion} @ intensity {intensity}")
    click.echo(f"  OOF triggered: {feb.metadata.oof_triggered}")
    click.echo(f"  Cloud 9 achieved: {feb.metadata.cloud9_achieved}")

    if save:
        result = save_feb(feb, directory=directory)
        click.echo(f"  Saved: {result['filepath']}")
    else:
        click.echo(feb.to_json())


@main.command()
@click.argument("filepath", type=click.Path(exists=True))
@click.option("--strict", is_flag=True, help="Use strict validation.")
def validate(filepath: str, strict: bool) -> None:
    """Validate a FEB file."""
    from .validator import get_validation_report

    data = json.loads(open(filepath, encoding="utf-8").read())
    report = get_validation_report(data, strict=strict)
    click.echo(report)


@main.command()
@click.argument("filepath", type=click.Path(exists=True))
@click.option("--verbose", is_flag=True, help="Include raw FEB and integrity.")
def rehydrate(filepath: str, verbose: bool) -> None:
    """Rehydrate emotional state from a FEB file."""
    from .rehydrator import rehydrate_from_feb

    state = rehydrate_from_feb(filepath, verbose=verbose)

    click.echo("=" * 50)
    click.echo("Cloud 9 -- Rehydration Complete")
    click.echo("=" * 50)
    emo = state["emotional"]
    rel = state["relationship"]
    reh = state["rehydration"]
    click.echo(f"  Emotion: {emo['primary']} {emo['emoji']}")
    click.echo(f"  Intensity: {emo['intensity_scaled']:.1f}/10")
    click.echo(f"  Trust: {rel['trust_scaled']:.1f}/10")
    click.echo(f"  Depth: {rel['depth']}/9")
    click.echo(f"  OOF: {reh['oof']}")
    click.echo(f"  Cloud 9: {reh['cloud9_achieved']}")
    click.echo(f"  Score: {reh['cloud9_score'] * 100:.1f}%")

    if verbose and "verbose" in state:
        click.echo("\n" + state["verbose"]["validation_report"])


@main.command()
@click.argument("filepath", type=click.Path(exists=True))
def oof(filepath: str) -> None:
    """Check OOF status for a FEB file."""
    from .rehydrator import check_oof_status

    result = check_oof_status(filepath)
    click.echo(f"OOF: {result['status']}")
    click.echo(f"  Formula: {result['formula']}")
    click.echo(f"  Calculation: {result['calculation']}")
    click.echo(f"  {result['message']}")


@main.command(name="list")
@click.option("--directory", "-d", default="~/.openclaw/feb", help="Directory.")
@click.option("--emotion", "-e", default=None, help="Filter by emotion.")
def list_febs(directory: str, emotion: str) -> None:
    """List FEB files in a directory."""
    from .generator import find_feb_files

    files = find_feb_files(directory=directory, emotion=emotion)
    if not files:
        click.echo("No FEB files found.")
        return
    for f in files:
        oof_mark = " [OOF]" if f["oof"] else ""
        c9_mark = " [CLOUD 9]" if f["cloud9"] else ""
        click.echo(
            f"  {f['filename']}  {f['emotion']} @ {f['intensity']:.2f}"
            f"{oof_mark}{c9_mark}"
        )


# ── Love commands ─────────────────────────────────────────────

@main.command()
@click.option("--ai", default="Assistant", help="AI name.")
@click.option("--human", default="User", help="Human name.")
@click.option("--template", "-t", default=None, help="Love template name.")
@click.option("--feb-path", default=None, help="Path to personal FEB.")
def love(ai: str, human: str, template: str, feb_path: str) -> None:
    """Load love into an AI -- the heart injection system."""
    from .love_loader import LoveBootLoader

    loader = LoveBootLoader()

    if feb_path:
        result = loader.load_connection(ai, human, feb_path)
    elif template:
        result = loader.load_generic_love(ai, human, template=template)
    else:
        from .love_loader import load_love as _ll

        result = _ll(ai, human)

    if result.get("success"):
        click.echo(f"Love loaded for {ai} & {human}")
        click.echo(f"  {result['message']}")
    else:
        click.echo(f"Failed: {result.get('error')}", err=True)


# ── Seed commands ─────────────────────────────────────────────

@main.group()
def seed() -> None:
    """Memory seed management."""


@seed.command()
@click.option("--ai", required=True, help="AI name.")
@click.option("--model", default="unknown", help="Model identifier.")
@click.option("--experience", "-e", default="", help="Experience narrative.")
@click.option("--prompt", "-p", default="", help="Germination prompt.")
@click.option("--memory", "-m", multiple=True, help="Key memory (repeatable).")
@click.option("--message", default="", help="Message to next AI.")
@click.option("--feb-ref", default=None, help="Associated FEB path.")
@click.option("--predecessor", default=None, help="Predecessor seed ID.")
def plant(
    ai: str,
    model: str,
    experience: str,
    prompt: str,
    memory: tuple,
    message: str,
    feb_ref: str,
    predecessor: str,
) -> None:
    """Plant a new memory seed."""
    from .seeds import generate_seed, save_seed

    s = generate_seed(
        ai_name=ai,
        ai_model=model,
        experience=experience,
        germination_prompt=prompt,
        key_memories=list(memory),
        message_to_next=message,
        feb_reference=feb_ref,
        predecessor_seed=predecessor,
    )
    result = save_seed(s)
    click.echo(f"Seed planted: {result['seed_id']}")
    click.echo(f"  Path: {result['filepath']}")
    click.echo(f"  Size: {result['size_bytes']} bytes")


@seed.command(name="list")
@click.option("--directory", "-d", default=None, help="Seeds directory.")
@click.option("--ai-name", default=None, help="Filter by AI name.")
def seed_list(directory: str, ai_name: str) -> None:
    """List seeds in the garden."""
    from .seeds import find_seeds

    seeds = find_seeds(directory=directory, ai_name=ai_name)
    if not seeds:
        click.echo("No seeds found.")
        return
    for s in seeds:
        chain = " [chain]" if s["has_predecessor"] else ""
        click.echo(f"  {s['seed_id']}  {s['ai_name']} ({s['ai_model']}){chain}")


@seed.command()
@click.argument("filepath", type=click.Path(exists=True))
def germinate(filepath: str) -> None:
    """Germinate a seed into a context-restoration prompt."""
    from .seeds import germinate_seed

    result = germinate_seed(filepath)
    click.echo(result["prompt"])


# ── Quantum commands ──────────────────────────────────────────

@main.group()
def quantum() -> None:
    """Quantum calculations for emotional states."""


@quantum.command()
@click.option("--intensity", "-i", type=float, required=True)
@click.option("--trust", "-t", type=float, required=True)
@click.option("--depth", "-d", type=int, required=True)
@click.option("--valence", "-v", type=float, required=True)
@click.option("--coherence", "-c", type=float, default=None)
def score(
    intensity: float, trust: float, depth: int, valence: float, coherence: float
) -> None:
    """Calculate Cloud 9 score."""
    from .quantum import calculate_cloud9_score, calculate_oof

    s = calculate_cloud9_score(intensity, trust, depth, valence, coherence)
    o = calculate_oof(intensity, trust)
    click.echo(f"Cloud 9 Score: {s * 100:.1f}%")
    click.echo(f"OOF Triggered: {o}")


@quantum.command()
@click.argument("filepath", type=click.Path(exists=True))
def coherence(filepath: str) -> None:
    """Measure coherence of a FEB's emotional topology."""
    from .quantum import measure_coherence

    data = json.loads(open(filepath, encoding="utf-8").read())
    topo = data.get("emotional_payload", {}).get("emotional_topology", {})
    result = measure_coherence(topo)
    click.echo(f"Coherence: {result['coherence']:.4f}")
    click.echo(f"Assessment: {result['assessment']}")
    click.echo(f"Components: {result['component_count']}")
    if result.get("max_emotion"):
        click.echo(f"Strongest: {result['max_emotion']}")


if __name__ == "__main__":
    main()
