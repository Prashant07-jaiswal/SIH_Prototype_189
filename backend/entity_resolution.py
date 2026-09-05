"""
Entity Resolution Module
Handles deduplication and merging of entities across multiple data sources
Solves the problem of "same criminal with different names/phones across districts"
"""

import logging
from typing import List, Dict, Tuple, Set
from difflib import SequenceMatcher

# Import rapidfuzz - try different import methods for compatibility
try:
    from rapidfuzz import fuzz
except ImportError:
    try:
        from rapidfuzz.fuzz import ratio as fuzz_ratio
        # Create a compatible fuzz object
        class fuzz:
            @staticmethod
            def token_set_ratio(s1, s2):
                from rapidfuzz.fuzz import token_set_ratio
                return token_set_ratio(s1, s2)
    except ImportError:
        # Fallback to difflib if rapidfuzz doesn't work
        from difflib import SequenceMatcher
        class fuzz:
            @staticmethod
            def token_set_ratio(s1, s2):
                return SequenceMatcher(None, s1.lower(), s2.lower()).ratio() * 100

from models import Entity, Person, Phone, Vehicle, BankAccount, Relationship, RelationType

logger = logging.getLogger(__name__)


# ============================================================================
# ENTITY RESOLUTION ENGINE
# ============================================================================

class EntityResolver:
    """Resolves and deduplicates entities using multiple matching strategies"""

    def __init__(self, name_similarity_threshold: float = 0.88):
        self.name_similarity_threshold = name_similarity_threshold
        self.entity_clusters: Dict[str, List[str]] = {}  # Maps representative ID to cluster members

    def calculate_string_similarity(self, str1: str, str2: str) -> float:
        """
        Calculate similarity between two strings using Jaro-Winkler distance
        Returns: 0.0 (completely different) to 1.0 (identical)
        """
        return fuzz.token_set_ratio(str1.lower(), str2.lower()) / 100.0

    def are_phones_same(self, phone1: str, phone2: str) -> bool:
        """Check if two phone numbers refer to the same phone"""
        # Normalize to 10-digit format
        p1 = phone1.replace('+91', '').replace('0', '')[-10:]
        p2 = phone2.replace('+91', '').replace('0', '')[-10:]
        return p1 == p2

    def are_accounts_same(self, acc1: str, acc2: str) -> bool:
        """Check if two accounts are the same"""
        # Remove common prefixes/suffixes and compare
        a1 = acc1.replace('_ACC_', '').replace('_', '').lower()
        a2 = acc2.replace('_ACC_', '').replace('_', '').lower()
        return a1 == a2

    def are_vehicles_same(self, plate1: str, plate2: str) -> bool:
        """Check if two vehicle plates are the same"""
        return plate1.upper() == plate2.upper()

    # ========================================================================
    # TIER 1: HARD ANCHOR MATCHING (100% confidence)
    # ========================================================================

    def find_hard_anchor_matches(self, entities: List[Entity]) -> List[Tuple[str, str]]:
        """
        Find entities with identical hard anchors:
        - Same phone number
        - Same vehicle plate
        - Same bank account
        Returns list of (entity1_id, entity2_id) pairs to merge
        """
        matches = []
        phones_map: Dict[str, List[str]] = {}  # phone -> entity_ids
        vehicles_map: Dict[str, List[str]] = {}
        accounts_map: Dict[str, List[str]] = {}

        # Group by anchors
        for entity in entities:
            if isinstance(entity, Phone):
                normalized = entity.number.replace('+91', '').replace('0', '')[-10:]
                if normalized not in phones_map:
                    phones_map[normalized] = []
                phones_map[normalized].append(entity.id)

            elif isinstance(entity, Vehicle):
                plate = entity.plate_number.upper()
                if plate not in vehicles_map:
                    vehicles_map[plate] = []
                vehicles_map[plate].append(entity.id)

            elif isinstance(entity, BankAccount):
                acc = entity.account_number.replace('_ACC_', '').lower()
                if acc not in accounts_map:
                    accounts_map[acc] = []
                accounts_map[acc].append(entity.id)

        # Find duplicates
        for phone, entity_ids in phones_map.items():
            if len(entity_ids) > 1:
                for i in range(len(entity_ids) - 1):
                    matches.append((entity_ids[0], entity_ids[i + 1]))

        for plate, entity_ids in vehicles_map.items():
            if len(entity_ids) > 1:
                for i in range(len(entity_ids) - 1):
                    matches.append((entity_ids[0], entity_ids[i + 1]))

        for acc, entity_ids in accounts_map.items():
            if len(entity_ids) > 1:
                for i in range(len(entity_ids) - 1):
                    matches.append((entity_ids[0], entity_ids[i + 1]))

        return matches

    # ========================================================================
    # TIER 2: FUZZY MATCHING (fuzzy name + phone similarity)
    # ========================================================================

    def find_fuzzy_matches(self, entities: List[Entity]) -> List[Tuple[str, str, float]]:
        """
        Find potential matches using fuzzy name matching and phone similarity
        Returns list of (entity1_id, entity2_id, confidence) tuples
        """
        matches = []
        persons: List[Person] = [e for e in entities if isinstance(e, Person)]

        for i, person1 in enumerate(persons):
            for person2 in persons[i + 1:]:
                # Name similarity
                name_sim = self.calculate_string_similarity(person1.name, person2.name)

                # Check if names are similar enough
                if name_sim < self.name_similarity_threshold:
                    continue

                # Extract phone IDs for these persons (from relationships)
                # This would require access to relationships, so we'll do basic check
                confidence = name_sim

                if confidence >= self.name_similarity_threshold:
                    matches.append((person1.id, person2.id, confidence))

        return matches

    # ========================================================================
    # TIER 3: GRAPH CONTEXT MATCHING (co-occurrence of connections)
    # ========================================================================

    def find_graph_context_matches(
        self,
        entities: List[Entity],
        relationships: List[Relationship],
        common_neighbors_threshold: int = 2
    ) -> List[Tuple[str, str, float]]:
        """
        Find matches based on shared connections in the network.
        If two suspects are both connected to 2+ common entities, likely same person
        """
        matches = []

        # Build adjacency
        adjacency: Dict[str, Set[str]] = {}
        for entity in entities:
            adjacency[entity.id] = set()

        for rel in relationships:
            if rel.type not in [RelationType.USES_PHONE, RelationType.OWNS_VEHICLE,
                               RelationType.OPERATES_ACCOUNT]:
                # Skip relationships like USES_PHONE, focus on person-to-person
                continue

            adjacency[rel.source_id].add(rel.target_id)
            adjacency[rel.target_id].add(rel.source_id)

        # Find pairs with common neighbors
        persons: List[Person] = [e for e in entities if isinstance(e, Person)]

        for i, person1 in enumerate(persons):
            for person2 in persons[i + 1:]:
                neighbors1 = adjacency.get(person1.id, set())
                neighbors2 = adjacency.get(person2.id, set())

                common = neighbors1 & neighbors2
                if len(common) >= common_neighbors_threshold:
                    confidence = min(1.0, len(common) / 5.0)  # Normalize confidence
                    matches.append((person1.id, person2.id, confidence))

        return matches

    # ========================================================================
    # MERGING LOGIC
    # ========================================================================

    def merge_entities(
        self,
        entities: List[Entity],
        relationships: List[Relationship],
        hard_anchor_matches: List[Tuple[str, str]],
        fuzzy_matches: List[Tuple[str, str, float]],
        graph_context_matches: List[Tuple[str, str, float]]
    ) -> Tuple[List[Entity], List[Relationship], List]:
        """
        Merge entities based on all matching tiers
        Returns deduplicated entities and updated relationships
        """
        merged = set()  # Track which entities have been merged
        entity_map: Dict[str, str] = {}  # Old ID -> New ID (representative)

        # TIER 1: Hard anchors (100% merge)
        for entity1_id, entity2_id in hard_anchor_matches:
            if entity1_id not in merged and entity2_id not in merged:
                logger.info(f"[TIER 1] Merging {entity2_id} into {entity1_id} (hard anchor)")
                entity_map[entity2_id] = entity1_id
                merged.add(entity2_id)

        # TIER 2: Fuzzy matches (high confidence merge)
        for entity1_id, entity2_id, confidence in fuzzy_matches:
            if entity1_id not in merged and entity2_id not in merged:
                if confidence >= self.name_similarity_threshold:
                    logger.info(
                        f"[TIER 2] Merging {entity2_id} into {entity1_id} "
                        f"(fuzzy match, confidence={confidence:.2f})"
                    )
                    entity_map[entity2_id] = entity1_id
                    merged.add(entity2_id)

        # TIER 3: Graph context (suggest, don't auto-merge)
        suggestions = []
        for entity1_id, entity2_id, confidence in graph_context_matches:
            if entity1_id not in merged and entity2_id not in merged:
                if confidence >= 0.60:  # Lower threshold for suggestions
                    suggestions.append((entity1_id, entity2_id, confidence))
                    logger.info(
                        f"[TIER 3] Suggested merge {entity2_id} into {entity1_id} "
                        f"(graph context, confidence={confidence:.2f})"
                    )

        # Create deduplicated entity list
        # NOTE: Always keep Vehicle and BankAccount entities even if merged,
        # since they represent distinct physical assets that shouldn't be completely removed
        merged_entities = [
            entity for entity in entities
            if entity.id not in merged or isinstance(entity, (Vehicle, BankAccount))
        ]

        # Update relationships to point to merged entity IDs
        merged_relationships = []
        for rel in relationships:
            new_source = entity_map.get(rel.source_id, rel.source_id)
            new_target = entity_map.get(rel.target_id, rel.target_id)

            # Skip self-relationships
            if new_source == new_target:
                continue

            rel.source_id = new_source
            rel.target_id = new_target
            merged_relationships.append(rel)

        return merged_entities, merged_relationships, suggestions

    # ========================================================================
    # PUBLIC INTERFACE
    # ========================================================================

    def resolve(
        self,
        entities: List[Entity],
        relationships: List[Relationship]
    ) -> Tuple[List[Entity], List[Relationship], Dict]:
        """
        Perform complete entity resolution pipeline

        Returns:
            - Deduplicated entities
            - Updated relationships
            - Metadata about merges performed
        """
        logger.info(f"Starting entity resolution: {len(entities)} entities, {len(relationships)} relationships")

        original_count = len(entities)

        # Run all matching tiers
        hard_matches = self.find_hard_anchor_matches(entities)
        fuzzy_matches = self.find_fuzzy_matches(entities)
        graph_matches = self.find_graph_context_matches(entities, relationships)

        logger.debug(f"Hard anchor matches: {len(hard_matches)}")
        logger.debug(f"Fuzzy matches: {len(fuzzy_matches)}")
        logger.debug(f"Graph context matches: {len(graph_matches)}")

        # Merge
        merged_entities, merged_relationships, suggestions = self.merge_entities(
            entities,
            relationships,
            hard_matches,
            fuzzy_matches,
            graph_matches
        )

        final_count = len(merged_entities)
        merged_count = original_count - final_count

        metadata = {
            "original_count": original_count,
            "final_count": final_count,
            "merged_count": merged_count,
            "hard_matches": len(hard_matches),
            "fuzzy_matches": len(fuzzy_matches),
            "graph_matches": len(graph_matches),
            "suggestions": suggestions
        }

        logger.info(f"Entity resolution complete: {original_count} → {final_count} entities "
                   f"({merged_count} merged)")

        return merged_entities, merged_relationships, metadata


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def resolve_entities(
    entities: List[Entity],
    relationships: List[Relationship],
    similarity_threshold: float = 0.88
) -> Tuple[List[Entity], List[Relationship], Dict]:
    """
    Convenience function to resolve entities in one call

    Args:
        entities: List of extracted entities
        relationships: List of relationships between entities
        similarity_threshold: Fuzzy matching threshold (0.0-1.0)

    Returns:
        Tuple of (resolved_entities, updated_relationships, metadata)
    """
    resolver = EntityResolver(name_similarity_threshold=similarity_threshold)
    return resolver.resolve(entities, relationships)
