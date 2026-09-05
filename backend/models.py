"""
Data models for entity extraction and graph representation
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime


# ============================================================================
# ENTITY TYPES
# ============================================================================

class EntityType(str, Enum):
    """Types of entities in criminal network"""
    PERSON = "Person"
    PHONE = "Phone"
    VEHICLE = "Vehicle"
    BANK_ACCOUNT = "BankAccount"
    LOCATION = "Location"
    ORGANIZATION = "Organization"
    CASE = "Case"
    CRIME = "Crime"


class RelationType(str, Enum):
    """Types of relationships between entities"""
    USES_PHONE = "USES_PHONE"
    OWNS_VEHICLE = "OWNS_VEHICLE"
    OPERATES_ACCOUNT = "OPERATES_ACCOUNT"
    CALLED = "CALLED"
    TRANSFERRED = "TRANSFERRED"
    ACCUSED_WITH = "ACCUSED_WITH"
    ASSOCIATE_OF = "ASSOCIATE_OF"
    MEMBER_OF = "MEMBER_OF"
    ACCUSED_IN = "ACCUSED_IN"
    USED_IN = "USED_IN"


# ============================================================================
# ENTITY MODELS
# ============================================================================

class Entity(BaseModel):
    """Base entity model"""
    id: str
    type: EntityType
    name: str
    aliases: List[str] = Field(default_factory=list)
    attributes: Dict[str, Any] = Field(default_factory=dict)
    confidence: float = Field(ge=0.0, le=1.0, default=1.0)
    source: str = "extraction"
    extracted_at: datetime = Field(default_factory=datetime.now)

    class Config:
        use_enum_values = False


class Person(Entity):
    """Criminal person entity"""
    type: EntityType = EntityType.PERSON
    risk_score: float = Field(ge=0.0, le=10.0, default=5.0)
    gang_affiliation: Optional[str] = None
    known_crimes: List[str] = Field(default_factory=list)
    last_seen_location: Optional[str] = None


class Phone(Entity):
    """Phone number entity"""
    type: EntityType = EntityType.PHONE
    number: str
    imei: Optional[str] = None
    imsi: Optional[str] = None
    active: bool = True


class Vehicle(Entity):
    """Vehicle entity"""
    type: EntityType = EntityType.VEHICLE
    plate_number: str
    model: Optional[str] = None
    color: Optional[str] = None
    owner: Optional[str] = None


class BankAccount(Entity):
    """Bank account entity"""
    type: EntityType = EntityType.BANK_ACCOUNT
    account_number: str
    bank_name: Optional[str] = None
    ifsc_code: Optional[str] = None
    account_holder: Optional[str] = None


class Location(Entity):
    """Location entity"""
    type: EntityType = EntityType.LOCATION
    city: Optional[str] = None
    state: Optional[str] = None
    country: str = "India"
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class Case(Entity):
    """Criminal case/FIR entity"""
    type: EntityType = EntityType.CASE
    fir_number: str
    district: str
    police_station: str
    ipc_sections: List[str] = Field(default_factory=list)
    filing_date: Optional[datetime] = None


# ============================================================================
# RELATIONSHIP MODELS
# ============================================================================

class Relationship(BaseModel):
    """Base relationship model"""
    source_id: str
    target_id: str
    type: RelationType
    attributes: Dict[str, Any] = Field(default_factory=dict)
    confidence: float = Field(ge=0.0, le=1.0, default=1.0)
    weight: float = Field(ge=0.0, default=1.0)
    source: str = "extraction"
    created_at: datetime = Field(default_factory=datetime.now)

    class Config:
        use_enum_values = False


class CallRelationship(Relationship):
    """Call relationship (from CDR)"""
    type: RelationType = RelationType.CALLED
    call_count: int = 0
    total_duration_seconds: int = 0
    avg_duration_seconds: float = 0.0
    night_calls: int = 0  # Calls between 1 AM - 4 AM
    last_call_datetime: Optional[datetime] = None


class TransferRelationship(Relationship):
    """Financial transfer relationship"""
    type: RelationType = RelationType.TRANSFERRED
    transfer_count: int = 0
    total_amount_inr: float = 0.0
    avg_amount_inr: float = 0.0
    last_transfer_datetime: Optional[datetime] = None


# ============================================================================
# EXTRACTION RESPONSE MODELS
# ============================================================================

class ExtractionResult(BaseModel):
    """Result from entity extraction"""
    fir_id: str
    entities: List[Entity]
    relationships: List[Relationship]
    text_snippet: str
    extraction_confidence: float
    processing_time_ms: float
    error: Optional[str] = None


class ExtractionBatchResult(BaseModel):
    """Results from batch extraction"""
    total_files: int
    successful: int
    failed: int
    results: List[ExtractionResult]
    total_entities_extracted: int
    total_relationships_extracted: int
    processing_time_ms: float


class EntityResolutionResult(BaseModel):
    """Result from entity resolution/deduplication"""
    original_count: int
    merged_count: int
    merges: List[Dict[str, Any]]  # Which entities were merged
    final_entity_count: int


# ============================================================================
# GRAPH MODELS
# ============================================================================

class GraphNode(BaseModel):
    """Node in the criminal network graph"""
    id: str
    label: str
    type: EntityType
    size: float = 1.0
    color: str = "#666"
    metadata: Dict[str, Any] = Field(default_factory=dict)


class GraphEdge(BaseModel):
    """Edge in the criminal network graph"""
    source: str
    target: str
    label: str
    type: RelationType
    weight: float = 1.0
    color: str = "#999"
    metadata: Dict[str, Any] = Field(default_factory=dict)


class CriminalNetworkGraph(BaseModel):
    """Complete criminal network graph"""
    nodes: List[GraphNode]
    edges: List[GraphEdge]
    metadata: Dict[str, Any] = Field(default_factory=dict)
    node_count: int
    edge_count: int
    community_count: int = 0


# ============================================================================
# ANALYTICS MODELS
# ============================================================================

class CentralityScores(BaseModel):
    """Centrality scores for a node"""
    entity_id: str
    entity_name: str
    betweenness: float = 0.0  # How often on shortest paths
    closeness: float = 0.0    # Average distance to other nodes
    pagerank: float = 0.0     # Link-based importance
    degree: int = 0           # Number of connections
    risk_score: float = 0.0


class KeyPlayer(BaseModel):
    """Key influential player in network"""
    rank: int
    entity_id: str
    entity_name: str
    aliases: List[str]
    centrality_score: float
    risk_score: float
    connections: int
    gang_affiliation: Optional[str]
    known_crimes: List[str]


class Community(BaseModel):
    """Community/cluster in network"""
    id: int
    label: str
    members: List[str]
    member_count: int
    internal_connections: int
    external_connections: int
    cohesion_score: float


class Anomaly(BaseModel):
    """Detected anomaly in the network"""
    id: str
    type: str  # "night_call", "smurfing", "rapid_cascade", etc.
    severity: int = Field(ge=1, le=5)  # 1=low, 5=critical
    description: str
    entities_involved: List[str]
    evidence: Dict[str, Any]
    detected_at: datetime = Field(default_factory=datetime.now)


# ============================================================================
# API REQUEST/RESPONSE MODELS
# ============================================================================

class UploadRequest(BaseModel):
    """Request to upload and process criminal data"""
    fir_folder_path: str
    cdr_file_path: str
    transaction_file_path: str


class AnalyticsResponse(BaseModel):
    """Response with network analytics"""
    key_players: List[KeyPlayer]
    communities: List[Community]
    anomalies: List[Anomaly]
    graph: CriminalNetworkGraph


class QueryRequest(BaseModel):
    """Natural language query request"""
    query: str
    max_paths: int = 5


class PathResult(BaseModel):
    """Result of path finding in network"""
    start_entity: str
    end_entity: str
    path_nodes: List[str]
    path_edges: List[tuple]
    path_length: int
    summary: str
