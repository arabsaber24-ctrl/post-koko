"""
Video Producer for Kids Educational Content
Creates vertical 9:16 videos with beautiful slides and male voice narration
"""

import os
import asyncio
import logging
import glob
from typing import Dict, List
from PIL import Image, ImageDraw, ImageFont
import textwrap
import pyttsx3
from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips, CompositeVideoClip

logger = logging.getLogger(__name__)


class VideoProducer:
    def __init__(self, output_dir="temp_assets"):
        self.output_dir = output_dir
        self.width = 1080
        self.height = 1920
        
        # Modern color scheme - vibrant and kid-friendly
        self.bg_colors = [
            (25, 45, 85),      # Deep blue
            (45, 85, 65),      # Forest green
            (95, 35, 65),      # Purple
            (85, 55, 25),      # Brown
        ]
        self.accent_colors = [
            (255, 200, 0),     # Golden yellow
            (0, 255, 150),     # Bright cyan
            (255, 100, 150),   # Pink
            (255, 150, 0),     # Orange
        ]
        self.text_color = (255, 255, 255)  # White text
        
        # Margins and spacing
        self.margin = 80
        self.line_spacing = 60
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Find available font
        self.font_path = self._find_font()
        
        # Initialize pyttsx3 for male voice
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', 150)  # Slower for kids
        self._setup_male_voice()
        
        logger.info("VideoProducer initialized with pyttsx3 male voice")

    def _setup_male_voice(self):
        """Setup male voice for pyttsx3"""
        try:
            voices = self.engine.getProperty('voices')
            # Find male voice
            for voice in voices:
                if 'male' in voice.name.lower() or 'david' in voice.name.lower():
                    self.engine.setProperty('voice', voice.id)
                    logger.info(f"Using voice: {voice.name}")
                    return
            # If no male voice found, use first available
            if voices:
                self.engine.setProperty('voice', voices[0].id)
                logger.info(f"Using default voice: {voices[0].name}")
        except Exception as e:
            logger.warning(f"Could not set voice: {e}")

    def _find_font(self) -> str:
        """Find an available TrueType font"""
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
        
        fonts = glob.glob("/usr/share/fonts/**/*.ttf", recursive=True)
        if fonts:
            logger.info(f"Using fallback font: {fonts[0]}")
            return fonts[0]
        
        logger.warning("No TrueType font found, using default")
        return None

    def generate_audio(self, text: str, filename: str) -> str:
        """
        Generate audio using pyttsx3 with male voice
        
        Args:
            text: Text to convert to speech
            filename: Output filename
            
        Returns:
            Path to generated audio file
        """
        try:
            path = os.path.join(self.output_dir, filename)
            self.engine.save_to_file(text, path)
            self.engine.runAndWait()
            logger.info(f"Audio generated: {filename}")
            return path
        except Exception as e:
            logger.error(f"Error generating audio: {e}")
            # Create a silent audio file as fallback
            import wave
            path = os.path.join(self.output_dir, filename)
            with wave.open(path, 'wb') as wav_file:
                wav_file.setnchannels(1)
                wav_file.setsampwidth(2)
                wav_file.setframerate(44100)
                wav_file.writeframes(b'\x00' * 44100 * 2)
            return path

    def create_slide_image(self, text: str, filename: str, is_title: bool = False, slide_index: int = 0) -> str:
        """
        Create a beautiful slide image with enhanced design
        
        Args:
            text: Text to display on slide
            filename: Output filename
            is_title: Whether this is a title slide
            slide_index: Index of the slide for color variation
            
        Returns:
            Path to generated image
        """
        # Select colors based on slide index
        bg_color = self.bg_colors[slide_index % len(self.bg_colors)]
        accent_color = self.accent_colors[slide_index % len(self.accent_colors)]
        
        # Create image with gradient-like effect
        img = Image.new('RGB', (self.width, self.height), color=bg_color)
        draw = ImageDraw.Draw(img)
        
        # Add decorative elements for title slides
        if is_title:
            # Draw decorative circles/shapes
            circle_size = 200
            draw.ellipse(
                [(self.width - circle_size - 50, -50), 
                 (self.width + 50, circle_size - 50)],
                fill=accent_color,
                outline=accent_color
            )
            draw.ellipse(
                [(50 - circle_size, self.height - circle_size + 50), 
                 (50, self.height + 50)],
                fill=accent_color,
                outline=accent_color
            )
        
        # Load font
        try:
            if is_title:
                font = ImageFont.truetype(self.font_path, 120)
            else:
                font = ImageFont.truetype(self.font_path, 80)
        except:
            font = ImageFont.load_default()
            logger.warning("Using default font")
        
        # Wrap text
        max_width = self.width - (2 * self.margin)
        lines = []
        for line in text.split('\n'):
            if line.strip():
                wrapped = textwrap.wrap(line, width=15 if is_title else 20)
                lines.extend(wrapped)
            else:
                lines.append("")
        
        # Calculate total height
        total_height = 0
        line_heights = []
        for line in lines:
            if line:
                bbox = draw.textbbox((0, 0), line, font=font)
                h = bbox[3] - bbox[1]
            else:
                h = 60
            line_heights.append(h)
            total_height += h
        
        total_height += (len(lines) - 1) * self.line_spacing
        
        # Start Y position (centered vertically)
        current_y = (self.height - total_height) // 2
        
        # Draw each line with shadow effect
        for line, h in zip(lines, line_heights):
            if line:
                bbox = draw.textbbox((0, 0), line, font=font)
                w = bbox[2] - bbox[0]
                x = (self.width - w) // 2
                
                # Draw shadow
                shadow_offset = 3
                draw.text(
                    (x + shadow_offset, current_y + shadow_offset),
                    line,
                    font=font,
                    fill=(0, 0, 0, 100)
                )
                
                # Draw main text
                color = accent_color if is_title else self.text_color
                draw.text((x, current_y), line, font=font, fill=color)
            
            current_y += h + self.line_spacing
        
        # Add bottom decorative bar
        bar_height = 10
        draw.rectangle(
            [(0, self.height - bar_height), (self.width, self.height)],
            fill=accent_color
        )
        
        # Save image
        img_path = os.path.join(self.output_dir, filename)
        img.save(img_path)
        logger.info(f"Slide image created: {filename}")
        return img_path

    def create_video(self, lesson_data: Dict, topic_data: Dict, output_filename: str) -> str:
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
                img_path = self.create_slide_image(text, img_filename, is_title=is_title, slide_index=i)
                
                # Generate audio for this slide
                audio_filename = f"audio_{i}.mp3"
                audio_path = self.generate_audio(text, audio_filename)
                
                # Load audio to get duration
                audio_clip = AudioFileClip(audio_path)
                duration = audio_clip.duration + 1.0  # Add 1 second buffer
                
                # Create video clip
                img_clip = ImageClip(img_path).set_duration(duration).set_audio(audio_clip)
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
                logger=None
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

    def cleanup(self, keep_final_video: bool = True):
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
            from moviepy.editor import VideoFileClip
            clip = VideoFileClip(video_path)
            duration = clip.duration
            clip.close()
            return duration
        except Exception as e:
            logger.error(f"Could not get video duration: {e}")
            return 0.0
