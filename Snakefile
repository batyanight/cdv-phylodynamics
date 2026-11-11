# cdv-phylodynamics: the CDV analysis on top of the wildphylo pipeline.
#
#   snakemake --configfile config/cdv.yaml --cores 8
#
# Everything pathogen-specific is in config/. The pipeline, its gates and its
# steps live in wildphylo (installed in the env); this file only locates its
# Snakefile and includes it, so builds land in ./builds/ and a build's
# provenance records the wildphylo version it ran with.
import importlib.resources
import subprocess
from pathlib import Path

try:
    import wildphylo
except ImportError as err:
    raise WorkflowError(
        "wildphylo is not installed in this environment; see environment.yml"
    ) from err

# The workflow ships next to the package source in the wildphylo checkout.
# `pip install` from git keeps it under <site-packages>/../ only when
# installed editable, so resolve it from the installed package location first
# and fall back to a sibling checkout for development.
_candidates = [
    Path(wildphylo.__file__).resolve().parents[2] / "workflow" / "Snakefile",
    Path(__file__).resolve().parent.parent / "wildphylo" / "workflow" / "Snakefile",
]
_pipeline = next((p for p in _candidates if p.is_file()), None)
if _pipeline is None:
    raise WorkflowError(
        "cannot find wildphylo's workflow/Snakefile; looked at: "
        + ", ".join(str(p) for p in _candidates)
    )

include: str(_pipeline)


# Snakemake takes the first rule of the *outer* file as the default target, and
# an included file's `rule all` does not count. Point the default at it.
rule cdv:
    default_target: True
    input: rules.all.input
