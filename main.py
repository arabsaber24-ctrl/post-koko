"""
Main Orchestrator for Kids Educational Content Automation
Coordinates all modules and handles scheduling
"""

import os
import sys
import time
import logging
import schedule
from datetime import datetime
from dotenv import load_dotenv

from db_manager import DBManager
from topic_manager import TopicManager
from content_generator import ContentGenerator
from video_producer import VideoProducer
from youtube_publisher import YouTubePublisher

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/app.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class KidsEduAutomation:
    def __init__(self):
        """Initialize all modules"""
        logger.info("=" * 80)
        logger.info("Initializing Kids Educational Content Automation System")
        logger.info("=" * 80)
        
        self.db = DBManager()
        self.topic_manager = TopicManager()
        self.content_generator = ContentGenerator()
        self.video_producer = VideoProducer()
        self.youtube = YouTubePublisher()
        
        # Configuration
        self.min_topics_threshold = 10  # Generate new topics when below this
        self.topic_batch_size = 200
        
        logger.info("All modules initialized successfully")

    def ensure_topics_available(self):
        """Ensure sufficient topics are available"""
        unused_count = self.db.get_unused_count()
        total_count = self.db.get_total_count()
        
        logger.info(f"Topics status: {unused_count} unused, {total_count} total")
        
        if unused_count == 0:
            logger.info("No unused topics available")
            
            if total_count > 0:
                logger.info("Recycling existing topics with new content generation")
                self.db.reset_all_topics()
                unused_count = self.db.get_unused_count()
                logger.info(f"Reset {unused_count} topics to unused status")
            else:
                logger.info("No topics in database, generating initial batch")
                self._generate_and_store_topics()
        
        elif unused_count < self.min_topics_threshold:
            logger.info(f"Low topic count ({unused_count}), generating more topics")
            self._generate_and_store_topics()

    def _generate_and_store_topics(self):
        """Generate topics and store in database"""
        try:
            logger.info(f"Generating {self.topic_batch_size} new topics...")
            
            # Generate topics in batches
            topics = self.topic_manager.generate_topics_batch(
                total_count=self.topic_batch_size,
                batch_size=50
            )
            
            if not topics:
                logger.error("Failed to generate topics")
                return False
            
            # Store in database
            added_count = self.db.add_topics(topics)
            logger.info(f"Successfully added {added_count} topics to database")
            
            self.db.add_log("INFO", f"Generated and stored {added_count} new topics")
            return True
            
        except Exception as e:
            logger.error(f"Failed to generate and store topics: {e}")
            self.db.add_log("ERROR", f"Topic generation failed: {e}")
            return False

    def create_and_upload_video(self):
        """Main workflow: create video and upload to YouTube"""
        logger.info("\n" + "=" * 80)
        logger.info("Starting video creation and upload workflow")
        logger.info("=" * 80)
        
        try:
            # Step 1: Ensure topics are available
            self.ensure_topics_available()
            
            # Step 2: Get next topic
            topic_data = self.db.get_next_topic()
            if not topic_data:
                logger.error("No topics available after ensuring availability")
                return False
            
            logger.info(f"Selected topic: {topic_data['category']} - {topic_data['main_topic']} - {topic_data['subtopic']}")
            
            # Step 3: Generate lesson content
            logger.info("Generating lesson content...")
            try:
                lesson_data = self.content_generator.generate_lesson(topic_data)
                logger.info("Lesson content generated successfully")
            except Exception as e:
                logger.error(f"Failed to generate lesson: {e}")
                self.db.add_log("ERROR", f"Lesson generation failed for topic {topic_data['id']}: {e}")
                return False
            
            # Step 4: Create video
            logger.info("Creating video...")
            try:
                video_filename = f"video_{topic_data['id']}_{int(time.time())}.mp4"
                video_path = self.video_producer.create_video(
                    lesson_data,
                    topic_data,
                    output_filename=video_filename
                )
                
                duration = self.video_producer.get_video_duration(video_path)
                logger.info(f"Video created successfully: {video_path} (duration: {duration:.1f}s)")
                
                if duration > 60:
                    logger.warning(f"Video duration ({duration:.1f}s) exceeds 60s limit for Shorts")
                
            except Exception as e:
                logger.error(f"Failed to create video: {e}")
                self.db.add_log("ERROR", f"Video creation failed for topic {topic_data['id']}: {e}")
                return False
            
            # Step 5: Authenticate with YouTube
            logger.info("Authenticating with YouTube...")
            if not self.youtube.authenticate():
                logger.error("YouTube authentication failed")
                self.db.add_log("ERROR", "YouTube authentication failed")
                return False
            
            # Step 6: Generate metadata and upload
            logger.info("Uploading to YouTube...")
            try:
                metadata = self.youtube.generate_video_metadata(topic_data)
                
                video_id = self.youtube.upload_video_with_retry(
                    video_path=video_path,
                    title=metadata['title'],
                    description=metadata['description'],
                    tags=metadata['tags'],
                    category_id="27",  # Education
                    privacy_status="public",
                    made_for_kids=True,
                    max_retries=5
                )
                
                if not video_id:
                    logger.error("Failed to upload video to YouTube")
                    self.db.add_log("ERROR", f"YouTube upload failed for topic {topic_data['id']}")
                    return False
                
                logger.info(f"Video uploaded successfully! Video ID: {video_id}")
                logger.info(f"Shorts URL: https://www.youtube.com/shorts/{video_id}")
                
            except Exception as e:
                logger.error(f"Failed to upload video: {e}")
                self.db.add_log("ERROR", f"YouTube upload error for topic {topic_data['id']}: {e}")
                return False
            
            # Step 7: Mark topic as used and log upload
            self.db.mark_topic_used(topic_data['id'])
            self.db.log_upload(topic_data['id'], metadata['title'], video_id)
            self.db.add_log("INFO", f"Successfully uploaded video {video_id} for topic {topic_data['id']}")
            
            # Step 8: Cleanup temporary files
            logger.info("Cleaning up temporary files...")
            try:
                self.video_producer.cleanup_temp_files(keep_final_video=False)
                if os.path.exists(video_path):
                    os.remove(video_path)
                logger.info("Cleanup completed")
            except Exception as e:
                logger.warning(f"Cleanup error: {e}")
            
            logger.info("=" * 80)
            logger.info("Workflow completed successfully!")
            logger.info("=" * 80 + "\n")
            return True
            
        except Exception as e:
            logger.error(f"Unexpected error in workflow: {e}")
            self.db.add_log("ERROR", f"Workflow error: {e}")
            return False

    def run_once(self):
        """Run the workflow once"""
        logger.info("Running workflow once...")
        success = self.create_and_upload_video()
        if success:
            logger.info("Single run completed successfully")
        else:
            logger.error("Single run failed")
        return success

    def run_scheduled(self):
        """Run with scheduling (2 posts per day)"""
        logger.info("Starting scheduled mode (2 posts per day)")
        
        # Get post times from environment or use defaults
        post_times = os.getenv("POST_TIMES", "08:00,20:00").split(",")
        
        for post_time in post_times:
            schedule.every().day.at(post_time.strip()).do(self.create_and_upload_video)
            logger.info(f"Scheduled daily post at {post_time.strip()}")
        
        logger.info("Scheduler started. Press Ctrl+C to stop.")
        
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
        except KeyboardInterrupt:
            logger.info("Scheduler stopped by user")

    def run_continuous(self, interval_hours: int = 12):
        """Run continuously with fixed interval"""
        logger.info(f"Starting continuous mode (every {interval_hours} hours)")
        
        try:
            while True:
                self.create_and_upload_video()
                
                logger.info(f"Waiting {interval_hours} hours until next run...")
                time.sleep(interval_hours * 3600)
                
        except KeyboardInterrupt:
            logger.info("Continuous mode stopped by user")


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Kids Educational Content Automation")
    parser.add_argument(
        "--mode",
        choices=["once", "scheduled", "continuous"],
        default="once",
        help="Execution mode: once, scheduled (2x daily), or continuous"
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=12,
        help="Interval in hours for continuous mode (default: 12)"
    )
    
    args = parser.parse_args()
    
    # Create automation instance
    automation = KidsEduAutomation()
    
    # Run based on mode
    if args.mode == "once":
        automation.run_once()
    elif args.mode == "scheduled":
        automation.run_scheduled()
    elif args.mode == "continuous":
        automation.run_continuous(interval_hours=args.interval)


if __name__ == "__main__":
    main()
