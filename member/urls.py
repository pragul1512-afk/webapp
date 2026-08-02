# from django.urls import path

# from . import views

# urlpatterns = [
#     # path('admin/', admin.site.urls),
#     path('NAME',views.NAME),
#     path('con', views.contact),
#     path('reg',views.registor),
#     path('data/',views.data,name="data"),
#     path('Update/<int:id>', views.Update,name="Update"),
#     path('Delete/<int:id>', views.Delete,name="Delete"),
# ]
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('book/', views.book_table, name='book_table'),
    path('checkout/', views.checkout_order, name='checkout_order'),
]
