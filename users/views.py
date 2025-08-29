from django.shortcuts import redirect, render
from businesses.forms import ProfileForm
from django.contrib.auth import authenticate, login, logout
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from .forms import LoginForm, SignupForm
from django.contrib.auth import get_user_model
User = get_user_model()

def signup_view(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            
            # Authenticate first to set the backend, then login
            authenticated_user = authenticate(
                request,
                username=user.username,
                password=form.cleaned_data['password']
            )
            login(request, authenticated_user)
            return redirect('businesses:dashboard')
    else:
        form = SignupForm()
    
    return render(request, 'businesses/signup.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username, password=password)
            login(request, user)
            return redirect('businesses:dashboard')
    else:
        form = LoginForm()
    
    return render(request, 'businesses/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('businesses:landing_page')


# Settings page
@login_required
def settings_view(request):
    profile_form = ProfileForm(instance=request.user)
    password_form = PasswordChangeForm(request.user)
    
    # Check if user has a password (for Google OAuth users)
    has_password = request.user.has_usable_password()
    
    if request.method == 'POST':
        action = request.GET.get('action')
        
        if action == 'profile':
            profile_form = ProfileForm(request.POST, instance=request.user)
            if profile_form.is_valid():
                profile_form.save()
                messages.success(request, 'Profile updated successfully!')
                return redirect('businesses:settings')
            else:
                messages.error(request, 'Please correct the errors below.')
        
        elif action == 'password':
            if not has_password:
                messages.error(request, 'Cannot change password for Google account. Please use Google to manage your password.')
            else:
                password_form = PasswordChangeForm(request.user, request.POST)
                if password_form.is_valid():
                    user = password_form.save()
                    update_session_auth_hash(request, user)
                    messages.success(request, 'Password changed successfully!')
                    return redirect('businesses:settings')
                else:
                    messages.error(request, 'Please correct the password errors below.')
        
        elif action == 'delete':
            if request.POST.get('confirm') == 'DELETE':
                request.user.delete()
                messages.success(request, 'Account deleted successfully!')
                return redirect('businesses:landing_page')
            else:
                messages.error(request, 'Account deletion cancelled.')
    
    context = {
        'user': request.user,
        'profile_form': profile_form,
        'password_form': password_form,
        'has_password': has_password,
    }
    return render(request, 'businesses/settings.html', context)