"""
Criminal Network Analysis System - Graph Analytics Module
Implements network algorithms: PageRank, Centrality, Community Detection, Pathfinding
"""

import logging
from typing import List, Dict, Tuple, Set, Optional
import networkx as nx
from collections import defaultdict
import json

from models import (
    Entity, Person, Relationship, KeyPlayer, Community, Anomaly,
    CentralityScores, RelationType
)

logger = logging.getLogger(__name__)


# ============================================================================
# STEP 1: GRAPH BUILDER - Convert entities & relationships to NetworkX graph
# ============================================================================

class CriminalNetworkGraphBuilder:
    """
    Converts extracted entities and relationships into a NetworkX graph

    Why this matters:
    - Entities become nodes (people, phones, accounts, etc.)
    - Relationships become edges (calls, transfers, accusations)
    - Graph enables algorithmic analysis
    """

    def __init__(self):
        self.graph = nx.Graph()  # Undirected graph (connections are bidirectional)
        self.entity_map: Dict[str, Entity] = {}  # entity_id -> Entity object
        self.relationship_map: Dict[tuple, Relationship] = {}  # (source, target) -> Relationship

    def add_nodes_from_entities(self, entities: List[Entity]):
        """
        Step 1a: Add all entities as nodes to the graph

        Each node gets:
        - id: unique identifier
        - label: display name
        - type: entity type (Person, Phone, etc.)
        - attributes: additional metadata
        """
        for entity in entities:
            self.entity_map[entity.id] = entity

            # Create node with attributes
            node_attributes = {
                'label': entity.name,
                'type': entity.type.value if hasattr(entity.type, 'value') else str(entity.type),
                'confidence': entity.confidence,
                'aliases': entity.aliases if hasattr(entity, 'aliases') else [],
            }

            # Add person-specific attributes (risk score, gang, crimes)
            if isinstance(entity, Person):
                node_attributes.update({
                    'risk_score': entity.risk_score,
                    'gang_affiliation': entity.gang_affiliation,
                    'known_crimes': entity.known_crimes,
                })

            self.graph.add_node(entity.id, **node_attributes)

        logger.info(f"Added {len(entities)} nodes to graph")

    def add_edges_from_relationships(self, relationships: List[Relationship]):
        """
        Step 1b: Add all relationships as edges to the graph

        Each edge gets:
        - weight: importance (call frequency, transaction amount)
        - type: relationship type (CALLED, TRANSFERRED, etc.)
        - confidence: how certain we are
        - attributes: metadata
        """
        for rel in relationships:
            # Skip self-relationships (shouldn't exist after entity resolution)
            if rel.source_id == rel.target_id:
                continue

            # Create edge with attributes
            edge_attributes = {
                'type': rel.type.value if hasattr(rel.type, 'value') else str(rel.type),
                'weight': rel.weight,  # Used for algorithms
                'confidence': rel.confidence,
                'attributes': rel.attributes,
            }

            # Add relationship-specific details
            if hasattr(rel, 'call_count'):
                edge_attributes.update({
                    'call_count': rel.call_count,
                    'avg_duration': rel.avg_duration_seconds,
                    'night_calls': rel.night_calls,  # Suspicious pattern
                })

            if hasattr(rel, 'transfer_count'):
                edge_attributes.update({
                    'transfer_count': rel.transfer_count,
                    'total_amount': rel.total_amount_inr,
                    'is_smurfing': rel.attributes.get('is_smurfing', False),
                    'is_cascading': rel.attributes.get('is_cascading', False),
                })

            self.graph.add_edge(
                rel.source_id,
                rel.target_id,
                **edge_attributes
            )

        logger.info(f"Added {len(relationships)} edges to graph")

    def build(self, entities: List[Entity], relationships: List[Relationship]) -> nx.Graph:
        """
        Main method: Build complete graph

        Returns: NetworkX graph ready for analysis
        """
        self.add_nodes_from_entities(entities)
        self.add_edges_from_relationships(relationships)

        logger.info(f"Graph built: {self.graph.number_of_nodes()} nodes, "
                   f"{self.graph.number_of_edges()} edges")

        return self.graph


# ============================================================================
# STEP 2: CENTRALITY CALCULATOR - Identify key influencers
# ============================================================================

class CentralityAnalyzer:
    """
    Calculates various centrality metrics to identify key players in the network

    Why each metric matters:
    - PageRank: Google-style importance (who's most connected/influential)
    - Betweenness: Who bridges different groups (critical intermediaries)
    - Closeness: Who's closest to everyone (coordinators)
    - Degree: Raw connection count
    """

    def __init__(self, graph: nx.Graph, entity_map: Dict[str, Entity]):
        self.graph = graph
        self.entity_map = entity_map

    def calculate_pagerank(self, alpha: float = 0.85, max_iter: int = 100) -> Dict[str, float]:
        """
        PageRank Algorithm (what Google uses to rank websites)

        How it works:
        1. Start: each node has equal importance
        2. Iterate: importance flows through connections
        3. Result: nodes with more/better connections rank higher

        Example: If Ramesh Bhat talks to 15 people daily, he gets high PageRank
        """
        logger.info("Calculating PageRank...")
        pagerank = nx.pagerank(self.graph, alpha=alpha, max_iter=max_iter, weight='weight')
        logger.info(f"PageRank calculated: top node score = {max(pagerank.values()):.4f}")
        return pagerank

    def calculate_betweenness(self, weight: Optional[str] = 'weight') -> Dict[str, float]:
        """
        Betweenness Centrality (who bridges groups)

        How it works:
        1. Find all shortest paths between every pair of nodes
        2. Count how many paths pass through each node
        3. Nodes on many paths = high betweenness

        Example: Ramesh Bhat is intermediary between Gang A and Gang C
                 (money flows through him) → HIGH betweenness
        """
        logger.info("Calculating Betweenness Centrality...")
        betweenness = nx.betweenness_centrality(self.graph, weight=weight, normalized=True)
        logger.info(f"Betweenness calculated: top node score = {max(betweenness.values()):.4f}")
        return betweenness

    def calculate_closeness(self) -> Dict[str, float]:
        """
        Closeness Centrality (average distance to all other nodes)

        How it works:
        1. Calculate shortest path from each node to all others
        2. Average these distances
        3. Smaller average = node is "close" to everyone = high closeness

        Example: Vikram Sharma is 2 hops from everyone (coordinator)
        """
        logger.info("Calculating Closeness Centrality...")
        closeness = nx.closeness_centrality(self.graph, distance='weight')
        logger.info(f"Closeness calculated: top node score = {max(closeness.values()):.4f}")
        return closeness

    def calculate_degree_centrality(self) -> Dict[str, int]:
        """
        Degree Centrality (simple connection count)

        How it works:
        1. Count how many edges each node has
        2. More connections = higher degree

        Example: Ramesh Bhat has 15 connections (calls daily)
        """
        logger.info("Calculating Degree Centrality...")
        degree = dict(self.graph.degree())
        logger.info(f"Degree centrality calculated: max degree = {max(degree.values())}")
        return degree

    def get_centrality_scores(self) -> Dict[str, CentralityScores]:
        """
        Combine all centrality metrics into one score per entity

        Returns: Dict mapping entity_id -> CentralityScores object
        """
        pagerank = self.calculate_pagerank()
        betweenness = self.calculate_betweenness()
        closeness = self.calculate_closeness()
        degree = self.calculate_degree_centrality()

        # Normalize all scores to 0-1 range
        max_pagerank = max(pagerank.values()) if pagerank else 1
        max_betweenness = max(betweenness.values()) if betweenness else 1
        max_closeness = max(closeness.values()) if closeness else 1
        max_degree = max(degree.values()) if degree else 1

        scores = {}
        for entity_id in self.graph.nodes():
            entity = self.entity_map.get(entity_id)
            if not entity:
                continue

            score = CentralityScores(
                entity_id=entity_id,
                entity_name=entity.name,
                betweenness=betweenness.get(entity_id, 0) / max_betweenness,
                closeness=closeness.get(entity_id, 0) / max_closeness,
                pagerank=pagerank.get(entity_id, 0) / max_pagerank,
                degree=degree.get(entity_id, 0),
                risk_score=0.0  # Will be updated below
            )
            scores[entity_id] = score

        logger.info(f"Calculated centrality scores for {len(scores)} entities")
        return scores


# ============================================================================
# STEP 3: COMMUNITY DETECTOR - Identify gangs/groups
# ============================================================================

class CommunityDetector:
    """
    Uses Louvain algorithm to detect communities in the network

    What are communities?
    - Groups of nodes more densely connected to each other than to outsiders
    - In criminal networks: gangs, rings, organizations
    - Identified automatically without knowing "real" gangs
    """

    def __init__(self, graph: nx.Graph, entity_map: Dict[str, Entity]):
        self.graph = graph
        self.entity_map = entity_map

    def detect_communities_louvain(self) -> Dict[int, Set[str]]:
        """
        Louvain Algorithm for community detection

        How it works:
        1. Start: each node is its own community
        2. Move: nodes join communities that maximize modularity
        3. Repeat: until no improvements
        4. Result: communities emerge naturally

        Why it's good:
        - Fast (O(n log n))
        - Works on large networks
        - Finds hierarchical structure
        """
        logger.info("Running Louvain community detection...")

        try:
            from networkx.algorithms import community
            communities = list(community.greedy_modularity_communities(self.graph, weight='weight'))

            # Convert to dict: community_id -> set of node_ids
            community_dict = {}
            for i, comm in enumerate(communities):
                community_dict[i] = set(comm)

            logger.info(f"Found {len(communities)} communities using Louvain")
            return community_dict

        except ImportError:
            logger.warning("NetworkX community module not available, using simple greedy clustering")
            # Fallback: simple greedy algorithm
            return self._simple_greedy_communities()

    def _simple_greedy_communities(self) -> Dict[int, Set[str]]:
        """
        Fallback: Simple greedy community detection

        Method: Start with high-degree nodes, grow communities greedily
        """
        visited = set()
        communities = {}
        community_id = 0

        # Sort nodes by degree (highest first)
        nodes_by_degree = sorted(
            self.graph.nodes(),
            key=lambda n: self.graph.degree(n),
            reverse=True
        )

        for node in nodes_by_degree:
            if node in visited:
                continue

            # Start new community with this node
            community = {node}
            visited.add(node)

            # Greedily add neighbors if they increase cohesion
            neighbors = set(self.graph.neighbors(node))
            for neighbor in neighbors:
                if neighbor not in visited:
                    community.add(neighbor)
                    visited.add(neighbor)

            communities[community_id] = community
            community_id += 1

        logger.info(f"Found {len(communities)} communities using greedy method")
        return communities

    def get_community_objects(self, communities: Dict[int, Set[str]]) -> List[Community]:
        """
        Convert raw community data into Community objects

        Calculates for each community:
        - Member count
        - Internal connections (within community)
        - External connections (to other communities)
        - Cohesion score (internal vs external)
        """
        community_objects = []

        for comm_id, member_ids in communities.items():
            members = [self.entity_map[mid].name for mid in member_ids if mid in self.entity_map]

            # Count internal vs external edges
            internal_edges = 0
            external_edges = 0

            for node in member_ids:
                for neighbor in self.graph.neighbors(node):
                    if neighbor in member_ids:
                        internal_edges += 1  # Within community
                    else:
                        external_edges += 1  # To other community

            # Cohesion score: internal / (internal + external)
            total_edges = internal_edges + external_edges
            cohesion = internal_edges / total_edges if total_edges > 0 else 0

            community_obj = Community(
                id=comm_id,
                label=f"Community {comm_id + 1}",
                members=members,
                member_count=len(members),
                internal_connections=internal_edges // 2,  # Divide by 2 (undirected)
                external_connections=external_edges,
                cohesion_score=cohesion
            )
            community_objects.append(community_obj)

        logger.info(f"Created {len(community_objects)} Community objects")
        return community_objects


# ============================================================================
# STEP 4: PATH FINDER - Answer "who connects A to B?" queries
# ============================================================================

class PathFinder:
    """
    Finds paths between entities in the network

    Use cases:
    - "Who connects Gang A to Hawala Network?"
    - "What's the shortest path from Vikram to ₹50L transfer?"
    - "Who's the intermediary between Mumbai and Delhi?"
    """

    def __init__(self, graph: nx.Graph, entity_map: Dict[str, Entity]):
        self.graph = graph
        self.entity_map = entity_map

    def find_shortest_path(self, source_id: str, target_id: str) -> Optional[List[str]]:
        """
        Find shortest path between two entities

        Algorithm: Dijkstra with edge weights
        - Shorter paths are preferred
        - Higher weights = longer distance = less preferred

        Example: Path from Vikram to Ramesh Bhat:
        Vikram → (calls) → Rohit → (calls) → Ramesh Bhat
        """
        try:
            path = nx.shortest_path(
                self.graph,
                source=source_id,
                target=target_id,
                weight='weight'
            )
            logger.info(f"Found path of length {len(path)} from {source_id} to {target_id}")
            return path
        except nx.NetworkXNoPath:
            logger.warning(f"No path exists between {source_id} and {target_id}")
            return None

    def find_all_shortest_paths(self, source_id: str, target_id: str, cutoff: int = 5) -> List[List[str]]:
        """
        Find ALL shortest paths between two entities (up to cutoff count)

        Why multiple paths matter:
        - Shows all possible routes for information/money flow
        - Reveals alternative intermediaries
        - Identifies critical nodes (appear in all paths)
        """
        try:
            paths = list(nx.all_shortest_paths(
                self.graph,
                source=source_id,
                target=target_id,
                weight='weight'
            ))
            # Limit to cutoff paths
            paths = paths[:cutoff]
            logger.info(f"Found {len(paths)} shortest paths between {source_id} and {target_id}")
            return paths
        except (nx.NetworkXNoPath, nx.NodeNotFound):
            logger.warning(f"No paths found between {source_id} and {target_id}")
            return []

    def get_common_neighbors(self, entity_id1: str, entity_id2: str) -> Set[str]:
        """
        Find entities that connect two suspects

        Example: Who do both Vikram and Ramesh call?
        Useful for: identifying key intermediaries
        """
        neighbors1 = set(self.graph.neighbors(entity_id1))
        neighbors2 = set(self.graph.neighbors(entity_id2))
        common = neighbors1 & neighbors2

        logger.info(f"Found {len(common)} common neighbors between {entity_id1} and {entity_id2}")
        return common


# ============================================================================
# STEP 5: RISK CALCULATOR - Assign risk scores
# ============================================================================

class RiskCalculator:
    """
    Calculate risk scores for entities based on:
    - Centrality (how central are they)
    - Connections (how many suspicious connections)
    - Anomalies (involved in suspicious patterns)
    """

    def __init__(self, graph: nx.Graph, entity_map: Dict[str, Entity],
                 centrality_scores: Dict[str, CentralityScores]):
        self.graph = graph
        self.entity_map = entity_map
        self.centrality_scores = centrality_scores

    def calculate_risk_score(self, entity_id: str, base_scores: Dict[str, float] = None) -> float:
        """
        Calculate comprehensive risk score (0-10)

        Factors:
        1. Centrality (30%): More central = more influential = higher risk
        2. Connections (30%): Type & count of connections
        3. Anomalies (20%): Involvement in suspicious patterns
        4. Base (20%): Entity's inherent risk
        """
        if entity_id not in self.centrality_scores:
            return 0.0

        scores = self.centrality_scores[entity_id]

        # Factor 1: Centrality (PageRank + Betweenness)
        centrality_risk = (scores.pagerank * 0.6 + scores.betweenness * 0.4) * 3.0

        # Factor 2: Connection anomalies
        connection_risk = 0.0
        night_calls = 0
        smurfing_edges = 0

        for neighbor in self.graph.neighbors(entity_id):
            edge_data = self.graph.get_edge_data(entity_id, neighbor)
            if edge_data:
                if edge_data.get('night_calls', 0) > 0:
                    night_calls += 1
                if edge_data.get('is_smurfing', False):
                    smurfing_edges += 1

        connection_risk = (night_calls * 0.5 + smurfing_edges * 1.5) * 0.3

        # Factor 3: Base risk (from entity attributes)
        base_risk = 0.0
        if isinstance(self.entity_map[entity_id], Person):
            person = self.entity_map[entity_id]
            base_risk = person.risk_score * 0.2 if hasattr(person, 'risk_score') else 0.0

        # Combine factors (normalize to 0-10)
        total_risk = min(10.0, centrality_risk + connection_risk + base_risk)

        logger.debug(f"Risk score for {entity_id}: {total_risk:.2f} "
                    f"(centrality: {centrality_risk:.2f}, connection: {connection_risk:.2f})")

        return total_risk


# ============================================================================
# MAIN GRAPH ANALYTICS ENGINE
# ============================================================================

class CriminalNetworkAnalytics:
    """
    Main engine combining all analytics components

    Workflow:
    1. Build graph from entities & relationships
    2. Calculate centrality metrics
    3. Detect communities
    4. Calculate risk scores
    5. Identify key players
    """

    def __init__(self):
        self.graph = None
        self.entity_map = None
        self.centrality_scores = None
        self.communities = None

    def analyze(self, entities: List[Entity], relationships: List[Relationship]):
        """
        Complete analytics pipeline

        Returns: All analytics results
        """
        logger.info("="*60)
        logger.info("STARTING GRAPH ANALYTICS PIPELINE")
        logger.info("="*60)

        # Step 1: Build graph
        logger.info("\n[STEP 1/5] Building NetworkX graph...")
        builder = CriminalNetworkGraphBuilder()
        self.graph = builder.build(entities, relationships)
        self.entity_map = builder.entity_map

        # Step 2: Calculate centrality
        logger.info("\n[STEP 2/5] Calculating centrality metrics...")
        analyzer = CentralityAnalyzer(self.graph, self.entity_map)
        self.centrality_scores = analyzer.get_centrality_scores()

        # Step 3: Detect communities
        logger.info("\n[STEP 3/5] Detecting communities (gangs)...")
        detector = CommunityDetector(self.graph, self.entity_map)
        raw_communities = detector.detect_communities_louvain()
        self.communities = detector.get_community_objects(raw_communities)

        # Step 4: Calculate risk scores
        logger.info("\n[STEP 4/5] Calculating risk scores...")
        risk_calculator = RiskCalculator(self.graph, self.entity_map, self.centrality_scores)
        for entity_id in self.centrality_scores:
            risk = risk_calculator.calculate_risk_score(entity_id)
            self.centrality_scores[entity_id].risk_score = risk

        # Step 5: Identify key players
        logger.info("\n[STEP 5/5] Identifying key players...")
        key_players = self._get_key_players()

        logger.info("="*60)
        logger.info("GRAPH ANALYTICS COMPLETE")
        logger.info(f"  • Nodes: {self.graph.number_of_nodes()}")
        logger.info(f"  • Edges: {self.graph.number_of_edges()}")
        logger.info(f"  • Communities: {len(self.communities)}")
        logger.info(f"  • Key Players: {len(key_players)}")
        logger.info("="*60)

        return {
            'graph': self.graph,
            'key_players': key_players,
            'communities': self.communities,
            'centrality_scores': self.centrality_scores
        }

    def _get_key_players(self, top_n: int = 10) -> List[KeyPlayer]:
        """
        Rank entities by risk score and create KeyPlayer objects

        Top players are those most central + most risky
        """
        if not self.centrality_scores:
            return []

        # Sort by risk score
        sorted_scores = sorted(
            self.centrality_scores.values(),
            key=lambda s: s.risk_score,
            reverse=True
        )

        key_players = []
        for rank, score in enumerate(sorted_scores[:top_n], 1):
            entity = self.entity_map[score.entity_id]
            aliases = entity.aliases if hasattr(entity, 'aliases') else []
            crimes = entity.known_crimes if isinstance(entity, Person) else []
            gang = entity.gang_affiliation if isinstance(entity, Person) else None

            key_player = KeyPlayer(
                rank=rank,
                entity_id=score.entity_id,
                entity_name=score.entity_name,
                aliases=aliases,
                centrality_score=score.pagerank,  # Use PageRank as main centrality
                risk_score=score.risk_score,
                connections=score.degree,
                gang_affiliation=gang,
                known_crimes=crimes
            )
            key_players.append(key_player)

        return key_players
