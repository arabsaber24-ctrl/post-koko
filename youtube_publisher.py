"""
YouTube Publisher for Kids Educational Content
Handles OAuth2 authentication and video uploads to YouTube
Uses saved token for automatic uploads without manual intervention
"""

import os
import logging
import pickle
from typing import Dict, Optional
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError

logger = logging.getLogger(__name__)


class YouTubePublisher:
    def __init__(self, credentials_file="client_secrets.json", token_file="youtube_token.pickle"):
        """
        Initialize YouTube Publisher
        
        Args:
            credentials_file: Path to OAuth2 credentials JSON file
            token_file: Path to save/load authentication token
        """
        self.credentials_file = credentials_file
        self.token_file = token_file
        self.youtube = None
        
        # OAuth2 scope for uploading videos
        self.scopes = ["https://www.googleapis.com/auth/youtube.upload"]
        
        logger.info("YouTubePublisher initialized")

    def authenticate(self):
        """
        Authenticate with YouTube API using OAuth2
        Uses saved token if available, otherwise creates new one
        
        Returns:
            True if authentication successful, False otherwise
        """
        credentials = None
        
        # Load existing token if available
        if os.path.exists(self.token_file):
            try:
                with open(self.token_file, 'rb') as token:
                    credentials = pickle.load(token)
                logger.info("Loaded existing credentials from token file")
                
                # Refresh if expired
                if credentials.expired and credentials.refresh_token:
                    try:
                        credentials.refresh(Request())
                        logger.info("Refreshed expired credentials")
                        
                        # Save refreshed token
                        with open(self.token_file, 'wb') as token:
                            pickle.dump(credentials, token)
                        logger.info("Saved refreshed credentials")
                    except Exception as e:
                        logger.error(f"Could not refresh credentials: {e}")
                        credentials = None
                
                if credentials and credentials.valid:
                    # Build YouTube service
                    try:
                        self.youtube = build('youtube', 'v3', credentials=credentials)
                        logger.info("YouTube API service built successfully")
                        return True
                    except Exception as e:
                        logger.error(f"Could not build YouTube service: {e}")
                        return False
                        
            except Exception as e:
                logger.warning(f"Could not load token file: {e}")
        
        # No valid token found
        logger.error(f"No valid YouTube token found in {self.token_file}")
        logger.error("Please run: python3 get_youtube_token.py")
        logger.error("This will save your YouTube token for automatic uploads.")
        return False

    def upload_video(
        self,
        video_path: str,
        title: str,
        description: str,
        tags: list,
        category_id: str = "27",
        privacy_status: str = "public",
        made_for_kids: bool = True
    ) -> Optional[str]:
        """
        Upload video to YouTube
        
        Args:
            video_path: Path to video file
            title: Video title
            description: Video description
            tags: List of tags
            category_id: YouTube category ID (27 = Education)
            privacy_status: "public", "private", or "unlisted"
            made_for_kids: Whether video is made for kids (COPPA compliance)
            
        Returns:
            YouTube video ID if successful, None otherwise
        """
        if not self.youtube:
            logger.error("Not authenticated. Call authenticate() first.")
            return None
        
        if not os.path.exists(video_path):
            logger.error(f"Video file not found: {video_path}")
            return None
        
        logger.info(f"Uploading video: {title}")
        
        # Build request body
        body = {
            "snippet": {
                "title": title,
                "description": description,
                "tags": tags,
                "categoryId": category_id
            },
            "status": {
                "privacyStatus": privacy_status,
                "selfDeclaredMadeForKids": made_for_kids
            }
        }
        
        # Create media upload
        media = MediaFileUpload(
            video_path,
            chunksize=-1,
            resumable=True
        )
        
        try:
            # Execute upload request
            request = self.youtube.videos().insert(
                part=",".join(body.keys()),
                body=body,
                media_body=media
            )
            
            response = None
            while response is None:
                status, response = request.next_chunk()
                if status:
                    progress = int(status.progress() * 100)
                    logger.info(f"Upload progress: {progress}%")
            
            video_id = response.get('id')
            logger.info(f"Video uploaded successfully! Video ID: {video_id}")
            logger.info(f"Video URL: https://www.youtube.com/watch?v={video_id}")
            logger.info(f"Shorts URL: https://www.youtube.com/shorts/{video_id}")
            
            return video_id
            
        except HttpError as e:
            logger.error(f"HTTP error during upload: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error during upload: {e}")
            return None

    def upload_video_with_retry(
        self,
        video_path: str,
        title: str,
        description: str,
        tags: list,
        max_retries: int = 3,
        **kwargs
    ) -> Optional[str]:
        """
        Upload video with retry logic
        
        Args:
            video_path: Path to video file
            title: Video title
            description: Video description
            tags: List of tags
            max_retries: Maximum number of retry attempts
            **kwargs: Additional arguments for upload_video
            
        Returns:
            YouTube video ID if successful, None otherwise
        """
        for attempt in range(max_retries):
            try:
                video_id = self.upload_video(
                    video_path, title, description, tags, **kwargs
                )
                if video_id:
                    return video_id
                logger.warning(f"Upload attempt {attempt + 1}/{max_retries} failed")
            except Exception as e:
                logger.error(f"Upload attempt {attempt + 1}/{max_retries} error: {e}")
            
            if attempt < max_retries - 1:
                logger.info("Retrying upload...")
        
        logger.error("All upload attempts failed")
        return None

    def generate_video_metadata(self, topic_data: Dict) -> Dict:
        """
        Generate video metadata from topic data
        
        Args:
            topic_data: Dictionary with category, main_topic, subtopic
            
        Returns:
            Dictionary with title, description, tags
        """
        category = topic_data['category']
        main_topic = topic_data['main_topic']
        subtopic = topic_data['subtopic']
        
        # Generate title
        title = f"{main_topic}: {subtopic} | Kids Learning #Shorts"
        
        # Generate description
        description = f"""Learn about {subtopic} in this short educational video for kids!

Category: {category}
Topic: {main_topic}

Perfect for young learners to understand important concepts in a fun and engaging way.

#Shorts #KidsEducation #Learning #Educational #Kids #Children
"""
        
        # Generate tags
        tags = [
            "kids education",
            "learning for kids",
            "educational video",
            category.lower(),
            main_topic.lower(),
            "shorts",
            "youtube shorts",
            "kids learning",
            "children education"
        ]
        
        return {
            "title": title[:100],
            "description": description[:5000],
            "tags": tags[:15]
        }
