from typing import Optional
from pydantic import BaseModel, ConfigDict

class VeiculoBase(BaseModel):
    placa: str
    modelo: str
    marca: Optional[str] = None
    ano: Optional[int] = None
    valor_diaria: float

class VeiculoCriacao(VeiculoBase):
    pass

class VeiculoAtualizacao(BaseModel):
    modelo: Optional[str] = None
    marca: Optional[str] = None
    ano: Optional[int] = None
    valor_diaria: Optional[float] = None

class Veiculo(VeiculoBase):
    veiculo_id: int
    model_config = ConfigDict(from_attributes=True)