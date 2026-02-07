import yt_dlp
import pandas as pd

def get_channel_videos(channel_url, max_results=20):
    ydl_opts = {
        "quiet": True,
        "extract_flat": True,
        "skip_download": True,
        "playlistend": max_results
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(channel_url, download=False)

    videos = []
    for entry in info["entries"]:
        videos.append({
            "title": entry.get("title"),
            "views": entry.get("view_count", 0),
            "likes": entry.get("like_count", 0),
            "comments": entry.get("comment_count", 0),
            "duration": entry.get("duration", 0),
            "upload_date": entry.get("upload_date")
        })

    df = pd.DataFrame(videos)
    df.to_csv("data/youtube_data.csv", index=False)
    return df
