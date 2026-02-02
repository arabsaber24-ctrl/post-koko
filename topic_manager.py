"""
Topic Manager for Kids Educational Content
Generates kid-friendly, halal topics using Longcat AI
"""

import os
import json
import logging
from typing import List, Dict
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)


class TopicManager:
    def __init__(self):
        self.client = OpenAI(
            api_key=os.getenv("LONGCAT_API_KEY"),
            base_url=os.getenv("LONGCAT_BASE_URL", "https://api.longcat.chat/openai")
        )
        self.model = "LongCat-Flash-Chat"
        
        # Educational categories for kids (halal & safe)
        self.categories = [
            "English Basics",
            "Math Basics",
            "Early Reading",
            "Writing Practice",
            "Good Manners",
            "Good Character",
            "Daily Etiquette",
            "Moral Stories",
            "Thinking Skills",
            "Problem Solving",
            "Time & Routine",
            "Colors & Shapes",
            "Numbers in Daily Life",
            "Safety Basics",
            "Self-Care",
            "Organization & Responsibility",
            "Emotions",
            "Good Deeds",
            "Islamic Manners",
            "General Knowledge"
        ]

    def generate_topics(self, count: int = 200) -> List[Dict]:
        """
        Generate kid-friendly educational topics using Longcat AI
        
        Args:
            count: Number of topics to generate (default 200)
            
        Returns:
            List of topic dictionaries with keys: category, main_topic, subtopic
        """
        logger.info(f"Generating {count} kid-friendly topics...")
        
        categories_str = ", ".join(self.categories)
        
        prompt = f"""Generate {count} unique, educational topics for young children (ages 4-10).

IMPORTANT RULES:
- Content must be halal, safe, and age-appropriate
- NO topics about humans, faces, animals, or living creatures
- Focus on concepts, manners, skills, and knowledge
- Each topic should be simple and easy to understand
- Topics should be positive and educational

CATEGORIES: {categories_str}

For each topic, provide:
1. category (from the list above)
2. main_topic (broad concept)
3. subtopic (specific lesson)

Return ONLY a JSON object with this structure:
{{
  "topics": [
    {{
      "category": "Good Manners",
      "main_topic": "Politeness",
      "subtopic": "Saying Thank You"
    }},
    {{
      "category": "Math Basics",
      "main_topic": "Counting",
      "subtopic": "Numbers 1 to 10"
    }}
  ]
}}

Generate {count} diverse topics covering all categories."""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert educator creating safe, halal, kid-friendly educational content. Return only valid JSON."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.8,
                max_tokens=8000,
                response_format={"type": "json_object"}
            )
            
            content = response.choices[0].message.content
            data = json.loads(content)
            
            # Extract topics from response
            if "topics" in data:
                topics = data["topics"]
            elif isinstance(data, list):
                topics = data
            else:
                # Try to find any list in the response
                for key in data:
                    if isinstance(data[key], list):
                        topics = data[key]
                        break
                else:
                    logger.error("Could not find topics list in response")
                    return []
            
            # Validate and clean topics
            valid_topics = []
            for topic in topics:
                if all(key in topic for key in ['category', 'main_topic', 'subtopic']):
                    valid_topics.append({
                        'category': topic['category'],
                        'main_topic': topic['main_topic'],
                        'subtopic': topic['subtopic']
                    })
            
            logger.info(f"Successfully generated {len(valid_topics)} topics")
            return valid_topics
            
        except Exception as e:
            logger.error(f"Failed to generate topics: {e}")
            return []

    def generate_topics_batch(self, total_count: int = 200, batch_size: int = 50) -> List[Dict]:
        """
        Generate topics in batches to avoid token limits
        
        Args:
            total_count: Total number of topics to generate
            batch_size: Number of topics per batch
            
        Returns:
            List of all generated topics
        """
        all_topics = []
        batches = (total_count + batch_size - 1) // batch_size
        
        for i in range(batches):
            count = min(batch_size, total_count - len(all_topics))
            logger.info(f"Generating batch {i+1}/{batches} ({count} topics)...")
            
            topics = self.generate_topics(count)
            all_topics.extend(topics)
            
            if len(all_topics) >= total_count:
                break
        
        return all_topics[:total_count]

    def get_sample_topics(self) -> List[Dict]:
        """
        Get a small set of sample topics for testing
        
        Returns:
            List of 10 sample topics
        """
        return [
            {"category": "Good Manners", "main_topic": "Politeness", "subtopic": "Saying Please"},
            {"category": "Good Manners", "main_topic": "Politeness", "subtopic": "Saying Thank You"},
            {"category": "Math Basics", "main_topic": "Counting", "subtopic": "Numbers 1 to 5"},
            {"category": "Math Basics", "main_topic": "Shapes", "subtopic": "Circle and Square"},
            {"category": "Colors & Shapes", "main_topic": "Colors", "subtopic": "Red and Blue"},
            {"category": "Good Character", "main_topic": "Honesty", "subtopic": "Telling the Truth"},
            {"category": "Self-Care", "main_topic": "Hygiene", "subtopic": "Washing Hands"},
            {"category": "Time & Routine", "main_topic": "Daily Schedule", "subtopic": "Morning Routine"},
            {"category": "Safety Basics", "main_topic": "Home Safety", "subtopic": "Being Careful"},
            {"category": "Good Deeds", "main_topic": "Helping Others", "subtopic": "Sharing with Friends"}
        ]
