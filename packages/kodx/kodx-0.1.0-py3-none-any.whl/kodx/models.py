"""Data models for Kodx configuration."""

from dataclasses import dataclass
from typing import Optional

from pydantic import BaseModel, Field


class DockerConfig(BaseModel):
    """Docker container configuration for Kodx."""

    model_config = {"extra": "forbid"}
    """Docker container configuration for Kodx."""

    image: str = Field(default="python:3.11", description="Docker image to use for the container")

    setup_script: Optional[str] = Field(
        default=None, description="Bash script to execute after container initialization"
    )

    disable_network_after_setup: bool = Field(
        default=False, 
        description="Disconnect container from networks after setup script completes"
    )


@dataclass
class CLIArgs:
    """Collected CLI arguments for Kodx."""

    program_path: Optional[str]
    prompt: Optional[str]
    prompt_file: Optional[str]
    append: bool = False
    json_output: bool = False
    json_output_file: Optional[str] = None
    quiet: bool = False
    log_level: str = "INFO"
    repo_dir: Optional[str] = None
    image: str = "python:3.11"
    setup_script: Optional[str] = None
    export_dir: Optional[str] = None
    cost_limit: Optional[float] = None
    disable_network_after_setup: bool = False
