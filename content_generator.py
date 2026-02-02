"""
Content Generator for Kids Educational Videos
Generates 4-slide lesson content using AI with extreme simplicity for kids
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
        self.client = OpenAI()
        self.model = "gpt-4.1-mini"
        
        self.fallback_content = {
            "English Basics": {
                "Alphabet": {
                    "Learning Letter A": {
                        "slide1": "Letter A",
                        "slide2": "A says Ah!",
                        "slide3": "Apple\nAnt\nAxe",
                        "slide4": "Say Ah!"
                    }
                }
            }
        }

    def generate_lesson(self, topic_data: Dict) -> Dict:
        """
        Generate 4-slide lesson content with extreme simplicity
        """
        category = topic_data.get('category', 'General')
        subtopic = topic_data.get('subtopic', 'Fun Learning')
        
        logger.info(f"Generating lesson for: {category} - {subtopic}")
        
        try:
            prompt = f"""Create a 4-slide educational lesson for toddlers (ages 2-5).
            
TOPIC: {subtopic} ({category})

STRICT RULES FOR KIDS:
1. EXTREME SIMPLICITY: Use as few words as possible.
2. NO animals, humans, or living creatures.
3. Slide 1 (Title): 1-2 words only.
4. Slide 2 (What is it?): 1 very short sentence (max 5 words).
5. Slide 3 (Examples): 3 simple objects, 1 word each.
6. Slide 4 (Action): 1 very short instruction (max 4 words).

FORMAT: Return ONLY JSON.
{{
  "slide1": "Title",
  "slide2": "Simple sentence.",
  "slide3": "Word1\\nWord2\\nWord3",
  "slide4": "Action word!"
}}"""

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert in toddler education. You speak in very few, simple words."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                response_format={ "type": "json_object" }
            )
            
            lesson_data = json.loads(response.choices[0].message.content)
            # Ensure all keys exist
            for key in ["slide1", "slide2", "slide3", "slide4"]:
                if key not in lesson_data:
                    lesson_data[key] = f"Slide {key[-1]}"
            
            return self.improve_lesson_content(lesson_data)
                
        except Exception as e:
            logger.error(f"API generation failed: {e}")
            return {
                "slide1": f"{subtopic}",
                "slide2": f"Look at {subtopic}!",
                "slide3": "Cool\nFun\nGreat",
                "slide4": "You do it!",
                "full_text": f"{subtopic}. Look at {subtopic}! Cool, Fun, Great. You do it!"
            }

    def improve_lesson_content(self, lesson_data: Dict) -> Dict:
        """
        AI Feature: Further improves content to be more engaging for kids
        """
        logger.info("AI Feature: Improving content for kids...")
        try:
            prompt = f"""You are a 'Kid-Friendly AI'. Your job is to take these 4 slides and make them even more fun, simpler, and engaging for a 3-year-old.
            
            Current Content:
            1: {lesson_data['slide1']}
            2: {lesson_data['slide2']}
            3: {lesson_data['slide3']}
            4: {lesson_data['slide4']}
            
            Your Task:
            - Make words sound 'happier'.
            - Ensure NO animals/humans.
            - Reduce word count even more.
            - Return the improved version in JSON format with keys: slide1, slide2, slide3, slide4.
            """
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a Kid-Friendly AI specialized in extreme simplicity and engagement."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.8,
                response_format={ "type": "json_object" }
            )
            
            improved_data = json.loads(response.choices[0].message.content)
            
            # Merge with original if keys missing
            for key in ["slide1", "slide2", "slide3", "slide4"]:
                if key not in improved_data:
                    improved_data[key] = lesson_data[key]
            
            # Add full_text for TTS
            s3 = improved_data['slide3'].replace('\n', '. ')
            improved_data["full_text"] = f"{improved_data['slide1']}. {improved_data['slide2']}. {s3}. {improved_data['slide4']}"
            
            logger.info("Content improved by AI successfully")
            return improved_data
        except Exception as e:
            logger.warning(f"AI improvement failed: {e}")
            s3 = lesson_data['slide3'].replace('\n', '. ')
            lesson_data["full_text"] = f"{lesson_data['slide1']}. {lesson_data['slide2']}. {s3}. {lesson_data['slide4']}"
            return lesson_data

    def generate_batch_topics(self, count: int = 200) -> list:
        categories = ["Colors", "Shapes", "Numbers", "Objects", "Manners"]
        topics = []
        for i in range(count):
            cat = categories[i % len(categories)]
            topics.append({
                "id": i + 1, "category": cat, "main_topic": f"{cat} Fun", "subtopic": f"Cool {cat}", "status": "unused"
            })
        return topics
