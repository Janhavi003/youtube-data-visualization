import yt_dlp
import pandas as pd
import os
import hashlib

DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)


def _cache_path(channel_url: str) -> str:
    return os.path.join(
        DATA_DIR,
        hashlib.md5(channel_url.encode("utf-8")).hexdigest() + ".csv"
    )


def get_channel_videos(channel_url, max_results=10, refresh=False):
    """
    SAFE scraper for deployment.
    NEVER crashes the Dash server.
    """

    try:
        if "/videos" not in channel_url:
            channel_url = channel_url.rstrip("/") + "/videos"

        cache_file = _cache_path(channel_url)

        # Load from cache
        if os.path.exists(cache_file) and not refresh:
            df = pd.read_csv(cache_file)
            return df, None, None

        ydl_opts = {
            "quiet": True,
            "skip_download": True,
            "extract_flat": True,
            "playlistend": max_results,
        }

        videos = []
        channel_name = None
        channel_logo = None

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            channel_info = ydl.extract_info(channel_url, download=False)

            channel_name = channel_info.get("uploader") or channel_info.get("channel")

            thumbs = channel_info.get("thumbnails", [])
            channel_logo = thumbs[-1]["url"] if thumbs else None

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
                    })

                except Exception:
                    # Skip unavailable/private videos
                    continue

        df = pd.DataFrame(videos)
        df.to_csv(cache_file, index=False)

        return df, channel_name, channel_logo

    except Exception as e:
        print("SCRAPER ERROR:", e)
        return pd.DataFrame(), None, None
