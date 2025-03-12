# Descrição: Serviço para enviar um pedido para a cozinha
import aio_pika
import json
import logging
from config import config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def enviar_para_cozinha(pedido):
    try:
        connection = await aio_pika.connect_robust(config.RABBITMQ_URL)
        channel = await connection.channel()
        queue = await channel.declare_queue("cozinha", durable=True)
        logger.info("Fila 'cozinha' declarada com sucesso")
        
        await channel.default_exchange.publish(
            aio_pika.Message(body=json.dumps(pedido).encode()),
            routing_key="cozinha"
        )
        
        await connection.close()
        logger.info(f"Pedido {pedido['id']} enviado para cozinha")
    except Exception as e:
        logger.error("Erro ao enviar pedido para cozinha. Verifique se o RabbitMQ está rodando e acessível.", exc_info=True)
        raise