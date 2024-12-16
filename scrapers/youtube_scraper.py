from typing import Dict, List
import googleapiclient.discovery
from .base_scraper import BaseScraper
from config import YOUTUBE_API_KEY
import re
import logging

class YouTubeScraper(BaseScraper):
    def __init__(self):
        super().__init__()
        self.setup_api()
    
    def setup_api(self):
        """Initialize YouTube API client"""
        try:
            self.youtube = googleapiclient.discovery.build(
                "youtube", "v3", 
                developerKey=YOUTUBE_API_KEY,
                cache_discovery=False
            )
        except Exception as e:
            self.logger.error(f"Failed to initialize YouTube API: {str(e)}")
            raise
    
    def extract_video_id(self, url: str) -> str:
        """Extract video ID from various YouTube URL formats"""
        patterns = [
            r'(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/|youtube\.com\/v\/)([^&\n?#]+)',
            r'youtube\.com\/watch.*[\&\?]v=([^&\n?#]+)',
            r'youtube\.com\/shorts\/([^&\n?#]+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        return None
    
    def get_video_info(self, video_id: str) -> Dict:
        """Get basic information about the video"""
        try:
            request = self.youtube.videos().list(
                part="snippet,statistics",
                id=video_id
            )
            response = request.execute()
            
            if response["items"]:
                video = response["items"][0]
                return {
                    "title": video["snippet"]["title"],
                    "channel": video["snippet"]["channelTitle"],
                    "view_count": video["statistics"]["viewCount"],
                    "comment_count": video["statistics"].get("commentCount", "0")
                }
        except Exception as e:
            self.logger.error(f"Error fetching video info for {video_id}: {str(e)}")
        
        return None
    
    def get_video_comments(self, video_id: str, max_comments: int = 100) -> List[Dict]:
        """Fetch comments from a specific YouTube video"""
        comments = []
        try:
            # First get video info
            video_info = self.get_video_info(video_id)
            if not video_info:
                self.logger.error(f"Could not fetch video info for {video_id}")
                return comments
            
            # Check if comments are enabled
            if int(video_info["comment_count"]) == 0:
                self.logger.warning(f"Comments are disabled for video {video_id}")
                return comments
            
            request = self.youtube.commentThreads().list(
                part="snippet",
                videoId=video_id,
                maxResults=min(100, max_comments)  # YouTube API limit is 100 per request
            )
            
            while request and len(comments) < max_comments:
                response = request.execute()
                
                for item in response["items"]:
                    comment = item["snippet"]["topLevelComment"]["snippet"]
                    
                    # Extract potential lead information
                    text = comment["textDisplay"]
                    author = comment["authorDisplayName"]
                    channel_url = comment.get("authorChannelUrl", "")
                    
                    lead_data = {
                        "name": author,
                        "email": self.extract_email(text),
                        "phone": self.extract_phone(text),
                        "website": self.extract_website(text) or channel_url,
                        "comment": text,
                        "video_id": video_id,
                        "video_title": video_info["title"],
                        "channel": video_info["channel"],
                        "platform": "YouTube",
                        "type": "Video Comment"
                    }
                    
                    if self.validate_data(lead_data):
                        comments.append(self.format_lead_data(lead_data))
                    
                    if len(comments) >= max_comments:
                        break
                
                # Get the next page of comments
                if "nextPageToken" in response and len(comments) < max_comments:
                    request = self.youtube.commentThreads().list(
                        part="snippet",
                        videoId=video_id,
                        pageToken=response["nextPageToken"],
                        maxResults=min(100, max_comments - len(comments))
                    )
                else:
                    break
                    
        except Exception as e:
            self.logger.error(f"Error fetching comments for video {video_id}: {str(e)}")
        
        return comments
    
    def scrape(self, video_urls: List[str], max_comments_per_video: int = 100) -> List[Dict]:
        """Scrape comments from multiple YouTube videos"""
        all_leads = []
        
        for url in video_urls:
            try:
                # Extract video ID from URL
                video_id = self.extract_video_id(url)
                if not video_id:
                    self.logger.error(f"Could not extract video ID from URL: {url}")
                    continue
                
                self.logger.info(f"Scraping comments from video: {url}")
                leads = self.get_video_comments(video_id, max_comments_per_video)
                self.logger.info(f"Found {len(leads)} potential leads in video {video_id}")
                
                all_leads.extend(leads)
                
            except Exception as e:
                self.logger.error(f"Error processing video URL {url}: {str(e)}")
                continue
            
        return all_leads
