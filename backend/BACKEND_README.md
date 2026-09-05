# FastAPI Backend - Criminal Network Analysis System

## 📁 Project Structure

```
backend/
├── __init__.py                 # Package initialization
├── config.py                   # Configuration management (Pydantic Settings)
├── models.py                   # Data models for entities, relationships, analytics
├── extraction.py               # NLP entity extraction (Regex-based)
├── entity_resolution.py        # Entity deduplication & stitching
├── data_loaders.py             # CDR and financial transaction parsers
├── main.py                     # FastAPI application & API endpoints
├── .env.example                # Environment configuration template
└── requirements.txt            # Python dependencies
```

---

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Set Up Environment

```bash
cp .env.example .env
```

### 3. Run the Server

```bash
python main.py
# Or: uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

API available at: **http://localhost:8000**
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

---

## 📡 Key API Endpoints

### Extraction
- `POST /api/extract/fir` — Extract from single FIR
- `POST /api/extract/batch` — Extract from all FIRs with entity resolution

### Data Ingestion
- `POST /api/ingest/all` — Complete pipeline (FIRs + CDR + Transactions)

### Graph Operations
- `GET /api/graph/current` — Get loaded criminal network graph
- `GET /api/graph/stats` — Get graph statistics

### Progress
- `GET /api/progress` — Get extraction progress (0-100%)
- `GET /health` — Health check

---

## 📊 Module Overview

| Module | Purpose |
|--------|---------|
| **config.py** | Pydantic Settings for env vars and configuration |
| **models.py** | Entity, Relationship, Analytics data models |
| **extraction.py** | Regex-based NLP extraction from FIR text |
| **entity_resolution.py** | 3-tier entity deduplication (hard anchor → fuzzy → graph context) |
| **data_loaders.py** | CDR & transaction CSV parsing with anomaly detection |
| **main.py** | FastAPI app with REST endpoints and state management |

---

## 🔄 Data Processing Pipeline

```
1. FIR Extraction
   Text → extract_from_fir() → Entities + Relationships
   - Phones, Vehicles, Accounts, Persons with aliases
   - Crime keywords, IPC sections, locations

2. Entity Resolution
   Raw Entities → EntityResolver.resolve() → Deduplicated Entities
   - Tier 1: Hard anchors (same phone/vehicle/account)
   - Tier 2: Fuzzy matching (88%+ name similarity)
   - Tier 3: Graph context (shared neighbors)

3. CDR Relationship Building
   call_detail_records.csv → parse_relationships_from_cdr()
   - Aggregates calls by (caller, receiver)
   - Calculates frequency, duration, night calls (1-4 AM)
   - Creates weighted CallRelationship objects

4. Financial Relationship Building
   financial_transactions.csv → parse_relationships_from_transactions()
   - Aggregates transfers by (sender_account, receiver_account)
   - Detects anomalies: smurfing, rapid cascading
   - Creates weighted TransferRelationship objects
```

---

## 🎯 Key Features

### Entity Extraction
- **10+ Regex Patterns:** Phone (+91), Vehicle (MH02AB1234), Bank Account, IFSC, Aadhaar, PAN, IPC Sections
- **Multilingual Support:** Hindi, English, Hinglish
- **Named Entity Recognition:** Persons with aliases (उर्फ़ pattern), Organizations, Locations
- **Crime Keyword Detection:** 6 categories (drug, theft, assault, fraud, money_laundering, extortion)

### Entity Resolution (Solves Multi-District Criminal Stitching)
- **Tier 1:** Same phone = Same person (100% confidence)
- **Tier 2:** Name similarity 88%+ = Merge (handles spelling variations)
- **Tier 3:** Co-occurrence matching = Suggest merge (2+ shared neighbors)

### Anomaly Detection
- **CDR Anomalies:** Night calls (1-4 AM), call bursts, long durations
- **Financial Anomalies:** Smurfing (<10L transfers), rapid cascading, odd-hour transfers

---

## 🧪 Example Usage

### Extract Single FIR
```bash
curl -X POST "http://localhost:8000/api/extract/fir" \
  -F "file=@synthetic_data/FIRs/FIR_001_MH.txt"
```

### Extract All FIRs with Resolution
```bash
curl -X POST "http://localhost:8000/api/extract/batch"
```

### Ingest All Data (3-Step Pipeline)
```bash
curl -X POST "http://localhost:8000/api/ingest/all"
```

### Get Graph
```bash
curl -X GET "http://localhost:8000/api/graph/current" | jq .
```

### Get Stats
```bash
curl -X GET "http://localhost:8000/api/graph/stats" | jq .
```

---

## 🔧 Configuration

Create `.env` file from `.env.example`:

```
DEBUG=True
GROQ_API_KEY=your_groq_key_here
DATA_DIR=./synthetic_data
ENTITY_SIMILARITY_THRESHOLD=0.88
```

---

## 📦 Dependencies

```
fastapi==0.104.1          # Web framework
uvicorn==0.24.0           # ASGI server
pydantic==2.5.0           # Data validation
pandas==2.1.3             # CSV parsing
rapidfuzz==3.5.2          # Fuzzy matching
networkx==3.2             # Graph algorithms (phase 3)
groq==0.4.3               # LLM API (future)
neo4j==5.15.0             # Graph DB (phase 3)
pytest==7.4.3             # Testing
```

---

## 🎓 Design Patterns

1. **Type Safety:** Pydantic models for all data
2. **Modularity:** Single responsibility per module
3. **Async-Ready:** Built for FastAPI async patterns
4. **Error Handling:** Try-catch with logging
5. **Testability:** Pure functions where possible

---

## 🚧 Phase 2 Status

✅ Project structure created
✅ Models defined (16 classes)
✅ Regex extraction engine (10+ patterns)
✅ Entity resolution (3-tier matching)
✅ CDR/Transaction parsers
✅ FastAPI app with 10+ endpoints
✅ Error handling & logging

**Next:** Phase 3 - Graph Analytics (NetworkX integration)
