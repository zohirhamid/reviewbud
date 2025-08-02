from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render
from businesses.ai_service import generate_review_with_ai
from businesses.models import ReviewLink, CustomerReview
from businesses.forms import CustomerReview, CustomerReviewForm


def review_form(request, token):
    try:
        review_link = ReviewLink.objects.get(token=token) # get the reviewlink for X token
        business = review_link.business # get the business of the reviewlink  
        review_link.increment_clicks()
        
        form = CustomerReviewForm()
        
        context = {
            'business': business,
            'review_link': review_link,
            'form': form,
        }
        
        return render(request, 'reviews/review_form.html', context)
    
    except ReviewLink.DoesNotExist:
        return render(request, '404.html')

def submit_review(request, token):
    print(f"submit_review called with method: {request.method}")
    print(f"Token: {token}")
    
    if request.method == 'POST':
        print("Processing POST request")
        try:
            # Step 1. Find the business in question
            ## Step 1.1 Find the reviewlink of the business using token
            review_link = ReviewLink.objects.get(token=token) 
            ## Step 1.2 Find the business using reviewLink (ReviewLink → Business)
            business = review_link.business
            print(f"Found business: {business.name}")
            
            # Get data the from manually
            food_rating = int(request.POST.get('food_rating', 3))
            service_rating = int(request.POST.get('service_rating', 3))
            atmosphere_rating = int(request.POST.get('atmosphere_rating', 3))
            recommend_rating = int(request.POST.get('recommend_rating', 3))
            
            # Calculate average rating
            avg_rating = round((food_rating + service_rating + atmosphere_rating + recommend_rating) / 4)
            
            feedback = request.POST.get('feedback', '')
            customer_name = request.POST.get('customer_name', '')
            tags = request.POST.get('tags', '')
            
            # Create comprehensive feedback for AI
            detailed_feedback = create_detailed_feedback(
                food_rating, service_rating, atmosphere_rating, 
                recommend_rating, feedback, tags
            )
            
            print(f"About to generate AI review with:")
            print(f"- Rating: {avg_rating}")
            print(f"- Feedback: {detailed_feedback}")
            print(f"- Business: {business.name}")
            print(f"- Tags: {tags}")
            
            # Save customer review to database (CustomerReview table)
            review = CustomerReview.objects.create(
                business=business,
                review_link=review_link,
                customer_name=customer_name,
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
                review.save() # update the DB by filling the ai_review

                '''
                print(f"SUCCESS! Review generated using {generation_method}")
                print(f"Generated review: {ai_review}")
                print(f"Review saved to database with ID: {review.id}")    
                '''
                
                # Return JSON response instead of rendering template
                return JsonResponse({
                    'success': True,
                    'ai_review': ai_review,
                    'generation_method': generation_method,
                    'google_url': business.google_review_url
                })
                
            except Exception as e:
                print(f"ERROR generating AI review: {str(e)}")
                
                # Fallback to old method if something goes wrong
                review.generate_ai_review()
                fallback_review = review.ai_review
                print("Used fallback generation method")
                
                return JsonResponse({
                    'success': True,
                    'ai_review': fallback_review,
                    'generation_method': 'Fallback Template',
                    'google_url': business.google_review_url
                })

        except ReviewLink.DoesNotExist:
            print("ReviewLink not found")
            return JsonResponse({
                'success': False,
                'error': 'Review link not found'
            })
        except Exception as e:
            print(f"Error in submit_review: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    print("Invalid request method")
    return JsonResponse({
        'success': False,
        'error': 'Invalid request method'
    })

# Converts slider ratings into natural language sentences
# that the AI can understand and use instead of just numbers and keywords.
def create_detailed_feedback(food_rating, service_rating, atmosphere_rating, recommend_rating, feedback, tags):
    """
    Create detailed feedback text that incorporates all slider ratings
    """
    feedback_parts = []
    
    # Add original feedback first
    if feedback.strip():
        feedback_parts.append(feedback.strip())
    
    # Add rating-specific feedback
    if food_rating >= 4:
        feedback_parts.append("The food quality was excellent")
    elif food_rating <= 2:
        feedback_parts.append("The food quality could be improved")
    
    if service_rating >= 4:
        feedback_parts.append("The service was fast and friendly")
    elif service_rating <= 2:
        feedback_parts.append("The service was slow")
    
    if atmosphere_rating >= 4:
        feedback_parts.append("I loved the atmosphere")
    elif atmosphere_rating <= 2:
        feedback_parts.append("The atmosphere was okay")
    
    if recommend_rating >= 4:
        feedback_parts.append("I would definitely recommend this place")
    elif recommend_rating <= 2:
        feedback_parts.append("I'm not sure I would recommend this place")
    
    # Add tags if present
    if tags.strip():
        feedback_parts.append(f"What stood out: {tags}")
    
    return ". ".join(feedback_parts) + "."