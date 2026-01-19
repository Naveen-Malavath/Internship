"""
Startup script for Web UI
Runs both backend and frontend
"""

import subprocess
import sys
import time
from pathlib import Path

def start_backend():
    """Start FastAPI backend server"""
    print("🚀 Starting backend server...")
    
    # Use virtual environment Python
    venv_python = Path(__file__).parent / "env" / "Scripts" / "python.exe"
    python_cmd = str(venv_python) if venv_python.exists() else sys.executable
    
    backend = subprocess.Popen(
        [python_cmd, "-m", "uvicorn", "src.web.server:app", "--reload", "--port", "8000"],
        cwd=Path(__file__).parent
    )
    return backend

def start_frontend():
    """Start React frontend dev server"""
    print("🎨 Starting frontend dev server...")
    frontend = subprocess.Popen(
        ["npm", "run", "dev"],
        cwd=Path(__file__).parent / "frontend",
        shell=True
    )
    return frontend

def main():
    print("=" * 60)
    print("🤖 AI Coding Agent - Web UI")
    print("=" * 60)
    print("\n")
    
    backend = start_backend()
    time.sleep(2)  # Wait for backend to start
    
    frontend = start_frontend()
    
    print("\n" + "=" * 60)
    print("✅ Servers are running!")
    print("=" * 60)
    print("\n📍 Backend API: http://localhost:8000")
    print("📍 Frontend UI: http://localhost:5173")
    print("\n💡 Press Ctrl+C to stop both servers\n")
    
    try:
        backend.wait()
    except KeyboardInterrupt:
        print("\n\n🛑 Shutting down servers...")
        backend.terminate()
        frontend.terminate()
        print("👋 Bye!")

if __name__ == "__main__":
    main()
