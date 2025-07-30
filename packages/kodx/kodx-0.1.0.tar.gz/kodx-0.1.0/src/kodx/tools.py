"""Docker container tools for Kodx."""

import logging
import os

import docker
from llmproc.tools.function_tools import register_tool

from .codex_shell import CodexShell

logger = logging.getLogger(__name__)


class SetupError(Exception):
    """Raised when setup script execution fails."""

    pass


class DockerCodexTools:
    """Container tools using CodexShell for enhanced shell interaction."""

    def __init__(self, container_image: str = "python:3.11", container_name: str = None):
        self.container_image = container_image
        self.container_name = container_name or f"kodx-{id(self)}"
        self.container = None
        self.shell = None
        self.docker_client = docker.from_env()

    async def __aenter__(self):
        """Initialize container when entering async context."""
        await self.initialize()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        """Ensure cleanup when exiting async context."""
        await self.cleanup()

    async def initialize(self):
        """Initialize Docker container and CodexShell."""
        try:
            # Create and start container
            self.container = self.docker_client.containers.run(
                self.container_image,
                command="sleep infinity",
                detach=True,
                remove=True,
                name=self.container_name,
                network_mode="bridge",
            )

            # Initialize CodexShell
            self.shell = await CodexShell.create(self.container)

            # Set up basic environment
            await self.shell.run("cd /workspace || mkdir -p /workspace && cd /workspace")
        except Exception:
            # Clean up if initialization fails
            await self.cleanup()
            raise

    @register_tool(description="Send characters/commands to the shell")
    async def feed_chars(self, chars: str) -> str:
        r"""Send characters or commands to the shell.

        Args:
            chars: Characters to send (commands, Ctrl+C as \\x03, etc.)

        Returns:
            Shell output from the command
        """
        if not self.shell:
            return "Error: Container not initialized"
        return await self.shell.run(chars)

    @register_tool(description="Create a new shell session")
    async def create_new_shell(self) -> str:
        """Create a fresh shell session, resetting the environment.

        Returns:
            Status message about the new shell creation
        """
        if not self.container:
            return "Error: Container not initialized"

        try:
            # Close current shell if it exists
            if self.shell:
                await self.shell.close()

            # Create new shell session
            self.shell = await CodexShell.create(self.container)

            # Set up basic environment again
            await self.shell.run("cd /workspace || mkdir -p /workspace && cd /workspace")

            return "New shell session created successfully. Working directory: /workspace"
        except Exception as e:
            return f"Error creating new shell: {e}"

    async def execute_setup_script(self, setup_path: str, disable_network_after: bool = False) -> str:
        """Execute setup script in container with clean isolation.

        Args:
            setup_path: Path to setup script on host
            disable_network_after: Disconnect container from networks after setup

        Returns:
            Setup script output

        Raises:
            SetupError: If setup script fails
        """
        if not self.shell:
            raise SetupError("Container not initialized")

        # 1. Validate setup file exists on host
        if not os.path.exists(setup_path):
            raise SetupError(f"Setup script not found: {setup_path}")

        # 2. Read setup script content
        with open(setup_path, encoding="utf-8") as f:
            script_content = f.read()

        # Execute the script content
        return await self.execute_setup_script_content(script_content, disable_network_after)

    async def execute_setup_script_content(self, script_content: str, disable_network_after: bool = False) -> str:
        """Execute setup script content in container with clean isolation.

        Args:
            script_content: Content of the setup script
            disable_network_after: Disconnect container from networks after setup

        Returns:
            Setup script output

        Raises:
            SetupError: If setup script fails
        """
        if not self.shell:
            raise SetupError("Container not initialized")

        # 1. Copy script to /tmp using docker cp (simpler and more reliable)
        import subprocess
        import tempfile

        # Create a temporary file on host
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as temp_file:
            temp_file.write(script_content)
            temp_file_path = temp_file.name

        try:
            # Copy temp file directly to container /tmp/setup.sh
            copy_cmd = ["docker", "cp", temp_file_path, f"{self.container.id}:/tmp/setup.sh"]
            subprocess.run(copy_cmd, check=True, capture_output=True)

        except subprocess.CalledProcessError as e:
            raise SetupError(f"Failed to copy setup script to container: {e}")
        finally:
            # Clean up temp file
            os.unlink(temp_file_path)

        # 2. Make executable and execute from /workspace
        setup_command = """chmod +x /tmp/setup.sh
cd /workspace && bash /tmp/setup.sh"""

        # 3. Execute setup script
        result = await self.shell.run(setup_command)

        # 4. Check for failure and fail fast
        if self._setup_failed(result):
            raise SetupError(f"Setup script failed: {result}")

        # 5. Disconnect network if requested and setup succeeded
        if disable_network_after:
            await self.disconnect_network()

        return result

    def _setup_failed(self, output: str) -> bool:
        """Detect if setup script failed based on output."""
        if not output:
            return False

        output_lower = output.lower()
        failure_indicators = [
            "command not found",
            "permission denied",
            "no such file",
            "error:",
            "failed",
            "cannot",
            "bash: line",  # Bash syntax errors
            "syntax error",
        ]
        return any(indicator in output_lower for indicator in failure_indicators)

    async def disconnect_network(self) -> None:
        """Disconnect container from all networks after setup is complete."""
        if not self.container:
            return

        try:
            # Reload container to get current network state
            self.container.reload()

            # Disconnect from all networks
            for net in self.container.attrs["NetworkSettings"]["Networks"]:
                network = self.docker_client.networks.get(net)
                network.disconnect(self.container)

        except Exception as e:  # noqa: BLE001
            # Fail fast if network disconnection fails
            logger.exception("Failed to disconnect networks: %s", e)
            raise SetupError(f"Network disconnection failed: {e}") from e

    def copy_text_to_container(self, text: str, dest_path: str) -> None:
        """Copy the given text to a file inside the container."""
        if not self.container:
            raise RuntimeError("Container not initialized")

        import subprocess
        import tempfile

        with tempfile.NamedTemporaryFile(mode="w", delete=False) as tmp:
            tmp.write(text)
            tmp_path = tmp.name

        try:
            subprocess.run(
                [
                    "docker",
                    "cp",
                    tmp_path,
                    f"{self.container.id}:{dest_path}",
                ],
                check=True,
                capture_output=True,
            )
        finally:
            os.unlink(tmp_path)

    @property
    def container_id(self) -> str:
        """Get the container ID for docker cp operations."""
        return self.container.id if self.container else None

    async def cleanup(self):
        """Clean up container and shell resources."""
        if self.shell:
            try:
                await self.shell.close()
            except Exception:
                pass  # Ignore cleanup errors
        if self.container:
            try:
                self.container.stop()
                self.container.remove()
            except Exception:
                pass  # Ignore cleanup errors
