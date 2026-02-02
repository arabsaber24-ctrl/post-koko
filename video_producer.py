"""
Video Producer for Kids Educational Content
Creates vertical 9:16 videos with beautiful slides and natural male voice narration
"""

import os
import logging
import glob
import subprocess
from typing import Dict, List
from PIL import Image, ImageDraw, ImageFont
import textwrap
from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips

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
        self.text_color = (255, 255, 255)
        
        self.margin = 100
        self.line_spacing = 80
        
        os.makedirs(output_dir, exist_ok=True)
        self.font_path = self._find_font()
        
        logger.info("VideoProducer initialized with gTTS + ffmpeg pitch shift for male voice")

    def _find_font(self) -> str:
        font_paths = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
            "/System/Library/Fonts/Helvetica.ttc",
            "C:\\Windows\\Fonts\\arial.ttf"
        ]
        for path in font_paths:
            if os.path.exists(path): return path
        fonts = glob.glob("/usr/share/fonts/**/*.ttf", recursive=True)
        return fonts[0] if fonts else None

    def generate_audio(self, text: str, filename: str) -> str:
        """
        Generate natural male voice using gTTS and ffmpeg pitch shifting
        """
        try:
            path = os.path.join(self.output_dir, filename)
            temp_female = os.path.join(self.output_dir, "temp_female.mp3")
            
            # 1. Generate female voice with gTTS
            subprocess.run(["gtts-cli", text, "--output", temp_female], check=True, capture_output=True)
            
            # 2. Shift pitch to male using ffmpeg
            # asetrate lowers pitch, atempo restores speed
            cmd = [
                "ffmpeg", "-i", temp_female, 
                "-af", "asetrate=24000*0.8,atempo=1.25", 
                path, "-y"
            ]
            subprocess.run(cmd, check=True, capture_output=True)
            
            if os.path.exists(temp_female):
                os.remove(temp_female)
                
            logger.info(f"Audio generated (Male Voice): {filename}")
            return path
        except Exception as e:
            logger.error(f"Error generating audio: {e}")
            import wave
            path = os.path.join(self.output_dir, filename)
            with wave.open(path, 'wb') as wav_file:
                wav_file.setnchannels(1); wav_file.setsampwidth(2); wav_file.setframerate(44100)
                wav_file.writeframes(b'\x00' * 44100 * 2)
            return path

    def create_slide_image(self, text: str, filename: str, is_title: bool = False, slide_index: int = 0) -> str:
        bg_color = self.bg_colors[slide_index % len(self.bg_colors)]
        accent_color = self.accent_colors[slide_index % len(self.accent_colors)]
        img = Image.new('RGB', (self.width, self.height), color=bg_color)
        draw = ImageDraw.Draw(img)
        
        # Decoration
        circle_size = 300
        draw.ellipse([(self.width - circle_size - 50, -50), (self.width + 50, circle_size - 50)], fill=accent_color)
        draw.ellipse([(50 - circle_size, self.height - circle_size + 50), (50, self.height + 50)], fill=accent_color)
        
        try:
            font = ImageFont.truetype(self.font_path, 150 if is_title else 100)
        except:
            font = ImageFont.load_default()
        
        lines = []
        for line in text.split('\n'):
            if line.strip():
                wrapped = textwrap.wrap(line, width=12 if is_title else 15)
                lines.extend(wrapped)
            else:
                lines.append("")
        
        total_height = sum(draw.textbbox((0, 0), l, font=font)[3] - draw.textbbox((0, 0), l, font=font)[1] if l else 60 for l in lines)
        total_height += (len(lines) - 1) * self.line_spacing
        current_y = (self.height - total_height) // 2
        
        for line in lines:
            if line:
                bbox = draw.textbbox((0, 0), line, font=font)
                w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
                x = (self.width - w) // 2
                draw.text((x + 5, current_y + 5), line, font=font, fill=(0, 0, 0, 150))
                draw.text((x, current_y), line, font=font, fill=accent_color if is_title else self.text_color)
                current_y += h + self.line_spacing
            else:
                current_y += 60 + self.line_spacing
        
        draw.rectangle([(0, self.height - 20), (self.width, self.height)], fill=accent_color)
        img_path = os.path.join(self.output_dir, filename)
        img.save(img_path)
        return img_path

    def create_video(self, lesson_data: Dict, topic_data: Dict, output_filename: str) -> str:
        logger.info("Starting video creation...")
        slides = ['slide1', 'slide2', 'slide3', 'slide4']
        clips = []
        try:
            for i, key in enumerate(slides):
                text = lesson_data[key]
                img_path = self.create_slide_image(text, f"slide_{i}.png", is_title=(i == 0), slide_index=i)
                audio_path = self.generate_audio(text, f"audio_{i}.mp3")
                audio_clip = AudioFileClip(audio_path)
                duration = audio_clip.duration + 1.0
                img_clip = ImageClip(img_path).set_duration(duration).set_audio(audio_clip)
                clips.append(img_clip)
            
            final_clip = concatenate_videoclips(clips, method="compose")
            output_path = os.path.join(self.output_dir, output_filename)
            final_clip.write_videofile(output_path, fps=24, codec="libx264", audio_codec="aac", preset="medium", logger=None)
            for clip in clips: clip.close()
            final_clip.close()
            return output_path
        except Exception as e:
            logger.error(f"Failed to create video: {e}"); raise

    def cleanup_temp_files(self, keep_final_video: bool = True):
        patterns = ["slide_*.png", "audio_*.mp3", "temp_female.mp3"]
        if not keep_final_video: patterns.append("*.mp4")
        for pattern in patterns:
            for f in glob.glob(os.path.join(self.output_dir, pattern)):
                try: os.remove(f)
                except: pass

    def get_video_duration(self, video_path: str) -> float:
        try:
            from moviepy.editor import VideoFileClip
            clip = VideoFileClip(video_path); d = clip.duration; clip.close(); return d
        except: return 0.0
