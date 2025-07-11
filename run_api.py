#!/usr/bin/env python3
"""
FastAPI Server Startup Script
Launches the House Finance Document API server
"""

import sys
import os
import uvicorn
from pathlib import Path

def find_project_root():
    """Find the project root directory containing the src folder."""
    current = Path(__file__).parent
    while current != current.parent:
        if (current / "src").exists() and (current / "src" / "api.py").exists():
            return current
        current = current.parent
    raise RuntimeError("Could not find project root directory")

def main():
    """Start the FastAPI server"""
    try:
        print("🚀 Starting House Finance Document API...")
        print("📚 Loading ChromaDB and embedding models...")
        
        # Find project root and add to Python path
        project_root = find_project_root()
        sys.path.insert(0, str(project_root))
        sys.path.insert(0, str(project_root / "src"))  # Add src directory to path
        
        # Change working directory to project root
        os.chdir(project_root)
        
        # Import here to catch any configuration errors early
        from settings import Settings
        config = Settings()
        
        print(f"✅ Configuration loaded:")
        print(f"   - Documents Path: {config.documents_path}")
        print(f"   - ChromaDB Path: {config.chroma_db_path}")
        print(f"   - Collection: {config.chroma_collection_name}")
        print(f"   - Embedding Model: {config.embedding_model} ({config.embedding_provider})")
        print("=" * 60)
        
        print("\n🌐 Starting server at http://localhost:8000")
        print("📖 API Documentation: http://localhost:8000/docs")
        print("🔍 Interactive API: http://localhost:8000/redoc")
        print("\nPress Ctrl+C to stop the server\n")
        
        # Start the server
        uvicorn.run(
            "src.api:app",
            host="0.0.0.0",
            port=8000,
            reload=False,  # Disable reload to prevent import issues
            log_level="info",
            access_log=True
        )
        
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        print("💡 Make sure all dependencies are installed:")
        print("   pip install fastapi uvicorn python-multipart")
        sys.exit(1)
        
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 