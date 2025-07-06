from datetime import date
from typing import List
from psycopg2 import errors
from psycopg2.extensions import connection
from fastapi import APIRouter, Depends, HTTPException, status
from src.database.connection import obter_conexao_banco
from . import service
from .schema import Veiculo, VeiculoCriacao, VeiculoAtualizacao

router = APIRouter(prefix="/veiculos", tags=["Veículos"])

@router.get("/disponiveis/", response_model=List[Veiculo])
def buscar_veiculos_disponiveis(
    data_inicio: date,
    data_fim: date,
    conexao_banco: connection = Depends(obter_conexao_banco)
):
    if data_inicio >= data_fim:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A data de início deve ser anterior à data de fim."
        )
    return service.obter_veiculos_disponiveis(
        conexao_banco, data_inicio, data_fim
    )

@router.post("", response_model=Veiculo, status_code=status.HTTP_201_CREATED)
def criar_veiculo(
    veiculo: VeiculoCriacao,
    conexao_banco: connection = Depends(obter_conexao_banco)
):
    try:
        return service.criar_veiculo(conexao_banco, veiculo)
    except errors.UniqueViolation as exc:
        msg = f"A placa '{veiculo.placa}' já está cadastrada."
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=msg
        ) from exc

@router.get("", response_model=List[Veiculo])
def ler_veiculos(conexao_banco: connection = Depends(obter_conexao_banco)):
    return service.obter_veiculos(conexao_banco)

@router.get("/{veiculo_id}", response_model=Veiculo)
def ler_veiculo(
    veiculo_id: int, conexao_banco: connection = Depends(obter_conexao_banco)
):
    veiculo_banco = service.obter_veiculo_por_id(conexao_banco, veiculo_id)
    if veiculo_banco is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Veículo não encontrado"
        )
    return veiculo_banco

@router.put("/{veiculo_id}", response_model=Veiculo)
def atualizar_veiculo(
    veiculo_id: int,
    dados_veiculo: VeiculoAtualizacao,
    conexao_banco: connection = Depends(obter_conexao_banco)
):
    atualizado = service.atualizar_veiculo(
        conexao_banco, veiculo_id, dados_veiculo
    )
    if atualizado is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Veículo não encontrado"
        )
    return atualizado

@router.delete("/{veiculo_id}", status_code=status.HTTP_204_NO_CONTENT)
def deletar_veiculo(
    veiculo_id: int, conexao_banco: connection = Depends(obter_conexao_banco)
):
    try:
        deletado = service.deletar_veiculo(conexao_banco, veiculo_id)
        if not deletado:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Veículo não encontrado"
            )
    except errors.ForeignKeyViolation as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Não é possível deletar veículo com reservas ativas."
        ) from exc