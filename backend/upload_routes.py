"""
FastAPI file-upload service for FIRs, CDR CSVs and transaction CSVs.

The UI will POST a multipart/form-data payload:
   • firs            – List[UploadFile]   (txt / pdf)
   • cdr             – UploadFile (CSV)
   • transactions    – UploadFile (CSV)

The endpoint
   1. Saves the uploaded files under ``data_uploads/`` (created on first call).
   2. Calls the same internal pipeline via ``ingest_all_data``.
   3. Returns the refreshed graph statistics, key-players and communities
      so the UI can instantly refresh its dashboard.
"""

import os
import shutil
import hashlib
from pathlib import Path
from typing import List, Optional

from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
import logging

from database import get_db, EvidenceLog, User
from auth import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/upload", tags=["Upload Evidence"])


def _calculate_hash(file_path: Path) -> str:
    """Calculate SHA-256 hash of a file for blockchain-like integrity verification."""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


def _save_upload(file: UploadFile, dest_dir: Path) -> Path:
    """Save a single UploadFile inside ``dest_dir`` and return the full path."""
    dest_dir.mkdir(parents=True, exist_ok=True)
    file_path = dest_dir / file.filename
    # Overwrite if the same name is uploaded again
    with open(file_path, "wb") as out:
        shutil.copyfileobj(file.file, out)
    return file_path


@router.post("/", summary="Upload FIRs, CDRs and transaction files")
async def upload_evidence(
    firs: List[UploadFile] = File(default=[]),
    cdr: Optional[UploadFile] = File(None),
    transactions: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Upload evidence files (FIRs, CDR, transactions), record SHA-256 hashes to the Database Ledger,
    and trigger the ingestion pipeline. Requires user authentication.
    """
    from main import ingest_all_data, app_state

    upload_root = Path(__file__).parent.parent / "data_uploads"

    # -------------------------------------------------
    # 1️⃣ Save the incoming files & compute hash
    # -------------------------------------------------
    evidence_records = []
    try:
        if firs:
            fir_dir = upload_root / "firs"
            for f in firs:
                saved_path = _save_upload(f, fir_dir)
                file_hash = _calculate_hash(saved_path)

                # Store record in database ledger (simulating blockchain-grade tamper proofing)
                evidence = EvidenceLog(
                    filename=f.filename,
                    file_type="fir",
                    uploader_id=current_user.id,
                    sha256_hash=file_hash
                )
                db.add(evidence)
                evidence_records.append({"filename": f.filename, "hash": file_hash})
                logger.info(f"Saved FIR: {f.filename} with hash {file_hash}")

        if cdr:
            cdr_path = _save_upload(cdr, upload_root)
            dest_cdr = upload_root / "cdr.csv"
            cdr_path.replace(dest_cdr)
            file_hash = _calculate_hash(dest_cdr)

            evidence = EvidenceLog(
                filename=cdr.filename,
                file_type="cdr",
                uploader_id=current_user.id,
                sha256_hash=file_hash
            )
            db.add(evidence)
            evidence_records.append({"filename": cdr.filename, "hash": file_hash})
            logger.info(f"Saved CDR: {cdr.filename} with hash {file_hash}")

        if transactions:
            txn_path = _save_upload(transactions, upload_root)
            dest_txn = upload_root / "transactions.csv"
            txn_path.replace(dest_txn)
            file_hash = _calculate_hash(dest_txn)

            evidence = EvidenceLog(
                filename=transactions.filename,
                file_type="transaction",
                uploader_id=current_user.id,
                sha256_hash=file_hash
            )
            db.add(evidence)
            evidence_records.append({"filename": transactions.filename, "hash": file_hash})
            logger.info(f"Saved Transactions: {transactions.filename} with hash {file_hash}")

        db.commit()
    except Exception as exc:
        db.rollback()
        logger.error(f"Failed to store uploaded files: {exc}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to store uploaded files: {exc}",
        ) from exc

    # -------------------------------------------------
    # 2️⃣ Run the ingestion pipeline (re-using existing code)
    # -------------------------------------------------
    try:
        logger.info("Starting ingestion pipeline on uploaded files...")
        response = await ingest_all_data(
            fir_folder=str(upload_root / "firs") if firs else None,
            cdr_file=str(upload_root / "cdr.csv") if cdr else None,
            transaction_file=str(upload_root / "transactions.csv") if transactions else None,
        )
        logger.info("Ingestion pipeline completed successfully")
    except Exception as exc:
        logger.error(f"Ingestion pipeline failed: {exc}")
        raise HTTPException(
            status_code=500,
            detail=f"Ingestion pipeline failed: {exc}",
        ) from exc

    # -------------------------------------------------
    # 3️⃣ Build a tiny "dashboard-ready" payload
    # -------------------------------------------------
    # The pipeline already updated ``app_state`` – just read from it.
    dash_payload = {
        "status": "success",
        "graph_stats": {
            "nodes": len(app_state.entities),
            "edges": len(app_state.relationships),
        },
        "key_players": app_state.key_players[:5],   # give the UI the top five
        "communities": app_state.communities[:3],   # give the UI a few syndicates
        "message": "✅ Data uploaded and analytics refreshed.",
        "evidence_records": evidence_records
    }

    from fastapi.encoders import jsonable_encoder

    logger.info(f"Upload completed: {dash_payload['graph_stats']['nodes']} nodes, {dash_payload['graph_stats']['edges']} edges")
    return JSONResponse(content=jsonable_encoder(dash_payload))


@router.get("/ledger", summary="Get Blockchain-style Audit Ledger of uploaded evidence")
def get_evidence_ledger(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Retrieve immutable audit trail / hash ledger of all uploaded evidence."""
    logs = db.query(EvidenceLog).order_by(EvidenceLog.timestamp.desc()).all()
    return [
        {
            "id": log.id,
            "filename": log.filename,
            "file_type": log.file_type,
            "sha256_hash": log.sha256_hash,
            "uploader_id": log.uploader_id,
            "timestamp": log.timestamp.isoformat() if log.timestamp else None
        }
        for log in logs
    ]
