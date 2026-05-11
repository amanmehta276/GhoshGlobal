import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

class Database:
    client: AsyncIOMotorClient = None

    def __init__(self):
        self.client = None
        self._db = None

    async def connect(self):
        mongo_url = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
        self.client = AsyncIOMotorClient(mongo_url)
        self._db = self.client[os.getenv("DB_NAME", "ghoshglobal")]
        print(f"✅ Connected to MongoDB: {os.getenv('DB_NAME', 'ghoshglobal')}")

    async def disconnect(self):
        if self.client:
            self.client.close()
            print("🔌 Disconnected from MongoDB")

    # ── Collections ──
    @property
    def clients(self):
        return self._db["clients"]

    @property
    def partners(self):
        return self._db["partners"]

    @property
    def stats(self):
        return self._db["stats"]

    @property
    def enquiries(self):
        return self._db["enquiries"]

db = Database()
