import logging
from django.http import JsonResponse
from django.views import View
from django.views.generic import TemplateView
from django.shortcuts import get_object_or_404

from businesses.ai_service import generate_review_with_ai
from businesses.models import ReviewLink, CustomerReview
from businesses.forms import CustomerReviewForm

logger = logging.getLogger(__name__)

class ReviewFormView(TemplateView):
    template_name = 'reviews/review_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        review_link = get_object_or_404(ReviewLink, token=self.kwargs['token'])
        review_link.increment_clicks()
        
        context.update({
            'business': review_link.business,
            'review_link': review_link,
            'form': CustomerReviewForm(),
        })
        return context

class SubmitReviewView(View):
    """
    Collect form input, send it to ai_service, get the generated review back.
    """

    def post(self, request, token):
        try:
            review_link = get_object_or_404(ReviewLink, token=token)
            business = review_link.business

            ratings = {
                'food': int(request.POST.get('food_rating', 3)),
                'service': int(request.POST.get('service_rating', 3)),
                'atmosphere': int(request.POST.get('atmosphere_rating', 3)),
                'recommend': int(request.POST.get('recommend_rating', 3)),
            }
            feedback = request.POST.get('feedback', '').strip()
            tags = request.POST.get('tags', '').strip()

            ai_review, generation_method, avg_rating = generate_review_with_ai(
                ratings=ratings,
                feedback=feedback,
                business_name=business.name,
                tags=tags,
            )

            CustomerReview.objects.create(
                business=business,
                review_link=review_link,
                rating=avg_rating,
                feedback=feedback,
                ai_review=ai_review,
                ip_address=request.META.get('REMOTE_ADDR'),
            )

            return JsonResponse({
                'success': True,
                'ai_review': ai_review,
                'generation_method': generation_method,
                'google_url': business.google_review_url,
            })

        except Exception as e:
            logger.error(f"Error in submit_review: {e}")
            return JsonResponse({'success': False, 'error': str(e)})

    def http_method_not_allowed(self, request, *args, **kwargs):
        return JsonResponse({'success': False, 'error': 'Invalid request method'})