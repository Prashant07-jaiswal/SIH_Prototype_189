# Complete Testing Guide - Phases 1-3

## 🧪 How to Test Everything We Built

This guide walks you through testing all components step-by-step.

---

## **PART 1: Test Synthetic Dataset (Phase 1)**

### Check if data was generated correctly:

```bash
# Navigate to project
cd c:\Users\jaisw\OneDrive\Desktop\SIH_Prototype_189

# Check FIR documents
ls synthetic_data/FIRs/
# Should show: FIR_001_MH.txt, FIR_002_UP.txt, FIR_003_DL.txt, FIR_004_MH.txt, FIR_005_UP.txt

# Check CSV files
ls synthetic_data/*.csv
# Should show: call_detail_records.csv, financial_transactions.csv

# Check metadata
ls synthetic_data/metadata.json
```

### View sample FIR document:

```bash
# Read first FIR (multilingual Hindi/English mix)
cat synthetic_data/FIRs/FIR_001_MH.txt

# Expected output: 
# - FIR Number: MH/2024/12345
# - Suspects: Vikram Sharma, Ramesh Gupta
# - Phone: 9876543210
# - Vehicle: MH02AB1234
# - Hindi/Hinglish narrative text
```

### Check CDR records:

```bash
# View first 10 CDR records
head -10 synthetic_data/call_detail_records.csv

# Count total records
wc -l synthetic_data/call_detail_records.csv
# Expected: 2849 lines (2848 + header)
```

### Check financial transactions:

```bash
# View first 10 transactions
head -10 synthetic_data/financial_transactions.csv

# Count total transactions
wc -l synthetic_data/financial_transactions.csv
# Expected: 106 lines (105 + header)
```

### View metadata structure:

```bash
# View gang structure
cat synthetic_data/metadata.json

# Expected: 4 gangs (Mumbai Cartel, UP Ring, Hawala Network, Interstate)
```

✅ **Phase 1 Test: Complete** - All synthetic data generated correctly

---

## **PART 2: Test Backend Setup (Phase 2)**

### Install dependencies:

```bash
cd backend
pip install -r requirements.txt

# Expected output: Successfully installed all 18 packages
```

### Verify all modules can be imported:

```bash
python -c "from config import settings; print('✅ config.py works')"
python -c "from models import *; print('✅ models.py works')"
python -c "from extraction import EntityExtractor; print('✅ extraction.py works')"
python -c "from entity_resolution import EntityResolver; print('✅ entity_resolution.py works')"
python -c "from data_loaders import load_cdr_csv; print('✅ data_loaders.py works')"
python -c "from analytics import CriminalNetworkAnalytics; print('✅ analytics.py works')"
python -c "from main import app; print('✅ main.py works')"
```

Expected: All 7 modules print ✅

### Start FastAPI server:

```bash
# Make sure you're in backend folder
cd backend

# Start server
python main.py

# Expected output:
# INFO:     Uvicorn running on http://0.0.0.0:8000
# INFO:     Application startup complete
```

Keep this terminal open for testing.

---

## **PART 3: Test API Endpoints (Phase 2)**

Open a **new terminal** (keep backend running in first terminal)

### Test 1: Health Check

```bash
curl http://localhost:8000/health

# Expected response:
# {
#   "status": "healthy",
#   "app": "Criminal Network Analysis API",
#   "version": "0.1.0",
#   "processing": false
# }
```

### Test 2: Extract Single FIR

```bash
curl -X POST "http://localhost:8000/api/extract/fir" \
  -F "file=@../synthetic_data/FIRs/FIR_001_MH.txt"

# Expected response:
# {
#   "fir_id": "FIR_001_MH",
#   "entities": [
#     {"id": "person_vikram_sharma", "name": "Vikram Sharma", "type": "Person"},
#     {"id": "phone_9876543210", "name": "+919876543210", "type": "Phone"},
#     ...
#   ],
#   "relationships": [...],
#   "extraction_confidence": 0.90,
#   "processing_time_ms": 145
# }
```

### Test 3: Batch Extract All FIRs

```bash
curl -X POST "http://localhost:8000/api/extract/batch"

# Expected response:
# {
#   "status": "success",
#   "total_firs_processed": 5,
#   "total_entities_extracted": 60,
#   "total_entities_after_resolution": 15,
#   "total_relationships": 80,
#   "merge_metadata": {...}
# }
```

---

## **PART 4: Test Complete Pipeline (Phase 2-3)**

### Test 4: Full Data Ingestion (Runs Extraction + Analytics)

This is the **main test** - it runs everything:

```bash
curl -X POST "http://localhost:8000/api/ingest/all"

# Expected response:
# {
#   "status": "success",
#   "entities": 50,
#   "relationships": 120,
#   "merge_metadata": {...},
#   "analytics": {
#     "key_players_found": 10,
#     "communities_detected": 4,
#     "graph_nodes": 50,
#     "graph_edges": 120
#   }
# }
```

✅ This means:
- FIRs extracted → 60 entities
- Entity resolution → 15 unique persons
- CDR parsed → 40 call relationships
- Transactions parsed → 15 transfer relationships
- **Analytics run → 10 key players, 4 communities detected**

---

## **PART 5: Test Graph Analytics Endpoints (Phase 3)**

### Test 5: Get Key Players

```bash
curl http://localhost:8000/api/analytics/key-players

# Expected response:
# {
#   "status": "success",
#   "key_players": [
#     {
#       "rank": 1,
#       "entity_name": "Ramesh Bhat",
#       "centrality_score": 0.87,
#       "risk_score": 9.2,
#       "connections": 15,
#       "aliases": [],
#       "gang_affiliation": "Hawala Network",
#       "known_crimes": ["Money Laundering", "Hawala"]
#     },
#     {
#       "rank": 2,
#       "entity_name": "Mohammad Khan",
#       "centrality_score": 0.82,
#       "risk_score": 8.9,
#       "connections": 14,
#       ...
#     },
#     ...
#   ]
# }
```

✅ What this shows:
- Ramesh Bhat ranked #1 (kingpin)
- Risk score: 9.2/10
- 15 connections (calls daily)
- PageRank centrality: 0.87

### Test 6: Get Communities

```bash
curl http://localhost:8000/api/analytics/communities

# Expected response:
# {
#   "status": "success",
#   "communities": [
#     {
#       "id": 0,
#       "label": "Community 1",
#       "members": ["Vikram Sharma", "Ramesh Gupta", "Priya Desai"],
#       "member_count": 3,
#       "internal_connections": 5,
#       "external_connections": 2,
#       "cohesion_score": 0.71
#     },
#     {
#       "id": 1,
#       "label": "Community 2",
#       "members": ["Rohit Singh", "Suresh Kumar", "Akshay Patel"],
#       "member_count": 3,
#       "internal_connections": 4,
#       "external_connections": 3,
#       "cohesion_score": 0.68
#     },
#     {
#       "id": 2,
#       "label": "Community 3",
#       "members": ["Ramesh Bhat", "Mohammad Khan"],
#       "member_count": 2,
#       "internal_connections": 3,
#       "external_connections": 1,
#       "cohesion_score": 0.85
#     },
#     {
#       "id": 3,
#       "label": "Community 4",
#       "members": ["Arun Verma", "Deepak Singh"],
#       "member_count": 2,
#       "internal_connections": 2,
#       "external_connections": 2,
#       "cohesion_score": 0.72
#     }
#   ],
#   "total_communities": 4
# }
```

✅ What this shows:
- 4 communities detected (gangs)
- Community 3 (Hawala) is tightest (0.85 cohesion)
- Shows internal vs external connections

### Test 7: Get Graph Statistics

```bash
curl http://localhost:8000/api/graph/stats

# Expected response:
# {
#   "total_entities": 50,
#   "total_relationships": 120,
#   "entity_types": {
#     "Person": 15,
#     "Phone": 12,
#     "Vehicle": 5,
#     "BankAccount": 4,
#     "Location": 8,
#     "Case": 6
#   },
#   "relationship_types": {
#     "USES_PHONE": 15,
#     "CALLED": 42,
#     "TRANSFERRED": 18,
#     "ACCUSED_IN": 15,
#     "ASSOCIATE_OF": 12,
#     "OWNED_VEHICLE": 5,
#     "OPERATES_ACCOUNT": 12
#   }
# }
```

✅ What this shows:
- 50 total entities (persons, phones, accounts)
- 120 relationships (calls, transfers, etc.)
- Breakdown by type

### Test 8: Get Current Graph

```bash
curl http://localhost:8000/api/graph/current

# Expected response (large JSON):
# {
#   "nodes": [
#     {
#       "id": "person_ramesh_bhat",
#       "label": "Ramesh Bhat",
#       "type": "Person",
#       "metadata": {...}
#     },
#     ...
#   ],
#   "edges": [
#     {
#       "source": "person_ramesh_bhat",
#       "target": "phone_7654321098",
#       "label": "USES_PHONE",
#       "type": "USES_PHONE",
#       "weight": 1.0,
#       "metadata": {...}
#     },
#     ...
#   ],
#   "node_count": 50,
#   "edge_count": 120
# }
```

✅ This is the complete graph data (ready for Phase 4 frontend)

---

## **PART 6: Test Progress Endpoint**

### Test 9: Check Progress During Processing

```bash
# While ingest is running, in another terminal:
curl http://localhost:8000/api/progress

# Expected response while processing:
# {
#   "is_processing": true,
#   "progress_percent": 45
# }

# After processing complete:
# {
#   "is_processing": false,
#   "progress_percent": 100
# }
```

---

## **COMPLETE TESTING CHECKLIST**

Use this to verify everything works:

### Phase 1: Dataset ✅
- [ ] 5 FIR documents exist
- [ ] 2,848 CDR records exist
- [ ] 105 transaction records exist
- [ ] Metadata JSON exists
- [ ] Data contains multilingual text

### Phase 2: Backend ✅
- [ ] All 7 modules import successfully
- [ ] FastAPI server starts without errors
- [ ] Health endpoint returns 200
- [ ] Single FIR extraction works
- [ ] Batch extraction works
- [ ] Full ingest runs successfully

### Phase 3: Analytics ✅
- [ ] Key players endpoint returns 10 suspects
- [ ] Communities endpoint returns 4 communities
- [ ] Graph stats endpoint returns correct counts
- [ ] Graph current endpoint returns nodes + edges
- [ ] Ramesh Bhat is ranked #1 (kingpin)
- [ ] 4 communities detected automatically
- [ ] Total processing time < 1.3 seconds

---

## **EXPECTED RESULTS SUMMARY**

When everything works correctly:

```
📊 DATASET
├─ 5 FIRs (multilingual)
├─ 2,848 CDR records
├─ 105 transactions
└─ 4 criminal gangs

📡 EXTRACTION (Phase 2)
├─ 60 entities extracted
├─ 45% deduplication (60 → 15 unique persons)
└─ 80+ relationships built

📈 ANALYTICS (Phase 3)
├─ 50 nodes, 120 edges in graph
├─ 10 key players ranked
├─ 4 communities detected
├─ PageRank calculated (0.87 max)
├─ Betweenness centrality calculated
└─ Risk scores assigned (9.2/10 max)

✅ ALL TESTS PASS
```

---

## **TROUBLESHOOTING**

If something doesn't work:

### Backend won't start:
```bash
# Check Python version
python --version  # Should be 3.8+

# Reinstall dependencies
pip install --upgrade -r requirements.txt

# Check for port conflicts
netstat -an | grep 8000
```

### API returns 500 error:
```bash
# Check backend console for error messages
# Look for ImportError, SyntaxError, etc.

# Test individual modules:
python -c "from analytics import CriminalNetworkAnalytics; print('OK')"
```

### Data files not found:
```bash
# Verify paths are correct
ls synthetic_data/FIRs/
ls synthetic_data/*.csv

# Check current directory
pwd  # Should be SIH_Prototype_189 or backend folder
```

---

## **QUICK TEST (5 Minutes)**

Run this if you just want to verify everything works:

```bash
# Terminal 1: Start backend
cd backend && python main.py

# Terminal 2: Run quick tests (wait 3 seconds between commands)
sleep 3
curl http://localhost:8000/health
sleep 1
curl -X POST http://localhost:8000/api/ingest/all
sleep 2
curl http://localhost:8000/api/analytics/key-players | head -30
curl http://localhost:8000/api/analytics/communities | head -30
```

If all curl commands return JSON (not errors), everything works! ✅

---

## **COMPLETE TEST OUTPUT EXAMPLE**

Here's what successful output looks like:

```
✅ Health Check: healthy
✅ FIR Extract: 60 entities found
✅ Batch Extract: 15 unique persons after resolution
✅ Full Ingest: 50 entities, 120 relationships
✅ Key Players: Ramesh Bhat ranked #1 (9.2/10 risk)
✅ Communities: 4 communities detected
✅ Graph Stats: 50 nodes, 120 edges
✅ Processing Time: 1.1 seconds total

🎉 ALL TESTS PASS - PROTOTYPE WORKING!
```

---

Ready to test? Start with the **Quick Test** section and work your way through! 🚀
