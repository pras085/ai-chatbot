import logging

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.auth_routes import auth_routes
from app.api.chat_routes import chat_routes
from app.api.code_check_rules_routes import code_check_rules_routes
from app.api.context_routes import context_routes
from app.api.file_routes import file_routes
from app.api.user_routes import user_routes
from app.config.database import engine, Base, create_tables

# Konfigurasi logging diletakkan di bagian paling atas
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Buat tabel di repositories jika belum ada
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
app.include_router(auth_routes, tags=["Auth Routes"])
app.include_router(user_routes, tags=["User Routes"])
app.include_router(chat_routes, tags=["Chat Routes"])
app.include_router(context_routes, tags=["Context Routes"])
app.include_router(code_check_rules_routes, tags=["Code Check Rules Routes"])
app.include_router(file_routes, tags=["File Routes"])

create_tables()

# Jalankan aplikasi dengan Uvicorn
if __name__ == "__main__":
    import uvicorn

    # Jalankan server uvicorn dengan reload mode
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
