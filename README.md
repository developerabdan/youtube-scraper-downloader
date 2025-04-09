# YouTube Scraper

A Python script that scrapes YouTube search results based on a keyword and saves video titles, links, and durations to a CSV file.

## Installation

1. Clone this repository or download the files
2. Install the required dependencies:

```bash
pip install -r requirements.txt
```

3. Make sure you have Chrome browser installed on your system (required for Selenium)

## Usage

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

## Output

The script generates a CSV file with the following columns:
- title: The title of the YouTube video
- link: The URL to the YouTube video
- duration: The duration of the video

If no output filename is specified, the script will generate a file with a timestamp: `youtube_results_YYYYMMDD_HHMMSS.csv`

## YouTube Downloader

This script allows you to download YouTube videos listed in your CSV file with a progress bar.

### Prerequisites

You'll need a virtual environment with the required packages installed:

```bash
# Create a virtual environment
python3 -m venv venv

# Activate the virtual environment
source venv/bin/activate

# Install required packages
pip install yt-dlp tqdm
```

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
