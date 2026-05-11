from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from contextlib import asynccontextmanager
import os, shutil, jwt, datetime
from pathlib import Path
from database import db
from routes import public, admin

# ── Startup: seed DB with default data if empty ──
@asynccontextmanager
async def lifespan(app: FastAPI):
    await db.connect()
    await seed_defaults()
    yield
    await db.disconnect()

async def seed_defaults():
    """Insert default data on first run if collections are empty."""
    if not await db.clients.find_one():
        default_clients = [
            {"name": "IIT Kharagpur"},
            {"name": "Airforce – Salua, Kharagpur"},
            {"name": "Airforce – Vadsar, Gujarat"},
            {"name": "Airforce – Silong"},
            {"name": "Airforce – Port Blair"},
            {"name": "AIIMS Bhubaneswar"},
            {"name": "AIIMS Kalyani"},
            {"name": "Varanasi Lal Bahadur Shastri Airport"},
            {"name": "Burdwan Bengal Faith Hospital"},
            {"name": "NTPC – Barh Unit, Bihar"},
            {"name": "DVC Power Plant – Raghunathpur, Purulia"},
            {"name": "TATA Cancer Hospital, New Town Kolkata"},
            {"name": "CESC – Budge Budge, Kolkata"},
            {"name": "Candor Building, New Town Kolkata"},
        ]
        await db.clients.insert_many(default_clients)

    if not await db.partners.find_one():
        default_partners = [
            {"name": "Indian Airforce"},
            {"name": "Bharat Electronics Limited"},
            {"name": "Blue Star Ltd."},
            {"name": "Voltas Ltd."},
            {"name": "Daikin"},
            {"name": "SMS Limited"},
            {"name": "ETS Lindgren Engineering India Pvt. Ltd"},
            {"name": "Frankonia India EMC Solutions Pvt. Ltd."},
            {"name": "Colour India Limited"},
            {"name": "Trity Environ Solutions Pvt. Ltd."},
        ]
        await db.partners.insert_many(default_partners)

    if not await db.stats.find_one():
        await db.stats.insert_one({
            "turnover": "5",
            "years": "15",
            "projects": "200",
            "states": "10"
        })

app = FastAPI(title="Ghosh Global Services API", version="1.0.0", lifespan=lifespan)

# ── CORS — allow your Netlify domain and localhost for dev ──
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost,http://127.0.0.1").split(",")
# Add your Netlify URL here once deployed, e.g.:
# ALLOWED_ORIGINS = ["https://ghoshglobal.netlify.app", "https://ghoshglobal.com"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],           # Change to ALLOWED_ORIGINS after going live
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Serve uploaded images as static files ──
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# ── Register route groups ──
app.include_router(public.router, prefix="/api",   tags=["Public"])
app.include_router(admin.router,  prefix="/admin", tags=["Admin"])

@app.get("/")
async def root():
    return {"status": "Ghosh Global Services API is running"}

@app.get("/health")
async def health():
    return {"status": "ok", "timestamp": datetime.datetime.utcnow().isoformat()}
