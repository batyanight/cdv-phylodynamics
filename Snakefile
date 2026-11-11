# cdv-phylodynamics: the CDV analysis on top of the wildphylo pipeline.
#
#   snakemake --configfile config/cdv.yaml --cores 8
#
# Everything pathogen-specific is in config/. The pipeline, its gates and its
# steps live in wildphylo (installed in the env, pinned by tag in
# environment.yml); this file only asks the installed package where its
# Snakefile is and includes it, so builds land in ./builds/ and a build's
# provenance records the wildphylo version it ran with.
import wildphylo

try:
    _pipeline = wildphylo.workflow_path()
except AttributeError as err:
    raise WorkflowError(
        "the installed wildphylo predates 0.3.0, which is the first release "
        "that ships its Snakefile inside the package; bump the pin in "
        "environment.yml"
    ) from err
except FileNotFoundError as err:
    raise WorkflowError(str(err)) from err


include: str(_pipeline)


# Snakemake takes the first rule of the *outer* file as the default target, and
# an included file's `rule all` does not count. Point the default at it.
rule cdv:
    default_target: True
    input: rules.all.input
