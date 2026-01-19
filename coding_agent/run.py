"""Simple runner for the AI Coding Agent"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.main import app

if __name__ == "__main__":
    app()
