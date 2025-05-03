from django.db import models
from django.contrib.auth.hashers import make_password, check_password

class UserProfile(models.Model):
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)  # Store hashed passwords
    is_superuser = models.BooleanField(default=False)  # Superuser flag
    created_at = models.DateTimeField(auto_now_add=True)

    # Required attributes for Django's auth checks
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []  # You can add additional required fields if needed

    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)

    def __str__(self):
        return self.username

    @property
    def is_authenticated(self):
        """Return True if the user is authenticated."""
        return True

    @property
    def is_anonymous(self):
        """Return False as this is a real user, not an anonymous user."""
        return False

# users_app/models.py

from django.db import models
from products.models import Product  # Import the Product model from the products app
from cart.models import Order  # Import the Order model from the current app

class OrderProduct(models.Model):
    order = models.ForeignKey(Order, related_name='order_products', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)  # Link to the Product model
    quantity = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.product.name} (x{self.quantity})"
