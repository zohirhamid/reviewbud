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
            model="gpt-3.5-turbo",
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
            max_tokens=55,
            temperature=0.7,
            presence_penalty=0.1,
            frequency_penalty=0.1
        )
        
        generated_review = response.choices[0].message.content.strip()
        logger.info("Successfully generated AI review")
        return generated_review, "ChatGPT API"
        
    except Exception as e:
        logger.error(f"Error generating AI review: {str(e)}")
        # Fallback to simple template if API fails
        review = generate_fallback_review(rating, feedback, business_name, tags)
        return review, "Fallback (API Error)"  # <-- And this too!

def create_review_prompt(rating, feedback, business_name, tags):
    """
    Create a structured prompt for ChatGPT based on customer input
    """
    # Convert rating to descriptive terms
    rating_descriptions = {
        1: "very disappointed and unsatisfied",
        2: "somewhat disappointed", 
        3: "okay/average experience",
        4: "good and satisfied",
        5: "excellent and very satisfied"
    }
    """
    get(): a function that looks for a value in a desc using a key (first param)
    and returns it if found
    if not returns a default value (second param)
    """
    rating_desc = rating_descriptions.get(rating, "satisfied")
    

    # Creating a prompt
    prompt = f"""Write a natural Google review for {business_name}. 
    Customer rating: {rating}/5 stars ({rating_desc})
    Customer feedback: "{feedback}"
    """
    
    if tags: # if we have tags input add them
        prompt += f"Positive aspects mentioned: {tags}\n"
    
    prompt += f"""
        Requirements:
        - Write in first person as if the customer wrote it
        - Sound natural and conversational
        - Include specific details from the feedback
        - Keep it between 30-50 words
        - Match the tone to the {rating}/5 star rating
        - Don't mention that this is AI-generated
        - Make it sound like a real customer experience
        """
    
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
    return random.choice(templates)  # <-- Just return the review, not a tuple

def test_ai_service():
    """
    Test function to verify AI service is working
    """
    try:
        test_review = generate_review_with_ai(
            rating=5,
            feedback="The food was amazing and service was super fast",
            business_name="Mario's Pizza",
            tags="Great value, Friendly staff"
        )
        print("AI Service Test Successful!")
        print(f"Generated review: {test_review}")
        return True
    except Exception as e:
        print(f"AI Service Test Failed: {str(e)}")
        return False