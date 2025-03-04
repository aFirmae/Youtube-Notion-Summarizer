import os
from googleapiclient.discovery import build
from .extractor import extract_video_info


def extract_playlist_videos_api(playlist_url):
    """
    Extract video information from a YouTube playlist using the YouTube Data API.

    Args:
        playlist_url (str): The URL of the YouTube playlist

    Returns:
        list: List of dictionaries containing video information
    """
    # Extract playlist ID from the URL
    if "list=" not in playlist_url:
        print("Invalid playlist URL")
        return []

    playlist_id = playlist_url.split("list=")[1]
    if "&" in playlist_id:
        playlist_id = playlist_id.split("&")[0]

    # Get API key from environment
    api_key = os.getenv("API_KEY_YOUTUBE")
    if not api_key:
        print("YouTube API key not set in environment variables")
        return []

    print(f"Using YouTube Data API to extract videos from playlist: {playlist_id}")

    try:
        youtube = build("youtube", "v3", developerKey=api_key)

        # Get playlist items
        videos_info = []
        next_page_token = None

        while True:
            request = youtube.playlistItems().list(
                part="snippet",
                maxResults=50,
                playlistId=playlist_id,
                pageToken=next_page_token,
            )
            response = request.execute()

            for item in response.get("items", []):
                video_id = item["snippet"]["resourceId"]["videoId"]
                video_url = f"https://www.youtube.com/watch?v={video_id}"
                print(f"Processing video: {item['snippet']['title']}")
                video_info = extract_video_info(video_url)
                video_info["url"] = (
                    video_url  # Add this line to ensure URL is in video_info
                )
                videos_info.append(video_info)

            next_page_token = response.get("nextPageToken")
            if not next_page_token:
                break

        print(f"Found {len(videos_info)} videos")
        return videos_info

    except Exception as e:
        print(f"Error using YouTube API: {e}")
        import traceback

        traceback.print_exc()
        return []
