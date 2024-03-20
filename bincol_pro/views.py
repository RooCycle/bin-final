from django.shortcuts import render
from django.contrib.auth.models import User

# views.py
from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth import authenticate, login
from .models import UserProfile
from .tokens import account_activation_token
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth import authenticate, login as auth_login

def signup(request):
    if request.method == 'POST':
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        email = request.POST['email']
        username = request.POST['username']
        password = request.POST['password']
        
        user = User.objects.create_user(first_name=first_name, last_name=last_name, email=email, username=username, password=password)
        user.is_active = False
        user.save()

        # Send activation email
        current_site = get_current_site(request)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = account_activation_token.make_token(user)
        activation_link = f"http://{current_site.domain}/activate/{uid}/{token}"  # Replace with your actual domain
        send_mail(
            'Activate your account',
            f'Click the link to activate your account: {activation_link}',
            'accounts@bincol.com',  # Replace with your email address
            [user.email],
            fail_silently=False,
        )
        return render(request, 'activation_sent.html')

    return render(request, 'signup.html')

def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        return render(request, 'login.html', {'message': 'Registration successful. Please log in.'})
    else:
        return render(request, 'activation_invalid.html')

"""def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None and user.is_active:
            auth_login(request, user)
            return redirect('home')
        else:
            return render(request, 'login.html', {'error_message': 'Invalid login'})
    return render(request, 'login.html')"""
def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None and user.is_active:
            auth_login(request, user)
            return redirect('profile_create')
        else:
            error_message = 'Invalid username or password'
            return render(request, 'login.html', {'error_message': error_message})
    return render(request, 'login.html')

def home(request):
    return render(request, 'home.html')

def profile_create(request):
    # We will add logic for creating profile here
    return render(request, 'profile_create.html')

"""def profile_create(request, username): 
    return render(request, 'profile_create.html', {'username': username})"""
