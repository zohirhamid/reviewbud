from django.http import JsonResponse
from businesses.ai_service import generate_review_with_ai
from businesses.models import ReviewLink, CustomerReview
from businesses.forms import CustomerReviewForm
from django.shortcuts import render, get_object_or_404

def review_form(request, token):
    """
    Display the review form for a specific business using the review link token.
    token: Unique token identifying the review link

    Rendered review form template or 404 page if token not found
    """
    # Get review link
    review_link = get_object_or_404(ReviewLink, token=token)
    
    # find the associated business
    business = review_link.business
    review_link.increment_clicks()
    form = CustomerReviewForm()
    
    context = {
        'business': business,
        'review_link': review_link,
        'form': form,
    }
    
    return render(request, 'reviews/review_form.html', context)


def submit_review(request, token):
    if request.method == 'POST':
        try:
            # Find the business from the token
            review_link = get_object_or_404(ReviewLink, token=token)
            business = review_link.business
            
            # Get ratings from form
            food_rating = int(request.POST.get('food_rating', 3))
            service_rating = int(request.POST.get('service_rating', 3))
            atmosphere_rating = int(request.POST.get('atmosphere_rating', 3))
            recommend_rating = int(request.POST.get('recommend_rating', 3))
            
            # Calculate average rating
            avg_rating = round((food_rating + service_rating + atmosphere_rating + recommend_rating) / 4)
            
            feedback = request.POST.get('feedback', '')
            tags = request.POST.get('tags', '')
            
            # Create comprehensive feedback for AI
            detailed_feedback = create_detailed_feedback(
                food_rating, service_rating, atmosphere_rating, 
                recommend_rating, feedback, tags
            )
            
            # Save customer review to database
            review = CustomerReview.objects.create(
                business=business,
                review_link=review_link,
                rating=avg_rating,
                feedback=detailed_feedback,
                ip_address=request.META.get('REMOTE_ADDR')
            )

            # Generate AI review
            try:
                ai_review, generation_method = generate_review_with_ai(
                    rating=avg_rating, 
                    feedback=detailed_feedback, 
                    business_name=business.name, 
                    tags=tags
                )
                review.ai_review = ai_review
                review.save()
                
                return JsonResponse({
                    'success': True,
                    'ai_review': ai_review,
                    'generation_method': generation_method,
                    'google_url': business.google_review_url
                })
                
            except Exception as e:
                # Fallback to template method
                review.generate_ai_review()
                fallback_review = review.ai_review
                
                return JsonResponse({
                    'success': True,
                    'ai_review': fallback_review,
                    'generation_method': 'Fallback Template',
                    'google_url': business.google_review_url
                })

        except ReviewLink.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Review link not found'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    return JsonResponse({
        'success': False,
        'error': 'Invalid request method'
    })

def create_detailed_feedback(food_rating, service_rating, atmosphere_rating, recommend_rating, feedback, tags):
    """Create detailed feedback text"""
    feedback_parts = []
    
    # Add original feedback first
    if feedback.strip():
        feedback_parts.append(feedback.strip())
    
    # Food rating feedback
    if food_rating >= 4:
        feedback_parts.append("The food quality was excellent")
    elif food_rating == 3:
        feedback_parts.append("The food was decent")
    elif food_rating <= 2:
        feedback_parts.append("The food quality could be improved")
    
    # Service rating feedback
    if service_rating >= 4:
        feedback_parts.append("The service was fast and friendly")
    elif service_rating == 3:
        feedback_parts.append("The service was adequate")
    elif service_rating <= 2:
        feedback_parts.append("The service was slow")
    
    # Atmosphere rating feedback
    if atmosphere_rating >= 4:
        feedback_parts.append("I loved the atmosphere")
    elif atmosphere_rating == 3:
        feedback_parts.append("The atmosphere was nice")
    elif atmosphere_rating <= 2:
        feedback_parts.append("The atmosphere was okay")
    
    # Recommendation feedback
    if recommend_rating >= 4:
        feedback_parts.append("I would definitely recommend this place")
    elif recommend_rating == 3:
        feedback_parts.append("I might recommend this place")
    elif recommend_rating <= 2:
        feedback_parts.append("I'm not sure I would recommend this place")
    
    # Add tags (optional)
    if tags.strip():
        feedback_parts.append(f"What stood out: {tags}")
    
    return ". ".join(feedback_parts) + "."