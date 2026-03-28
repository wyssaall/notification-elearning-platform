import logging

from django.core.management.base import BaseCommand

from notifications.messaging import run_consumer

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Consume RabbitMQ messages and create notifications (blocking)."

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("Starting RabbitMQ consumer..."))
        run_consumer()
