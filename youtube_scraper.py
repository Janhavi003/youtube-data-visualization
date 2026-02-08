import yt_dlp
import pandas as pd

def get_channel_videos(channel_url, max_results=10):
    ydl_opts = {
        "quiet": True,
        "skip_download": True,
        "extract_flat": True,
        "playlistend": max_results
    }

    videos = []

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        channel_info = ydl.extract_info(channel_url, download=False)

        for entry in channel_info["entries"]:
            video_id = entry.get("id")

            if not video_id:
                continue

            video_url = f"https://www.youtube.com/watch?v={video_id}"

            video_info = ydl.extract_info(video_url, download=False)

            videos.append({
                "title": video_info.get("title"),
                "views": video_info.get("view_count", 0),
                "likes": video_info.get("like_count", 0),
                "comments": video_info.get("comment_count", 0),
                "duration": video_info.get("duration", 0),
                "upload_date": video_info.get("upload_date")
            })

    df = pd.DataFrame(videos)
    df.to_csv("data/youtube_data.csv", index=False)
    return df
