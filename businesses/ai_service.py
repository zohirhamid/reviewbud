import openai
from django.conf import settings
import logging
import random
import re

logger = logging.getLogger(__name__)

def generate_review_with_ai(rating, feedback, business_name, tags=""):
    try:
        client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
        
        # Pick personality and length FIRST
        personality = random.choice([
            "busy professional - quick and to the point",
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
        
        prompt = create_review_prompt(rating, feedback, business_name, tags, personality, length_config["words"])

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "You write quick, casual Google reviews. Be brief, imperfect, and natural. Avoid AI clichés."
                },
                {"role": "user", "content": prompt}
            ],
            max_tokens=int(length_config["tokens"]),  # Explicitly convert to integer
            temperature=0.92,
            presence_penalty=0.6,
            frequency_penalty=0.7,
            top_p=0.95
        )

        content = response.choices[0].message.content
        if not content:
            raise ValueError("OpenAI API returned empty content")
        
        generated_review = content.strip()
        generated_review = humanize(generated_review, rating)

        logger.info(f"AI review generated: {len(generated_review.split())} words")
        return generated_review, "ChatGPT API"

    except Exception as e:
        logger.error(f"Error generating AI review: {str(e)}")
        return generate_fallback_review(rating, feedback, business_name, tags)


def create_review_prompt(rating, feedback, business_name, tags, personality, target_words):
    """Simplified, less instructional prompt"""
    
    # Build context naturally
    context = f"Rating: {rating}⭐"
    if feedback:
        context += f"\nWhat happened: {feedback}"
    if tags:
        context += f"\nNotable: {tags}"
    
    # Rating-specific guidance (minimal)
    if rating >= 5:
        vibe = "excited and positive, mention what made it special"
    elif rating == 4:
        vibe = "mostly happy but mention one small thing that could be better"
    elif rating == 3:
        vibe = "it was mid, just state the facts quickly, no analysis needed"
    else:
        vibe = "frustrated and disappointed, be direct about what sucked"
    
    # Anti-AI blocklist
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
- Any meta-analysis or philosophical observations
"""
    
    # Examples to guide tone
    examples = ""
    if rating >= 4:
        examples = """
Good examples:
- "food was fire, service was quick, coming back"
- "great spot, had the burger and it slapped"
- "vibes were immaculate, coffee was good too"
"""
    elif rating == 3:
        examples = """
Good examples (3-star):
- "food was okay, nothing special. prob won't go back"
- "decent spot but overpriced for what you get"
- "meh. service was fine, food was mid"
"""
    else:
        examples = """
Good examples (1-2 star):
- "waited 30 mins for cold food, not going back"
- "order was wrong and they didn't fix it. disappointed"
- "overpriced and service was terrible"
"""
    
    prompt = f"""Write a Google review for {business_name}.

{context}

Style: {personality}
Tone: {vibe}
Length: {target_words} words MAX (seriously, keep it brief)

{forbidden}

{examples}

Rules:
- Write like texting a friend
- Focus on 1-2 things that mattered most
- Use casual language ("pretty good", "kinda meh", "tbh")
- Can use fragments or incomplete sentences
- NO corporate speak or flowery language
- Don't mention everything, just what stood out

Write the review now (no intro, just the review):"""
    
    return prompt


HUMANIZERS = {
    "starters": ["honestly", "ngl", "so", "okay so", "real talk", "tbh"],
    "intensifiers": ["super", "really", "pretty", "so", "very", "lowkey", "highkey"],
    "endings": ["!", ".", "..", ""],
    "casual_replacements": {
        "very good": random.choice(["really good", "pretty good", "solid"]),
        "excellent": random.choice(["great", "fire", "amazing", "really good"]),
        "terrible": random.choice(["bad", "not good", "disappointing"]),
        "wonderful": random.choice(["great", "nice", "good"]),
        "delicious": random.choice(["good", "tasty", "fire", "great"]),
        "absolutely": "",
        "extremely": "really",
        "quite": "pretty",
    },
    "emojis": ["🔥", "👌", "💯", ""],
}

def humanize(text: str, rating: int) -> str:
    """Post-process to add human imperfections"""
    
    # 1. Replace overly formal words
    for formal, casual in HUMANIZERS["casual_replacements"].items():
        if formal in text.lower():
            # Case-insensitive replacement
            pattern = re.compile(re.escape(formal), re.IGNORECASE)
            text = pattern.sub(casual, text)
    
    # 2. Remove quotation marks (AI loves these)
    text = text.replace('"', '').replace("'", "'")
    
    # 3. Random casual starter (20% chance)
    if random.random() > 0.80:
        starter = random.choice(HUMANIZERS["starters"])
        text = f"{starter} {text}"
    
    # 4. Vary ending punctuation
    if text.endswith('.'):
        text = text[:-1] + random.choice(HUMANIZERS["endings"])
    
    # 5. Sometimes lowercase first letter (20% chance)
    if random.random() > 0.8 and len(text) > 1:
        text = text[0].lower() + text[1:]
    
    # 6. Remove excessive exclamation marks (AI overuses these)
    text = re.sub(r'!{2,}', '!', text)
    
    # 7. Add emoji rarely for positive reviews (15% chance)
    if rating >= 4 and random.random() > 0.85:
        emoji = random.choice([e for e in HUMANIZERS["emojis"] if e])
        text = f"{text} {emoji}"
    
    # 8. Contract common phrases
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
    if len(words) > 5 and random.random() > 0.6:
        # Find an adjective-ish word to intensify
        for i in range(1, len(words) - 1):
            if words[i].lower() in ["good", "bad", "nice", "slow", "fast", "busy"]:
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
    """Simpler fallback without AI"""
    
    feedback_text = feedback.strip() if feedback else "visited this place"
    
    if rating >= 4:
        templates = [
            f"great experience at {business_name}. {feedback_text}. coming back for sure",
            f"{business_name} was solid. {feedback_text}. recommend",
            f"really enjoyed {business_name}. {feedback_text} 👌"
        ]
    elif rating == 3:
        templates = [
            f"{business_name} was alright. {feedback_text}",
            f"decent spot. {feedback_text}. nothing crazy",
        ]
    else:
        templates = [
            f"not great. {feedback_text}",
            f"{feedback_text} at {business_name}. disappointing",
        ]
    
    return random.choice(templates)