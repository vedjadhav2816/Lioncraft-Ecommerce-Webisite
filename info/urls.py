from django.urls import path
from . import views  # ✅ Correct way to import views
 # Import home view

urlpatterns = [
    path('', views.faq_view, name='faq'),
    path('careers/', views.careers_view, name='careers'),
    path('press/', views.press_view, name='press'),
    path('Sustainability/', views.sustainability_view, name='Sustainability'),
    path('privacy/', views.privacy_view, name='privacy'),
    path('terms/',views.terms_view,name='terms'),
    path('cookie/',views.cookie_view,name='cookie'),
    path('accessibility/',views.accessibility_view,name='accessibility'),
    path('returns_exchange/',views.returns_exchange,name='returns_exchange'),

]