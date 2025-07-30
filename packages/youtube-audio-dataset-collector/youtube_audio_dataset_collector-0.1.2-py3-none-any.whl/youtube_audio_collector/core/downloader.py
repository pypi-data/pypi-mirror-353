"""
YouTube downloader for extracting audio from YouTube videos and playlists.
"""

import os
import sys
import glob
import subprocess
import logging
from pathlib import Path
from typing import List, Optional
import datetime

from ..exceptions import DownloadError, DependencyError

logger = logging.getLogger(__name__)


class YouTubeDownloader:
    """
    Downloads audio from YouTube videos and playlists using yt-dlp.
    
    Features:
    - Downloads audio from single videos or entire playlists
    - Uses cookies for authentication to access restricted content
    - Converts downloaded audio to WAV format using ffmpeg
    """
    
    def __init__(self, cookies_path: Optional[str] = None):
        """
        Initialize the YouTube downloader
        
        Args:
            cookies_path: Path to cookies.txt file for authentication
            
        Raises:
            DependencyError: If required dependencies are not found
        """
        self.cookies_path = cookies_path
        
        # Check if yt-dlp is installed
        try:
            subprocess.run(["yt-dlp", "--version"], capture_output=True, text=True, check=True)
        except (subprocess.SubprocessError, FileNotFoundError):
            raise DependencyError(
                "yt-dlp not found. Please install it with: pip install yt-dlp"
            )
        
        # Check if ffmpeg is installed
        try:
            subprocess.run(["ffmpeg", "-version"], capture_output=True, text=True, check=True)
        except (subprocess.SubprocessError, FileNotFoundError):
            raise DependencyError(
                "ffmpeg not found. Please install ffmpeg before continuing."
            )
        
        logger.info("YouTube downloader initialized successfully")
    
    def download_audio(self, url: str, output_dir: str, prefix: str = "") -> List[str]:
        """
        Download audio from a YouTube URL
        
        Args:
            url: YouTube video or playlist URL
            output_dir: Directory to save downloaded audio
            prefix: Prefix for output filenames
            
        Returns:
            List of paths to downloaded audio files
            
        Raises:
            DownloadError: If download fails
        """
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Determine if URL is a playlist
        is_playlist = "playlist" in url or "&list=" in url
        
        # Prepare output template
        if is_playlist:
            output_template = os.path.join(output_dir, f"{prefix}%(playlist_index)s-%(title)s.%(ext)s")
            logger.info(f"Downloading playlist: {url}")
        else:
            output_template = os.path.join(output_dir, f"{prefix}%(title)s.%(ext)s")
            logger.info(f"Downloading single video: {url}")
        
        # Prepare yt-dlp command
        cmd = self._build_download_command(url, output_template)
        
        # Execute download command
        try:
            logger.info("Executing yt-dlp command...")
            process = subprocess.run(cmd, capture_output=True, text=True, check=True)
            logger.info("Download completed successfully")
            
            # Find all downloaded WAV files
            wav_files = self._find_downloaded_files(output_dir, prefix)
            logger.info(f"Found {len(wav_files)} downloaded WAV files")
            
            # Rename files to prefix + timestamp, ensuring name length < 32 chars
            effective_prefix = prefix if prefix else os.path.basename(output_dir)
            renamed_files = []
            for file_path in wav_files:
                ext = os.path.splitext(file_path)[1]
                timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
                base_name = f"{effective_prefix}_{timestamp}"
                max_len = 32 - len(ext)
                base_name = base_name[:max_len]
                new_name = f"{base_name}{ext}"
                new_path = os.path.join(output_dir, new_name)
                os.rename(file_path, new_path)
                renamed_files.append(new_path)
            wav_files = renamed_files
            
            return wav_files
            
        except subprocess.CalledProcessError as e:
            error_msg = f"Error downloading audio: {str(e)}"
            logger.error(error_msg)
            logger.error(f"yt-dlp stdout: {e.stdout}")
            logger.error(f"yt-dlp stderr: {e.stderr}")
            raise DownloadError(f"Failed to download audio from {url}: {e.stderr}")
    
    def _build_download_command(self, url: str, output_template: str) -> List[str]:
        """Build the yt-dlp command with all necessary options"""
        cmd = ["yt-dlp"]
        
        # Add cookies if available
        if self.cookies_path and os.path.exists(self.cookies_path):
            cmd.extend(["--cookies", self.cookies_path])
            logger.info(f"Using cookies file: {self.cookies_path}")
        
        # Configure audio extraction and format
        cmd.extend([
            "-x",  # Extract audio
            "--audio-format", "wav",  # Convert to WAV
            "--audio-quality", "0",  # Best quality
            "--no-playlist",  # Don't download playlist if URL is a single video in a playlist
            "-o", output_template,
            url
        ])
        
        # If URL is explicitly a playlist, enable playlist mode
        if "playlist" in url or "&list=" in url:
            cmd.remove("--no-playlist")
            cmd.extend(["--yes-playlist"])
        
        return cmd
    
    def _find_downloaded_files(self, output_dir: str, prefix: str) -> List[str]:
        """Find all downloaded audio files"""
        audio_extensions = ['.wav', '.mp3', '.m4a', '.ogg', '.flac']
        files = []
        
        for ext in audio_extensions:
            pattern = os.path.join(output_dir, f"{prefix}*{ext}")
            files.extend(glob.glob(pattern))
        
        # Also check for files without prefix (in case yt-dlp naming differs)
        if not files:
            for ext in audio_extensions:
                pattern = os.path.join(output_dir, f"*{ext}")
                files.extend(glob.glob(pattern))
        
        return sorted(files)
    
    def validate_url(self, url: str) -> bool:
        """
        Validate if a URL is a valid YouTube URL
        
        Args:
            url: URL to validate
            
        Returns:
            True if URL is valid, False otherwise
        """
        youtube_domains = [
            'youtube.com',
            'youtu.be', 
            'www.youtube.com',
            'm.youtube.com'
        ]
        
        return any(domain in url.lower() for domain in youtube_domains)
    
    def get_video_info(self, url: str) -> dict:
        """
        Get information about a YouTube video/playlist without downloading
        
        Args:
            url: YouTube URL
            
        Returns:
            Dictionary with video/playlist information
            
        Raises:
            DownloadError: If unable to get video info
        """
        cmd = [
            "yt-dlp",
            "--dump-json",
            "--no-download",
            url
        ]
        
        try:
            process = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            # Parse JSON output
            import json
            lines = process.stdout.strip().split('\n')
            videos = []
            for line in lines:
                if line.strip():
                    videos.append(json.loads(line))
            
            return {
                'url': url,
                'video_count': len(videos),
                'videos': videos
            }
            
        except subprocess.CalledProcessError as e:
            raise DownloadError(f"Failed to get video info: {e.stderr}")
        except json.JSONDecodeError as e:
            raise DownloadError(f"Failed to parse video info: {str(e)}")
    
    @staticmethod
    def check_dependencies() -> List[str]:
        """
        Check if all required dependencies are available
        
        Returns:
            List of missing dependencies
        """
        missing = []
        
        # Check yt-dlp
        try:
            subprocess.run(["yt-dlp", "--version"], capture_output=True, check=True)
        except (subprocess.SubprocessError, FileNotFoundError):
            missing.append("yt-dlp")
        
        # Check ffmpeg
        try:
            subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True)
        except (subprocess.SubprocessError, FileNotFoundError):
            missing.append("ffmpeg")
        
        return missing
