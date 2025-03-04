import os
import ssl
from dotenv import load_dotenv
from youtube.downloader import download_content
from youtube.extractor import extract_video_info
from youtube.api_extractor import extract_playlist_videos_api
from summarizer.summary import summarize_video
from notion.client import NotionClient

# Fix SSL certificate issues - place this BEFORE main() function
ssl._create_default_https_context = ssl._create_unverified_context


def main():
    # Load environment variables
    load_dotenv()

    # Get user input for YouTube video or playlist
    user_input = input("Enter the YouTube video URL or playlist URL: ")
    print(f"Processing URL: {user_input}")

    # For playlists, use extract_playlist_videos_api directly
    if "playlist" in user_input:
        print("Detected playlist URL. Extracting videos using API...")
        videos_info = extract_playlist_videos_api(user_input)
        print(f"Found {len(videos_info)} videos in the playlist")

        # Initialize Notion client with token
        notion_client = NotionClient(os.getenv("API_KEY_NOTION"))
        notion_database_id = os.getenv("NOTION_DATABASE_ID")

        # Reverse the videos list to maintain chronological order in Notion
        videos_info.reverse()

        # Process each video in the playlist
        for video_info in videos_info:
            print(f"Processing video: {video_info['title']}")
            summary = summarize_video(video_info)
            print("Generated summary, saving to Notion...")
            notion_client.create_page(
                notion_database_id,
                video_info["title"],
                summary,
                video_url=video_info.get("url", ""),
            )
            print(f"Processed video: {video_info['title']}")
    else:
        # For single videos
        print("Extracting video information...")
        video_info = extract_video_info(user_input)

        # Initialize Notion client with token
        notion_client = NotionClient(os.getenv("API_KEY_NOTION"))
        notion_database_id = os.getenv("NOTION_DATABASE_ID")

        print(f"Processing video: {video_info['title']}")
        summary = summarize_video(video_info)
        print("Generated summary, saving to Notion...")
        notion_client.create_page(
            notion_database_id, video_info["title"], summary, video_url=user_input
        )
        print(f"Processed video: {video_info['title']}")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error in main program: {e}")
        import traceback

        traceback.print_exc()
