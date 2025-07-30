"""
Basic tests for YouTube Audio Dataset Collector
"""

import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from youtube_audio_collector import YouTubeAudioCollector
from youtube_audio_collector.core import APIKeyManager, YouTubeDownloader, AudioProcessor, TranscriptionService
from youtube_audio_collector.config import ConfigManager, CollectorConfig
from youtube_audio_collector.exceptions import (
    YouTubeAudioCollectorError, 
    DownloadError, 
    ProcessingError, 
    TranscriptionError,
    ConfigurationError
)


class TestCollectorConfig(unittest.TestCase):
    """Test configuration management"""
    
    def test_config_creation(self):
        """Test creating configuration"""
        config = CollectorConfig(
            output_dir="./test",
            api_key="test_key"
        )
        self.assertEqual(config.output_dir, "./test")
        self.assertEqual(config.api_key, "test_key")
    
    def test_config_validation_no_api_key(self):
        """Test configuration validation fails without API key"""
        config = CollectorConfig(output_dir="./test")
        with self.assertRaises(ConfigurationError):
            config.validate()
    
    def test_config_validation_invalid_threads(self):
        """Test configuration validation fails with invalid threads"""
        config = CollectorConfig(
            output_dir="./test",
            api_key="test_key",
            threads=0
        )
        with self.assertRaises(ConfigurationError):
            config.validate()
    
    def test_config_to_dict(self):
        """Test converting configuration to dictionary"""
        config = CollectorConfig(
            output_dir="./test",
            api_key="test_key",
            threads=2
        )
        config_dict = config.to_dict()
        self.assertIsInstance(config_dict, dict)
        self.assertEqual(config_dict['output_dir'], "./test")
        self.assertEqual(config_dict['threads'], 2)
    
    def test_config_from_dict(self):
        """Test creating configuration from dictionary"""
        data = {
            'output_dir': './test',
            'api_key': 'test_key',
            'threads': 3,
            'unknown_key': 'should_be_ignored'  # Should be filtered out
        }
        config = CollectorConfig.from_dict(data)
        self.assertEqual(config.output_dir, "./test")
        self.assertEqual(config.threads, 3)


class TestAPIKeyManager(unittest.TestCase):
    """Test API key management"""
    
    def test_manager_creation(self):
        """Test creating API key manager"""
        keys = ["key1", "key2", "key3"]
        manager = APIKeyManager(keys)
        self.assertEqual(len(manager.api_keys), 3)
    
    def test_key_rotation(self):
        """Test key rotation"""
        keys = ["key1", "key2"]
        manager = APIKeyManager(keys)
        
        # Get keys in sequence
        first_key = manager.get_next_available_key()
        second_key = manager.get_next_available_key()
        
        # Should rotate
        self.assertNotEqual(first_key, second_key)
        self.assertIn(first_key, keys)
        self.assertIn(second_key, keys)
    
    def test_mark_key_unhealthy(self):
        """Test marking keys as unhealthy"""
        keys = ["key1", "key2"]
        manager = APIKeyManager(keys)
        
        # Mark first key as unhealthy
        manager.mark_key_unhealthy("key1")
        self.assertFalse(manager.key_health["key1"])
        
        # Should still get key2
        available_key = manager.get_next_available_key()
        self.assertEqual(available_key, "key2")


class TestYouTubeDownloader(unittest.TestCase):
    """Test YouTube downloader"""
    
    def setUp(self):
        self.downloader = YouTubeDownloader()
    
    def test_dependency_check(self):
        """Test yt-dlp dependency check"""
        # Should not raise exception if yt-dlp is available
        try:
            missing = self.downloader.check_dependencies()
            self.assertEqual(missing, [], "Dependencies should be available")
        except Exception as e:
            self.fail(f"Dependency check failed: {e}")
    
    def test_url_validation(self):
        """Test URL validation"""
        valid_urls = [
            "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "https://youtu.be/dQw4w9WgXcQ",
            "https://www.youtube.com/playlist?list=PLx0sYbCqOb8Q"
        ]
        
        invalid_urls = [
            "not_a_url",
            "https://example.com",
            ""
        ]
        
        for url in valid_urls:
            self.assertTrue(self.downloader.validate_url(url))
        
        for url in invalid_urls:
            self.assertFalse(self.downloader.validate_url(url))


class TestAudioProcessor(unittest.TestCase):
    """Test audio processor"""
    
    def setUp(self):
        self.processor = AudioProcessor()
    
    def test_processor_creation(self):
        """Test creating audio processor"""
        self.assertEqual(self.processor.sample_rate, 16000)
    
    def test_supported_formats(self):
        """Test getting supported formats"""
        formats = AudioProcessor.get_supported_formats()
        self.assertIsInstance(formats, list)
        self.assertIn('.wav', formats)
        self.assertIn('.mp3', formats)
    
    def test_get_audio_info_file_not_found(self):
        """Test getting audio info for non-existent file"""
        with self.assertRaises(ProcessingError):
            self.processor.get_audio_info("non_existent_file.wav")


class TestTranscriptionService(unittest.TestCase):
    """Test transcription service"""
    
    def test_service_creation_with_single_key(self):
        """Test creating transcription service with single API key"""
        service = TranscriptionService(api_key="test_key")
        self.assertEqual(service.api_key, "test_key")
        self.assertTrue(service.single_key_mode)
    
    def test_service_creation_with_manager(self):
        """Test creating transcription service with API key manager"""
        manager = APIKeyManager(["key1", "key2"])
        service = TranscriptionService(api_key_manager=manager)
        self.assertFalse(service.single_key_mode)
        self.assertEqual(service.api_key_manager, manager)
    
    def test_supported_languages(self):
        """Test getting supported languages"""
        service = TranscriptionService(api_key="test_key")
        languages = service.get_supported_languages()
        self.assertIsInstance(languages, dict)
        self.assertIn('en', languages)
        self.assertIn('kn', languages)
    
    def test_validate_language(self):
        """Test language validation"""
        service = TranscriptionService(api_key="test_key")
        self.assertTrue(service.validate_language('en'))
        self.assertTrue(service.validate_language('kn'))
        self.assertFalse(service.validate_language('invalid_lang'))


class TestYouTubeAudioCollector(unittest.TestCase):
    """Test main collector class"""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.collector = YouTubeAudioCollector(
            output_dir=self.temp_dir,
            api_key="test_key"
        )
    
    def tearDown(self):
        # Clean up temporary directory
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_collector_creation(self):
        """Test creating collector"""
        self.assertEqual(self.collector.output_dir, self.temp_dir)
        self.assertIsInstance(self.collector.downloader, YouTubeDownloader)
        self.assertIsInstance(self.collector.processor, AudioProcessor)
        self.assertIsInstance(self.collector.transcriber, TranscriptionService)
    
    def test_collector_with_multiple_keys(self):
        """Test creating collector with multiple API keys"""
        collector = YouTubeAudioCollector(
            output_dir=self.temp_dir,
            api_keys=["key1", "key2", "key3"]
        )
        self.assertIsInstance(collector.api_key_manager, APIKeyManager)
        self.assertFalse(collector.transcriber.single_key_mode)
    
    def test_collector_no_api_key(self):
        """Test creating collector without API key raises error"""
        with self.assertRaises(ConfigurationError):
            YouTubeAudioCollector(output_dir=self.temp_dir)
    
    def test_get_stats(self):
        """Test getting statistics"""
        stats = self.collector.get_stats()
        self.assertIsInstance(stats, dict)
        self.assertIn('output_directory', stats)
        self.assertIn('configuration', stats)
        self.assertIn('raw_files', stats)
        self.assertIn('converted_files', stats)
        self.assertIn('segments', stats)


class TestConfigManager(unittest.TestCase):
    """Test configuration manager"""
    
    def test_config_manager_creation(self):
        """Test creating configuration manager"""
        manager = ConfigManager()
        self.assertIsInstance(manager, ConfigManager)
    
    def test_load_api_keys_from_env(self):
        """Test loading API keys from environment"""
        with patch.dict(os.environ, {
            'GEMINI_API_KEY': 'test_key',
            'GEMINI_API_KEY_1': 'key1',
            'GEMINI_API_KEY_2': 'key2'
        }):
            manager = ConfigManager()
            keys = manager._load_api_keys_from_env()
            # Should get the single key and numbered keys
            self.assertIn('test_key', keys)
            self.assertIn('key1', keys)
            self.assertIn('key2', keys)
    
    def test_load_config_from_env(self):
        """Test loading configuration from environment"""
        with patch.dict(os.environ, {
            'YADC_OUTPUT_DIR': './test_output',
            'YADC_THREADS': '8',
            'YADC_BATCH_SIZE': '6',
            'GEMINI_API_KEY': 'test_key'
        }):
            manager = ConfigManager()
            config_data = manager._load_from_env()
            self.assertEqual(config_data.get('output_dir'), './test_output')
            self.assertEqual(config_data.get('threads'), 8)
            self.assertEqual(config_data.get('batch_size'), 6)


if __name__ == '__main__':
    # Configure logging for tests
    logging.basicConfig(level=logging.WARNING)
    
    # Run tests
    unittest.main(verbosity=2)
