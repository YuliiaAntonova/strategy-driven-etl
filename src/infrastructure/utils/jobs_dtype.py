from __future__ import annotations

from sqlalchemy import Boolean, DateTime, Float, Integer, String, Text


JOBS_DTYPE_MAP: dict[str, object] = {
    "job_url": Text(),
    "site": String(100),
    "title": Text(),
    "company": Text(),
    "location": Text(),
    "job_type": String(100),
    "date_posted": String(50),
    "interval": String(50),
    "min_amount": Float(),
    "max_amount": Float(),
    "currency": String(50),
    "is_remote": String(50),
    "num_urgent_words": Integer(),
    "benefits": Text(),
    "emails": Text(),
    "description": Text(),
    "source_name": String(100),
    "run_id": String(100),
    "dt": String(50),
    "date_created": DateTime(timezone=True),
    "date_loaded": DateTime(timezone=True),
    "environment": String(50),
    "row_hash": String(64),
    "is_current": Boolean(),
}
