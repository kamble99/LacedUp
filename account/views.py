from email.message import EmailMessage
from django.contrib import messages,auth
from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.contrib.auth.hashers import make_password,check_password
from django.contrib.auth import login as auth_login
from django.contrib.auth.decorators import login_required
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.core.mail import EmailMessage
from django.contrib.auth.tokens import default_token_generator
from account.models import Account


def register(request):
    if request.method == 'POST':
        first_name = request.POST['fname']
        last_name = request.POST['lname']
        email = request.POST['email']
        password = request.POST['password']
        epass = make_password(password)
        phoneno = request.POST['phoneno']
        username = email.split('@')[0]

        # Check if email already exists
        if Account.objects.filter(email=email).exists():
            messages.error(request, "Email already exists.")
            return redirect('register')  # or just render the same page with an error message

        # Create the account
        data = Account.objects.create(
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=epass,
            phone_number=phoneno,
            username=username
        )
        data.save()
        messages.success(request, "Account created successfully!")
        return redirect('login')  # redirect to login or home

    return render(request, 'register.html')

def login(request):
    if request.method == 'POST':
        email = request.POST['lemail']
        password = request.POST['lpassword']

        try:
            user = Account.objects.get(email=email)
            if check_password(password, user.password):
                auth_login(request, user)  # Log the user in
                messages.success(request, 'You are logged in!')
                return redirect('home')
            else:
                messages.error(request, 'Invalid password, please try again.')
                return redirect('login')
        except Account.DoesNotExist:
            messages.error(request, 'Email not found, please register.')
            return redirect('login')

    return render(request, 'login.html')

@login_required(login_url='login')
def logout(request):
    auth.logout(request)
    messages.success(request,'you are logged out.')
    return redirect('home')

@login_required(login_url='login')
def dashboard(request):
    return render(request,'dashboard.html')

 
