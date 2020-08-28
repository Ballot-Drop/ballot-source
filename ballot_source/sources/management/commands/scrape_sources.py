from django.contrib.sites.models import Site
from django.core.mail import send_mail
from django.core.management.base import BaseCommand

from ballot_source.sources.models import Source


class Command(BaseCommand):
    help = "Scrape new versions of every source"

    def handle(self, *args, **kwargs):
        changes = []
        for source in Source.objects.all():
            self.stdout.write(self.style.NOTICE(f"Scraping {source}"))
            source.scrape()
            msg = "Success: No differences found"

            if source.details.first().date_pulled == source.last_checked:
                msg = "Success: Differences found"
                changes.append(source)

            self.stdout.write(self.style.SUCCESS(msg))
        if changes:
            html_msg = (
                "<strong>Ballot Source found changes in the following sites</strong>"
                "<ul>"
            )
            for source in changes:
                html_msg += f"""
                    <li>
                        {source.url} -
                        <a href='{Site.objects.get_current().domain}{source.get_absolute_url()}'>See changes</a>
                    </li>
                    """
            html_msg += "</ul>"

            msg = "Ballot source found changes."
            send_mail(
                "Ballot Source: Scrape found changes",
                msg,
                from_email="ballotsource@somewhere.net",
                recipient_list=["pj.hoberman@gmail.com"],
                fail_silently=False,
                html_message=html_msg,
            )
