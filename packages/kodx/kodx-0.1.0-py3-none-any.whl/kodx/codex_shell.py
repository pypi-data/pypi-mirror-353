"""CodexShell - PTY server shell for code execution environments"""

import asyncio
import json
import logging
import os

logger = logging.getLogger(__name__)


class BashNotFoundError(Exception):
    """Raised when bash is not found in container."""

    pass


class CodexShell:
    """Shell with PTY server for enhanced program interaction.

    Features:
    - stdin: Clean input via HTTP (no echo)
    - stdout/stderr: PTY-enabled (shows REPL output)
    - Ctrl+C support via feed_chars() method
    - Network isolation resilient
    - Best for code execution environments
    """

    def __init__(self, container, shell_pid: int):
        self.container = container
        self.shell_pid = shell_pid
        self._server_installed = False

    @classmethod
    async def create(cls, container) -> "CodexShell":
        """Create a new CodexShell session with PTY server"""
        # Check prerequisites - fail fast with clear error messages
        prerequisites = [
            ("which bash", "bash"),
            ("which python3", "python3"),
            ("which pip3", "pip3"),
            ("which curl", "curl"),
        ]

        for cmd, name in prerequisites:
            result = container.exec_run(cmd)
            if result.exit_code != 0:
                raise BashNotFoundError(
                    f"{name} not found in container. "
                    f"Please use a Docker image with Python 3, pip, bash, and curl installed. "
                    f"Recommended: python:3.11 or python:3.12. "
                    f"For custom images, see documentation on image requirements."
                )

        # Install FastAPI and uvicorn
        logger.info("Installing PTY server dependencies...")
        result = container.exec_run("pip3 install -q fastapi uvicorn")
        if result.exit_code != 0:
            raise Exception(f"Failed to install dependencies: {result.output.decode()}")

        # Deploy PTY server code using docker cp for reliability
        import subprocess
        import tempfile

        server_code = cls._get_pty_server_code()

        # Write the server code to a temporary file on the host
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as tmp:
            tmp.write(server_code)
            tmp_path = tmp.name

        try:
            # Copy the file into the container
            subprocess.run(
                [
                    "docker",
                    "cp",
                    tmp_path,
                    f"{container.id}:/root/pty_server.py",
                ],
                check=True,
                capture_output=True,
            )
        finally:
            os.unlink(tmp_path)

        # Start PTY server in background
        container.exec_run("python3 /root/pty_server.py > /dev/null 2>&1 &", detach=True)

        # Wait for server to start and be ready
        await asyncio.sleep(2.0)

        # Test server health with curl
        result = container.exec_run("curl -s http://localhost:1384/healthcheck")
        if result.exit_code != 0 or b"ok" not in result.output:
            raise Exception(f"PTY server health check failed: {result.output}")

        # Create bash session via PTY server
        open_req = {"cmd": ["/bin/bash"], "env": {"PS1": "\\w $ ", "TERM": "xterm", "PYTHONUNBUFFERED": "1"}}

        result = container.exec_run(
            [
                "curl",
                "-s",
                "-X",
                "POST",
                "http://localhost:1384/open",
                "-H",
                "Content-Type: application/json",
                "-d",
                json.dumps(open_req),
            ]
        )

        if result.exit_code != 0:
            raise Exception(f"Failed to create bash session: {result.output}")

        try:
            shell_pid = int(result.output.strip())
        except ValueError as e:
            raise Exception(f"Failed to parse shell PID from response: {result.output}, error: {e}")

        # Create shell instance
        shell = cls(container, shell_pid)
        shell._server_installed = True

        return shell

    async def run(self, chars: str = None, timeout: float = 1.0) -> str:
        """Send characters and read output via PTY server"""
        # Send characters if provided
        if chars is not None:
            # Escape the input properly for shell injection safety
            escaped_chars = chars.replace("'", "'\"'\"'")
            result = self.container.exec_run(
                [
                    "bash",
                    "-c",
                    f"printf '%s\\n' '{escaped_chars}' | curl -s -X POST http://localhost:1384/write/{self.shell_pid} --data-binary @-",
                ]
            )

            if result.exit_code != 0:
                logger.warning("Write failed: %s", result.output)

        # Read output multiple times to get all available output
        total_output = ""
        for i in range(3):  # Try multiple times
            await asyncio.sleep(0.3)

            result = self.container.exec_run(
                ["curl", "-s", "-X", "POST", f"http://localhost:1384/read/{self.shell_pid}", "-d", "8192"]
            )

            if result.exit_code == 0:
                chunk = result.output.decode(errors="replace")
                if chunk:
                    total_output += chunk
                elif i > 0:  # If no more output after first read, we're probably done
                    break

        return total_output

    async def close(self) -> None:
        """Close the shell session"""
        # Kill the bash process via PTY server
        if self._server_installed:
            try:
                self.container.exec_run(["curl", "-s", "-X", "POST", f"http://localhost:1384/kill/{self.shell_pid}"])
            except Exception:
                pass

    @staticmethod
    def _get_pty_server_code() -> str:
        """Return the PTY server code"""
        return '''"""PTY Server for CodexShell - runs inside container to provide PTY functionality"""
import asyncio
import logging
import os
import pty
import subprocess
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.responses import JSONResponse
from pydantic import BaseModel

logger = logging.getLogger(__name__)

HOST = "0.0.0.0"
PORT = 1384


class OpenRequest(BaseModel):
    """Request to open a new process."""
    cmd: list[str]
    env: dict[str, str]
    cwd: str | None = None


class RawResponse(Response):
    media_type = "application/octet-stream"


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.pipes = {}
    try:
        yield
    finally:
        for pipe in app.state.pipes.values():
            try:
                os.close(pipe)
            except Exception:
                pass


app = FastAPI(lifespan=lifespan)


def get_env(request: OpenRequest) -> dict[str, str]:
    # Start with a copy of the current environment variables
    env = os.environ.copy()

    # Update with specific defaults and any variables from the request
    env.update({
        "TERM": "xterm",
        "COLUMNS": "80",
        "LINES": "24",
        **request.env,
    })

    return env


@app.get("/healthcheck")
async def healthcheck() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/open")
async def open(request: OpenRequest) -> int:
    """Start a new process and return the PID."""
    master, slave = pty.openpty()
    os.set_blocking(master, False)

    if request.cwd and not os.path.isabs(request.cwd):
        raise HTTPException(
            status_code=400, detail=f"CWD must be an absolute path. Received: '{request.cwd}'"
        )

    env = get_env(request)

    try:
        # Start the process with PTY
        process = subprocess.Popen(
            request.cmd,
            stdin=slave,
            stdout=slave,
            stderr=slave,
            start_new_session=True,
            text=False,
            env=env,
            cwd=request.cwd,
        )
        os.close(slave)
    except Exception as e:
        logger.exception("Failed to open process")
        try:
            os.close(master)
            os.close(slave)
        except Exception:
            pass
        raise HTTPException(status_code=400, detail=f"Failed to create process: {e}") from e

    app.state.pipes[process.pid] = master
    return process.pid


@app.post("/read/{pid}")
async def read(pid: int, request: Request) -> RawResponse:
    pipe = app.state.pipes.get(pid)
    if pipe is None:
        raise HTTPException(status_code=404, detail=f"Process not found: {pid}")

    try:
        size = int(await request.body())
        data = bytearray()

        # Read available data up to size
        deadline = asyncio.get_event_loop().time() + 1.0  # Max 1 second per read

        while size > 0 and asyncio.get_event_loop().time() < deadline:
            try:
                chunk = os.read(pipe, min(size, 4096))
                if chunk:
                    size -= len(chunk)
                    data.extend(chunk)
                else:
                    break
            except BlockingIOError:
                await asyncio.sleep(0.01)

        return RawResponse(content=bytes(data))
    except ValueError as e:
        logger.exception("Failed to parse size")
        raise HTTPException(status_code=400, detail=f"Failed to parse size: {e}") from e


@app.post("/write/{pid}")
async def write(pid: int, request: Request) -> int:
    pipe = app.state.pipes.get(pid)
    if pipe is None:
        raise HTTPException(status_code=404, detail=f"Process not found: {pid}")

    try:
        data = await request.body()
        size = os.write(pipe, data)
        return size
    except Exception as e:
        logger.exception("Failed to write to pipe")
        raise HTTPException(status_code=409, detail=f"Failed to write: {e}") from e


@app.post("/kill/{pid}")
async def kill(pid: int) -> None:
    pipe = app.state.pipes.pop(pid, None)
    if pipe is None:
        raise HTTPException(status_code=404, detail=f"Process not found: {pid}")

    try:
        os.close(pipe)
        # Also try to kill the process
        try:
            os.kill(pid, 15)  # SIGTERM
        except ProcessLookupError:
            pass
    except Exception as e:
        logger.exception("Failed to close pipe")
        raise HTTPException(status_code=409, detail=f"Failed to close: {e}") from e


@app.post("/write_file/{file_path:path}")
async def write_file(file_path: str, request: Request) -> dict:
    """Write content to a file."""
    try:
        content = await request.body()

        # Ensure parent directory exists
        import pathlib
        pathlib.Path(file_path).parent.mkdir(parents=True, exist_ok=True)

        # Write file
        with open(file_path, 'wb') as f:
            f.write(content)

        return {"status": "success", "path": file_path, "size": len(content)}
    except Exception as e:
        logger.exception("Failed to write file")
        raise HTTPException(status_code=500, detail=f"Failed to write file: {e}") from e


@app.get("/read_file/{file_path:path}")
async def read_file(file_path: str) -> Response:
    """Read content from a file."""
    try:
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail=f"File not found: {file_path}")

        with open(file_path, 'rb') as f:
            content = f.read()

        return Response(content=content, media_type="application/octet-stream")
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Failed to read file")
        raise HTTPException(status_code=500, detail=f"Failed to read file: {e}") from e


def main() -> None:
    uvicorn.run(app, host=HOST, port=PORT, log_level="error")


if __name__ == "__main__":
    main()'''
