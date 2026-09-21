"""
Synthetic Criminal Network Dataset Generator
Generates interconnected FIRs (Hindi/English mix), CDRs, and Financial Transactions
"""

import json
import csv
from datetime import datetime, timedelta
import random
from pathlib import Path
import sys
import os

# Fix Windows encoding issue
if sys.platform == 'win32':
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    sys.stdout.reconfigure(encoding='utf-8')

# ============================================================================
# PHASE 1: DEFINE CRIMINAL NETWORK STRUCTURE
# ============================================================================

# Create a network of interconnected criminals across gangs
GANGS = {
    "Gang_A_Mumbai": {
        "name": "मुंबई कार्टेल (Mumbai Cartel)",
        "members": ["Vikram Sharma", "Ramesh Gupta", "Priya Desai"],
        "locations": ["Mumbai", "Thane", "Navi Mumbai"],
        "crimes": ["Drug Trafficking", "Extortion", "Money Laundering"]
    },
    "Gang_B_UP": {
        "name": "उत्तर प्रदेश रिंग (UP Criminal Ring)",
        "members": ["Rohit Singh", "Suresh Kumar", "Akshay Patel"],
        "locations": ["Lucknow", "Kanpur", "Agra"],
        "crimes": ["Vehicle Theft", "Highway Robbery", "Forgery"]
    },
    "Gang_C_Hawala": {
        "name": "हवाला नेटवर्क (Hawala Network)",
        "members": ["Ramesh Bhat", "Mohammad Khan", "Vikram Iyer"],
        "locations": ["Delhi", "Bangalore", "Hyderabad"],
        "crimes": ["Money Laundering", "Hawala", "Illegal Fund Transfer"]
    },
    "Gang_D_Interstate": {
        "name": "अंतरराज्यीय सिंडिकेट (Interstate Smuggling)",
        "members": ["Arun Verma", "Deepak Singh", "Ravi Nair"],
        "locations": ["Delhi", "Gurgaon", "Noida"],
        "crimes": ["Smuggling", "GST Fraud", "Counterfeiting"]
    }
}

# Vehicles to link suspects
VEHICLES = [
    {"plate": "MH02AB1234", "model": "Fortuner", "owner": "Vikram Sharma"},
    {"plate": "UP32CD5678", "model": "Splendor", "owner": "Rohit Singh"},
    {"plate": "DL01EF9012", "model": "Creta", "owner": "Ramesh Bhat"},
    {"plate": "KA03GH3456", "model": "Innova", "owner": "Mohammad Khan"},
    {"plate": "UP14IJ7890", "model": "Swift", "owner": "Suresh Kumar"},
]

# Banks for transaction trails
BANKS = [
    {"name": "HDFC Bank", "ifsc": "HDFC0000123"},
    {"name": "ICICI Bank", "ifsc": "ICIC0000456"},
    {"name": "Axis Bank", "ifsc": "UTIB0000789"},
    {"name": "SBI", "ifsc": "SBIN0001234"},
]

# ============================================================================
# PHASE 2: GENERATE FIR DOCUMENTS (Mixed Hindi/English)
# ============================================================================

FIR_TEMPLATES = [
    {
        "case_id": "FIR_001_MH",
        "fir_no": "MH/2024/12345",
        "district": "Mumbai",
        "police_station": "Colaba Police Station",
        "date": "2024-01-15",
        "ipc_sections": ["21", "120B", "292", "293"],
        "narrative_hindi": """
        तारीख 14-01-2024 को शाम 6:30 पर Colaba Police Station को सूचना मिली कि
        suspect Vikram Sharma (उर्फ़ विक्रम शर्मा, विक्की, विक्रम बंगाली)
        एक Fortuner (MH02AB1234) में बैठकर Nariman Point से Marine Drive की ओर जा रहे हैं।
        उनके साथ एक अन्य accused Ramesh Gupta (उर्फ़ रमेश गुप्ता, रमेश मुंबई, रामू) भी था।

        फोन नंबर 9876543210 से कॉल करके उन्होंने किसी को ड्रग्स की सप्लाई करने के बारे में बात की।
        Informant के हिसाब से इनकी एक अवैध नेटवर्क है जो मुंबई, ठाणे और नवी मुंबई में
        काम करता है। Ramesh Gupta का अकाउंट नंबर HDFC0000123 है जिससे हवाला के माध्यम से
        ₹50,00,000 का ट्रांसफर हुआ है।
        """,
        "suspects": ["Vikram Sharma", "Ramesh Gupta"],
        "phones": ["9876543210", "9123456789"],
        "vehicles": ["MH02AB1234"],
        "accounts": ["HDFC_ACC_1001"]
    },
    {
        "case_id": "FIR_002_UP",
        "fir_no": "UP/2024/67890",
        "district": "Kanpur",
        "police_station": "Jajmau Police Station",
        "date": "2024-02-10",
        "ipc_sections": ["379", "411", "420"],
        "narrative_hindi": """
        तारीख 09-02-2024 को रात 11:45 पर एक वाहन चोरी की रिपोर्ट आई।
        Suspect Rohit Singh (उर्फ़ रोहित, रोहित सिंह UP, रोहीत) और उसका साथी Suresh Kumar
        (उर्फ़ सुरेश, सुरेश कुमार UP) को Highway No. 2 पर Splendor Car (UP32CD5678) चलाते हुए देखा गया।

        Rohit Singh का phone नंबर 8765432109 है और वह बार-बार Vikram Sharma (Mumbai के से)
        को कॉल कर रहा था (कॉल records से पता चला - 15 बार एक सप्ताह में)।

        दोनों के बीच ₹25,00,000 का अवैध ट्रांसफर हुआ है। Suresh Kumar का अकाउंट ICIC0000456 है।
        """,
        "suspects": ["Rohit Singh", "Suresh Kumar"],
        "phones": ["8765432109", "8912345678"],
        "vehicles": ["UP32CD5678"],
        "accounts": ["ICIC_ACC_2001"]
    },
    {
        "case_id": "FIR_003_DL",
        "fir_no": "DL/2024/11223",
        "district": "Delhi",
        "police_station": "Cyber Crime Cell",
        "date": "2024-03-05",
        "ipc_sections": ["420", "408", "120B", "188"],
        "narrative_hindi": """
        तारीख 04-03-2024 को Intelligence agency को एक tip मिला कि एक बड़ा hawala नेटवर्क
        Delhi, Bangalore और Hyderabad में काम कर रहा है।

        मुख्य suspect है Ramesh Bhat (उर्फ़ रमेश भट्ट, भैया, धनी रमेश) जिसका Creta (DL01EF9012)
        है और उसका partner है Mohammad Khan (उर्फ़ मोहम्मद खान, खान sahab, मो खान)।

        फोन 7654321098 और 7123456789 से इन्होंने 15 दिन में ₹3,50,00,000 का illegal transfer किया है।
        Bank accounts: UTIB_ACC_3001, SBIN_ACC_3002।

        Financial trail से पता चला कि Vikram Sharma (Mumbai) से भी connection है।
        """,
        "suspects": ["Ramesh Bhat", "Mohammad Khan"],
        "phones": ["7654321098", "7123456789"],
        "vehicles": ["DL01EF9012"],
        "accounts": ["UTIB_ACC_3001", "SBIN_ACC_3002"]
    },
    {
        "case_id": "FIR_004_MH",
        "fir_no": "MH/2024/34567",
        "district": "Thane",
        "police_station": "Thane Central",
        "date": "2024-03-20",
        "ipc_sections": ["21", "379", "120B"],
        "narrative_hindi": """
        तारीख 19-03-2024 को Thane में एक अवैध हथियार store को raid किया गया।
        Suspects: Priya Desai (उर्फ़ प्रिया, प्रिया ठाणे) और Akshay Patel (उर्फ़ अक्षय पटेल, अक्षय)

        Priya के फोन (9012345678) की call logs से पता चला कि वह Vikram Sharma और Ramesh Gupta
        दोनों के साथ नियमित संपर्क में है। Vehicle Innova (KA03GH3456) को संदिग्ध माना गया है।

        Account HDFC_ACC_1001 से ₹15,00,000 का transfer हुआ है।
        """,
        "suspects": ["Priya Desai", "Akshay Patel"],
        "phones": ["9012345678", "9234567890"],
        "vehicles": ["KA03GH3456"],
        "accounts": ["HDFC_ACC_1001"]
    },
    {
        "case_id": "FIR_005_UP",
        "fir_no": "UP/2024/55443",
        "district": "Lucknow",
        "police_station": "Lucknow Central",
        "date": "2024-04-01",
        "ipc_sections": ["420", "120B", "188"],
        "narrative_hindi": """
        तारीख 31-03-2024 को GST Fraud का एक बड़ा case दर्ज किया गया।
        Main accused: Arun Verma (उर्फ़ अरुण वर्मा, अरुण, अरुण दिल्ली)
        Accomplice: Deepak Singh (उर्फ़ दीपक सिंह, दीपक, दीपक UP)

        Vehicle Swift (UP14IJ7890) में documents मिले। Phone records से ज्ञात हुआ कि
        Arun और Rohit Singh (UP gang) के बीच 20+ calls हुई हैं।

        ₹40,00,000 का संदिग्ध transfer account ICIC_ACC_2001 से हुआ है।
        Ravi Nair (उर्फ़ राविराज, राज) भी इसमें involved है।
        """,
        "suspects": ["Arun Verma", "Deepak Singh", "Ravi Nair"],
        "phones": ["6543210987", "6234567890", "6678901234"],
        "vehicles": ["UP14IJ7890"],
        "accounts": ["ICIC_ACC_2001"]
    }
]

# ============================================================================
# PHASE 3: GENERATE CDR (CALL DETAIL RECORDS)
# ============================================================================

def generate_cdrs(base_date, days=30):
    """Generate realistic CDR records with call patterns"""
    cdrs = []
    call_patterns = [
        # Intra-gang calls (frequent)
        ("9876543210", "9123456789", 8),  # Vikram -> Ramesh
        ("9876543210", "8765432109", 6),  # Vikram -> Rohit (cross-gang)
        ("9876543210", "7654321098", 5),  # Vikram -> Ramesh Bhat (cross-gang)
        ("9123456789", "9876543210", 8),  # Ramesh -> Vikram
        ("9012345678", "9876543210", 6),  # Priya -> Vikram
        ("8765432109", "8912345678", 10), # Rohit -> Suresh
        ("8765432109", "6543210987", 7),  # Rohit -> Arun (cross-gang)
        ("7654321098", "7123456789", 15), # Ramesh Bhat <-> Mohammad (frequent)
        ("7123456789", "7654321098", 15),
        ("6543210987", "6234567890", 9),  # Arun <-> Deepak
    ]

    cdr_id = 1
    for day_offset in range(days):
        current_date = base_date + timedelta(days=day_offset)

        for caller, receiver, avg_frequency in call_patterns:
            # Add randomness to frequency
            num_calls = max(1, avg_frequency + random.randint(-2, 3))

            for _ in range(num_calls):
                # Random time of day (some at night for suspicion)
                hour = random.choice(
                    list(range(9, 22)) + [1, 2, 3, 23] * 2  # More night calls
                )
                minute = random.randint(0, 59)
                call_time = current_date.replace(hour=hour, minute=minute)

                duration = random.randint(30, 1200)  # 30 sec to 20 min
                cell_tower = random.choice(["Tower_Mumbai_Central", "Tower_UP_Kanpur",
                                           "Tower_Delhi_Central", "Tower_Bangalore"])

                cdrs.append({
                    "cdr_id": cdr_id,
                    "caller": caller,
                    "receiver": receiver,
                    "call_datetime": call_time.isoformat(),
                    "duration_seconds": duration,
                    "call_type": "Mobile-Mobile",
                    "cell_tower": cell_tower
                })
                cdr_id += 1

    return cdrs

# ============================================================================
# PHASE 4: GENERATE FINANCIAL TRANSACTIONS
# ============================================================================

def generate_transactions(base_date, days=30):
    """Generate financial transaction records with suspicious patterns"""
    transactions = []

    # Define transaction flows (sender -> receiver -> amount pattern)
    transaction_patterns = [
        # Hawala network flows
        ("HDFC_ACC_1001", "SBIN_ACC_3002", 500000, "Multiple small deposits"),
        ("SBIN_ACC_3002", "UTIB_ACC_3001", 750000, "Cross-bank transfer"),
        ("UTIB_ACC_3001", "ICIC_ACC_2001", 400000, "Interstate movement"),

        # Smurfing pattern (below reporting threshold of 10L)
        ("HDFC_ACC_1001", "ICIC_ACC_2001", 200000, "Multiple transactions"),
        ("ICIC_ACC_2001", "UTIB_ACC_3001", 250000, "Rapid movement"),

        # Cash-heavy accounts
        ("HDFC_ACC_1001", "SBIN_ACC_3002", 150000, "Cash deposit suspicious"),
    ]

    txn_id = 1
    for day_offset in range(days):
        current_date = base_date + timedelta(days=day_offset)

        for sender, receiver, amount, reason in transaction_patterns:
            # Add randomness
            if random.random() > 0.4:  # 60% chance per day
                actual_amount = amount + random.randint(-50000, 50000)
                hour = random.randint(0, 23)
                minute = random.randint(0, 59)
                txn_time = current_date.replace(hour=hour, minute=minute)

                transactions.append({
                    "transaction_id": txn_id,
                    "sender_account": sender,
                    "receiver_account": receiver,
                    "amount_inr": abs(actual_amount),
                    "transaction_datetime": txn_time.isoformat(),
                    "transaction_type": random.choice(["NEFT", "RTGS", "UPI", "IFT"]),
                    "sender_bank": random.choice(["HDFC", "ICICI", "Axis", "SBI"]),
                    "receiver_bank": random.choice(["HDFC", "ICICI", "Axis", "SBI"]),
                    "status": "SUCCESS",
                    "remarks": reason
                })
                txn_id += 1

    return transactions

# ============================================================================
# PHASE 5: WRITE FILES TO DISK
# ============================================================================

def main():
    output_dir = Path("synthetic_data")
    output_dir.mkdir(exist_ok=True)

    print("🔴 Generating Synthetic Criminal Network Dataset...\n")

    # 1. Create FIR documents folder
    firs_dir = output_dir / "FIRs"
    firs_dir.mkdir(exist_ok=True)

    print("📄 Creating FIR Documents...")
    for fir in FIR_TEMPLATES:
        fir_filename = firs_dir / f"{fir['case_id']}.txt"
        content = f"""
═══════════════════════════════════════════════════════════════════
                    FIRST INFORMATION REPORT (FIR)
═══════════════════════════════════════════════════════════════════

FIR Number: {fir['fir_no']}
District: {fir['district']}
Police Station: {fir['police_station']}
Date of FIR: {fir['date']}
IPC Sections: {', '.join(fir['ipc_sections'])}

NARRATIVE:
{fir['narrative_hindi']}

SUSPECTS: {', '.join(fir['suspects'])}
PHONE NUMBERS: {', '.join(fir['phones'])}
VEHICLES: {', '.join(fir['vehicles'])}
BANK ACCOUNTS: {', '.join(fir['accounts'])}

═══════════════════════════════════════════════════════════════════
"""
        fir_filename.write_text(content, encoding='utf-8')
        print(f"  ✓ {fir_filename.name}")

    # 2. Create CDR CSV
    print("\n📞 Creating Call Detail Records (CDR)...")
    base_date = datetime(2024, 1, 1)
    cdrs = generate_cdrs(base_date)

    cdr_file = output_dir / "call_detail_records.csv"
    with open(cdr_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['cdr_id', 'caller', 'receiver',
                                               'call_datetime', 'duration_seconds',
                                               'call_type', 'cell_tower'])
        writer.writeheader()
        writer.writerows(cdrs)
    print(f"  ✓ {cdr_file.name} ({len(cdrs)} records)")

    # 3. Create Financial Transactions CSV
    print("\n💰 Creating Financial Transactions...")
    transactions = generate_transactions(base_date)

    txn_file = output_dir / "financial_transactions.csv"
    with open(txn_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['transaction_id', 'sender_account',
                                               'receiver_account', 'amount_inr',
                                               'transaction_datetime', 'transaction_type',
                                               'sender_bank', 'receiver_bank', 'status', 'remarks'])
        writer.writeheader()
        writer.writerows(transactions)
    print(f"  ✓ {txn_file.name} ({len(transactions)} records)")

    # 4. Create metadata JSON
    print("\n📋 Creating Network Metadata...")
    metadata = {
        "dataset_name": "Criminal Network Synthetic Data (SIH 2024)",
        "generated_date": datetime.now().isoformat(),
        "gangs": GANGS,
        "vehicles": VEHICLES,
        "banks": BANKS,
        "summary": {
            "total_firs": len(FIR_TEMPLATES),
            "total_cdr_records": len(cdrs),
            "total_transactions": len(transactions),
            "date_range": f"{base_date.date()} to {(base_date + timedelta(days=30)).date()}"
        }
    }

    metadata_file = output_dir / "metadata.json"
    metadata_file.write_text(json.dumps(metadata, indent=2, ensure_ascii=False), encoding='utf-8')
    print(f"  ✓ {metadata_file.name}")

    print("\n" + "="*70)
    print("✅ DATASET GENERATION COMPLETE!")
    print("="*70)
    print(f"\n📁 Output Directory: {output_dir.absolute()}")
    print(f"\n📊 Dataset Summary:")
    print(f"   • FIR Documents: {len(FIR_TEMPLATES)} files")
    print(f"   • CDR Records: {len(cdrs)} call records")
    print(f"   • Financial Transactions: {len(transactions)} transactions")
    print(f"   • Criminal Networks: {len(GANGS)} gangs")
    print(f"   • Time Period: {metadata['summary']['date_range']}")

if __name__ == "__main__":
    main()
