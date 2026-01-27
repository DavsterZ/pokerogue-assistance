from fastapi import FastAPI
from app.api.routes import router


app = FastAPI(
    title = "PokeRogue Assistant",
    description = "Asistente inteligente para el juego PokeRogue",
    version = "0.1"
)


app.include_router(router)


@app.get("/")
def root():
    return {"status": "Assistant is running"}