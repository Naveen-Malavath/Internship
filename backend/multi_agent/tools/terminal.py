"""Terminal execution tool for running commands"""

import asyncio
import logging
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, Optional

from .base import Tool, ToolParameter

logger = logging.getLogger(__name__)


class TerminalTool(Tool):
    """Tool for executing terminal commands"""

    name = "terminal"
    description = """Execute terminal commands to install dependencies, run builds, start servers.
    
Use this tool to:
- Install dependencies: npm install, pip install
- Run dev servers: npm run dev, uvicorn main:app
- Execute any shell command
"""
    parameters = [
        ToolParameter(
            name="command",
            type="string",
            description="Command to execute",
            required=True,
        ),
        ToolParameter(
            name="cwd",
            type="string",
            description="Working directory for command execution",
            required=False,
        ),
        ToolParameter(
            name="timeout",
            type="number",
            description="Timeout in seconds (default: 120)",
            required=False,
        ),
        ToolParameter(
            name="background",
            type="boolean",
            description="Run command in background without waiting",
            required=False,
        ),
    ]

    def __init__(self, workspace_path: Optional[Path] = None, event_callback=None):
        """Initialize terminal tool"""
        self.workspace_path = workspace_path or Path.cwd()
        self.event_callback = event_callback
        logger.info(f"[TERMINAL] Initialized with workspace: {self.workspace_path}")

    async def execute(self, **kwargs) -> Dict[str, Any]:
        """Execute terminal command"""
        command = kwargs.get("command")
        if not command:
            return {
                "success": False,
                "error": "Missing required parameter: command",
                "stdout": "",
                "stderr": "",
                "exit_code": 1,
            }

        cwd = kwargs.get("cwd", str(self.workspace_path))
        timeout = kwargs.get("timeout", 120)
        background = kwargs.get("background", False)
        
        # Auto-detect dev server commands
        is_dev_server = any(keyword in command.lower() for keyword in [
            "npm run dev", "npm start", "uvicorn", "flask run"
        ])
        if is_dev_server:
            timeout = max(timeout, 300)  # 5 min for dev servers
            background = True  # Dev servers should run in background

        logger.info(f"[TERMINAL] Executing: {command} in {cwd}")

        try:
            return await self._run_command(command, cwd, timeout, background)
        except Exception as e:
            logger.error(f"[TERMINAL] Error: {e}")
            return {
                "success": False,
                "error": str(e),
                "stdout": "",
                "stderr": str(e),
                "exit_code": 1,
                "command": command,
                "cwd": cwd
            }

    async def _run_command(
        self, command: str, cwd: str, timeout: int, background: bool
    ) -> Dict[str, Any]:
        """Run command and capture output"""
        
        # Resolve cwd path
        cwd_path = Path(cwd) if cwd else self.workspace_path
        if not cwd_path.is_absolute():
            cwd_path = self.workspace_path / cwd_path
        cwd_str = str(cwd_path.resolve())

        # Verify directory exists
        if not Path(cwd_str).exists():
            return {
                "success": False,
                "error": f"Directory does not exist: {cwd_str}",
                "stdout": "",
                "stderr": f"Directory not found: {cwd_str}",
                "exit_code": 1,
                "command": command,
                "cwd": cwd_str
            }

        logger.info(f"[TERMINAL] Running in: {cwd_str}")

        if background:
            return await self._run_background(command, cwd_str)
        
        # Use synchronous subprocess for reliability (especially on Windows)
        try:
            result = subprocess.run(
                command,
                shell=True,
                cwd=cwd_str,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=timeout
            )

            stdout_text = result.stdout or ""
            stderr_text = result.stderr or ""
            return_code = result.returncode
            success = return_code == 0

            # Generate error message for failed commands
            error_msg = ""
            if not success:
                if stderr_text.strip():
                    error_msg = stderr_text.strip()
                elif stdout_text.strip():
                    error_msg = stdout_text.strip()
                else:
                    error_msg = f"Command '{command}' failed with exit code {return_code}"

            logger.info(f"[TERMINAL] {'SUCCESS' if success else 'FAILED'} (exit: {return_code})")

            return {
                "success": success,
                "stdout": stdout_text,
                "stderr": stderr_text,
                "exit_code": return_code,
                "command": command,
                "cwd": cwd_str,
                "error": error_msg if not success else "",
            }

        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": f"Command timed out after {timeout} seconds",
                "stdout": "",
                "stderr": f"Timeout after {timeout}s",
                "exit_code": -1,
                "command": command,
                "cwd": cwd_str,
            }

    async def _run_background(self, command: str, cwd: str) -> Dict[str, Any]:
        """Run command in background and capture initial output"""
        import threading
        import time

        logger.info(f"[TERMINAL] Starting background process: {command}")

        try:
            process = subprocess.Popen(
                command,
                shell=True,
                cwd=cwd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding="utf-8",
                errors="replace",
            )

            # Capture initial output (useful for dev servers to get port info)
            stdout_lines = []
            stderr_lines = []

            def read_output(pipe, lines_list, name):
                try:
                    for line in iter(pipe.readline, ''):
                        if line:
                            lines_list.append(line)
                            logger.debug(f"[TERMINAL] {name}: {line.rstrip()}")
                except Exception as e:
                    logger.warning(f"[TERMINAL] Error reading {name}: {e}")

            stdout_thread = threading.Thread(
                target=read_output, 
                args=(process.stdout, stdout_lines, "STDOUT")
            )
            stderr_thread = threading.Thread(
                target=read_output, 
                args=(process.stderr, stderr_lines, "STDERR")
            )
            stdout_thread.daemon = True
            stderr_thread.daemon = True
            stdout_thread.start()
            stderr_thread.start()

            # Wait briefly for startup output (e.g., port info)
            time.sleep(5)

            stdout_text = ''.join(stdout_lines)
            stderr_text = ''.join(stderr_lines)

            # Check if process is still running (good for dev servers)
            if process.poll() is None:
                return_code = 0
                success = True
                stdout_text += f"\n\n✅ Process running in background (PID: {process.pid})"
            else:
                return_code = process.returncode
                success = return_code == 0

            return {
                "success": success,
                "stdout": stdout_text,
                "stderr": stderr_text,
                "exit_code": return_code,
                "command": command,
                "cwd": cwd,
                "error": "" if success else stderr_text or stdout_text,
                "pid": process.pid,
                "background": True,
            }

        except Exception as e:
            logger.error(f"[TERMINAL] Background process error: {e}")
            return {
                "success": False,
                "error": str(e),
                "stdout": "",
                "stderr": str(e),
                "exit_code": -1,
                "command": command,
                "cwd": cwd,
            }
