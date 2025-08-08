"""
YouTube video downloader using yt-dlp.
"""

import os
import sys
from pathlib import Path
from typing import Dict, Optional, Any, List
import yt_dlp
from rich.console import Console
from rich.progress import Progress, TaskID


class YouTubeDownloader:
    """Handle YouTube video downloads with yt-dlp."""
    
    def __init__(self, output_dir: str = "downloads", quality: str = "best"):
        """
        Initialize the downloader.
        
        Args:
            output_dir: Directory to save downloaded videos
            quality: Video quality preference (best, worst, 720p, etc.)
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.quality = quality
        self.console = Console()
        
    def _get_ydl_opts(self, filename_template: Optional[str] = None) -> Dict[str, Any]:
        """Get yt-dlp options configuration."""
        opts = {
            'outtmpl': str(self.output_dir / (filename_template or '%(title)s.%(ext)s')),
            'format': self._parse_quality(self.quality),
            'noplaylist': True,  # Download single video, not playlist
            'extract_flat': False,
        }
        return opts
    
    def _parse_quality(self, quality: str) -> str:
        """Convert quality preference to yt-dlp format string."""
        quality_map = {
            'best': 'bv*+ba/b',
            'worst': 'wv*+wa/w', 
            'audio': 'ba/best',
            '144p': 'bv*[height<=144]+ba/b[height<=144]/wv*[height<=144]+wa/w[height<=144]',
            '240p': 'bv*[height<=240]+ba/b[height<=240]/wv*[height<=240]+wa/w[height<=240]',
            '360p': 'bv*[height<=360]+ba/b[height<=360]/wv*[height<=360]+wa/w[height<=360]',
            '480p': 'bv*[height<=480]+ba/b[height<=480]/wv*[height<=480]+wa/w[height<=480]',
            '720p': 'bv*[height<=720]+ba/b[height<=720]/wv*[height<=720]+wa/w[height<=720]',
            '1080p': 'bv*[height<=1080]+ba/b[height<=1080]/wv*[height<=1080]+wa/w[height<=1080]',
        }
        return quality_map.get(quality, quality)
    
    def get_video_info(self, url: str) -> Dict[str, Any]:
        """
        Extract video metadata without downloading.
        
        Args:
            url: YouTube video URL
            
        Returns:
            Video metadata dictionary
        """
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                return ydl.sanitize_info(info)
        except Exception as e:
            raise RuntimeError(f"Failed to extract video info: {e}")
    
    def download(self, url: str, filename_template: Optional[str] = None) -> str:
        """
        Download a YouTube video.
        
        Args:
            url: YouTube video URL
            filename_template: Custom filename template (optional)
            
        Returns:
            Path to downloaded file
        """
        ydl_opts = self._get_ydl_opts(filename_template)
        
        # Add progress hook
        downloaded_file = None
        
        def progress_hook(d):
            nonlocal downloaded_file
            if d['status'] == 'finished':
                downloaded_file = d['filename']
                self.console.print(f"✅ Download completed: {os.path.basename(downloaded_file)}")
            elif d['status'] == 'downloading':
                if 'total_bytes' in d and 'downloaded_bytes' in d:
                    percent = (d['downloaded_bytes'] / d['total_bytes']) * 100
                    self.console.print(f"📥 Downloading... {percent:.1f}%", end='\r')
        
        ydl_opts['progress_hooks'] = [progress_hook]
        
        try:
            self.console.print(f"🎬 Starting download from: {url}")
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            
            if downloaded_file:
                return downloaded_file
            else:
                raise RuntimeError("Download completed but file path not captured")
                
        except Exception as e:
            raise RuntimeError(f"Download failed: {e}")
    
    def download_audio_only(self, url: str, filename_template: Optional[str] = None) -> str:
        """
        Download audio-only version of a YouTube video.
        
        Args:
            url: YouTube video URL
            filename_template: Custom filename template (optional)
            
        Returns:
            Path to downloaded audio file
        """
        ydl_opts = self._get_ydl_opts(filename_template)
        ydl_opts['format'] = 'ba/best'  # Best audio
        ydl_opts['postprocessors'] = [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }]
        
        downloaded_file = None
        
        def progress_hook(d):
            nonlocal downloaded_file
            if d['status'] == 'finished':
                downloaded_file = d['filename']
                self.console.print(f"✅ Audio extraction completed: {os.path.basename(downloaded_file)}")
            elif d['status'] == 'downloading':
                if 'total_bytes' in d and 'downloaded_bytes' in d:
                    percent = (d['downloaded_bytes'] / d['total_bytes']) * 100
                    self.console.print(f"📥 Downloading audio... {percent:.1f}%", end='\r')
        
        ydl_opts['progress_hooks'] = [progress_hook]
        
        try:
            self.console.print(f"🎵 Starting audio download from: {url}")
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            
            if downloaded_file:
                # yt-dlp might change extension after post-processing
                base_name = os.path.splitext(downloaded_file)[0]
                mp3_file = f"{base_name}.mp3"
                if os.path.exists(mp3_file):
                    return mp3_file
                return downloaded_file
            else:
                raise RuntimeError("Download completed but file path not captured")
                
        except Exception as e:
            raise RuntimeError(f"Audio download failed: {e}")
    
    def list_formats(self, url: str) -> List[Dict[str, Any]]:
        """
        List available formats for a video.
        
        Args:
            url: YouTube video URL
            
        Returns:
            List of available formats
        """
        try:
            info = self.get_video_info(url)
            formats = info.get('formats', [])
            
            # Filter and format the information
            formatted_formats = []
            for fmt in formats:
                formatted_formats.append({
                    'format_id': fmt.get('format_id'),
                    'ext': fmt.get('ext'),
                    'resolution': fmt.get('resolution', 'audio only' if fmt.get('vcodec') == 'none' else 'unknown'),
                    'filesize': fmt.get('filesize'),
                    'vcodec': fmt.get('vcodec'),
                    'acodec': fmt.get('acodec'),
                })
            
            return formatted_formats
            
        except Exception as e:
            raise RuntimeError(f"Failed to list formats: {e}")


def validate_youtube_url(url: str) -> bool:
    """
    Validate if a URL is a valid YouTube URL.
    
    Args:
        url: URL to validate
        
    Returns:
        True if valid YouTube URL, False otherwise
    """
    youtube_domains = [
        'youtube.com',
        'www.youtube.com', 
        'youtu.be',
        'm.youtube.com'
    ]
    
    try:
        from urllib.parse import urlparse
        parsed = urlparse(url)
        return parsed.netloc.lower() in youtube_domains
    except:
        return False