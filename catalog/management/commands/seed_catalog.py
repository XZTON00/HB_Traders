from django.core.management.base import BaseCommand

from catalog.models import BusinessDetail, Product, ProductSpec


class Command(BaseCommand):
    help = "Seeds the business details and 20 placeholder products, matching the original static catalog."

    def handle(self, *args, **options):
        business, _ = BusinessDetail.objects.update_or_create(
            pk=1,
            defaults=dict(
                company_name="H.B. Trader's",
                tagline="Est. Supplier · UP Region",
                subtitle="Wholesale & Retail Sanitary Items",
                description=(
                    "We supply sanitary products in both wholesale and retail. "
                    "We procure directly from manufacturers and distributors, then "
                    "supply straight to retail shops and customers across the region."
                ),
                address="UP, Pharenda, Anand Nagar, Maharajganj",
                phone="8114218260",
                email="arslanayan761@gmail.com",
            ),
        )
        self.stdout.write(self.style.SUCCESS(f"Business detail ready: {business}"))

        created_count = 0
        for n in range(1, 21):
            product, created = Product.objects.get_or_create(
                number=n,
                defaults=dict(
                    name=f"Item {n}",
                    sku=f"HBT-{n:02d}",
                    price="",
                    description=(
                        "Product description placeholder. Replace this text with "
                        "details about material, pack size, usage, and anything "
                        "customers need to know."
                    ),
                    in_stock=True,
                    is_active=True,
                ),
            )
            if created:
                created_count += 1
                for label, value in [("Brand", "—"), ("Pack Size", "—"), ("Unit", "—"), ("SKU", f"HBT-{n:02d}")]:
                    ProductSpec.objects.create(product=product, label=label, value=value)

        self.stdout.write(self.style.SUCCESS(f"Products seeded: {created_count} created, {20 - created_count} already existed."))
