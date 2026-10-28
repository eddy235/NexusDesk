from django.core.management.base import BaseCommand
from desk.sla import record_escalations

class Command(BaseCommand):
    help = 'Record overdue deadline events'

    def handle(self, *args, **options):
        count = record_escalations()
        self.stdout.write(f'{count} new deadline breaches recorded.')
