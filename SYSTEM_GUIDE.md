# SYSTEM_GUIDE.md — Feature Deep Dives

> **Audience:** Developers, evaluators, and contributors who want to understand the *mechanics* behind three core intelligence features.
> Cross-reference with `TECHNICAL_REFERENCE.md` for full architecture and `README.md` for setup.

---

## Table of Contents

1. [High Risk Subject Breakdown](#1-high-risk-subject-breakdown)
2. [Natural Language Query (NLQ)](#2-natural-language-query-nlq)
3. [Node (Entity) Breakdown](#3-node-entity-breakdown)

---

## 1. High Risk Subject Breakdown

### 1.1 What It Is

The **Key Players** panel in the dashboard ranks suspects by a composite risk score (0–10). It answers: *"Who in this criminal network is most dangerous and central—and why?"*

This is not a black-box ML model. It is a deliberately **explainable formula** combining four quantifiable factors, so every score can be justified to investigators and in court.

---

### 1.2 The Multi-Factor Risk Formula

```
Risk Score = (Centrality × 0.30) + (Connections × 0.30) + (Anomalies × 0.20) + (Base × 0.20)
```

| Factor | Weight | What It Captures |
|:---|:---:|:---|
| **Centrality** | 30% | Graph-algorithmic importance (PageRank score, scaled 0–1) |
| **Connections** | 30% | Normalised raw degree (number of links, scaled 0–1 across all nodes) |
| **Anomalies** | 20% | Count of flagged suspicious behaviours (night calls, smurfing, etc.) |
| **Base Risk** | 20% | Static factor for confirmed entity type (Person nodes get highest base) |

Final score is multiplied by 10 for the dashboard display (e.g., `0.73 → 7.3`).

---

### 1.3 The Four Centrality Metrics

All four are computed by **NetworkX** after the full graph is built from FIRs, CDR, and financial data.

#### PageRank (Primary Ranking Signal)
- **Algorithm:** Google's PageRank adapted for criminal networks.
- **What it finds:** Nodes that are *linked to by many well-connected nodes* — the "kingpins" who may have few visible connections but occupy critical network positions.
- **Analogy:** A criminal who rarely makes calls himself but every active gang member calls him ranks higher.
- **Edge weights:** Call frequency and transaction amounts amplify the PageRank signal.

#### Betweenness Centrality
- **Algorithm:** Fraction of shortest paths (across all node pairs) that pass through a node.
- **What it finds:** **Bridge nodes** — people or phones that connect otherwise separate clusters. Removing a high-betweenness node would fragment the network.
- **Analogy:** A courier who moves between the Mumbai Cartel and the UP Ring without belonging to either.
- **Range:** 0 (peripheral) → 1 (on every shortest path).

#### Closeness Centrality
- **Algorithm:** Inverse of average shortest path length from a node to all others.
- **What it finds:** Nodes that can **reach the rest of the network quickly** — coordinators and message-relay hubs.
- **Analogy:** A logistics coordinator at the geographic centre of a drug distribution ring.
- **Range:** 0 (isolated) → 1 (can reach every other node in 1 hop).

#### Degree Centrality
- **Algorithm:** Normalised count of direct edges.
- **What it finds:** Raw **connection volume** — useful for identifying phones used as hubs.
- **Range:** 0 → 1 (connected to every other node).

---

### 1.4 Worked Calculation Example

```
Entity: "Vikram" (Person node)

Step 1 — PageRank:
  Raw PageRank from NetworkX = 0.089
  Normalised across all nodes (max = 0.12): centrality_score = 0.089 / 0.12 = 0.742

Step 2 — Connections:
  Degree = 14 edges
  Normalised (max degree in network = 20): conn_score = 14 / 20 = 0.70

Step 3 — Anomalies:
  3 night-hour calls flagged in CDR
  anomaly_score = min(3 / 5, 1.0) = 0.60    ← capped at 1.0

Step 4 — Base Risk:
  Entity type = Person → base_risk = 1.0

Risk = (0.742 × 0.30) + (0.70 × 0.30) + (0.60 × 0.20) + (1.0 × 0.20)
     = 0.2226 + 0.21 + 0.12 + 0.20
     = 0.7526

Dashboard display: 0.7526 × 10 = 7.5
```

---

### 1.5 Anomaly Detection (The 20% Factor)

CDR and financial anomalies that increment the anomaly count:

**CDR Anomalies (from `data_loaders.py`)**
| Anomaly | Definition |
|:---|:---|
| Night calls | Calls made between 01:00–04:00 (operational window criminals avoid police scrutiny) |
| Call burst | >10 calls to different numbers within a 30-minute window |
| Frequent contact | Same two numbers calling each other >15 times |

**Financial Anomalies (from `data_loaders.py`)**
| Anomaly | Definition |
|:---|:---|
| Smurfing | Transactions just below ₹10,00,000 (₹10L) — the reporting threshold |
| Rapid cascading | Same money transferred through 3+ accounts within 24 hours |
| Odd-hour transfer | High-value transfers between 23:00–05:00 |
| Round-tripping | Funds returned to originating account within 48 hours |

---

### 1.6 Louvain Community Detection (Syndicate Scoring)

**Algorithm:** Louvain modularity optimisation (randomised, multi-pass).

**Cohesion Score Formula:**
```
cohesion_score = internal_edges / (internal_edges + external_edges)
```
- `1.0` = fully isolated syndicate (no contact with outside network)
- `0.0` = every edge crosses to a different community
- Typical syndicates score `0.55–0.85`

**Dashboard display:** Syndicates listed by member count; cohesion shown as decimal (e.g., `0.73 Cohesion`).

---

## 2. Natural Language Query (NLQ)

### 2.1 What It Is

The **Query Bar** (`QueryBar.jsx` → `/api/query`) lets investigators type free-text questions about the network and get filtered, relevant answers without knowing entity IDs or graph terminology.

---

### 2.2 Three-Step Processing Pipeline

```
Input text
    │
    ▼
Step 1: Intent Detection        — What entity type does the user want?
    │
    ▼
Step 2: Entity Matching         — Which node(s) in the graph match keywords?
    │
    ▼
Step 3: Filtered Neighbor Fetch — List that node's connections, filtered by intent
    │
    ▼
Structured response with entity names, types, and match count
```

---

### 2.3 Intent Detection — Keyword-to-Entity-Type Map

The system reads every word in the query and maps known terms to entity type filters. Multiple keywords can be matched; results are de-duplicated.

```python
# From backend/main.py → /api/query
intent_filters = {
    # → BankAccount filter
    'account':     ['BankAccount'],
    'bank':        ['BankAccount'],
    'money':       ['BankAccount'],
    'transaction': ['BankAccount'],
    'transfer':    ['BankAccount'],
    'hawala':      ['BankAccount'],

    # → Person filter
    'person':      ['Person'],
    'people':      ['Person'],
    'suspect':     ['Person'],
    'criminal':    ['Person'],
    'who':         ['Person'],
    'accused':     ['Person'],
    'driver':      ['Person'],
    'owner':       ['Person'],

    # → Vehicle filter
    'vehicle':     ['Vehicle'],
    'car':         ['Vehicle'],
    'bike':        ['Vehicle'],
    'auto':        ['Vehicle'],
    'plate':       ['Vehicle'],
    'registration':['Vehicle'],

    # → Location filter
    'location':    ['Location'],
    'place':       ['Location'],
    'city':        ['Location'],
    'area':        ['Location'],
    'district':    ['Location'],

    # → Case filter
    'case':        ['Case'],
    'fir':         ['Case'],
    'complaint':   ['Case'],
    'crime':       ['Case']
}
```

**No matched keyword → no filter applied** → all neighbor types returned.

---

### 2.4 Query Examples with Expected Behaviour

| Query | Detected Intent | Filter Applied | Returns |
|:---|:---|:---|:---|
| `"What accounts link to Vikram?"` | `account` | BankAccount | Only bank accounts connected to Vikram |
| `"Who drove the vehicle MH02AB1234?"` | `who` | Person | Only Person nodes connected to that vehicle |
| `"What cases mention Ranjit?"` | `case` | Case | Only Case nodes connected to Ranjit |
| `"Show all hawala connections"` | `hawala` | BankAccount | BankAccount neighbours of matched node |
| `"List suspects in Mumbai"` | `suspect, city` | Person, Location | Person & Location neighbours |
| `"Show connections for 9876543210"` | *(none)* | None | All entity types returned |

---

### 2.5 Entity Matching Logic

```python
# Tokenise query, skip tokens ≤ 2 chars (noise)
keywords = query.split()
for entity in app_state.entities:
    entity_name = entity.name.lower()
    for keyword in keywords:
        if len(keyword) > 2 and keyword in entity_name:
            matches.append(entity)
```

- Matching is **substring-based** (not exact), so `"vikram"` matches `"Vikram Singh"`.
- First matched entity is used for the neighbor-fetch step.
- Up to 5 unique entity names shown in the response text.

---

### 2.6 Limitations and V2 Improvements

| V1 Limitation | V2 Plan |
|:---|:---|
| Substring keyword match (case-insensitive only) | Groq LLM for semantic intent parsing |
| First matched entity used (may be wrong) | Ranked entity disambiguation |
| No multi-hop queries | Dijkstra path between two queried entities |
| No date/time filtering | Temporal filtering in query |

---

## 3. Node (Entity) Breakdown

### 3.1 Entity Type Catalogue

The graph contains 8 entity types. Each represents a real-world investigative object extracted from FIRs, CDR, or financial data.

| Type | Source | What It Represents |
|:---|:---|:---|
| **Person** | FIR NLP extraction | Named individual (accused, witness, complainant) |
| **Phone** | FIR text + CDR | Mobile number (Indian 10-digit or +91 format) |
| **Vehicle** | FIR text | Registered vehicle (plate number, Indian format) |
| **BankAccount** | FIR text + transactions CSV | Bank account or IFSC code |
| **Location** | FIR text | Named place, city, or district |
| **Case** | FIR metadata | FIR / case identifier |
| **Organization** | FIR NLP extraction | Named company, gang, or institution |
| **Crime** | FIR text | IPC section or offence type |

---

### 3.2 Visual Representation (Graph Canvas)

```javascript
// From frontend/src/components/GraphCanvas.jsx
const ENTITY_COLORS = {
  Person:      '#ef4444',   // Crimson Red
  Phone:       '#06b6d4',   // Cyan
  Vehicle:     '#f59e0b',   // Amber
  BankAccount: '#10b981',   // Emerald Green
  Location:    '#a855f7',   // Purple
  Case:        '#3b82f6',   // Blue
  Organization:'#ec4899',   // Pink
  Crime:       '#dc2626'    // Dark Red
};
```

**Node Sizing (radius in pixels):**
| Entity Type | Radius | Rationale |
|:---|:---:|:---|
| Person | 8 | Largest — key investigative subject |
| BankAccount | 6 | Medium — financial hubs are important |
| All others | 4 | Standard — supporting evidence nodes |

**Additional visual cues:**
- **Node glow intensity**: proportional to PageRank centrality score (brighter = more central)
- **Edge thickness**: proportional to relationship weight (call frequency / transaction amount)
- **Edge colour**: varies by relationship type (call = blue, transaction = green, co-accused = red)

---

### 3.3 Relationship (Edge) Types

| Edge Label | Between Entities | Data Source | Weight Attribute |
|:---|:---|:---|:---|
| `CALLED` | Phone ↔ Phone | CDR CSV | Call frequency count |
| `OWNS_PHONE` | Person → Phone | FIR NLP | Confidence score |
| `TRANSFERRED_TO` | BankAccount → BankAccount | Transactions CSV | Transfer amount (₹) |
| `OWNS_VEHICLE` | Person → Vehicle | FIR NLP | Confidence score |
| `OWNS_ACCOUNT` | Person → BankAccount | FIR NLP | Confidence score |
| `LOCATED_IN` | Person → Location | FIR NLP | Confidence score |
| `LINKED_TO_CASE` | Person → Case | FIR NLP | Confidence score |
| `CO_ACCUSED` | Person ↔ Person | FIR NLP | Co-occurrence count |
| `MEMBER_OF` | Person → Organization | FIR NLP | Confidence score |

---

### 3.4 Node Metadata (Inspector Panel)

Clicking any node opens the **Node Inspector** with:

```json
{
  "id": "entity-uuid",
  "label": "Vikram Singh",
  "type": "Person",
  "metadata": {
    "aliases": ["Vikku", "V. Singh"],
    "confidence": 0.92,
    "risk_score": 7.5,
    "connections": 14,
    "community_id": 2,
    "centrality": {
      "pagerank": 0.089,
      "betweenness": 0.34,
      "degree": 0.70
    }
  }
}
```

---

### 3.5 NLP Extraction Patterns (How Nodes Are Created)

Entities are extracted from raw FIR text by regex in `backend/extraction.py`:

| Entity Pattern | Example Match |
|:---|:---|
| Indian mobile: `[6-9]\d{9}` | `9876543210` |
| Vehicle plate: `[A-Z]{2}\d{2}[A-Z]{1,2}\d{4}` | `MH02AB1234` |
| Aadhaar: `\d{4}\s\d{4}\s\d{4}` | `1234 5678 9012` |
| PAN: `[A-Z]{5}\d{4}[A-Z]` | `ABCDE1234F` |
| IFSC: `[A-Z]{4}0[A-Z0-9]{6}` | `SBIN0001234` |
| IPC Section: `Section\s+\d+[A-Z]?` | `Section 302`, `Section 420A` |

**3-Tier Entity Resolution** then deduplicates across FIRs before graph insertion:

```
Tier 1 — Hard Anchor : same phone / vehicle / account number → guaranteed same entity
Tier 2 — Fuzzy Match : RapidFuzz ≥ 88% on name → likely same person (alias handling)
Tier 3 — Graph Context: share 2+ common neighbours → inferred same entity
```

---

### 3.6 Synthetic Dataset Node Counts (V1 Demo Data)

The `synthetic_data/` directory ships with pre-built data for 4 fictional criminal rings:

| Gang | Primary Members | Communication Channel |
|:---|:---|:---|
| Mumbai Cartel | 3 persons, 2 phones, 1 vehicle | Night calls 1–4 AM |
| UP Ring | 2 persons, 1 phone, 2 bank accounts | Smurfing transactions |
| Hawala Network | 4 persons, 3 bank accounts | Rapid cascading transfers |
| Interstate Smuggling | 2 persons, 1 vehicle, 1 phone | Cross-district location overlap |

**Data volume:**
- CDR records: **2,848 call pairs**
- Financial transactions: **105 records**
- FIR documents: **5 (.txt files)**
- Expected node count after resolution: **~40–60 unique entities**

---

*End of SYSTEM_GUIDE.md*
