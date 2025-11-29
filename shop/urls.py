from django.urls import path
from . import views

app_name = 'shop'

urlpatterns = [
    # PUBLIC SHOP
    path('', views.product_list, name='product_list'),

    # MANAGEMENT (MUST GO BEFORE SLUG ROUTE)
    path('manage/products/', views.manage_products, name='manage_products'),
    path('manage/products/add/', views.add_product, name='add_product'),
    path('manage/products/<int:pk>/edit/', views.edit_product, name='edit_product'),
    path('manage/products/<int:pk>/delete/', views.delete_product, name='delete_product'),

    # PRODUCT DETAIL (CATCH-ALL LAST)
    path('<slug:slug>/', views.product_detail, name='product_detail'),
]
