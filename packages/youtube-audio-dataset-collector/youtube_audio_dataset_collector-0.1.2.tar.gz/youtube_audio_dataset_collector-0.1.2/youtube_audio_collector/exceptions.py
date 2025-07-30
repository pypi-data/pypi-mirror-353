"""
Custom exceptions for YouTube Audio Dataset Collector
"""


class YouTubeAudioCollectorError(Exception):
    """Base exception for all YouTube Audio Collector errors"""
    pass


class DownloadError(YouTubeAudioCollectorError):
    """Raised when audio download fails"""
    pass


class ProcessingError(YouTubeAudioCollectorError):
    """Raised when audio processing fails"""
    pass


class TranscriptionError(YouTubeAudioCollectorError):
    """Raised when transcription fails"""
    pass


class APIKeyError(YouTubeAudioCollectorError):
    """Raised when API key management fails"""
    pass


class ConfigurationError(YouTubeAudioCollectorError):
    """Raised when configuration is invalid"""
    pass


class DependencyError(YouTubeAudioCollectorError):
    """Raised when required system dependencies are missing"""
    pass
