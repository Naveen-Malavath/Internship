"""Simple test to check if server imports work"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from src.web.server import app
    print("✅ Server imports successfully!")
    print(f"✅ App created: {app}")
except Exception as e:
    print(f"❌ Error importing server: {e}")
    import traceback
    traceback.print_exc()
