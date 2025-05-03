# products/urls.py
from django.urls import path
from .views import (
    add_product, 
    home, 
    premium_products, 
    accessories_products, 
    tshirts_products,
    delete_product,
    edit_product,
    tshirts_view,
    premium_collection,
    accessories_view,
    product_detail,
    ai_design,
    generate_design_view,
    add_ai_cart,
    admin_orders_view,
    mark_order_status
    
)

urlpatterns = [
    # Home Page
    path("", home, name="home"),
    
    # Add Product
    path("add-product/", add_product, name="add_product"),
    
    # Category Views
    path("premium/", premium_products, name="premium_products"),
    path("accessories/", accessories_products, name="accessories_products"),
    path("tshirts/", tshirts_products, name="tshirts_products"),
    
    # Product Deletion and Edit
    path('delete-product/<int:product_id>/', delete_product, name='delete_product'),
    path("edit-product/<int:product_id>/", edit_product, name="edit_product"),
    
    # Specific Category Views (Additional)
    path("t-shirts/", tshirts_view, name="tshirts"),
    path("premium/", premium_collection, name="premium"),
    path("accessories/", accessories_view, name="accessories"),
    path('ai-design/', ai_design, name='ai_design'),

     path('ai-design/generate/', generate_design_view, name='generate_design'),
    path('add-ai-cart/', add_ai_cart, name='add_ai_cart'),
   

       path('admin/orders/', admin_orders_view, name='admin_orders'),
    path('admin/orders/<int:order_id>/status/', mark_order_status, name='mark_order_status'),
    # Product Detail View
    path('product/<int:product_id>/', product_detail, name='product_detail'),
]
