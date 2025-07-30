"""CLI entry point for Kodx."""

import asyncio
import os
import subprocess
import sys
import tempfile
from pathlib import Path

import click
import yaml
from llmproc import LLMProgram
from llmproc.cli.log_utils import CliCallbackHandler, get_logger, log_program_info
from llmproc.cli.run import _get_provided_prompt, _resolve_prompt, run_with_prompt

from .defaults import DEFAULT_ASSISTANT_PROGRAM
from .models import CLIArgs, DockerConfig
from .tools import DockerCodexTools


@click.command()
@click.argument("program_path", type=click.Path(exists=True, dir_okay=False), required=False)
@click.option("--prompt", "-p", help="Prompt text. If omitted, read from stdin")
@click.option("--prompt-file", "-f", type=click.Path(exists=True, dir_okay=False), help="Read prompt from file")
@click.option("--append", "-a", is_flag=True, help="Append provided prompt to embedded prompt")
@click.option("--json", "json_output", is_flag=True, help="Output results as JSON")
@click.option("--json-output-file", type=click.Path(), help="Write JSON results to file instead of stdout")
@click.option("--quiet", "-q", is_flag=True, help="Suppress most output")
@click.option(
    "--log-level",
    "-l",
    default="INFO",
    show_default=True,
    help="Set logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)",
)
# Kodx extensions:
@click.option("--repo-dir", help="Local directory to copy into container (empty string for clean container)")
@click.option("--image", default="python:3.11", show_default=True, help="Docker image to use")
@click.option("--setup-script", type=click.Path(exists=True), help="Setup script to execute in container before task")
@click.option("--export-dir", type=click.Path(), help="Host directory to export container changes")
@click.option("--cost-limit", type=float, metavar="USD", help="Stop execution when cost exceeds this limit in USD")
@click.option("--disable-network-after-setup", is_flag=True, help="Disconnect container from networks after setup script")
def main(
    program_path,
    prompt,
    prompt_file,
    append,
    json_output,
    json_output_file,
    quiet,
    log_level,
    repo_dir,
    image,
    setup_script,
    export_dir,
    cost_limit,
    disable_network_after_setup,
):
    """Execute LLM program with container isolation.

    PROGRAM_PATH: Path to LLM program file (YAML/TOML). If omitted, uses built-in assistant.
    """
    args = CLIArgs(
        program_path=program_path,
        prompt=prompt,
        prompt_file=prompt_file,
        append=append,
        json_output=json_output,
        json_output_file=json_output_file,
        quiet=quiet,
        log_level=log_level,
        repo_dir=repo_dir,
        image=image,
        setup_script=setup_script,
        export_dir=export_dir,
        cost_limit=cost_limit,
        disable_network_after_setup=disable_network_after_setup,
    )

    asyncio.run(_async_main(args))


async def _async_main(args: CLIArgs):
    """Async main implementation."""
    logger = get_logger(args.log_level)
    program_path = args.program_path
    prompt = args.prompt
    prompt_file = args.prompt_file
    append = args.append
    json_output = args.json_output
    json_output_file = args.json_output_file
    quiet = args.quiet
    repo_dir = args.repo_dir
    image = args.image
    setup_script = args.setup_script
    export_dir = args.export_dir
    cost_limit = args.cost_limit
    disable_network_after_setup = args.disable_network_after_setup

    try:
        # Early validation: Check if we have a prompt before starting container
        provided_prompt = _get_provided_prompt(prompt, prompt_file, logger)
        
        # 1. Load program (use default if not provided)
        if program_path:
            program = LLMProgram.from_file(Path(program_path))
            logger.info(f"Loaded program from {program_path}")
        else:
            # Use default assistant program
            with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
                f.write(DEFAULT_ASSISTANT_PROGRAM)
                temp_path = f.name

            try:
                program = LLMProgram.from_file(Path(temp_path))
                logger.info("Using default assistant program")
            finally:
                os.unlink(temp_path)

        # Early prompt validation: Check if we have any way to get a prompt
        embedded_prompt = getattr(program, "user_prompt", "")
        if provided_prompt is None and not (embedded_prompt and embedded_prompt.strip()):
            logger.error("No prompt provided via command line, stdin, or configuration")
            sys.exit(1)

        # 2. Extract Docker configuration from program if present
        docker_dict = getattr(program, "docker", {})
        docker_config = DockerConfig(**docker_dict) if docker_dict else DockerConfig()
        
        # Override config with CLI flag if provided
        if disable_network_after_setup:
            docker_config.disable_network_after_setup = True

        # Use CLI image if provided, otherwise use from config
        docker_image = image or docker_config.image

        # Initialize container with configured image using context manager
        async with DockerCodexTools(container_image=docker_image) as docker_tools:
            logger.info(f"Initialized Docker container with image: {docker_image}")

            # 3. Copy local directory if specified
            if repo_dir is not None:  # Only skip if not provided at all
                if repo_dir and not os.path.exists(repo_dir):  # Empty string is valid for clean container
                    logger.error(f"Directory does not exist: {repo_dir}")
                    sys.exit(1)
                if repo_dir:  # Non-empty string = copy directory
                    await _copy_local_directory_to_container(docker_tools, repo_dir, logger)
                    logger.info(f"Copied {repo_dir} to /workspace/repo")
                else:
                    logger.info("Starting with clean container (no repository copied)")
            else:
                # When --repo-dir not provided, default to current directory
                logger.info("No --repo-dir specified, using current directory")
                await _copy_local_directory_to_container(docker_tools, ".", logger)
                logger.info("Copied current directory to /workspace/repo")

            # 4. Handle setup scripts (CLI has precedence over config)
            if setup_script:
                # Execute CLI-provided setup script
                logger.info(f"Executing setup script from CLI: {setup_script}")
                await docker_tools.execute_setup_script(setup_script, disable_network_after=docker_config.disable_network_after_setup)
                logger.info("CLI setup script completed successfully")
            elif docker_config.setup_script:
                # Execute inline setup script from config
                logger.info("Executing setup script from config")
                await docker_tools.execute_setup_script_content(docker_config.setup_script, disable_network_after=docker_config.disable_network_after_setup)
                logger.info("Config setup script completed successfully")

            # 5. Register tools with program
            program.register_tools([docker_tools.feed_chars, docker_tools.create_new_shell])

            # 6. Start process
            process = await program.start()

            # 7. Handle prompt resolution (same logic as llmproc)
            embedded_prompt = getattr(process, "user_prompt", "")
            final_prompt = _resolve_prompt(provided_prompt, embedded_prompt, append, logger)

            # 8. Set up callbacks and run
            callback_handler = CliCallbackHandler(logger, cost_limit=cost_limit)
            process.add_callback(callback_handler)

            log_program_info(process, final_prompt, logger)
            run_result = await run_with_prompt(
                process, final_prompt, "kodx", logger, callback_handler, quiet, json_output
            )

            # 9. Export container changes if requested
            if export_dir:
                await _export_container_to_host(docker_tools, export_dir, logger)

            # Handle JSON output (same as llmproc but with file option)
            if json_output or json_output_file:
                import json

                output = {
                    "api_calls": run_result.api_calls,
                    "last_message": process.get_last_message(),
                    "stderr": process.get_stderr_log(),
                }

                # Add cost information if available
                if hasattr(run_result, "usd_cost"):
                    output["usd_cost"] = run_result.usd_cost

                # Add stop reason if available
                if hasattr(run_result, "stop_reason"):
                    output["stop_reason"] = run_result.stop_reason

                # Add cost limit if it was specified and stop reason is cost-related
                if (
                    cost_limit is not None
                    and hasattr(run_result, "stop_reason")
                    and run_result.stop_reason == "cost_limit_exceeded"
                ):
                    output["cost_limit"] = cost_limit

                json_str = json.dumps(output)

                if json_output_file:
                    # Write to file
                    with open(json_output_file, "w") as f:
                        f.write(json_str)
                    logger.info(f"JSON output written to {json_output_file}")
                else:
                    # Write to stdout (original behavior)
                    click.echo(json_str)

            await process.aclose()

    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)


def _docker_cp(src: str, dest: str, logger, check: bool = True) -> subprocess.CompletedProcess:
    """Run a ``docker cp`` command with consistent error handling."""
    cmd = ["docker", "cp", src, dest]
    try:
        return subprocess.run(cmd, check=check, capture_output=True)
    except subprocess.CalledProcessError as e:
        if isinstance(e.stderr, bytes):
            stderr = e.stderr.decode()
        else:
            stderr = e.stderr or ""
        logger.error(f"docker cp failed: {stderr}")
        raise RuntimeError(f"docker cp failed: {stderr}") from e


async def _copy_local_directory_to_container(docker_tools, local_dir, logger):
    """Copy local directory to container workspace."""
    # Create workspace directory in container
    await docker_tools.feed_chars("mkdir -p /workspace/repo")

    # Copy files using docker cp
    container_id = docker_tools.container_id
    if not container_id:
        raise RuntimeError("Container not initialized")

    # Copy all files from local directory
    try:
        _docker_cp(f"{local_dir}/.", f"{container_id}:/workspace/repo/", logger)
        logger.info(f"Successfully copied {local_dir} to container")

        # Set working directory to repo
        await docker_tools.feed_chars("cd /workspace/repo")

    except RuntimeError as e:
        raise RuntimeError(f"Failed to copy directory to container: {e}")


async def _export_container_to_host(docker_tools, export_dir, logger):
    """Export container workspace to host directory."""
    container_id = docker_tools.container_id
    if not container_id:
        raise RuntimeError("Container not initialized")

    # Create export directory if it doesn't exist
    os.makedirs(export_dir, exist_ok=True)

    # Try to copy /workspace/repo first, then fallback to /workspace
    result = _docker_cp(f"{container_id}:/workspace/repo/.", f"{export_dir}/", logger, check=False)
    if result.returncode == 0:
        logger.info(f"Successfully exported /workspace/repo to {export_dir}")
        return

    try:
        _docker_cp(f"{container_id}:/workspace/.", f"{export_dir}/", logger)
        logger.info(f"Successfully exported /workspace to {export_dir}")
    except RuntimeError as e:
        cause = e.__cause__
        stderr = cause.stderr.decode() if getattr(cause, "stderr", None) else ""
        if "No such file or directory" in stderr:
            logger.warning("No files to export - container workspace is empty")
        else:
            raise RuntimeError(f"Failed to export container changes: {e}")


if __name__ == "__main__":
    main()
