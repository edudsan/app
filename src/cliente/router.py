from typing import List
from psycopg2 import errors
from psycopg2.extensions import connection
from fastapi import APIRouter, Depends, HTTPException, status
from src.database.connection import obter_conexao_banco
from . import service
from .schema import (
    Pessoa, PessoaFisicaCriacao, PessoaAtualizacao, PessoaJuridicaCriacao
)

router = APIRouter(prefix="/clientes", tags=["Clientes"])

@router.post("/pf", response_model=Pessoa, status_code=status.HTTP_201_CREATED)
def criar_cliente_pf(
    cliente: PessoaFisicaCriacao,
    conexao_banco: connection = Depends(obter_conexao_banco)
):
    try:
        return service.criar_cliente_pf(conexao_banco, cliente)
    except errors.UniqueViolation as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="O e-mail ou CPF fornecido já está em uso."
        ) from exc

@router.post("/pj", response_model=Pessoa, status_code=status.HTTP_201_CREATED)
def criar_cliente_pj(
    cliente: PessoaJuridicaCriacao,
    conexao_banco: connection = Depends(obter_conexao_banco)
):
    try:
        return service.criar_cliente_pj(conexao_banco, cliente)
    except errors.UniqueViolation as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="O e-mail ou CNPJ fornecido já está em uso."
        ) from exc

@router.get("", response_model=List[Pessoa])
def ler_clientes(conexao_banco: connection = Depends(obter_conexao_banco)):
    return service.obter_clientes(conexao_banco)

@router.get("/{pessoa_id}", response_model=Pessoa)
def ler_cliente(
    pessoa_id: int, conexao_banco: connection = Depends(obter_conexao_banco)
):
    cliente_banco = service.obter_cliente_por_id(conexao_banco, pessoa_id)
    if cliente_banco is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cliente não encontrado"
        )
    return cliente_banco

@router.put("/{pessoa_id}", response_model=Pessoa)
def atualizar_cliente(
    pessoa_id: int,
    dados_cliente: PessoaAtualizacao,
    conexao_banco: connection = Depends(obter_conexao_banco)
):
    try:
        atualizado = service.atualizar_cliente(
            conexao_banco, pessoa_id, dados_cliente
        )
        if atualizado is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cliente não encontrado"
            )
        return atualizado
    except errors.UniqueViolation as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="O e-mail fornecido já está em uso."
        ) from exc

@router.delete("/{pessoa_id}", status_code=status.HTTP_204_NO_CONTENT)
def deletar_cliente(
    pessoa_id: int, conexao_banco: connection = Depends(obter_conexao_banco)
):
    try:
        deletado = service.deletar_cliente(conexao_banco, pessoa_id)
        if not deletado:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cliente não encontrado"
            )
    except errors.ForeignKeyViolation as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Não é possível deletar cliente com reservas ativas."
        ) from exc