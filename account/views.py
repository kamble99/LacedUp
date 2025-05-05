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
import requests
from account.models import Account
from django.utils.http import urlsafe_base64_decode


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
                request.session['uname'] = user.first_name
                url=request.META.get('HTTP_REFERER')
                try:
                    query=requests.utils.urlparse(url).query
                    params=dict(x.split('=')for x in query.split('&'))
                    if 'next' in params:
                        nextpage=params['nexy']
                        return redirect(nextpage)
                    return redirect('home')
                except:
                    pass
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

 
def forgot_password(request):
    if request.method == 'POST':
        email = request.POST['email']
        if Account.objects.filter(email=email).exists():
            user = Account.objects.get(email=email)
            
            # Generate token
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            
            # Create reset link
            reset_link = request.build_absolute_uri(f'/account/reset_password_validate/{uid}/{token}/')

            # Send email
            subject = 'Reset your Password'
            message = f'Click the link below to reset your password:\n{reset_link}'
            email_message = EmailMessage(subject, message, to=[email])
            email_message.send()

            messages.success(request, 'Password reset email has been sent to your email address.')
            return redirect('login')
        else:
            messages.error(request, 'Account with this email does not exist.')
            return redirect('forgot_password')
    return render(request, 'forgot_password.html')



def reset_password_validate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        request.session['uid'] = uid
        messages.success(request, 'Please reset your password.')
        return redirect('reset_password')
    else:
        messages.error(request, 'Link is invalid or has expired.')
        return redirect('login')
    
def reset_password(request):
    if request.method == 'POST':
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if password == confirm_password:
            uid = request.session.get('uid')
            user = Account.objects.get(pk=uid)
            user.set_password(password)
            user.save()
            messages.success(request, 'Password reset successful.')
            return redirect('login')
        else:
            messages.error(request, 'Passwords do not match.')
            return redirect('reset_password')
    else:
        return render(request, 'reset_password.html')

@login_required
def userinfo(request):
    profile = request.user  # If Account is your custom user model
    return render(request, 'Profile.html', {'profile': profile})

