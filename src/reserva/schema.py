from datetime import date
from typing import List, Optional
from pydantic import BaseModel, ConfigDict
from src.cliente.schema import Pessoa
from src.veiculo.schema import Veiculo

class ReservaBase(BaseModel):
    data_inicio: date
    data_fim: date
    cliente_id: int
    veiculo_id: int

class ReservaCriacao(ReservaBase):
    tipo_reserva: str

class ReservaAtualizacao(BaseModel):
    data_inicio: Optional[date] = None
    data_fim: Optional[date] = None
    tipo_reserva: Optional[str] = None

class Reserva(ReservaBase):
    reserva_id: int
    diarias: int
    valor_total: float
    tipo_reserva: str
    cliente: Pessoa
    veiculo: Veiculo
    model_config = ConfigDict(from_attributes=True)

class RelatorioFaturamento(BaseModel):
    periodo_inicio: date
    periodo_fim: date
    total_reservas: int
    faturamento_total: float
    reservas_incluidas: List[Reserva]