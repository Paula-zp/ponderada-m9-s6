import os
from dotenv import load_dotenv

# Carrega explicitamente o .env localizado em src
dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(dotenv_path)

class Config:
    # Configurações da API de clima
    API_CLIMA_URL = os.getenv("API_CLIMA_URL", "https://api.open-meteo.com/v1/forecast")
    LATITUDE = os.getenv("LATITUDE", "-23.5505")
    LONGITUDE = os.getenv("LONGITUDE", "-46.6333")

    # Configurações do RabbitMQ
    RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost/")

    # Configurações gerais
    TAXA_CHUVA = 5.0
    LOG_FILE = "app.log"

config = Config()