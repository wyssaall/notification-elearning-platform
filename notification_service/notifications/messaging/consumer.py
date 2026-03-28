"""
RabbitMQ consumer: receives JSON messages and creates Notification rows.
Run with: python manage.py run_rabbitmq_consumer
"""
import json
import logging

import pika
from django.conf import settings

from notifications.models import Notification

logger = logging.getLogger(__name__)


def _get_connection_params() -> pika.ConnectionParameters:
    return pika.ConnectionParameters(
        host=settings.RABBITMQ_HOST,
        port=settings.RABBITMQ_PORT,
        credentials=pika.PlainCredentials(
            settings.RABBITMQ_USER,
            settings.RABBITMQ_PASSWORD,
        ),
        heartbeat=600,
        blocked_connection_timeout=300,
    )


def _handle_message(body: bytes) -> None:
    data = json.loads(body.decode("utf-8"))
    user_id = int(data["user_id"])
    title = str(data["title"])
    message = str(data["message"])
    Notification.objects.create(user_id=user_id, title=title, message=message)


def run_consumer() -> None:
    queue = settings.RABBITMQ_QUEUE
    params = _get_connection_params()
    connection = pika.BlockingConnection(params)
    channel = connection.channel()
    channel.queue_declare(queue=queue, durable=True)

    def callback(ch, method, properties, body):
        try:
            _handle_message(body)
            ch.basic_ack(delivery_tag=method.delivery_tag)
        except Exception:
            logger.exception("Failed to process message; rejecting without requeue")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=queue, on_message_callback=callback)
    logger.info("Waiting for messages on queue %r. To exit press CTRL+C", queue)
    channel.start_consuming()
