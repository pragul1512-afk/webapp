# from django.db import models
# class User(models.Model):
#     username=models.CharField(max_length=255, default="")
#     email=models.EmailField(max_length=255, default="")
#     password=models.CharField(max_length=255, default="")

# Create your models here.
from django.db import models
from django.contrib.auth.models import User

# Food Menu Items
class MenuItem(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=6, decimal_places=2)
    image_url = models.URLField(blank=True, null=True)

    def __str__(self):  # <-- Fixed: Changed from _str_ to __str__
        return self.name

# Table Bookings
class Booking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    guest_name = models.CharField(max_length=100)
    guest_count = models.IntegerField()
    booking_date = models.DateField()
    booking_time = models.TimeField()
    created_at = models.DateTimeField(auto_now_add=True)

# Food Orders
class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    items = models.ManyToManyField(MenuItem, through='OrderItem')
    total_price = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    status = models.CharField(max_length=20, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)

# Order Item Relationship (Handles Quantities)
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
