from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import datetime
from database import db

router = APIRouter()

# ── Helper: convert MongoDB doc to JSON-safe dict ──
def doc(d):
    d["_id"] = str(d["_id"])
    return d

# ───────────────────────────────────────────
# PUBLIC ENDPOINTS (no auth)
# ───────────────────────────────────────────

@router.get("/clients")
async def get_clients():
    """Return all clients for the public website."""
    clients = await db.clients.find().to_list(length=100)
    return [doc(c) for c in clients]


@router.get("/partners")
async def get_partners():
    """Return all authorised partners."""
    partners = await db.partners.find().to_list(length=100)
    return [doc(p) for p in partners]


@router.get("/stats")
async def get_stats():
    """Return company stats shown on the homepage."""
    stats = await db.stats.find_one()
    if not stats:
        return {"turnover": "5", "years": "15", "projects": "200", "states": "10"}
    return doc(stats)


# ── Contact form submission ──
class ContactForm(BaseModel):
    name: str
    contact: str
    org: Optional[str] = ""
    service: Optional[str] = ""
    message: Optional[str] = ""

@router.post("/contact")
async def submit_contact(form: ContactForm):
    """Save a contact form submission."""
    if not form.name.strip() or not form.contact.strip():
        raise HTTPException(status_code=400, detail="Name and contact are required.")

    enquiry = {
        **form.model_dump(),
        "status": "new",
        "submitted_at": datetime.datetime.utcnow().isoformat()
    }
    await db.enquiries.insert_one(enquiry)
    return {"success": True, "message": "Enquiry received. We will contact you shortly."}
