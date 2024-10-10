import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import api
from dotenv import load_dotenv
from fastapi.staticfiles import StaticFiles
from app.database.database import Base, engine

# Konfigurasi logging diletakkan di bagian paling atas
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Buat tabel di database jika belum ada
Base.metadata.create_all(bind=engine)

# Inisialisasi FastAPI
app = FastAPI()

# Mount folder untuk serving file statis
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Middleware CORS untuk mengizinkan akses dari frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Sesuaikan dengan URL frontend Anda
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Tambahkan router untuk endpoint
app.include_router(api)

# Jalankan aplikasi dengan Uvicorn
if __name__ == "__main__":
    import uvicorn

    # Jalankan server uvicorn dengan reload mode
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
