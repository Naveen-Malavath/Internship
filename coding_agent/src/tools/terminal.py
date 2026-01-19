"""Terminal execution tool for running commands"""

import asyncio
import json
import os
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional

from loguru import logger

from .base import Tool, ToolParameter


class BackgroundProcess:
    """Represents a background process"""

    def __init__(self, process_id: str, process: asyncio.subprocess.Process, command: str):
        self.process_id = process_id
        self.process = process
        self.command = command
        self.output_lines: List[str] = []
        self.is_running = True


class TerminalTool(Tool):
    """Tool for executing terminal commands"""

    name = "terminal"
    description = """Execute terminal commands to install dependencies, run builds, start servers, and perform system operations.

**CRITICAL: Use this tool to:**
- Install dependencies: `npm install`, `pip install -r requirements.txt`, `npm install --prefix <dir>`
- Run development servers: `npm run dev`, `npm start`, `uvicorn main:app --reload`
- Execute build commands: `npm run build`, `python setup.py build`
- Run any system command: `node --version`, `python --version`, `ls`, `dir`
- Navigate and execute: Use `cwd` parameter for directory, or `cd <dir> && command` format

**Examples:**
- Install npm dependencies: command="npm install", cwd="calculator-app"
- Start dev server: command="npm run dev", cwd="calculator-app", background=true (for long-running)
- Check version: command="npm --version"
- Install and run: Use two separate tool calls (install first, then run)

**Important:**
- Always use this tool to execute commands - do NOT just describe what command to run
- After creating projects, ALWAYS install dependencies using this tool
- After installing, ALWAYS launch the application using this tool
- For long-running servers (dev servers), use background=true or they will timeout"""
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
            description="Timeout in seconds (default: 60)",
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
        """
        Initialize terminal tool
        
        Args:
            workspace_path: Default working directory
            event_callback: Optional callback for streaming events (async function)
        """
        self.workspace_path = workspace_path or Path.cwd()
        self.background_processes: Dict[str, BackgroundProcess] = {}
        self.event_callback = event_callback  # For real-time streaming

    async def execute(self, **kwargs) -> Dict[str, Any]:
        """Execute terminal command"""
        command = kwargs.get("command")
        if not command:
            error_msg = "Missing required parameter: command"
            logger.error(f"🔴 [TERMINAL] {error_msg}")
            return {
                "success": False,
                "error": error_msg,
                "stdout": "",
                "stderr": error_msg,
                "exit_code": 1,
                "command": ""
            }

        cwd = kwargs.get("cwd", str(self.workspace_path))
        # Auto-detect dev server commands and increase timeout
        timeout = kwargs.get("timeout", None)
        if timeout is None:
            # Auto-detect long-running commands
            if any(keyword in command.lower() for keyword in ["npm run dev", "npm start", "uvicorn", "flask run", "python -m http.server", "serve"]):
                timeout = 300  # 5 minutes for dev servers
                logger.info(f"🔄 [TERMINAL] Auto-detected dev server command, setting timeout to 300s")
                print(f"[TERMINAL] Auto-detected dev server command, setting timeout to 300s")
            else:
                timeout = 60  # Default 60 seconds
        
        background = kwargs.get("background", False)
        
        # Auto-detect if this should be a background command (dev servers)
        if not background and any(keyword in command.lower() for keyword in ["npm run dev", "npm start", "uvicorn", "flask run"]):
            logger.info(f"🔄 [TERMINAL] Auto-detected dev server command, suggesting background mode")
            print(f"[TERMINAL] Auto-detected dev server command - consider using background=true for long-running servers")

        logger.info(f"🔄 [TERMINAL] Execute called: command={command}, cwd={cwd}, timeout={timeout}, background={background}")
        print(f"[TERMINAL] Execute called: command={command}, cwd={cwd}")

        # Store original command for result tracking (before any wrapping/modification)
        original_command = command
        
        # Handle commands with "cd X && command" format
        # Extract directory from cd command and use it as cwd
        actual_command = command
        actual_cwd = cwd
        
        if command.startswith("cd "):
            # Check for "cd X && command" pattern
            if " && " in command:
                parts = command.split(" && ", 1)
                if len(parts) == 2:
                    cd_part = parts[0].replace("cd ", "").strip()
                    actual_command = parts[1]
                    
                    # Resolve the directory path
                    cd_path = Path(cd_part)
                    if not cd_path.is_absolute():
                        cd_path = self.workspace_path / cd_path
                    
                    actual_cwd = str(cd_path.resolve())
                    logger.info(f"🔄 [TERMINAL] Extracted cd from command: cd '{cd_part}' -> cwd={actual_cwd}, command='{actual_command}'")
                    print(f"[TERMINAL] Extracted cd from command: cd '{cd_part}' -> cwd={actual_cwd}, command='{actual_command}'")
            elif command.strip() == "cd" or command.strip().startswith("cd "):
                # Just "cd" or "cd X" without && - this should be handled differently
                logger.warning(f"⚠️ [TERMINAL] Command is just 'cd' - this won't work. Command: {command}")
                print(f"[WARNING] [TERMINAL] Command is just 'cd' - this won't work")

        try:
            if background:
                return await self._run_background(actual_command, actual_cwd)
            else:
                # Pass original_command so result shows the user's command, not the modified one
                result = await self._run_command(actual_command, actual_cwd, timeout, original_command)
                return result
        except Exception as e:
            logger.error(f"🔴 [TERMINAL] Terminal execution error: {e}", exc_info=True)
            print(f"[ERROR] [TERMINAL] Terminal execution error: {e}")
            import traceback
            traceback.print_exc()
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
        self, command: str, cwd: str, timeout: int, original_command: str = None
    ) -> Dict[str, Any]:
        """Run command and wait for completion"""
        logger.info(f"Executing command: {command} in cwd: {cwd}")
        print(f"[TERMINAL] Executing: {command} in cwd: {cwd}")

        try:
            # Check if cwd exists (resolve path to handle relative paths)
            cwd_path = Path(cwd) if cwd else self.workspace_path
            if not cwd_path.is_absolute():
                cwd_path = self.workspace_path / cwd_path
            
            cwd_str = str(cwd_path.resolve())
            
            if cwd and not Path(cwd_str).exists():
                error_msg = f"Directory does not exist: {cwd_str}"
                logger.error(f"🔴 [TERMINAL] {error_msg}")
                print(f"[ERROR] [TERMINAL] {error_msg}")
                return {
                    "success": False,
                    "error": error_msg,
                    "stdout": "",
                    "stderr": error_msg,
                    "exit_code": 1,
                    "command": command,
                    "cwd": cwd_str
                }
            
            # Log directory check
            logger.info(f"🟢 [TERMINAL] Directory exists: {cwd_str}")
            print(f"[OK] [TERMINAL] Directory exists: {cwd_str}")
            
            # CRITICAL: Verify this is the correct directory by checking for package.json (for npm projects)
            if "npm" in command.lower() or "node" in command.lower():
                package_json_path = Path(cwd_str) / "package.json"
                if package_json_path.exists():
                    logger.info(f"✅ [TERMINAL] Found package.json in cwd: {package_json_path}")
                    print(f"[OK] [TERMINAL] ✅ Found package.json in cwd: {package_json_path}")
                else:
                    logger.warning(f"⚠️ [TERMINAL] WARNING: No package.json found in cwd: {cwd_str}")
                    print(f"[WARNING] [TERMINAL] ⚠️ No package.json found in cwd: {cwd_str}")
                    # Try to find package.json in workspace
                    workspace_pkg = self.workspace_path / "package.json"
                    if workspace_pkg.exists():
                        logger.warning(f"⚠️ [TERMINAL] Found package.json in workspace root instead: {workspace_pkg}")
                        print(f"[WARNING] [TERMINAL] ⚠️ Found package.json in workspace root instead: {workspace_pkg}")
                    # Check if there are subdirectories with package.json
                    for subdir in Path(cwd_str).parent.iterdir():
                        if subdir.is_dir():
                            subdir_pkg = subdir / "package.json"
                            if subdir_pkg.exists():
                                logger.warning(f"⚠️ [TERMINAL] Found package.json in subdirectory: {subdir_pkg}")
                                print(f"[WARNING] [TERMINAL] ⚠️ Found package.json in subdirectory: {subdir_pkg}")
                                logger.warning(f"⚠️ [TERMINAL] SUGGESTION: Command might need to run in: {subdir}")
                                print(f"[WARNING] [TERMINAL] ⚠️ SUGGESTION: Command might need to run in: {subdir}")
            
            # Get system PATH to ensure commands are found
            import os
            import shutil
            import sys
            
            # CRITICAL: Get the ACTUAL system/user PATH, not just Python's environment
            # On Windows, Python's os.environ might not have the full user PATH
            # We need to query the actual system environment
            
            env = os.environ.copy()
            
            # On Windows, get the actual user/system PATH from the registry/system
            if sys.platform == "win32":
                try:
                    # Use PowerShell to get the actual PATH from the system
                    # This gets the PATH that your actual PowerShell session uses
                    import subprocess
                    result = subprocess.run(
                        ['powershell', '-Command', '$env:PATH'],
                        capture_output=True,
                        text=True,
                        timeout=5,
                        shell=False
                    )
                    if result.returncode == 0 and result.stdout.strip():
                        actual_path = result.stdout.strip()
                        env["PATH"] = actual_path
                        logger.info(f"✅ [TERMINAL] Got actual system PATH (length: {len(actual_path)})")
                        print(f"[OK] [TERMINAL] Got actual system PATH (length: {len(actual_path)})")
                    else:
                        logger.warning(f"⚠️ [TERMINAL] Could not get system PATH from PowerShell, using Python's env")
                        print(f"[WARNING] [TERMINAL] Could not get system PATH from PowerShell")
                except Exception as e:
                    logger.warning(f"⚠️ [TERMINAL] Error getting system PATH: {e}, using Python's env")
                    print(f"[WARNING] [TERMINAL] Error getting system PATH: {e}")
            
            # First, check what npm/node paths exist using shutil.which in current environment
            npm_path = shutil.which("npm", path=env.get("PATH", ""))
            node_path = shutil.which("node", path=env.get("PATH", ""))
            
            logger.info(f"🔍 [TERMINAL] npm found at: {npm_path}")
            print(f"[DEBUG] [TERMINAL] npm found at: {npm_path}")
            logger.info(f"🔍 [TERMINAL] node found at: {node_path}")
            print(f"[DEBUG] [TERMINAL] node found at: {node_path}")
            
            # Get the actual PATH from the environment
            current_path = env.get("PATH", "")
            logger.info(f"🔍 [TERMINAL] PATH length: {len(current_path)}")
            print(f"[DEBUG] [TERMINAL] PATH length: {len(current_path)}")
            
            # Common Node.js installation paths on Windows
            possible_node_paths = [
                r"C:\Program Files\nodejs",
                r"C:\Program Files (x86)\nodejs",
                os.path.expanduser(r"~\AppData\Roaming\npm"),
            ]
            
            # If npm is not found even with system PATH, try common locations
            if not npm_path:
                logger.warning(f"⚠️ [TERMINAL] npm not found in system PATH, trying common locations")
                print(f"[WARNING] [TERMINAL] npm not found in system PATH, trying common locations")
                
                # Try to find npm in common locations
                for path in possible_node_paths:
                    if os.path.exists(path):
                        npm_cmd = os.path.join(path, "npm.cmd")
                        if os.path.exists(npm_cmd):
                            npm_path = npm_cmd
                            logger.info(f"✅ [TERMINAL] Found npm at: {npm_path}")
                            print(f"[OK] [TERMINAL] Found npm at: {npm_path}")
                            break
                
                # If still not found, add common paths to PATH
                if not npm_path:
                    for path in possible_node_paths:
                        if os.path.exists(path) and path not in current_path:
                            env["PATH"] = f"{path};{env.get('PATH', '')}"
                            logger.info(f"✅ [TERMINAL] Added to PATH: {path}")
                            print(f"[OK] [TERMINAL] Added to PATH: {path}")
                    
                    # Re-check after adding paths
                    npm_path = shutil.which("npm", path=env.get("PATH", ""))
            
            # Verify npm is accessible
            final_npm_path = npm_path or shutil.which("npm", path=env.get("PATH", ""))
            if final_npm_path:
                logger.info(f"✅ [TERMINAL] npm is accessible: {final_npm_path}")
                print(f"[OK] [TERMINAL] npm is accessible: {final_npm_path}")
            else:
                logger.warning(f"⚠️ [TERMINAL] npm NOT found - commands may fail")
                print(f"[WARNING] [TERMINAL] npm NOT found - commands may fail")
                logger.warning(f"⚠️ [TERMINAL] PATH (first 500 chars): {env.get('PATH', '')[:500]}")
                print(f"[WARNING] [TERMINAL] PATH (first 500 chars): {env.get('PATH', '')[:500]}")
            
            # On Windows, ALWAYS use full path to npm/node if available
            # This completely bypasses PATH issues
            if sys.platform == "win32" and not command.startswith("powershell") and not command.startswith("cmd") and not command.startswith('"'):
                # Check if npm is in the command
                if "npm" in command.lower() and final_npm_path:
                    # Replace "npm" with full path
                    # Handle npm.cmd or npm.exe
                    npm_exe = final_npm_path
                    if not npm_exe.endswith('.cmd') and not npm_exe.endswith('.exe'):
                        # Try to find npm.cmd in the same directory
                        npm_dir = os.path.dirname(npm_exe)
                        npm_cmd = os.path.join(npm_dir, "npm.cmd")
                        if os.path.exists(npm_cmd):
                            npm_exe = npm_cmd
                    
                    # Replace npm (case-insensitive) with full path
                    import re
                    # Match "npm" as word boundary and replace with literal path
                    # Use a replacement function to avoid regex escaping issues
                    def replace_npm(match):
                        return f'"{npm_exe}"'
                    command = re.sub(r'\bnpm\b', replace_npm, command, flags=re.IGNORECASE)
                    logger.info(f"✅ [TERMINAL] Replaced npm with full path: {command[:150]}")
                    print(f"[OK] [TERMINAL] Replaced npm with full path: {command[:150]}")
                elif "node" in command.lower() and node_path:
                    # Replace node with full path
                    import re
                    # Ensure we have node.exe
                    node_exe = node_path
                    if not node_exe.endswith('.exe'):
                        node_exe = node_path + '.exe' if os.path.exists(node_path + '.exe') else node_path
                    # Simple string replace to avoid regex escaping issues
                    def replace_node(match):
                        return f'"{node_exe}"'
                    command = re.sub(r'\bnode\b', replace_node, command, flags=re.IGNORECASE)
                    logger.info(f"✅ [TERMINAL] Replaced node with full path: {command[:150]}")
                    print(f"[OK] [TERMINAL] Replaced node with full path: {command[:150]}")
            
            logger.info(f"🔍 [TERMINAL] Creating subprocess with command: {command}")
            print(f"[DEBUG] [TERMINAL] Creating subprocess with command: {command}")
            print(f"[INFO] [TERMINAL] ════════════════════════════════════════════════════")
            print(f"[INFO] [TERMINAL] EXECUTING COMMAND: {command}")
            print(f"[INFO] [TERMINAL] Working Directory: {cwd_str}")
            print(f"[INFO] [TERMINAL] ════════════════════════════════════════════════════")
            logger.debug(f"🔍 [TERMINAL] PATH (first 300 chars): {env.get('PATH', '')[:300]}")
            
            # On Windows, asyncio.create_subprocess_shell uses cmd.exe by default
            # Ensure the command works properly with cmd.exe syntax
            # If we've replaced npm/node with full paths, the command should work
            # But cmd.exe needs proper quoting for paths with spaces
            
            # IMPORTANT: Commands run in isolated subprocesses, NOT in your visible CMD window
            # This is by design - output is captured programmatically
            # To see commands, check the server logs or frontend UI
            
            # CRITICAL: Verify we're in the right directory by listing files before execution
            if "npm" in command.lower() or "node" in command.lower():
                try:
                    import os
                    files_in_cwd = os.listdir(cwd_str)
                    logger.info(f"🔍 [TERMINAL] Files in cwd ({cwd_str}): {files_in_cwd[:10]}")
                    print(f"[DEBUG] [TERMINAL] Files in cwd ({cwd_str}): {files_in_cwd[:10]}")
                    if "package.json" in files_in_cwd:
                        logger.info(f"✅ [TERMINAL] Confirmed: package.json exists in cwd")
                        print(f"[OK] [TERMINAL] ✅ Confirmed: package.json exists in cwd")
                    else:
                        logger.warning(f"⚠️ [TERMINAL] WARNING: package.json NOT in cwd, but npm command is being run!")
                        print(f"[WARNING] [TERMINAL] ⚠️ package.json NOT in cwd!")
                except Exception as e:
                    logger.warning(f"⚠️ [TERMINAL] Could not list files in cwd: {e}")
                    print(f"[WARNING] [TERMINAL] Could not list files in cwd: {e}")
            
            # Create subprocess with proper environment
            # On Windows, this uses cmd.exe which handles .cmd files properly
            # CRITICAL: cwd_str is the ACTUAL directory where the command will run
            logger.info(f"🔍 [TERMINAL] About to execute in cwd: {cwd_str}")
            print(f"[DEBUG] [TERMINAL] About to execute command: {command}")
            print(f"[DEBUG] [TERMINAL] Working directory (cwd): {cwd_str}")
            
            # CRITICAL: Handle Windows asyncio subprocess issue
            # On Windows, create_subprocess_shell is UNRELIABLE - it often fails silently
            # ALWAYS use synchronous subprocess on Windows for reliability
            import sys
            import subprocess
            
            process = None
            use_sync_subprocess = sys.platform == "win32"  # ALWAYS use sync on Windows
            
            if use_sync_subprocess:
                logger.info(f"🔧 [TERMINAL] Using synchronous subprocess (Windows mode)")
                print(f"[INFO] [TERMINAL] Using synchronous subprocess (Windows mode - more reliable)")
                # Go directly to synchronous fallback
                e = None  # No exception, just forcing sync mode
            else:
                try:
                    process = await asyncio.create_subprocess_shell(
                        command,
                        stdout=asyncio.subprocess.PIPE,
                        stderr=asyncio.subprocess.PIPE,
                        cwd=cwd_str,  # THIS determines where the command runs
                        env=env,  # Use environment with proper PATH
                        shell=True,  # Explicitly use shell (default on Windows)
                    )
                except (NotImplementedError, RuntimeError, OSError) as e:
                    pass  # Fall through to sync subprocess
            
            # Use synchronous subprocess (either forced on Windows, or as fallback)
            if use_sync_subprocess or process is None:
                # On Windows, create_subprocess_shell may raise NotImplementedError
                # or RuntimeError if the event loop doesn't support it
                # Fallback to synchronous subprocess
                # Fallback: Use subprocess.run instead of asyncio if shell subprocess not supported
                if e:
                    logger.warning(f"⚠️ [TERMINAL] create_subprocess_shell failed with: {e}")
                    print(f"[WARNING] [TERMINAL] create_subprocess_shell failed: {e}")
                logger.info(f"🔧 [TERMINAL] Using synchronous subprocess fallback")
                print(f"[INFO] [TERMINAL] Using synchronous subprocess - this is reliable on Windows")
                
                try:
                    # Use synchronous subprocess as fallback
                    logger.info(f"🔍 [TERMINAL] Executing subprocess: {command} in cwd: {cwd_str}")
                    print(f"[DEBUG] [TERMINAL] Executing subprocess: {command} in cwd: {cwd_str}")
                    
                    # CRITICAL: For dev server commands in fallback mode, we need a different approach
                    # Regular subprocess.run() will block forever for dev servers
                    # Check if this is a dev server command
                    # CRITICAL: Use original_command for detection since 'command' has been transformed
                    # (e.g., npm -> "C:\Program Files\nodejs\npm.cmd")
                    detection_cmd = (original_command if original_command else command).lower()
                    is_dev_server = any(keyword in detection_cmd for keyword in [
                        "npm run dev", "npm start", "npm run start", 
                        "uvicorn", "flask run", "python -m http.server"
                    ])
                    
                    if is_dev_server:
                        # For dev servers, start process and capture initial output including port info
                        logger.info(f"🔄 [TERMINAL] Dev server detected. Starting process and capturing initial output...")
                        print(f"[INFO] [TERMINAL] Dev server detected. Starting process and capturing startup output...")
                        
                        try:
                            import select
                            import threading
                            import queue
                            
                            # Start process without waiting
                            process = subprocess.Popen(
                                command,
                                shell=True,
                                cwd=cwd_str,
                                env=env,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                text=True,
                                encoding="utf-8",
                                errors="replace",
                                bufsize=1  # Line buffered for real-time output
                            )
                            
                            # Use threads to read stdout and stderr without blocking
                            stdout_lines = []
                            stderr_lines = []
                            
                            def read_output(pipe, output_list, stream_name):
                                """Read output from pipe line by line"""
                                try:
                                    for line in iter(pipe.readline, ''):
                                        if line:
                                            output_list.append(line)
                                            logger.info(f"📤 [TERMINAL] {stream_name}: {line.rstrip()}")
                                            print(f"[TERMINAL] {stream_name}: {line.rstrip()}")
                                except Exception as e:
                                    logger.warning(f"⚠️ [TERMINAL] Error reading {stream_name}: {e}")
                            
                            # Start reader threads
                            stdout_thread = threading.Thread(target=read_output, args=(process.stdout, stdout_lines, "STDOUT"))
                            stderr_thread = threading.Thread(target=read_output, args=(process.stderr, stderr_lines, "STDERR"))
                            stdout_thread.daemon = True
                            stderr_thread.daemon = True
                            stdout_thread.start()
                            stderr_thread.start()
                            
                            # Wait for initial output (dev servers typically print port info within 5-8 seconds)
                            import time
                            max_wait = 8  # Wait up to 8 seconds for startup output
                            start_time = time.time()
                            
                            # Keep checking for output and look for port/URL indicators
                            port_found = False
                            while time.time() - start_time < max_wait:
                                time.sleep(0.5)
                                
                                # Check if we found port/URL info in stdout
                                current_output = ''.join(stdout_lines)
                                if any(indicator in current_output.lower() for indicator in [
                                    'localhost:', 'http://', '127.0.0.1:', 'listening on', 'running at', 
                                    'ready in', 'local:', 'network:', 'port'
                                ]):
                                    port_found = True
                                    # Wait a bit more to capture all startup messages
                                    time.sleep(1)
                                    break
                                
                                # Also check stderr (some tools output to stderr)
                                current_stderr = ''.join(stderr_lines)
                                if any(indicator in current_stderr.lower() for indicator in [
                                    'localhost:', 'http://', '127.0.0.1:', 'listening on', 'running at'
                                ]):
                                    port_found = True
                                    time.sleep(1)
                                    break
                            
                            # Collect all output
                            stdout_text = ''.join(stdout_lines)
                            stderr_text = ''.join(stderr_lines)
                            
                            # Check if process is still running
                            if process.poll() is None:  # Process is still running (good for dev server)
                                return_code = 0
                                success = True
                                
                                # If no output captured, add informative message
                                if not stdout_text.strip() and not stderr_text.strip():
                                    stdout_text = "Development server is starting...\nProcess is running in background.\n(No startup output captured - server may take longer to start)"
                                else:
                                    # Add a note that the server is running
                                    stdout_text = stdout_text.rstrip() + "\n\n✅ Development server is running in background (PID: {})".format(process.pid)
                                
                                logger.info(f"✅ [TERMINAL] Dev server started successfully, captured {len(stdout_text)} chars of output")
                                print(f"[OK] [TERMINAL] Dev server started successfully")
                                if port_found:
                                    print(f"[OK] [TERMINAL] Port/URL info found in output")
                            else:
                                # Process exited (unexpected for dev server)
                                return_code = process.returncode
                                success = False
                                
                                # If no output captured, provide informative message
                                if not stdout_text.strip() and not stderr_text.strip():
                                    if return_code == -1 or return_code == 9009:
                                        stdout_text = f"Process failed to start (exit code {return_code}). The command may not be found or PATH may be incorrect."
                                    else:
                                        stdout_text = f"Process exited unexpectedly with code {return_code}"
                                
                                logger.warning(f"⚠️ [TERMINAL] Dev server exited with code {return_code}")
                                print(f"[WARNING] [TERMINAL] Dev server exited with code {return_code}")
                            
                            # Build error message for dev server
                            error_msg = "" if success else stderr_text.strip() if stderr_text.strip() else stdout_text.strip() if stdout_text.strip() else "Dev server failed to start"
                            cmd_display = original_command if original_command else command
                            
                            logger.info(f"🔄 [TERMINAL] Dev server completed - exit_code: {return_code}, success: {success}, stdout_len: {len(stdout_text)}")
                            print(f"[OK] [TERMINAL] Dev server completed - exit_code: {return_code}, success: {success}")
                            print(f"[OK] [TERMINAL] Captured output:\n{stdout_text[:500]}")
                            
                            return {
                                "success": success,
                                "stdout": stdout_text,
                                "stderr": stderr_text,
                                "exit_code": return_code,
                                "command": cmd_display,
                                "cwd": cwd_str,
                                "error": error_msg,
                                "pid": process.pid if process.poll() is None else None,
                            }
                        except Exception as popen_error:
                            # If Popen fails, return error with all required fields
                            logger.error(f"🔴 [TERMINAL] Failed to start dev server process: {popen_error}")
                            print(f"[ERROR] [TERMINAL] Failed to start dev server process: {popen_error}")
                            import traceback
                            traceback.print_exc()
                            cmd_display = original_command if original_command else command
                            return {
                                "success": False,
                                "error": f"Failed to start dev server: {str(popen_error)}",
                                "stdout": "",
                                "stderr": str(popen_error),
                                "exit_code": -1,
                                "command": cmd_display,
                                "cwd": cwd_str,
                            }
                    else:
                        # For regular commands, use normal subprocess.run()
                        logger.info(f"🔍 [TERMINAL] About to call subprocess.run with:")
                        logger.info(f"   command: {command}")
                        logger.info(f"   cwd: {cwd_str}")
                        logger.info(f"   shell: True")
                        logger.info(f"   timeout: {timeout}")
                        print(f"[DEBUG] [TERMINAL] === SUBPROCESS.RUN CALL ===")
                        print(f"[DEBUG] [TERMINAL] Command: {command}")
                        print(f"[DEBUG] [TERMINAL] CWD: {cwd_str}")
                        print(f"[DEBUG] [TERMINAL] Timeout: {timeout}")
                        
                        result_obj = subprocess.run(
                            command,
                            shell=True,
                            cwd=cwd_str,
                            env=env,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            text=True,
                            encoding="utf-8",
                            errors="replace",
                            timeout=timeout
                        )
                        
                        logger.info(f"🔍 [TERMINAL] subprocess.run returned:")
                        logger.info(f"   returncode: {result_obj.returncode}")
                        logger.info(f"   stdout length: {len(result_obj.stdout) if result_obj.stdout else 0}")
                        logger.info(f"   stderr length: {len(result_obj.stderr) if result_obj.stderr else 0}")
                        print(f"[DEBUG] [TERMINAL] === SUBPROCESS.RUN RESULT ===")
                        print(f"[DEBUG] [TERMINAL] Return code: {result_obj.returncode}")
                        print(f"[DEBUG] [TERMINAL] STDOUT length: {len(result_obj.stdout) if result_obj.stdout else 0}")
                        print(f"[DEBUG] [TERMINAL] STDERR length: {len(result_obj.stderr) if result_obj.stderr else 0}")
                        print(f"[DEBUG] [TERMINAL] STDOUT content: {repr(result_obj.stdout[:200]) if result_obj.stdout else '(none)'}")
                        print(f"[DEBUG] [TERMINAL] STDERR content: {repr(result_obj.stderr[:200]) if result_obj.stderr else '(none)'}")
                        
                        # Convert to async-compatible result
                        stdout_text = result_obj.stdout if result_obj.stdout else ""
                        stderr_text = result_obj.stderr if result_obj.stderr else ""
                        return_code = result_obj.returncode
                        success = return_code == 0
                        
                        logger.info(f"✅ [TERMINAL] Fallback subprocess completed - exit_code: {return_code}, success: {success}")
                        print(f"[OK] [TERMINAL] ✅ Fallback subprocess completed - exit_code: {return_code}, success: {success}")
                        print(f"[OK] [TERMINAL] STDOUT length: {len(stdout_text)}, STDERR length: {len(stderr_text)}")
                        
                        # Build error message
                        error_msg = ""
                        if not success:
                            if stderr_text and stderr_text.strip():
                                error_msg = stderr_text.strip()
                            elif stdout_text and stdout_text.strip():
                                error_msg = stdout_text.strip()
                            else:
                                error_msg = f"Command '{command}' failed with exit code {return_code}"
                            logger.warning(f"⚠️ [TERMINAL] Command failed - error: {error_msg[:200]}")
                            print(f"[WARNING] [TERMINAL] Command failed - error: {error_msg[:200]}")
                        else:
                            logger.info(f"✅ [TERMINAL] Command succeeded via fallback method")
                            print(f"[OK] [TERMINAL] Command succeeded via fallback method")
                        
                        # Use original_command for display if available
                        cmd_display = original_command if original_command else command
                        
                        return {
                            "success": success,
                            "stdout": stdout_text,
                            "stderr": stderr_text,
                            "exit_code": return_code,
                            "command": cmd_display,
                            "cwd": cwd_str,
                            "error": "" if success else error_msg,
                        }
                except subprocess.TimeoutExpired:
                    cmd_display = original_command if original_command else command
                    error_msg = f"Command timed out after {timeout} seconds"
                    logger.error(f"🔴 [TERMINAL] Fallback subprocess timeout: {error_msg}")
                    print(f"[ERROR] [TERMINAL] Fallback subprocess timeout: {error_msg}")
                    return {
                        "success": False,
                        "error": error_msg,
                        "stdout": "",
                        "stderr": error_msg,
                        "exit_code": -1,
                        "command": cmd_display,
                        "cwd": cwd_str,
                    }
                except Exception as fallback_error:
                    cmd_display = original_command if original_command else command
                    error_msg = f"Both async and sync subprocess failed. Async error: {str(e)}, Sync error: {str(fallback_error)}"
                    logger.error(f"🔴 [TERMINAL] All subprocess methods failed: {error_msg}")
                    print(f"[ERROR] [TERMINAL] All subprocess methods failed: {error_msg}")
                    import traceback
                    traceback.print_exc()
                    # Return error result instead of raising to prevent crashes
                    return {
                        "success": False,
                        "error": error_msg,
                        "stdout": "",
                        "stderr": error_msg,
                        "exit_code": -1,
                        "command": cmd_display,
                        "cwd": cwd_str,
                    }

            # If process creation failed and fallback wasn't used, return error
            if process is None:
                logger.error(f"🔴 [TERMINAL] Process is None after creation attempt (fallback should have been used)")
                print(f"[ERROR] [TERMINAL] Process is None after creation attempt")
                cmd_display = original_command if original_command else command
                return {
                    "success": False,
                    "error": "Failed to create subprocess and fallback didn't execute",
                    "stdout": "",
                    "stderr": "Failed to create subprocess",
                    "exit_code": -1,
                    "command": cmd_display,
                    "cwd": cwd_str,
                }

            # Stream output in real-time
            stdout_chunks = []
            stderr_chunks = []
            
            # Get display command early
            display_cmd = original_command if original_command else command
            
            async def stream_output(stream, is_stdout=True):
                """Stream output line by line and emit events in real-time"""
                chunk_buffer = ""
                while True:
                    try:
                        chunk = await stream.readline()
                        if not chunk:
                            break
                        chunk_text = chunk.decode('utf-8', errors='replace')
                        chunk_buffer += chunk_text
                        
                        # Emit streaming event for each line/chunk
                        if self.event_callback:
                            from datetime import datetime
                            await self.event_callback({
                                "type": "terminal_output_stream",
                                "source": "terminal",
                                "target": "ui",
                                "data": {
                                    "command": display_cmd,
                                    "cwd": cwd_str,
                                    "stream": "stdout" if is_stdout else "stderr",
                                    "chunk": chunk_text,
                                    "accumulated": chunk_buffer[-1000:] if len(chunk_buffer) > 1000 else chunk_buffer
                                },
                                "metadata": {},
                                "timestamp": datetime.now().isoformat()
                            })
                        
                        if is_stdout:
                            stdout_chunks.append(chunk_text)
                        else:
                            stderr_chunks.append(chunk_text)
                        
                        # Also log to console
                        if is_stdout:
                            print(f"[TERMINAL STREAM] STDOUT: {chunk_text.rstrip()}")
                        else:
                            print(f"[TERMINAL STREAM] STDERR: {chunk_text.rstrip()}")
                    except Exception as e:
                        logger.error(f"🔴 [TERMINAL] Error streaming output: {e}")
                        break
            
            # Wait for completion with timeout - stream output in real-time
            try:
                logger.info(f"🔍 [TERMINAL] Starting to stream output (timeout: {timeout}s)")
                print(f"[DEBUG] [TERMINAL] Starting to stream output (timeout: {timeout}s)")
                
                # Stream stdout and stderr concurrently
                stdout_task = asyncio.create_task(stream_output(process.stdout, is_stdout=True))
                stderr_task = asyncio.create_task(stream_output(process.stderr, is_stdout=False))
                
                # Wait for process to complete or timeout
                try:
                    await asyncio.wait_for(process.wait(), timeout=timeout)
                    # Wait for streams to finish
                    await stdout_task
                    await stderr_task
                except asyncio.TimeoutError:
                    stdout_task.cancel()
                    stderr_task.cancel()
                    raise
                
                # Combine chunks
                stdout_text = "".join(stdout_chunks)
                stderr_text = "".join(stderr_chunks)
                
                logger.info(f"🔍 [TERMINAL] Process completed. Return code: {process.returncode}")
                print(f"[DEBUG] [TERMINAL] Process completed. Return code: {process.returncode}")
            except asyncio.TimeoutError:
                process.kill()
                await process.wait()
                timeout_error = f"Command timed out after {timeout} seconds"
                logger.error(f"🔴 [TERMINAL] {timeout_error}: {command}")
                print(f"[ERROR] [TERMINAL] {timeout_error}: {command}")
                return {
                    "success": False,
                    "error": timeout_error,
                    "stdout": "",
                    "stderr": timeout_error,
                    "exit_code": -1,
                    "command": command,
                    "cwd": cwd_str if 'cwd_str' in locals() else cwd,
                }

            # Get return code BEFORE decoding (critical!)
            return_code = process.returncode
            logger.info(f"🔍 [TERMINAL] Process return_code: {return_code}")
            print(f"[DEBUG] [TERMINAL] Process return_code: {return_code}")
            
            # Decode output - CRITICAL: Always decode even if empty
            try:
                stdout_text = stdout.decode("utf-8", errors="replace") if stdout else ""
                stderr_text = stderr.decode("utf-8", errors="replace") if stderr else ""
            except Exception as e:
                logger.error(f"🔴 [TERMINAL] Error decoding output: {e}")
                print(f"[ERROR] [TERMINAL] Error decoding output: {e}")
                stdout_text = str(stdout) if stdout else ""
                stderr_text = str(stderr) if stderr else ""
            
            # CRITICAL: Log raw bytes and decoded text
            logger.info(f"🔍 [TERMINAL] Raw stdout bytes: {len(stdout) if stdout else 0}, Raw stderr bytes: {len(stderr) if stderr else 0}")
            print(f"[DEBUG] [TERMINAL] Raw stdout bytes: {len(stdout) if stdout else 0}, Raw stderr bytes: {len(stderr) if stderr else 0}")

            success = return_code == 0
            
            # CRITICAL DIAGNOSTIC: Log all information before building error message
            logger.info(f"🔍 [TERMINAL] DIAGNOSTIC - return_code={return_code}, success={success}, stdout_len={len(stdout_text)}, stderr_len={len(stderr_text)}")
            print(f"[DEBUG] [TERMINAL] DIAGNOSTIC - return_code={return_code}, success={success}, stdout_len={len(stdout_text)}, stderr_len={len(stderr_text)}")
            
            # CRITICAL: Always log output content, even if empty
            logger.info(f"🔍 [TERMINAL] STDOUT content (first 500 chars): {repr(stdout_text[:500])}")
            print(f"[DEBUG] [TERMINAL] STDOUT content (first 500 chars): {repr(stdout_text[:500])}")
            logger.info(f"🔍 [TERMINAL] STDERR content (first 500 chars): {repr(stderr_text[:500])}")
            print(f"[DEBUG] [TERMINAL] STDERR content (first 500 chars): {repr(stderr_text[:500])}")

            logger.info(f"🔍 [TERMINAL] Command result - exit_code: {return_code}, success: {success}")
            print(f"[DEBUG] [TERMINAL] Command result - exit_code: {return_code}, success: {success}")
            logger.info(f"🔍 [TERMINAL] STDOUT length: {len(stdout_text)}, content: {repr(stdout_text[:100])}")
            print(f"[DEBUG] [TERMINAL] STDOUT length: {len(stdout_text)}, content: {repr(stdout_text[:100])}")
            logger.info(f"🔍 [TERMINAL] STDERR length: {len(stderr_text)}, content: {repr(stderr_text[:100])}")
            print(f"[DEBUG] [TERMINAL] STDERR length: {len(stderr_text)}, content: {repr(stderr_text[:100])}")

            if success:
                logger.info(f"✅ [TERMINAL] Command completed successfully: {command}")
                print(f"[OK] [TERMINAL] Command completed successfully: {command}")
                if stdout_text:
                    logger.info(f"ℹ️ [TERMINAL] STDOUT: {stdout_text[:200]}")
                    print(f"[INFO] [TERMINAL] STDOUT: {stdout_text[:200]}")
            else:
                logger.warning(
                    f"⚠️ [TERMINAL] Command failed with exit code {process.returncode}: {command}"
                )
                print(f"[WARNING] [TERMINAL] Command failed with exit code {process.returncode}: {command}")
                if stderr_text:
                    logger.warning(f"⚠️ [TERMINAL] STDERR: {stderr_text[:200]}")
                    print(f"[WARNING] [TERMINAL] STDERR: {stderr_text[:200]}")
                if stdout_text:
                    logger.info(f"ℹ️ [TERMINAL] STDOUT: {stdout_text[:200]}")
                    print(f"[INFO] [TERMINAL] STDOUT: {stdout_text[:200]}")

            # Build error message from stderr or exit code
            # Always provide a meaningful error message if command failed
            # CRITICAL: Initialize error_msg BEFORE the if statement to ensure it's always defined
            error_msg = ""  # Default to empty for success
            
            if not success:
                logger.info(f"🔴 [TERMINAL] Building error message - command failed, exit_code: {return_code}")
                print(f"[ERROR] [TERMINAL] Building error message - command failed, exit_code: {return_code}")
                logger.info(f"🔴 [TERMINAL] STDOUT available: {bool(stdout_text)}, STDERR available: {bool(stderr_text)}")
                print(f"[ERROR] [TERMINAL] STDOUT available: {bool(stdout_text)}, STDERR available: {bool(stderr_text)}")
                logger.info(f"🔴 [TERMINAL] STDOUT content: {repr(stdout_text[:200])}, STDERR content: {repr(stderr_text[:200])}")
                print(f"[ERROR] [TERMINAL] STDOUT content: {repr(stdout_text[:200])}, STDERR content: {repr(stderr_text[:200])}")
                
                if stderr_text and stderr_text.strip():
                    error_msg = stderr_text.strip()
                    logger.info(f"🔴 [TERMINAL] Using STDERR for error: {error_msg[:100]}")
                    print(f"[ERROR] [TERMINAL] Using STDERR for error: {error_msg[:100]}")
                elif stdout_text and stdout_text.strip():
                    # Sometimes errors are in stdout (e.g., Windows)
                    error_msg = stdout_text.strip()
                    logger.info(f"🔴 [TERMINAL] Using STDOUT for error: {error_msg[:100]}")
                    print(f"[ERROR] [TERMINAL] Using STDOUT for error: {error_msg[:100]}")
                else:
                    # No error output - likely "command not found" on Windows
                    # Provide helpful error message with command and exit code
                    error_msg = f"Command '{command}' failed with exit code {return_code}"
                    if return_code == 1 or return_code == 9009 or return_code == -1:
                        # Exit code 9009 on Windows typically means "command not found"
                        # Exit code -1 often means process was killed or command not found
                        error_msg = f"Command not found or failed to execute: '{command}'. Exit code: {return_code}. The program may not be installed or not in PATH."
                        # Check for common missing commands
                        if "npm" in command.lower() or "node" in command.lower():
                            error_msg += "\n\nNode.js/npm may not be installed. Please install Node.js from https://nodejs.org/"
                    elif return_code == 2:
                        error_msg += " (Command syntax error or file not found)"
                    else:
                        error_msg += f" (No error output captured - exit code: {return_code})"
                    
                    logger.info(f"🔴 [TERMINAL] Generated error message (no output): {error_msg}")
                    print(f"[ERROR] [TERMINAL] Generated error message (no output): {error_msg}")
                
                # CRITICAL VALIDATION: Ensure error_msg is NEVER empty for failed commands
                if not error_msg or error_msg.strip() == "":
                    logger.error(f"🔴 [TERMINAL] CRITICAL BUG: error_msg is empty after generation! Exit code: {return_code}")
                    print(f"[ERROR] [TERMINAL] CRITICAL BUG: error_msg is empty after generation! Exit code: {return_code}")
                    error_msg = f"CRITICAL: Command '{command}' failed with exit code {return_code} but error message generation failed. STDOUT: {stdout_text[:100] if stdout_text else '(empty)'}, STDERR: {stderr_text[:100] if stderr_text else '(empty)'}"
            else:
                error_msg = ""  # Empty string for success
                logger.info(f"✅ [TERMINAL] Command succeeded - error field set to empty string")
                print(f"[OK] [TERMINAL] Command succeeded - error field set to empty string")
            
            # Build result dict with guaranteed error field
            # Use original_command for display (user's command) if available, otherwise use the executed command
            display_command = original_command if original_command else command
            
            # CRITICAL: Log the result state before building result dict
            logger.info(f"🔍 [TERMINAL] Building result - success={success}, exit_code={return_code}, stdout_len={len(stdout_text)}, stderr_len={len(stderr_text)}")
            print(f"[DEBUG] [TERMINAL] Building result - success={success}, exit_code={return_code}, stdout_len={len(stdout_text)}, stderr_len={len(stderr_text)}")
            logger.info(f"🔍 [TERMINAL] error_msg value: {repr(error_msg[:200]) if error_msg else '(empty/None)'}")
            print(f"[DEBUG] [TERMINAL] error_msg value: {repr(error_msg[:200]) if error_msg else '(empty/None)'}")
            
            # CRITICAL: For failed commands, ensure error_msg is NEVER empty
            if not success:
                if not error_msg or error_msg.strip() == "":
                    logger.error(f"🔴 [TERMINAL] CRITICAL: error_msg is empty for failed command! Exit code: {return_code}")
                    print(f"[ERROR] [TERMINAL] CRITICAL: error_msg is empty for failed command! Exit code: {return_code}")
                    # Generate error message as last resort
                    error_msg = (
                        f"Command '{command}' failed with exit code {return_code}. "
                        f"STDOUT: {stdout_text[:200] if stdout_text and stdout_text.strip() else '(empty)'}, "
                        f"STDERR: {stderr_text[:200] if stderr_text and stderr_text.strip() else '(empty)'}"
                    )
                    if return_code == 1 or return_code == 9009 or return_code == -1:
                        error_msg = f"Command not found or failed to execute: '{command}'. Exit code: {return_code}. The program may not be installed or not in PATH."
                        if "npm" in command.lower() or "node" in command.lower():
                            error_msg += " Node.js/npm may not be installed. Please install Node.js from https://nodejs.org/"
                    logger.error(f"🔴 [TERMINAL] Generated emergency error message: {error_msg[:200]}")
                    print(f"[ERROR] [TERMINAL] Generated emergency error message: {error_msg[:200]}")
            
            # Build result dict with error field set IMMEDIATELY
            result = {
                "success": success,
                "stdout": stdout_text,
                "stderr": stderr_text,
                "exit_code": return_code,
                "command": display_command,  # Show original user command for clarity
                "cwd": cwd_str if 'cwd_str' in locals() else cwd,
                "error": "" if success else error_msg,  # Set error field IMMEDIATELY in dict
            }
            
            # CRITICAL VALIDATION: Ensure error field is NEVER empty for failed commands
            if not success:
                if not result.get("error") or result["error"].strip() == "":
                    logger.error(f"🔴 [TERMINAL] CRITICAL VALIDATION FAILED: result['error'] is empty after dict creation!")
                    print(f"[ERROR] [TERMINAL] CRITICAL VALIDATION FAILED: result['error'] is empty after dict creation!")
                    emergency_error = (
                        f"EMERGENCY: Command '{command}' failed with exit code {return_code} "
                        f"but error field is empty. STDOUT: {stdout_text[:100] if stdout_text else '(empty)'}, "
                        f"STDERR: {stderr_text[:100] if stderr_text else '(empty)'}"
                    )
                    result["error"] = emergency_error
                    logger.error(f"🔴 [TERMINAL] Set emergency error: {emergency_error[:200]}")
                    print(f"[ERROR] [TERMINAL] Set emergency error: {emergency_error[:200]}")
                
                logger.info(f"🔴 [TERMINAL] Final error field value: {repr(result['error'][:200])}")
                print(f"[ERROR] [TERMINAL] Final error field value: {repr(result['error'][:200])}")
            else:
                # Success case - error field already set to "" in dict creation
                logger.info(f"✅ [TERMINAL] Command succeeded - error field is empty string (correct)")
                print(f"[OK] [TERMINAL] Command succeeded - error field is empty string (correct)")
            
            # CRITICAL: Verify error field is NEVER empty for failed commands
            if "error" not in result:
                logger.error(f"🔴 [TERMINAL] CRITICAL BUG: error field missing from result dict!")
                print(f"[ERROR] [TERMINAL] CRITICAL BUG: error field missing from result dict!")
                result["error"] = f"CRITICAL BUG: Error field missing. Exit code: {return_code}"
            
            # FORCE error field to have a value for failed commands
            if not success:
                if not result.get("error") or result["error"].strip() == "":
                    logger.error(f"🔴 [TERMINAL] CRITICAL: Failed command has empty/null error field! Exit code: {return_code}")
                    print(f"[ERROR] [TERMINAL] CRITICAL: Failed command has empty/null error field! Exit code: {return_code}")
                    # Force set error with all available information
                    result["error"] = (
                        f"Command '{command}' failed with exit code {return_code}. "
                        f"STDOUT: {stdout_text[:200] if stdout_text else '(empty)'}, "
                        f"STDERR: {stderr_text[:200] if stderr_text else '(empty)'}"
                    )
                logger.info(f"🔴 [TERMINAL] Final error message for failed command: {result['error'][:200]}")
                print(f"[ERROR] [TERMINAL] Final error message for failed command: {result['error'][:200]}")

            # FINAL SAFETY CHECK: Ensure error_msg is never None or empty for failed commands
            if not success:
                if not error_msg or error_msg.strip() == "":
                    logger.error(f"🔴 [TERMINAL] FINAL SAFETY CHECK FAILED: error_msg is empty! Exit code: {return_code}")
                    print(f"[ERROR] [TERMINAL] FINAL SAFETY CHECK FAILED: error_msg is empty! Exit code: {return_code}")
                    # Last resort - generate minimal error message
                    error_msg = f"Command '{command}' failed with exit code {return_code}"
                    if return_code == 1 or return_code == 9009 or return_code == -1:
                        error_msg = f"Command not found or failed to execute: '{command}'. Exit code: {return_code}. The program may not be installed or not in PATH."
                    elif return_code == 2:
                        error_msg = f"Command syntax error or file not found: '{command}'. Exit code: {return_code}"
                    logger.error(f"🔴 [TERMINAL] FINAL SAFETY CHECK: Set error_msg to: {error_msg[:200]}")
                    print(f"[ERROR] [TERMINAL] FINAL SAFETY CHECK: Set error_msg to: {error_msg[:200]}")
            
            # Always log the result clearly
            if success:
                logger.info(f"✅ [TERMINAL] SUCCESS - exit_code: {process.returncode}, command: {command}")
                print(f"[OK] [TERMINAL] ════════════════════════════════════════════════════")
                print(f"[OK] [TERMINAL] ✅ COMMAND SUCCEEDED")
                print(f"[OK] [TERMINAL] Command: {command}")
                print(f"[OK] [TERMINAL] Exit Code: {process.returncode}")
                if stdout_text.strip():
                    logger.info(f"✅ [TERMINAL] Output: {stdout_text.strip()[:200]}")
                    print(f"[OK] [TERMINAL] Output:\n{stdout_text.strip()[:500]}")
                print(f"[OK] [TERMINAL] ════════════════════════════════════════════════════")
            else:
                logger.error(f"🔴 [TERMINAL] FAILED - exit_code: {process.returncode}, command: {command}")
                print(f"[ERROR] [TERMINAL] ════════════════════════════════════════════════════")
                print(f"[ERROR] [TERMINAL] ❌ COMMAND FAILED")
                print(f"[ERROR] [TERMINAL] Command: {command}")
                print(f"[ERROR] [TERMINAL] Exit Code: {process.returncode}")
                logger.error(f"🔴 [TERMINAL] Error message (length: {len(error_msg)}): {error_msg[:500]}")
                print(f"[ERROR] [TERMINAL] Error (length: {len(error_msg)}): {error_msg[:500]}")
                if stdout_text.strip():
                    print(f"[ERROR] [TERMINAL] STDOUT: {stdout_text.strip()[:500]}")
                if stderr_text.strip():
                    print(f"[ERROR] [TERMINAL] STDERR: {stderr_text.strip()[:500]}")
                print(f"[ERROR] [TERMINAL] ════════════════════════════════════════════════════")
            
            # LOG FINAL STATE before returning
            logger.info(f"🔍 [TERMINAL] FINAL STATE - success: {success}, exit_code: {return_code}, error_msg length: {len(error_msg)}, error_msg value: {repr(error_msg[:200])}")
            print(f"[DEBUG] [TERMINAL] FINAL STATE - success: {success}, exit_code: {return_code}, error_msg length: {len(error_msg)}, error_msg: {repr(error_msg[:200])}")
            
            # FINAL VALIDATION: Ensure all required fields exist and error is never empty for failures
            required_fields = ["success", "stdout", "stderr", "exit_code", "command", "error", "cwd"]
            missing_fields = [field for field in required_fields if field not in result]
            if missing_fields:
                logger.error(f"🔴 [TERMINAL] CRITICAL: Missing required fields: {missing_fields}")
                print(f"[ERROR] [TERMINAL] CRITICAL: Missing required fields: {missing_fields}")
                for field in missing_fields:
                    if field == "success":
                        result[field] = return_code == 0
                    elif field == "exit_code":
                        result[field] = return_code
                    elif field == "error":
                        result[field] = "" if success else f"Command failed with exit code {return_code}"
                    elif field == "command":
                        result[field] = display_command
                    elif field == "cwd":
                        result[field] = cwd_str if 'cwd_str' in locals() else cwd
                    else:
                        result[field] = ""
            
            # CRITICAL: Final check - error must NEVER be empty for failed commands
            if not result.get('success', True):
                if not result.get('error') or result.get('error', '').strip() == '':
                    logger.error(f"🔴 [TERMINAL] CRITICAL VALIDATION FAILED: Command failed but error is empty! Setting emergency error message.")
                    print(f"[ERROR] [TERMINAL] CRITICAL VALIDATION FAILED: Command failed but error is empty! Setting emergency error message.")
                    result['error'] = (
                        f"CRITICAL: Command '{result.get('command', command)}' failed with exit code {result.get('exit_code', return_code)} "
                        f"but no error message was captured. This is a bug. "
                        f"STDOUT: {result.get('stdout', '')[:100] if result.get('stdout') else '(empty)'}, "
                        f"STDERR: {result.get('stderr', '')[:100] if result.get('stderr') else '(empty)'}"
                    )
                    logger.error(f"🔴 [TERMINAL] Emergency error message set: {result['error'][:200]}")
                    print(f"[ERROR] [TERMINAL] Emergency error message set: {result['error'][:200]}")
            
            logger.info(f"🔍 [TERMINAL] Final result dict keys: {list(result.keys())}")
            logger.info(f"🔍 [TERMINAL] Final result - success: {result['success']}, exit_code: {result['exit_code']}, error: {repr(result['error'])[:100]}")
            print(f"[DEBUG] [TERMINAL] Final result - success: {result['success']}, exit_code: {result['exit_code']}, error: {repr(result['error'])[:100]}")
            print(f"[DEBUG] [TERMINAL] Full result: {json.dumps({k: str(v)[:100] for k, v in result.items()})}")
            
            return result

        except Exception as e:
            logger.error(f"🔴 [TERMINAL] Command execution error: {e}", exc_info=True)
            print(f"[ERROR] [TERMINAL] Command execution error: {e}")
            import traceback
            traceback.print_exc()
            return {
                "success": False,
                "error": str(e),
                "stdout": "",
                "stderr": str(e),
                "exit_code": 1,
                "command": command,
                "cwd": cwd_str if 'cwd_str' in locals() else cwd,
            }

    async def _run_background(self, command: str, cwd: str) -> Dict[str, Any]:
        """Run command in background and capture initial output (including port info)"""
        logger.info(f"Starting background process: {command} in cwd: {cwd}")

        try:
            # Check if cwd exists (resolve path to handle relative paths)
            cwd_path = Path(cwd) if cwd else self.workspace_path
            if not cwd_path.is_absolute():
                cwd_path = self.workspace_path / cwd_path
            
            cwd_str = str(cwd_path.resolve())
            
            if cwd and not Path(cwd_str).exists():
                error_msg = f"Directory does not exist: {cwd_str}"
                logger.error(f"🔴 [TERMINAL] {error_msg}")
                return {
                    "success": False,
                    "error": error_msg,
                    "command": command,
                    "cwd": cwd_str
                }
            
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=cwd_str,
            )

            process_id = str(uuid.uuid4())[:8]
            bg_process = BackgroundProcess(process_id, process, command)
            self.background_processes[process_id] = bg_process

            # Start output collection task
            asyncio.create_task(self._collect_output(process_id))

            logger.info(f"Background process started with ID: {process_id}")
            
            # Wait briefly to capture initial output (especially for dev servers that print port info)
            is_dev_server = any(keyword in command.lower() for keyword in [
                "npm run dev", "npm start", "npm run start", "uvicorn", "flask run", "vite"
            ])
            
            initial_output = ""
            if is_dev_server:
                logger.info(f"🔄 [TERMINAL] Dev server detected in background mode, waiting for initial output...")
                print(f"[INFO] [TERMINAL] Waiting for dev server startup output...")
                
                # Wait up to 8 seconds for initial output, checking every 0.5 seconds
                import time
                start_time = time.time()
                max_wait = 8
                
                while time.time() - start_time < max_wait:
                    await asyncio.sleep(0.5)
                    
                    # Check if we have any output yet
                    current_output = "\n".join(bg_process.output_lines)
                    if current_output.strip():
                        # Check if we found port/URL info
                        if any(indicator in current_output.lower() for indicator in [
                            'localhost:', 'http://', '127.0.0.1:', 'listening on', 
                            'running at', 'ready in', 'local:', 'network:', 'port'
                        ]):
                            # Wait a bit more for complete output
                            await asyncio.sleep(1)
                            initial_output = "\n".join(bg_process.output_lines)
                            logger.info(f"✅ [TERMINAL] Captured dev server startup output ({len(initial_output)} chars)")
                            print(f"[OK] [TERMINAL] Found dev server URL/port info")
                            break
                    
                    # Check if process exited unexpectedly
                    if process.returncode is not None:
                        initial_output = "\n".join(bg_process.output_lines)
                        logger.warning(f"⚠️ [TERMINAL] Background process exited with code {process.returncode}")
                        return {
                            "success": False,
                            "process_id": process_id,
                            "command": command,
                            "stdout": initial_output,
                            "stderr": "",
                            "exit_code": process.returncode,
                            "error": f"Process exited unexpectedly with code {process.returncode}",
                            "message": f"Background process failed",
                        }
                
                # Get final captured output
                if not initial_output:
                    initial_output = "\n".join(bg_process.output_lines)
                
                if initial_output.strip():
                    initial_output = initial_output.rstrip() + f"\n\n✅ Development server is running in background (PID: {process.pid}, ID: {process_id})"
                else:
                    initial_output = f"Development server starting in background (PID: {process.pid}, ID: {process_id})\n(No startup output captured yet - server may take longer to start)"

            return {
                "success": True,
                "process_id": process_id,
                "command": command,
                "stdout": initial_output,
                "stderr": "",
                "exit_code": 0,
                "pid": process.pid,
                "message": f"Background process started: {process_id}",
            }

        except Exception as e:
            logger.error(f"Background process error: {e}")
            return {
                "success": False,
                "error": str(e),
                "command": command,
            }

    async def _collect_output(self, process_id: str):
        """Collect output from background process"""
        bg_process = self.background_processes.get(process_id)
        if not bg_process:
            return

        try:
            # Collect stdout
            while True:
                line = await bg_process.process.stdout.readline()
                if not line:
                    break
                bg_process.output_lines.append(
                    line.decode("utf-8", errors="replace").strip()
                )

            # Wait for process to complete
            await bg_process.process.wait()
            bg_process.is_running = False

            logger.info(f"Background process {process_id} completed")

        except Exception as e:
            logger.error(f"Error collecting output for {process_id}: {e}")
            bg_process.is_running = False

    def get_background_output(self, process_id: str) -> Dict[str, Any]:
        """Get output from background process"""
        bg_process = self.background_processes.get(process_id)
        if not bg_process:
            return {"success": False, "error": f"Process {process_id} not found"}

        return {
            "success": True,
            "process_id": process_id,
            "command": bg_process.command,
            "is_running": bg_process.is_running,
            "output": "\n".join(bg_process.output_lines),
        }

    async def kill_background(self, process_id: str) -> Dict[str, Any]:
        """Kill a background process"""
        bg_process = self.background_processes.get(process_id)
        if not bg_process:
            return {"success": False, "error": f"Process {process_id} not found"}

        try:
            bg_process.process.kill()
            await bg_process.process.wait()
            bg_process.is_running = False

            logger.info(f"Killed background process: {process_id}")

            return {
                "success": True,
                "process_id": process_id,
                "message": f"Process {process_id} killed",
            }

        except Exception as e:
            logger.error(f"Error killing process {process_id}: {e}")
            return {"success": False, "error": str(e)}
