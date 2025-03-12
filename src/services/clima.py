# Descrição: Serviço para consultar a API de clima e verificar se está chovendo na região
import httpx
import logging
from config import config

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def verificar_chuva():
    try:
        params = {
            "latitude": config.LATITUDE,
            "longitude": config.LONGITUDE,
            "current": "precipitation",
            "timezone": "America/Sao_Paulo"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(config.API_CLIMA_URL, params=params)
            response.raise_for_status()
            
            dados = response.json()
            
            if "current" not in dados or "precipitation" not in dados["current"]:
                logger.error("Resposta da API de clima com estrutura inválida")
                return False
            
            return dados["current"]["precipitation"] > 0
            
    # Regra: Em caso de erro, retornar False porque é melhor não cobrar a taxa do que cobrar indevidamente
    except Exception as e:
        logger.error(f"Erro ao consultar API de clima: {e}", exc_info=True)
        return False
    