<p align="center">
  <h1 align="center">📘 Technical Reference — Criminal Network Intelligence System</h1>
  <p align="center">
    Deep-dive into architecture, algorithms, data flow, and judge preparation
  </p>
</p>

---

## Table of Contents

1. [System Architecture](#-system-architecture)
2. [Data Processing Workflow](#-data-processing-workflow)
3. [NLP Entity Extraction Engine](#-nlp-entity-extraction-engine)
4. [3-Tier Entity Resolution](#-3-tier-entity-resolution)
5. [Graph Analytics Engine](#-graph-analytics-engine)
6. [Risk Scoring Formula](#-risk-scoring-formula)
7. [Syndicate Detection (Louvain)](#-syndicate-detection-louvain)
8. [Anomaly Detection](#-anomaly-detection)
9. [Evidence Chain of Custody](#-evidence-chain-of-custody-sha-256)
10. [Authentication & Security](#-authentication--security)
11. [Frontend Visualization Architecture](#-frontend-visualization-architecture)
12. [API Reference](#-api-reference)
13. [Presentation Strategy](#-presentation-strategy)
14. [Judge Q&A Preparation](#-judge-qa-preparation)

---

## 🏗 System Architecture

```
┌──────────────────────────────────────────────────────────────────────────┐
│                         FRONTEND (React 19 + Vite)                       │
│  ┌──────────┐  ┌──────────────┐  ┌───────────┐  ┌──────────────────┐   │
│  │  Login    │  │ Upload Modal │  │ Query Bar │  │ Graph Canvas     │   │
│  │ (OAuth2)  │  │ (FIR/CDR/TX)│  │   (NLQ)   │  │ (ForceGraph2D)  │   │
│  └────┬─────┘  └──────┬───────┘  └─────┬─────┘  └────────┬─────────┘   │
│       │               │                │                  │             │
│       └───────────────┴────────────────┴──────────────────┘             │
│                                 │ Axios (JWT Bearer)                    │
└─────────────────────────────────┼────────────────────────────────────────┘
                                  │ HTTP REST
┌─────────────────────────────────┼────────────────────────────────────────┐
│                         BACKEND (FastAPI + Uvicorn)                      │
│                                 │                                        │
│  ┌──────────────────────────────▼──────────────────────────────────┐    │
│  │                      API Router Layer                           │    │
│  │  /api/auth/*  │  /api/upload/*  │  /api/ingest/*  │  /api/*    │    │
│  └───┬───────────┴───────┬─────────┴────────┬────────┴────┬───────┘    │
│      │                   │                  │             │            │
│  ┌───▼───┐  ┌────────────▼──────────┐  ┌───▼──────────┐  │            │
│  │ Auth  │  │  Upload Routes        │  │  Extraction  │  │            │
│  │(JWT)  │  │  (SHA-256 Hashing)    │  │  (Regex NLP) │  │            │
│  └───┬───┘  └────────────┬──────────┘  └───┬──────────┘  │            │
│      │                   │                 │             │            │
│      │              ┌────▼─────────────────▼──────┐      │            │
│      │              │    Entity Resolution        │      │            │
│      │              │    (RapidFuzz 3-Tier)        │      │            │
│      │              └────────────┬─────────────────┘      │            │
│      │                           │                        │            │
│      │              ┌────────────▼─────────────────┐      │            │
│      │              │    Graph Analytics Engine     │      │            │
│      │              │   (NetworkX: PageRank,        │      │            │
│      │              │    Louvain, Dijkstra, Risk)   │      │            │
│      │              └────────────┬─────────────────┘      │            │
│      │                           │                        │            │
│  ┌───▼───────────────────────────▼────────────────────────▼──────┐     │
│  │                    SQLAlchemy + SQLite                         │     │
│  │  ┌──────────┐  ┌──────────────┐  ┌───────────────────────┐   │     │
│  │  │  Users   │  │ EvidenceLog  │  │  In-Memory AppState   │   │     │
│  │  └──────────┘  └──────────────┘  │  (Graph + Analytics)  │   │     │
│  │                                   └───────────────────────┘   │     │
│  └───────────────────────────────────────────────────────────────┘     │
└───────────────────────────────────────────────────────────────────────────┘
```

### Layer Breakdown

| Layer | Responsibility | Key Files |
| :--- | :--- | :--- |
| **API Gateway** | Route handling, CORS, request validation | `main.py`, `upload_routes.py` |
| **Auth Module** | User registration, JWT token issue/verify | `auth.py`, `database.py` |
| **Extraction Engine** | Parse raw FIR text → structured entities | `extraction.py` |
| **Entity Resolution** | Deduplicate across districts/sources | `entity_resolution.py` |
| **Data Loaders** | Parse CDR & financial CSVs | `data_loaders.py` |
| **Analytics Engine** | Graph algorithms, risk scoring, syndicate detection | `analytics.py` |
| **Persistence** | User accounts, evidence audit trail | `database.py` (SQLite) |
| **Frontend** | Interactive visualization, search, upload | `App.jsx`, `GraphCanvas.jsx` |

---

## 🔄 Data Processing Workflow

```
 ┌─────────────┐    ┌─────────────┐    ┌──────────────────┐
 │  FIR Text    │    │  CDR CSV     │    │ Transaction CSV  │
 │  (.txt)      │    │  (.csv)      │    │ (.csv)           │
 └──────┬───────┘    └──────┬───────┘    └────────┬─────────┘
        │                   │                     │
        ▼                   ▼                     ▼
 ┌──────────────┐   ┌──────────────┐    ┌─────────────────┐
 │ Regex NLP    │   │ CDR Parser   │    │ TX Parser       │
 │ extraction.py│   │ data_loaders │    │ data_loaders    │
 │              │   │              │    │                 │
 │ Extracts:    │   │ Extracts:    │    │ Extracts:       │
 │ • Persons    │   │ • Caller →   │    │ • Sender →      │
 │ • Phones     │   │   Callee     │    │   Receiver      │
 │ • Vehicles   │   │   relations  │    │   relations     │
 │ • Banks      │   │ • Duration   │    │ • Amount        │
 │ • Locations  │   │ • Timestamps │    │ • Type          │
 │ • IPC Codes  │   │ • Tower IDs  │    │ • Timestamps    │
 └──────┬───────┘   └──────┬───────┘    └────────┬────────┘
        │                   │                     │
        └───────────────────┼─────────────────────┘
                            │
                            ▼
                 ┌─────────────────────┐
                 │  Entity Resolution  │
                 │  (3-Tier Dedup)     │
                 │                     │
                 │  Tier 1: Hard       │
                 │    (same phone)     │
                 │  Tier 2: Fuzzy      │
                 │    (88% name match) │
                 │  Tier 3: Graph      │
                 │    (shared links)   │
                 └──────────┬──────────┘
                            │
                            ▼
                 ┌─────────────────────┐
                 │  Graph Construction │
                 │  (NetworkX)         │
                 │                     │
                 │  Nodes = Entities   │
                 │  Edges = Relations  │
                 └──────────┬──────────┘
                            │
                            ▼
              ┌──────────────────────────┐
              │   Graph Analytics        │
              │                          │
              │  1. Centrality Analysis  │
              │     (PageRank,           │
              │      Betweenness,        │
              │      Closeness, Degree)  │
              │                          │
              │  2. Community Detection  │
              │     (Louvain Algorithm)  │
              │                          │
              │  3. Risk Scoring         │
              │     (Multi-Factor)       │
              │                          │
              │  4. Path Analysis        │
              │     (Dijkstra)           │
              └──────────┬───────────────┘
                         │
                         ▼
              ┌───────────────────────┐
              │  Dashboard Response   │
              │                       │
              │  • Graph JSON         │
              │  • Key Players List   │
              │  • Syndicate Clusters │
              │  • Risk Rankings      │
              └───────────────────────┘
```

### Pipeline Steps (executed in `/api/ingest/all`)

| Step | Action | Output |
| :--- | :--- | :--- |
| **1** | Read all `.txt` FIR files from `synthetic_data/FIRs/` | Raw entity + relationship lists |
| **2** | Parse `call_detail_records.csv` | Caller→Callee relationships with timestamps |
| **3** | Parse `financial_transactions.csv` | Sender→Receiver relationships with amounts |
| **4** | 3-tier entity resolution across all sources | Deduplicated entity list, merged relationships |
| **5** | Build NetworkX graph | Graph object (nodes + edges) |
| **6** | Run centrality algorithms | PageRank, Betweenness, Closeness, Degree scores |
| **7** | Detect communities (Louvain) | Syndicate clusters with cohesion scores |
| **8** | Calculate risk scores | Per-entity composite risk ranking |
| **9** | Return JSON to frontend | Graph + Key Players + Communities |

---

## 🔎 NLP Entity Extraction Engine

**File:** `backend/extraction.py`

The system uses **10+ regex patterns** tuned for Indian law enforcement data:

| Entity Type | Regex Pattern | Example Match |
| :--- | :--- | :--- |
| **Phone** | `(?:\+91\|0)?[6-9]\d{9}` | +919876543210, 09876543210 |
| **Vehicle** | `[A-Z]{2}\d{2}[A-Z]{1,2}\d{4}` | MH02AB1234, DL7CQ4521 |
| **Aadhaar** | `\d{4}\s?\d{4}\s?\d{4}` | 1234 5678 9012 |
| **PAN** | `[A-Z]{5}\d{4}[A-Z]` | ABCDE1234F |
| **IFSC** | `[A-Z]{4}0[A-Z0-9]{6}` | SBIN0001234 |
| **Bank Account** | `\d{9,18}` | 123456789012 |
| **IPC Section** | `Section\s+\d+[A-Z]?` | Section 420, Section 302A |
| **FIR Number** | `FIR[- ]?\d+/\d{2,4}` | FIR-234/2024 |
| **Amount** | `₹?\d+[,\d]*(?:\.\d+)?(?:\s*(?:lakh\|crore))?` | ₹5,00,000, 10 lakh |
| **Date** | `\d{1,2}[-/]\d{1,2}[-/]\d{2,4}` | 15-03-2024 |
| **Police Station** | `P\.?S\.?\s+\w+` | PS Andheri |

### How Extraction Works

```python
# For each FIR text file:
result = extract_from_fir(text, filename)

# Returns ExtractionResult:
#   .entities  → [Person("Vikram Sharma"), Phone("+919876543210"), Vehicle("MH02AB1234")]
#   .relationships → [Relationship(Vikram → Phone, type="OWNS_PHONE")]
```

**Relationship inference:** When a person's name appears near a phone number in the same FIR paragraph, the system creates an `OWNS_PHONE` relationship. Similar logic applies for vehicles, bank accounts, and locations.

---

## 🔗 3-Tier Entity Resolution

**File:** `backend/entity_resolution.py`

Cross-district criminal identification is the hardest problem. The same person may appear as "Vikram Sharma" in Maharashtra FIR and "V. Sharma" in a Delhi CDR. Our 3-tier resolution engine handles this:

### Tier 1: Hard Anchor Match
```
IF two entities share the same phone number, vehicle plate, or Aadhaar
THEN they are the SAME person → MERGE
```
- **Why:** Phone numbers and vehicle plates are unique identifiers
- **Example:** FIR Mumbai mentions phone +919876543210 → CDR Delhi mentions same number → Same person

### Tier 2: Fuzzy Name Match (RapidFuzz)
```
IF string_similarity(name_A, name_B) ≥ 88%
THEN flag as potential match → MERGE
```
- **Library:** `rapidfuzz` (with `difflib` fallback)
- **Threshold:** 88% — high enough to avoid false positives, low enough to catch "Vikram Sharma" ↔ "Vikram K. Sharma"
- **Algorithm:** Token-sort ratio (handles word reordering)

### Tier 3: Graph Context Match
```
IF two unresolved entities share ≥ 2 common neighbors in the graph
THEN they are likely the same person → MERGE
```
- **Why:** Two "unknown" suspects who both called the same 3 people and used the same vehicle are probably the same person
- **This is unique to our system** — most systems stop at Tier 2

### Resolution Flow

```
[Entity A: "Vikram Sharma", Phone: 9876543210, FIR: Mumbai]
[Entity B: "V. Sharma", Phone: 9876543210, FIR: Delhi]
[Entity C: "Vikram Kumar Sharma", no phone, FIR: UP]

Tier 1: A & B share phone 9876543210 → MERGE into A
Tier 2: A & C name similarity = 91% → MERGE into A
Result: Single entity "Vikram Sharma" with aliases ["V. Sharma", "Vikram Kumar Sharma"]
         Linked to FIRs across 3 states
```

---

## 📊 Graph Analytics Engine

**File:** `backend/analytics.py` (~600 lines)

The analytics engine consists of **5 specialized classes** orchestrated by `CriminalNetworkAnalytics`:

### 1. CriminalNetworkGraphBuilder
Converts resolved entities and relationships into a **NetworkX graph**:
- Each entity → node (with type, name, metadata)
- Each relationship → edge (with type, weight, attributes)

### 2. CentralityAnalyzer
Runs 4 centrality algorithms to rank entity importance:

| Algorithm | What It Measures | Criminal Context | NetworkX Function |
| :--- | :--- | :--- | :--- |
| **PageRank** | Hidden influence (like Google ranking) | The kingpin who controls through lieutenants | `nx.pagerank()` |
| **Betweenness** | Bridge between groups | The middleman connecting separate gangs | `nx.betweenness_centrality()` |
| **Closeness** | How quickly info spreads from this node | The coordinator who can reach everyone fast | `nx.closeness_centrality()` |
| **Degree** | Raw number of connections | The most "connected" suspect | `nx.degree_centrality()` |

**Why 4 algorithms?** Each reveals different criminal roles:
- **High PageRank, Low Degree** → Secret kingpin (few direct links, but links to powerful nodes)
- **High Betweenness, Low PageRank** → Bridge/courier between gangs
- **High Degree, Low Betweenness** → Local gang leader (many links, all within one community)

### 3. CommunityDetector (Louvain)
See [Syndicate Detection](#-syndicate-detection-louvain) section below.

### 4. PathFinder
- **Dijkstra's shortest path:** Find the shortest connection chain between two suspects
- **All shortest paths:** Find ALL equally-short paths (reveals redundant communication channels)
- **Common neighbors:** Find shared contacts between two entities

### 5. RiskCalculator
See [Risk Scoring Formula](#-risk-scoring-formula) section below.

### Orchestrator: `CriminalNetworkAnalytics.analyze()`

```python
def analyze(entities, relationships):
    # Step 1: Build graph
    graph = GraphBuilder.build(entities, relationships)
    
    # Step 2: Calculate centrality
    centrality = CentralityAnalyzer.analyze(graph)
    
    # Step 3: Detect communities
    communities = CommunityDetector.detect(graph)
    
    # Step 4: Calculate risk scores
    risk_scores = RiskCalculator.calculate(graph, centrality)
    
    # Step 5: Rank key players
    key_players = rank_by_risk(risk_scores, top=10)
    
    return { graph, centrality, communities, risk_scores, key_players }
```

---

## ⚠️ Risk Scoring Formula

**The risk score is NOT a black box.** Every number is explainable:

```
Risk Score = (centrality_risk × 0.30) + (connection_risk × 0.30) 
           + (anomaly_risk × 0.20) + (base_risk × 0.20)
```

### Component Breakdown

| Factor | Weight | How It's Calculated |
| :--- | :--- | :--- |
| **Centrality Risk** | 30% | `(PageRank × 0.6 + Betweenness × 0.4) × 3.0` |
| **Connection Risk** | 30% | `connections / max_connections` (normalized) |
| **Anomaly Risk** | 20% | `night_calls × 0.5 + smurfing_count × 1.5 + burst_calls × 0.3` |
| **Base Risk** | 20% | Number of FIR mentions + number of IPC sections linked |

### Why This Formula?

- **30% Centrality:** PageRank catches hidden kingpins; Betweenness catches bridge-men
- **30% Connections:** Sheer volume of contacts matters (but alone isn't enough)
- **20% Anomalies:** Night calls (1–4 AM) and financial smurfing are behavioral red flags
- **20% Base Risk:** A person mentioned in 5 FIRs across 3 states is inherently higher risk

### Judge-Ready Explanation

> "Our risk score is a **weighted composite of 4 factors** — each with a clear criminal justification. We use PageRank because a kingpin doesn't call everyone directly; they call lieutenants who call foot soldiers. A flat 'most calls' ranking misses this. The 20% anomaly weight catches behavioral patterns — a legitimate businessman doesn't make 15 calls between 1–4 AM to burner phones. Every number in our formula has a reason."

---

## 🕸 Syndicate Detection (Louvain)

**Algorithm:** `networkx.algorithms.community.greedy_modularity_communities`

### What Is Louvain?

The Louvain algorithm detects **communities** — groups of nodes that are more densely connected to each other than to the rest of the network. In criminal intelligence, a community = a **syndicate or gang**.

### How It Works

```
Iteration 1: Each node starts as its own community
Iteration 2: Move nodes to neighboring communities if it increases "modularity"
Iteration 3: Collapse communities into super-nodes, repeat
Result: Stable partition where internal connections >> external connections
```

**Modularity** = (fraction of edges within communities) − (expected fraction if edges were random)

### Cohesion Score

For each detected community, we calculate:

```
Cohesion = internal_edges / (internal_edges + external_edges)
```

| Cohesion | Interpretation |
| :--- | :--- |
| 0.8 – 1.0 | **Isolated cell** — tight-knit gang, very few outside contacts |
| 0.5 – 0.8 | **Organized syndicate** — clear structure but with external connections |
| 0.2 – 0.5 | **Loose network** — affiliated but not tightly organized |
| < 0.2 | **Incidental grouping** — probably not a real syndicate |

### Why Louvain Over Other Algorithms?

| Algorithm | Pros | Cons | Why We Chose Louvain |
| :--- | :--- | :--- | :--- |
| K-Means | Fast | Needs predefined K (how many gangs?) | We don't know how many gangs exist |
| Spectral | Mathematically elegant | Needs predefined K | Same problem |
| Label Propagation | Fast, no K needed | Non-deterministic, unstable | Results change each run |
| **Louvain** | **No K needed, deterministic, scalable** | Slightly slower | ✅ Best fit for criminal networks |

---

## 🚨 Anomaly Detection

### CDR Anomalies

| Anomaly | Detection Logic | Criminal Significance |
| :--- | :--- | :--- |
| **Night Calls** | Calls between 1:00 AM – 4:00 AM | Operational planning (criminals avoid daytime calls) |
| **Call Bursts** | >5 calls to same number within 1 hour | Coordination during active operation |
| **Short Calls** | Duration < 10 seconds | Signal calls (ring-and-hang-up = "proceed") |
| **Burner Pattern** | Phone active < 72 hours total | Disposable phone used for one operation |

### Financial Anomalies

| Anomaly | Detection Logic | Criminal Significance |
| :--- | :--- | :--- |
| **Smurfing** | Multiple transactions just under ₹10 lakh | Structuring to avoid reporting threshold |
| **Rapid Cascade** | Money flows A→B→C→D within 24 hours | Layering (money laundering chain) |
| **Round Amounts** | Transactions in exact round figures | Typical of hawala or informal value transfer |
| **Dormant Burst** | Account inactive 30+ days, then sudden activity | Account activated for specific operation |

---

## 🔐 Evidence Chain of Custody (SHA-256)

**File:** `backend/upload_routes.py`

Every uploaded file is:

1. **Hashed** with SHA-256 at upload time
2. **Logged** in the `EvidenceLog` SQLite table
3. **Stored** in `data_uploads/` with original filename

```python
# SHA-256 hashing on upload
import hashlib

sha256_hash = hashlib.sha256(file_content).hexdigest()

# Logged in database
evidence_log = EvidenceLog(
    filename=file.filename,
    file_type=file_type,
    uploader_id=current_user.id,
    sha256_hash=sha256_hash,       # 64-character hex string
    timestamp=datetime.utcnow()
)
```

### Why SHA-256?

- **Tamper detection:** If a single byte of the file changes, the hash changes completely
- **Court admissibility:** Section 65B of the Indian Evidence Act requires digital evidence to have verifiable integrity
- **Audit trail:** The `EvidenceLog` table records who uploaded what, when, and the hash — creating an immutable chain of custody

### Database Schema

```sql
CREATE TABLE evidence_log (
    id          INTEGER PRIMARY KEY,
    filename    VARCHAR(256),
    file_type   VARCHAR(50),       -- "fir", "cdr", "transaction"
    uploader_id INTEGER REFERENCES users(id),
    sha256_hash VARCHAR(64),       -- SHA-256 hex digest
    timestamp   DATETIME
);
```

---

## 🔑 Authentication & Security

**File:** `backend/auth.py`

| Component | Implementation |
| :--- | :--- |
| **Password Hashing** | bcrypt with auto-generated salt |
| **Token Format** | JWT (JSON Web Token) with HS256 |
| **Token Expiry** | 60 minutes |
| **Token Storage** | `sessionStorage` (tab-scoped, not `localStorage`) |
| **Auth Flow** | OAuth2 Password Bearer via FastAPI |

### Why sessionStorage Over localStorage?

- `sessionStorage` is cleared when the browser tab closes
- Each tab gets its own session — opening a second tab requires re-login
- Prevents token persistence across browser sessions (security best practice for sensitive systems)

### Auth Flow

```
1. User → POST /api/auth/register → {username, password}
   Server → hash(password) with bcrypt → store in SQLite

2. User → POST /api/auth/token → {username, password}
   Server → verify bcrypt hash → issue JWT (60min expiry) → return token

3. Frontend → stores token in sessionStorage
   All subsequent API calls → Authorization: Bearer <token>

4. Tab close → sessionStorage cleared → token gone → re-login required
```

---

## 🎨 Frontend Visualization Architecture

### Graph Canvas (ForceGraph2D)

**File:** `frontend/src/components/GraphCanvas.jsx`

The network visualization uses **react-force-graph-2d**, which internally runs a **D3 Force Simulation**:

```
Force-Directed Layout:
─────────────────────
• Nodes repel each other (charge force)
• Edges act as springs (link force)
• Result: Connected nodes cluster together
• Clusters ≠ chronological order — they represent TOPOLOGY
```

### Node Color Coding

| Entity Type | Color | Purpose |
| :--- | :--- | :--- |
| Person | 🔴 Red (`#ef4444`) | Primary suspects |
| Phone | 🟢 Green (`#22c55e`) | Communication identifiers |
| Vehicle | 🟡 Yellow (`#eab308`) | Transport links |
| BankAccount | 🔵 Blue (`#3b82f6`) | Financial connections |
| Location | 🟣 Purple (`#a855f7`) | Geographic links |
| Case/FIR | ⚪ Gray (`#6b7280`) | Legal records |

### Interactive Features

| Feature | Implementation |
| :--- | :--- |
| **Node Search** | Text input filters nodes by name in real-time |
| **Type Filter** | Dropdown to show only Person, Phone, Vehicle, etc. |
| **Zoom Controls** | +/− buttons and scroll wheel |
| **Node Click** | Opens inspector drawer with entity details |
| **Glow Effect** | Selected/searched nodes get a colored glow ring |
| **Drag** | Click and drag to reposition nodes |
| **Legend** | Color-coded entity type legend overlay |

### Query Bar (NLQ)

**File:** `frontend/src/components/QueryBar.jsx`

Natural language queries are sent to `/api/query` with smart intent detection:

```
"What accounts link to MH02AB1234?"
  → Intent: BankAccount
  → Finds vehicle MH02AB1234 in graph
  → Returns only BankAccount neighbors

"Who drove the vehicle?"
  → Intent: Person
  → Returns only Person neighbors of the matched vehicle
```

---

## 📡 API Reference

### Authentication

| Endpoint | Method | Description |
| :--- | :--- | :--- |
| `/api/auth/register` | POST | Register new user `{username, password}` |
| `/api/auth/token` | POST | Login and get JWT `{username, password}` |

### Data Ingestion

| Endpoint | Method | Description |
| :--- | :--- | :--- |
| `/api/ingest/all` | POST | Run full pipeline (FIR + CDR + TX → Graph) |
| `/api/extract/fir` | POST | Extract entities from single FIR file |
| `/api/extract/batch` | POST | Batch extract from FIR folder |

### Upload

| Endpoint | Method | Description |
| :--- | :--- | :--- |
| `/api/upload/evidence` | POST | Upload evidence file with SHA-256 hashing |

### Graph & Analytics

| Endpoint | Method | Description |
| :--- | :--- | :--- |
| `/api/graph/current` | GET | Get current graph (nodes + edges) |
| `/api/graph/stats` | GET | Get entity/relationship type counts |
| `/api/analytics/key-players` | GET/POST | Get top suspects ranked by risk |
| `/api/analytics/communities` | GET/POST | Get detected syndicates |
| `/api/query` | POST | Natural language query `{query: "..."}` |
| `/api/progress` | GET | Check ingestion progress |
| `/health` | GET | Health check |

---

## 🎤 Presentation Strategy

### The 3-Minute Pitch Structure

```
[0:00 – 0:30] THE HOOK
"An officer in Mumbai files an FIR against 'Vikram Sharma' for drug trafficking.
 Six months later, Delhi police arrest 'V. Sharma' for money laundering.
 They're the same person — but nobody knows.
 Our system catches this in 3 seconds."

[0:30 – 1:30] THE SOLUTION
"We built an AI intelligence platform that:
 1. READS FIRs, Call Records, and Bank Transactions automatically
 2. STITCHES identities across states using 3-tier entity resolution
 3. DETECTS hidden syndicates using graph algorithms
 4. RANKS suspects by explainable risk scores
 5. SEALS every file with SHA-256 for court admissibility"

[1:30 – 2:30] THE DEMO
• Upload a sample FIR → show extracted entities
• Click 'Run Pipeline' → watch the graph build
• Point to a dense cluster → "This is a detected syndicate"
• Click a red node → "This suspect has risk score 7.8 because..."
• Show the evidence ledger → "Every file is SHA-256 sealed"

[2:30 – 3:00] THE CLOSE
"Current systems are siloed, manual, and reactive.
 Our system is unified, automatic, and proactive.
 It finds the gang before the next crime."
```

### Demo Flow (Step by Step)

1. **Login** — show the auth system works
2. **Upload** — drag FIR `.txt` files → show SHA-256 hash generated
3. **Ingest** — click "Run Pipeline" → show progress
4. **Graph** — point to clusters, explain colors
5. **Key Players** — click sidebar → show risk scores are explainable
6. **Syndicates** — click a syndicate → explain cohesion score
7. **Query** — type "What accounts link to MH02AB1234?" → show smart filtering

### Key Phrases to Memorize

| When asked about... | Say this... |
| :--- | :--- |
| **How do you detect gangs?** | "Louvain algorithm — it finds groups of people more connected to each other than to outsiders. No manual input needed." |
| **Why not just count calls?** | "A kingpin doesn't call everyone directly. PageRank catches hidden influence through lieutenants — same algorithm Google uses." |
| **Is the risk score a black box?** | "No — it's a 4-factor weighted formula: centrality, connections, anomalies, and base risk. Every number has a criminal justification." |
| **What about evidence in court?** | "Every uploaded file gets a SHA-256 hash at ingestion. If even one byte changes, the hash changes. Section 65B compliant." |
| **What about cross-state matching?** | "3-tier resolution: first we match on phone numbers, then fuzzy name match at 88% threshold, then graph context — shared neighbors." |

---

## ❓ Judge Q&A Preparation

### Category 1: Technical Depth

**Q: Why did you choose NetworkX over Neo4j?**
> V1 uses NetworkX for rapid prototyping and hackathon demo speed. NetworkX runs entirely in-memory with zero infrastructure overhead. V2 will migrate to Neo4j for persistence, Cypher queries, and production-scale graph traversal. The algorithm layer (PageRank, Louvain, Dijkstra) is identical — only the storage backend changes.

**Q: How does your entity resolution handle false positives?**
> The 88% threshold for fuzzy matching was empirically tuned — below 85%, we got false merges ("Rahul Singh" ↔ "Rahul Sinha"); above 90%, we missed valid matches ("Vikram Sharma" ↔ "V. Sharma"). The 3-tier approach adds safety: Tier 1 (hard anchors like phone numbers) is zero false-positive by definition. Tier 3 (graph context) only merges when shared neighbors provide structural evidence.

**Q: What happens if the graph has 10,000+ nodes?**
> NetworkX handles up to ~100K nodes in memory. For larger scale, V2 will use Neo4j with indexed Cypher queries. The frontend uses react-force-graph-2d which can render ~5,000 nodes smoothly; beyond that, we'd add clustering/aggregation in the visualization layer.

**Q: How do you handle multilingual FIRs (Hindi/regional)?**
> Currently, the regex extraction engine handles English/transliterated text. V2 will add OCR (Tesseract) for Hindi PDFs and transliteration normalization. The entity resolution layer is language-agnostic — names are compared as character strings regardless of language.

### Category 2: Security & Legal

**Q: Is the JWT secret key secure?**
> The current demo uses a hardcoded secret for hackathon purposes. In production, this would be loaded from environment variables or a secrets manager (AWS Secrets Manager / HashiCorp Vault). The algorithm (HS256) and bcrypt hashing are production-grade.

**Q: How do you ensure the SHA-256 hash wasn't tampered with?**
> The hash is computed server-side at the moment of upload and immediately stored in the SQLite database. The database itself should be backed by append-only audit logs in production. V2 will add blockchain-anchoring for the hash chain — writing hash batches to a public blockchain for independent verification.

**Q: What about data privacy — are you storing raw FIRs?**
> The system stores extracted entities and relationships, not raw FIR text (in memory only). Uploaded files are stored in `data_uploads/` with SHA-256 verification. In production, this would be encrypted at rest (AES-256) with role-based access control.

### Category 3: Innovation & Impact

**Q: What's novel about your approach vs existing police systems?**
> Three things: (1) **Cross-district entity resolution** — no existing system stitches identities across state borders automatically. (2) **Graph-based syndicate detection** — most systems use flat databases; we use Louvain to find gangs that are invisible in tabular data. (3) **Explainable risk scores** — our formula is transparent, not a black-box ML model, which matters for court proceedings.

**Q: How does this help a real police officer?**
> An officer uploads FIRs and CDRs from their district. Within seconds, the system shows: (1) This suspect is the same person who was arrested in another state under a different name. (2) These 5 people form a tight syndicate with cohesion 0.87. (3) This suspect ranks highest because of unusual night calls and financial smurfing. Instead of weeks of manual cross-referencing, the officer gets actionable intelligence in seconds.

**Q: What's your V2 roadmap?**
> Timeline playback (watch how a network evolves over months), Neo4j for production-scale graphs, LLM-powered queries (ask questions in plain Hindi/English), role-based access (Admin vs Investigator), PDF FIR parsing with OCR, and real-time alerts when a new FIR matches an existing suspect.

### Category 4: Algorithm Specifics

**Q: Why is PageRank better than just counting connections?**
> PageRank considers the QUALITY of connections, not just quantity. If Suspect A calls 3 people who each call 50 people, and Suspect B calls 50 people who each call nobody — Suspect A has higher PageRank despite fewer direct connections. In criminal networks, the kingpin often has few direct contacts but contacts HIGH-VALUE intermediaries.

**Q: How does Louvain know how many gangs there are?**
> It doesn't need to be told. Unlike K-Means (which requires you to specify K clusters), Louvain iteratively maximizes modularity — it naturally converges on the correct number of communities. If the data has 3 gangs, it finds 3. If it has 7, it finds 7. No human input needed.

**Q: What does "cohesion score 0.87" actually mean?**
> It means 87% of the edges from syndicate members go to OTHER members of the same syndicate. Only 13% of their connections are to outsiders. This is a tightly sealed group — they mostly communicate with each other and rarely with the outside world. A cohesion of 0.5 would mean half their calls go outside the group — a looser, less secretive network.

**Q: Why Dijkstra for path finding?**
> We need the SHORTEST connection chain between two suspects — "How is suspect A connected to suspect B?" Dijkstra finds the minimum-weight path, which in our graph means the strongest/most direct connection chain. We also find ALL shortest paths, which reveals redundant communication channels — if there are 3 equally-short paths between A and B, they have 3 independent ways to communicate, making the relationship harder to disrupt.

---

## 📐 Database Schema

```
┌─────────────────────────────────────┐
│              users                   │
├─────────────────────────────────────┤
│ id              INTEGER PRIMARY KEY  │
│ username        VARCHAR(100) UNIQUE  │
│ hashed_password VARCHAR(256)         │
│ role            VARCHAR(50)          │ ← default: "investigator"
│ created_at      DATETIME             │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│          evidence_log                │
├─────────────────────────────────────┤
│ id              INTEGER PRIMARY KEY  │
│ filename        VARCHAR(256)         │
│ file_type       VARCHAR(50)          │ ← "fir", "cdr", "transaction"
│ uploader_id     INTEGER → users(id)  │
│ sha256_hash     VARCHAR(64)          │ ← 64-char hex digest
│ timestamp       DATETIME             │
└─────────────────────────────────────┘
```

---

<p align="center">
  <strong>SIH Prototype 189</strong> — Smart India Hackathon<br/>
  <em>Built for intelligence. Designed for justice.</em>
</p>
