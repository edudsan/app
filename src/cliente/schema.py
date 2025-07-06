from typing import Optional
from pydantic import BaseModel, EmailStr, ConfigDict

class EnderecoBase(BaseModel):
    rua: str
    bairro: Optional[str] = None
    cidade: str
    estado: str
    numero: Optional[int] = None

class EnderecoCriacao(EnderecoBase):
    pass

class EnderecoAtualizacao(BaseModel):
    rua: Optional[str] = None
    bairro: Optional[str] = None
    cidade: Optional[str] = None
    estado: Optional[str] = None
    numero: Optional[int] = None

class Endereco(EnderecoBase):
    endereco_id: int
    model_config = ConfigDict(from_attributes=True)

class PessoaBase(BaseModel):
    nome: str
    email: EmailStr
    telefone: Optional[str] = None

class PessoaCriacao(PessoaBase):
    pass

class PessoaFisicaCriacao(PessoaCriacao):
    tipo_pessoa: str = "PF"
    cpf: str
    estado_civil: Optional[str] = None
    endereco: EnderecoCriacao

class PessoaJuridicaCriacao(PessoaCriacao):
    tipo_pessoa: str = "PJ"
    cnpj: str
    endereco: EnderecoCriacao

class PessoaAtualizacao(BaseModel):
    nome: Optional[str] = None
    telefone: Optional[str] = None
    endereco: Optional[EnderecoAtualizacao] = None

class Pessoa(PessoaBase):
    pessoa_id: int
    tipo_pessoa: str
    cpf: Optional[str] = None
    cnpj: Optional[str] = None
    endereco: Endereco
    model_config = ConfigDict(from_attributes=True)