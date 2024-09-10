from fastapi import FastAPI
from app.api.routes import router
import os

# Inisialisasi FastAPI
app = FastAPI()

# Tambahkan router untuk endpoint
app.include_router(router)

# Pastikan variabel lingkungan telah disetel dengan benar
CLAUDE_API_KEY = os.getenv("CLAUDE_API_KEY")
if not CLAUDE_API_KEY:
    raise ValueError("CLAUDE_API_KEY environment variable is not set")

if __name__ == "__main__":
    import uvicorn

    # Jalankan aplikasi menggunakan uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
