import yt_dlp
from typing import Tuple, Optional, Callable
import os

class YouTubeDownloader:
    @staticmethod
    def download_video(
        url: str, 
        max_file_size: Optional[int] = 50 * 1024 * 1024,  # 50MB default limit
        progress_callback: Optional[Callable[[float], None]] = None
    ) -> Tuple[str | None, str | None]:
        """
        Download YouTube video with size and quality limits suitable for Telegram.
        
        Args:
            url: YouTube video URL
            max_file_size: Maximum file size in bytes (default 50MB)
            progress_callback: Optional callback function to report download progress
            
        Returns:
            Tuple of (file_path, error_message)
        """
        try:
            def progress_hook(d):
                if d['status'] == 'downloading' and progress_callback:
                    # Calculate download progress
                    downloaded = d.get('downloaded_bytes', 0)
                    total = d.get('total_bytes') or d.get('total_bytes_estimate', 0)
                    if total > 0:
                        progress = (downloaded / total) * 100
                        progress_callback(progress)

            ydl_opts = {
                # Limit quality for faster download and smaller file size
                'format': 'best[filesize<{}][ext=mp4]/best[ext=mp4]'.format(max_file_size),
                'outtmpl': '%(title)s.%(ext)s',
                'quiet': True,
                'no_warnings': True,
                'progress_hooks': [progress_hook],
                'http_headers': {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                }
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # Get video info first
                info = ydl.extract_info(url, download=False)
                video_title = info['title']
                video_path = f"{video_title}.mp4"

                # Check estimated file size before downloading
                format_info = info['formats'][-1]  # Best format
                filesize = format_info.get('filesize', 0)
                if filesize > max_file_size:
                    return None, f"Video file size ({filesize/1024/1024:.1f}MB) exceeds limit ({max_file_size/1024/1024:.1f}MB)"
                
                # Download the video
                ydl.download([url])
                
                # Verify downloaded file
                if os.path.exists(video_path):
                    actual_size = os.path.getsize(video_path)
                    if actual_size > max_file_size:
                        os.remove(video_path)
                        return None, f"Downloaded file size ({actual_size/1024/1024:.1f}MB) exceeds limit"
                    return video_path, None
                else:
                    return None, "Video downloaded but file not found."
                
        except Exception as e:
            return None, f"Error downloading video: {str(e)}" 