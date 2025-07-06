import logging

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from src.cliente import router as cliente_router
from src.reserva import router as reserva_router
from src.veiculo import router as veiculo_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="API da Locadora",
    description="API para gerenciamento de uma locadora de veículos.",
    version="3.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(cliente_router.router)
app.include_router(veiculo_router.router)
app.include_router(reserva_router.router)

app.mount("/static", StaticFiles(directory="frontend"), name="static")
templates = Jinja2Templates(directory="frontend")


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
async def ler_raiz(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})