import yt_dlp
import pandas as pd
import os
import hashlib

DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)

def _cache_path(channel_url):
    hash_name = hashlib.md5(channel_url.encode()).hexdigest()
    return os.path.join(DATA_DIR, f"{hash_name}.csv")

def get_channel_videos(channel_url, max_results=10, refresh=False):
    # Normalize URL
    if "/videos" not in channel_url:
        channel_url = channel_url.rstrip("/") + "/videos"

    cache_file = _cache_path(channel_url)

    # Load from cache if exists and not refreshing
    if os.path.exists(cache_file) and not refresh:
        return pd.read_csv(cache_file)

    ydl_opts = {
        "quiet": True,
        "skip_download": True,
        "extract_flat": True,
        "playlistend": max_results
    }

    videos = []

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        channel_info = ydl.extract_info(channel_url, download=False)

        for entry in channel_info.get("entries", []):
            video_id = entry.get("id")
            if not video_id:
                continue

            video_url = f"https://www.youtube.com/watch?v={video_id}"

            try:
                video_info = ydl.extract_info(video_url, download=False)

                videos.append({
                    "title": video_info.get("title"),
                    "views": video_info.get("view_count", 0),
                    "likes": video_info.get("like_count", 0),
                    "comments": video_info.get("comment_count", 0),
                    "duration": video_info.get("duration", 0),
                    "upload_date": video_info.get("upload_date")
                })

            except Exception:
                continue

    df = pd.DataFrame(videos)
    df.to_csv(cache_file, index=False)
    return df
