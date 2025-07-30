import os
import select
import subprocess
import tempfile

import click
from click.core import Context as ClickContext
from gable.api.client import GableAPIClient
from gable.cli.helpers.npm import get_sca_cmd, prepare_npm_environment
from gable.cli.options import global_options
from loguru import logger


@click.group(hidden=True)
def demo():
    """Demo commands"""


@demo.command(
    # Disable help, we re-add it in global_options()
    add_help_option=False,
)
@global_options(add_endpoint_options=False)
@click.option(
    "--project-root",
    help="The root directory of the Java project that will be analyzed.",
    type=click.Path(exists=True),
    required=True,
)
@click.option(
    "--build-command",
    help="The build command used to build the Java project (e.g. mvn clean install).",
    type=str,
    required=False,
)
@click.option(
    "--java-version",
    help="The version of Java used to build the project.",
    type=str,
    default="17",
)
@click.option(
    "--llm-extraction/--no-llm-extraction",
    help="Use LLM for feature extraction.",
    type=bool,
    default=False,
    is_flag=True,
)
@click.option(
    "--dataflow-config-file",
    type=click.Path(exists=True),
    help="The path to the dataflow config JSON file.",
    required=False,
)
@click.option(
    "--schema-depth",
    help="The max depth of the schemas to be extracted.",
    type=int,
    required=False,
)
@click.pass_context
def java_dataflow(
    ctx: ClickContext,
    project_root: str,
    build_command: str,
    java_version: str,
    llm_extraction: bool,
    dataflow_config_file: str,
    schema_depth: int,
):
    """Prints connections between sources and sinks in Java code"""
    if os.getenv("GABLE_CLI_ISOLATION", "false").lower() == "true":
        print("GABLE_CLI_ISOLATION is true, skipping NPM authentication")
    else:
        client: GableAPIClient = ctx.obj.client
        prepare_npm_environment(client)
    args = (
        [
            "java-dataflow",
            project_root,
            "--java-version",
            java_version,
        ]
        + (["--build-command", build_command] if build_command else [])
        + (
            ["--dataflow-config-file", dataflow_config_file]
            if dataflow_config_file
            else []
        )
        + (["--schema-depth", str(schema_depth)] if schema_depth else [])
    )

    stdout_output = []

    process = subprocess.Popen(
        get_sca_cmd(None, args),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=-1,  # Use system default buffering
    )

    # Read both streams concurrently.
    while True:
        reads = []
        if process.stdout:
            reads.append(process.stdout)
        if process.stderr:
            reads.append(process.stderr)

        if not reads:
            break

        # Wait until at least one stream has data
        ready, _, _ = select.select(reads, [], [])

        for stream in ready:
            line = stream.readline()
            if not line:
                continue
            if stream == process.stdout:
                stdout_output.append(line)
            elif stream == process.stderr:
                logger.debug(line.rstrip("\n"))

        if process.poll() is not None:
            break

    # Drain any remaining stdout (if any)
    if process.stdout:
        remaining = process.stdout.read()
        if remaining:
            stdout_output.append(remaining)

    process.wait()
    final_stdout = "".join(stdout_output)

    print(final_stdout, end="")

    if process.returncode != 0:
        raise click.ClickException(f"Error running Gable SCA")

    if llm_extraction:
        run_llm_feature_extraction(final_stdout, project_root)
    else:
        print("Skipping LLM feature extraction")
        return


def run_llm_feature_extraction(sca_results: str, project_root: str):
    with tempfile.NamedTemporaryFile(
        mode="w", delete=False, suffix=".json", encoding="utf-8"
    ) as f:
        f.write(sca_results)
    feature_extraction_cmd = [
        "./venv/bin/python",
        "-m",
        "main",
        "--repo",
        os.path.abspath(project_root),
        "--sca",
        f.name,
    ]
    feature_extraction_result = subprocess.run(
        feature_extraction_cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        cwd=os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "../../../../../sca-pl-mve/",
        ),
    )
    logger.debug(
        f"Calling feature extraction subprocess: {' '.join(feature_extraction_cmd)}"
    )
    if feature_extraction_result.returncode != 0:
        logger.debug(feature_extraction_result.stdout)
        logger.debug(feature_extraction_result.stderr)
        raise click.ClickException(
            f"Error running Gable feature extraction: {feature_extraction_result.stderr}"
        )
    print(feature_extraction_result.stdout)
