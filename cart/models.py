from django.db import models
from django.conf import settings
from products.models import Product
from users_app.models import UserProfile  #

class Cart(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=20, default="active")  # For order/payment tracking

    def __str__(self):
        return f"Cart of {self.user}"

    def total_price(self):
        return sum(item.total_price() for item in self.items.all())

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True)
    quantity = models.PositiveIntegerField(default=1)  # Fix: prevents NULL
    size = models.CharField(max_length=5, default="M")
    custom_image_url = models.TextField(null=True, blank=True)
    custom_name = models.CharField(max_length=255, null=True, blank=True)

    def total_price(self):
        if self.product:
            return self.product.price_inr * self.quantity
        return 600 * self.quantity  # fallback price if product is missing

    class Meta:
        db_table = 'cart_cartitem'

    def __str__(self):
        if self.custom_name:
            return f"{self.quantity} × {self.custom_name} (AI Design)"
        elif self.product:
            return f"{self.quantity} × {self.product.name} ({self.size})"
        return f"{self.quantity} × Unknown Item"


# ————————————————
# ORDER MODELS
# ————————————————

class Order(models.Model):
    order_id = models.AutoField(primary_key=True) 
    order_code = models.CharField(max_length=50, unique=True)
    



    
    user = models.ForeignKey(
    UserProfile,
    on_delete=models.CASCADE,
    db_column="user_id"
)
    cart_id = models.IntegerField(db_column="cart_id")
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    region = models.CharField(max_length=100, blank=True, null=True)
    house_number = models.CharField(max_length=50)
    street_name = models.CharField(max_length=255)
    apartment_suite_unit = models.CharField(max_length=100)
    town = models.CharField(max_length=100, blank=True, null=True)
    city = models.CharField(max_length=100)
    post_code = models.CharField(max_length=20)
    phone = models.CharField(max_length=20)
    order_notes = models.TextField(blank=True, null=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    shipping_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    status = models.CharField(
        max_length=30,
        choices=[
            ('Pending', 'Pending'),
            ('Paid', 'Paid'),
            ('Failed', 'Failed'),
            ('Order to be delivered', 'Order to be delivered'),
            ('Delivered', 'Delivered'),
        ],
        default='Pending'
    )
    razorpay_order_id = models.CharField(max_length=100, blank=True, null=True)
    razorpay_payment_id = models.CharField(max_length=100, blank=True, null=True)
    razorpay_signature = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "orders"
        managed = False  # Important: make sure DB has this already created

    @property
    def calculate_total(self):
        return self.total_price + self.shipping_price

    def __str__(self):
        return f"Order {self.order_id} by {self.user}"

class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items",
        db_column="order_id",
        null=True,
    )
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True)
    quantity = models.PositiveIntegerField()
    product_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    size = models.CharField(max_length=5, default="M") 

    class Meta:
        db_table = "order_items"
        managed = True  # Let Django manage this if you're not syncing to an existing table

    @property
    def total_price(self):
        # Use the related product's price
        if self.product:
            return self.product.price_inr * self.quantity
        return 0  # Fallback if no product is associated

    def __str__(self):
        return f"{self.quantity} × {self.product.name if self.product else 'Unknown Product'}"

from django.contrib.auth import get_user_model
User = get_user_model()
class OrderAddress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    country = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    house_number = models.CharField(max_length=10)
    street_name = models.CharField(max_length=100)
    city = models.CharField(max_length=50)
    post_code = models.CharField(max_length=10)
    phone = models.CharField(max_length=15)
    order_notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
