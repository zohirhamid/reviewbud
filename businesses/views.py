from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from businesses.forms import SignupForm
from businesses.models import Business, ReviewLink, CustomerReview
from django.contrib.auth import authenticate, login, logout
from .forms import LoginForm, SignupForm, BusinessForm, CustomerReviewForm, ProfileForm
from django.conf import settings
from django.contrib import messages
import qrcode
from io import BytesIO
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.models import User
from .forms import LoginForm, SignupForm, BusinessForm, CustomerReviewForm, ProfileForm

def landing_page(request):
    if request.user.is_authenticated:
        return redirect('businesses:dashboard')
    else:
        return render(request, 'landing_page.html')

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

@login_required
def dashboard(request):
    if request.user.is_authenticated:
        businesses = Business.objects.filter(owner=request.user)

        for business in businesses:
            business.get_review_link()
    else:
        businesses = []
    
    context = { # context is a dictionary of data u want to pass to the HTML template
        'businesses': businesses,
    }
    
    return render(request, 'businesses/dashboard.html', context)

@login_required
def create_business(request):
    if request.method == 'POST':
        form = BusinessForm(request.POST)
        if form.is_valid():
            business = form.save(commit=False)
            business.owner = request.user
            business.save()
            return redirect('businesses:dashboard')
        else:
            print(form.errors)  # optional: helpful for debugging
    else:
        '''
        Diplay the add business form for the first time
        before the user fills it out to submit it.
        '''
        # Create an instance of BusinessForm (an empty one to be filled by client)
        # form = BusinessForm()
        form = BusinessForm(initial={
            'name': '',
            'address': '',
            'google_review_url': '',
        })

    return render(request, 'businesses/create_business.html', {
        'form': form,
        'GOOGLE_PLACES_API_KEY': settings.GOOGLE_PLACES_API_KEY,  # or pass from settings
    })


def update_business(request, id):
    business = get_object_or_404(Business, id=id)
    if request.method == 'POST':
        form = BusinessForm(request.POST, instance=business)
        if form.is_valid():
            form.save()
            return redirect("businesses:dashboard")
    else:
        form = BusinessForm(instance=business)
    
    context = {
        "form": form,
        "business": business
    }
    
    return render(request, 'businesses/update_business.html', context)
    
@login_required
def delete_business(request, id):
    if request.method == 'POST':
        business = get_object_or_404(Business, id=id)
        business.delete()
        return redirect('businesses:dashboard')
    # If not POST, redirect back to dashboard or detail page
    return redirect('businesses:dashboard')

@login_required  
def business_detail(request, id):
    business = get_object_or_404(Business, id=id, owner=request.user)
    form = BusinessForm(instance=business)
    
    context = {
        'business': business,
        'form': form,
    }
    
    return render(request, 'businesses/business_detail.html', context)

@login_required
def create_qr_code_page(request, token):
    # Retrieve the ReviewLink using token (or return 404 if not found)
    review_link = get_object_or_404(ReviewLink, token=token)
    
    # Retrieve the associated Business
    business = review_link.business
    
    # Ensure the user owns this business (permission check)
    if business.owner != request.user:
        return render(request, '403.html')  # show 403 Forbidden page
    
    context = {
        'business': business,
        'review_link': review_link,
    }
    
    return render(request, 'businesses/create_qrcode.html', context)

def qr_code(request, token):
    # Get the review link
    review_link = get_object_or_404(ReviewLink, token=token)
    
    # Create full URL for QR code
    review_url = request.build_absolute_uri(review_link.get_absolute_url())
    
    # Generate QR code
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(review_url)
    qr.make(fit=True)
    
    # Create image
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Return as HTTP response
    buffer = BytesIO()
    img.save(buffer, 'PNG')
    buffer.seek(0)
    
    return HttpResponse(buffer.getvalue(), content_type="image/png")

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
        'has_password': has_password,  # Pass this to template
    }
    return render(request, 'businesses/settings.html', context)