"""
Main YouTube Audio Dataset Collector class that orchestrates all components.
"""

import os
import csv
import logging
import concurrent.futures
from pathlib import Path
from typing import List, Optional, Union

from .downloader import YouTubeDownloader
from .processor import AudioProcessor
from .transcriber import TranscriptionService
from .api_manager import APIKeyManager
from ..config import CollectorConfig
from ..exceptions import YouTubeAudioCollectorError, ConfigurationError

logger = logging.getLogger(__name__)


class YouTubeAudioCollector:
    """
    Main class for YouTube Audio Dataset Collector.
    
    This class orchestrates the complete pipeline:
    1. Downloads audio from YouTube videos/playlists
    2. Converts audio to specified format (16kHz, 16-bit, stereo)
    3. Segments audio into chunks based on silence detection
    4. Transcribes audio using Gemini API with multiple key rotation
    5. Exports results in CSV format
    
    Features:
    - Multi-threaded processing for efficiency
    - API key rotation to avoid rate limits
    - Intelligent audio segmentation
    - Comprehensive error handling
    """
    
    def __init__(self, 
                 config: Optional[CollectorConfig] = None,
                 output_dir: Optional[str] = None, 
                 prefix: str = "", 
                 cookies_path: Optional[str] = None,
                 api_keys: Optional[List[str]] = None, 
                 api_key: Optional[str] = None,
                 sample_rate: int = 16000, 
                 threads: int = 4, 
                 batch_size: int = 4,
                 calls_per_key_per_minute: int = 15, 
                 key_cooldown: int = 60,
                 test_mode: bool = False):
        """
        Initialize the YouTube Audio Collector
        
        Args:
            config: CollectorConfig object (preferred method)
            output_dir: Directory to save output files (if config not provided)
            prefix: Prefix for output filenames
            cookies_path: Path to cookies.txt file for authentication
            api_keys: List of Gemini API keys for rotation
            api_key: Single Gemini API key (used if api_keys is not provided)
            sample_rate: Target sample rate for processed audio
            threads: Number of threads for parallel processing
            batch_size: Batch size for transcription
            calls_per_key_per_minute: Maximum calls allowed per key per minute
            key_cooldown: Cooldown period in seconds after a key hits rate limit
            test_mode: Skip transcription for testing purposes
            
        Raises:
            ConfigurationError: If neither api_keys nor api_key is provided (unless test_mode=True)
        """
        # Handle config object vs individual parameters
        if config:
            config.validate()
            self.config = config
            output_dir = config.output_dir
            prefix = config.prefix
            cookies_path = config.cookies_path
            api_keys = config.api_keys
            api_key = config.api_key
            sample_rate = config.sample_rate
            threads = config.threads
            batch_size = config.batch_size
            calls_per_key_per_minute = config.calls_per_key_per_minute
            key_cooldown = config.key_cooldown
            test_mode = config.test_mode
        else:
            # Create config from individual parameters
            if not output_dir:
                raise ConfigurationError("output_dir must be provided if config is not specified")
            self.config = CollectorConfig(
                output_dir=output_dir,
                prefix=prefix,
                cookies_path=cookies_path,
                api_keys=api_keys,
                api_key=api_key,
                sample_rate=sample_rate,
                threads=threads,
                batch_size=batch_size,
                calls_per_key_per_minute=calls_per_key_per_minute,
                key_cooldown=key_cooldown,
                test_mode=test_mode
            )
            self.config.validate()
        
        # Validate configuration (unless in test mode)
        if not test_mode and not api_keys and not api_key:
            raise ConfigurationError("Either api_keys or api_key must be provided (unless test_mode=True)")
        
        # Store configuration
        self.output_dir = output_dir
        self.prefix = prefix if prefix.endswith("_") or not prefix else f"{prefix}_"
        self.cookies_path = cookies_path
        self.threads = threads
        self.batch_size = batch_size
        self.test_mode = test_mode
        
        # Create output directories
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        self.raw_dir = os.path.join(output_dir, f"{self.prefix}raw")
        self.converted_dir = os.path.join(output_dir, f"{self.prefix}converted")
        self.segments_dir = os.path.join(output_dir, f"{self.prefix}segments")
        
        for directory in [self.raw_dir, self.converted_dir, self.segments_dir]:
            Path(directory).mkdir(parents=True, exist_ok=True)
        
        # Initialize components
        self.downloader = YouTubeDownloader(cookies_path=cookies_path)
        self.processor = AudioProcessor(sample_rate=sample_rate)
        
        # Initialize transcription service (skip if in test mode)
        if not test_mode:
            if api_keys:
                self.api_key_manager = APIKeyManager(
                    api_keys=api_keys,
                    calls_per_key_per_minute=calls_per_key_per_minute,
                    cooldown_period=key_cooldown
                )
                self.transcriber = TranscriptionService(api_key_manager=self.api_key_manager)
            else:
                self.transcriber = TranscriptionService(api_key=api_key)
        else:
            self.transcriber = None
            logger.info("Test mode enabled - transcription will be skipped")
        
        logger.info(f"Initialized YouTube Audio Collector")
        logger.info(f"Output directory: {output_dir}")
        logger.info(f"Processing threads: {threads}")
        logger.info(f"Transcription batch size: {batch_size}")
    
    def process_url(self, url: str, language: str = "en") -> str:
        """
        Process a YouTube URL to create a labeled audio dataset
        
        Args:
            url: YouTube video or playlist URL
            language: Language code for transcription (e.g., 'en', 'kn', 'hi')
            
        Returns:
            Path to the output CSV file containing audio_filepath and transcript columns
            
        Raises:
            YouTubeAudioCollectorError: If any step in the pipeline fails
        """
        try:
            logger.info(f"Starting processing of URL: {url}")
            logger.info(f"Language: {language}")
            
            # Step 1: Download audio
            logger.info("Step 1: Downloading audio")
            raw_audio_files = self.downloader.download_audio(
                url=url,
                output_dir=self.raw_dir,
                prefix=self.prefix
            )
            logger.info(f"Downloaded {len(raw_audio_files)} audio files")
            
            # Step 2: Convert audio format
            logger.info("Step 2: Converting audio format")
            converted_audio_files = []
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=self.threads) as executor:
                conversion_futures = {
                    executor.submit(
                        self.processor.convert_format,
                        audio_path=audio_file,
                        output_dir=self.converted_dir
                    ): audio_file for audio_file in raw_audio_files
                }
                
                for future in concurrent.futures.as_completed(conversion_futures):
                    try:
                        converted_file = future.result()
                        converted_audio_files.append(converted_file)
                        logger.info(f"Converted: {os.path.basename(converted_file)}")
                    except Exception as e:
                        original_file = conversion_futures[future]
                        logger.error(f"Error converting {original_file}: {str(e)}")
            
            logger.info(f"Converted {len(converted_audio_files)} audio files")
            
            # Step 3: Segment audio
            logger.info("Step 3: Segmenting audio")
            all_segments = []
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=self.threads) as executor:
                segmentation_futures = []
                
                for audio_file in converted_audio_files:
                    future = executor.submit(
                        self.processor.segment_audio,
                        audio_path=audio_file,
                        output_dir=self.segments_dir,
                        min_length=12000,  # 12 seconds
                        max_length=28000,  # 28 seconds
                        min_silence_len=500,  # 500ms
                        silence_thresh=-35,  # -35dB
                        prefix=self.prefix
                    )
                    segmentation_futures.append(future)
                
                # Collect segments
                for future in concurrent.futures.as_completed(segmentation_futures):
                    try:
                        segments = future.result()
                        all_segments.extend(segments)
                        logger.info(f"Segmented into {len(segments)} chunks")
                    except Exception as e:
                        logger.error(f"Error segmenting audio: {str(e)}")
            
            logger.info(f"Total segments created: {len(all_segments)}")
            
            # Step 4: Transcribe segments (or skip in test mode)
            if self.test_mode:
                logger.info(f"Step 4: Skipping transcription (test mode) for {len(all_segments)} segments")
                transcriptions = [(segment, f"TEST_MODE_TRANSCRIPT_{os.path.basename(segment)}") for segment in all_segments]
            else:
                logger.info(f"Step 4: Transcribing {len(all_segments)} segments")
                transcriptions = []
                
                with concurrent.futures.ThreadPoolExecutor(max_workers=self.threads) as executor:
                    # Process in batches to manage API rate limits
                    for i in range(0, len(all_segments), self.batch_size):
                        batch = all_segments[i:i + self.batch_size]
                        logger.info(f"Processing batch {i//self.batch_size + 1}/{(len(all_segments)-1)//self.batch_size + 1}")
                        
                        # Submit transcription tasks
                        transcription_futures = {
                            executor.submit(
                                self.transcriber.transcribe_audio,
                                audio_path=segment,
                                language=language
                            ): segment for segment in batch
                        }
                        
                        # Collect transcriptions
                        for future in concurrent.futures.as_completed(transcription_futures):
                            segment = transcription_futures[future]
                            try:
                                transcript = future.result()
                                transcriptions.append((segment, transcript))
                                logger.info(f"Transcribed: {os.path.basename(segment)}")
                            except Exception as e:
                                logger.error(f"Error transcribing {segment}: {str(e)}")
                                transcriptions.append((segment, f"ERROR: {str(e)}"))
                
                logger.info(f"Transcribed {len(transcriptions)} segments")
            
            # Step 5: Export CSV
            logger.info("Step 5: Exporting CSV")
            output_csv = os.path.join(self.output_dir, f"{self.prefix}transcriptions.csv")
            
            with open(output_csv, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(['audio_filepath', 'transcript'])
                
                for segment, transcript in transcriptions:
                    # Use relative path for portability
                    relative_path = os.path.relpath(segment, self.output_dir)
                    writer.writerow([relative_path, transcript])
            
            logger.info(f"Processing completed successfully")
            logger.info(f"Output CSV: {output_csv}")
            logger.info(f"Total transcriptions: {len(transcriptions)}")
            
            return output_csv
            
        except Exception as e:
            error_msg = f"Error processing URL {url}: {str(e)}"
            logger.error(error_msg)
            raise YouTubeAudioCollectorError(error_msg) from e
    
    def process_multiple_urls(self, 
                             urls: List[str], 
                             language: str = "en",
                             combined_csv: bool = True) -> Union[str, List[str]]:
        """
        Process multiple YouTube URLs
        
        Args:
            urls: List of YouTube URLs to process
            language: Language code for transcription
            combined_csv: If True, combine all results into one CSV file
            
        Returns:
            Path to combined CSV file or list of individual CSV files
        """
        try:
            logger.info(f"Processing {len(urls)} URLs")
            
            csv_files = []
            all_transcriptions = []
            
            for i, url in enumerate(urls, 1):
                logger.info(f"Processing URL {i}/{len(urls)}: {url}")
                
                try:
                    # Create subdirectory for this URL
                    url_dir = os.path.join(self.output_dir, f"url_{i:03d}")
                    temp_collector = YouTubeAudioCollector(
                        output_dir=url_dir,
                        prefix=self.prefix,
                        cookies_path=self.cookies_path,
                        api_keys=getattr(self, 'api_key_manager', None) and self.api_key_manager.api_keys,
                        api_key=getattr(self.transcriber, 'api_key', None) if not hasattr(self, 'api_key_manager') else None,
                        threads=self.threads,
                        batch_size=self.batch_size
                    )
                    
                    csv_file = temp_collector.process_url(url, language)
                    csv_files.append(csv_file)
                    
                    # If combining, read transcriptions
                    if combined_csv:
                        with open(csv_file, 'r', encoding='utf-8') as f:
                            reader = csv.reader(f)
                            next(reader)  # Skip header
                            for row in reader:
                                # Adjust path to be relative to main output directory
                                audio_path = os.path.join(f"url_{i:03d}", row[0])
                                all_transcriptions.append((audio_path, row[1]))
                    
                except Exception as e:
                    logger.error(f"Error processing URL {url}: {str(e)}")
                    continue
            
            if combined_csv and all_transcriptions:
                # Create combined CSV
                combined_csv_path = os.path.join(self.output_dir, f"{self.prefix}combined_transcriptions.csv")
                with open(combined_csv_path, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(['audio_filepath', 'transcript'])
                    writer.writerows(all_transcriptions)
                
                logger.info(f"Created combined CSV: {combined_csv_path}")
                return combined_csv_path
            
            return csv_files
            
        except Exception as e:
            error_msg = f"Error processing multiple URLs: {str(e)}"
            logger.error(error_msg)
            raise YouTubeAudioCollectorError(error_msg) from e
    
    def get_stats(self) -> dict:
        """
        Get statistics about the collection process
        
        Returns:
            Dictionary with processing statistics
        """
        stats = {
            'output_directory': self.output_dir,
            'configuration': {
                'prefix': self.prefix,
                'threads': self.threads,
                'batch_size': self.batch_size,
                'cookies_enabled': self.cookies_path is not None
            }
        }
        
        # Add API key manager stats if available (and not in test mode)
        if hasattr(self, 'api_key_manager') and not self.test_mode:
            api_stats = self.transcriber.get_api_stats()
            if api_stats:
                stats['api_usage'] = api_stats
        elif self.test_mode:
            stats['api_usage'] = {'test_mode': True, 'transcription_skipped': True}
        
        # Count files in directories
        for name, directory in [
            ('raw_files', self.raw_dir),
            ('converted_files', self.converted_dir),
            ('segments', self.segments_dir)
        ]:
            if os.path.exists(directory):
                audio_files = []
                for ext in ['.wav', '.mp3', '.m4a', '.ogg', '.flac']:
                    audio_files.extend(Path(directory).glob(f"*{ext}"))
                stats[name] = len(audio_files)
            else:
                stats[name] = 0
        
        return stats
    
    def cleanup_intermediate_files(self, keep_converted: bool = False):
        """
        Clean up intermediate files to save disk space
        
        Args:
            keep_converted: If True, keep converted audio files
        """
        try:
            logger.info("Cleaning up intermediate files")
            
            # Always clean up raw files (largest)
            if os.path.exists(self.raw_dir):
                import shutil
                shutil.rmtree(self.raw_dir)
                logger.info("Removed raw audio files")
            
            # Optionally clean up converted files
            if not keep_converted and os.path.exists(self.converted_dir):
                import shutil
                shutil.rmtree(self.converted_dir)
                logger.info("Removed converted audio files")
            
            logger.info("Cleanup completed")
            
        except Exception as e:
            logger.warning(f"Error during cleanup: {str(e)}")
