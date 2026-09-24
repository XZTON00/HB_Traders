from django.contrib import admin
from django.utils.html import format_html

from .models import BusinessDetail, Product, ProductSpec

admin.site.site_header = "H.B. Trader's — Admin"
admin.site.site_title = "H.B. Trader's Admin"
admin.site.index_title = "Catalog Management"


class ProductSpecInline(admin.TabularInline):
    model = ProductSpec
    extra = 1


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("number", "thumb", "name", "sku", "price", "in_stock", "is_active")
    list_display_links = ("number", "name")
    list_editable = ("price", "in_stock", "is_active")
    list_filter = ("in_stock", "is_active")
    search_fields = ("name", "sku", "number")
    ordering = ("number",)
    inlines = [ProductSpecInline]
    fieldsets = (
        (None, {"fields": ("number", "name", "sku", "image")}),
        ("Storefront details", {"fields": ("price", "description", "in_stock", "is_active")}),
    )

    @admin.display(description="Image")
    def thumb(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="height:38px;width:38px;object-fit:cover;border:2px solid #101010;">', obj.image.url)
        return "—"


@admin.register(BusinessDetail)
class BusinessDetailAdmin(admin.ModelAdmin):
    list_display = ("company_name", "phone", "email", "address")
    fieldsets = (
        ("Branding", {"fields": ("company_name", "tagline", "subtitle", "description")}),
        ("Contact", {"fields": ("address", "phone", "email")}),
    )

    def has_add_permission(self, request):
        return not BusinessDetail.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False
