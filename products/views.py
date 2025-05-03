from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .db_operations import ProductCatalogClass
from .models import Product
from .forms import ProductForm
from django.http import HttpResponse
from cart.models import CartItem
from cart.models import Cart, CartItem  

from django.contrib.auth.decorators import login_required, user_passes_test

# ✅ Add Product View
def add_product(request):
    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.save()

            # Call stored procedure (optional)
            result_msg = ProductCatalogClass.addProductRecord(
                product.category,
                product.name.strip(),
                product.description.strip(),
                product.price_inr,
                product.price_usd,
                product.image1.url if product.image1 else None,
                product.image2.url if product.image2 else None,
                product.image3.url if product.image3 else None
            )

            messages.success(request, result_msg or "Product added successfully!")
            return redirect("home")  # Redirect to home after adding product
        else:
            messages.error(request, "There was an error in the form. Please correct it below.")
            print(form.errors)  # DEBUG: Check form errors in terminal/logs
    else:
        form = ProductForm()

    return render(request, "add_product.html", {"form": form})


# ✅ Home Page - Show all products including featured section
from django.shortcuts import render
from .models import Product

def home(request):
    # Fetch all products for the "Featured Roars" section
    all_products = Product.objects.all().order_by("-id")

    # Fetch products based on category
    tshirts = Product.objects.filter(category="T-Shirts").order_by("-id")
    premium = Product.objects.filter(category="Premium").order_by("-id")
    accessories = Product.objects.filter(category="Accessories").order_by("-id")

    return render(request, "home.html", {
        "all_products": all_products,  # For Featured Roars
        "tshirts": tshirts,
        "premium": premium,
        "accessories": accessories
    })




# ✅ Category-wise Product Views
def premium_products(request):
    products = Product.objects.filter(category="Premium").order_by("-id")
    return render(request, "premium.html", {"products": products})

def accessories_products(request):
    products = Product.objects.filter(category="Accessories").order_by("-id")
    return render(request, "accessories.html", {"products": products})

def tshirts_products(request):
    products = Product.objects.filter(category="T-Shirts").order_by("-id")
    return render(request, "tshirts.html", {"products": products})

# ✅ Category View (Dynamic)
def category_view(request, category_name):
    products = Product.objects.filter(category=category_name).order_by("-id")  
    return render(request, "category.html", {"products": products, "category": category_name})

# ✅ Add to Cart (Coming Soon)
# def add_to_cart(request, product_id):
#     return HttpResponse("Cart feature coming soon!")

# ✅ Check if User is Superuser
def is_superuser(user):
    return user.is_authenticated and user.is_superuser


def delete_product(request, product_id):
    if not request.session.get("is_superuser", False):  # ✅ Check session instead of request.user
        return HttpResponse("Permission Denied", status=403)

    product = get_object_or_404(Product, id=product_id)
    product.delete()
    return redirect("home")

def edit_product(request, product_id):
    product = Product.objects.get(id=product_id)

    if request.method == 'POST':
        # Update text fields
        product.category = request.POST.get('category')
        product.name = request.POST.get('name')
        product.description = request.POST.get('description')
        product.price_inr = request.POST.get('price_inr')
        product.price_usd = request.POST.get('price_usd')

        # ✅ Only update images if a new file is uploaded
        if 'image1' in request.FILES:
            product.image1 = request.FILES['image1']
        if 'image2' in request.FILES:
            product.image2 = request.FILES['image2']
        if 'image3' in request.FILES:
            product.image3 = request.FILES['image3']

        product.save()
        messages.success(request, "Product updated successfully!")
        return redirect('home')

    return render(request, 'edit_product.html', {'product': product})


def tshirts_view(request):
    """ Show only T-Shirts category products. """
    products = Product.objects.filter(category="T-Shirts").order_by("-id")
    return render(request, "tshirts.html", {"products": products})

def premium_collection(request):
    # Filter premium products
    premium_products = Product.objects.filter(is_premium=True)
    
    # Optional: Paginate the products for better UI experience (if you have many)
    from django.core.paginator import Paginator
    paginator = Paginator(premium_products, 9)  # 9 products per page
    page_number = request.GET.get('page')  # Get page number from URL query parameter
    page_obj = paginator.get_page(page_number)

    # Pass the products and page object to the template
    return render(request, "premium.html", {
        "products": page_obj
    })
from django.shortcuts import render, get_object_or_404, redirect
from products.models import Product
from cart.models import CartItem
from users_app.models import UserProfile

from django.shortcuts import render, get_object_or_404, redirect
from products.models import Product
from cart.models import CartItem
from users_app.models import UserProfile

def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    similar_products = Product.objects.filter(category=product.category).exclude(id=product.id)[:4]
    
    cart_count = 0
    user_id = request.session.get("user_id")
    if user_id:
        user = get_object_or_404(UserProfile, id=user_id)
        cart = Cart.objects.filter(user=user).first()
        if cart:
            cart_count = CartItem.objects.filter(cart=cart).count()

    return render(request, "product_detail.html", {
        "product": product,
        "similar_products": similar_products,
        "cart_count": cart_count,
    })

def accessories_view(request):
    """ Show only Accessories category products. """
    products = Product.objects.filter(category="Accessories").order_by("-id")
    return render(request, "accessories.html", {"products": products})
import os
import json
import base64
import io
from dotenv import load_dotenv
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

# 1) Load your HF token from .env
load_dotenv()
HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY")

# 2) Import and initialize InferenceClient
from huggingface_hub import InferenceClient
client = InferenceClient(
    provider="fal-ai",
    api_key=HUGGINGFACE_API_KEY,
)

def ai_design(request):
    return render(request, 'ai_design.html')

def generate_design(prompt: str) -> bytes | None:
    """
    Uses the FAL provider + FLUX.1-dev model to generate a PIL.Image,
    then encodes it to PNG bytes.
    """
    try:
        # This returns a PIL.Image object
        img = client.text_to_image(prompt, model="black-forest-labs/FLUX.1-dev")
    except Exception as e:
        print("❌ InferenceClient error:", e)
        return None

    # Convert PIL.Image → PNG bytes
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()

@csrf_exempt
def generate_design_view(request):
    """
    AJAX endpoint: POST {"prompt":"..."} → JSON { success, image:data_url }
    """
    if request.method != "POST":
        return JsonResponse(
            {"success": False, "error": "Only POST allowed."},
            status=405
        )

    try:
        data = json.loads(request.body)
        prompt = (data.get("prompt") or "").strip()
        if not prompt:
            return JsonResponse(
                {"success": False, "error": "No prompt provided."},
                status=400
            )

        png_bytes = generate_design(prompt)
        if png_bytes is None:
            return JsonResponse(
                {"success": False, "error": "Image generation failed."},
                status=500
            )

        b64 = base64.b64encode(png_bytes).decode("utf-8")
        return JsonResponse(
            {"success": True, "image": f"data:image/png;base64,{b64}"}
        )

    except json.JSONDecodeError:
        return JsonResponse(
            {"success": False, "error": "Invalid JSON."},
            status=400
        )
    except Exception as e:
        return JsonResponse(
            {"success": False, "error": f"Server error: {e}"},
            status=500
        )

# Add Generated Design to Cart
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

            CartItem.objects.create(
                cart=cart,
                quantity=quantity,
                size=size,
                custom_name=custom_name,
                custom_image_url=custom_image_url
            )
            return redirect("cart:cart_page")
        else:
            # Guest session cart
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
            return redirect("cart:cart_page")

    return JsonResponse({"status": "error", "message": "Invalid request"}, status=400)

from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.http import require_POST
from cart .models import Order
import json
from django.shortcuts import render
from django.http import JsonResponse, HttpResponseForbidden


def admin_orders_view(request):
    # only allow your own “superuser” flag
    if not request.session.get('is_superuser', False):
        return HttpResponseForbidden("Permission Denied")

    # eager‐load user and items
    orders = (
        Order.objects
             .select_related('user')
             .prefetch_related('items__product')
             .order_by('-created_at')
    )
    return render(request, 'admin_orders.html', {'orders': orders})

def mark_order_status(request, order_id):
    if not request.session.get('is_superuser', False):
        return JsonResponse({'error': 'Permission Denied'}, status=403)

    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid method'}, status=405)

    try:
        data = json.loads(request.body)
        new_status = data.get('new_status')
        # validate against your Order.status choices
        valid = dict(Order._meta.get_field('status').choices)
        if new_status not in valid:
            return JsonResponse({'error': 'Invalid status'}, status=400)

        order = Order.objects.get(order_id=order_id)
        order.status = new_status
        order.save()
        return JsonResponse({'success': True, 'status': order.status})

    except Order.DoesNotExist:
        return JsonResponse({'error': 'Order not found'}, status=404)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
