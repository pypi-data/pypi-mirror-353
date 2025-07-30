#!/usr/bin/env python3
"""
Command-line interface for YouTube Audio Dataset Collector
"""

import os
import sys
import argparse
import logging
from pathlib import Path
from typing import List, Optional

from . import YouTubeAudioCollector
from .exceptions import YouTubeAudioCollectorError


def setup_logging(verbose: bool = False):
    """Setup logging configuration"""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )


def load_api_keys_from_file(keys_file: str) -> List[str]:
    """Load API keys from a text file (one key per line)"""
    try:
        with open(keys_file, 'r', encoding='utf-8') as f:
            keys = [line.strip() for line in f if line.strip() and not line.startswith('#')]
        return keys
    except FileNotFoundError:
        raise FileNotFoundError(f"API keys file not found: {keys_file}")
    except Exception as e:
        raise RuntimeError(f"Error reading API keys file: {str(e)}")


def load_api_keys_from_env() -> List[str]:
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
        keys.append(key)
        i += 1
    
    return keys


def validate_url(url: str) -> bool:
    """Basic YouTube URL validation"""
    youtube_domains = ['youtube.com', 'youtu.be', 'm.youtube.com']
    return any(domain in url.lower() for domain in youtube_domains)


def create_parser() -> argparse.ArgumentParser:
    """Create command-line argument parser"""
    parser = argparse.ArgumentParser(
        description='YouTube Audio Dataset Collector - Download, process, and transcribe YouTube audio for ML datasets',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  # Basic usage with single video
  youtube-audio-collector -u "https://www.youtube.com/watch?v=VIDEO_ID" -o ./dataset

  # Process playlist with multiple API keys
  youtube-audio-collector -u "https://www.youtube.com/playlist?list=PLAYLIST_ID" \\
                         -o ./dataset -k gemini_keys.txt

  # Advanced options
  youtube-audio-collector -u "https://www.youtube.com/watch?v=VIDEO_ID" \\
                         -o ./dataset -t 8 -b 6 -l kn --cookies cookies.txt

  # Process multiple URLs
  youtube-audio-collector -u "url1" "url2" "url3" -o ./dataset --combine-csv

Supported Languages:
  en (English), kn (Kannada), hi (Hindi), es (Spanish), fr (French), etc.
        '''
    )
    
    # Required arguments
    parser.add_argument(
        '-u', '--url', '--urls',
        nargs='+',
        required=True,
        help='YouTube video or playlist URL(s) to process'
    )
    
    parser.add_argument(
        '-o', '--output',
        required=True,
        help='Output directory for the dataset'
    )
    
    # API key options
    api_group = parser.add_mutually_exclusive_group()
    api_group.add_argument(
        '-k', '--keys-file',
        help='Path to file containing Gemini API keys (one per line)'
    )
    api_group.add_argument(
        '--api-key',
        help='Single Gemini API key'
    )
    
    # Processing options
    parser.add_argument(
        '-l', '--language',
        default='en',
        help='Language code for transcription (default: en)'
    )
    
    parser.add_argument(
        '-p', '--prefix',
        default='',
        help='Prefix for output filenames'
    )
    
    parser.add_argument(
        '-t', '--threads',
        type=int,
        default=4,
        help='Number of processing threads (default: 4)'
    )
    
    parser.add_argument(
        '-b', '--batch-size',
        type=int,
        default=4,
        help='Batch size for transcription (default: 4)'
    )
    
    parser.add_argument(
        '--sample-rate',
        type=int,
        default=16000,
        help='Audio sample rate in Hz (default: 16000)'
    )
    
    # Advanced options
    parser.add_argument(
        '--cookies',
        help='Path to cookies.txt file for accessing restricted content'
    )
    
    parser.add_argument(
        '--calls-per-minute',
        type=int,
        default=15,
        help='API calls per key per minute (default: 15)'
    )
    
    parser.add_argument(
        '--key-cooldown',
        type=int,
        default=60,
        help='Key cooldown period in seconds (default: 60)'
    )
    
    # Multi-URL options
    parser.add_argument(
        '--combine-csv',
        action='store_true',
        help='Combine results from multiple URLs into one CSV file'
    )
    
    # Utility options
    parser.add_argument(
        '--cleanup',
        action='store_true',
        help='Clean up intermediate files after processing'
    )
    
    parser.add_argument(
        '--keep-converted',
        action='store_true',
        help='Keep converted audio files during cleanup'
    )
    
    parser.add_argument(
        '--stats',
        action='store_true',
        help='Show processing statistics after completion'
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='%(prog)s 1.0.0'
    )
    
    return parser


def main():
    """Main entry point for the CLI"""
    parser = create_parser()
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.verbose)
    logger = logging.getLogger(__name__)
    
    try:
        # Validate URLs
        for url in args.url:
            if not validate_url(url):
                logger.warning(f"URL might not be a valid YouTube URL: {url}")
        
        # Load API keys
        api_keys = None
        api_key = None
        
        if args.keys_file:
            api_keys = load_api_keys_from_file(args.keys_file)
            logger.info(f"Loaded {len(api_keys)} API keys from file")
        elif args.api_key:
            api_key = args.api_key
            logger.info("Using single API key")
        else:
            # Try loading from environment
            api_keys = load_api_keys_from_env()
            if api_keys:
                logger.info(f"Loaded {len(api_keys)} API keys from environment")
            else:
                logger.error("No API keys provided. Use --keys-file, --api-key, or set GEMINI_API_KEY environment variable.")
                sys.exit(1)
        
        # Validate cookies file if provided
        if args.cookies and not os.path.exists(args.cookies):
            logger.error(f"Cookies file not found: {args.cookies}")
            sys.exit(1)
        
        # Create output directory
        Path(args.output).mkdir(parents=True, exist_ok=True)
        
        # Initialize collector
        logger.info("Initializing YouTube Audio Collector...")
        collector = YouTubeAudioCollector(
            output_dir=args.output,
            prefix=args.prefix,
            cookies_path=args.cookies,
            api_keys=api_keys,
            api_key=api_key,
            sample_rate=args.sample_rate,
            threads=args.threads,
            batch_size=args.batch_size,
            calls_per_key_per_minute=args.calls_per_minute,
            key_cooldown=args.key_cooldown
        )
        
        # Process URLs
        if len(args.url) == 1:
            # Single URL
            logger.info(f"Processing single URL: {args.url[0]}")
            output_csv = collector.process_url(args.url[0], args.language)
            print(f"✅ Processing completed successfully!")
            print(f"📁 Output CSV: {output_csv}")
            
        else:
            # Multiple URLs
            logger.info(f"Processing {len(args.url)} URLs")
            result = collector.process_multiple_urls(
                args.url, 
                args.language, 
                args.combine_csv
            )
            
            print(f"✅ Processing completed successfully!")
            if args.combine_csv:
                print(f"📁 Combined CSV: {result}")
            else:
                print(f"📁 Individual CSV files:")
                for csv_file in result:
                    print(f"   - {csv_file}")
        
        # Show statistics if requested
        if args.stats:
            stats = collector.get_stats()
            print("\n📊 Processing Statistics:")
            print(f"   Output Directory: {stats['output_directory']}")
            print(f"   Raw Files: {stats.get('raw_files', 0)}")
            print(f"   Converted Files: {stats.get('converted_files', 0)}")
            print(f"   Segments: {stats.get('segments', 0)}")
            
            if 'api_usage' in stats:
                print(f"   API Usage: {stats['api_usage']}")
        
        # Cleanup if requested
        if args.cleanup:
            logger.info("Cleaning up intermediate files...")
            collector.cleanup_intermediate_files(args.keep_converted)
            print("🧹 Cleanup completed")
        
        print(f"\n🎉 All done! Check your dataset in: {args.output}")
        
    except KeyboardInterrupt:
        logger.info("Process interrupted by user")
        sys.exit(130)
    except YouTubeAudioCollectorError as e:
        logger.error(f"Collection error: {str(e)}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
