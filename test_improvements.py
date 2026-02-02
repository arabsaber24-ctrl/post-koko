import os
import logging
from content_generator import ContentGenerator
from video_producer import VideoProducer

# Setup logging to console
logging.basicConfig(level=logging.INFO)

def test():
    print("--- Testing Improvements ---")
    
    # 1. Test Content Generation
    print("\n1. Testing Content Generation (Kid-friendly + AI Improvement)...")
    cg = ContentGenerator()
    topic_data = {
        'category': 'Colors',
        'main_topic': 'Red',
        'subtopic': 'The Color Red'
    }
    lesson = cg.generate_lesson(topic_data)
    print(f"Generated Lesson Content:\n{lesson}")
    
    # 2. Test Audio Generation
    print("\n2. Testing Natural Male Voice (OpenAI TTS)...")
    vp = VideoProducer(output_dir="test_assets")
    audio_path = vp.generate_audio(lesson['full_text'], "test_audio.mp3")
    print(f"Audio generated at: {audio_path}")
    
    # 3. Test Slide Creation
    print("\n3. Testing Simplified Slide Design...")
    slide_path = vp.create_slide_image(lesson['slide2'], "test_slide.png", is_title=False, slide_index=1)
    print(f"Slide image generated at: {slide_path}")
    
    print("\n--- Test Completed Successfully ---")

if __name__ == "__main__":
    test()
