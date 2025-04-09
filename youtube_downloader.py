#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
YouTube Video Downloader with Progress Bar

This script reads YouTube video links from a CSV file and allows 
downloading the videos with a progress bar display.

@author: @abdansyakuro.id
"""

import os
import csv
import argparse
import subprocess
from tqdm import tqdm
import shutil


def get_video_info(csv_file):
    """
    Read video information from the CSV file.
    
    @author: @abdansyakuro.id
    
    Args:
        csv_file (str): Path to the CSV file containing YouTube video information.
        
    Returns:
        list: List of dictionaries with video information.
    """
    videos = []
    with open(csv_file, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            videos.append({
                'title': row['title'],
                'link': row['link'],
                'duration': row['duration']
            })
    return videos


def download_video(video_url, output_path, quality="best", format="mp4", resolution=None):
    """
    Download a YouTube video using yt-dlp with progress bar.
    
    @author: @abdansyakuro.id
    
    Args:
        video_url (str): YouTube video URL.
        output_path (str): Directory to save the downloaded video.
        quality (str): Quality of the video to download. Options: best, worst, audio
        format (str): Format of the video to download (mp4, webm, etc.)
        resolution (str): Specific resolution to download (e.g., 720, 1080)
        
    Returns:
        bool: True if download was successful, False otherwise.
    """
    try:
        # Check if yt-dlp is installed
        if not shutil.which("yt-dlp"):
            print("yt-dlp is not installed. Installing...")
            subprocess.run(["pip", "install", "yt-dlp"], check=True)
        
        # Prepare the format option based on user preference
        format_option = "best"  # Default
        
        if quality == "worst":
            format_option = "worst"
        elif quality == "audio":
            format_option = "bestaudio"
        elif resolution:
            # Example: 'bestvideo[height<=720]+bestaudio/best[height<=720]'
            format_option = f"bestvideo[height<={resolution}]+bestaudio/best[height<={resolution}]"
        elif format != "mp4":
            # Specific format like webm
            format_option = f"best[ext={format}]/best"
            
        # Prepare the command
        cmd = [
            "yt-dlp",
            "-f", format_option,
            "--newline",  # Ensure progress bar works well
            "--progress",  # Show progress bar
            "-o", f"{output_path}/%(title)s.%(ext)s",  # Output file pattern
            video_url  # The URL to download
        ]
        
        # Execute the command
        process = subprocess.run(cmd, check=True)
        
        if process.returncode == 0:
            print(f"Successfully downloaded: {video_url}")
            return True
        else:
            print(f"Error downloading {video_url}")
            return False
    
    except Exception as e:
        print(f"Error downloading {video_url}: {str(e)}")
        return False


def main():
    """
    Main function to parse arguments and execute the download.
    
    @author: @abdansyakuro.id
    """
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Download YouTube videos from a CSV file with progress bar")
    parser.add_argument("--csv", default="youtube_results.csv", help="Path to the CSV file with YouTube links")
    parser.add_argument("--output", default="downloads", help="Directory to save downloaded videos")
    parser.add_argument("--all", action="store_true", help="Download all videos from the CSV")
    parser.add_argument("--index", type=int, help="Download a specific video by its index (starting from 1)")
    parser.add_argument("--range", help="Download videos in a range (e.g., 1-5)")
    parser.add_argument("--quality", default="best", choices=["best", "worst", "audio"], 
                        help="Quality of the video to download (default: best)")
    parser.add_argument("--format", default="mp4", help="Format of the video (mp4, webm, etc.)")
    parser.add_argument("--resolution", help="Specific resolution to download (e.g., 720, 1080)")
    
    args = parser.parse_args()
    
    # Create output directory if it doesn't exist
    if not os.path.exists(args.output):
        os.makedirs(args.output)
        print(f"Created output directory: {args.output}")
    
    # Get video information from CSV
    videos = get_video_info(args.csv)
    
    if not videos:
        print(f"No videos found in {args.csv}")
        return
    
    # Display available videos
    if not args.all and args.index is None and args.range is None:
        print("\nAvailable videos:")
        for i, video in enumerate(videos, 1):
            print(f"{i}. {video['title']} [{video['duration']}]")
        
        print("\nUse one of these options to download:")
        print("  --all              Download all videos")
        print("  --index NUMBER     Download a specific video by index")
        print("  --range START-END  Download videos in a range (e.g., 1-5)")
        print("\nQuality options:")
        print("  --quality QUALITY  Set video quality: best, worst, audio (default: best)")
        print("  --format FORMAT    Set video format: mp4, webm, etc. (default: mp4)")
        print("  --resolution RES   Set specific resolution: 360, 720, 1080, etc.")
        return
    
    # Download videos based on provided arguments
    if args.all:
        # Download all videos
        print(f"Downloading all {len(videos)} videos...")
        for video in videos:
            download_video(video['link'], args.output, args.quality, args.format, args.resolution)
    
    elif args.index is not None:
        # Download a specific video by index
        if 1 <= args.index <= len(videos):
            video = videos[args.index - 1]
            print(f"Downloading video {args.index}: {video['title']}")
            download_video(video['link'], args.output, args.quality, args.format, args.resolution)
        else:
            print(f"Invalid index. Please choose a number between 1 and {len(videos)}")
    
    elif args.range:
        # Download videos in a range
        try:
            start, end = map(int, args.range.split('-'))
            if 1 <= start <= end <= len(videos):
                print(f"Downloading videos {start} to {end}...")
                for i in range(start - 1, end):
                    video = videos[i]
                    download_video(video['link'], args.output, args.quality, args.format, args.resolution)
            else:
                print(f"Invalid range. Please choose numbers between 1 and {len(videos)}")
        except ValueError:
            print("Invalid range format. Please use format like '1-5'")


if __name__ == "__main__":
    main()
