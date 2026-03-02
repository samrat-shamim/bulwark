"""Waitlist / early access signup endpoint."""

from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.auth import get_agent
from app.db import async_session, WaitlistEntry, Agent

router = APIRouter()


class WaitlistRequest(BaseModel):
    email: EmailStr
    name: Optional[str] = None
    company: Optional[str] = None


@router.post("/waitlist", status_code=201)
async def join_waitlist(req: WaitlistRequest):
    """Submit an early access request. No auth required (public endpoint)."""
    async with async_session() as db:
        entry = WaitlistEntry(
            email=req.email,
            name=req.name,
            company=req.company,
        )
        db.add(entry)
        try:
            await db.commit()
        except IntegrityError:
            # Email already exists — return success silently
            return {"message": "You're on the list. We'll be in touch."}

    return {"message": "You're on the list. We'll be in touch."}


@router.get("/waitlist")
async def list_waitlist(agent: Agent = Depends(get_agent)):
    """List all waitlist signups. Requires API key (admin only)."""
    async with async_session() as db:
        result = await db.execute(
            select(WaitlistEntry).order_by(WaitlistEntry.created_at.desc())
        )
        entries = result.scalars().all()

    return {
        "entries": [
            {
                "id": e.id,
                "email": e.email,
                "name": e.name,
                "company": e.company,
                "created_at": e.created_at.isoformat(),
            }
            for e in entries
        ],
        "total": len(entries),
    }
