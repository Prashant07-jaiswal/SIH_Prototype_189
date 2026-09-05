# Criminal Network Synthetic Dataset - SIH 2024

## 📋 Overview

This dataset contains **realistic, interconnected criminal network data** designed for the AI-Powered Criminal Network Analysis System prototype. It simulates real-world law enforcement data challenges:

- **Multilingual FIRs** (Hindi/English/Hinglish mix)
- **Call Detail Records (CDRs)** with cross-gang communication patterns
- **Financial Transaction Records** with money laundering indicators
- **Cross-district criminal stitching** (same criminal across multiple cases)

---

## 📊 Dataset Statistics

| Metric | Count |
|--------|-------|
| **FIR Documents** | 5 files |
| **CDR Records** | 2,848 call records |
| **Financial Transactions** | 105 transactions |
| **Criminal Gangs** | 4 interconnected networks |
| **Individual Suspects** | 15 unique criminals |
| **Vehicles** | 5 linked to suspects |
| **Bank Accounts** | 4 accounts showing money flows |
| **Time Period** | 2024-01-01 to 2024-01-31 (30 days) |

---

## 🗂️ Directory Structure

```
synthetic_data/
├── FIRs/
│   ├── FIR_001_MH.txt          (Mumbai - Drug Trafficking)
│   ├── FIR_002_UP.txt          (Uttar Pradesh - Vehicle Theft)
│   ├── FIR_003_DL.txt          (Delhi - Hawala Network)
│   ├── FIR_004_MH.txt          (Thane - Weapons & Gang)
│   └── FIR_005_UP.txt          (Lucknow - GST Fraud)
├── call_detail_records.csv     (2,848 CDR entries)
├── financial_transactions.csv  (105 transaction records)
├── metadata.json               (Network structure & metadata)
└── DATASET_README.md           (This file)
```

---

## 🔗 Criminal Network Structure

### **Gang A: मुंबई कार्टेल (Mumbai Cartel)**
- **Members:** Vikram Sharma, Ramesh Gupta, Priya Desai
- **Locations:** Mumbai, Thane, Navi Mumbai
- **Crimes:** Drug Trafficking, Extortion, Money Laundering
- **Key Phone:** 9876543210 (Vikram Sharma)
- **Vehicle:** MH02AB1234 (Fortuner)
- **Bank Account:** HDFC_ACC_1001

**Network Connections:**
- Vikram ↔ Ramesh (8 calls/day on average)
- Vikram ↔ Priya (6 calls/day)
- Ramesh → Hawala Network (cross-gang connection)

---

### **Gang B: उत्तर प्रदेश रिंग (UP Criminal Ring)**
- **Members:** Rohit Singh, Suresh Kumar, Akshay Patel
- **Locations:** Lucknow, Kanpur, Agra
- **Crimes:** Vehicle Theft, Highway Robbery, Forgery
- **Key Phone:** 8765432109 (Rohit Singh)
- **Vehicle:** UP32CD5678 (Splendor)
- **Bank Account:** ICIC_ACC_2001

**Network Connections:**
- Rohit ↔ Suresh (10 calls/day - tightest gang bond)
- Rohit → Vikram Sharma (cross-gang) - 6 calls/week ⚠️
- Rohit → Arun Verma (Interstate gang) - 7 calls/week

---

### **Gang C: हवाला नेटवर्क (Hawala Network)**
- **Members:** Ramesh Bhat, Mohammad Khan, Vikram Iyer
- **Locations:** Delhi, Bangalore, Hyderabad
- **Crimes:** Money Laundering, Hawala, Illegal Fund Transfer
- **Key Phone:** 7654321098 (Ramesh Bhat)
- **Vehicle:** DL01EF9012 (Creta)
- **Bank Accounts:** UTIB_ACC_3001, SBIN_ACC_3002

**Network Connections:**
- Ramesh ↔ Mohammad (15 calls/day - **highest frequency** = central hub)
- Receives funds from: Mumbai Cartel (Gang A), UP Ring (Gang B)
- Distributes funds to Interstate Smugglers (Gang D)

---

### **Gang D: अंतरराज्यीय सिंडिकेट (Interstate Smuggling)**
- **Members:** Arun Verma, Deepak Singh, Ravi Nair
- **Locations:** Delhi, Gurgaon, Noida
- **Crimes:** Smuggling, GST Fraud, Counterfeiting
- **Key Phone:** 6543210987 (Arun Verma)
- **Vehicle:** UP14IJ7890 (Swift)
- **Bank Account:** ICIC_ACC_2001

**Network Connections:**
- Arun ↔ Deepak (9 calls/day)
- Arun → Rohit Singh (UP gang) - 7 calls/week
- Receives hawala funds for smuggling operations

---

## 📄 FIR Document Format

Each FIR contains:
- **Formal metadata** (FIR number, district, police station, date, IPC sections)
- **Mixed Hindi/English narrative** with:
  - Suspect names and **aliases** (उर्फ़ = "aka")
  - Phone numbers embedded in text
  - Vehicle registration plates
  - Bank account references
  - Crime descriptions in colloquial Hinglish
- **Extracted fields** at bottom (Suspects, Phones, Vehicles, Accounts)

### Example Extraction Challenge:
```
"फोन नंबर 9876543210 से कॉल करके उन्होंने किसी को ड्रग्स की सप्लाई करने के बारे में बात की"
↓
NLP Must Extract:
  - Entity: Person (Phone 9876543210)
  - Entity: Crime (Drug Supply)
  - Relation: COMMUNICATED_ABOUT_CRIME
```

---

## 📞 Call Detail Records (CDR)

**Schema:**
```csv
cdr_id,caller,receiver,call_datetime,duration_seconds,call_type,cell_tower
```

**Patterns Embedded:**
- **Within-gang calls:** High frequency (8-15 calls/day)
- **Cross-gang calls:** Moderate frequency (5-7 calls/week)
- **Night calls (1 AM - 4 AM):** 20% of calls = suspicious pattern ⚠️
- **Call duration:** 30 sec to 20 min (realistic)
- **Cell towers:** Geographic distribution (Mumbai, UP, Delhi, Bangalore)

**Key Anomalies to Detect:**
- `9876543210 → 8765432109`: Gang A to Gang B (Money transfer trigger?)
- `7654321098 ↔ 7123456789`: Hawala hub (15 calls/day = central node)
- Calls at `01:00-04:00`: Late-night coordination

---

## 💰 Financial Transactions

**Schema:**
```csv
transaction_id,sender_account,receiver_account,amount_inr,transaction_datetime,
transaction_type,sender_bank,receiver_bank,status,remarks
```

**Transaction Flow (Money Laundering Trail):**

```
HDFC_ACC_1001 (Mumbai Cartel) 
    ↓ ₹500K-750K (Multiple transactions)
SBIN_ACC_3002 (Hawala Hub) 
    ↓ ₹400K-750K (Rapid movement)
UTIB_ACC_3001 (Hawala Hub) 
    ↓ ₹250K-450K (Final distribution)
ICIC_ACC_2001 (UP Ring / Interstate)
```

**Suspicious Patterns:**
1. **Smurfing:** Transactions just below ₹10 lakh (reporting threshold) ⚠️
2. **Rapid Movement:** Funds transferred within 1-2 hours across 3+ banks
3. **Cash Heavy:** Multiple deposits from same account
4. **Time Anomalies:** Transactions at odd hours (00:00-06:00)

**Anomaly Detection Triggers:**
- Transaction amount > ₹5 lakh without corresponding CDR
- Multiple transfers to same account within 24 hours
- Sender and receiver in different cities (high-risk)

---

## 🎯 Expected Graph Nodes & Relationships

### **Node Types:**
```
(:Person)
  - Vikram Sharma (Risk: 9.2/10)
  - Ramesh Bhat (Risk: 8.9/10, Centrality: HIGH - Hawala Hub)
  - Mohammad Khan (Risk: 8.5/10, Centrality: HIGH)
  - Rohit Singh (Risk: 8.1/10)
  ... 15 total

(:Phone)
  - 9876543210, 9123456789, 8765432109, ...
  
(:Vehicle)
  - MH02AB1234, UP32CD5678, DL01EF9012, ...
  
(:BankAccount)
  - HDFC_ACC_1001, SBIN_ACC_3002, UTIB_ACC_3001, ICIC_ACC_2001

(:Location)
  - Mumbai, Thane, Kanpur, Delhi, Bangalore, ...

(:Case)
  - MH/2024/12345, UP/2024/67890, DL/2024/11223, ...
```

### **Relationship Types:**
```
(Person)-[:USES_PHONE]->(Phone)
(Person)-[:OWNS_VEHICLE]->(Vehicle)
(Person)-[:OPERATES_ACCOUNT]->(BankAccount)
(Person)-[:CALLED {count, avg_duration, dates}]->(Person)  [from CDR]
(BankAccount)-[:TRANSFERRED {amount, count, dates}]->(BankAccount)  [from Transactions]
(Person)-[:ACCUSED_IN]->(Case)  [from FIR]
(Person)-[:ASSOCIATE_OF {source: "FIR"}]->(Person)
(Vehicle)-[:USED_IN]->(Case)
```

---

## 🔍 Key Investigative Queries This Dataset Enables

### Query 1: **Find Hidden Connections**
*"Who connects Gang A (Mumbai) to Hawala Network?"*
```
Expected Path: Vikram Sharma → (calls) → Ramesh Bhat → (transfers) → SBIN_ACC_3002
```

### Query 2: **Identify Key Players**
*"Who is the most central figure in this network?"*
```
Expected: Ramesh Bhat (Hawala Hub)
Reason: 15 calls/day + facilitates ₹3.5 crore fund movement
Centrality Score: Betweenness = HIGH, PageRank = HIGH
```

### Query 3: **Detect Suspicious Patterns**
*"Which transactions follow unusual patterns?"*
```
Expected: 
- HDFC_ACC_1001 → SBIN_ACC_3002 (₹500K, 1 AM)
- UTIB_ACC_3001 → ICIC_ACC_2001 (₹750K, 3 AM)
- Calls 15 min before/after transfer
```

### Query 4: **Community Detection**
*"Which suspects form tight-knit groups?"*
```
Expected 4 communities:
- Cluster A: Vikram, Ramesh Gupta, Priya (Mumbai Cartel)
- Cluster B: Rohit, Suresh, Akshay (UP Ring)
- Cluster C: Ramesh Bhat, Mohammad (Hawala Hub)
- Cluster D: Arun, Deepak (Interstate)
```

### Query 5: **Cross-District Stitching**
*"What cases involve the same criminal?"*
```
Example: Vikram Sharma appears in:
- FIR_001_MH (Mumbai, Jan 15)
- FIR_004_MH (Thane, Mar 20)
And is mentioned as "connection" in FIR_003_DL
```

---

## 🚀 Using This Dataset

### **For NLP Entity Extraction Testing:**
```python
# Load FIRs
from pathlib import Path

fir_folder = Path("synthetic_data/FIRs")
for fir_file in fir_folder.glob("*.txt"):
    content = fir_file.read_text(encoding='utf-8')
    # Extract: Names, Phones, Vehicles, Accounts, Crimes, Locations
```

### **For Graph Building:**
```python
# Parse FIRs → Extract entities
# Parse CDRs → Create CALLED relationships
# Parse Transactions → Create TRANSFERRED relationships
# Merge by phone/account/vehicle (entity resolution)

import networkx as nx
G = nx.Graph()
# Add nodes and edges...
```

### **For Anomaly Detection:**
```python
# CDR Anomalies:
- Night calls (1 AM - 4 AM): 20% of dataset
- Call bursts (10+ calls in 1 hour)
- Calls 10+ min long

# Transaction Anomalies:
- Smurfing pattern (amounts < 1000000)
- Rapid cascading transfers (3+ hops in 2 hours)
- Transfers at odd hours (00:00-06:00)
```

---

## 📌 Dataset Design Rationale

### **Why This Structure?**
1. **Real-world complexity:** Messy Hindi/English FIRs mimic actual Indian police records
2. **Multi-source fusion:** Requires combining unstructured (FIRs) + structured (CDR, Transactions) data
3. **Entity resolution challenge:** Same criminal with different names, phone numbers across districts
4. **Graph complexity:** Not too large (2,800 CDR records) for hackathon, but complex enough to showcase value
5. **Interconnectedness:** 4 gangs with deliberate cross-gang links show hidden networks

### **Realistic Anomalies Embedded:**
- ✅ Names written as "Vikram Sharma, विक्रम शर्मा, विक्की, विक्रम बंगाली"
- ✅ Night calls (criminal operational pattern)
- ✅ Money cascading across 3+ banks (hawala)
- ✅ Same person in multiple FIRs across districts
- ✅ Hinglish phrases in narratives ("chaku se vaar", "hawala")

---

## 📝 Next Steps for Implementation

1. **Phase 2:** Build NLP extraction pipeline
   - Regex for IDs/phones/vehicles
   - LLM for entity relations
   
2. **Phase 3:** Graph construction & analytics
   - Entity resolution (fuzzy matching)
   - Load into Neo4j
   - Calculate centrality scores
   
3. **Phase 4:** Frontend visualization
   - React + force-graph
   - Interactive filters & queries

---

## 📞 Data Generation Script

Generated using: `generate_synthetic_data.py`

```bash
python generate_synthetic_data.py
```

To regenerate with different parameters, edit `GANGS`, `VEHICLES`, `BANKS` in the script.

---

**Dataset Ready for SIH Prototype! 🚀**
