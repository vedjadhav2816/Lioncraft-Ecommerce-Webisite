from django.shortcuts import render

def faq_view(request):
    return render(request, 'faq.html')


def careers_view(request):
    return render(request,'careers.html')

def press_view(request):
    return render(request,'press.html')


def sustainability_view(request):
    return render(request,'Sustainability.html')

def privacy_view(request):
    return render(request,'Privacy.html')

def terms_view(request):
    return render(request,'terms.html')

def cookie_view(request):
    return render(request,'cookie.html')

def accessibility_view(request):
    return render(request,'Accessibility.html')


def returns_exchange(request):
    return render(request,'returns_exchanges.html')