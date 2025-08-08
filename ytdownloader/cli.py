"""
Command-line interface for ytdownloader.
"""

import os
import sys
from pathlib import Path
from typing import Optional

import click
from rich.console import Console

from .downloader import YouTubeDownloader, validate_youtube_url
from .editor import VideoEditor, parse_time, parse_time_range
from .utils import (
    display_video_info, 
    display_formats_table, 
    generate_output_filename, 
    validate_file_path,
    ensure_directory,
    confirm_action
)


console = Console()


@click.group()
@click.version_option(version="0.1.0", prog_name="ytdownloader")
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output.')
@click.pass_context
def cli(ctx, verbose):
    """
    YouTube Downloader and Video Editor CLI Tool
    
    Download videos from YouTube and perform basic video editing operations.
    
    Examples:
        ytdownloader download "https://youtube.com/watch?v=..."
        ytdownloader edit video.mp4 --trim-start 10
        ytdownloader download "https://youtube.com/watch?v=..." --trim 30-120
    """
    ctx.ensure_object(dict)
    ctx.obj['verbose'] = verbose


@cli.command()
@click.argument('url')
@click.option(
    '--output-dir', '-o', 
    default='downloads', 
    help='Output directory for downloads.',
    type=click.Path()
)
@click.option(
    '--quality', '-q', 
    default='best',
    type=click.Choice(['best', 'worst', '144p', '240p', '360p', '480p', '720p', '1080p', 'audio']),
    help='Video quality preference.'
)
@click.option(
    '--filename', '-f',
    help='Custom filename template (e.g., "%(title)s.%(ext)s").'
)
@click.option(
    '--trim-start', 
    type=float,
    help='Remove N seconds from the beginning.'
)
@click.option(
    '--trim-end',
    type=float, 
    help='Remove N seconds from the end.'
)
@click.option(
    '--trim',
    help='Trim to time range (e.g., "30-120" or "1:30-2:45").'
)
@click.option(
    '--audio-only', '-a',
    is_flag=True,
    help='Download audio only.'
)
@click.option(
    '--info-only', '-i',
    is_flag=True, 
    help='Show video information without downloading.'
)
@click.option(
    '--list-formats', '-l',
    is_flag=True,
    help='List available formats without downloading.'
)
@click.pass_context
def download(ctx, url, output_dir, quality, filename, trim_start, trim_end, trim, audio_only, info_only, list_formats):
    """
    Download a YouTube video.
    
    URL: YouTube video URL to download
    
    Examples:
        ytdownloader download "https://youtube.com/watch?v=dQw4w9WgXcQ"
        ytdownloader download "URL" --quality 720p --output-dir ~/Videos
        ytdownloader download "URL" --trim-start 10 --trim-end 5
        ytdownloader download "URL" --trim "1:30-3:45"
        ytdownloader download "URL" --audio-only
    """
    verbose = ctx.obj.get('verbose', False)
    
    # Validate URL
    if not validate_youtube_url(url):
        console.print("❌ [red]Invalid YouTube URL[/red]")
        console.print("   Supported formats: youtube.com, youtu.be, m.youtube.com")
        sys.exit(1)
    
    # Validate trim options
    trim_options = [trim_start, trim_end, trim]
    if sum(1 for opt in trim_options if opt is not None) > 1:
        console.print("❌ [red]Cannot specify multiple trim options[/red]")
        sys.exit(1)
    
    try:
        # Initialize downloader
        ensure_directory(output_dir)
        downloader = YouTubeDownloader(output_dir=output_dir, quality=quality)
        
        # Get video info
        if verbose:
            console.print(f"📡 Fetching video information...")
        
        video_info = downloader.get_video_info(url)
        
        # Show info only
        if info_only:
            display_video_info(video_info, console)
            return
        
        # List formats only
        if list_formats:
            formats = downloader.list_formats(url)
            display_formats_table(formats, console)
            return
        
        # Download the video
        if audio_only:
            console.print("🎵 [yellow]Audio-only mode enabled[/yellow]")
            downloaded_file = downloader.download_audio_only(url, filename)
        else:
            downloaded_file = downloader.download(url, filename)
        
        # Apply trimming if requested
        if any([trim_start, trim_end, trim]):
            console.print("✂️  [yellow]Applying video trimming...[/yellow]")
            
            editor = VideoEditor()
            
            # Generate output filename for edited video
            edited_file = generate_output_filename(downloaded_file, suffix='_trimmed')
            
            if trim_start is not None:
                editor.remove_start(downloaded_file, edited_file, trim_start)
            elif trim_end is not None:
                editor.remove_end(downloaded_file, edited_file, trim_end)
            elif trim:
                start_time, end_time = parse_time_range(trim)
                duration = None
                if start_time is not None and end_time is not None:
                    duration = end_time - start_time
                    end_time = None  # Use duration instead
                
                editor.trim_video(
                    downloaded_file, 
                    edited_file, 
                    start=start_time, 
                    end=end_time, 
                    duration=duration
                )
            
            # Ask if user wants to keep original
            if not confirm_action("Keep original file?", default=False):
                os.remove(downloaded_file)
                console.print(f"🗑️  Removed original file: {os.path.basename(downloaded_file)}")
        
        console.print("🎉 [green]Download completed successfully![/green]")
        
    except Exception as e:
        console.print(f"❌ [red]Error: {e}[/red]")
        if verbose:
            console.print_exception()
        sys.exit(1)


@cli.command()
@click.argument('input_file', type=click.Path(exists=True))
@click.option(
    '--output', '-o',
    help='Output file path.'
)
@click.option(
    '--trim-start',
    type=float,
    help='Remove N seconds from the beginning.'
)
@click.option(
    '--trim-end', 
    type=float,
    help='Remove N seconds from the end.'
)
@click.option(
    '--trim',
    help='Trim to time range (e.g., "30-120" or "1:30-2:45").'
)
@click.option(
    '--extract-audio', '-a',
    is_flag=True,
    help='Extract audio to separate file.'
)
@click.option(
    '--convert-to',
    type=click.Choice(['mp4', 'avi', 'mkv', 'mov', 'webm']),
    help='Convert to different video format.'
)
@click.option(
    '--resize',
    help='Resize video (e.g., "720p", "1080p", "1280x720").'
)
@click.option(
    '--info', '-i',
    is_flag=True,
    help='Show video file information.'
)
@click.pass_context
def edit(ctx, input_file, output, trim_start, trim_end, trim, extract_audio, convert_to, resize, info):
    """
    Edit a video file.
    
    INPUT_FILE: Path to the video file to edit
    
    Examples:
        ytdownloader edit video.mp4 --trim-start 10
        ytdownloader edit video.mp4 --trim "1:30-3:45" --output edited.mp4
        ytdownloader edit video.mp4 --extract-audio
        ytdownloader edit video.mp4 --convert-to mp4 --resize 720p
    """
    verbose = ctx.obj.get('verbose', False)
    
    # Validate trim options
    trim_options = [trim_start, trim_end, trim]
    if sum(1 for opt in trim_options if opt is not None) > 1:
        console.print("❌ [red]Cannot specify multiple trim options[/red]")
        sys.exit(1)
    
    try:
        editor = VideoEditor()
        
        # Show info only
        if info:
            video_info = editor.get_video_info(input_file)
            display_video_info(video_info, console)
            return
        
        operations = []
        final_output = input_file
        
        # Trim operations
        if trim_start is not None:
            if not output:
                output = generate_output_filename(input_file, suffix='_trimmed')
            editor.remove_start(input_file, output, trim_start)
            operations.append(f"removed {trim_start}s from start")
            final_output = output
            
        elif trim_end is not None:
            if not output:
                output = generate_output_filename(input_file, suffix='_trimmed')
            editor.remove_end(input_file, output, trim_end)
            operations.append(f"removed {trim_end}s from end")
            final_output = output
            
        elif trim:
            if not output:
                output = generate_output_filename(input_file, suffix='_trimmed')
            
            start_time, end_time = parse_time_range(trim)
            duration = None
            if start_time is not None and end_time is not None:
                duration = end_time - start_time
                end_time = None  # Use duration instead
            
            editor.trim_video(input_file, output, start=start_time, end=end_time, duration=duration)
            operations.append(f"trimmed to range {trim}")
            final_output = output
        
        # Conversion operations  
        if convert_to:
            if not output:
                output = generate_output_filename(input_file, suffix='_converted', extension=convert_to)
            elif not output.endswith(f'.{convert_to}'):
                # Add correct extension if not present
                output = f"{os.path.splitext(output)[0]}.{convert_to}"
            
            # Determine appropriate codecs
            codec_map = {
                'mp4': ('libx264', 'aac'),
                'avi': ('libx264', 'mp3'), 
                'mkv': ('libx264', 'aac'),
                'mov': ('libx264', 'aac'),
                'webm': ('libvpx-vp9', 'libopus')
            }
            
            vcodec, acodec = codec_map.get(convert_to, ('libx264', 'aac'))
            editor.convert_format(final_output, output, video_codec=vcodec, audio_codec=acodec)
            operations.append(f"converted to {convert_to}")
            final_output = output
        
        # Resize operations
        if resize:
            if not output:
                output = generate_output_filename(input_file, suffix='_resized')
            
            if resize.endswith('p'):
                # Handle 720p, 1080p format
                editor.resize_video(final_output, output, scale=resize)
            elif 'x' in resize:
                # Handle WIDTHxHEIGHT format
                try:
                    width, height = map(int, resize.split('x'))
                    editor.resize_video(final_output, output, width=width, height=height)
                except ValueError:
                    console.print(f"❌ [red]Invalid resize format: {resize}[/red]")
                    sys.exit(1)
            else:
                console.print(f"❌ [red]Invalid resize format: {resize}. Use '720p' or '1280x720'[/red]")
                sys.exit(1)
            
            operations.append(f"resized to {resize}")
            final_output = output
        
        # Audio extraction
        if extract_audio:
            audio_output = generate_output_filename(input_file, suffix='_audio', extension='mp3')
            editor.extract_audio(final_output, audio_output)
            operations.append("extracted audio")
        
        if operations:
            console.print(f"🎉 [green]Video editing completed![/green]")
            console.print(f"   Operations: {', '.join(operations)}")
            if final_output != input_file:
                console.print(f"   Output: {os.path.basename(final_output)}")
        else:
            console.print("ℹ️  [yellow]No operations specified. Use --help for available options.[/yellow]")
        
    except Exception as e:
        console.print(f"❌ [red]Error: {e}[/red]")
        if verbose:
            console.print_exception()
        sys.exit(1)


@cli.command()
@click.argument('input_file', type=click.Path(exists=True))
@click.option(
    '--format', '-f',
    default='mp3',
    type=click.Choice(['mp3', 'wav', 'aac', 'flac']),
    help='Audio format for extraction.'
)
@click.option(
    '--output', '-o',
    help='Output file path.'
)
@click.pass_context
def extract_audio(ctx, input_file, format, output):
    """
    Extract audio from a video file.
    
    INPUT_FILE: Path to the video file
    
    Examples:
        ytdownloader extract-audio video.mp4
        ytdownloader extract-audio video.mp4 --format wav --output audio.wav
    """
    verbose = ctx.obj.get('verbose', False)
    
    try:
        editor = VideoEditor()
        
        if not output:
            output = generate_output_filename(input_file, suffix='_audio', extension=format)
        
        editor.extract_audio(input_file, output, format=format)
        
        console.print(f"🎉 [green]Audio extraction completed![/green]")
        console.print(f"   Output: {os.path.basename(output)}")
        
    except Exception as e:
        console.print(f"❌ [red]Error: {e}[/red]")
        if verbose:
            console.print_exception()
        sys.exit(1)


@cli.command()
@click.argument('url')
@click.pass_context
def info(ctx, url):
    """
    Show information about a YouTube video without downloading.
    
    URL: YouTube video URL
    
    Examples:
        ytdownloader info "https://youtube.com/watch?v=dQw4w9WgXcQ"
    """
    verbose = ctx.obj.get('verbose', False)
    
    # Validate URL
    if not validate_youtube_url(url):
        console.print("❌ [red]Invalid YouTube URL[/red]")
        sys.exit(1)
    
    try:
        downloader = YouTubeDownloader()
        
        console.print("📡 [yellow]Fetching video information...[/yellow]")
        video_info = downloader.get_video_info(url)
        
        display_video_info(video_info, console)
        
    except Exception as e:
        console.print(f"❌ [red]Error: {e}[/red]")
        if verbose:
            console.print_exception()
        sys.exit(1)


@cli.command()
@click.argument('url')
@click.pass_context  
def formats(ctx, url):
    """
    List available download formats for a YouTube video.
    
    URL: YouTube video URL
    
    Examples:
        ytdownloader formats "https://youtube.com/watch?v=dQw4w9WgXcQ"
    """
    verbose = ctx.obj.get('verbose', False)
    
    # Validate URL
    if not validate_youtube_url(url):
        console.print("❌ [red]Invalid YouTube URL[/red]")
        sys.exit(1)
    
    try:
        downloader = YouTubeDownloader()
        
        console.print("📡 [yellow]Fetching available formats...[/yellow]")
        formats_list = downloader.list_formats(url)
        
        display_formats_table(formats_list, console)
        
    except Exception as e:
        console.print(f"❌ [red]Error: {e}[/red]")
        if verbose:
            console.print_exception()
        sys.exit(1)


def main():
    """Main entry point for the CLI."""
    try:
        cli()
    except KeyboardInterrupt:
        console.print("\n⏹️  [yellow]Operation cancelled by user[/yellow]")
        sys.exit(1)
    except Exception as e:
        console.print(f"❌ [red]Unexpected error: {e}[/red]")
        sys.exit(1)


if __name__ == '__main__':
    main()