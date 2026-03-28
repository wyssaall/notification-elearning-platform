#!/usr/bin/env python3
"""Demo publisher (Course Service). Same JSON as the notification consumer expects.

Usage: python examples/course_service_producer.py [user_id] [course_name]
Requires: RabbitMQ running, pika installed (`pip install -r requirements.txt`).
"""
import json
import os
import sys

import pika

QUEUE = os.environ.get("RABBITMQ_QUEUE", "notifications.enrollment")
HOST = os.environ.get("RABBITMQ_HOST", "localhost")
PORT = int(os.environ.get("RABBITMQ_PORT", "5672"))
USER = os.environ.get("RABBITMQ_USER", "guest")
PASSWORD = os.environ.get("RABBITMQ_PASSWORD", "guest")


def publish_enrollment_notification(user_id: int, course_name: str) -> None:
    payload = {
        "user_id": user_id,
        "title": "Enrollment confirmed",
        "message": f'You are now enrolled in "{course_name}".',
    }
    body = json.dumps(payload).encode("utf-8")

    credentials = pika.PlainCredentials(USER, PASSWORD)
    params = pika.ConnectionParameters(
        host=HOST, port=PORT, credentials=credentials
    )
    connection = pika.BlockingConnection(params)
    channel = connection.channel()
    channel.queue_declare(queue=QUEUE, durable=True)

    channel.basic_publish(
        exchange="",
        routing_key=QUEUE,
        body=body,
        properties=pika.BasicProperties(
            delivery_mode=2,
            content_type="application/json",
        ),
    )
    connection.close()
    print(f"Sent to queue {QUEUE!r}: {payload}")


if __name__ == "__main__":
    uid = int(sys.argv[1]) if len(sys.argv) > 1 else 42
    course = sys.argv[2] if len(sys.argv) > 2 else "Introduction to Django"
    publish_enrollment_notification(uid, course)
