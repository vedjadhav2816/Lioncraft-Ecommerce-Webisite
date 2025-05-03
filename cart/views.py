from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from products.models import Product
from .models import Cart, CartItem
from users_app.models import UserProfile

def add_to_cart(request, product_id):
    if request.method == "POST":
        product = get_object_or_404(Product, id=product_id)
        quantity = int(request.POST.get("quantity", 1))
        size = request.POST.get("size", "M")

        user_id = request.session.get("user_id")
        if user_id:
            user = get_object_or_404(UserProfile, id=user_id)
            cart, _ = Cart.objects.get_or_create(user=user)
            cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product, size=size)
            if not created:
                cart_item.quantity += quantity
            else:
                cart_item.quantity = quantity
            cart_item.save()
            cart_count = CartItem.objects.filter(cart=cart).count()
            return JsonResponse({
                "status": "success",
                "message": f"{product.name} added to cart!",
                "cart_count": cart_count
            })
        else:
            # Guest user cart handling (in session)
            cart = request.session.get("cart", {})
            cart_item_key = f"{product_id}_{size}"
            if cart_item_key in cart:
                cart[cart_item_key]["quantity"] += quantity
            else:
                cart[cart_item_key] = {
                    "quantity": quantity,
                    "size": size,
                    "product_id": product_id
                }
            request.session["cart"] = cart
            request.session.modified = True
            cart_count = len(cart)
            return JsonResponse({
                "status": "success",
                "message": f"{product.name} added to cart (guest)!",
                "cart_count": cart_count
            })

    return JsonResponse({"status": "error", "error": "Invalid request"}, status=400)


def cart_page(request):
    user_id = request.session.get("user_id")
    if not user_id:
        return redirect("login")

    user = get_object_or_404(UserProfile, id=user_id)
    cart = Cart.objects.filter(user=user).first()
    cart_items = CartItem.objects.filter(cart=cart) if cart else []

    total_price = 0
    for item in cart_items:
        if item.product:
            total_price += item.product.price_inr * item.quantity
        else:
            total_price += 600 * item.quantity

    return render(request, "cart.html", {"cart_items": cart_items, "total_price": total_price})


def remove_from_cart(request, cart_item_id):
    if request.method == "POST":
        user_id = request.session.get("user_id")
        # We assume that if the user is logged in, the session key "user_id" is set.
        user = get_object_or_404(UserProfile, id=user_id)
        cart_item = get_object_or_404(CartItem, id=cart_item_id, cart__user=user)
        cart_item.delete()
        return JsonResponse({"message": "Item removed from cart!"})
    return JsonResponse({"error": "Invalid request"}, status=400)






# 📌 View to display the home page (home.html) with all products
def home(request):
    # Fetch all products from the database
    products = Product.objects.all()  # You can apply filters if needed, e.g., featured products
    return render(request, 'home.html', {'products': products})

# 📌 View to display product details
def product_detail(request, product_id):
    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        return redirect('home')  # Redirect to home if product is not found
    
    return render(request, 'product_detail.html', {'product': product})

from django.http import JsonResponse
from .models import Cart, CartItem
from users_app.models import UserProfile

def cart_count_view(request):
    user_id = request.session.get("user_id")
    
    if user_id:
        user = UserProfile.objects.filter(id=user_id).first()
        cart = Cart.objects.filter(user=user).first()
        cart_count = CartItem.objects.filter(cart=cart).count() if cart else 0
    else:
        cart = request.session.get("cart", {})
        cart_count = len(cart)  # Count guest cart items

    return JsonResponse({"cart_count": cart_count})
def add_ai_cart(request):
    if request.method == "POST":
        size = request.POST.get("size", "M")
        quantity = int(request.POST.get("quantity", 1))
        custom_name = request.POST.get("custom_name")
        custom_image_url = request.POST.get("custom_image_url")

        if not custom_name or not custom_image_url:
            return JsonResponse({"status": "error", "message": "Missing AI design data"}, status=400)

        user_id = request.session.get("user_id")
        if user_id:
            user = get_object_or_404(UserProfile, id=user_id)
            cart, _ = Cart.objects.get_or_create(user=user)
            
            cart_item = CartItem.objects.create(
                cart=cart,
                quantity=quantity,
                size=size,
                custom_name=custom_name,
                custom_image_url=custom_image_url
            )
            return redirect("cart:cart_page")

        else:
            # Guest user session cart
            cart = request.session.get("cart", {})
            key = f"ai_{custom_name}_{size}"
            cart[key] = {
                "quantity": quantity,
                "size": size,
                "custom_name": custom_name,
                "custom_image_url": custom_image_url
            }
            request.session["cart"] = cart
            request.session.modified = True
            return redirect("cart_page")

    return JsonResponse({"status": "error", "message": "Invalid request"}, status=400)

from django.template import engines

def test_filter(request):
    print("LOADED TAG LIBS:", engines['django'].engine.template_libraries)
    return render(request, 'test.html')
import json
import logging
import pycountry
import mysql.connector
import razorpay
import os

from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from .models import Cart, Order
from users_app.models import UserProfile  # you’ll need this to look up the user

logger = logging.getLogger(__name__)

# Initialize Razorpay client
razorpay_client = razorpay.Client(auth=(
    os.getenv("RAZORPAY_KEY_ID"),
    os.getenv("RAZORPAY_KEY_SECRET")
))

def payment_view(request):
    """
    Handles POST from cart.html with cart_data → stores in session, renders payment.html
    Any other method redirects to cart page
    """
    if request.method == 'POST':
        # ─────────── your existing JSON decode & session stash ───────────
        raw = request.POST.get('cart_data', '[]')
        try:
            cart_items = json.loads(raw)
        except json.JSONDecodeError:
            cart_items = []
        request.session['payment_cart_data'] = cart_items
        request.session.modified = True

        # ─────────── fetch the actual Cart for this user ───────────
        user_id = request.session.get("user_id")
        if not user_id:
            return redirect("login")
        user = get_object_or_404(UserProfile, id=user_id)
        cart = Cart.objects.filter(user=user).first()

        # ─────────── your totals ───────────
        subtotal = sum(i['price'] * i['quantity'] for i in cart_items)
        shipping = 50
        total = subtotal + shipping

        # ─────────── country data ───────────
        countries = sorted([c.name for c in pycountry.countries])
        countries_with_states = {
            c.name: [s.name for s in pycountry.subdivisions.get(country_code=c.alpha_2)]
            for c in pycountry.countries
        }

        # ─────────── render with the real cart instance ───────────
        return render(request, "payment.html", {
            "cart": cart,                   # ← now this is your Cart instance
            "cart_items": cart_items,
            "subtotal": subtotal,
            "shipping_price": shipping,
            "total_price": total,
            "countries": countries,
            "countries_with_states": countries_with_states,
            "razorpay_key_id": settings.RAZORPAY_KEY_ID,
        })

    return redirect("cart:cart_page")

from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.shortcuts import redirect
from cart.models import Cart

from users_app.models import UserProfile  # Custom user model
import razorpay
import logging

logger = logging.getLogger(__name__)

# Razorpay client (replace with your keys)
import os
razorpay_client = razorpay.Client(auth=(
    os.getenv("RAZORPAY_KEY_ID"),
    os.getenv("RAZORPAY_KEY_SECRET")
))

# Custom login_required decorator
def custom_login_required(view_func):
    def _wrapped_view(request, *args, **kwargs):
        if "user_id" not in request.session:
            return redirect(f'/login/?next={request.path}')
        return view_func(request, *args, **kwargs)
    return _wrapped_view

from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

import razorpay
import logging

logger = logging.getLogger(__name__)

razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

@custom_login_required
@require_http_methods(["POST", "OPTIONS"])
def create_order(request):
    if request.method == "OPTIONS":
        return JsonResponse({}, status=200)

    try:
        # Get user_id from session
        user_id = request.session.get("user_id")
        if not user_id:
            return JsonResponse({"error": "User not authenticated"}, status=401)

        try:
            user = UserProfile.objects.get(id=user_id)
        except UserProfile.DoesNotExist:
            return JsonResponse({"error": "User not found"}, status=404)

        # Parse the request body to get the cart_id
        try:
            data = json.loads(request.body)
            cart_id = data.get("cart_id")
            if not isinstance(cart_id, int):
                return JsonResponse({"error": "Invalid cart_id"}, status=400)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON data"}, status=400)

        # Fetch cart items for the user
        cart_qs = Cart.objects.filter(user=user).first()  # Get the first cart for the user
        if not cart_qs:
            return JsonResponse({"error": "Cart is empty"}, status=400)

        # Calculate the total price by iterating through the cart items
        cart_items = [
            {"price": item.product.price_inr if item.product else 600, "quantity": item.quantity}
            for item in cart_qs.items.all()
        ]
        total = sum(item['price'] * item['quantity'] for item in cart_items)

        # Check if the total price is greater than zero
        if total <= 0:
            return JsonResponse({"error": "Total must be greater than zero"}, status=400)

        amount_paise = int(total * 100)  # Convert to paise for Razorpay

        # Create Razorpay order
        rz_order = razorpay_client.order.create({
            "amount": amount_paise,
            "currency": "INR",
            "payment_capture": "1"
        })

        # Save the order in the database
        order = Order.objects.create(
            user=user,
            cart_id=cart_id, 
            order_code=rz_order["id"],
            total_price=total,
            shipping_price=0.00,
            first_name="Temp",
            last_name="User",
            country="India",
            state="Maharashtra",
            house_number="N/A",
            street_name="N/A",
            apartment_suite_unit="N/A",
            city="N/A",
            post_code="000000",
            phone="0000000000",
            status="Pending"
        )


        # Return Razorpay order details and API key for frontend
        return JsonResponse({
            "razorpay_order_id": rz_order["id"],
            "razorpay_amount": rz_order["amount"],
            "razorpay_currency": rz_order["currency"],
            "razorpay_key_id": settings.RAZORPAY_KEY_ID  # Razorpay key for frontend
        })

    except Exception as e:
        logger.exception("❌ Order creation failed due to internal error")
        return JsonResponse({"error": "❌ Order creation failed."}, status=500)
# cart/views.py

import json
import logging
import mysql.connector
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import razorpay

from cart.models import Order, Cart, OrderItem

logger = logging.getLogger(__name__)
razorpay_client = razorpay.Client(
    auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
)

@csrf_exempt
@require_http_methods(["POST", "OPTIONS"])
def verify_payment(request):
    """
    AJAX: Verifies Razorpay signature, writes shipping data into Order,
    marks payment success, copies CartItems → OrderItems, and calls stored proc.
    """
    if request.method == "OPTIONS":
        return JsonResponse({}, status=200)

    # 1) Parse payload
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"status": "fail", "message": "Invalid JSON"}, status=400)

    # 2) Verify signature
    try:
        razorpay_client.utility.verify_payment_signature({
            "razorpay_order_id":   data["razorpay_order_id"],
            "razorpay_payment_id": data["razorpay_payment_id"],
            "razorpay_signature":  data["razorpay_signature"],
        })
    except Exception:
        return JsonResponse({"status": "fail", "message": "Signature mismatch."}, status=400)

    # 3) Load the Order
    try:
        order = Order.objects.get(order_code=data["razorpay_order_id"])
    except Order.DoesNotExist:
        return JsonResponse({"status": "fail", "message": "Order not found."}, status=404)

    # 4) Write shipping info
    shipping_fields = (
        "first_name","last_name","country","state","region",
        "house_number","street_name","apartment_suite_unit",
        "town","city","post_code","phone","order_notes"
    )
    for f in shipping_fields:
        setattr(order, f, data.get(f, ""))
    order.payment_status = "Success"
    order.status = "Paid"
    order.save()

    # 5) Copy CartItems → OrderItems
    try:
        cart = Cart.objects.get(id=order.cart_id, user=order.user)
    except Cart.DoesNotExist:
        cart = None
        logger.warning("Cart %s not found for user %s", order.cart_id, order.user)

    if cart:
        for ci in cart.items.all():
            OrderItem.objects.create(
                order=order,
                product=ci.product,
                quantity=ci.quantity,
                product_price=(ci.product.price_inr if ci.product else 0),
                size=ci.size
            )
        cart.items.all().delete()

    # 6) (Optional) Call your stored procedure
    try:
        conn = mysql.connector.connect(
            host=settings.DATABASES['default']['HOST'],
            user=settings.DATABASES['default']['USER'],
            password=settings.DATABASES['default']['PASSWORD'],
            database=settings.DATABASES['default']['NAME'],
        )
        cursor = conn.cursor()
        cursor.callproc('CreateOrder', [
            order.order_id,
            order.first_name,
            order.last_name,
            order.country,
            order.state,
            order.region,
            order.house_number,
            order.street_name,
            order.apartment_suite_unit,
            order.town,
            order.city,
            order.post_code,
            order.phone,
            order.order_notes or '',
            order.total_price,
            50,  # static shipping cost
        ])
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        logger.error("SP CreateOrder failed", exc_info=e)

    return JsonResponse({"status": "success", "message": "Payment stored!"})


def payment_success_view(request):
    """
    Renders 'Thank You' success page after payment
    """
    return render(request, "payment_success.html")

from django.http import JsonResponse
from .models import CartItem
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def delete_cart_item(request, item_id):
    if request.method == 'POST':
        try:
            item = CartItem.objects.get(id=item_id)
            item.delete()
            return JsonResponse({'success': True})
        except CartItem.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Item not found'})

from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from .models import OrderAddress
from users_app.models import UserProfile

@csrf_exempt
def save_address_before_payment(request):
    if request.method == 'POST':
        user_id = request.session.get("user_id")
        if user_id:
            user = get_object_or_404(UserProfile, id=user_id)
        else:
            return JsonResponse({'status': 'fail', 'message': 'User not logged in'}, status=401)

        address = OrderAddress.objects.create(
            user=user,
            first_name=request.POST['first_name'],
            last_name=request.POST['last_name'],
            country=request.POST['country'],
            state=request.POST['state'],
            house_number=request.POST['house_number'],
            street_name=request.POST['street_name'],
            city=request.POST['city'],
            post_code=request.POST['post_code'],
            phone=request.POST['phone'],
            order_notes=request.POST.get('order_notes', '')
        )
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'fail'})

import json
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.shortcuts import get_object_or_404
from users_app.models import UserProfile
from .models import CartItem

@require_POST
def update_cart_item(request, item_id):
    user_id = request.session.get("user_id")
    if not user_id:
        return JsonResponse({"error": "Not authenticated"}, status=401)

    data = json.loads(request.body)
    new_qty = data.get("quantity")
    if not isinstance(new_qty, int) or new_qty < 1:
        return JsonResponse({"error": "Invalid quantity"}, status=400)

    user = get_object_or_404(UserProfile, id=user_id)
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=user)
    cart_item.quantity = new_qty
    cart_item.save()

    # Recalculate totals
    line_total = cart_item.total_price()
    cart_total = cart_item.cart.total_price()

    return JsonResponse({
        "quantity": new_qty,
        "line_total": line_total,
        "cart_total": cart_total
    })
