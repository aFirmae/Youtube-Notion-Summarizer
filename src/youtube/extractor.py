from pytube import Playlist, YouTube
from youtube_transcript_api import YouTubeTranscriptApi
import re


def extract_video_id(url):
    # Extract video ID from various YouTube URL formats
    video_id_match = re.search(
        r"(?:v=|/videos/|embed/|youtu.be/|/v/|/e/|watch\?v=|&v=)([^#\&\?]*)", url
    )
    if video_id_match:
        return video_id_match.group(1)
    return None


def get_transcript(video_id):
    try:
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
        transcript = " ".join([item["text"] for item in transcript_list])
        return transcript
    except Exception as e:
        print(f"Error getting transcript for video {video_id}: {e}")
        return "Transcript unavailable"


def extract_video_info(video_url):
    """
    Extract information about a YouTube video including title, description, and transcript.

    Args:
        video_url (str): URL of the YouTube video

    Returns:
        dict: Dictionary containing video information
    """
    try:
        import re
        import os
        from googleapiclient.discovery import build

        # Extract video ID
        video_id = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11}).*", video_url)
        video_id = video_id.group(1) if video_id else None

        if not video_id:
            print(f"Could not extract video ID from URL: {video_url}")
            return {
                "title": "Unknown",
                "description": "",
                "transcript": "Video ID could not be extracted",
            }

        # Use YouTube API directly instead of PyTube
        youtube = build("youtube", "v3", developerKey=os.getenv("API_KEY_YOUTUBE"))

        request = youtube.videos().list(part="snippet", id=video_id)
        response = request.execute()

        if response["items"]:
            snippet = response["items"][0]["snippet"]
            title = snippet["title"]
            description = snippet["description"]
        else:
            title = f"Video {video_id} (unavailable)"
            description = "This video may have restricted access or is unavailable"

        # Try getting transcript
        transcript = "No transcript available"
        try:
            from youtube_transcript_api import YouTubeTranscriptApi

            transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
            transcript = " ".join([item["text"] for item in transcript_list])
        except Exception as t_err:
            print(f"Transcript error for {video_id}: {t_err}")

        return {"title": title, "description": description, "transcript": transcript}

    except Exception as e:
        print(f"Error extracting video info: {e}")
        return {
            "title": f'Video (ID: {video_id if "video_id" in locals() else "unknown"})',
            "description": "Unable to retrieve video information",
            "transcript": "No transcript available",
        }


def extract_playlist_info(playlist_url):
    try:
        # Print debug info
        print(f"Extracting info from playlist: {playlist_url}")

        # Special handling for playlist URLs
        if "list=" in playlist_url:
            playlist_id = playlist_url.split("list=")[1]
            if "&" in playlist_id:
                playlist_id = playlist_id.split("&")[0]
            playlist_url = f"https://www.youtube.com/playlist?list={playlist_id}"
            print(f"Using formatted playlist URL: {playlist_url}")

        # Create playlist instance with improved handling
        from pytube import Playlist

        playlist = Playlist(playlist_url)

        # Fix: Use the correct way to access videos in a playlist
        # This avoids the regex error by using a more reliable approach
        print("Attempting to extract videos...")

        # Initialize empty list for video info
        videos_info = []

        try:
            # Try to get video URLs directly - the safe way
            print("Getting video URLs from playlist...")
            urls = list(playlist.video_urls)
            print(f"Found {len(urls)} videos")

            for url in urls:
                print(f"Processing URL: {url}")
                video_info = extract_video_info(url)
                videos_info.append(video_info)
        except Exception as e:
            print(f"Error with playlist.video_urls: {e}")

            # Alternative approach using YouTube API
            print("Trying alternative approach with YouTube API...")
            if os.getenv("API_KEY_YOUTUBE"):
                # Add your alternative approach here
                pass

        return videos_info
    except Exception as e:
        print(f"Error extracting playlist info: {e}")
        import traceback

        traceback.print_exc()
        return []
