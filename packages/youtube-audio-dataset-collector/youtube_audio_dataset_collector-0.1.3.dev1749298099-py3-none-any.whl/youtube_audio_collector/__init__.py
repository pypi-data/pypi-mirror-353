"""
YouTube Audio Dataset Collector

A comprehensive Python library for downloading, processing, and transcribing 
audio from YouTube videos and playlists for machine learning datasets.

Features:
- YouTube audio download with yt-dlp
- Audio format conversion and segmentation
- Multi-API key support for Gemini transcription
- Parallel processing for efficient data collection
- Export to CSV format for ML workflows

Example:
    Basic usage:
    
    >>> from youtube_audio_collector import YouTubeAudioCollector
    >>> collector = YouTubeAudioCollector(
    ...     output_dir="./dataset",
    ...     api_key="your_gemini_api_key"
    ... )
    >>> csv_file = collector.process_url("https://www.youtube.com/watch?v=VIDEO_ID")
    
    Advanced usage with multiple API keys:
    
    >>> collector = YouTubeAudioCollector(
    ...     output_dir="./dataset", 
    ...     api_keys=["key1", "key2", "key3"],
    ...     threads=8
    ... )
    >>> csv_file = collector.process_url(
    ...     "https://www.youtube.com/playlist?list=PLAYLIST_ID",
    ...     language="kn"
    ... )

Author: YouTube Audio Dataset Team
License: MIT
"""

__version__ = "1.0.0"
__author__ = "YouTube Audio Dataset Team"
__email__ = "your-email@example.com"
__license__ = "MIT"

# Import main classes for easy access
from .core.collector import YouTubeAudioCollector
from .core.downloader import YouTubeDownloader
from .core.processor import AudioProcessor
from .core.transcriber import TranscriptionService
from .core.api_manager import APIKeyManager

# Import configuration utilities
from .config import ConfigManager, CollectorConfig, load_config_from_file, load_config_from_env

# Import exceptions
from .exceptions import (
    YouTubeAudioCollectorError,
    DownloadError,
    ProcessingError,
    TranscriptionError,
    APIKeyError,
    ConfigurationError
)

# Define public API
__all__ = [
    # Main classes
    'YouTubeAudioCollector',
    'YouTubeDownloader', 
    'AudioProcessor',
    'TranscriptionService',
    'APIKeyManager',
    
    # Configuration
    'ConfigManager',
    'CollectorConfig',
    'load_config_from_file',
    'load_config_from_env',
    
    # Exceptions
    'YouTubeAudioCollectorError',
    'DownloadError',
    'ProcessingError', 
    'TranscriptionError',
    'APIKeyError',
    'ConfigurationError',
    
    # Metadata
    '__version__',
    '__author__',
    '__email__',
    '__license__',
]
