from django.urls import path
from .views import add_to_cart, cart_page, remove_from_cart, cart_count_view, add_ai_cart, test_filter,payment_view,create_order,verify_payment,payment_success_view,update_cart_item

app_name = "cart"

urlpatterns = [
    path("add/<int:product_id>/", add_to_cart, name="add_to_cart"),
    path("", cart_page, name="cart_page"),
    path("remove/<int:cart_item_id>/", remove_from_cart, name="remove_from_cart"),
    path("count/", cart_count_view, name="cart_count"),
    path("add-ai-cart/", add_ai_cart, name="add_ai_cart"),
      path('update/<int:item_id>/', update_cart_item, name='update_cart_item'),

    
  
   
    path("test/", test_filter, name="test_filter"),
     path('payment/',         payment_view,          name='payment'),
    path('create_order/',    create_order,          name='create_order'),
    path('verify_payment/',  verify_payment,        name='verify_payment'),
    path('payment_success/', payment_success_view,  name='payment_success'),
    
]
