#!/usr/bin/env python3
"""
Example client for the House Finance Document API
Demonstrates how to interact with the FastAPI server
"""

import requests
import json
import sys
from pathlib import Path

# API base URL
BASE_URL = "http://localhost:8000"

class DocumentAPIClient:
    """Client for interacting with the Document API"""
    
    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url.rstrip('/')
        
    def health_check(self):
        """Check if the API server is running"""
        try:
            response = requests.get(f"{self.base_url}/")
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"❌ API server not accessible: {e}")
            return None
    
    def get_stats(self):
        """Get collection statistics"""
        try:
            response = requests.get(f"{self.base_url}/stats")
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"❌ Error getting stats: {e}")
            return None
    
    def search_documents(self, query: str, n_results: int = 5, include_metadata: bool = True):
        """Search for documents"""
        try:
            payload = {
                "query": query,
                "n_results": n_results,
                "include_metadata": include_metadata
            }
            response = requests.post(f"{self.base_url}/search", json=payload)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"❌ Error searching: {e}")
            return None
    
    def ingest_directory(self, directory_path: str):
        """Ingest documents from a directory"""
        try:
            params = {"directory_path": directory_path}
            response = requests.post(f"{self.base_url}/ingest-directory", params=params)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"❌ Error ingesting directory: {e}")
            return None
    
    def upload_files(self, file_paths: list):
        """Upload files to the API"""
        try:
            files = []
            for file_path in file_paths:
                if Path(file_path).exists():
                    files.append(('files', open(file_path, 'rb')))
                else:
                    print(f"⚠️  File not found: {file_path}")
            
            if not files:
                print("❌ No valid files to upload")
                return None
            
            response = requests.post(f"{self.base_url}/upload", files=files)
            
            # Close file handles
            for _, file_handle in files:
                file_handle.close()
            
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"❌ Error uploading files: {e}")
            return None
    
    def reset_collection(self):
        """Reset the document collection"""
        try:
            response = requests.delete(f"{self.base_url}/reset")
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"❌ Error resetting collection: {e}")
            return None

def main():
    """Example usage of the API client"""
    client = DocumentAPIClient()
    
    print("🔍 House Finance Document API Client Example")
    print("=" * 50)
    
    # Health check
    print("\n1. Health Check")
    health = client.health_check()
    if health:
        print(f"✅ API Status: {health['status']}")
        print(f"📊 Embedding Model: {health['embedding_model']}")
        print(f"🏢 Provider: {health['embedding_provider']}")
    else:
        print("❌ API server is not running. Start it with: python src/run_api.py")
        return
    
    # Get stats
    print("\n2. Collection Statistics")
    stats = client.get_stats()
    if stats:
        print(f"📚 Collection: {stats['collection_name']}")
        print(f"📄 Documents: {stats['document_count']}")
        print(f"🧠 Model: {stats['embedding_model']}")
        print(f"📐 Dimensions: {stats['embedding_dimensions']}")
    
    # Example search (only if there are documents)
    if stats and stats['document_count'] > 0:
        print("\n3. Example Search")
        query = "budget allocation for education"
        print(f"🔍 Searching for: '{query}'")
        
        results = client.search_documents(query, n_results=3)
        if results:
            print(f"📊 Found {results['total_results']} results:")
            for i, result in enumerate(results['results'], 1):
                print(f"\n   Result {i} (Score: {result['score']:.3f}):")
                print(f"   ID: {result['id']}")
                print(f"   Content: {result['content'][:200]}...")
                if result['metadata']:
                    print(f"   Metadata: {json.dumps(result['metadata'], indent=6)}")
    else:
        print("\n3. No documents in collection")
        print("💡 To ingest documents, you can:")
        print("   - Use the /ingest-directory endpoint")
        print("   - Use the /upload endpoint")
        print("   - Run: python src/documents/ingest_documents.py")
    
    print("\n" + "=" * 50)
    print("🌐 API Documentation available at: http://localhost:8000/docs")
    print("🔍 Interactive API at: http://localhost:8000/redoc")

if __name__ == "__main__":
    main() 