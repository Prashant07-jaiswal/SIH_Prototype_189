# Phase 1 Complete: Synthetic Dataset Ready 🎉

## What Was Built

Generated a production-ready synthetic criminal network dataset with **realistic interconnections** across multiple law enforcement data sources:

### 📁 Dataset Contents

```
synthetic_data/
├── FIRs/
│   ├── FIR_001_MH.txt    (Mumbai - Drug Trafficking Network)
│   ├── FIR_002_UP.txt    (Uttar Pradesh - Vehicle Theft Ring)
│   ├── FIR_003_DL.txt    (Delhi - Hawala Money Laundering)
│   ├── FIR_004_MH.txt    (Thane - Weapons & Gang Activity)
│   └── FIR_005_UP.txt    (Lucknow - GST Fraud Syndicate)
├── call_detail_records.csv      (2,848 CDR records, 30 days)
├── financial_transactions.csv   (105 transaction records)
└── metadata.json                (Network structure & gang info)
```

### 🕸️ Criminal Network Structure

**4 Interconnected Gangs:**

1. **Gang A: मुंबई कार्टेल** (Mumbai Cartel)
   - Vikram Sharma, Ramesh Gupta, Priya Desai
   - Crimes: Drug Trafficking, Extortion, Money Laundering
   
2. **Gang B: उत्तर प्रदेश रिंग** (UP Criminal Ring)
   - Rohit Singh, Suresh Kumar, Akshay Patel
   - Crimes: Vehicle Theft, Highway Robbery, Forgery

3. **Gang C: हवाला नेटवर्क** (Hawala Network) ⭐ **THE HUB**
   - Ramesh Bhat (7654321098), Mohammad Khan (7123456789)
   - Crimes: Money Laundering, Hawala, Illegal Fund Transfer
   - **15 calls/day between members = highest frequency**

4. **Gang D: अंतरराज्यीय सिंडिकेट** (Interstate Smuggling)
   - Arun Verma, Deepak Singh, Ravi Nair
   - Crimes: Smuggling, GST Fraud, Counterfeiting

### 🔗 Hidden Cross-Gang Connections

```
Vikram Sharma (Mumbai)
  ├─→ calls Rohit Singh (UP) 6×/week
  └─→ transfers ₹500K to Ramesh Bhat (Hawala)

Rohit Singh (UP)
  ├─→ calls Arun Verma (Interstate) 7×/week
  └─→ receives funds from Mumbai & Hawala

Ramesh Bhat (Hawala HUB)
  ├─→ calls Mohammad Khan 15×/day (busiest node)
  ├─→ receives ₹3.5 crore from multiple gangs
  └─→ distributes to Interstate smugglers
```

### 📊 Data Statistics

| Metric | Count |
|--------|-------|
| FIR Documents | 5 |
| Unique Suspects | 15 |
| CDR Records | 2,848 |
| Financial Transactions | 105 |
| Criminal Gangs | 4 |
| Vehicles Tracked | 5 |
| Bank Accounts | 4 |
| Date Range | 30 days (Jan 2024) |

### 🎯 Embedded Anomalies (for Detection)

**Call Patterns:**
- 20% of calls between 1 AM - 4 AM (suspicious coordination)
- Ramesh Bhat ↔ Mohammad Khan: 15 calls/day (central hub)
- Calls 10-15 minutes before/after transactions

**Financial Patterns:**
- Smurfing: Multiple transfers below ₹10 lakh threshold
- Rapid cascading: ₹500K → ₹750K → ₹400K in 2 hours
- Interstate laundering: Mumbai → Delhi → UP flow
- Odd-hour transfers: 3 AM, 4 AM transactions

**Entity Resolution Challenges:**
- Same criminal with 3+ aliases across FIRs
- Same person mentioned in multiple districts/cases
- Different phone numbers for same suspect

### 🌍 Real-World Realism

✅ **Multilingual FIRs:** Hindi + English + Hinglish mix  
✅ **Messy Narratives:** Colloquial terms, informal format  
✅ **Indian Context:** Vehicle plates (MH02AB1234), IFSC codes, CDR cell towers  
✅ **Cross-District Stitching:** Same criminal across Mumbai, UP, Delhi  
✅ **Fragmented Data:** Unstructured (FIRs) + Structured (CSV) sources  

---

## Generation Code

**Script:** `generate_synthetic_data.py`

Features:
- Configurable gang structures
- Realistic CDR patterns (call frequency, duration, night calls)
- Money laundering trails (smurfing, cascading transfers)
- Interconnected phone numbers and accounts
- UTF-8 encoding for Hindi/Hinglish text

**Run:**
```bash
python generate_synthetic_data.py
```

Output: ~2.5 MB of data in `synthetic_data/` folder

---

## Documentation Generated

1. **DATASET_README.md** — Comprehensive guide (expected queries, network structure, usage)
2. **DATASET_SUMMARY.txt** — Quick reference (gangs, connections, anomalies)
3. **metadata.json** — Programmatic access to network structure

---

## Ready for Phase 2 ✅

**Next Step:** Build FastAPI backend for:
- ✅ NLP entity extraction from FIRs (regex + LLM)
- ✅ Entity resolution (fuzzy matching, co-occurrence merging)
- ✅ CDR parsing and relationship building
- ✅ Financial transaction anomaly detection
- ✅ Live extraction stream (SSE) for UI

**Time Estimate:** 2-3 days for full pipeline
**Impact:** Judges will see live extraction feeding real graph construction

---

## Demo Preview

When completed, users will:

1. **Upload Data**
   - Select `synthetic_data/FIRs/` folder
   - Select `call_detail_records.csv`
   - Select `financial_transactions.csv`

2. **Watch Live Extraction**
   - FIR entities appear in real-time
   - "Vikram Sharma", "9876543210", "MH02AB1234" extracted with confidence scores
   - Relations shown: "ASSOCIATED_WITH", "CALLED", "TRANSFERRED"

3. **See Interactive Graph**
   - 15 nodes (suspects)
   - 4 colored clusters (gangs)
   - Edges showing calls/transactions
   - Ramesh Bhat appears LARGEST (highest centrality)

4. **Query the Network**
   - "Who connects Gang A to hawala?"
   - System highlights path: Vikram → Ramesh Bhat
   - Shows: "14 calls + ₹500K transfer" as evidence

5. **Get Actionable Intelligence**
   - Key Players ranked: Ramesh Bhat (9.2/10 risk)
   - Anomalies flagged: Night calls, smurfing, rapid cascades
   - Communities detected: 4 gangs + bridging nodes

---

## 🚀 Status

✅ **Phase 1:** Synthetic Dataset — COMPLETE  
⏳ **Phase 2:** NLP Extraction Engine — Ready to Start  
⏳ **Phase 3:** Graph Analytics — Queued  
⏳ **Phase 4:** React Frontend — Queued  

**Prototype On Track for SIH Submission! 🎉**
