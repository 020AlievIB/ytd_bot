import yt_dlp
import os
from typing import Tuple, Optional
from config import MAX_VIDEO_SIZE, SUPPORTED_FORMATS

class YouTubeDownloader:
    @staticmethod
    def download_video(url: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Download a YouTube video and return the file path and any error message.
        
        Args:
            url: YouTube video URL
            
        Returns:
            Tuple of (file_path, error_message)
        """
        try:
            ydl_opts = {
                'format': f'best[filesize<{MAX_VIDEO_SIZE}][ext=mp4]/best[ext=mp4]',
                'outtmpl': '%(title)s.%(ext)s',
                'quiet': True,
                'no_warnings': True,
                'extract_flat': False,
                'postprocessors': [{
                    'key': 'FFmpegVideoConvertor',
                    'preferedformat': 'mp4',
                }],
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # Get video info first
                info = ydl.extract_info(url, download=False)
                video_title = info['title']
                video_path = f"{video_title}.mp4"

                # Check if video is too large
                if info.get('filesize', 0) > MAX_VIDEO_SIZE:
                    return None, f"Video is too large (max {MAX_VIDEO_SIZE/1024/1024}MB)"

                # Download the video
                ydl.download([url])

                # Verify the downloaded file
                if os.path.exists(video_path):
                    actual_size = os.path.getsize(video_path)
                    if actual_size > MAX_VIDEO_SIZE:
                        os.remove(video_path)
                        return None, f"Downloaded file is too large ({actual_size/1024/1024:.1f}MB)"
                    return video_path, None
                else:
                    return None, "Failed to download video"

        except Exception as e:
            return None, f"Error downloading video: {str(e)}" 