# Descrição: API para receber pedidos e notificar a cozinha
from fastapi import FastAPI, WebSocket, HTTPException, Request
from services import clima, pedidos, websocket
from config import config
import logging
import time

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler(config.LOG_FILE), logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

app = FastAPI()

@app.middleware("http")
async def monitorar_tempo(request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    logger.info(f"Request: {request.method} {request.url} - Tempo: {process_time:.4f}s")
    return response

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.notificador.conectar(websocket)
    while True:
        await websocket.receive_text()

@app.post("/pedidos")
async def criar_pedido(request: Request):
    try:
        pedido = await request.json()
        esta_chovendo = await clima.verificar_chuva()
        
        if esta_chovendo:
            pedido["total"] += config.TAXA_CHUVA
            pedido["taxas"] = pedido.get("taxas", [])
            pedido["taxas"].append({
                "descricao": "Taxa de entrega (chuva)",
                "valor": config.TAXA_CHUVA
            })
        
        await pedidos.enviar_para_cozinha(pedido)
        
        await websocket.notificador.notificar(f"Novo pedido: {pedido['id']}")
        
        return {"mensagem": "Pedido criado com sucesso", "pedido": pedido}
    
    except Exception as e:
        logger.error(f"Erro ao processar pedido: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Erro ao processar pedido")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)