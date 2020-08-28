from django.core.management.base import BaseCommand

from ballot_source.sources.models import Source


class Command(BaseCommand):
    help = "Scrape new versions of every source"

    def handle(self, *args, **kwargs):
        for source in Source.objects.all():
            self.stdout.write(self.style.NOTICE(f"Scraping {source}"))
            source.scrape()
            msg = "Success: No differences found"

            if source.details.last().date_pulled == source.last_checked:
                msg = "Success: Differences found"

            self.stdout.write(self.style.SUCCESS(msg))
