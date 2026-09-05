"""
PHASE 3 STEP 1: GRAPH ANALYTICS MODULE - COMPLETE EXPLANATION

===================================================================================
                    WHAT WE JUST BUILT & WHY EACH PART MATTERS
===================================================================================

The analytics.py file contains 5 interconnected components working together to:
1. Convert entities into a graph structure
2. Identify key influencers using algorithms
3. Detect communities/gangs automatically
4. Find connection paths between suspects
5. Calculate risk scores

---

COMPONENT 1: GRAPH BUILDER
--------------------------
What it does:
  - Takes entities (people, phones, accounts) and makes them NODES
  - Takes relationships (calls, transfers) and makes them EDGES
  - Stores metadata on each node/edge

Example:
  Nodes:
    • Vikram Sharma (person)
    • 9876543210 (phone)
    • HDFC_ACC_1001 (bank account)
  
  Edges (with weights/importance):
    • Vikram → Phone: "USES_PHONE" (confidence: 0.95)
    • Vikram → Account: "OPERATES_ACCOUNT" (confidence: 0.75)
    • Vikram → Ramesh: "CALLED" (15 calls/month, weight: 15)

Why it matters:
  Graph algorithms work on this structure. Without converting to a graph,
  we can't calculate PageRank, centrality, or find paths.

---

COMPONENT 2: CENTRALITY ANALYZER
--------------------------------
What it does:
  Calculates 4 different "importance" scores for each person

  A) PageRank (0-1 scale)
     How it works: Google's algorithm
     Importance flows through connections
     Example: Ramesh Bhat gets HIGH PageRank because:
       • He talks to 15 people daily
       • Those people are connected to others
       • He's in the "center" of information flow
     
  B) Betweenness Centrality (0-1 scale)
     How it works: Count how many shortest paths go THROUGH this person
     Example: Vikram is on the path from Mumbai gang → Hawala network
       • Path: Mumbai gang → Vikram → Ramesh Bhat → Delhi
       • Vikram appears in many paths = HIGH betweenness
       • Means: Vikram is a CRITICAL BRIDGE/INTERMEDIARY
     
  C) Closeness Centrality (0-1 scale)
     How it works: Average distance to everyone else
     Example: Ramesh Bhat is 2 hops away from everyone
       • Close to everyone = High closeness
       • Means: Good communicator/coordinator
     
  D) Degree Centrality (count)
     How it works: Simple connection count
     Example: Ramesh Bhat has 15 connections (calls 15 people)

Why it matters:
  Different metrics reveal different types of influence:
  • PageRank: Who's most important overall
  • Betweenness: Who bridges different groups (KEY FOR DETECTING INTERMEDIARIES)
  • Closeness: Who can reach everyone quickly
  • Degree: Who has most raw connections

In SIH Demo:
  Shows judges "Ramesh Bhat is the kingpin" with data-backed scoring

---

COMPONENT 3: COMMUNITY DETECTOR
-------------------------------
What it does:
  Automatically finds groups/clusters without knowing the real gangs

Algorithm: Louvain (state-of-the-art for this)
  How it works:
    1. Start: each person is their own group
    2. Iterate: person joins group that maximizes "modularity"
       (modularity = more connections within group, fewer outside)
    3. Repeat until stable
    4. Result: Natural communities emerge

Example output:
  Community 1: Vikram Sharma, Ramesh Gupta, Priya Desai (Mumbai gang)
  Community 2: Rohit Singh, Suresh Kumar, Akshay Patel (UP gang)
  Community 3: Ramesh Bhat, Mohammad Khan (Hawala network)
  Community 4: Arun Verma, Deepak Singh, Ravi Nair (Interstate gang)

Why it matters:
  • Discovers gangs AUTOMATICALLY (no manual input needed)
  • Shows cohesion score (how tight is each community)
  • Shows bridge nodes (people connecting communities)
  • Judges see "System detected 4 gangs" - impressive!

---

COMPONENT 4: PATH FINDER
-----------------------
What it does:
  Answers questions like:
    "Who connects Gang A to Hawala Network?"
    "What's the route of ₹50L transfer?"
    "Who's the intermediary?"

Algorithm: Dijkstra shortest path
  How it works:
    1. Start from source entity
    2. Explore neighbors, tracking distance
    3. Use weights (call frequency, transfer amount) as distance
    4. Find shortest path to target

Example:
  Query: "Who connects Vikram (Mumbai) to Ramesh Bhat (Hawala)?"
  
  Answer Path:
    Vikram (Mumbai) 
      → calls → Rohit (UP)
      → calls → Arun (Interstate)
      → calls → Ramesh Bhat (Hawala)
  
  With evidence:
    • Vikram & Rohit: 6 calls/week + ₹500K transfer
    • Rohit & Arun: 7 calls/week + ₹300K transfer
    • Arun & Ramesh: 8 calls/week + ₹400K transfer

Why it matters:
  • Visualize the hidden connections
  • Show judges "follow the money/calls"
  • Prove criminal network exists (judges love this)

---

COMPONENT 5: RISK CALCULATOR
---------------------------
What it does:
  Combines multiple factors into ONE RISK SCORE (0-10)

Factors considered:
  1. Centrality (30%): Are they central/important?
  2. Connections (30%): Do they have suspicious connections?
  3. Anomalies (20%): Are they in smurfing/night calls?
  4. Base (20%): Their inherent risk

Calculation example for Ramesh Bhat:
  • PageRank score: 0.87 × 3.0 = 2.61
  • Betweenness: 0.82 × 0.4 = 0.33 (sub-component)
  • Night calls to Mohammad: +0.5
  • Smurfing patterns: +1.5
  • Total: 9.2/10 (VERY HIGH RISK)

Why it matters:
  • Single number judges can understand
  • Combines multiple signals into one score
  • Shows who's most dangerous/important
  • Automatically ranks suspects

===================================================================================
                        HOW ALL 5 COMPONENTS WORK TOGETHER
===================================================================================

Input: 50 entities + 120 relationships (from Phase 2 extraction)
  ↓
[STEP 1] GraphBuilder converts them to NetworkX graph
  ↓
[STEP 2] CentralityAnalyzer scores each node (PageRank, Betweenness, etc.)
  ↓
[STEP 3] CommunityDetector finds 4 gangs automatically
  ↓
[STEP 4] PathFinder ready to answer "who connects X to Y?" queries
  ↓
[STEP 5] RiskCalculator combines all factors into risk scores
  ↓
Output: 
  • Key players ranked (Ramesh Bhat: 9.2/10 risk)
  • Communities detected (4 gangs)
  • Paths ready (for demo queries)
  • Risk scores (for suspect prioritization)

===================================================================================
                        WHAT HAPPENS IN SIH DEMO (Phase 5)
===================================================================================

Judges ask: "Show me key players in this criminal network"

System response:
  1. Ramesh Bhat (Hawala Hub)
     Centrality: 0.87 | Risk: 9.2/10
     Connections: 15
     Crimes: Money Laundering, Hawala

  2. Mohammad Khan (Hawala Network)
     Centrality: 0.82 | Risk: 8.9/10
     Connections: 14
     Crimes: Money Laundering

  3. Vikram Sharma (Mumbai Gang)
     Centrality: 0.64 | Risk: 8.1/10
     Connections: 8
     Crimes: Drug Trafficking

Judges ask: "Show me the gangs"

System shows 4 colored clusters:
  • Red: Mumbai Cartel (3 members)
  • Blue: UP Ring (3 members)
  • Green: Hawala Network (3 members)
  • Yellow: Interstate Smugglers (3 members)
  
  Plus: Bridging edges showing cross-gang connections
  Plus: Cohesion scores showing how tight each gang is

Judges ask: "Who connects Gang A (Mumbai) to Hawala Network?"

System highlights path:
  Vikram Sharma (Mumbai)
    → [6 calls/week, ₹500K transfer] →
  Rohit Singh (UP)
    → [7 calls/week, ₹300K transfer] →
  Arun Verma (Interstate)
    → [8 calls/week, ₹400K transfer] →
  Ramesh Bhat (Hawala)

Judges impressed: "This connects two supposedly separate investigations!"

===================================================================================
                        NEXT STEP: Update FastAPI Endpoints
===================================================================================

Now we need to:
1. Import analytics.py into main.py
2. Update the 3 placeholder endpoints:
   • POST /api/analytics/key-players
   • POST /api/analytics/communities
   • POST /api/query
3. Call CriminalNetworkAnalytics when data is loaded
4. Return results in graph-friendly format

This will complete Phase 3 ✅

===================================================================================
"""

print(__doc__)
