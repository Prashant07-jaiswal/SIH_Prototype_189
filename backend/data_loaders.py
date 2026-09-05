"""
Data Loaders Module
Handles loading and parsing of CDR and financial transaction data
"""

import logging
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime
import pandas as pd

from models import (
    Entity, Person, Phone, BankAccount,
    Relationship, CallRelationship, TransferRelationship, RelationType
)

logger = logging.getLogger(__name__)


# ============================================================================
# FIR LOADER
# ============================================================================

def load_fir_folder(folder_path: Path) -> List[tuple]:
    """
    Load all FIR documents from a folder

    Returns:
        List of (fir_id, text_content) tuples
    """
    fir_folder = Path(folder_path)

    if not fir_folder.exists():
        logger.error(f"FIR folder not found: {fir_folder}")
        return []

    firs = []
    for fir_file in fir_folder.glob("*.txt"):
        try:
            text = fir_file.read_text(encoding='utf-8')
            firs.append((fir_file.stem, text))
            logger.debug(f"Loaded FIR: {fir_file.name}")
        except Exception as e:
            logger.error(f"Error loading FIR {fir_file.name}: {str(e)}")

    logger.info(f"Loaded {len(firs)} FIR documents from {fir_folder}")
    return firs


# ============================================================================
# CDR LOADER
# ============================================================================

def load_cdr_csv(csv_path: Path) -> pd.DataFrame:
    """Load CDR CSV file"""
    try:
        df = pd.read_csv(csv_path)
        logger.info(f"Loaded CDR CSV with {len(df)} records from {csv_path}")
        return df
    except Exception as e:
        logger.error(f"Error loading CDR CSV: {str(e)}")
        return pd.DataFrame()


def parse_relationships_from_cdr(
    cdr_path: Path,
    entities: List[Entity]
) -> List[CallRelationship]:
    """
    Parse CDR CSV and create call relationships between phone entities

    Args:
        cdr_path: Path to call_detail_records.csv
        entities: List of existing entities to link to

    Returns:
        List of CallRelationship objects
    """
    df = load_cdr_csv(cdr_path)

    if df.empty:
        logger.warning("CDR CSV is empty or could not be loaded")
        return []

    # Build phone entity map
    phone_map: Dict[str, str] = {}  # normalized_phone -> entity_id
    for entity in entities:
        if isinstance(entity, Phone):
            normalized = entity.number.replace('+91', '').replace('0', '')[-10:]
            phone_map[normalized] = entity.id

    relationships = []
    call_logs: Dict[tuple, Dict] = {}  # (caller, receiver) -> aggregated data

    # Aggregate CDR records by caller-receiver pair
    for _, row in df.iterrows():
        caller = str(row['caller']).replace('+91', '').replace('0', '')[-10:]
        receiver = str(row['receiver']).replace('+91', '').replace('0', '')[-10:]

        # Skip if we don't have these phones in our entity map
        if caller not in phone_map or receiver not in phone_map:
            continue

        key = (caller, receiver)

        if key not in call_logs:
            call_logs[key] = {
                'count': 0,
                'total_duration': 0,
                'night_calls': 0,
                'last_call': None,
                'durations': []
            }

        # Parse call time
        try:
            call_datetime = pd.to_datetime(row['call_datetime'])
            hour = call_datetime.hour

            call_logs[key]['count'] += 1
            call_logs[key]['total_duration'] += int(row['duration_seconds'])
            call_logs[key]['durations'].append(int(row['duration_seconds']))

            # Count night calls (1 AM - 4 AM)
            if 1 <= hour <= 4:
                call_logs[key]['night_calls'] += 1

            if call_logs[key]['last_call'] is None or call_datetime > call_logs[key]['last_call']:
                call_logs[key]['last_call'] = call_datetime

        except Exception as e:
            logger.debug(f"Error parsing CDR row: {str(e)}")
            continue

    # Create CallRelationship objects
    for (caller, receiver), data in call_logs.items():
        if data['count'] > 0:
            caller_id = phone_map[caller]
            receiver_id = phone_map[receiver]

            avg_duration = data['total_duration'] / data['count']

            # Calculate confidence based on frequency and night calls
            base_confidence = min(1.0, data['count'] / 20.0)  # More calls = higher confidence
            night_call_boost = 0.1 if data['night_calls'] > 0 else 0.0  # Night calls suspicious
            confidence = min(1.0, base_confidence + night_call_boost)

            relationship = CallRelationship(
                source_id=caller_id,
                target_id=receiver_id,
                call_count=data['count'],
                total_duration_seconds=data['total_duration'],
                avg_duration_seconds=round(avg_duration, 2),
                night_calls=data['night_calls'],
                last_call_datetime=data['last_call'],
                weight=data['count'],  # Weight = call frequency
                confidence=confidence,
                source="cdr"
            )
            relationships.append(relationship)

    logger.info(f"Created {len(relationships)} call relationships from CDR data")
    return relationships


# ============================================================================
# FINANCIAL TRANSACTION LOADER
# ============================================================================

def load_financial_transactions(csv_path: Path) -> pd.DataFrame:
    """Load financial transactions CSV file"""
    try:
        df = pd.read_csv(csv_path)
        logger.info(f"Loaded financial transactions with {len(df)} records from {csv_path}")
        return df
    except Exception as e:
        logger.error(f"Error loading financial transactions CSV: {str(e)}")
        return pd.DataFrame()


def detect_smurfing_pattern(amounts: List[float]) -> bool:
    """
    Detect smurfing pattern: multiple transfers just below reporting threshold (10L)
    Returns True if pattern detected
    """
    reporting_threshold = 1000000  # 10 lakh
    below_threshold = [a for a in amounts if a < reporting_threshold]

    # Smurfing: 3+ transfers below threshold
    if len(below_threshold) >= 3:
        return True

    return False


def detect_rapid_cascade(transactions: List[Dict]) -> bool:
    """
    Detect rapid cascading: fund movement through multiple banks in short time
    Returns True if pattern detected
    """
    if len(transactions) < 3:
        return False

    # Sort by time
    sorted_txns = sorted(transactions, key=lambda t: t['datetime'])

    # Check if multiple transfers within 2 hours
    time_window = 2 * 3600  # 2 hours in seconds

    for i, txn in enumerate(sorted_txns):
        following = [t for t in sorted_txns[i+1:]]
        if not following:
            continue

        time_diff = (following[-1]['datetime'] - txn['datetime']).total_seconds()

        if time_diff <= time_window and len(following) >= 2:
            return True

    return False


def parse_relationships_from_transactions(
    transaction_path: Path,
    entities: List[Entity]
) -> List[TransferRelationship]:
    """
    Parse financial transaction CSV and create transfer relationships

    Args:
        transaction_path: Path to financial_transactions.csv
        entities: List of existing entities to link to

    Returns:
        List of TransferRelationship objects
    """
    df = load_financial_transactions(transaction_path)

    if df.empty:
        logger.warning("Financial transactions CSV is empty or could not be loaded")
        return []

    # Build account entity map
    account_map: Dict[str, str] = {}  # normalized_account -> entity_id
    for entity in entities:
        if isinstance(entity, BankAccount):
            normalized = entity.account_number.replace('_ACC_', '').lower()
            account_map[normalized] = entity.id

    relationships = []
    transfer_logs: Dict[tuple, Dict] = {}  # (sender, receiver) -> aggregated data

    # Aggregate transactions by sender-receiver pair
    for _, row in df.iterrows():
        sender = str(row['sender_account']).replace('_ACC_', '').lower()
        receiver = str(row['receiver_account']).replace('_ACC_', '').lower()

        # Skip if we don't have these accounts
        if sender not in account_map or receiver not in account_map:
            continue

        key = (sender, receiver)

        if key not in transfer_logs:
            transfer_logs[key] = {
                'count': 0,
                'total_amount': 0,
                'last_transfer': None,
                'amounts': [],
                'transactions': []
            }

        try:
            amount = float(row['amount_inr'])
            transfer_datetime = pd.to_datetime(row['transaction_datetime'])

            transfer_logs[key]['count'] += 1
            transfer_logs[key]['total_amount'] += amount
            transfer_logs[key]['amounts'].append(amount)
            transfer_logs[key]['transactions'].append({
                'datetime': transfer_datetime,
                'amount': amount
            })

            if transfer_logs[key]['last_transfer'] is None or transfer_datetime > transfer_logs[key]['last_transfer']:
                transfer_logs[key]['last_transfer'] = transfer_datetime

        except Exception as e:
            logger.debug(f"Error parsing transaction row: {str(e)}")
            continue

    # Create TransferRelationship objects
    for (sender, receiver), data in transfer_logs.items():
        if data['count'] > 0:
            sender_id = account_map[sender]
            receiver_id = account_map[receiver]

            avg_amount = data['total_amount'] / data['count']

            # Detect anomalies
            is_smurfing = detect_smurfing_pattern(data['amounts'])
            is_cascading = detect_rapid_cascade(data['transactions'])

            # Calculate confidence based on total amount and patterns
            base_confidence = min(1.0, data['total_amount'] / 5000000)  # 50L threshold
            anomaly_boost = 0.2 if (is_smurfing or is_cascading) else 0.0
            confidence = min(1.0, base_confidence + anomaly_boost)

            attributes = {
                'is_smurfing': is_smurfing,
                'is_cascading': is_cascading,
            }

            relationship = TransferRelationship(
                source_id=sender_id,
                target_id=receiver_id,
                transfer_count=data['count'],
                total_amount_inr=round(data['total_amount'], 2),
                avg_amount_inr=round(avg_amount, 2),
                last_transfer_datetime=data['last_transfer'],
                weight=min(100, data['total_amount'] / 100000),  # Weight = amount (normalized)
                confidence=confidence,
                source="financial_transactions",
                attributes=attributes
            )
            relationships.append(relationship)

    logger.info(f"Created {len(relationships)} transfer relationships from financial data")
    return relationships


# ============================================================================
# METADATA LOADER
# ============================================================================

def load_metadata(metadata_path: Path) -> Dict:
    """Load metadata JSON file"""
    try:
        with open(metadata_path, 'r', encoding='utf-8') as f:
            import json
            metadata = json.load(f)
            logger.info(f"Loaded metadata from {metadata_path}")
            return metadata
    except Exception as e:
        logger.error(f"Error loading metadata: {str(e)}")
        return {}


# ============================================================================
# COMPLETE DATA LOADING PIPELINE
# ============================================================================

def load_all_data(
    fir_folder: Path,
    cdr_path: Path,
    transaction_path: Path,
    metadata_path: Path
) -> tuple:
    """
    Load all data sources

    Returns:
        Tuple of (all_entities, all_relationships, metadata)
    """
    logger.info("="*60)
    logger.info("Starting complete data loading pipeline")
    logger.info("="*60)

    # Load metadata first (for context)
    metadata = load_metadata(metadata_path)

    # Load FIRs and extract entities (done in extraction.py)
    # This function just prepares CDR and transaction data

    logger.info("Data loading pipeline complete")

    return metadata
