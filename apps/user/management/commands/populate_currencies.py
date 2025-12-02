from django.core.management.base import BaseCommand
import pycountry
from ...models import Currency


class Command(BaseCommand):
    help = 'Populates the Currency table with ISO 4217 world currencies'
    # https://www.iso.org/iso-4217-currency-codes.html

    def handle(self, *args, **kwargs):
        self.stdout.write("Starting currency population...")

        count = 0
        for currency in pycountry.currencies:
            code = currency.alpha_3
            name = currency.name

            if len(name) > 128:
                name = name[:128]

            obj, created = Currency.objects.update_or_create(
                currency_short_name=code,
                defaults={'currency_long_name': name}
            )

            if created:
                count += 1

        self.stdout.write(self.style.SUCCESS(f'Successfully added {count} new currencies.'))