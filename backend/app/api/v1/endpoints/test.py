"""Endpoint de teste SEM banco para verificar se backend funciona"""
from fastapi import APIRouter

test_router = APIRouter(prefix="/test", tags=["Test"])

@test_router.get("/ping")
async def ping():
    """Teste simples sem banco"""
    return {"status": "pong", "message": "Backend funcionando!"}

@test_router.post("/echo")
async def echo(data: dict):
    """Echo dos dados recebidos"""
    return {"received": data, "status": "ok"}
