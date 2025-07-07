import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database.init_db import initialize_database

# Importa os seus roteadores
from src.cliente import router as cliente_router
from src.reserva import router as reserva_router
from src.veiculo import router as veiculo_router

# --- Inicialização da Aplicação ---
print("Iniciando a aplicação...")
initialize_database()
print("Verificação do banco de dados concluída. Iniciando o servidor web.")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="API da Locadora",
    description="API para gerenciamento de uma locadora de veículos.",
    version="3.0.0"
)

# --- Configuração do CORS (Cross-Origin Resource Sharing) ---
# Lista de "origens" (sites) que podem fazer requisições para a sua API.
origins = [
    "https://locadora-frontend.onrender.com", # O seu frontend no Render
    "http://localhost",
    "http://localhost:8080",
    "http://127.0.0.1:5500" # Endereço comum para desenvolvimento local
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Permite as origens da lista
    allow_credentials=True,
    allow_methods=["*"],    # Permite todos os métodos (GET, POST, etc.)
    allow_headers=["*"],    # Permite todos os cabeçalhos
)

# --- Inclusão das Rotas da API ---
# O FastAPI irá adicionar os prefixos corretos, como /clientes, /veiculos, etc.
app.include_router(cliente_router.router)
app.include_router(veiculo_router.router)
app.include_router(reserva_router.router)

# --- Rota Raiz ---
# Uma rota simples para verificar se a API está no ar.
@app.get("/")
def read_root():
    return {"message": "API da Locadora de Veículos no ar!"}

