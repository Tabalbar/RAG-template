from fastapi import FastAPI, HTTPException, UploadFile, File, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import os
import tempfile
import shutil
from pathlib import Path

# Handle both relative and absolute imports
try:
    from .settings import Settings
    from .documents.embeddings import ChromaDBManager
    from .documents.document_processor import DocumentProcessor
except ImportError:
    from settings import Settings
    from documents.embeddings import ChromaDBManager
    from documents.document_processor import DocumentProcessor

# Initialize FastAPI app
app = FastAPI(
    title="House Finance Document API",
    description="API for managing and searching financial documents using ChromaDB",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
config = Settings()
chroma_manager = ChromaDBManager()
doc_processor = DocumentProcessor("financial")

# Pydantic models for API
class SearchQuery(BaseModel):
    query: str = Field(..., description="Search query text")
    n_results: int = Field(default=5, ge=1, le=50, description="Number of results to return")
    include_metadata: bool = Field(default=True, description="Include document metadata in results")

class SearchResult(BaseModel):
    id: str
    content: str
    score: float
    metadata: Optional[Dict[str, Any]] = None

class SearchResponse(BaseModel):
    query: str
    results: List[SearchResult]
    total_results: int

class DocumentInfo(BaseModel):
    filename: str
    size: int
    chunks_created: int
    metadata: Dict[str, Any]

class IngestionResponse(BaseModel):
    success: bool
    message: str
    documents: List[DocumentInfo]

class CollectionStats(BaseModel):
    collection_name: str
    document_count: int
    embedding_model: str
    embedding_dimensions: int

# API Endpoints

@app.get("/", summary="Health Check")
async def root():
    """Health check endpoint"""
    return {
        "message": "House Finance Document API",
        "status": "healthy",
        "embedding_model": config.embedding_model,
        "embedding_provider": config.embedding_provider
    }

@app.get("/stats", response_model=CollectionStats, summary="Get Collection Statistics")
async def get_stats():
    """Get statistics about the document collection"""
    try:
        stats = chroma_manager.get_collection_stats()
        return CollectionStats(
            collection_name=stats["collection_name"],
            document_count=stats["document_count"],
            embedding_model=stats["embedding_model"],
            embedding_dimensions=stats["embedding_dimensions"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting stats: {str(e)}")

@app.post("/search", response_model=SearchResponse, summary="Search Documents")
async def search_documents(search_query: SearchQuery):
    """Search for documents using semantic similarity"""
    try:
        results = chroma_manager.query_documents(
            query_text=search_query.query,
            n_results=search_query.n_results
        )
        
        search_results = []
        for i, (doc_id, content, score, metadata) in enumerate(zip(
            results["ids"][0],
            results["documents"][0],
            results["distances"][0],
            results["metadatas"][0] if search_query.include_metadata else [None] * len(results["ids"][0])
        )):
            search_results.append(SearchResult(
                id=doc_id,
                content=content,
                score=1 - score,  # Convert distance to similarity score
                metadata=metadata if search_query.include_metadata else None
            ))
        
        return SearchResponse(
            query=search_query.query,
            results=search_results,
            total_results=len(search_results)
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching documents: {str(e)}")

@app.post("/upload", response_model=IngestionResponse, summary="Upload and Process Documents")
async def upload_documents(files: List[UploadFile] = File(...)):
    """Upload and process documents for ingestion into ChromaDB"""
    if not files:
        raise HTTPException(status_code=400, detail="No files provided")
    
    temp_dir = None
    try:
        # Create temporary directory
        temp_dir = tempfile.mkdtemp()
        temp_path = Path(temp_dir)
        
        # Save uploaded files
        saved_files = []
        for file in files:
            if not file.filename:
                continue
                
            file_path = temp_path / file.filename
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            saved_files.append(file_path)
        
        if not saved_files:
            raise HTTPException(status_code=400, detail="No valid files to process")
        
        # Process documents
        all_chunks = []
        document_info = []
        
        for file_path in saved_files:
            try:
                chunks = doc_processor.process_document(file_path)
                all_chunks.extend(chunks)
                
                # Get file info
                file_stats = file_path.stat()
                doc_info = DocumentInfo(
                    filename=file_path.name,
                    size=file_stats.st_size,
                    chunks_created=len(chunks),
                    metadata=chunks[0].metadata if chunks else {}
                )
                document_info.append(doc_info)
                
            except Exception as e:
                print(f"Error processing {file_path.name}: {e}")
                continue
        
        if not all_chunks:
            raise HTTPException(status_code=400, detail="No content could be extracted from files")
        
        # Add to ChromaDB
        chroma_manager.add_document_chunks(all_chunks)
        
        return IngestionResponse(
            success=True,
            message=f"Successfully processed {len(document_info)} documents with {len(all_chunks)} chunks",
            documents=document_info
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing documents: {str(e)}")
    
    finally:
        # Clean up temporary directory
        if temp_dir and os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)

@app.post("/ingest-directory", response_model=IngestionResponse, summary="Ingest Documents from Directory")
async def ingest_directory(directory_path: str = Query(..., description="Path to directory containing documents")):
    """Ingest all documents from a specified directory"""
    try:
        if not os.path.exists(directory_path):
            raise HTTPException(status_code=404, detail="Directory not found")
        
        if not os.path.isdir(directory_path):
            raise HTTPException(status_code=400, detail="Path is not a directory")
        
        # Process all documents in directory
        all_chunks = []
        document_info = []
        errors = []
        
        files_found = list(Path(directory_path).glob("*"))
        print(f"DEBUG: Found {len(files_found)} files in directory: {directory_path}")
        
        for file_path in files_found:
            if file_path.is_file():
                print(f"DEBUG: Processing file: {file_path}")
                try:
                    chunks = doc_processor.process_document(file_path)
                    print(f"DEBUG: Created {len(chunks)} chunks from {file_path.name}")
                    all_chunks.extend(chunks)
                    
                    # Get file info
                    file_stats = file_path.stat()
                    doc_info = DocumentInfo(
                        filename=file_path.name,
                        size=file_stats.st_size,
                        chunks_created=len(chunks),
                        metadata=chunks[0].metadata if chunks else {}
                    )
                    document_info.append(doc_info)
                    
                except Exception as e:
                    error_msg = f"Error processing {file_path.name}: {str(e)}"
                    print(f"DEBUG: {error_msg}")
                    errors.append(error_msg)
                    continue
        
        if not all_chunks:
            error_detail = f"No content could be extracted from directory. Errors: {errors}" if errors else "No content could be extracted from directory. No supported files found."
            raise HTTPException(status_code=400, detail=error_detail)
        
        # Add to ChromaDB
        print(f"DEBUG: Adding {len(all_chunks)} chunks to ChromaDB")
        success = chroma_manager.add_document_chunks(all_chunks)
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to add documents to ChromaDB")
        
        return IngestionResponse(
            success=True,
            message=f"Successfully processed {len(document_info)} documents with {len(all_chunks)} chunks",
            documents=document_info
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error ingesting directory: {str(e)}")

@app.delete("/reset", summary="Reset Collection")
async def reset_collection():
    """Reset the document collection (delete all documents)"""
    try:
        chroma_manager.reset_collection()
        return {"message": "Collection reset successfully", "success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error resetting collection: {str(e)}")

@app.get("/documents/{document_id}", summary="Get Document by ID")
async def get_document(document_id: str):
    """Get a specific document by its ID"""
    try:
        # Query for specific document ID
        results = chroma_manager.collection.get(ids=[document_id])
        
        if not results["ids"]:
            raise HTTPException(status_code=404, detail="Document not found")
        
        return {
            "id": results["ids"][0],
            "content": results["documents"][0],
            "metadata": results["metadatas"][0] if results["metadatas"] else None
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting document: {str(e)}")

# Run the server
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 