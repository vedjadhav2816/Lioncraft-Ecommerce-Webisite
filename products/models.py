from django.db import models

class Product(models.Model):
    # explicitly tell Django “this is a BIGINT primary key”
    id = models.BigAutoField(primary_key=True)

    CATEGORY_CHOICES = [
        ('Premium',     'Premium'),
        ('Accessories', 'Accessories'),
        ('T‑Shirts',    'T‑Shirts'),
    ]
    category      = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    name          = models.CharField(max_length=255)
    description   = models.TextField()
    price_inr     = models.DecimalField(max_digits=10, decimal_places=2)
    price_usd     = models.DecimalField(max_digits=10, decimal_places=2)
    image1        = models.ImageField(upload_to='products/', blank=True, null=True)
    image2        = models.ImageField(upload_to='products/', blank=True, null=True)
    image3        = models.ImageField(upload_to='products/', blank=True, null=True)
    custom_name   = models.CharField(max_length=255, null=True, blank=True)
    custom_image_url = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "products"
