from datetime import date
from typing import List
from psycopg2.extensions import connection
from fastapi import APIRouter, Depends, HTTPException, status
from src.database.connection import obter_conexao_banco
from . import service
from .schema import (
    Reserva, ReservaCriacao, ReservaAtualizacao, RelatorioFaturamento
)

router = APIRouter(prefix="/reservas", tags=["Reservas"])

@router.get("/relatorio/faturamento/", response_model=RelatorioFaturamento)
def obter_relatorio_faturamento(
    data_inicio: date,
    data_fim: date,
    conexao_banco: connection = Depends(obter_conexao_banco)
):
    if data_inicio >= data_fim:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A data de início deve ser anterior à data de fim."
        )
    relatorio = service.gerar_relatorio_faturamento(
        conexao_banco, data_inicio, data_fim
    )
    return relatorio

@router.post("", response_model=Reserva, status_code=status.HTTP_201_CREATED)
def criar_reserva(
    reserva: ReservaCriacao,
    conexao_banco: connection = Depends(obter_conexao_banco)
):
    try:
        return service.criar_reserva(conexao_banco, reserva)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=str(exc)
        ) from exc

@router.get("", response_model=List[Reserva])
def ler_reservas(conexao_banco: connection = Depends(obter_conexao_banco)):
    return service.obter_reservas(conexao_banco)

@router.get("/{reserva_id}", response_model=Reserva)
def ler_reserva(
    reserva_id: int, conexao_banco: connection = Depends(obter_conexao_banco)
):
    reserva_banco = service.obter_reserva_por_id(conexao_banco, reserva_id)
    if reserva_banco is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Reserva não encontrada"
        )
    return reserva_banco

@router.put("/{reserva_id}", response_model=Reserva)
def atualizar_reserva(
    reserva_id: int,
    dados_reserva: ReservaAtualizacao,
    conexao_banco: connection = Depends(obter_conexao_banco)
):
    try:
        reserva_atualizada = service.atualizar_reserva(
            conexao_banco, reserva_id, dados_reserva
        )
        return reserva_atualizada
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=str(exc)
        ) from exc

@router.delete("/{reserva_id}", status_code=status.HTTP_204_NO_CONTENT)
def deletar_reserva(
    reserva_id: int, conexao_banco: connection = Depends(obter_conexao_banco)
):
    deletado = service.deletar_reserva(conexao_banco, reserva_id)
    if not deletado:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reserva não encontrada"
        )