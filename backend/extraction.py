"""
NLP Entity Extraction Module
Handles regex-based and LLM-based entity extraction from FIRs
"""

import re
import json
from typing import List, Dict, Any, Tuple, Optional
from datetime import datetime
import logging

from models import (
    Entity, Person, Phone, Vehicle, BankAccount, Location, Case,
    Relationship, ExtractionResult, EntityType, RelationType
)

logger = logging.getLogger(__name__)


# ============================================================================
# REGEX PATTERNS FOR DETERMINISTIC EXTRACTION
# ============================================================================

class RegexPatterns:
    """Collection of regex patterns for entity extraction"""

    # Indian phone numbers: +91 or 0, followed by 10 digits
    PHONE = re.compile(r'(?:\+91|0)?[6-9]\d{9}\b')

    # Indian vehicle registration: 2 letters, 2 digits, 1-2 letters, 4 digits
    # Example: MH02AB1234, UP32CD5678
    VEHICLE = re.compile(r'\b[A-Z]{2}\d{2}[A-Z]{1,2}\d{4}\b')

    # Bank account (flexible pattern): XXXX_ACC_XXXX or just account number
    BANK_ACCOUNT = re.compile(r'\b[A-Z]+_?ACC_?\d+\b|(?:Account|Acc|A/C)\s*(?:No|#)?[:\s]*(\d+)')

    # IFSC code: 4 letters, 0, 6 digits
    IFSC = re.compile(r'\b[A-Z]{4}0[A-Z0-9]{6}\b')

    # Aadhaar: 12 digits
    AADHAAR = re.compile(r'\b\d{12}\b')

    # PAN: 5 letters, 4 digits, 1 letter
    PAN = re.compile(r'\b[A-Z]{5}[0-9]{4}[A-Z]{1}\b')

    # IPC Sections: Section followed by digits/letters
    IPC_SECTION = re.compile(r'(?:Section|Sec|S\.|IPC)\s+([0-9A-Za-z]+)')

    # Dates: Various Indian date formats
    DATE = re.compile(r'\d{1,2}[-/]\d{1,2}[-/]\d{2,4}|\d{1,2}\s(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s\d{2,4}')

    # Amount in Rupees: ₹ symbol or "Rs" followed by number
    AMOUNT = re.compile(r'(?:₹|Rs\.?)\s*([0-9,]+)')

    # FIR Number: District code + 4 digits
    FIR_NUMBER = re.compile(r'\b(?:FIR|FIR No\.?)\s*([A-Z]+/\d+/\d+|[A-Z]+/\d+)\b')

    # Police Station name
    POLICE_STATION = re.compile(r'Police Station|P\.?S\.|थाना')

    # Crimes/offences
    CRIME_KEYWORDS = {
        'drug': ['drug', 'narcotic', 'cannabis', 'mdma', 'heroin', 'cocaine'],
        'theft': ['theft', 'चोरी', 'चुराई', 'robbery', 'डकैती'],
        'assault': ['assault', 'मारपीट', 'वार', 'हमला', 'beating'],
        'fraud': ['fraud', 'cheating', 'forgery', 'fake', 'जालसाजी', 'धोखाधड़ी'],
        'money_laundering': ['laundering', 'hawala', 'हवाला', 'smurfing', 'structuring'],
        'extortion': ['extortion', 'blackmail', 'वसूली', 'ब्लैकमेल'],
    }


# ============================================================================
# ENTITY EXTRACTOR
# ============================================================================

class EntityExtractor:
    """Extracts entities from FIR text using regex patterns"""

    def __init__(self):
        self.patterns = RegexPatterns()

    def extract_phones(self, text: str) -> List[Phone]:
        """Extract phone numbers from text"""
        phones = []
        for match in self.patterns.PHONE.finditer(text):
            phone_number = match.group(0)
            # Normalize to +91 format
            if not phone_number.startswith('+'):
                phone_number = '+91' + phone_number[-10:] if phone_number.startswith('0') else '+91' + phone_number

            phone = Phone(
                id=f"phone_{phone_number}",
                name=phone_number,
                number=phone_number,
                confidence=0.95
            )
            phones.append(phone)
        return phones

    def extract_vehicles(self, text: str) -> List[Vehicle]:
        """Extract vehicle registration plates"""
        vehicles = []
        for match in self.patterns.VEHICLE.finditer(text):
            plate = match.group(0)
            vehicle = Vehicle(
                id=f"vehicle_{plate}",
                name=f"Vehicle {plate}",
                plate_number=plate,
                confidence=0.95
            )
            vehicles.append(vehicle)
        return vehicles

    def extract_bank_accounts(self, text: str) -> List[BankAccount]:
        """Extract bank account numbers"""
        accounts = []
        for match in self.patterns.BANK_ACCOUNT.finditer(text):
            account = match.group(0)
            bank_account = BankAccount(
                id=f"account_{account}",
                name=account,
                account_number=account,
                confidence=0.90
            )
            accounts.append(bank_account)

        # Also extract IFSC codes
        for match in self.patterns.IFSC.finditer(text):
            ifsc = match.group(0)
            # Try to find associated account nearby
            logger.debug(f"Found IFSC: {ifsc}")

        return accounts

    def extract_case_details(self, text: str) -> Optional[Case]:
        """Extract case/FIR details"""
        # FIR Number
        fir_match = self.patterns.FIR_NUMBER.search(text)
        fir_number = fir_match.group(1) if fir_match else "UNKNOWN"

        # District (usually at beginning)
        district_match = re.search(r'District[:\s]+([A-Za-z\s]+)', text)
        district = district_match.group(1).strip() if district_match else "Unknown"

        # Police Station
        ps_match = re.search(r'Police Station[:\s]+([A-Za-z\s]+)', text)
        police_station = ps_match.group(1).strip() if ps_match else "Unknown"

        # Date
        date_match = self.patterns.DATE.search(text)
        filing_date = None
        if date_match:
            try:
                date_str = date_match.group(0)
                # Try to parse the date
                filing_date = datetime.strptime(date_str, "%d-%m-%Y") if '-' in date_str else None
            except:
                pass

        # IPC Sections
        ipc_sections = []
        for match in self.patterns.IPC_SECTION.finditer(text):
            section = match.group(1)
            ipc_sections.append(section)

        case = Case(
            id=f"case_{fir_number}",
            name=fir_number,
            fir_number=fir_number,
            district=district,
            police_station=police_station,
            ipc_sections=ipc_sections,
            filing_date=filing_date,
            confidence=0.85
        )
        return case

    def extract_amounts(self, text: str) -> List[Tuple[float, str]]:
        """Extract monetary amounts mentioned in text"""
        amounts = []
        for match in self.patterns.AMOUNT.finditer(text):
            amount_str = match.group(1).replace(',', '')
            try:
                amount = float(amount_str)
                amounts.append((amount, match.group(0)))
            except ValueError:
                pass
        return amounts

    def extract_crimes(self, text: str) -> List[str]:
        """Extract crime types mentioned in text"""
        crimes = []
        text_lower = text.lower()

        for crime_type, keywords in self.patterns.CRIME_KEYWORDS.items():
            for keyword in keywords:
                if keyword in text_lower:
                    crimes.append(crime_type)
                    break

        return list(set(crimes))

    def extract_person_names(self, text: str) -> List[Tuple[str, List[str]]]:
        """
        Extract person names and aliases using simple patterns.
        Pattern: Name (उर्फ़/aka Alias1, Alias2)
        Supports: "Name (उर्फ़ Alias1, Alias2)" or "Name aka Alias1, Alias2"
        """
        persons = []

        # Pattern 1: Name followed by parenthesis with उर्फ़ or aka
        # Matches: "Vikram Sharma (उर्फ़ विक्रम शर्मा, विक्की, विक्रम बंगाली)"
        pattern1 = r'([A-Z][a-z]+\s+[A-Z][a-z]+)\s*\(\s*(?:उर्फ़|aka)\s+(.+?)\)'

        # Pattern 2: Name followed directly by उर्फ़ or aka (without parenthesis)
        # Matches: "Name उर्फ़ Alias1, Alias2"
        pattern2 = r'([A-Z][a-z]+\s+[A-Z][a-z]+)\s*(?:उर्फ़|aka)\s+(.+?)(?=\.|,|और|\n|in)'

        seen_names = set()  # Track to avoid duplicates

        for pattern in [pattern1, pattern2]:
            for match in re.finditer(pattern, text, re.IGNORECASE | re.UNICODE):
                name = match.group(1).strip()

                # Skip if already extracted
                if name in seen_names:
                    continue

                aliases_str = match.group(2).strip()

                # Remove closing parenthesis if present
                aliases_str = aliases_str.rstrip(')')

                # Parse aliases (comma or "और" separated)
                aliases = [
                    a.strip().strip('"\'')
                    for a in re.split(r',|और', aliases_str)
                    if a.strip()
                ]

                persons.append((name, aliases))
                seen_names.add(name)

        return persons

    def extract_locations(self, text: str) -> List[Location]:
        """Extract locations mentioned in text"""
        locations = []

        # Common Indian cities/locations
        common_locations = {
            'Mumbai': ['Mumbai', 'Bombay', 'मुंबई'],
            'Delhi': ['Delhi', 'New Delhi', 'दिल्ली'],
            'Lucknow': ['Lucknow', 'लखनऊ'],
            'Kanpur': ['Kanpur', 'कानपुर'],
            'Thane': ['Thane', 'ठाणे'],
            'Bangalore': ['Bangalore', 'Bengaluru', 'बेंगलुरु'],
            'Hyderabad': ['Hyderabad', 'हैदराबाद'],
            'UP': ['Uttar Pradesh', 'UP', 'उत्तर प्रदेश'],
        }

        for city, variants in common_locations.items():
            for variant in variants:
                if variant in text:
                    location = Location(
                        id=f"location_{city.lower()}",
                        name=city,
                        city=city,
                        confidence=0.90
                    )
                    if location not in locations:
                        locations.append(location)

        return locations

    def extract_all(self, text: str, fir_id: str) -> Tuple[List[Entity], List[Relationship]]:
        """Extract all entities and basic relationships from text"""
        entities: List[Entity] = []
        relationships: List[Relationship] = []

        # Extract each entity type
        phones = self.extract_phones(text)
        vehicles = self.extract_vehicles(text)
        accounts = self.extract_bank_accounts(text)
        case = self.extract_case_details(text)
        locations = self.extract_locations(text)
        crimes = self.extract_crimes(text)
        persons_data = self.extract_person_names(text)

        # Add to entities
        entities.extend(phones)
        entities.extend(vehicles)
        entities.extend(accounts)
        if case:
            entities.append(case)
        entities.extend(locations)

        # Create person entities with relationships to phones/vehicles
        for person_name, aliases in persons_data:
            person = Person(
                id=f"person_{person_name.lower().replace(' ', '_')}",
                name=person_name,
                aliases=aliases,
                known_crimes=crimes,
                confidence=0.85
            )
            entities.append(person)

            # Create relationships to phones mentioned nearby
            for phone in phones:
                relationship = Relationship(
                    source_id=person.id,
                    target_id=phone.id,
                    type=RelationType.USES_PHONE,
                    confidence=0.80
                )
                relationships.append(relationship)

            # Create relationships to vehicles mentioned nearby
            for vehicle in vehicles:
                relationship = Relationship(
                    source_id=person.id,
                    target_id=vehicle.id,
                    type=RelationType.OWNS_VEHICLE,
                    confidence=0.75
                )
                relationships.append(relationship)

            # Create relationships to accounts
            for account in accounts:
                relationship = Relationship(
                    source_id=person.id,
                    target_id=account.id,
                    type=RelationType.OPERATES_ACCOUNT,
                    confidence=0.75
                )
                relationships.append(relationship)

            # Link to case
            if case:
                relationship = Relationship(
                    source_id=person.id,
                    target_id=case.id,
                    type=RelationType.ACCUSED_IN,
                    confidence=0.90
                )
                relationships.append(relationship)

        return entities, relationships


# ============================================================================
# MAIN EXTRACTION FUNCTION
# ============================================================================

def extract_from_fir(fir_text: str, fir_id: str) -> ExtractionResult:
    """
    Extract entities and relationships from a single FIR document

    Args:
        fir_text: Raw FIR text content
        fir_id: Identifier for the FIR

    Returns:
        ExtractionResult with entities, relationships, and metadata
    """
    start_time = datetime.now()

    try:
        extractor = EntityExtractor()
        entities, relationships = extractor.extract_all(fir_text, fir_id)

        extraction_time = (datetime.now() - start_time).total_seconds() * 1000

        # Calculate average confidence
        avg_confidence = (
            sum(e.confidence for e in entities) / len(entities)
            if entities
            else 0.0
        )

        result = ExtractionResult(
            fir_id=fir_id,
            entities=entities,
            relationships=relationships,
            text_snippet=fir_text[:200],
            extraction_confidence=avg_confidence,
            processing_time_ms=extraction_time,
            error=None
        )

        return result

    except Exception as e:
        logger.error(f"Error extracting from FIR {fir_id}: {str(e)}")
        extraction_time = (datetime.now() - start_time).total_seconds() * 1000

        return ExtractionResult(
            fir_id=fir_id,
            entities=[],
            relationships=[],
            text_snippet=fir_text[:200],
            extraction_confidence=0.0,
            processing_time_ms=extraction_time,
            error=str(e)
        )
