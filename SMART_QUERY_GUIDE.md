# Smart Natural Language Query System

## Overview

The NLQ engine now intelligently detects your **query intent** and filters results to show only relevant entity types. This solves the problem where queries like "what accounts link to vehicle MH02AB1234?" would return mixed vehicle plates instead of bank account names.

## How It Works

### Three-Step Process

**Step 1: Intent Detection**
- Analyzes query keywords to determine what type of entities you're interested in
- Maps keywords to entity types:
  - "account", "bank", "money", "transaction" → `BankAccount`
  - "person", "suspect", "driver", "owner" → `Person`
  - "vehicle", "car", "plate", "registration" → `Vehicle`
  - "location", "city", "area" → `Location`
  - "case", "fir", "crime" → `Case`

**Step 2: Entity Matching**
- Searches for entities matching your keywords (e.g., "MH02AB1234")
- Returns the best match as the primary entity

**Step 3: Smart Neighbor Filtering**
- Gets all neighbors connected to the matched entity
- **Filters by detected intent type**
- Shows ONLY the entity types you're asking about

## Example Queries & Results

### Query 1: "What accounts link to MH02AB1234?"
```
Intent Detected: BankAccount
Matching Entity: MH02AB1234 (Vehicle)
Connected Neighbors: 12 total
After Filtering: 3 BankAccount entities

Result:
✓ MH02AB1234 is connected to 3 BankAccount entities:
  → HDFC_ACC_2015 (BankAccount)
  → ICICI_ACC_1847 (BankAccount)
  → SBI_ACC_3421 (BankAccount)
```

### Query 2: "Who drove the vehicle MH02AB1234?"
```
Intent Detected: Person
Matching Entity: MH02AB1234 (Vehicle)
Connected Neighbors: 12 total
After Filtering: 2 Person entities

Result:
✓ MH02AB1234 is connected to 2 Person entities:
  → Vikram Sharma (Person)
  → Rajesh Kumar (Person)
```

### Query 3: "What cases mention Vikram?"
```
Intent Detected: Case
Matching Entity: Vikram Sharma (Person)
Connected Neighbors: 8 total
After Filtering: 2 Case entities

Result:
✓ Vikram Sharma is connected to 2 Case entities:
  → FIR_2024_001 (Case)
  → FIR_2024_005 (Case)
```

### Query 4: "Show connections for Vikram" (No specific filter)
```
Intent Detected: None (generic query)
Matching Entity: Vikram Sharma (Person)
Connected Neighbors: 8 total
No Filtering Applied

Result:
✓ Vikram Sharma is connected to 8 entities:
  → Phone: +919876543210 (Phone)
  → Vehicle: MH02AB1234 (Vehicle)
  → BankAccount: HDFC_ACC_2015 (BankAccount)
  → Location: Mumbai (Location)
  → Case: FIR_2024_001 (Case)
  → Person: Rajesh Kumar (Person)
  → ... and 2 more
```

## Intent Keywords Mapping

### BankAccount Intent
Triggers on: `account`, `bank`, `money`, `transaction`, `transfer`, `hawala`

### Person Intent
Triggers on: `person`, `people`, `suspect`, `criminal`, `who`, `accused`, `driver`, `owner`

### Vehicle Intent
Triggers on: `vehicle`, `car`, `bike`, `auto`, `plate`, `registration`

### Location Intent
Triggers on: `location`, `place`, `city`, `area`, `district`

### Case Intent
Triggers on: `case`, `fir`, `complaint`, `crime`

## Error Handling

### No Results After Filtering
If a query filters results but finds no matches:
```
Query: "What bank accounts link to Vikram?"
Result:
⚠️ No BankAccount entities connected to Vikram Sharma.
Available neighbors: 8 total entities
(Vikram may be connected to phones, vehicles, or other types instead)
```

### No Entity Match
If the search term doesn't match any entity:
```
Query: "What accounts link to NONEXISTENT123?"
Result:
No matching entities found for query: 'what accounts link to nonexistent123?'

Try searching for:
• Vikram Sharma
• Rajesh Kumar
• +919876543210
...
```

## Response Structure

The `/api/query` endpoint now returns:

```json
{
  "status": "success",
  "query": "what accounts link to MH02AB1234?",
  "message": "Found 1 matching entities:\n\n• MH02AB1234\n\nMH02AB1234 is connected to 3 BankAccount entities:\n  → HDFC_ACC_2015 (BankAccount)\n  → ICICI_ACC_1847 (BankAccount)\n  → SBI_ACC_3421 (BankAccount)",
  "matches": [
    {
      "name": "MH02AB1234",
      "id": "vehicle_1",
      "type": "Vehicle",
      "keyword": "mh02ab1234"
    }
  ],
  "matches_found": 1,
  "entities_analyzed": 57,
  "intent_filter": ["BankAccount"]  // ← NEW: shows detected intent
}
```

## Use Cases for Law Enforcement

### Fraud Investigation
- **Query**: "What bank accounts link to Hawala network Delhi?"
- **Result**: Shows only BankAccount nodes connected to the suspect, filtering out noise

### Vehicle Tracking
- **Query**: "What cases mention vehicle MH04XY5678?"
- **Result**: Shows only Case/FIR nodes, not unrelated persons or locations

### Network Mapping
- **Query**: "Who are the suspects linked to +919876543210?"
- **Result**: Shows only Person nodes, filtering out phones, vehicles, and accounts

### Asset Tracing
- **Query**: "What locations has Vikram visited?"
- **Result**: Shows only Location nodes with connections to the suspect

## Visual Feedback on Frontend

When you see query results:
- **Matched nodes** glow **cyan** on the graph
- **Filtered type** is shown in the result header: `"is connected to 3 BankAccount entities"`
- **Count reflects filtering**: Shows actual filtered count, not total neighbors

## Technical Implementation

**File Modified**: `backend/main.py` - `/api/query` endpoint

**Algorithm**:
1. Extract keywords from query
2. Match against 5 intent keyword maps
3. Collect matching entity types
4. Find entities matching search term
5. Get all neighbors of primary entity
6. Filter neighbors by detected types
7. Return filtered results with intent info

**Performance**: O(n) where n = total entities + neighbors
- Keyword matching: linear scan
- Filtering: linear scan of neighbors
- No additional database queries needed

## Limitations & Future Improvements

### Current Limitations
- Single keyword intent detection (first match wins if multiple intents)
- Simple string matching for entity names
- Doesn't handle complex path queries ("who connects A to B")

### Future Enhancements
- Multi-step path finding: "Who connects Vikram to the Hawala network?"
- Relationship type filtering: "What direct calls (not indirect) link X to Y?"
- Temporal queries: "What accounts linked to Vikram in 2024?"
- Confidence-based filtering: "Show high-confidence connections only"

## Testing the Feature

```bash
# Terminal 1: Start Backend
cd backend
python main.py

# Terminal 2: Start Frontend
cd frontend
npm run dev

# In Browser - Test Queries:
1. Type: "what accounts link to MH02AB1234?"
   Expected: Only BankAccount entities shown

2. Type: "who drove MH02AB1234?"
   Expected: Only Person entities shown

3. Type: "what cases mention vikram?"
   Expected: Only Case entities shown

4. Type: "vikram"
   Expected: All entity types shown (no specific filter)
```

---

## Summary

✅ **Smart Query Engine**: Detects what you're asking for and filters results accordingly
✅ **No False Positives**: Vehicle plates won't appear when asking for accounts
✅ **Law Enforcement Focused**: Designed for real police investigation workflows
✅ **Backward Compatible**: Generic queries still work without filtering
✅ **Audit Trail Preserved**: Filtering doesn't affect data, only display
