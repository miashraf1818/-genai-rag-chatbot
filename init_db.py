import sys
import os

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.database.connection import init_db

if __name__ == "__main__":
    print("🔧 Initializing database...")
    init_db()
    print("✅ Done! Database is ready.")
