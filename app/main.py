from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router


app = FastAPI(
    title = "PokeRogue Assistant",
    description = "Asistente inteligente para el juego PokeRogue",
    version = "0.1"
)


# Configuracion de CORS (Permisos para que el Frontend hable con el Backend))
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],    # Permitir todos los metodos (GET, POST, etc.)
    allow_headers=["*"],
)

app.include_router(router)


@app.get("/")
def root():
    return {"status": "Assistant is running"}