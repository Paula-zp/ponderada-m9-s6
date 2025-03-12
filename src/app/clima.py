# Descrição: Função para verificar se está chovendo em São Paulo
import requests

async def verificar_chuva():
    url = "https://api.open-meteo.com/v1/forecast?latitude=-23.5505&longitude=-46.6333&current=precipitation"
    resposta = requests.get(url).json()
    return resposta.get("current", {}).get("precipitation", 0) > 0