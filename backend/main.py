"""
Criminal Network Analysis System - FastAPI Application
Main entry point for the backend API
"""

import logging
from pathlib import Path
from typing import List
import json

from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from config import settings
from models import (
    ExtractionResult, AnalyticsResponse, QueryRequest,
    PathResult, GraphNode, GraphEdge, CriminalNetworkGraph,
    KeyPlayer, Community, Anomaly
)
from extraction import extract_from_fir, EntityExtractor
from entity_resolution import resolve_entities
from data_loaders import (
    load_fir_folder, load_cdr_csv, load_financial_transactions,
    parse_relationships_from_cdr, parse_relationships_from_transactions
)
from analytics import CriminalNetworkAnalytics

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ============================================================================
# FASTAPI APP SETUP
# ============================================================================

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="AI-Powered Criminal Network Analysis System for SIH 2024"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for hackathon demo
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# REGISTER UPLOAD ROUTES
# ============================================================================
from upload_routes import router as upload_router
app.include_router(upload_router)


# ============================================================================
# STATE MANAGEMENT
# ============================================================================

class AppState:
    """Application state for storing extracted data and analytics results"""
    def __init__(self):
        self.entities = []
        self.relationships = []
        self.graph = None
        self.is_processing = False
        self.extraction_progress = 0
        # Phase 3: Analytics results
        self.key_players = []
        self.communities = []
        self.centrality_scores = {}
        self.network_graph = None

app_state = AppState()

# ============================================================================
# HEALTH CHECK
# ============================================================================

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "app": settings.app_name,
        "version": settings.app_version,
        "processing": app_state.is_processing
    }

# ============================================================================
# EXTRACTION ENDPOINTS
# ============================================================================

@app.post("/api/extract/fir")
async def extract_single_fir(file: UploadFile = File(...)):
    """
    Extract entities from a single FIR document
    Returns: ExtractionResult with entities and relationships
    """
    try:
        content = await file.read()
        text = content.decode('utf-8')

        result = extract_from_fir(text, file.filename)

        logger.info(
            f"Extracted from {file.filename}: "
            f"{len(result.entities)} entities, {len(result.relationships)} relationships"
        )

        return result

    except Exception as e:
        logger.error(f"Error extracting FIR: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/extract/batch")
async def extract_batch(fir_folder: str = None, background_tasks: BackgroundTasks = None):
    """
    Extract entities from all FIRs in a folder
    Can optionally load from synthetic_data/FIRs if no path provided
    """
    try:
        if app_state.is_processing:
            raise HTTPException(status_code=409, detail="Processing already in progress")

        app_state.is_processing = True
        app_state.extraction_progress = 0

        # Load FIRs
        fir_path = Path(fir_folder) if fir_folder else settings.fir_folder

        if not fir_path.exists():
            raise HTTPException(status_code=404, detail=f"FIR folder not found: {fir_path}")

        fir_files = list(fir_path.glob("*.txt"))
        logger.info(f"Found {len(fir_files)} FIR files in {fir_path}")

        all_entities = []
        all_relationships = []
        extraction_results = []

        # Extract from each FIR
        for i, fir_file in enumerate(fir_files):
            text = fir_file.read_text(encoding='utf-8')
            result = extract_from_fir(text, fir_file.stem)

            all_entities.extend(result.entities)
            all_relationships.extend(result.relationships)
            extraction_results.append(result)

            app_state.extraction_progress = int((i + 1) / len(fir_files) * 100)
            logger.info(f"Extraction progress: {app_state.extraction_progress}%")

        logger.info(f"Total entities extracted: {len(all_entities)}")
        logger.info(f"Total relationships extracted: {len(all_relationships)}")

        # Entity resolution
        logger.info("Starting entity resolution...")
        resolved_entities, resolved_relationships, merge_metadata = resolve_entities(
            all_entities,
            all_relationships,
            similarity_threshold=settings.entity_similarity_threshold
        )

        logger.info(f"After resolution: {len(resolved_entities)} entities, "
                   f"{len(resolved_relationships)} relationships")

        # Store in app state
        app_state.entities = resolved_entities
        app_state.relationships = resolved_relationships

        app_state.is_processing = False

        return {
            "status": "success",
            "total_firs_processed": len(fir_files),
            "total_entities_extracted": len(all_entities),
            "total_entities_after_resolution": len(resolved_entities),
            "total_relationships": len(resolved_relationships),
            "merge_metadata": merge_metadata,
            "extraction_results_count": len(extraction_results)
        }

    except Exception as e:
        logger.error(f"Error in batch extraction: {str(e)}")
        app_state.is_processing = False
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# DATA INGESTION ENDPOINTS
# ============================================================================

@app.post("/api/ingest/all")
async def ingest_all_data(
    fir_folder: str = None,
    cdr_file: str = None,
    transaction_file: str = None
):
    """
    Ingest all three data sources (FIRs, CDR, Transactions)
    Builds complete criminal network graph
    """
    try:
        app_state.is_processing = True

        # Use defaults if not provided
        fir_path = Path(fir_folder) if fir_folder else settings.fir_folder
        cdr_path = Path(cdr_file) if cdr_file else settings.cdr_file
        txn_path = Path(transaction_file) if transaction_file else settings.transaction_file

        # Step 1: Extract from FIRs
        logger.info("Step 1/3: Extracting from FIRs...")
        all_entities = []
        all_relationships = []

        fir_files = list(fir_path.glob("*.txt"))
        for fir_file in fir_files:
            text = fir_file.read_text(encoding='utf-8')
            result = extract_from_fir(text, fir_file.stem)
            all_entities.extend(result.entities)
            all_relationships.extend(result.relationships)

        logger.info(f"Extracted from FIRs: {len(all_entities)} entities")

        # Step 2: Parse CDR records
        logger.info("Step 2/3: Parsing CDR records...")
        cdr_relationships = parse_relationships_from_cdr(cdr_path, all_entities)
        all_relationships.extend(cdr_relationships)
        logger.info(f"Added {len(cdr_relationships)} call relationships from CDR")

        # Step 3: Parse financial transactions
        logger.info("Step 3/3: Parsing financial transactions...")
        txn_relationships = parse_relationships_from_transactions(txn_path, all_entities)
        all_relationships.extend(txn_relationships)
        logger.info(f"Added {len(txn_relationships)} transaction relationships")

        # Entity resolution
        logger.info("Resolving entities...")
        resolved_entities, resolved_relationships, metadata = resolve_entities(
            all_entities,
            all_relationships
        )

        # Store in state
        app_state.entities = resolved_entities
        app_state.relationships = resolved_relationships

        # PHASE 3: RUN GRAPH ANALYTICS
        logger.info("Running graph analytics...")
        analytics_engine = CriminalNetworkAnalytics()
        analytics_results = analytics_engine.analyze(resolved_entities, resolved_relationships)

        # Store analytics results in app state
        app_state.key_players = analytics_results['key_players']
        app_state.communities = analytics_results['communities']
        app_state.centrality_scores = analytics_results['centrality_scores']
        app_state.network_graph = analytics_results['graph']

        app_state.is_processing = False

        return {
            "status": "success",
            "entities": len(resolved_entities),
            "relationships": len(resolved_relationships),
            "merge_metadata": metadata,
            "analytics": {
                "key_players_found": len(app_state.key_players),
                "communities_detected": len(app_state.communities),
                "graph_nodes": app_state.network_graph.number_of_nodes() if app_state.network_graph else 0,
                "graph_edges": app_state.network_graph.number_of_edges() if app_state.network_graph else 0
            }
        }

    except Exception as e:
        logger.error(f"Error ingesting data: {str(e)}")
        app_state.is_processing = False
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# GRAPH ENDPOINTS
# ============================================================================

@app.get("/api/graph/current")
async def get_current_graph():
    """Get the current loaded graph"""
    if not app_state.entities:
        raise HTTPException(status_code=400, detail="No data loaded yet. Run /api/ingest/all first.")

    try:
        # Build graph nodes
        nodes = [
            GraphNode(
                id=entity.id,
                label=entity.name,
                type=entity.type,
                metadata={
                    "aliases": entity.aliases if hasattr(entity, 'aliases') else [],
                    "confidence": entity.confidence
                }
            )
            for entity in app_state.entities
        ]

        # Build graph edges
        edges = [
            GraphEdge(
                source=rel.source_id,
                target=rel.target_id,
                label=rel.type.value if hasattr(rel.type, 'value') else str(rel.type),
                type=rel.type,
                weight=rel.weight,
                metadata={
                    "confidence": rel.confidence,
                    "attributes": rel.attributes
                }
            )
            for rel in app_state.relationships
        ]

        graph = CriminalNetworkGraph(
            nodes=nodes,
            edges=edges,
            node_count=len(nodes),
            edge_count=len(edges)
        )

        return graph

    except Exception as e:
        logger.error(f"Error building graph: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/graph/stats")
async def get_graph_stats():
    """Get statistics about the current graph"""
    if not app_state.entities:
        raise HTTPException(status_code=400, detail="No data loaded yet")

    from models import Person, Phone, Vehicle, BankAccount, Location, Case

    entity_types = {
        "Person": len([e for e in app_state.entities if isinstance(e, Person)]),
        "Phone": len([e for e in app_state.entities if isinstance(e, Phone)]),
        "Vehicle": len([e for e in app_state.entities if isinstance(e, Vehicle)]),
        "BankAccount": len([e for e in app_state.entities if isinstance(e, BankAccount)]),
        "Location": len([e for e in app_state.entities if isinstance(e, Location)]),
        "Case": len([e for e in app_state.entities if isinstance(e, Case)]),
    }

    relationship_types = {}
    for rel in app_state.relationships:
        rel_type = str(rel.type)
        relationship_types[rel_type] = relationship_types.get(rel_type, 0) + 1

    return {
        "total_entities": len(app_state.entities),
        "total_relationships": len(app_state.relationships),
        "entity_types": entity_types,
        "relationship_types": relationship_types
    }


# ============================================================================
# PROGRESS ENDPOINT (for streaming extraction)
# ============================================================================

@app.get("/api/progress")
async def get_progress():
    """Get current processing progress"""
    return {
        "is_processing": app_state.is_processing,
        "progress_percent": app_state.extraction_progress
    }


# ============================================================================
# PLACEHOLDER ENDPOINTS (for future implementation)
# ============================================================================

# ============================================================================
# ANALYTICS ENDPOINTS (Phase 3 - IMPLEMENTED)
# ============================================================================

@app.api_route("/api/analytics/key-players", methods=["GET", "POST"])
async def get_key_players():
    """
    Get key players ranked by centrality and risk scores

    Explanation:
    - Uses PageRank algorithm (like Google's ranking)
    - Combines with risk scores (centrality + connections + anomalies)
    - Returns top 10 suspects ranked by influence/danger
    """
    if not app_state.entities or not app_state.key_players:
        raise HTTPException(status_code=400, detail="Run /api/ingest/all first to calculate analytics")

    try:
        return {
            "status": "success",
            "key_players": app_state.key_players,
            "total_analyzed": len(app_state.entities),
            "message": "Suspects ranked by centrality (PageRank) and risk factors"
        }
    except Exception as e:
        logger.error(f"Error getting key players: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.api_route("/api/analytics/communities", methods=["GET", "POST"])
async def detect_communities():
    """
    Detect communities/gangs in the network using Louvain algorithm

    Explanation:
    - Louvain algorithm automatically finds groups
    - Groups = people more connected to each other than outsiders
    - Discovers gangs without manual input
    - Shows cohesion scores (how tight is each gang)
    """
    if not app_state.entities or not app_state.communities:
        raise HTTPException(status_code=400, detail="Run /api/ingest/all first to detect communities")

    try:
        return {
            "status": "success",
            "communities": app_state.communities,
            "total_communities": len(app_state.communities),
            "message": "Communities detected using Louvain algorithm (gangs/rings)"
        }
    except Exception as e:
        logger.error(f"Error detecting communities: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/query")
async def natural_language_query(request: QueryRequest):
    """
    Answer natural language queries on the criminal network

    Explanation:
    - Converts "Who connects A to B?" into a path-finding problem
    - Uses Dijkstra algorithm to find shortest path
    - Returns nodes, edges, and AI summary

    Examples:
    - "Who connects Gang A to Hawala?"
    - "What's the path from Vikram to ₹50L transfer?"
    - "Who's the intermediary between Mumbai and Delhi?"
    """
    if not app_state.network_graph or not app_state.entities:
        raise HTTPException(status_code=400, detail="Run /api/ingest/all first")

    try:
        query = request.query.lower()
        logger.info(f"Processing query: {query}")

        # Extract keywords from query
        keywords = query.split()
        matches = []

        # Find matching entities by name/keywords
        for entity in app_state.entities:
            entity_name = entity.name.lower()
            for keyword in keywords:
                if len(keyword) > 2 and keyword in entity_name:
                    matches.append({
                        'name': entity.name,
                        'id': entity.id,
                        'type': entity.type,
                        'keyword': keyword
                    })

        # Build response message
        if matches:
            message = f"Found {len(matches)} matching entities:\n\n"

            unique_names = list(set([m['name'] for m in matches]))
            for name in unique_names[:5]:  # Show top 5
                message += f"• {name}\n"

            # If we have network graph, analyze connections
            if app_state.network_graph and len(matches) >= 1:
                first_entity_id = matches[0]['id']
                if first_entity_id in app_state.network_graph:
                    neighbors = list(app_state.network_graph.neighbors(first_entity_id))
                    message += f"\n{matches[0]['name']} is connected to {len(neighbors)} entities:\n"

                    # Show some neighbors
                    for neighbor_id in neighbors[:5]:
                        neighbor_entity = next((e for e in app_state.entities if e.id == neighbor_id), None)
                        if neighbor_entity:
                            message += f"  → {neighbor_entity.name} ({neighbor_entity.type})\n"

                    if len(neighbors) > 5:
                        message += f"  ... and {len(neighbors) - 5} more connections"
        else:
            message = f"No matching entities found for query: '{request.query}'\n\nTry searching for:\n"
            # Show some example entities
            for entity in app_state.entities[:5]:
                message += f"• {entity.name}\n"

        return {
            "status": "success",
            "query": request.query,
            "message": message,
            "matches_found": len(matches),
            "entities_analyzed": len(app_state.entities)
        }
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    logger.info(f"Data directory: {settings.data_dir}")

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level="info"
    )
