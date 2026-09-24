from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse


class BusinessDetail(models.Model):
    company_name = models.CharField(max_length=120, default="H.B. Trader's")
    tagline = models.CharField(max_length=120, default="Est. Supplier · UP Region")
    subtitle = models.CharField(max_length=160, default="Wholesale & Retail Sanitary Items")
    description = models.TextField(default=(
        "We supply sanitary products in both wholesale and retail. "
        "We procure directly from manufacturers and distributors, then "
        "supply straight to retail shops and customers across the region."
    ))
    address = models.CharField(max_length=255, default="UP, Pharenda, Anand Nagar, Maharajganj")
    phone = models.CharField(max_length=20, default="8114218260")
    email = models.EmailField(default="arslanayan761@gmail.com")

    class Meta:
        verbose_name = "Business Detail"
        verbose_name_plural = "Business Details"

    def save(self, *args, **kwargs):
        if not self.pk and BusinessDetail.objects.exists():
            self.pk = BusinessDetail.objects.first().pk
        super().save(*args, **kwargs)

    def clean(self):
        if BusinessDetail.objects.exclude(pk=self.pk).exists():
            raise ValidationError("Only one Business Detail record is allowed. Edit the existing one instead.")

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

    def whatsapp_number(self):
        digits = "".join(ch for ch in self.phone if ch.isdigit())
        return f"91{digits}" if len(digits) == 10 else digits

    def __str__(self):
        return self.company_name


class Product(models.Model):
    number = models.PositiveIntegerField(unique=True, help_text="Catalog position, e.g. 1, 2, 3…")
    name = models.CharField(max_length=120)
    sku = models.CharField(max_length=40, blank=True)
    price = models.CharField(max_length=40, blank=True, default="",
        help_text="Displayed after the ₹ symbol. Leave blank to show '______'.")
    description = models.TextField(blank=True, default="")
    image = models.ImageField(upload_to="products/", blank=True, null=True)
    in_stock = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True, help_text="Untick to hide from the catalog without deleting it.")

    class Meta:
        ordering = ["number"]

    def save(self, *args, **kwargs):
        if not self.sku:
            self.sku = f"HBT-{self.number:02d}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.number:02d} — {self.name}"

    def get_absolute_url(self):
        return reverse("catalog:product_detail", args=[self.number])

    def display_price(self):
        return self.price if self.price else "______"

    def variant(self):
        return "abcd"[(self.number - 1) % 4]

    def previous(self):
        return Product.objects.filter(number__lt=self.number, is_active=True).order_by("-number").first()

    def next(self):
        return Product.objects.filter(number__gt=self.number, is_active=True).order_by("number").first()


class ProductSpec(models.Model):
    product = models.ForeignKey(Product, related_name="specs", on_delete=models.CASCADE)
    label = models.CharField(max_length=60)
    value = models.CharField(max_length=120)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return f"{self.label}: {self.value}"
