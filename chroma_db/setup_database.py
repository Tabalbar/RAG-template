#!/usr/bin/env python3
"""
Database Setup Script for House Finance RAG System
Initializes ChromaDB and tests the embedding system
"""

import sys
import os
from pathlib import Path

# Add src directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.settings import settings, validate_settings
from src.documents.embeddings import ChromaDBManager
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def setup_database():
    """Initialize ChromaDB database and collection."""
    print("🚀 Setting up ChromaDB for Financial Document RAG System")
    print("=" * 60)
    
    try:
        # Validate configuration
        print("📋 Validating configuration...")
        validate_settings()
        print("✅ Configuration valid")
        
        # Display configuration
        print(f"📁 Database path: {settings.chroma_db_path}")
        print(f"📚 Collection name: {settings.chroma_collection_name}")
        print(f"🤖 Embedding model: {settings.embedding_model} ({settings.embedding_provider})")
        print(f"📏 Embedding dimensions: {settings.embedding_dimensions}")
        print(f"📐 Distance function: {settings.chroma_distance_function}")
        
        # Initialize ChromaDB manager
        print("\n🔧 Initializing ChromaDB...")
        manager = ChromaDBManager()
        
        # Get collection stats
        stats = manager.get_collection_stats()
        print(f"✅ ChromaDB initialized successfully!")
        print(f"📊 Collection: {stats.get('name', 'N/A')}")
        print(f"📄 Documents: {stats.get('document_count', 0)}")
        print(f"🎯 Model: {stats.get('embedding_model', 'N/A')}")
        
        # Test embedding functionality
        print("\n🧪 Testing embedding functionality...")
        test_text = "This is a test of the Google AI embedding system."
        
        # Test query (this will create embeddings)
        results = manager.query_documents(test_text, n_results=1)
        print("✅ Embedding system working correctly!")
        
        print("\n🎉 Database setup completed successfully!")
        print("=" * 60)
        print("Next steps:")
        print("1. Run: python src/documents/ingest_documents.py --source output/")
        print("2. Test queries with your financial documents")
        
        return True
        
    except Exception as e:
        print(f"❌ Setup failed: {str(e)}")
        logger.error(f"Database setup failed: {str(e)}", exc_info=True)
        return False

def reset_database():
    """Reset (clear) the ChromaDB collection."""
    print("⚠️  Resetting ChromaDB collection...")
    
    try:
        manager = ChromaDBManager()
        success = manager.reset_collection()
        
        if success:
            print("✅ Database reset successfully!")
        else:
            print("❌ Database reset failed!")
            
        return success
        
    except Exception as e:
        print(f"❌ Reset failed: {str(e)}")
        return False

def show_database_info():
    """Show database information and statistics."""
    print("📊 ChromaDB Information")
    print("=" * 40)
    
    try:
        manager = ChromaDBManager()
        stats = manager.get_collection_stats()
        
        print(f"Collection Name: {stats.get('name', 'N/A')}")
        print(f"Document Count: {stats.get('document_count', 0)}")
        print(f"Embedding Model: {stats.get('embedding_model', 'N/A')}")
        print(f"Embedding Dimensions: {stats.get('embedding_dimensions', 'N/A')}")
        print(f"Database Path: {settings.chroma_db_path}")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to get database info: {str(e)}")
        return False

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="ChromaDB setup and management")
    parser.add_argument(
        "--action", 
        choices=["setup", "reset", "info"], 
        default="setup",
        help="Action to perform (default: setup)"
    )
    
    args = parser.parse_args()
    
    if args.action == "setup":
        success = setup_database()
    elif args.action == "reset":
        success = reset_database()
    elif args.action == "info":
        success = show_database_info()
    
    sys.exit(0 if success else 1) 