from django.core.management.base import BaseCommand

from common.tasks import cleanup_accounts

class Command(BaseCommand):
    help = 'Deletes all accounts without a verified e-mail address'

    def handle(self, *args, **options):
        cleanup_accounts()
