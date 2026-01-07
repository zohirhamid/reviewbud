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
from django.urls import reverse
from businesses.tasks import update_google_stats_for_one_business
from businesses.services import fetch_google_stats_for_place

def landing_page(request):
    if request.user.is_authenticated:
        return redirect('businesses:dashboard')
    else:
        return render(request, 'landing_page.html')

@login_required # only authenticated users can reach this function
def dashboard(request):
    businesses = Business.objects.filter(owner=request.user)
    
    context = {'businesses': businesses,}
    return render(request, 'businesses/dashboard.html', context)

@login_required
def analytics(request):
    businesses = Business.objects.filter(owner=request.user)
    selected_id = request.GET.get('business')
    selected_business = None

    # Only get a business if an ID was provided
    if selected_id:
        try:
            selected_business = businesses.get(id=int(selected_id))
        except (Business.DoesNotExist, ValueError):
            selected_business = None

    context = {
        'businesses': businesses,
        'selected_business': selected_business,
        'selected_id': selected_id,
    }
    return render(request, 'businesses/analytics.html', context)



@login_required
def support_view(request):
    return render(request, 'businesses/support.html')

@login_required
def create_business(request):
    if request.method == 'POST':
        form = BusinessForm(request.POST)

        # Guard: user typed text but didn’t pick from autocomplete
        if not request.POST.get('place_id'):
            form.add_error(None, "Please select your business from the autocomplete suggestions.")

        if form.is_valid():
            business = form.save(commit=False)
            business.owner = request.user
            business.save()
            business.get_review_link()

            # 1. Sync fetch so the dashboard shows numbers immediately
            rating, count = fetch_google_stats_for_place(business.place_id)
            if (rating is not None) or (count is not None):
                business.rating = rating
                business.total_reviews = count
                business.save(update_fields=["rating", "total_reviews"])
            else:
                # 2. Fallback: queue a background refresh just for this business
                update_google_stats_for_one_business.delay(business.id) # type: ignore

            return redirect('businesses:dashboard')

        # If invalid, fall through and re-render
        return render(
            request,
            'businesses/create_business.html',
            {'GOOGLE_PLACES_API_KEY': settings.GOOGLE_PLACES_API_KEY, 'form': form},
        )

    # GET
    form = BusinessForm()
    return render(
        request,
        'businesses/create_business.html',
        {'GOOGLE_PLACES_API_KEY': settings.GOOGLE_PLACES_API_KEY, 'form': form},
    )


@login_required  
def business_detail(request, id):
    business = get_object_or_404(Business, id=id, owner=request.user)
    if request.method == 'POST':
        form = BusinessForm(request.POST, instance=business)
        if form.is_valid():
            form.save()
            return redirect("businesses:dashboard")
    else:
        form = BusinessForm(instance=business)

    context = {
        'business': business,
        'form': form,
    }
    
    return render(request, 'businesses/business_detail.html', context)
    
@login_required
def delete_business(request, id):
    if request.method == 'POST':
        business = get_object_or_404(Business, id=id)
        business.delete()
        return redirect('businesses:dashboard')
    return redirect('businesses:dashboard')

@login_required
def create_qr_code_page(request, token):
    review_link = get_object_or_404(ReviewLink, token=token)
    business = review_link.business # Retrieve the associated Business

    context = {
        'business': business,
        'review_link': review_link, }
    
    return render(request, 'businesses/create_qrcode.html', context)

def qr_code(request, token):
    review_link = get_object_or_404(ReviewLink, token=token)
    review_url = request.build_absolute_uri(review_link.get_absolute_url())

    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(review_url)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white") 

    buffer = BytesIO()
    img.save(buffer, "PNG")
    buffer.seek(0)

    return HttpResponse(buffer.getvalue(), content_type="image/png")