<p align="center">
  <h1 align="center">🕵️ AI-Powered Criminal Network Analysis & Intelligence System</h1>
  <p align="center">
    <strong>SIH Prototype 189</strong> — Graph Intelligence for Law Enforcement
  </p>
  <p align="center">
    <em>Internal SIH Winner — Score: 47.67 / 50</em>
  </p>
</p>

---

## 📌 Problem Statement

Indian law enforcement generates massive volumes of **FIRs, Call Detail Records (CDRs), and financial transaction logs** across multiple districts. Criminals operate under aliases, burner phones, and layered financial networks. Current systems are:

- **Siloed:** Each district maintains separate records — the same criminal appears as a different person in Mumbai vs Delhi.
- **Manual:** Officers manually cross-reference spreadsheets, missing hidden connections.
- **Reactive:** Investigations start after crimes, instead of proactively identifying organized networks.

**There is no unified intelligence platform that can automatically stitch multi-source data, detect criminal syndicates, and rank suspects by risk — all while maintaining a tamper-proof evidence chain for court admissibility.**

---

## 💡 Our Solution

An end-to-end AI intelligence platform that:

1. **Ingests** unstructured FIR text, CDR CSVs, and financial transaction logs.
2. **Extracts** entities (persons, phones, vehicles, bank accounts) using NLP regex patterns.
3. **Resolves** duplicates across districts with 3-tier entity resolution (hard anchor → fuzzy match → graph context).
4. **Builds** a unified criminal network graph and runs graph algorithms (PageRank, Louvain, Dijkstra).
5. **Visualizes** the network as an interactive force-directed graph with syndicate detection.
6. **Seals** every uploaded document with a **SHA-256 cryptographic hash** for digital chain of custody (Section 65B, Indian Evidence Act).

---

## 🔥 Why It Matters

| Problem | Our Solution |
| :--- | :--- |
| Criminals use aliases across states | 3-tier Entity Resolution stitches them into one identity |
| Syndicates are invisible in flat databases | Louvain Algorithm automatically detects gang clusters |
| Risk assessment is subjective | Explainable multi-factor scoring formula (not a black box) |
| Evidence tampering in digital files | SHA-256 hashing creates immutable audit trail |
| Manual cross-referencing takes weeks | Automated ingestion pipeline does it in seconds |

---

## 🛠️ Tech Stack

| Layer | Technologies |
| :--- | :--- |
| **Backend** | Python 3, FastAPI, Uvicorn, Pydantic |
| **Database** | SQLAlchemy + SQLite |
| **Graph Engine** | NetworkX (PageRank, Louvain, Dijkstra, Betweenness) |
| **NLP Extraction** | Regex-based (10+ Indian patterns: Phone, Vehicle, Aadhaar, PAN, IFSC, IPC Sections) |
| **Entity Resolution** | RapidFuzz (fuzzy matching at 88% threshold) |
| **Data Processing** | Pandas, NumPy |
| **Frontend** | React 19, Vite, Tailwind CSS |
| **Graph Visualization** | react-force-graph-2d (D3 Force Simulation) |
| **Icons** | Lucide React |
| **Auth & Security** | OAuth2 + JWT (HS256), bcrypt password hashing, SHA-256 evidence sealing |

---

## 📁 Project Structure

```
SIH_Prototype_189/
├── backend/
│   ├── main.py                 # FastAPI app & API endpoints
│   ├── config.py               # Pydantic Settings configuration
│   ├── models.py               # 16+ data models (Entity, Relationship, Analytics)
│   ├── extraction.py           # NLP regex-based entity extraction from FIRs
│   ├── entity_resolution.py    # 3-tier deduplication engine
│   ├── data_loaders.py         # CDR & financial CSV parsers
│   ├── analytics.py            # Graph algorithms (PageRank, Louvain, Risk)
│   ├── auth.py                 # OAuth2 JWT authentication
│   ├── database.py             # SQLAlchemy models (Users, Evidence Ledger)
│   ├── upload_routes.py        # File upload + SHA-256 hashing
│   └── requirements.txt        # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── App.jsx             # Main dashboard (Stats, Graph, Syndicates)
│   │   ├── components/
│   │   │   ├── GraphCanvas.jsx     # Interactive force-directed network graph
│   │   │   ├── QueryBar.jsx        # Natural language query interface
│   │   │   ├── UploadModal.jsx     # Evidence upload with ingestion feedback
│   │   │   ├── Login.jsx           # Authentication UI
│   │   │   └── LocationMapView.jsx # Suspect geolocation map
│   │   └── services/
│   │       └── api.js              # Axios API client
│   └── package.json
├── synthetic_data/
│   ├── FIRs/                   # 5 sample FIR documents (MH, UP, DL)
│   ├── call_detail_records.csv # Sample CDR data
│   ├── financial_transactions.csv
│   └── metadata.json
├── data_uploads/               # Uploaded evidence persistence
├── TECHNICAL_REFERENCE.md      # Deep-dive: architecture, algorithms, judge Q&A
├── SYSTEM_GUIDE.md             # Feature deep-dives: risk scoring, NLQ, node types
└── README.md                   # ← You are here
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Node.js 18+

### 1. Backend

```bash
cd backend

# Create and activate virtual environment
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create environment file
cp .env.example .env

# Register your first user (one-time)
# POST to http://localhost:8000/api/auth/register
# Body: {"username": "admin", "password": "admin123"}

# Run the server
uvicorn main:app --reload
```

API available at **http://localhost:8000** — Swagger UI at `/docs`.

### 2. Frontend

```bash
cd frontend
npm install
npm run dev
```

Dashboard available at **http://localhost:5173**.

### 3. Login & Load Data

1. Open the dashboard → Login with your registered credentials.
2. Click **Upload Data** → Upload FIRs (.txt), CDRs (.csv), Transactions (.csv).
3. Click **Process & Build Graph** → The system extracts, resolves, and builds the network.
4. Explore the interactive graph, key players panel, and detected syndicates.

---

## 📊 Version History

| Version | Date | Features |
| :--- | :--- | :--- |
| **v1.0** | Sep 2026 | ✅ NLP entity extraction (10+ regex patterns for Indian identifiers) |
| | | ✅ 3-tier entity resolution (hard anchor → fuzzy 88% → graph context) |
| | | ✅ CDR & financial transaction parsers with anomaly detection |
| | | ✅ NetworkX graph construction with PageRank, Betweenness, Closeness, Degree centrality |
| | | ✅ Louvain community detection (syndicate identification + cohesion scoring) |
| | | ✅ Explainable composite risk scoring formula |
| | | ✅ Dijkstra shortest-path & common-neighbor queries |
| | | ✅ Interactive force-directed graph visualization (react-force-graph-2d) |
| | | ✅ Node search, type filtering, zoom controls, selection inspector |
| | | ✅ Natural language query bar |
| | | ✅ OAuth2 JWT authentication with bcrypt |
| | | ✅ Tab-scoped auto-logout (sessionStorage) |
| | | ✅ SHA-256 cryptographic evidence sealing (digital chain of custody) |
| | | ✅ SQLite persistence (Users + Evidence Ledger) |
| | | ✅ Multi-file evidence upload (FIR, CDR, Transactions) |
| | | ✅ Suspect geolocation map view |
| **v2.0** | _Upcoming_ | 🔜 Timeline playback & temporal analysis |
| | | 🔜 Neo4j graph database integration |
| | | 🔜 LLM-powered advanced query (Groq) |
| | | 🔜 Role-based access control (Admin / Investigator) |
| | | 🔜 PDF FIR parsing & OCR |
| | | 🔜 Real-time alert system |

---

## 👥 Team

**SIH Prototype 189** — Smart India Hackathon

---

## 📄 License

This project is developed as part of the Smart India Hackathon and is intended for educational and government use.
