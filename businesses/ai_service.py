import openai
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

def generate_review_with_ai(rating, feedback, business_name, tags=""):
    """
    Generate a natural review using ChatGPT API based on customer input
    Returns: (review_text, generation_method)
    """
    try:
        # Initialize OpenAI client
        client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
        
        # Prepare the prompt based on rating and input
        prompt = create_review_prompt(rating, feedback, business_name, tags)
        
        response = client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant that writes authentic, natural-sounding Google reviews based on customer feedback. Keep reviews conversational, genuine, and between 35-55 words. Avoid overly promotional language."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            max_tokens=75,
            temperature=0.8,
            presence_penalty=0.3,
            frequency_penalty=0.3,
            top_p=0.95
        )
        
        # Fix: Add None check before calling strip()
        content = response.choices[0].message.content
        if content is None:
            raise ValueError("OpenAI API returned None content")
        generated_review = content.strip()
        
        logger.info("Successfully generated AI review")
        return generated_review, "ChatGPT API"
        
    except Exception as e:
        logger.error(f"Error generating AI review: {str(e)}")
        # Fallback to simple template if API fails
        review = generate_fallback_review(rating, feedback, business_name, tags)
        return review, "Fallback (API Error)"
    

def create_review_prompt(rating, feedback, business_name, tags):
    prompt = f"""Generate a natural Google review for {business_name}.

    Context:
    - Overall rating: {rating}/5 stars
    - Customer's actual feedback: "{feedback}"
    - Key highlights: {tags if tags else 'None specified'}

    Instructions:
    1. Incorporate specific details from the feedback naturally
    2. Match the emotional tone to the {rating}-star rating
    3. Include 1-2 specific details that make it feel authentic
    4. Avoid generic phrases like "great place" or "nice restaurant"
    5. Write as if recommending (or warning) a friend
    6. Length: 35-50 words
    7. Don't use exclamation marks excessively
    8. Include subtle imperfections for authenticity (e.g., minor critiques even in positive reviews)

    Generate the review:"""
    
    return prompt

def generate_fallback_review(rating, feedback, business_name, tags=""):
    """
    Fallback method if ChatGPT API fails - uses simple templates
    """
    feedback_text = feedback.strip() if feedback else ""
    tags_text = tags.strip() if tags else ""
    
    if rating >= 4:
        templates = [
            f"Had a great experience at {business_name}! {feedback_text} {tags_text} Definitely recommend this place.",
            f"Really enjoyed my visit to {business_name}. {feedback_text} {tags_text} Will definitely be back!",
            f"Excellent service at {business_name}. {feedback_text} {tags_text} Highly recommended!"
        ]
    elif rating == 3:
        templates = [
            f"Decent experience at {business_name}. {feedback_text} {tags_text}",
            f"Overall okay visit to {business_name}. {feedback_text} {tags_text}"
        ]
    else:
        templates = [
            f"Visited {business_name}. {feedback_text} {tags_text}",
        ]
    
    import random
    return random.choice(templates)