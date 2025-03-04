import ssl

def download_video(video_url):
    from pytube import YouTube

    try:
        yt = YouTube(video_url)
        stream = yt.streams.filter(progressive=True, file_extension="mp4").first()
        stream.download()
        return yt.title
    except Exception as e:
        print(f"Error downloading video: {e}")
        return None


def download_playlist(playlist_url):
    from pytube import Playlist

    try:
        playlist = Playlist(playlist_url)
        titles = []
        for video in playlist.videos:
            title = download_video(video.watch_url)
            if title:
                titles.append(title)
        return titles
    except Exception as e:
        print(f"Error downloading playlist: {e}")
        return []


def download_content(input_url):
        # Modify your existing code to use this context with urlopen or requests
    try:
        if "playlist" in input_url:
            return download_playlist(input_url)
        else:
            return [download_video(input_url)]
    except Exception as e:
        print(f"Error downloading playlist: {e}")
        return []
