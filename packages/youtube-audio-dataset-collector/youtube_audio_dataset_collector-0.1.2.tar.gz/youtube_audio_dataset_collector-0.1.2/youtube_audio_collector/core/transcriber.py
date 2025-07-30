"""
Transcription service for converting audio to text using Gemini API.
"""

import logging
from typing import Optional, Dict, Any

import google.generativeai as genai

from .api_manager import APIKeyManager
from ..exceptions import TranscriptionError

logger = logging.getLogger(__name__)


class TranscriptionService:
    """
    Transcribes audio using the Gemini API.
    
    Features:
    - Transcribes audio files to text
    - Supports multiple API keys with rotation
    - Handles rate limiting and retries
    """
    
    def __init__(self, api_key_manager: Optional[APIKeyManager] = None, api_key: Optional[str] = None):
        """
        Initialize the transcription service
        
        Args:
            api_key_manager: API key manager for multiple keys
            api_key: Single API key (used if api_key_manager is not provided)
            
        Raises:
            TranscriptionError: If neither api_key_manager nor api_key is provided
        """
        if api_key_manager:
            self.api_key_manager = api_key_manager
            self.single_key_mode = False
            logger.info("Initialized Transcription Service with API Key Manager")
        elif api_key:
            self.api_key = api_key
            self.single_key_mode = True
            logger.info("Initialized Transcription Service with single API key")
        else:
            raise TranscriptionError("Either api_key_manager or api_key must be provided")
    
    def transcribe_audio(self, audio_path: str, language: str = "en", **kwargs) -> str:
        """
        Transcribe audio file to text
        
        Args:
            audio_path: Path to audio file
            language: Language code (default: "en" for English)
            **kwargs: Additional transcription parameters
            
        Returns:
            Transcription text
            
        Raises:
            TranscriptionError: If transcription fails
        """
        # Get API key
        if self.single_key_mode:
            api_key = self.api_key
        else:
            api_key = self.api_key_manager.get_next_available_key()
        
        try:
            # Configure API key
            genai.configure(api_key=api_key)
            
            # Upload file to Gemini
            logger.info(f"Uploading audio for transcription: {audio_path}")
            file = genai.upload_file(audio_path)
            
            # Check for None values
            if file.uri is None or file.mime_type is None:
                raise TranscriptionError("File URI or MIME type is None")
            
            # Prepare transcription request
            response = self._make_transcription_request(file, language, **kwargs)
            
            logger.info(f"Transcription completed successfully")
            return response.text
            
        except Exception as e:
            logger.error(f"Error transcribing {audio_path}: {str(e)}")
            
            # Mark key as unhealthy if not in single key mode
            if not self.single_key_mode:
                self.api_key_manager.mark_key_unhealthy(api_key)
                
                # Retry with a different key
                logger.info(f"Retrying with a different API key")
                return self.transcribe_audio(audio_path, language, **kwargs)
            
            raise TranscriptionError(f"Failed to transcribe {audio_path}: {str(e)}")
    
    def _make_transcription_request(self, 
                                  file: Any, 
                                  language: str, 
                                  **kwargs) -> Any:
        """Make the actual transcription request to Gemini API"""
        
        model_name = kwargs.get('model', "gemini-2.0-flash")
        
        # Generate prompt based on language
        prompt = self._generate_prompt(language, **kwargs)
        
        # Create model instance
        model = genai.GenerativeModel(model_name)
        
        # Make transcription request
        logger.debug(f"Requesting transcription from Gemini API")
        response = model.generate_content([file, prompt])
        
        return response
    
    def _generate_prompt(self, language: str, **kwargs) -> str:
        """Generate appropriate prompt based on language and parameters"""
        
        # Custom prompt if provided
        if 'custom_prompt' in kwargs:
            return kwargs['custom_prompt']
        
        # Language-specific prompts
        language_prompts = {
            "en": "Transcribe the provided English audio into a clean, accurate text. Remove all filler sounds (e.g., 'hmm', 'uh'), background noise, pop sounds, and music. Retain only the meaningful spoken content, ensuring that the transcription follows proper English grammar, punctuation, and spelling. This output will be used as training data.",
            
            "kn": "Transcribe the provided Kannada audio into a clean, accurate text. Remove all filler sounds (e.g., 'hmm', 'uh'), background noise, pop sounds, and music. Retain only the meaningful spoken content, ensuring that the transcription follows proper Kannada grammar, punctuation, and spelling. This output will be used as training data.",
            
            "hi": "Transcribe the provided Hindi audio into a clean, accurate text. Remove all filler sounds (e.g., 'hmm', 'uh'), background noise, pop sounds, and music. Retain only the meaningful spoken content, ensuring that the transcription follows proper Hindi grammar, punctuation, and spelling. This output will be used as training data.",
            
            "es": "Transcribe the provided Spanish audio into a clean, accurate text. Remove all filler sounds (e.g., 'hmm', 'uh'), background noise, pop sounds, and music. Retain only the meaningful spoken content, ensuring that the transcription follows proper Spanish grammar, punctuation, and spelling. This output will be used as training data.",
            
            "fr": "Transcribe the provided French audio into a clean, accurate text. Remove all filler sounds (e.g., 'hmm', 'uh'), background noise, pop sounds, and music. Retain only the meaningful spoken content, ensuring that the transcription follows proper French grammar, punctuation, and spelling. This output will be used as training data.",
        }
        
        # Return language-specific prompt or generic prompt
        if language in language_prompts:
            return language_prompts[language]
        else:
            return f"Transcribe the provided audio into a clean, accurate text in {language}. Remove all filler sounds (e.g., 'hmm', 'uh'), background noise, pop sounds, and music. Retain only the meaningful spoken content, ensuring that the transcription follows proper grammar, punctuation, and spelling. This output will be used as training data."
    
    def batch_transcribe(self, audio_paths: list, language: str = "en", **kwargs) -> Dict[str, str]:
        """
        Transcribe multiple audio files
        
        Args:
            audio_paths: List of audio file paths
            language: Language code
            **kwargs: Additional transcription parameters
            
        Returns:
            Dictionary mapping audio paths to transcriptions
        """
        results = {}
        
        for i, audio_path in enumerate(audio_paths):
            logger.info(f"Transcribing {i+1}/{len(audio_paths)}: {audio_path}")
            try:
                transcript = self.transcribe_audio(audio_path, language, **kwargs)
                results[audio_path] = transcript
            except TranscriptionError as e:
                logger.error(f"Failed to transcribe {audio_path}: {str(e)}")
                results[audio_path] = f"ERROR: {str(e)}"
        
        return results
    
    def get_supported_languages(self) -> Dict[str, str]:
        """
        Get dictionary of supported language codes and names
        
        Returns:
            Dictionary mapping language codes to language names
        """
        return {
            "en": "English",
            "kn": "Kannada", 
            "hi": "Hindi",
            "es": "Spanish",
            "fr": "French",
            "de": "German",
            "it": "Italian",
            "pt": "Portuguese",
            "ru": "Russian",
            "ja": "Japanese",
            "ko": "Korean",
            "zh": "Chinese",
            "ar": "Arabic",
        }
    
    def validate_language(self, language: str) -> bool:
        """
        Validate if a language code is supported
        
        Args:
            language: Language code to validate
            
        Returns:
            True if language is supported, False otherwise
        """
        return language in self.get_supported_languages()
    
    def get_api_stats(self) -> Optional[Dict]:
        """
        Get API usage statistics if using API key manager
        
        Returns:
            Dictionary with API statistics or None if using single key
        """
        if not self.single_key_mode:
            return self.api_key_manager.get_key_stats()
        return None
