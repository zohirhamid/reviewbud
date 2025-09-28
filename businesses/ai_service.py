import openai
from django.conf import settings
import logging
import random

logger = logging.getLogger(__name__)

def generate_review_with_ai(rating, feedback, business_name, tags=""):
    try:
        client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
        prompt = create_review_prompt(rating, feedback, business_name, tags)

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant that writes authentic, human-like Google reviews. Sound casual, detailed, and natural. Do not sound like AI."
                },
                {"role": "user", "content": prompt}
            ],
            max_tokens=150,
            temperature=0.7,
            presence_penalty=0.3,
            frequency_penalty=0.4,
            top_p=0.9
        )

        content = response.choices[0].message.content
        if not content:
            raise ValueError("OpenAI API returned empty content")
        generated_review = content.strip()

        logger.info("AI review generated successfully")
        return generated_review, "ChatGPT API"

    except Exception as e:
        logger.error(f"Error generating AI review: {str(e)}")
        return generate_fallback_review(rating, feedback, business_name, tags)
    

def create_review_prompt(rating, feedback, business_name, tags):
    prompt = f"""Write a natural, authentic-sounding Google review for {business_name}.

    Context:
    - Rating: {rating}/5 stars
    - Customer's notes: "{feedback}"
    - Highlights: {tags if tags else 'None specified'}

    Review requirements:
    - Length: 50–90 words (aim for realistic, medium-length reviews).
    - Sound like a real customer talking to a friend, not a marketer.
    - Vary the opening sentence across reviews (avoid starting with "Had a great experience..." every time).
    - Reference at least one specific aspect: service, staff, food, drinks, atmosphere, waiting time, or price.
    - If rating = 5 stars → warm, detailed praise with a personal touch ("will bring my family again", "perfect for date night").
    - If rating = 4 stars → mostly positive, add a minor suggestion.
    - If rating = 3 stars → balanced: mention both good points and what could be better.
    - If rating = 1–2 stars → clear frustrations but stay polite and constructive.
    - Use casual, everyday language. Small imperfections like "kind of", "a bit", or "honestly" are good for realism.
    - Do not sound like AI. Avoid generic filler phrases like "great food" or "nice place."

    Now write the review:
    """
    return prompt


def generate_fallback_review(rating, feedback, business_name, tags=""):
    feedback_text = feedback.strip() if feedback else ""
    tags_text = f" {tags.strip()}" if tags else ""
    
    if rating >= 4:
        templates = [
            f"Had a great experience at {business_name}! {feedback_text}{tags_text} Definitely recommend this place.",
            f"Really enjoyed my visit to {business_name}. {feedback_text}{tags_text} Will definitely be back!",
            f"Excellent service at {business_name}. {feedback_text}{tags_text} Highly recommended!"
        ]
    elif rating == 3:
        templates = [
            f"Decent experience at {business_name}. {feedback_text}{tags_text}",
            f"Overall okay visit to {business_name}. {feedback_text}{tags_text}"
        ]
    else:
        templates = [
            f"Visited {business_name}. {feedback_text}{tags_text}",
        ]
    
    return random.choice(templates)