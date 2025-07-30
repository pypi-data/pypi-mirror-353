"""
Configuration utilities for YouTube Audio Dataset Collector
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict

try:
    from dotenv import load_dotenv
    DOTENV_AVAILABLE = True
except ImportError:
    DOTENV_AVAILABLE = False

from .exceptions import ConfigurationError

logger = logging.getLogger(__name__)


@dataclass
class CollectorConfig:
    """Configuration dataclass for YouTubeAudioCollector"""
    
    # Required settings
    output_dir: str
    
    # API settings
    api_keys: Optional[List[str]] = None
    api_key: Optional[str] = None
    calls_per_key_per_minute: int = 15
    key_cooldown: int = 60
    
    # Processing settings
    prefix: str = ""
    sample_rate: int = 16000
    threads: int = 4
    batch_size: int = 4
    
    # Audio segmentation settings
    min_segment_length: int = 12000  # 12 seconds in ms
    max_segment_length: int = 28000  # 28 seconds in ms
    min_silence_len: int = 500       # 500ms
    silence_thresh: int = -35        # -35dB
    
    # Optional settings
    cookies_path: Optional[str] = None
    language: str = "en"
    
    # Utility settings
    cleanup_intermediate: bool = False
    keep_converted: bool = False
    verbose: bool = False
    test_mode: bool = False  # Skip transcription for testing
    
    def validate(self) -> None:
        """Validate configuration"""
        if not self.test_mode and not self.api_keys and not self.api_key:
            raise ConfigurationError("Either api_keys or api_key must be provided (unless test_mode=True)")
        
        if self.output_dir and not isinstance(self.output_dir, str):
            raise ConfigurationError("output_dir must be a string")
        
        if self.threads < 1:
            raise ConfigurationError("threads must be at least 1")
        
        if self.batch_size < 1:
            raise ConfigurationError("batch_size must be at least 1")
        
        if self.sample_rate < 8000 or self.sample_rate > 48000:
            raise ConfigurationError("sample_rate must be between 8000 and 48000 Hz")
        
        if self.min_segment_length >= self.max_segment_length:
            raise ConfigurationError("min_segment_length must be less than max_segment_length")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CollectorConfig':
        """Create from dictionary"""
        # Filter out unknown keys
        valid_keys = {field.name for field in cls.__dataclass_fields__.values()}
        filtered_data = {k: v for k, v in data.items() if k in valid_keys}
        return cls(**filtered_data)


class ConfigManager:
    """
    Manages configuration loading from various sources:
    1. Environment variables
    2. Configuration files (.json, .yaml)
    3. .env files
    4. Default values
    """
    
    def __init__(self, config_file: Optional[str] = None, load_dotenv_file: bool = True):
        """
        Initialize configuration manager
        
        Args:
            config_file: Path to configuration file
            load_dotenv_file: Whether to load .env file
        """
        self.config_file = config_file
        
        # Load .env file if available
        if load_dotenv_file and DOTENV_AVAILABLE:
            self._load_dotenv()
    
    def _load_dotenv(self) -> None:
        """Load .env file from current directory or parent directories"""
        try:
            # Look for .env file in current directory and parent directories
            env_path = Path('.env')
            if not env_path.exists():
                # Try parent directories
                for parent in Path.cwd().parents:
                    potential_env = parent / '.env'
                    if potential_env.exists():
                        env_path = potential_env
                        break
            
            if env_path.exists():
                load_dotenv(env_path)
                logger.info(f"Loaded environment variables from: {env_path}")
            else:
                logger.debug("No .env file found")
                
        except Exception as e:
            logger.warning(f"Failed to load .env file: {str(e)}")
    
    def load_config(self, **overrides) -> CollectorConfig:
        """
        Load configuration from all sources with precedence:
        1. Function overrides (highest priority)
        2. Environment variables
        3. Configuration file
        4. Default values (lowest priority)
        
        Args:
            **overrides: Configuration overrides
            
        Returns:
            CollectorConfig instance
        """
        config_data = {}
        
        # 1. Load from configuration file
        if self.config_file:
            config_data.update(self._load_config_file())
        
        # 2. Load from environment variables
        config_data.update(self._load_from_env())
        
        # 3. Apply overrides
        config_data.update(overrides)
        
        # Create and validate configuration
        config = CollectorConfig.from_dict(config_data)
        config.validate()
        
        return config
    
    def _load_config_file(self) -> Dict[str, Any]:
        """Load configuration from file"""
        if not self.config_file:
            return {}
        
        config_path = Path(self.config_file)
        if not config_path.exists():
            raise ConfigurationError(f"Configuration file not found: {self.config_file}")
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                if config_path.suffix.lower() == '.json':
                    data = json.load(f)
                elif config_path.suffix.lower() in ['.yaml', '.yml']:
                    try:
                        import yaml
                        data = yaml.safe_load(f)
                    except ImportError:
                        raise ConfigurationError("PyYAML is required to load YAML configuration files")
                else:
                    raise ConfigurationError(f"Unsupported configuration file format: {config_path.suffix}")
            
            logger.info(f"Loaded configuration from: {config_path}")
            return data
            
        except Exception as e:
            raise ConfigurationError(f"Failed to load configuration file: {str(e)}")
    
    def _load_from_env(self) -> Dict[str, Any]:
        """Load configuration from environment variables"""
        config = {}
        
        # Output directory
        if os.getenv('YADC_OUTPUT_DIR'):
            config['output_dir'] = os.getenv('YADC_OUTPUT_DIR')
        
        # API keys
        api_keys = self._load_api_keys_from_env()
        if api_keys:
            if len(api_keys) == 1:
                config['api_key'] = api_keys[0]
            else:
                config['api_keys'] = api_keys
        
        # Processing settings
        env_mappings = {
            'YADC_PREFIX': 'prefix',
            'YADC_SAMPLE_RATE': ('sample_rate', int),
            'YADC_THREADS': ('threads', int),
            'YADC_BATCH_SIZE': ('batch_size', int),
            'YADC_CALLS_PER_MINUTE': ('calls_per_key_per_minute', int),
            'YADC_KEY_COOLDOWN': ('key_cooldown', int),
            'YADC_LANGUAGE': 'language',
            'YADC_COOKIES_PATH': 'cookies_path',
            
            # Segmentation settings
            'YADC_MIN_SEGMENT_LENGTH': ('min_segment_length', int),
            'YADC_MAX_SEGMENT_LENGTH': ('max_segment_length', int),
            'YADC_MIN_SILENCE_LEN': ('min_silence_len', int),
            'YADC_SILENCE_THRESH': ('silence_thresh', int),
            
            # Utility settings
            'YADC_CLEANUP': ('cleanup_intermediate', lambda x: x.lower() in ['true', '1', 'yes']),
            'YADC_KEEP_CONVERTED': ('keep_converted', lambda x: x.lower() in ['true', '1', 'yes']),
            'YADC_VERBOSE': ('verbose', lambda x: x.lower() in ['true', '1', 'yes']),
        }
        
        for env_var, mapping in env_mappings.items():
            value = os.getenv(env_var)
            if value is not None:
                if isinstance(mapping, tuple):
                    key, converter = mapping
                    try:
                        config[key] = converter(value)
                    except (ValueError, TypeError) as e:
                        logger.warning(f"Invalid value for {env_var}: {value}")
                else:
                    config[mapping] = value
        
        if config:
            logger.info(f"Loaded {len(config)} settings from environment variables")
        
        return config
    
    def _load_api_keys_from_env(self) -> List[str]:
        """Load API keys from environment variables"""
        keys = []
        
        # Try single key first
        single_key = os.getenv('GEMINI_API_KEY')
        if single_key:
            keys.append(single_key)
        
        # Try numbered keys
        i = 1
        while True:
            key = os.getenv(f'GEMINI_API_KEY_{i}')
            if not key:
                break
            if key not in keys:  # Avoid duplicates
                keys.append(key)
            i += 1
        
        return keys
    
    def save_config(self, config: CollectorConfig, output_path: str) -> None:
        """
        Save configuration to file
        
        Args:
            config: Configuration to save
            output_path: Path to save configuration
        """
        config_path = Path(output_path)
        config_data = config.to_dict()
        
        try:
            with open(config_path, 'w', encoding='utf-8') as f:
                if config_path.suffix.lower() == '.json':
                    json.dump(config_data, f, indent=2, ensure_ascii=False)
                elif config_path.suffix.lower() in ['.yaml', '.yml']:
                    try:
                        import yaml
                        yaml.dump(config_data, f, default_flow_style=False, allow_unicode=True)
                    except ImportError:
                        raise ConfigurationError("PyYAML is required to save YAML configuration files")
                else:
                    # Default to JSON
                    json.dump(config_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Saved configuration to: {config_path}")
            
        except Exception as e:
            raise ConfigurationError(f"Failed to save configuration: {str(e)}")
    
    @staticmethod
    def create_example_config(output_path: str) -> None:
        """Create an example configuration file"""
        example_config = CollectorConfig(
            output_dir="./dataset",
            api_keys=["your_gemini_api_key_1", "your_gemini_api_key_2"],
            prefix="my_dataset_",
            language="en",
            threads=4,
            batch_size=4
        )
        
        manager = ConfigManager()
        manager.save_config(example_config, output_path)
        print(f"Created example configuration: {output_path}")


def load_config_from_file(config_file: str, **overrides) -> CollectorConfig:
    """
    Convenience function to load configuration from file
    
    Args:
        config_file: Path to configuration file
        **overrides: Configuration overrides
        
    Returns:
        CollectorConfig instance
    """
    manager = ConfigManager(config_file)
    return manager.load_config(**overrides)


def load_config_from_env(**overrides) -> CollectorConfig:
    """
    Convenience function to load configuration from environment
    
    Args:
        **overrides: Configuration overrides
        
    Returns:
        CollectorConfig instance
    """
    manager = ConfigManager()
    return manager.load_config(**overrides)
