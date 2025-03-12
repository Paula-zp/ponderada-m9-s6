# Descrição: Serviço para notificar clientes via WebSocket
from fastapi import WebSocket
import logging
from typing import List

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Notificador:
    def __init__(self):
        self.conexoes: List[WebSocket] = []

    async def conectar(self, websocket: WebSocket):
        await websocket.accept()
        self.conexoes.append(websocket)
        logger.info("Nova conexão WebSocket estabelecida")

    async def notificar(self, mensagem: str):
        for conexao in self.conexoes:
            await conexao.send_text(mensagem)
        logger.info(f"Notificação enviada: {mensagem}")

notificador = Notificador()