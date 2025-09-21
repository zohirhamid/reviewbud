import openai
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

def generate_review_with_ai(rating, feedback, business_name, tags=""):
    try:
        client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
        prompt = create_review_prompt(rating, feedback, business_name, tags)

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant that writes authentic, human-like Google reviews. Sound casual, detailed, and natural. Do not sound like AI."
                },
                {"role": "user", "content": prompt}
            ],
            max_tokens=120,
            temperature=0.9,
            presence_penalty=0.4,
            frequency_penalty=0.5,
            top_p=0.95
        )

        content = response.choices[0].message.content
        if not content:
            raise ValueError("OpenAI API returned empty content")
        generated_review = content.strip()

        logger.info("AI review generated successfully")
        return generated_review, "ChatGPT API"

    except Exception as e:
        logger.error(f"Error generating AI review: {str(e)}")
        review = generate_fallback_review(rating, feedback, business_name, tags)
        return review, "Fallback (API Error)"
    

def create_review_prompt(rating, feedback, business_name, tags):
    prompt = f"""Write a natural, authentic-sounding Google review for {business_name}.

    Context:
    - Rating: {rating}/5 stars
    - Customer's notes: "{feedback}"
    - Highlights: {tags if tags else 'None specified'}

    Review requirements:
    - Length: 40–60 words.
    - Sound like a real customer, not a marketer.
    - Reference at least one *specific* aspect (e.g., service, staff, food, vibe, price, waiting time).
    - Match tone to the rating:
        • 5 stars → warm, detailed praise but not over the top.
        • 4 stars → mostly positive with a minor suggestion.
        • 3 stars → balanced mix of good and “could be better”.
        • 1–2 stars → clear frustrations but still polite and constructive.
    - Avoid clichés like “nice place” or “great food”.
    - Write as if telling a friend casually.
    - Small imperfections or hesitation words (“kind of”, “a bit”, “honestly”) make it feel more real.

    Now generate the review:"""
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