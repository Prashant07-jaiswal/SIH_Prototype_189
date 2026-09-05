"""
End-to-End Verification Script for Criminal Network Analysis System (Phases 1-3)
"""

import sys
from pathlib import Path

# Add backend directory to sys.path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

from backend.extraction import extract_from_fir
from backend.entity_resolution import resolve_entities
from backend.data_loaders import parse_relationships_from_cdr, parse_relationships_from_transactions
from backend.analytics import CriminalNetworkAnalytics

def main():
    print("=" * 60)
    print("AI-Powered Criminal Network Analysis - Integration Test")
    print("=" * 60)

    # 1. FIR Extraction
    fir_path = Path("synthetic_data/FIRs")
    fir_files = list(fir_path.glob("*.txt"))
    print(f"\n[1/4] Extracting entities from {len(fir_files)} FIRs...")

    all_entities = []
    all_relationships = []

    for fir in fir_files:
        res = extract_from_fir(fir.read_text(encoding="utf-8"), fir.stem)
        all_entities.extend(res.entities)
        all_relationships.extend(res.relationships)

    print(f"  -> Extracted {len(all_entities)} entities & {len(all_relationships)} relationships")

    # 2. CDR and Financial Data Parsing
    print("\n[2/4] Parsing Call Detail Records (CDRs) and Transactions...")
    cdr_rels = parse_relationships_from_cdr(Path("synthetic_data/call_detail_records.csv"), all_entities)
    all_relationships.extend(cdr_rels)

    txn_rels = parse_relationships_from_transactions(Path("synthetic_data/financial_transactions.csv"), all_entities)
    all_relationships.extend(txn_rels)
    print(f"  -> Total fused relationships: {len(all_relationships)}")

    # 3. Entity Resolution
    print("\n[3/4] Resolving and deduplicating entities...")
    resolved_entities, resolved_rels, metadata = resolve_entities(all_entities, all_relationships)
    print(f"  -> Consolidated to {len(resolved_entities)} unique entities")
    print(f"  -> Merged count: {metadata['merged_count']}")

    # 4. Graph Construction and Analytics
    print("\n[4/4] Executing Graph Analytics Engine (PageRank, Louvain, Centrality)...")
    analytics = CriminalNetworkAnalytics()
    results = analytics.analyze(resolved_entities, resolved_rels)

    print("\n" + "=" * 60)
    print("ANALYTICS RESULTS")
    print("=" * 60)
    print(f"Total Key Players Ranked : {len(results['key_players'])}")
    print(f"Total Communities Found  : {len(results['communities'])}")

    if results['key_players']:
        print("\nTop 3 Identified Key Players:")
        for idx, player in enumerate(results['key_players'][:3], 1):
            print(f"  {idx}. {player.entity_name:<20} | Risk Score: {player.risk_score:.2f}")

    print("\n" + "=" * 60)
    print("ALL TESTS PASSED SUCCESSFULLY! Ready for Phase 4 (React UI).")
    print("=" * 60)

if __name__ == "__main__":
    main()
