# House Finance Document RAG System

A document search and question-answering system built with ChromaDB and Google AI embeddings. Upload financial documents and ask questions about them using natural language.

## 🚀 Quick Start

### Prerequisites
- Docker installed on your system
- Google API key (for embeddings)

### 1. Clone and Setup
```bash
git clone <your-repo-url>
cd house-finance
```

### 2. Configure Environment
Create a `.env` file:
```bash
GOOGLE_API_KEY=your_google_api_key_here
CHROMA_DB_PATH=./chroma_db/data
DOCUMENTS_PATH=./output
```

### 3. Start the Server

**Option A: Using Docker (Recommended)**
```bash
docker pull tabalbar/house-of-finance:v1.0.0
docker run -d -p 8000:8000 --env-file .env tabalbar/house-of-finance:v1.0.0
```

**Option B: Local Python**
```bash
pip install -r src/requirements.txt
python src/run_api.py
```

### 4. Test the System
```bash
# Run the test client to verify everything works
python src/tests/api_client_example.py
```

The server will be available at `http://localhost:8000`

## 📖 Using the API

### Web Interface
- **API Documentation**: http://localhost:8000/docs
- **Interactive Testing**: http://localhost:8000/redoc

### Upload Documents
```bash
curl -X POST "http://localhost:8000/upload" -F "files=@your-document.pdf"
```

### Search Documents
```bash
curl -X POST "http://localhost:8000/search" \
  -H "Content-Type: application/json" \
  -d '{"query": "budget allocation for education", "n_results": 3}'
```

### Get Statistics
```bash
curl http://localhost:8000/stats
```

## 📁 Project Structure

```
house-finance/
├── src/
│   ├── api.py                    # Main FastAPI application
│   ├── run_api.py               # Server startup script
│   ├── settings.py              # Configuration
│   ├── documents/               # Document processing
│   ├── chroma_db/              # Database setup
│   └── tests/                  # Testing utilities
├── output/                     # Place your documents here
├── chroma_db/                  # Database storage
└── README.md                   # This file
```

## 🔧 Development

### Setup Database
```bash
python src/chroma_db/setup_database.py
```

### Ingest Documents
```bash
python src/documents/ingest_documents.py --source output/
```

### Run Tests
```bash
python -m pytest src/tests/
```

## 💡 Example Usage

1. **Start the server**: `python src/run_api.py`
2. **Upload a financial document** via the web interface at http://localhost:8000/docs
3. **Ask questions** like:
   - "What is the total budget allocation?"
   - "How much funding goes to education?"
   - "Show me all departments with budgets over $1 million"

## 🆘 Troubleshooting

**Server won't start?**
- Check that port 8000 is available
- Verify your Google API key is valid
- Check logs: `docker logs <container-id>`

**No search results?**
- Make sure you've uploaded documents first
- Check if documents were processed: `curl http://localhost:8000/stats`

**Need help?**
- Check the full API documentation at http://localhost:8000/docs
- Run the test client: `python src/tests/api_client_example.py`

## 📄 License

[Your License Here] 