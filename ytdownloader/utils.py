"""
Utility functions for ytdownloader.
"""

import os
import re
from pathlib import Path
from typing import Optional, Union
from rich.console import Console
from rich.table import Table


def format_filesize(size_bytes: Union[int, str, None]) -> str:
    """
    Format file size in human readable format.
    
    Args:
        size_bytes: Size in bytes
        
    Returns:
        Formatted size string
    """
    if size_bytes is None or size_bytes == '':
        return 'Unknown'
    
    try:
        size = int(size_bytes)
    except (ValueError, TypeError):
        return 'Unknown'
    
    if size == 0:
        return '0 B'
    
    size_names = ['B', 'KB', 'MB', 'GB', 'TB']
    i = 0
    while size >= 1024 and i < len(size_names) - 1:
        size /= 1024.0
        i += 1
    
    return f"{size:.1f} {size_names[i]}"


def format_duration(seconds: Union[float, int, None]) -> str:
    """
    Format duration in human readable format.
    
    Args:
        seconds: Duration in seconds
        
    Returns:
        Formatted duration string (HH:MM:SS or MM:SS)
    """
    if seconds is None:
        return 'Unknown'
    
    try:
        total_seconds = int(float(seconds))
    except (ValueError, TypeError):
        return 'Unknown'
    
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    secs = total_seconds % 60
    
    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    else:
        return f"{minutes:02d}:{secs:02d}"


def sanitize_filename(filename: str, max_length: int = 255) -> str:
    """
    Sanitize filename for cross-platform compatibility.
    
    Args:
        filename: Original filename
        max_length: Maximum filename length
        
    Returns:
        Sanitized filename
    """
    # Remove or replace invalid characters
    sanitized = re.sub(r'[<>:"/\\|?*]', '_', filename)
    
    # Remove control characters
    sanitized = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', sanitized)
    
    # Trim whitespace and dots from ends
    sanitized = sanitized.strip(' .')
    
    # Ensure it's not empty
    if not sanitized:
        sanitized = 'video'
    
    # Truncate if too long
    if len(sanitized) > max_length:
        name, ext = os.path.splitext(sanitized)
        max_name_length = max_length - len(ext)
        sanitized = name[:max_name_length] + ext
    
    return sanitized


def generate_output_filename(
    input_file: str, 
    suffix: str = '_edited', 
    extension: Optional[str] = None,
    output_dir: Optional[str] = None
) -> str:
    """
    Generate output filename based on input filename.
    
    Args:
        input_file: Path to input file
        suffix: Suffix to add to filename
        extension: New extension (optional)
        output_dir: Output directory (optional)
        
    Returns:
        Generated output filename
    """
    input_path = Path(input_file)
    
    # Base name without extension
    base_name = input_path.stem
    
    # Use provided extension or keep original
    ext = extension if extension else input_path.suffix
    if not ext.startswith('.'):
        ext = f'.{ext}'
    
    # Generate new filename
    new_filename = f"{base_name}{suffix}{ext}"
    
    # Use provided output directory or same as input
    if output_dir:
        output_path = Path(output_dir) / new_filename
    else:
        output_path = input_path.parent / new_filename
    
    return str(output_path)


def display_video_info(info: dict, console: Optional[Console] = None) -> None:
    """
    Display video information in a formatted table.
    
    Args:
        info: Video information dictionary
        console: Rich console instance (optional)
    """
    if console is None:
        console = Console()
    
    table = Table(title="Video Information")
    table.add_column("Property", style="cyan", no_wrap=True)
    table.add_column("Value", style="white")
    
    # Add basic info
    if 'title' in info:
        table.add_row("Title", info['title'])
    
    if 'uploader' in info:
        table.add_row("Uploader", info['uploader'])
    
    if 'duration' in info:
        table.add_row("Duration", format_duration(info['duration']))
    
    if 'view_count' in info:
        table.add_row("Views", f"{info['view_count']:,}")
    
    if 'upload_date' in info:
        date_str = info['upload_date']
        if len(date_str) == 8:  # YYYYMMDD format
            formatted_date = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}"
            table.add_row("Upload Date", formatted_date)
    
    # Video specs
    if 'width' in info and 'height' in info:
        table.add_row("Resolution", f"{info['width']}x{info['height']}")
    
    if 'fps' in info:
        table.add_row("FPS", f"{info['fps']:.1f}")
    
    if 'video_codec' in info:
        table.add_row("Video Codec", info['video_codec'])
    
    if 'audio_codec' in info:
        table.add_row("Audio Codec", info['audio_codec'])
    
    if 'filesize' in info:
        table.add_row("File Size", format_filesize(info['filesize']))
    
    console.print(table)


def display_formats_table(formats: list, console: Optional[Console] = None) -> None:
    """
    Display available formats in a formatted table.
    
    Args:
        formats: List of format dictionaries
        console: Rich console instance (optional)
    """
    if console is None:
        console = Console()
    
    table = Table(title="Available Formats")
    table.add_column("Format ID", style="cyan", no_wrap=True)
    table.add_column("Extension", style="yellow")
    table.add_column("Resolution", style="green")
    table.add_column("File Size", style="blue")
    table.add_column("Video Codec", style="magenta")
    table.add_column("Audio Codec", style="red")
    
    for fmt in formats:
        table.add_row(
            fmt.get('format_id', 'unknown'),
            fmt.get('ext', 'unknown'),
            fmt.get('resolution', 'unknown'),
            format_filesize(fmt.get('filesize')),
            fmt.get('vcodec', 'none'),
            fmt.get('acodec', 'none')
        )
    
    console.print(table)


def validate_file_path(file_path: str, must_exist: bool = True) -> bool:
    """
    Validate file path.
    
    Args:
        file_path: Path to validate
        must_exist: Whether file must exist
        
    Returns:
        True if valid, False otherwise
    """
    try:
        path = Path(file_path)
        
        if must_exist and not path.exists():
            return False
        
        if must_exist and not path.is_file():
            return False
        
        # Check if parent directory exists (for output files)
        if not must_exist and not path.parent.exists():
            return False
        
        return True
        
    except Exception:
        return False


def ensure_directory(directory: str) -> None:
    """
    Ensure directory exists, create if it doesn't.
    
    Args:
        directory: Directory path to ensure
    """
    Path(directory).mkdir(parents=True, exist_ok=True)


def get_file_extension_from_url(url: str) -> str:
    """
    Extract file extension from URL or return default.
    
    Args:
        url: URL to analyze
        
    Returns:
        File extension (with dot)
    """
    try:
        path = Path(url)
        ext = path.suffix
        if ext in ['.mp4', '.webm', '.mkv', '.avi', '.mov', '.flv']:
            return ext
    except Exception:
        pass
    
    return '.mp4'  # Default


def confirm_action(message: str, default: bool = False) -> bool:
    """
    Ask user for confirmation.
    
    Args:
        message: Confirmation message
        default: Default response if user just presses enter
        
    Returns:
        True if confirmed, False otherwise
    """
    suffix = " [Y/n]" if default else " [y/N]"
    
    try:
        response = input(f"{message}{suffix}: ").lower().strip()
        
        if not response:
            return default
        
        return response in ['y', 'yes', 'true', '1']
        
    except (KeyboardInterrupt, EOFError):
        return False