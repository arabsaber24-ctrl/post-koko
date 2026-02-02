"""
Content Generator for Kids Educational Videos
Generates 4-slide lesson content using Longcat AI with fallback
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
        
        # Fallback content for common topics
        self.fallback_content = {
            "English Basics": {
                "Alphabet": {
                    "Learning Letter A": {
                        "slide1": "Learning Letter A",
                        "slide2": "The letter A is the first letter of the alphabet. It makes the sound 'ah' like in apple.",
                        "slide3": "Apple\nAnt\nAirplane",
                        "slide4": "Can you find things that start with A?"
                    },
                    "Learning Letter B": {
                        "slide1": "Learning Letter B",
                        "slide2": "The letter B is the second letter. It makes the sound 'buh' like in ball.",
                        "slide3": "Ball\nBee\nBanana",
                        "slide4": "What words start with B?"
                    }
                }
            },
            "Good Manners": {
                "Politeness": {
                    "Saying Thank You": {
                        "slide1": "Saying Thank You",
                        "slide2": "Thank you means we are grateful. We say it when someone helps us.",
                        "slide3": "When someone gives you a gift\nWhen someone opens the door\nWhen someone shares food",
                        "slide4": "Can you say thank you today?"
                    },
                    "Saying Please": {
                        "slide1": "Saying Please",
                        "slide2": "Please is a magic word. We use it when we ask for something.",
                        "slide3": "Please pass the water\nPlease help me\nPlease share your toy",
                        "slide4": "Remember to say please!"
                    }
                }
            },
            "Math Basics": {
                "Numbers": {
                    "Counting to 10": {
                        "slide1": "Counting to 10",
                        "slide2": "Numbers help us count things. Let's learn to count from 1 to 10.",
                        "slide3": "1, 2, 3, 4, 5\n6, 7, 8, 9, 10",
                        "slide4": "Can you count to 10?"
                    },
                    "Number One": {
                        "slide1": "Number One",
                        "slide2": "One is the first number. It means a single thing.",
                        "slide3": "One sun\nOne moon\nOne star",
                        "slide4": "Find one thing in your room"
                    }
                }
            },
            "Colors & Shapes": {
                "Colors": {
                    "Learning Red": {
                        "slide1": "Learning Red",
                        "slide2": "Red is a bright color. We see it in many things around us.",
                        "slide3": "Red apple\nRed flower\nRed car",
                        "slide4": "Find something red!"
                    },
                    "Learning Blue": {
                        "slide1": "Learning Blue",
                        "slide2": "Blue is a cool color. It reminds us of the sky and ocean.",
                        "slide3": "Blue sky\nBlue water\nBlue bird",
                        "slide4": "What blue things do you see?"
                    }
                },
                "Shapes": {
                    "Learning Circle": {
                        "slide1": "Learning Circle",
                        "slide2": "A circle is round. It has no corners or edges.",
                        "slide3": "The sun is round\nA ball is round\nA plate is round",
                        "slide4": "Can you draw a circle?"
                    },
                    "Learning Square": {
                        "slide1": "Learning Square",
                        "slide2": "A square has four equal sides. It has four corners.",
                        "slide3": "A window is square\nA box is square\nA tile is square",
                        "slide4": "Find a square shape!"
                    }
                }
            },
            "Daily Etiquette": {
                "Greetings": {
                    "Saying Hello": {
                        "slide1": "Saying Hello",
                        "slide2": "Hello is a friendly greeting. We say it when we meet someone.",
                        "slide3": "Hello in the morning\nHello to a friend\nHello to a teacher",
                        "slide4": "Say hello to someone today!"
                    }
                }
            }
        }

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
        
        # Try to use fallback content first
        if category in self.fallback_content:
            if main_topic in self.fallback_content[category]:
                if subtopic in self.fallback_content[category][main_topic]:
                    content = self.fallback_content[category][main_topic][subtopic]
                    logger.info("Using fallback content")
                    return {
                        "slide1": content["slide1"],
                        "slide2": content["slide2"],
                        "slide3": content["slide3"],
                        "slide4": content["slide4"],
                        "full_text": f"{content['slide1']}. {content['slide2']} {content['slide3']} {content['slide4']}"
                    }
        
        # Try to generate using API
        try:
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

Slide 2 - EXPLANATION:
- Explain what it is
- 1-2 short sentences
- Simple words

Slide 3 - EXAMPLES:
- Give 2-3 simple examples
- Real-life situations kids understand
- Short phrases or sentences
- Separate with newlines

Slide 4 - PRACTICE/REFLECTION:
- A simple question or task
- Encourages thinking or action
- Positive and friendly

RESPONSE FORMAT:
Return ONLY a JSON object with exactly these keys:
{{
  "slide1": "text",
  "slide2": "text",
  "slide3": "text with\\nnewlines",
  "slide4": "text"
}}

Do not include any other text or explanation."""

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that creates educational content for children."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            response_text = response.choices[0].message.content.strip()
            
            # Parse JSON response
            try:
                # Try to extract JSON from response
                if "```json" in response_text:
                    json_str = response_text.split("```json")[1].split("```")[0].strip()
                elif "```" in response_text:
                    json_str = response_text.split("```")[1].split("```")[0].strip()
                else:
                    json_str = response_text
                
                lesson_data = json.loads(json_str)
                
                logger.info("Lesson generated successfully from API")
                return {
                    "slide1": lesson_data.get("slide1", ""),
                    "slide2": lesson_data.get("slide2", ""),
                    "slide3": lesson_data.get("slide3", ""),
                    "slide4": lesson_data.get("slide4", ""),
                    "full_text": f"{lesson_data.get('slide1', '')}. {lesson_data.get('slide2', '')} {lesson_data.get('slide3', '')} {lesson_data.get('slide4', '')}"
                }
            except json.JSONDecodeError as e:
                logger.warning(f"Failed to parse JSON response: {e}")
                raise
                
        except Exception as e:
            logger.error(f"API generation failed: {e}")
            
            # Generate simple fallback content
            logger.info("Generating simple fallback content")
            return {
                "slide1": f"Learning {subtopic}",
                "slide2": f"Let's learn about {subtopic}. It's an important concept.",
                "slide3": f"Example 1\nExample 2\nExample 3",
                "slide4": f"Can you think about {subtopic}?",
                "full_text": f"Learning {subtopic}. Let's learn about {subtopic}. It's an important concept. Example 1, Example 2, Example 3. Can you think about {subtopic}?"
            }

    def generate_batch_topics(self, count: int = 200) -> list:
        """
        Generate a batch of topics
        
        Args:
            count: Number of topics to generate
            
        Returns:
            List of topic dictionaries
        """
        logger.info(f"Generating {count} topics...")
        
        categories = [
            "English Basics", "Math Basics", "Early Reading", "Writing Practice",
            "Good Manners", "Good Character", "Daily Etiquette", "Moral Stories",
            "Thinking Skills", "Problem Solving", "Time & Routine", "Colors & Shapes",
            "Numbers in Daily Life", "Safety Basics", "Self-Care", "Organization",
            "Emotions", "Good Deeds", "Islamic Manners", "General Knowledge"
        ]
        
        topics = []
        topic_id = 1
        
        for category in categories:
            # Generate topics for each category
            for i in range(count // len(categories)):
                topics.append({
                    "id": topic_id,
                    "category": category,
                    "main_topic": f"Topic {i+1}",
                    "subtopic": f"Lesson {i+1}",
                    "status": "unused"
                })
                topic_id += 1
        
        logger.info(f"Generated {len(topics)} topics")
        return topics
