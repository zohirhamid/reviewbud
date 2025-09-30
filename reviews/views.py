from venv import logger
from django.http import JsonResponse
from businesses.ai_service import generate_review_with_ai, generate_fallback_review
from businesses.models import ReviewLink, CustomerReview
from businesses.forms import CustomerReviewForm
from django.shortcuts import render, get_object_or_404

def review_form(request, token):
    review_link = get_object_or_404(ReviewLink, token=token)
    review_link.increment_clicks()
    
    context = {
        'business': review_link.business,
        'review_link': review_link,
        'form': CustomerReviewForm(),
    }
    
    return render(request, 'reviews/review_form.html', context)


def submit_review(request, token):
    '''
    Collect form input, send it to ai_service, get the generated review back
    '''
    if request.method != 'POST':  # only allow POST requests
        return JsonResponse({'success': False, 'error': 'Invalid request method'})

    try:
        review_link = get_object_or_404(ReviewLink, token=token)
        business = review_link.business

        # Collect ratings (form input)
        ratings = {
            'food': int(request.POST.get('food_rating', 3)),
            'service': int(request.POST.get('service_rating', 3)),
            'atmosphere': int(request.POST.get('atmosphere_rating', 3)),
            'recommend': int(request.POST.get('recommend_rating', 3)),
        }
        feedback = request.POST.get('feedback', '').strip()
        tags = request.POST.get('tags', '').strip()

        # Generate AI review API/Fallback
        ai_review, generation_method, avg_rating = generate_review_with_ai(
            ratings=ratings,
            feedback=feedback,
            business_name=business.name,
            tags=tags,
        )

        # Save review
        CustomerReview.objects.create(
            business=business,
            review_link=review_link,
            rating=avg_rating,
            feedback=feedback,
            ai_review=ai_review,
            ip_address=request.META.get('REMOTE_ADDR')
        )

        return JsonResponse({
            'success': True,
            'ai_review': ai_review,
            'generation_method': generation_method,
            'google_url': business.google_review_url
        })
    

    except Exception as e:
        logger.error(f"Error in submit_review: {e}")
        return JsonResponse({'success': False, 'error': str(e)})