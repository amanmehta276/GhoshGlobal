from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form
from pydantic import BaseModel
from typing import List, Optional
from pathlib import Path
import shutil, uuid, datetime
from bson import ObjectId
from database import db
from auth import verify_password, create_token, verify_token

router = APIRouter()

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

# ── Helper ──
def doc(d):
    d["_id"] = str(d["_id"])
    return d


# ───────────────────────────────────────────
# AUTH
# ───────────────────────────────────────────

class LoginRequest(BaseModel):
    password: str

@router.post("/login")
async def admin_login(req: LoginRequest):
    """Verify admin password and return a JWT token."""
    if not verify_password(req.password):
        raise HTTPException(status_code=401, detail="Incorrect password.")
    token = create_token()
    return {"token": token, "message": "Login successful"}


# ───────────────────────────────────────────
# CLIENTS  (protected)
# ───────────────────────────────────────────

class ClientItem(BaseModel):
    name: str

@router.put("/clients")
async def update_clients(clients: List[ClientItem], _=Depends(verify_token)):
    """Replace the entire clients list."""
    await db.clients.delete_many({})
    if clients:
        await db.clients.insert_many([c.model_dump() for c in clients])
    return {"success": True, "count": len(clients)}

@router.post("/clients")
async def add_client(client: ClientItem, _=Depends(verify_token)):
    """Add a single client."""
    result = await db.clients.insert_one(client.model_dump())
    return {"success": True, "id": str(result.inserted_id)}

@router.delete("/clients/{client_id}")
async def delete_client(client_id: str, _=Depends(verify_token)):
    """Delete a client by ID."""
    result = await db.clients.delete_one({"_id": ObjectId(client_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Client not found.")
    return {"success": True}


# ───────────────────────────────────────────
# PARTNERS  (protected)
# ───────────────────────────────────────────

class PartnerItem(BaseModel):
    name: str

@router.put("/partners")
async def update_partners(partners: List[PartnerItem], _=Depends(verify_token)):
    """Replace the entire partners list."""
    await db.partners.delete_many({})
    if partners:
        await db.partners.insert_many([p.model_dump() for p in partners])
    return {"success": True, "count": len(partners)}

@router.post("/partners")
async def add_partner(partner: PartnerItem, _=Depends(verify_token)):
    result = await db.partners.insert_one(partner.model_dump())
    return {"success": True, "id": str(result.inserted_id)}

@router.delete("/partners/{partner_id}")
async def delete_partner(partner_id: str, _=Depends(verify_token)):
    result = await db.partners.delete_one({"_id": ObjectId(partner_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Partner not found.")
    return {"success": True}


# ───────────────────────────────────────────
# STATS  (protected)
# ───────────────────────────────────────────

class StatsUpdate(BaseModel):
    turnover: Optional[str] = None
    years: Optional[str] = None
    projects: Optional[str] = None
    states: Optional[str] = None

@router.put("/stats")
async def update_stats(stats: StatsUpdate, _=Depends(verify_token)):
    """Update company stats shown on homepage."""
    update_data = {k: v for k, v in stats.model_dump().items() if v is not None}
    await db.stats.update_one({}, {"$set": update_data}, upsert=True)
    return {"success": True, "updated": update_data}


# ───────────────────────────────────────────
# ENQUIRIES  (protected)
# ───────────────────────────────────────────

@router.get("/enquiries")
async def get_enquiries(_=Depends(verify_token)):
    """Get all contact form submissions."""
    enquiries = await db.enquiries.find().to_list(length=500)
    return [doc(e) for e in enquiries]

@router.patch("/enquiries/{enquiry_id}/read")
async def mark_read(enquiry_id: str, _=Depends(verify_token)):
    """Mark an enquiry as read."""
    await db.enquiries.update_one(
        {"_id": ObjectId(enquiry_id)},
        {"$set": {"status": "read"}}
    )
    return {"success": True}

@router.delete("/enquiries/{enquiry_id}")
async def delete_enquiry(enquiry_id: str, _=Depends(verify_token)):
    result = await db.enquiries.delete_one({"_id": ObjectId(enquiry_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Enquiry not found.")
    return {"success": True}


# ───────────────────────────────────────────
# IMAGE UPLOAD  (protected)
# ───────────────────────────────────────────

ALLOWED_TYPES = {"hero-bg", "logo", "proprietor", "favicon"}
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".ico", ".webp"}

@router.post("/upload")
async def upload_image(
    file: UploadFile = File(...),
    type: str = Form(...),
    _=Depends(verify_token)
):
    """
    Upload an image and save it to the uploads/ folder.
    type must be one of: hero-bg, logo, proprietor, favicon
    The frontend will reference it as /uploads/<type>.<ext>
    """
    if type not in ALLOWED_TYPES:
        raise HTTPException(status_code=400, detail=f"Invalid type. Allowed: {ALLOWED_TYPES}")

    suffix = Path(file.filename).suffix.lower()
    if suffix not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"Invalid file type. Allowed: jpg, png, ico, webp")

    # For favicon keep .ico, everything else use original extension
    filename = f"{type}{suffix}"
    save_path = UPLOAD_DIR / filename

    with save_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return {
        "success": True,
        "filename": filename,
        "url": f"/uploads/{filename}",
        "message": f"Image saved as {filename}"
    }
