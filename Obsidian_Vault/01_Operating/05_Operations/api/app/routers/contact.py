from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from typing import Optional
import sqlite3
from pathlib import Path
from datetime import datetime

router = APIRouter()

VAULT = Path(r"D:\Work\Torus Coffee Company LLC")
DB_PATH = VAULT / "10_Skills_Library/05_Operations/data/torus_local.db"


class InquiryCreate(BaseModel):
    name: str
    email: str
    inquiry_type: str = "general"
    subject: str
    message: str
    product_interest: Optional[str] = None


@router.post("/inquiries", status_code=201)
def create_inquiry(inquiry: InquiryCreate):
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS inquiries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL,
                inquiry_type TEXT NOT NULL,
                subject TEXT NOT NULL,
                message TEXT NOT NULL,
                product_interest TEXT,
                status TEXT DEFAULT 'new',
                created_at TEXT NOT NULL
            )
            """
        )
        cur.execute(
            """
            INSERT INTO inquiries (name, email, inquiry_type, subject, message, product_interest, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                inquiry.name,
                inquiry.email,
                inquiry.inquiry_type,
                inquiry.subject,
                inquiry.message,
                inquiry.product_interest,
                datetime.utcnow().isoformat(),
            ),
        )
        inquiry_id = cur.lastrowid
        conn.commit()
        conn.close()
        return {
            "id": inquiry_id,
            "status": "new",
            "message": "Inquiry received. We will respond within 1 business day.",
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
