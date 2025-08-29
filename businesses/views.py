from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from businesses.models import Business, ReviewLink
from django.conf import settings
import qrcode
from io import BytesIO
from django.contrib.auth.decorators import login_required
from .forms import BusinessForm
from django.contrib.auth import get_user_model
User = get_user_model()


def landing_page(request):
    if request.user.is_authenticated:
        return redirect('businesses:dashboard')
    else:
        return render(request, 'landing_page.html')

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
        'GOOGLE_PLACES_API_KEY': settings.GOOGLE_PLACES_API_KEY, 
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