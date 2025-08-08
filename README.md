# YouTube Downloader & Video Editor

A powerful command-line tool for downloading YouTube videos and performing basic video editing operations.

## Features

### 🎬 Video Downloading
- Download videos from YouTube in various qualities (144p to 1080p)
- Audio-only downloads with automatic MP3 conversion
- Custom output directories and filename templates
- Progress tracking with rich console output
- Video information display without downloading

### ✂️ Video Editing
- Trim videos (remove start/end seconds or specific time ranges)
- Convert between video formats (MP4, AVI, MKV, MOV, WebM)
- Extract audio from video files
- Resize videos to different resolutions
- Comprehensive video file information display

### 🎯 Combined Operations
- Download and edit in a single command
- Automatic filename generation for edited videos
- Batch processing capabilities

## Installation

### Prerequisites

**FFmpeg is required** for video editing functionality. Install it before using this tool:

#### Windows
1. Download FFmpeg from [https://ffmpeg.org/download.html](https://ffmpeg.org/download.html)
2. Extract and add to your PATH environment variable

#### macOS
```bash
brew install ffmpeg
```

#### Ubuntu/Debian
```bash
sudo apt update
sudo apt install ffmpeg
```

### Install ytdownloader

#### Quick Installation (Recommended)
```bash
# Run the automated installer
chmod +x install.sh
./install.sh
```

#### From Source with uv (Fastest)
```bash
# Install uv if you don't have it
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone and install
git clone <repository-url>
cd ytdownloader
uv venv
source .venv/bin/activate
uv sync
uv pip install -e .
```

#### Using pip (Legacy method)
```bash
git clone <repository-url>
cd ytdownloader
pip install -e .
```

#### Using uv (when published)
```bash
uv add ytdownloader
```

## Quick Start

### Download a YouTube Video
```bash
# Basic download
ytdownloader download "https://youtube.com/watch?v=dQw4w9WgXcQ"

# Download in specific quality
ytdownloader download "URL" --quality 720p

# Download to custom directory
ytdownloader download "URL" --output-dir ~/Videos
```

### Edit a Video File
```bash
# Remove first 10 seconds
ytdownloader edit video.mp4 --trim-start 10

# Trim to specific time range
ytdownloader edit video.mp4 --trim "1:30-3:45"

# Convert format and resize
ytdownloader edit video.mp4 --convert-to mp4 --resize 720p
```

### Combined Download and Edit
```bash
# Download and remove first 10 seconds
ytdownloader download "URL" --trim-start 10

# Download and trim to time range
ytdownloader download "URL" --trim "30-120"
```

## Detailed Usage

### Download Command

```bash
ytdownloader download [OPTIONS] URL
```

**Options:**
- `--output-dir, -o`: Output directory (default: downloads)
- `--quality, -q`: Video quality [best|worst|144p|240p|360p|480p|720p|1080p|audio]
- `--filename, -f`: Custom filename template
- `--trim-start`: Remove N seconds from beginning
- `--trim-end`: Remove N seconds from end  
- `--trim`: Trim to time range (e.g., "30-120" or "1:30-2:45")
- `--audio-only, -a`: Download audio only
- `--info-only, -i`: Show video info without downloading
- `--list-formats, -l`: List available formats

**Examples:**
```bash
# Download best quality
ytdownloader download "https://youtube.com/watch?v=dQw4w9WgXcQ"

# Download 720p quality
ytdownloader download "URL" --quality 720p

# Download and trim first 30 seconds
ytdownloader download "URL" --trim-start 30

# Download audio only
ytdownloader download "URL" --audio-only

# Custom filename and output directory
ytdownloader download "URL" --filename "%(uploader)s - %(title)s.%(ext)s" --output-dir ~/Downloads

# Show video information
ytdownloader download "URL" --info-only

# List available formats
ytdownloader download "URL" --list-formats
```

### Edit Command

```bash
ytdownloader edit [OPTIONS] INPUT_FILE
```

**Options:**
- `--output, -o`: Output file path
- `--trim-start`: Remove N seconds from beginning
- `--trim-end`: Remove N seconds from end
- `--trim`: Trim to time range
- `--extract-audio, -a`: Extract audio to separate file
- `--convert-to`: Convert to format [mp4|avi|mkv|mov|webm]
- `--resize`: Resize video (e.g., "720p", "1080p", "1280x720")
- `--info, -i`: Show video file information

**Examples:**
```bash
# Remove first 10 seconds
ytdownloader edit video.mp4 --trim-start 10

# Trim to time range (1:30 to 3:45)
ytdownloader edit video.mp4 --trim "1:30-3:45"

# Convert to MP4 and resize to 720p
ytdownloader edit video.mkv --convert-to mp4 --resize 720p

# Extract audio
ytdownloader edit video.mp4 --extract-audio

# Multiple operations with custom output
ytdownloader edit input.avi --convert-to mp4 --resize 1080p --output final.mp4

# Show video information
ytdownloader edit video.mp4 --info
```

### Extract Audio Command

```bash
ytdownloader extract-audio [OPTIONS] INPUT_FILE
```

**Options:**
- `--format, -f`: Audio format [mp3|wav|aac|flac] (default: mp3)
- `--output, -o`: Output file path

**Examples:**
```bash
# Extract as MP3 (default)
ytdownloader extract-audio video.mp4

# Extract as WAV
ytdownloader extract-audio video.mp4 --format wav

# Custom output filename
ytdownloader extract-audio video.mp4 --output my_audio.mp3
```

### Info Command

```bash
ytdownloader info URL
```

Show detailed information about a YouTube video without downloading.

**Example:**
```bash
ytdownloader info "https://youtube.com/watch?v=dQw4w9WgXcQ"
```

### Formats Command

```bash
ytdownloader formats URL
```

List all available download formats for a YouTube video.

**Example:**
```bash
ytdownloader formats "https://youtube.com/watch?v=dQw4w9WgXcQ"
```

## Time Format Reference

Time values can be specified in multiple formats:

- **Seconds**: `30` (30 seconds)
- **Minutes:Seconds**: `1:30` (1 minute 30 seconds) 
- **Hours:Minutes:Seconds**: `1:30:45` (1 hour 30 minutes 45 seconds)

Time ranges use the format `start-end`:
- `10-30`: From 10 seconds to 30 seconds
- `1:30-2:45`: From 1:30 to 2:45
- `10-`: From 10 seconds to end
- `-30`: From start to 30 seconds

## Quality Options

### Video Quality
- `best`: Highest available quality
- `worst`: Lowest available quality
- `144p`, `240p`, `360p`, `480p`, `720p`, `1080p`: Specific resolutions
- `audio`: Audio only

### Video Formats
- `mp4`: Most compatible, good quality
- `mkv`: High quality, supports multiple audio tracks
- `avi`: Older format, widely supported
- `mov`: Apple QuickTime format
- `webm`: Web-optimized format

### Audio Formats
- `mp3`: Most compatible
- `wav`: Uncompressed, high quality
- `aac`: Good compression and quality
- `flac`: Lossless compression

## Configuration

### Custom Filename Templates

Use yt-dlp's filename template system:

```bash
# Include uploader and title
--filename "%(uploader)s - %(title)s.%(ext)s"

# Include upload date
--filename "%(upload_date)s - %(title)s.%(ext)s"

# Include video ID
--filename "%(id)s - %(title)s.%(ext)s"
```

Available template fields:
- `%(title)s`: Video title
- `%(uploader)s`: Channel name
- `%(id)s`: Video ID
- `%(upload_date)s`: Upload date (YYYYMMDD)
- `%(duration)s`: Video duration
- `%(view_count)s`: View count
- `%(ext)s`: File extension

## Troubleshooting

### Common Issues

**"FFmpeg not found" error:**
- Install FFmpeg and ensure it's in your PATH
- Test with `ffmpeg -version` in terminal

**YouTube download errors:**
- Check if the URL is valid and accessible
- Some videos may be region-locked or private
- Try updating yt-dlp: `uv pip install --upgrade yt-dlp` (or `pip install --upgrade yt-dlp`)

**Video editing fails:**
- Ensure input file exists and is a valid video
- Check disk space for output file
- Verify FFmpeg installation

**Permission errors:**
- Check write permissions in output directory
- Try running with elevated permissions if needed

### Getting Help

```bash
# General help
ytdownloader --help

# Command-specific help
ytdownloader download --help
ytdownloader edit --help

# Verbose output for debugging
ytdownloader --verbose download "URL"
```

## Advanced Usage

### Batch Processing

Process multiple videos by using shell scripting:

```bash
# Download multiple videos
while IFS= read -r url; do
    ytdownloader download "$url" --quality 720p
done < urls.txt

# Convert multiple files
for file in *.mkv; do
    ytdownloader edit "$file" --convert-to mp4
done
```

### Quality Selection Strategy

The tool uses yt-dlp's format selection:
- `best`: Best video+audio or best combined format
- Specific resolution (e.g., `720p`): Best format at or below that resolution
- `audio`: Best audio-only format, converted to MP3

### Performance Tips

- Use `--quality` to avoid downloading unnecessarily large files
- For batch operations, use lower quality settings to save bandwidth
- Audio-only downloads are much faster for music/podcasts
- Consider available disk space when downloading high-quality videos

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- [yt-dlp](https://github.com/yt-dlp/yt-dlp) - YouTube downloading
- [FFmpeg](https://ffmpeg.org/) - Video processing
- [Click](https://click.palletsprojects.com/) - CLI framework
- [Rich](https://rich.readthedocs.io/) - Terminal formatting