from .models import Cart, CartItem
from users_app.models import UserProfile

def cart_count_processor(request):
    cart_count = 0
    user_id = request.session.get('user_id')

    if user_id:
        user = UserProfile.objects.filter(id=user_id).first()
        cart = Cart.objects.filter(user=user).first()
        cart_count = CartItem.objects.filter(cart=cart).count() if cart else 0
    else:
        cart = request.session.get("cart", {})
        cart_count = len(cart)  # Guest cart count

    return {'cart_count': cart_count}
from cart.models import Cart

def cart_count_context(request):
    """Returns the total number of items in the cart."""
    cart = Cart.objects.filter(user=request.user).first() if request.user.is_authenticated else None
    return {'cart_count': cart.items.count() if cart else 0}
