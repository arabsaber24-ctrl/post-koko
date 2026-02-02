"""
Video Producer for Kids Educational Content
Creates vertical 9:16 videos with slides and male voice narration
"""

import os
import asyncio
import logging
import glob
from typing import Dict, List
from PIL import Image, ImageDraw, ImageFont
import textwrap
import edge_tts
from moviepy import ImageClip, AudioFileClip, concatenate_videoclips

logger = logging.getLogger(__name__)


class VideoProducer:
    def __init__(self, output_dir="temp_assets"):
        self.output_dir = output_dir
        self.width = 1080
        self.height = 1920
        
        # Color scheme
        self.bg_color = (30, 30, 30)  # Dark background
        self.text_color = (255, 255, 255)  # White text
        self.accent_color = (255, 204, 0)  # Yellow for titles
        
        # Margins and spacing
        self.margin = 120  # Safe margin
        self.line_spacing = 50
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Find available font
        self.font_path = self._find_font()
        
        # Male voice for narration
        self.male_voice = os.getenv("MALE_VOICE", "en-US-GuyNeural")
        
        logger.info(f"VideoProducer initialized with voice: {self.male_voice}")

    def _find_font(self) -> str:
        """Find an available TrueType font"""
        # Try common font paths
        font_paths = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
            "/System/Library/Fonts/Helvetica.ttc",
            "C:\\Windows\\Fonts\\arial.ttf"
        ]
        
        for path in font_paths:
            if os.path.exists(path):
                logger.info(f"Using font: {path}")
                return path
        
        # Fallback: find any TTF font
        fonts = glob.glob("/usr/share/fonts/**/*.ttf", recursive=True)
        if fonts:
            logger.info(f"Using fallback font: {fonts[0]}")
            return fonts[0]
        
        logger.warning("No TrueType font found, using default")
        return None

    async def generate_audio(self, text: str, filename: str) -> str:
        """
        Generate audio using Edge-TTS with male voice
        
        Args:
            text: Text to convert to speech
            filename: Output filename
            
        Returns:
            Path to generated audio file
        """
        communicate = edge_tts.Communicate(text, self.male_voice, rate="-10%")
        path = os.path.join(self.output_dir, filename)
        await communicate.save(path)
        logger.info(f"Audio generated: {filename}")
        return path

    def create_slide_image(self, text: str, filename: str, is_title: bool = False) -> str:
        """
        Create a slide image with text
        
        Args:
            text: Text to display on slide
            filename: Output filename
            is_title: Whether this is a title slide (larger font)
            
        Returns:
            Path to generated image
        """
        # Create image
        img = Image.new('RGB', (self.width, self.height), color=self.bg_color)
        draw = ImageDraw.Draw(img)
        
        # Font sizes
        title_size = 110
        body_size = 75
        font_size = title_size if is_title else body_size
        
        # Load font
        try:
            font = ImageFont.truetype(self.font_path, font_size)
        except:
            font = ImageFont.load_default()
            logger.warning("Using default font")
        
        # Calculate max width for text
        max_width = self.width - (2 * self.margin)
        
        # Wrap text
        lines = []
        for line in text.split('\n'):
            if line.strip():
                # Wrap each line
                wrapped = textwrap.wrap(line, width=20 if is_title else 25)
                lines.extend(wrapped)
            else:
                lines.append("")  # Preserve empty lines
        
        # Calculate total height
        total_height = 0
        line_heights = []
        for line in lines:
            if line:
                bbox = draw.textbbox((0, 0), line, font=font)
                h = bbox[3] - bbox[1]
            else:
                h = font_size // 2  # Empty line spacing
            line_heights.append(h)
            total_height += h
        
        total_height += (len(lines) - 1) * self.line_spacing
        
        # Start Y position (centered vertically)
        current_y = (self.height - total_height) // 2
        
        # Draw each line
        color = self.accent_color if is_title else self.text_color
        for line, h in zip(lines, line_heights):
            if line:
                bbox = draw.textbbox((0, 0), line, font=font)
                w = bbox[2] - bbox[0]
                x = (self.width - w) // 2  # Center horizontally
                draw.text((x, current_y), line, font=font, fill=color)
            current_y += h + self.line_spacing
        
        # Save image
        path = os.path.join(self.output_dir, filename)
        img.save(path)
        logger.info(f"Slide image created: {filename}")
        return path

    def create_video(self, lesson_data: Dict, topic_data: Dict, output_filename: str = "final_video.mp4") -> str:
        """
        Create complete video from lesson data
        
        Args:
            lesson_data: Dictionary with slide1, slide2, slide3, slide4
            topic_data: Dictionary with category, main_topic, subtopic
            output_filename: Name of output video file
            
        Returns:
            Path to generated video file
        """
        logger.info("Starting video creation...")
        
        slides = ['slide1', 'slide2', 'slide3', 'slide4']
        clips = []
        
        try:
            for i, key in enumerate(slides):
                text = lesson_data[key]
                is_title = (i == 0)
                
                # Create slide image
                img_filename = f"slide_{i}.png"
                img_path = self.create_slide_image(text, img_filename, is_title=is_title)
                
                # Generate audio for this slide
                audio_filename = f"audio_{i}.mp3"
                loop = asyncio.get_event_loop()
                audio_path = loop.run_until_complete(self.generate_audio(text, audio_filename))
                
                # Load audio to get duration
                audio_clip = AudioFileClip(audio_path)
                duration = audio_clip.duration + 1.0  # Add 1 second buffer
                
                # Create video clip
                img_clip = ImageClip(img_path).with_duration(duration).with_audio(audio_clip)
                clips.append(img_clip)
                
                logger.info(f"Slide {i+1}/4 completed (duration: {duration:.1f}s)")
            
            # Concatenate all clips
            final_clip = concatenate_videoclips(clips, method="compose")
            
            # Write video file
            output_path = os.path.join(self.output_dir, output_filename)
            final_clip.write_videofile(
                output_path,
                fps=24,
                codec="libx264",
                audio_codec="aac",
                preset="medium",
                logger=None  # Suppress moviepy verbose output
            )
            
            # Close clips to free resources
            for clip in clips:
                clip.close()
            final_clip.close()
            
            logger.info(f"Video created successfully: {output_filename}")
            return output_path
            
        except Exception as e:
            logger.error(f"Failed to create video: {e}")
            raise

    def cleanup_temp_files(self, keep_final_video: bool = True):
        """
        Clean up temporary files
        
        Args:
            keep_final_video: Whether to keep the final video file
        """
        logger.info("Cleaning up temporary files...")
        
        patterns = ["slide_*.png", "audio_*.mp3"]
        if not keep_final_video:
            patterns.append("*.mp4")
        
        deleted_count = 0
        for pattern in patterns:
            files = glob.glob(os.path.join(self.output_dir, pattern))
            for file in files:
                try:
                    os.remove(file)
                    deleted_count += 1
                except Exception as e:
                    logger.warning(f"Could not delete {file}: {e}")
        
        logger.info(f"Cleaned up {deleted_count} temporary files")

    def get_video_duration(self, video_path: str) -> float:
        """
        Get duration of a video file
        
        Args:
            video_path: Path to video file
            
        Returns:
            Duration in seconds
        """
        try:
            from moviepy import VideoFileClip
            clip = VideoFileClip(video_path)
            duration = clip.duration
            clip.close()
            return duration
        except Exception as e:
            logger.error(f"Could not get video duration: {e}")
            return 0.0
