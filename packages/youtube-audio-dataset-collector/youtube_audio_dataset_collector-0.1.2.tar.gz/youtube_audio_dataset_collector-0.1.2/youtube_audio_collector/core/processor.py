"""
Audio processor for converting and segmenting audio files for ML datasets.
"""

import os
import subprocess
import logging
from pathlib import Path
from typing import List, Optional, Tuple

from pydub import AudioSegment
from pydub.silence import detect_silence

from ..exceptions import ProcessingError, DependencyError

logger = logging.getLogger(__name__)


class AudioProcessor:
    """
    Processes audio files for machine learning datasets.
    
    Features:
    - Converts audio to specified format (16kHz, 16-bit, mono)
    - Segments audio into chunks based on silence detection
    - Saves processed audio segments
    """
    
    def __init__(self, sample_rate: int = 16000):
        """
        Initialize the audio processor
        
        Args:
            sample_rate: Target sample rate for processed audio
            
        Raises:
            DependencyError: If ffmpeg is not available
        """
        self.sample_rate = sample_rate
        
        # Check if ffmpeg is available
        try:
            subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True)
        except (subprocess.SubprocessError, FileNotFoundError):
            raise DependencyError("ffmpeg not found. Please install ffmpeg before continuing.")
        
        logger.info(f"Initialized Audio Processor (sample rate: {sample_rate}Hz)")
    
    def convert_format(self, audio_path: str, output_dir: str) -> str:
        """
        Convert audio to 16kHz, 16-bit, mono WAV format
        
        Args:
            audio_path: Path to input audio file
            output_dir: Directory to save converted audio
            
        Returns:
            Path to converted audio file
            
        Raises:
            ProcessingError: If conversion fails
        """
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Prepare output filename
        filename = os.path.basename(audio_path)
        name, _ = os.path.splitext(filename)
        output_path = os.path.join(output_dir, f"converted_{name}.wav")
        
        # Prepare ffmpeg command
        cmd = [
            "ffmpeg",
            "-i", audio_path,
            "-ar", str(self.sample_rate),  # Sample rate
            "-ac", "2",  # Stereo
            "-sample_fmt", "s16",  # 16-bit
            "-y",  # Overwrite output file if it exists
            output_path
        ]
        
        # Execute conversion command
        try:
            logger.info(f"Converting audio format: {audio_path}")
            process = subprocess.run(cmd, capture_output=True, text=True, check=True)
            logger.info(f"Conversion completed successfully: {output_path}")
            return output_path
            
        except subprocess.CalledProcessError as e:
            error_msg = f"Error converting audio format: {str(e)}"
            logger.error(error_msg)
            logger.error(f"ffmpeg stdout: {e.stdout}")
            logger.error(f"ffmpeg stderr: {e.stderr}")
            raise ProcessingError(f"Failed to convert audio format: {audio_path}")
    
    def segment_audio(self, 
                     audio_path: str, 
                     output_dir: str, 
                     min_length: int = 12000, 
                     max_length: int = 28000,
                     min_silence_len: int = 500, 
                     silence_thresh: int = -35, 
                     prefix: str = "") -> List[str]:
        """
        Segment audio into chunks based on silence detection
        
        Args:
            audio_path: Path to input audio file
            output_dir: Directory to save segmented audio
            min_length: Minimum segment length in milliseconds (default: 12s)
            max_length: Maximum segment length in milliseconds (default: 28s)
            min_silence_len: Minimum silence length to consider for segmentation (ms)
            silence_thresh: Silence threshold in dB
            prefix: Prefix for output filenames
            
        Returns:
            List of paths to segmented audio files
            
        Raises:
            ProcessingError: If segmentation fails
        """
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        try:
            # Load audio
            logger.info(f"Loading audio for segmentation: {audio_path}")
            audio = AudioSegment.from_file(audio_path)
            
            # Ensure audio is in the correct format
            if audio.frame_rate != self.sample_rate:
                logger.info(f"Resampling audio to {self.sample_rate}Hz")
                audio = audio.set_frame_rate(self.sample_rate)
            
            if audio.channels != 2:
                logger.info("Converting audio to stereo")
                audio = audio.set_channels(2)
            
            # Segment the audio
            segments = self._create_segments(audio, min_length, max_length, min_silence_len, silence_thresh)
            
            # Save segments
            segment_paths = self._save_segments(segments, audio_path, output_dir, prefix)
            
            logger.info(f"Segmentation completed: {len(segment_paths)} segments")
            return segment_paths
            
        except Exception as e:
            logger.error(f"Error segmenting audio: {str(e)}")
            raise ProcessingError(f"Failed to segment audio: {audio_path}")
    
    def _create_segments(self, 
                        audio: AudioSegment, 
                        min_length: int, 
                        max_length: int,
                        min_silence_len: int, 
                        silence_thresh: int) -> List[Tuple[int, int]]:
        """Create segment boundaries based on silence detection"""
        
        # Detect silence
        logger.info("Detecting silence for segmentation")
        silences = detect_silence(audio, min_silence_len=min_silence_len, silence_thresh=silence_thresh)
        
        # Prepare segmentation
        segments = []
        start = 0
        
        for silence_start, silence_end in silences:
            # Check if current segment exceeds minimum length
            if silence_start - start >= min_length:
                # Check if current segment exceeds maximum length
                if silence_start - start <= max_length:
                    # Add segment
                    segments.append((start, silence_start))
                    start = silence_end
                else:
                    # Segment exceeds maximum length, split at maximum length
                    while silence_start - start > max_length:
                        segments.append((start, start + max_length))
                        start += max_length
                    
                    # Add remaining segment if it meets minimum length
                    if silence_start - start >= min_length:
                        segments.append((start, silence_start))
                        start = silence_end
        
        # Add final segment if it meets minimum length
        if len(audio) - start >= min_length:
            segments.append((start, len(audio)))
        
        logger.info(f"Created {len(segments)} segments")
        return segments
    
    def _save_segments(self, 
                      segments: List[Tuple[int, int]], 
                      audio_path: str, 
                      output_dir: str, 
                      prefix: str) -> List[str]:
        """Save audio segments to files"""
        
        # Load the original audio again for segmentation
        audio = AudioSegment.from_file(audio_path)
        
        segment_paths = []
        base_filename = os.path.splitext(os.path.basename(audio_path))[0]
        
        for i, (seg_start, seg_end) in enumerate(segments):
            segment = audio[seg_start:seg_end]
            
            # Prepare output filename
            segment_filename = f"{prefix}{base_filename}_segment_{i+1:03d}.wav"
            segment_path = os.path.join(output_dir, segment_filename)
            
            # Save segment
            logger.debug(f"Saving segment {i+1}/{len(segments)}: {segment_path}")
            segment.export(segment_path, format="wav")
            segment_paths.append(segment_path)
        
        return segment_paths
    
    def get_audio_info(self, audio_path: str) -> dict:
        """
        Get information about an audio file
        
        Args:
            audio_path: Path to audio file
            
        Returns:
            Dictionary with audio information
        """
        try:
            audio = AudioSegment.from_file(audio_path)
            
            return {
                'duration_seconds': len(audio) / 1000.0,
                'duration_ms': len(audio),
                'sample_rate': audio.frame_rate,
                'channels': audio.channels,
                'sample_width': audio.sample_width,
                'frame_count': audio.frame_count(),
                'file_size_bytes': os.path.getsize(audio_path)
            }
            
        except Exception as e:
            raise ProcessingError(f"Failed to get audio info: {str(e)}")
    
    def validate_audio_file(self, audio_path: str) -> bool:
        """
        Validate if a file is a valid audio file
        
        Args:
            audio_path: Path to audio file
            
        Returns:
            True if file is valid audio, False otherwise
        """
        try:
            audio = AudioSegment.from_file(audio_path)
            return len(audio) > 0
        except:
            return False
    
    @staticmethod
    def get_supported_formats() -> List[str]:
        """Get list of supported audio formats"""
        return ['.wav', '.mp3', '.m4a', '.ogg', '.flac', '.aac', '.wma']
