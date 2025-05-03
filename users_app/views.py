from django.shortcuts import render, redirect
from django.contrib import messages
from users_app.models import UserProfile
from django.contrib.auth.hashers import make_password
from cart.models import Order, CartItem, Cart  # If Cart and Order models are in the 'cart' app
from products.models import Product  # If Product model is in the 'products' app

def register(request):
    if request.method == "POST":
        username         = request.POST["username"].strip()
        email            = request.POST["email"].strip()
        password         = request.POST["password"]
        confirm_password = request.POST["confirm_password"]

        if password != confirm_password:
            messages.error(request, "Passwords do not match!")
            return redirect("register")

        if UserProfile.objects.filter(username=username).exists():
            messages.error(request, "Username already taken!")
            return redirect("register")

        if UserProfile.objects.filter(email=email).exists():
            messages.error(request, "Email already in use!")
            return redirect("register")

        user = UserProfile(username=username, email=email)
        user.set_password(password)
        user.save()

        messages.success(request, "Account created! Please log in.")
        return redirect("login")

    return render(request, "register.html")


from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.hashers import check_password
from users_app.models import UserProfile

from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.hashers import check_password
from users_app.models import UserProfile

from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.hashers import check_password
from users_app.models import UserProfile
def login_view(request):
    if request.session.get("user_id"):
        return redirect(request.GET.get("next", "home"))

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        try:
            user = UserProfile.objects.get(username=username)
            if check_password(password, user.password):
                # ✅ Set session manually
                request.session["user_id"] = user.id
                request.session["username"] = user.username
                request.session["is_superuser"] = user.is_superuser  # Optional

                return redirect(request.GET.get("next", "home"))
            else:
                messages.error(request, "Invalid password.")
        except UserProfile.DoesNotExist:
            messages.error(request, "User does not exist.")

    return render(request, "login.html")


# ✅ Logout View
def logout_view(request):
    request.session.flush()  # Clear session
    messages.success(request, "You have been logged out.")
    return redirect("home")



# ✅ Basic Pages
def about(request):
    return render(request, "about.html")


def contact(request):
    return render(request, "contact.html")


def home(request):
    if request.user.is_authenticated:
        order = Order.objects.filter(user=request.user).first()
        return render(request, 'home.html', {'order': order})
    else:
        return render(request, 'home.html')  # Return something even if not logged in

# users_app/views.py
from django.shortcuts import render
from cart.models import Order  # adjust path if needed
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Order

from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from users_app.models import UserProfile
from cart.models import Order  
from django.shortcuts import render, redirect, get_object_or_404
from .models import UserProfile, Order

from django.shortcuts import render, redirect, get_object_or_404
from users_app.models import UserProfile
from cart.models import Order

def user_orders(request):
    user_id = request.session.get("user_id")
    if not user_id:
        return redirect("login")

    user = get_object_or_404(UserProfile, id=user_id)

    # grab all orders (newest first), along with their items and products
    orders = (
        Order.objects
             .filter(user=user)
             .prefetch_related("items__product")
             .order_by("-created_at")
    )

    # blank out any “N/A” values so your template shows nothing instead
    for order in orders:
        for f in ("house_number", "street_name", "city",
                  "state", "country", "post_code", "phone"):
            if getattr(order, f) == "N/A":
                setattr(order, f, "")

    return render(request, "orders.html", {"orders": orders})



# from django.shortcuts import render
# from django.contrib.auth.decorators import login_required
# from .models import Order
# @login_required
# def user_profile_view(request):
#     print(request.user)  # Check if user is logged in
#     user_orders = Order.objects.filter(user=request.user).prefetch_related("items__product").order_by("-created_at")
#     return render(request, "user_profile.html", {"orders": user_orders})

from django.shortcuts import render
from django.http import HttpResponse
from .models import Order
import csv
def sales_report_view(request):
    """
    Shows sales.html with delivered orders.
    """
    delivered_orders = Order.objects.filter(status='Delivered').order_by('-created_at')
    for order in delivered_orders:
        print(order.items.all())  # Debugging: Check if items are properly linked
    return render(request, 'sales.html', {'orders': delivered_orders})

def download_sales_csv(request):
    """
    Downloads a CSV file with all delivered orders.
    """
    response = HttpResponse(
        content_type='text/csv',
        headers={'Content-Disposition': 'attachment; filename="sales_report.csv"'},
    )

    writer = csv.writer(response)
    writer.writerow(['Order ID', 'Buyer Email', 'Total (₹)', 'Items', 'Address', 'Phone', 'Order Date'])

    delivered_orders = Order.objects.filter(status='Delivered')

    for order in delivered_orders:
        items = []
        for it in order.items.all():
            if it.product:
                items.append(f"{it.product.name} ×{it.quantity}")
            else:
                items.append(f"{it.custom_name} ×{it.quantity}")
        items_str = "; ".join(items)

        address = f"{order.house_number}, {order.street_name}, {order.city}, {order.state}, {order.country} - {order.post_code}"

        writer.writerow([
            order.order_id,
            order.user.email,
            order.calculate_total,
            items_str,
            address,
            order.phone,
            order.created_at.strftime("%Y-%m-%d %H:%M")
        ])

    return response
