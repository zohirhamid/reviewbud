import openai
from django.conf import settings
import logging
import random
import re
import json
import os
logger = logging.getLogger(__name__)

# Load reviews once at module level
REVIEWS_PATH = os.path.join(settings.BASE_DIR, 'businesses', 'data', 'restaurant_reviews.json')
REVIEW_DATASET = None

def load_review_dataset():
    """Load the review dataset once."""
    global REVIEW_DATASET
    if REVIEW_DATASET is None:
        try:
            with open(REVIEWS_PATH, 'r', encoding='utf-8') as f:
                REVIEW_DATASET = json.load(f)
            logger.info(f"Loaded {len(REVIEW_DATASET)} reviews from dataset")
        except Exception as e:
            logger.error(f"Failed to load review dataset: {e}")
            REVIEW_DATASET = []
    return REVIEW_DATASET

def get_example_reviews(rating, num_examples=3):
    """Get random real reviews matching the rating for few-shot learning."""
    reviews = load_review_dataset()
    
    if not reviews:
        return []
    
    # Filter by rating (exact match preferred, ±1 tolerance)
    exact_matches = [r for r in reviews if r.get('stars') == rating]
    
    if len(exact_matches) >= num_examples:
        matching = exact_matches
    else:
        # Fallback to ±1 star tolerance
        matching = [r for r in reviews if abs(r.get('stars', 0) - rating) <= 1]
    
    if not matching:
        return []
    
    return random.sample(matching, min(num_examples, len(matching)))




def generate_review_with_ai(ratings, feedback, business_name, tags=""):
    """
    Generate a Google-style review using GPT-4o with humanization post-processing.
    Falls back to simple templates if API fails.

    Args:
        ratings (dict): food, service, atmosphere, recommend ratings (int 1-5)
        feedback (str): optional customer notes
        business_name (str): name of the business
        tags (str): optional highlights/keywords

    Returns:
        tuple: (ai_review, generation_method, avg_rating)
    """
    if not ratings:
        logger.error("Empty ratings dictionary provided")
        return generate_fallback_review(3, feedback, business_name, tags), "Fallback", 3

    avg_rating = round(sum(ratings.values()) / len(ratings))

    try:
        client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)

        # Randomize personality and target length
        personality = random.choice([
            "busy professional - quick and blunt",
            "college student - casual with some slang",
            "foodie - focuses on taste and quality",
            "regular customer - relaxed and familiar",
            "first-timer - excited or disappointed"
        ])
        
        length_config = random.choice([
            {"words": "15-25", "tokens": 40},
            {"words": "30-45", "tokens": 70},
            {"words": "50-70", "tokens": 100}
        ])

        prompt = create_review_prompt(
            avg_rating, feedback, business_name, tags, personality, length_config["words"]
        )

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system",
                 "content": "You write quick, casual Google reviews. Be brief, imperfect, and natural. Avoid AI clichés."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=int(length_config["tokens"]),
            temperature=0.92,
            presence_penalty=0.6,
            frequency_penalty=0.7,
            top_p=0.95
        )

        content = response.choices[0].message.content
        if not content:
            raise ValueError("OpenAI API returned empty content")

        ai_review = content.strip()
        
        # Apply humanization post-processing
        ai_review = humanize(ai_review, avg_rating)
        
        logger.info(f"AI review generated ({len(ai_review.split())} words)")
        return ai_review, "ChatGPT API", avg_rating

    except Exception as e:
        logger.error(f"Error generating AI review: {e}")
        review = generate_fallback_review(avg_rating, feedback, business_name, tags)
        return review, "Fallback Template", avg_rating


def create_review_prompt(rating, feedback, business_name, tags, personality, target_words):
    """Builds a comprehensive prompt with anti-AI guardrails and real examples."""
    
    # Build context naturally
    context = f"Rating: {rating}⭐"
    if feedback:
        context += f"\nWhat happened: {feedback}"
    if tags:
        context += f"\nNotable: {tags}"

    # Rating-specific tone guidance - FIXED FOR 3-STAR
    tone_map = {
        5: "excited and positive, mention what made it special",
        4: "mostly happy, highlight what was good",
        3: "neutral to slightly positive, it was decent/fine but nothing crazy",
        2: "disappointed but fair, explain what went wrong",
        1: "frustrated and disappointed, be direct about what failed"
    }
    vibe = tone_map.get(rating, "neutral, balanced tone")

    # Get real review examples for style reference
    real_examples = get_example_reviews(rating, num_examples=2)
    examples_section = ""
    
    if real_examples:
        examples_text = "\n".join([f"- \"{ex.get('clean_text', '')}\"" for ex in real_examples])
        examples_section = f"""
Real Google reviews with similar ratings (for STYLE reference only):
{examples_text}

Match this natural, casual writing style.
"""

    # Anti-AI phrase blocklist
    forbidden = """
NEVER use these AI phrases:
- "I recently visited"
- "The ambiance was"
- "I would highly recommend"
- "nothing to write home about"
- "Overall, it's"
- "Don't get me wrong"
- "At the end of the day"
- "That being said"
- "Definitely worth"
- "Hidden gem"
- "couldn't decide if it's"
- "making special trips"
- "Maybe next time"
- "mind-blowing" or "blow your mind"
- Any words with dashes or hyphens
- Any meta-analysis or philosophical observations

CRITICAL: Do NOT invent specific menu items, dishes, or products unless the customer specifically mentioned them in their feedback. Use general terms like "food", "meal", "order" instead.
"""

    # Additional instruction based on feedback presence
    specificity_rule = ""
    if not feedback or len(feedback.strip()) < 10:
        specificity_rule = "\nIMPORTANT: Customer gave minimal details. Keep the review VERY general. Only mention things from the tags or rating, nothing else."

    return f"""Write a Google review for {business_name}.

{context}

{examples_section}

Style: {personality}
Tone: {vibe}
Length: {target_words} words MAX (seriously, keep it brief)

{forbidden}

Rules:
- Write like texting a friend - can be one long run-on sentence or short fragments
- Focus on 1-2 things that mattered most
- Use casual language ("pretty good", "kinda meh", "tbh", "solid", "decent")
- Prefer commas over periods when connecting thoughts
- NO corporate speak or flowery language
- Don't mention everything, just what stood out
- ONLY mention specific items/dishes if customer mentioned them in feedback
- If no specific details provided, stay general ("food", "service", "place"){specificity_rule}

Write the review now (no intro, just the review):"""


# Humanization constants
HUMANIZERS = {
    "starters": ["honestly", "ngl", "real talk", "tbh"],
    "intensifiers": ["super", "really", "pretty", "so", "very", "lowkey", "highkey"],
    "endings": ["!", ".", ""],
    "casual_replacements": {
        "very good": ["really good", "pretty good", "solid"],
        "excellent": ["great", "fire", "amazing", "really good"],
        "terrible": ["bad", "not good", "disappointing"],
        "wonderful": ["great", "nice", "good"],
        "delicious": ["good", "tasty", "fire", "great"],
        "absolutely": [""],
        "extremely": ["really"],
        "quite": ["pretty"],
    },
    "emojis": ["🔥", "👌", "💯"],
}

def humanize(text, rating):
    """
    Post-process AI output to add human imperfections and casual language.
    
    Args:
        text (str): AI-generated review
        rating (int): Star rating (1-5)
    
    Returns:
        str: Humanized review text
    """
    
    # 1. Replace overly formal words with casual alternatives
    for formal, casual_options in HUMANIZERS["casual_replacements"].items():
        if formal in text.lower():
            replacement = random.choice(casual_options)
            pattern = re.compile(re.escape(formal), re.IGNORECASE)
            text = pattern.sub(replacement, text)
    
    # 2. Remove quotation marks (AI loves these)
    text = text.replace('"', '').replace("'", "'")
    
    # 3. Add casual starter (5% chance instead of 20%, or remove this section entirely)
    if random.random() < 0.05:  # Changed from 0.20 to 0.05
        starter = random.choice(HUMANIZERS["starters"])
        text = f"{starter} {text}"
    
    # 4. Vary ending punctuation
    if text.endswith('.'):
        text = text[:-1] + random.choice(HUMANIZERS["endings"])
    
    # 5. Sometimes lowercase first letter (20% chance)
    if random.random() < 0.20 and len(text) > 1:
        text = text[0].lower() + text[1:]
    
    # 6. Remove excessive exclamation marks
    text = re.sub(r'!{2,}', '!', text)
    
    # 7. Add emoji for positive reviews (15% chance)
    if rating >= 4 and random.random() < 0.15:
        emoji = random.choice(HUMANIZERS["emojis"])
        text = f"{text} {emoji}"
    
    # 8. Apply common contractions
    contractions = {
        "I am": "I'm",
        "do not": "don't",
        "did not": "didn't",
        "was not": "wasn't",
        "is not": "isn't",
        "would not": "wouldn't",
        "will not": "won't",
        "cannot": "can't",
        "it is": "it's",
        "that is": "that's",
    }
    for full, short in contractions.items():
        text = re.sub(rf'\b{full}\b', short, text, flags=re.IGNORECASE)
    
    # 9. Random intensifier injection (40% chance)
    words = text.split()
    if len(words) > 5 and random.random() < 0.40:
        # Find common adjectives to intensify
        for i in range(1, len(words) - 1):
            if words[i].lower() in ["good", "bad", "nice", "slow", "fast", "busy", "quick"]:
                intensifier = random.choice(HUMANIZERS["intensifiers"])
                words[i] = f"{intensifier} {words[i]}"
                break
        text = " ".join(words)
    
    # 10. Remove AI-ish transition phrases
    ai_transitions = [
        "Additionally, ",
        "Furthermore, ",
        "Moreover, ",
        "In addition, ",
        "However, ",
        "Nevertheless, ",
    ]
    for transition in ai_transitions:
        text = text.replace(transition, "")
    
    return text.strip()


def generate_fallback_review(rating, feedback, business_name, tags=""):
    """
    Simple backup review generator if GPT API fails.
    
    Args:
        rating (int): Average star rating
        feedback (str): Customer notes
        business_name (str): Business name
        tags (str): Optional highlights
    
    Returns:
        str: Simple template-based review
    """
    feedback_text = feedback.strip() if feedback else "visited this place"
    tags_text = f" {tags}" if tags else ""

    if rating >= 4:
        templates = [
            f"great experience at {business_name}. {feedback_text}{tags_text}. coming back for sure",
            f"{business_name} was solid. {feedback_text}{tags_text}. recommend",
            f"really enjoyed {business_name}. {feedback_text}{tags_text} 👌"
        ]
    elif rating == 3:
        templates = [
            f"{business_name} was alright. {feedback_text}{tags_text}",
            f"decent spot. {feedback_text}{tags_text}. nothing crazy",
        ]
    else:
        templates = [
            f"not great. {feedback_text}{tags_text}",
            f"{feedback_text} at {business_name}. disappointing",
        ]

    return random.choice(templates)