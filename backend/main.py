from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import api
from dotenv import load_dotenv
from fastapi.staticfiles import StaticFiles
from app.database import Base, engine

load_dotenv()

Base.metadata.create_all(bind=engine)

# Inisialisasi FastAPI
app = FastAPI()
app.mount("/static", StaticFiles(directory="uploads"), name="static")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Sesuaikan dengan URL frontend Anda
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Tambahkan router untuk endpoint
app.include_router(api)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
