# from django.contrib import admin
# from .models import User

# admin.site.register([User])

# Register your models here.
from django.contrib import admin
from .models import MenuItem, Booking, Order, OrderItem

# Register your custom models here
admin.site.register(MenuItem)
admin.site.register(Booking)
admin.site.register(Order)
admin.site.register(OrderItem)

# DO NOT include admin.site.register(User) here!
