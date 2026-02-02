"""
Content Generator for Kids Educational Videos
Generates 4-slide lesson content using Longcat AI
"""

import os
import json
import logging
from typing import Dict
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)


class ContentGenerator:
    def __init__(self):
        self.client = OpenAI(
            api_key=os.getenv("LONGCAT_API_KEY"),
            base_url=os.getenv("LONGCAT_BASE_URL", "https://api.longcat.chat/openai")
        )
        self.model = "LongCat-Flash-Chat"

    def generate_lesson(self, topic_data: Dict) -> Dict:
        """
        Generate 4-slide lesson content for a given topic
        
        Args:
            topic_data: Dictionary with keys: category, main_topic, subtopic
            
        Returns:
            Dictionary with keys: slide1, slide2, slide3, slide4, full_text
        """
        category = topic_data['category']
        main_topic = topic_data['main_topic']
        subtopic = topic_data['subtopic']
        
        logger.info(f"Generating lesson for: {category} - {main_topic} - {subtopic}")
        
        prompt = f"""Create a 4-slide educational lesson for young children (ages 4-10).

TOPIC DETAILS:
- Category: {category}
- Main Topic: {main_topic}
- Subtopic: {subtopic}

IMPORTANT RULES:
- Content must be halal, safe, and age-appropriate
- Use simple, clear language for kids
- NO mentions of humans, faces, animals, or living creatures
- Focus on concepts, actions, and ideas
- Keep text short and easy to read
- Be positive and encouraging

SLIDE STRUCTURE:

Slide 1 - TITLE:
- Just the subtopic name
- Short and catchy (3-6 words maximum)
- Example: "Saying Thank You"

Slide 2 - EXPLANATION:
- Explain what it is
- 1-2 short sentences
- Simple words
- Example: "Thank you means we are grateful. We say it when someone helps us."

Slide 3 - EXAMPLES:
- Give 2-3 simple examples
- Real-life situations kids understand
- Short phrases or sentences
- Example: "When someone gives you a toy\\nWhen someone opens the door\\nWhen someone shares food"

Slide 4 - PRACTICE/REFLECTION:
- A simple question or task
- Encourages thinking or action
- Positive and friendly
- Example: "Can you say thank you today?"

Return ONLY a JSON object with this exact structure:
{{
  "slide1": "Title text here",
  "slide2": "Explanation text here",
  "slide3": "Examples text here (use \\\\n for line breaks)",
  "slide4": "Practice/reflection text here"
}}"""

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
                temperature=0.7,
                max_tokens=1000,
                response_format={"type": "json_object"}
            )
            
            content = response.choices[0].message.content
            lesson_data = json.loads(content)
            
            # Validate that all slides are present
            required_keys = ['slide1', 'slide2', 'slide3', 'slide4']
            if not all(key in lesson_data for key in required_keys):
                raise ValueError("Missing required slide keys in response")
            
            # Create full text for voiceover (combines all slides)
            full_text = f"{lesson_data['slide1']}. {lesson_data['slide2']} {lesson_data['slide3']} {lesson_data['slide4']}"
            lesson_data['full_text'] = full_text
            
            logger.info("Lesson content generated successfully")
            return lesson_data
            
        except Exception as e:
            logger.error(f"Failed to generate lesson: {e}")
            raise

    def generate_lesson_with_retry(self, topic_data: Dict, max_retries: int = 3) -> Dict:
        """
        Generate lesson with retry logic
        
        Args:
            topic_data: Topic information
            max_retries: Maximum number of retry attempts
            
        Returns:
            Generated lesson data
        """
        for attempt in range(max_retries):
            try:
                return self.generate_lesson(topic_data)
            except Exception as e:
                logger.warning(f"Attempt {attempt + 1}/{max_retries} failed: {e}")
                if attempt == max_retries - 1:
                    logger.error("All retry attempts exhausted")
                    raise
        
        # This should never be reached, but just in case
        raise Exception("Failed to generate lesson after all retries")

    def get_sample_lesson(self) -> Dict:
        """
        Get a sample lesson for testing
        
        Returns:
            Sample lesson dictionary
        """
        return {
            "slide1": "Saying Thank You",
            "slide2": "Thank you means we are grateful. We say it when someone helps us.",
            "slide3": "When someone gives you a toy\nWhen someone opens the door\nWhen someone shares food",
            "slide4": "Can you say thank you today?",
            "full_text": "Saying Thank You. Thank you means we are grateful. We say it when someone helps us. When someone gives you a toy. When someone opens the door. When someone shares food. Can you say thank you today?"
        }
