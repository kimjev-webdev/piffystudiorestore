from django.contrib import admin
from .models import Product, Category, ProductImage

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1

class ProductAdmin(admin.ModelAdmin):
    list_display = ('title', 'price', 'product_type', 'featured')
    prepopulated_fields = {'slug': ('title',)}
    inlines = [ProductImageInline]

admin.site.register(Category)
admin.site.register(Product, ProductAdmin)
