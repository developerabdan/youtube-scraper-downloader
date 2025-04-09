# YouTube Scraper & Downloader

A comprehensive tool for searching and downloading YouTube videos:
1. **YouTube Scraper**: Search YouTube and save video details to CSV
2. **YouTube Downloader**: Download videos from the CSV with customizable quality options
3. **Interactive Tool**: User-friendly interactive command-line interface

## Quick Start

### Installation

```bash
# Clone this repository
git clone https://github.com/developerabdan/youtube-scraper-downloader.git
cd youtube-scraper-downloader

# Create a virtual environment
python3 -m venv venv

# Activate the virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install all dependencies
pip install -r requirements.txt
```

> **Note**: For the scraper, you need Chrome browser installed on your system (required for Selenium)

## Interactive Tool (Recommended for Beginners)

The easiest way to use this tool is with the interactive command-line interface:

```bash
python yt_interactive.py
```

This will guide you through the process with simple prompts:
1. Enter your search keywords
2. Choose how many results to fetch
3. View the search results
4. Select which videos to download
5. Choose your preferred quality and resolution
6. Specify where to save the downloaded videos

No need to remember complex commands or arguments!

## YouTube Scraper

### Usage

Run the script from the command line with a search keyword:

```bash
python youtube_scraper.py "your search keyword"
```

### Optional arguments:

- `--max`: Maximum number of results to fetch (default: 10)
- `--output`: Specify the output CSV filename

Example:
```bash
python youtube_scraper.py "python tutorial" --max 20 --output results.csv
```

### Output

The script generates a CSV file with the following columns:
- title: The title of the YouTube video
- link: The URL to the YouTube video
- duration: The duration of the video

If no output filename is specified, the script will generate a file with a timestamp: `youtube_results_YYYYMMDD_HHMMSS.csv`

## YouTube Downloader

This script allows you to download YouTube videos listed in your CSV file with a progress bar.

### Usage

The downloader script provides several options:

```
python youtube_downloader.py [--csv CSV_FILE] [--output OUTPUT_DIR] [--all] [--index INDEX] [--range START-END] [--quality QUALITY] [--format FORMAT] [--resolution RES]
```

Arguments:
- `--csv`: Path to the CSV file with YouTube links (default: youtube_results.csv)
- `--output`: Directory to save downloaded videos (default: downloads)
- `--all`: Download all videos from the CSV
- `--index`: Download a specific video by its index (starting from 1)
- `--range`: Download videos in a range (e.g., 1-5)
- `--quality`: Quality of the video to download: best, worst, audio (default: best)
- `--format`: Format of the video: mp4, webm, etc. (default: mp4)
- `--resolution`: Specific resolution to download (e.g., 720, 1080)

### Examples

List all available videos:
```bash
python youtube_downloader.py
```

Download a specific video (e.g., the first video):
```bash
python youtube_downloader.py --index 1
```

Download a range of videos:
```bash
python youtube_downloader.py --range 1-5
```

Download all videos:
```bash
python youtube_downloader.py --all
```

Save videos to a custom folder:
```bash
python youtube_downloader.py --index 1 --output english_tutorials
```

Download only the audio of a video:
```bash
python youtube_downloader.py --index 1 --quality audio
```

Download a video in 720p resolution:
```bash
python youtube_downloader.py --index 1 --resolution 720
```

Download a video in webm format:
```bash
python youtube_downloader.py --index 1 --format webm
```

## Author

@abdansyakuro.id
