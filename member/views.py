# from django.shortcuts import render,redirect

# from django.http import HttpResponse

# def Home(request):
#     return HttpResponse("<h1> hi ragul</h1>")
# def NAME(request):
#     return HttpResponse("<h1> hi muthu anna</h1>")
# def contact(request):
#     return render(request,"index.html")


# # def registor(request):
# #     if request.method == "POST":
# #         username=request.POST.get('name')
        
# #         email=request.POST.get('email')
# #         password=request.POST.get('password')
# #         user=users(username=username , email=email , password=password)
# #         user.save()
# #         return redirect('/data/')
# #     return render(request,"registor.html")
# # def data (request):

# #     users=User.objects.all()
# #     print(users)
# #     return render(request ,"data.html", {"users": users})    
# # Create your views here.

# # Create your views here.
# from django.shortcuts import render, redirect
# from django.contrib.auth.models import User  # Standard Django User model

# def registor(request):
#     if request.method == "POST":
#         username = request.POST.get('name')
#         email = request.POST.get('email')
#         password = request.POST.get('password')
        
#         # FIX: Added .objects here to properly access the manager
#         user = User.objects.create_user(username=username, email=email, password=password)
#         # user.save() is NOT needed here; create_user saves it automatically!
        
#         return redirect('/data/')
        
#     return render(request, "registor.html")

# def data(request):
#     all_users = User.objects.all() 
#     return render(request, "data.html", {"users": all_users})

# def Update(request,id):
#     user=User.objects.get(id=id)
#     if request.method=="POST":
#          username=request.POST.get('username')
#          email=request.POST.get('email')
#          password=request.POST.get('password')
#          user=User.objects.get(id=id)
#          user.username=username
#          user.email=email
#          user.password=password
#          user.save()
#          return redirect('/data/')
#     return render(request,"Update.html",{"user":user})

# def Delete(request,id):
#     user=User.objects.get(id=id)
#     user.delete()
#     return redirect('/data')



import json
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import MenuItem, Booking, Order, OrderItem

# Home view fetching menu items
def index(request):
    menu_items = MenuItem.objects.all()
    return render(request, 'restaurant/index.html', {'menu_items': menu_items})

# Handle Table Reservation
@login_required
def book_table(request):
    if request.method == 'POST':
        guest_name = request.POST.get('name')
        guest_count = request.POST.get('guests')
        booking_date = request.POST.get('date')
        booking_time = request.POST.get('time')
        
        Booking.objects.create(
            user=request.user,
            guest_name=guest_name,
            guest_count=guest_count,
            booking_date=booking_date,
            booking_time=booking_time
        )
        return redirect('index')
    return render(request, 'restaurant/index.html')

# Handle Cart Checkout API
@login_required
def checkout_order(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            cart = data.get('cart', [])
            
            if not cart:
                return JsonResponse({'error': 'Cart is empty'}, status=400)

            # Create Order Shell
            order = Order.objects.create(user=request.user, total_price=0)
            total = 0

            for cart_item in cart:
                item = MenuItem.objects.get(id=cart_item['id'])
                qty = int(cart_item['quantity'])
                OrderItem.objects.create(order=order, item=item, quantity=qty)
                total += item.price * qty
            
            order.total_price = total
            order.save()
            return JsonResponse({'message': 'Order placed successfully!'}, status=201) # <-- Fixed: Return JSON for API
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Invalid request method'}, status=400)
