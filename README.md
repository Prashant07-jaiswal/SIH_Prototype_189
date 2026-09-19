# SIH Prototype 189 - AI-Powered Criminal Network Analysis System

An advanced investigative intelligence platform designed to uncover syndicates, map kingpins, and trail financial anomalies in complex criminal networks. Developed for the Smart India Hackathon (SIH).

## 🚀 Overview

This system transforms unstructured investigative data (FIRs, CDRs, Transactions) into a searchable, interactive graph database to detect hidden alliances, quantify suspect risk, and maintain a tamper-proof evidence ledger using cryptographic SHA-256 hashing.

### Key Capabilities
*   **Graph Intelligence:** Louvain Modularity for syndicate detection and PageRank/Degree Centrality for kingpin identification.
*   **Explainable Risk Scoring:** Transparent, multi-factor risk scoring formula (Centrality + Case Frequency + Financial Volume).
*   **Tamper-Proof Evidence:** SHA-256 cryptographic sealing for all ingested documents, supporting Section 65B (Indian Evidence Act) digital chain of custody standards.
*   **NLP Extraction:** Automated entity extraction from unstructured police report text (FIRs) and anomalies detection in CDRs and financial transfers.

---

## 🛠️ Tech Stack

| Domain | Technlogies |
| :--- | :--- |
| **Backend** | Python, FastAPI, SQLAlchemy (SQLite), NetworkX, Pandas |
| **Frontend** | React, Vite, Tailwind CSS, react-force-graph-2d, Lucide Icons |
| **Intelligence** | NLP Extraction (Regex), Louvain Community Detection, centrality algorithms |
| **Security** | OAuth2 JWT, bcrypt, SHA-256 Evidence Ledgering |

---

## 📁 Project Structure

```text
SIH_Prototype_189/
├── backend/            # FastAPI analytics engine & data pipeline
├── frontend/           # React dashboard & graph visualization
├── synthetic_data/     # Sample FIRs, CDRs, and Financial data
└── data_uploads/       # Document persistence (internal)
```

---

## 🚀 Quick Start

### 1. Backend Setup
1. Navigate to `/backend`.
2. Ensure you have Python installed and create/activate your virtual environment (`python -m venv .venv`).
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Setup environment: `cp .env.example .env`.
5. Run the server:
   ```bash
   uvicorn main:app --reload
   ```
*   API Docs: `http://localhost:8000/docs`

### 2. Frontend Setup
1. Navigate to `/frontend`.
2. Install dependencies:
   ```bash
   npm install
   ```
3. Run the development server:
   ```bash
   npm run dev
   ```

---

## 📡 API Overview (Key Endpoints)

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/api/upload/` | Upload FIR/CDR/Transactions, compute SHA-256, seal ledger. |
| `POST` | `/api/ingest/all` | Runs full NLP extraction, resolution, and graph construction. |
| `GET` | `/api/graph/current`| Returns graph data for Force-Directed visualization. |
| `POST` | `/api/query` | Natural language network query. |
| `GET` | `/api/analytics/key-players`| Retrieves high-risk suspects. |
| `GET` | `/api/analytics/communities`| Retrieves detected criminal syndicates. |

---

## 🔒 Security & Compliance

This platform implements a mandatory **digital chain of custody**:
1. Every file submitted via local upload generates a unique **SHA-256 fingerprint**.
2. This hash is permanently stored in the SQLite `evidence_ledger`.
3. Anomaly detection flags suspicious financial patterns and communication bursts for investigator review.

For inquiries or setup help, please contact the development team.
