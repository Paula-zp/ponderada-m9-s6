# Descrição: Arquivo principal da aplicação FastAPI com a lógica de negócio
import time
import logging
from fastapi import FastAPI, Request, Depends
from pydantic import BaseModel
from app.clima import verificar_chuva
from fastapi.exceptions import HTTPException

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("app.log"), 
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="API de Pedidos",
    version="2.1.0",
)

@app.middleware("http")
async def add_headers(request: Request, call_next):
    start_time = time.time()
    
    client_version = request.headers.get("X-API-Version", app.version)
    if client_version != app.version:
        raise HTTPException(
            status_code=400,
            detail=f"Versão da API incompatível. Use a versão {app.version}"
        )
    
    response = await call_next(request)
    
    process_time = time.time() - start_time
    response.headers.update({
        "X-API-Version": app.version, 
        "X-Process-Time": f"{process_time:.4f}s"
    })
    
    logger.info(f"Tempo de processamento: {process_time:.4f}s")
    logger.info(f"Versao: {client_version}")
    
    return response

class Pedido(BaseModel):
    id: int
    itens: list[str]
    total: float

@app.post("/pedido")
async def fazer_pedido(pedido: Pedido, chuva: bool = Depends(verificar_chuva)):
    logger.info(f"Pedido recebido: {pedido}")
    logger.info(f"Chuva detectada: {chuva}")
    
    taxa_entrega = 5.0 if chuva else 0.0
    total_final = pedido.total + taxa_entrega
    
    return {"id": pedido.id, "version": app.version, "total": total_final, "taxa_entrega": taxa_entrega}
