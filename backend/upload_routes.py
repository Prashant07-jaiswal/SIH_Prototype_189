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
from pathlib import Path
from typing import List, Optional

from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/upload", tags=["Upload Evidence"])


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
    firs: Optional[List[UploadFile]] = File(None),
    cdr: Optional[UploadFile] = File(None),
    transactions: Optional[UploadFile] = File(None),
):
    """
    Upload evidence files (FIRs, CDR, transactions) and trigger the ingestion pipeline.

    The system will:
    1. Save files to a temporary ``data_uploads`` folder
    2. Run the extraction and analytics pipeline
    3. Return updated graph statistics and key findings
    """
    from .main import ingest_all_data, app_state

    upload_root = Path(__file__).parent.parent / "data_uploads"

    # -------------------------------------------------
    # 1️⃣ Save the incoming files
    # -------------------------------------------------
    try:
        if firs:
            fir_dir = upload_root / "firs"
            for f in firs:
                _save_upload(f, fir_dir)
                logger.info(f"Saved FIR: {f.filename}")

        if cdr:
            cdr_path = _save_upload(cdr, upload_root)
            cdr_path.rename(upload_root / "cdr.csv")
            logger.info(f"Saved CDR: {cdr.filename}")

        if transactions:
            txn_path = _save_upload(transactions, upload_root)
            txn_path.rename(upload_root / "transactions.csv")
            logger.info(f"Saved Transactions: {transactions.filename}")
    except Exception as exc:
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
    }

    logger.info(f"Upload completed: {dash_payload['graph_stats']['nodes']} nodes, {dash_payload['graph_stats']['edges']} edges")
    return JSONResponse(content=dash_payload)
