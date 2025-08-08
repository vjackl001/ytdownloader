"""
Video editing functionality using ffmpeg-python.
"""

import os
import sys
from pathlib import Path
from typing import Optional, Tuple, Union
import ffmpeg
from rich.console import Console


class VideoEditor:
    """Handle basic video editing operations with ffmpeg."""
    
    def __init__(self):
        """Initialize the video editor."""
        self.console = Console()
        self._check_ffmpeg()
    
    def _check_ffmpeg(self):
        """Check if ffmpeg is installed and accessible."""
        try:
            ffmpeg.probe('dummy')  # This will fail but tests if ffmpeg is available
        except ffmpeg.Error:
            pass  # Expected error for dummy input
        except FileNotFoundError:
            raise RuntimeError(
                "FFmpeg not found. Please install FFmpeg and ensure it's in your PATH.\n"
                "Installation instructions:\n"
                "- Windows: Download from https://ffmpeg.org/download.html\n"
                "- macOS: brew install ffmpeg\n"
                "- Ubuntu/Debian: sudo apt install ffmpeg"
            )
    
    def get_video_info(self, input_file: str) -> dict:
        """
        Get video file information.
        
        Args:
            input_file: Path to input video file
            
        Returns:
            Video metadata dictionary
        """
        try:
            probe = ffmpeg.probe(input_file)
            video_stream = next(
                (stream for stream in probe['streams'] if stream['codec_type'] == 'video'), 
                None
            )
            audio_stream = next(
                (stream for stream in probe['streams'] if stream['codec_type'] == 'audio'), 
                None
            )
            
            info = {
                'duration': float(probe['format'].get('duration', 0)),
                'size': int(probe['format'].get('size', 0)),
                'format_name': probe['format'].get('format_name', 'unknown'),
            }
            
            if video_stream:
                info.update({
                    'width': int(video_stream.get('width', 0)),
                    'height': int(video_stream.get('height', 0)),
                    'fps': eval(video_stream.get('r_frame_rate', '0/1')),
                    'video_codec': video_stream.get('codec_name', 'unknown'),
                })
            
            if audio_stream:
                info.update({
                    'audio_codec': audio_stream.get('codec_name', 'unknown'),
                    'sample_rate': int(audio_stream.get('sample_rate', 0)),
                    'channels': int(audio_stream.get('channels', 0)),
                })
            
            return info
            
        except Exception as e:
            raise RuntimeError(f"Failed to get video info: {e}")
    
    def trim_video(
        self, 
        input_file: str, 
        output_file: str, 
        start: Optional[float] = None,
        end: Optional[float] = None,
        duration: Optional[float] = None
    ) -> str:
        """
        Trim video to specified time range.
        
        Args:
            input_file: Path to input video file
            output_file: Path to output video file
            start: Start time in seconds (optional)
            end: End time in seconds (optional)
            duration: Duration in seconds from start (optional)
            
        Returns:
            Path to output file
        """
        if not os.path.exists(input_file):
            raise FileNotFoundError(f"Input file not found: {input_file}")
        
        # Validate time parameters
        if start is None and end is None and duration is None:
            raise ValueError("At least one of start, end, or duration must be specified")
        
        if end is not None and duration is not None:
            raise ValueError("Cannot specify both end time and duration")
        
        try:
            input_stream = ffmpeg.input(input_file)
            
            # Build filter arguments
            filter_args = {}
            if start is not None:
                filter_args['start'] = start
            if end is not None:
                filter_args['end'] = end
            if duration is not None:
                filter_args['duration'] = duration
            
            # Apply trim filter
            if filter_args:
                video = input_stream.video.filter('trim', **filter_args).filter('setpts', 'PTS-STARTPTS')
                audio = input_stream.audio.filter('atrim', **filter_args).filter('asetpts', 'PTS-STARTPTS')
            else:
                video = input_stream.video
                audio = input_stream.audio
            
            # Output with re-encoding
            output = ffmpeg.output(
                video, audio, output_file,
                vcodec='libx264',
                acodec='aac',
                **{'avoid_negative_ts': 'make_zero'}
            )
            
            # Run ffmpeg
            self.console.print(f"✂️  Trimming video: {os.path.basename(input_file)}")
            if start is not None:
                self.console.print(f"   Start: {start}s")
            if end is not None:
                self.console.print(f"   End: {end}s")
            if duration is not None:
                self.console.print(f"   Duration: {duration}s")
            
            ffmpeg.run(output, overwrite_output=True, quiet=True)
            
            self.console.print(f"✅ Trimming completed: {os.path.basename(output_file)}")
            return output_file
            
        except ffmpeg.Error as e:
            stderr = e.stderr.decode() if e.stderr else "Unknown error"
            raise RuntimeError(f"FFmpeg error during trimming: {stderr}")
    
    def remove_start(self, input_file: str, output_file: str, seconds: float) -> str:
        """
        Remove the first N seconds from a video.
        
        Args:
            input_file: Path to input video file
            output_file: Path to output video file
            seconds: Number of seconds to remove from start
            
        Returns:
            Path to output file
        """
        return self.trim_video(input_file, output_file, start=seconds)
    
    def remove_end(self, input_file: str, output_file: str, seconds: float) -> str:
        """
        Remove the last N seconds from a video.
        
        Args:
            input_file: Path to input video file
            output_file: Path to output video file
            seconds: Number of seconds to remove from end
            
        Returns:
            Path to output file
        """
        # Get video duration first
        info = self.get_video_info(input_file)
        duration = info['duration']
        end_time = duration - seconds
        
        if end_time <= 0:
            raise ValueError(f"Cannot remove {seconds}s from a {duration}s video")
        
        return self.trim_video(input_file, output_file, end=end_time)
    
    def convert_format(
        self, 
        input_file: str, 
        output_file: str, 
        video_codec: Optional[str] = None,
        audio_codec: Optional[str] = None,
        crf: Optional[int] = None
    ) -> str:
        """
        Convert video to different format/codec.
        
        Args:
            input_file: Path to input video file
            output_file: Path to output video file
            video_codec: Video codec (e.g., 'libx264', 'libx265')
            audio_codec: Audio codec (e.g., 'aac', 'mp3')
            crf: Constant Rate Factor for quality (lower = better quality)
            
        Returns:
            Path to output file
        """
        if not os.path.exists(input_file):
            raise FileNotFoundError(f"Input file not found: {input_file}")
        
        try:
            input_stream = ffmpeg.input(input_file)
            
            # Build output options
            output_options = {}
            if video_codec:
                output_options['vcodec'] = video_codec
            if audio_codec:
                output_options['acodec'] = audio_codec
            if crf is not None:
                output_options['crf'] = crf
            
            output = ffmpeg.output(input_stream, output_file, **output_options)
            
            self.console.print(f"🔄 Converting: {os.path.basename(input_file)}")
            if video_codec:
                self.console.print(f"   Video codec: {video_codec}")
            if audio_codec:
                self.console.print(f"   Audio codec: {audio_codec}")
            
            ffmpeg.run(output, overwrite_output=True, quiet=True)
            
            self.console.print(f"✅ Conversion completed: {os.path.basename(output_file)}")
            return output_file
            
        except ffmpeg.Error as e:
            stderr = e.stderr.decode() if e.stderr else "Unknown error"
            raise RuntimeError(f"FFmpeg error during conversion: {stderr}")
    
    def extract_audio(self, input_file: str, output_file: str, format: str = 'mp3') -> str:
        """
        Extract audio from video file.
        
        Args:
            input_file: Path to input video file
            output_file: Path to output audio file
            format: Audio format (mp3, wav, aac, etc.)
            
        Returns:
            Path to output file
        """
        if not os.path.exists(input_file):
            raise FileNotFoundError(f"Input file not found: {input_file}")
        
        try:
            input_stream = ffmpeg.input(input_file)
            
            # Extract audio only
            output = ffmpeg.output(
                input_stream.audio, 
                output_file,
                acodec='mp3' if format == 'mp3' else format,
                audio_bitrate='192k'
            )
            
            self.console.print(f"🎵 Extracting audio: {os.path.basename(input_file)}")
            
            ffmpeg.run(output, overwrite_output=True, quiet=True)
            
            self.console.print(f"✅ Audio extraction completed: {os.path.basename(output_file)}")
            return output_file
            
        except ffmpeg.Error as e:
            stderr = e.stderr.decode() if e.stderr else "Unknown error"
            raise RuntimeError(f"FFmpeg error during audio extraction: {stderr}")
    
    def resize_video(
        self, 
        input_file: str, 
        output_file: str, 
        width: Optional[int] = None,
        height: Optional[int] = None,
        scale: Optional[str] = None
    ) -> str:
        """
        Resize video to specified dimensions.
        
        Args:
            input_file: Path to input video file
            output_file: Path to output video file
            width: Target width in pixels
            height: Target height in pixels
            scale: Predefined scale (e.g., '720', '1080', 'hd720', 'hd1080')
            
        Returns:
            Path to output file
        """
        if not os.path.exists(input_file):
            raise FileNotFoundError(f"Input file not found: {input_file}")
        
        if not any([width, height, scale]):
            raise ValueError("Must specify width, height, or scale")
        
        try:
            input_stream = ffmpeg.input(input_file)
            
            # Determine scale parameters
            if scale:
                scale_map = {
                    '720': 'hd720',
                    '1080': 'hd1080', 
                    'hd720': 'hd720',
                    'hd1080': 'hd1080',
                    '480': '854:480',
                    '360': '640:360',
                }
                scale_param = scale_map.get(scale, scale)
                video = input_stream.video.filter('scale', scale_param)
            else:
                # Use width/height
                w = width if width else -1
                h = height if height else -1
                video = input_stream.video.filter('scale', w, h)
            
            output = ffmpeg.output(
                video, input_stream.audio, 
                output_file,
                vcodec='libx264',
                acodec='copy'
            )
            
            self.console.print(f"📐 Resizing video: {os.path.basename(input_file)}")
            if scale:
                self.console.print(f"   Scale: {scale}")
            else:
                self.console.print(f"   Dimensions: {width or 'auto'}x{height or 'auto'}")
            
            ffmpeg.run(output, overwrite_output=True, quiet=True)
            
            self.console.print(f"✅ Resize completed: {os.path.basename(output_file)}")
            return output_file
            
        except ffmpeg.Error as e:
            stderr = e.stderr.decode() if e.stderr else "Unknown error"
            raise RuntimeError(f"FFmpeg error during resize: {stderr}")


def parse_time(time_str: str) -> float:
    """
    Parse time string to seconds.
    
    Supports formats like:
    - "30" (30 seconds)
    - "1:30" (1 minute 30 seconds)
    - "1:30:45" (1 hour 30 minutes 45 seconds)
    
    Args:
        time_str: Time string to parse
        
    Returns:
        Time in seconds
    """
    try:
        parts = time_str.split(':')
        if len(parts) == 1:
            return float(parts[0])
        elif len(parts) == 2:
            return float(parts[0]) * 60 + float(parts[1])
        elif len(parts) == 3:
            return float(parts[0]) * 3600 + float(parts[1]) * 60 + float(parts[2])
        else:
            raise ValueError("Invalid time format")
    except ValueError:
        raise ValueError(f"Invalid time format: {time_str}. Use seconds, MM:SS, or HH:MM:SS")


def parse_time_range(time_range: str) -> Tuple[Optional[float], Optional[float]]:
    """
    Parse time range string to start and end times.
    
    Supports formats like:
    - "10-30" (10 seconds to 30 seconds)
    - "1:30-2:45" (1m30s to 2m45s)
    - "10-" (from 10 seconds to end)
    - "-30" (from start to 30 seconds)
    
    Args:
        time_range: Time range string to parse
        
    Returns:
        Tuple of (start_time, end_time) in seconds
    """
    if '-' not in time_range:
        raise ValueError(f"Invalid time range format: {time_range}. Use 'start-end', 'start-', or '-end'")
    
    start_str, end_str = time_range.split('-', 1)
    
    start_time = parse_time(start_str) if start_str else None
    end_time = parse_time(end_str) if end_str else None
    
    return start_time, end_time