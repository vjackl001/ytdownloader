# ytdownloader Examples

This file contains practical examples of using the ytdownloader CLI tool.

## Installation Examples

### Quick Installation with uv (Recommended)
```bash
# Install uv if not already installed
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone and install ytdownloader
git clone https://github.com/vjackl001/ytdownloader.git
cd ytdownloader
chmod +x install.sh
./install.sh
```

### Manual Installation with uv
```bash
# Create virtual environment and install
uv venv
source .venv/bin/activate
uv sync
uv pip install -e .

# Verify installation
ytdownloader --version
```

## Basic Download Examples

### Download a video in best quality
```bash
ytdownloader download "https://youtube.com/watch?v=dQw4w9WgXcQ"
```

### Download in specific quality
```bash
# Download in 720p
ytdownloader download "https://youtube.com/watch?v=dQw4w9WgXcQ" --quality 720p

# Download in 480p
ytdownloader download "URL" --quality 480p

# Download worst quality (saves bandwidth)
ytdownloader download "URL" --quality worst
```

### Custom output directory
```bash
# Download to specific folder
ytdownloader download "URL" --output-dir ~/Videos

# Download to current directory
ytdownloader download "URL" --output-dir .
```

### Audio-only downloads
```bash
# Download audio only (converted to MP3)
ytdownloader download "URL" --audio-only

# Download audio in specific quality
ytdownloader download "URL" --audio-only --quality best
```

## Video Information Examples

### Get video information without downloading
```bash
ytdownloader info "https://youtube.com/watch?v=dQw4w9WgXcQ"
```

### List all available formats
```bash
ytdownloader formats "https://youtube.com/watch?v=dQw4w9WgXcQ"
```

### Quick info during download
```bash
ytdownloader download "URL" --info-only
```

## Download with Editing Examples

### Remove sections from downloaded video
```bash
# Remove first 10 seconds
ytdownloader download "URL" --trim-start 10

# Remove last 5 seconds
ytdownloader download "URL" --trim-end 5

# Remove both start and end (download, then edit)
ytdownloader download "URL" --trim-start 10
ytdownloader edit downloaded_video.mp4 --trim-end 5
```

### Trim to specific time ranges
```bash
# Keep only seconds 30-120 (1.5 minutes of content)
ytdownloader download "URL" --trim "30-120"

# Keep from 1:30 to 3:45 (MM:SS format)
ytdownloader download "URL" --trim "1:30-3:45"

# Keep from 2 minutes to end
ytdownloader download "URL" --trim "120-"

# Keep from start to 1 minute
ytdownloader download "URL" --trim "-60"
```

## Video Editing Examples

### Basic trimming operations
```bash
# Remove first 15 seconds from existing video
ytdownloader edit video.mp4 --trim-start 15

# Remove last 10 seconds
ytdownloader edit video.mp4 --trim-end 10

# Keep only middle section (30s to 90s)
ytdownloader edit video.mp4 --trim "30-90"
```

### Format conversion
```bash
# Convert MKV to MP4
ytdownloader edit video.mkv --convert-to mp4

# Convert to WebM for web use
ytdownloader edit video.mp4 --convert-to webm

# Convert AVI to MP4 with custom output name
ytdownloader edit old_video.avi --convert-to mp4 --output new_video.mp4
```

### Video resizing
```bash
# Resize to 720p
ytdownloader edit video.mp4 --resize 720p

# Resize to 1080p
ytdownloader edit video.mp4 --resize 1080p

# Resize to specific dimensions
ytdownloader edit video.mp4 --resize 1280x720

# Resize and convert format
ytdownloader edit video.mkv --resize 720p --convert-to mp4
```

### Audio extraction
```bash
# Extract audio as MP3 (default)
ytdownloader edit video.mp4 --extract-audio

# Extract as WAV for high quality
ytdownloader extract-audio video.mp4 --format wav

# Extract as AAC
ytdownloader extract-audio video.mp4 --format aac --output audio.aac
```

## Complex Combined Operations

### Download, trim, and convert in sequence
```bash
# Download video
ytdownloader download "URL" --quality 720p --output-dir ./temp

# Edit the downloaded video
ytdownloader edit ./temp/video.mp4 --trim "10-120" --convert-to mp4 --resize 480p --output final_video.mp4

# Extract audio from final video
ytdownloader extract-audio final_video.mp4
```

### Batch processing with shell scripts

#### Download multiple videos from a list
```bash
# Create urls.txt with one URL per line
cat > urls.txt << EOF
https://youtube.com/watch?v=dQw4w9WgXcQ
https://youtube.com/watch?v=another_video
https://youtube.com/watch?v=third_video
EOF

# Download all videos
while IFS= read -r url; do
    echo "Downloading: $url"
    ytdownloader download "$url" --quality 720p --output-dir ./downloads
done < urls.txt
```

#### Convert all MKV files to MP4
```bash
# Convert all MKV files in current directory
for file in *.mkv; do
    if [ -f "$file" ]; then
        echo "Converting: $file"
        ytdownloader edit "$file" --convert-to mp4
    fi
done
```

#### Trim all videos in a folder
```bash
# Remove first 10 seconds from all MP4 files
for file in *.mp4; do
    if [ -f "$file" ]; then
        echo "Trimming: $file"
        ytdownloader edit "$file" --trim-start 10 --output "trimmed_$file"
    fi
done
```

## Custom Filename Templates

### Use uploader name in filename
```bash
ytdownloader download "URL" --filename "%(uploader)s - %(title)s.%(ext)s"
```

### Include upload date
```bash
ytdownloader download "URL" --filename "%(upload_date)s - %(title)s.%(ext)s"
```

### Create organized structure
```bash
# Download to subfolder named after uploader
mkdir -p downloads/%(uploader)s
ytdownloader download "URL" --filename "downloads/%(uploader)s/%(title)s.%(ext)s"
```

## Troubleshooting Examples

### Verbose output for debugging
```bash
# Enable verbose output to see detailed information
ytdownloader --verbose download "URL"
ytdownloader --verbose edit video.mp4 --trim-start 10
```

### Check video information before processing
```bash
# Check video info to plan editing
ytdownloader edit video.mp4 --info

# Check available formats before downloading
ytdownloader formats "URL"
```

### Handle special characters in filenames
```bash
# Use quotes for URLs with special characters
ytdownloader download "https://youtube.com/watch?v=dQw4w9WgXcQ&t=30s"

# Use custom filename for problematic titles
ytdownloader download "URL" --filename "my_video_%(id)s.%(ext)s"
```

## Performance Optimization Examples

### Bandwidth-conscious downloading
```bash
# Download lowest quality to save bandwidth
ytdownloader download "URL" --quality worst

# Download audio only for podcasts/music
ytdownloader download "URL" --audio-only

# Download specific format if you know what you need
ytdownloader formats "URL"  # Check available formats first
ytdownloader download "URL" --quality 360p  # Choose appropriate quality
```

### Disk space management
```bash
# Download to temporary location
ytdownloader download "URL" --output-dir /tmp/videos

# Process and clean up
ytdownloader edit /tmp/videos/video.mp4 --trim "60-180" --output final_video.mp4
rm /tmp/videos/video.mp4  # Remove original
```

## Educational/Research Use Cases

### Create clips for presentations
```bash
# Download a lecture/tutorial
ytdownloader download "EDUCATION_URL" --quality 720p

# Extract specific segments
ytdownloader edit lecture.mp4 --trim "5:30-8:45" --output intro_clip.mp4
ytdownloader edit lecture.mp4 --trim "15:00-18:30" --output main_concept.mp4
ytdownloader edit lecture.mp4 --trim "25:00-27:00" --output conclusion.mp4
```

### Extract audio for transcription
```bash
# Download and extract audio for transcription services
ytdownloader download "INTERVIEW_URL" --audio-only
# Audio will be saved as MP3 file ready for transcription
```

### Create preview clips
```bash
# Create 30-second preview from beginning
ytdownloader edit full_video.mp4 --trim "0-30" --output preview.mp4

# Create highlight reel from multiple segments
ytdownloader edit video.mp4 --trim "2:15-2:45" --output highlight1.mp4
ytdownloader edit video.mp4 --trim "8:30-9:00" --output highlight2.mp4
```

## Integration Examples

### Use with other tools
```bash
# Download and immediately upload to cloud storage
ytdownloader download "URL" --output-dir ./temp
rsync ./temp/ user@server:/videos/
rm -rf ./temp/

# Download, edit, and prepare for streaming
ytdownloader download "URL" --quality 1080p
ytdownloader edit video.mp4 --convert-to mp4 --resize 720p --output stream_ready.mp4
```

### Automation with cron jobs
```bash
# Add to crontab for scheduled downloads
# crontab -e
# 0 2 * * * /usr/local/bin/ytdownloader download "$(cat /path/to/daily_url.txt)" --output-dir /path/to/videos/
```

Remember to always respect copyright laws and terms of service when downloading content!