#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Interactive YouTube Search and Download Tool

This script provides an interactive command-line interface for searching
YouTube videos and downloading them with customizable options.

@author: @abdansyakuro.id
"""

import os
import csv
import subprocess
import shutil
import tempfile
from datetime import datetime

def clear_screen():
    """Clear the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header():
    """Print a nice header for the tool."""
    clear_screen()
    print("=" * 60)
    print("        YOUTUBE SEARCH & DOWNLOAD INTERACTIVE TOOL")
    print("=" * 60)
    print()

def get_input(prompt, default=None):
    """
    Get user input with a default value.
    
    @author: @abdansyakuro.id
    """
    if default:
        user_input = input(f"{prompt} [{default}]: ").strip()
        return user_input if user_input else default
    return input(f"{prompt}: ").strip()

def search_youtube(keyword, max_results=10, output_file=None):
    """
    Search YouTube for videos based on keyword.
    
    @author: @abdansyakuro.id
    """
    if not output_file:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"youtube_results_{timestamp}.csv"
    
    try:
        print(f"\nSearching YouTube for: '{keyword}'...")
        print(f"Fetching up to {max_results} results...")
        
        # Execute the youtube_scraper.py script
        cmd = [
            "python", "youtube_scraper.py", 
            keyword,
            "--max", str(max_results),
            "--output", output_file
        ]
        
        process = subprocess.run(
            cmd, 
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        if process.returncode == 0:
            print(f"\n✅ Search completed! Results saved to: {output_file}")
            return output_file
        else:
            print(f"\n❌ Error searching YouTube: {process.stderr}")
            return None
    
    except Exception as e:
        print(f"\n❌ Error searching YouTube: {str(e)}")
        return None

def display_search_results(csv_file):
    """
    Display YouTube search results from CSV file.
    
    @author: @abdansyakuro.id
    """
    if not os.path.exists(csv_file):
        print(f"\n❌ Results file not found: {csv_file}")
        return []
    
    videos = []
    try:
        with open(csv_file, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            videos = list(reader)
        
        if not videos:
            print("\n❌ No videos found in the results file.")
            return []
        
        print("\n📋 SEARCH RESULTS:")
        print("-" * 60)
        for i, video in enumerate(videos, 1):
            title = video['title']
            duration = video['duration']
            
            # Truncate long titles for better display
            if len(title) > 70:
                title = title[:67] + "..."
                
            print(f"{i}. [{duration}] {title}")
        
        print("-" * 60)
        return videos
    
    except Exception as e:
        print(f"\n❌ Error reading results: {str(e)}")
        return []

def download_video(video_url, output_path, quality="best", resolution=None):
    """
    Download a YouTube video using yt-dlp.
    
    @author: @abdansyakuro.id
    """
    try:
        # Check if yt-dlp is installed
        if not shutil.which("yt-dlp"):
            print("yt-dlp is not installed. Installing...")
            subprocess.run(["pip", "install", "yt-dlp"], check=True)
        
        # Prepare the format option based on user preference
        format_option = "best"  # Default
        
        if quality == "audio":
            format_option = "bestaudio"
        elif resolution:
            format_option = f"bestvideo[height<={resolution}]+bestaudio/best[height<={resolution}]"
        
        # Prepare the command
        cmd = [
            "yt-dlp",
            "-f", format_option,
            "--newline",
            "--progress",
            "-o", f"{output_path}/%(title)s.%(ext)s",
            video_url
        ]
        
        # Execute the command
        process = subprocess.run(cmd, check=True)
        
        if process.returncode == 0:
            print(f"\n✅ Successfully downloaded: {video_url}")
            return True
        else:
            print(f"\n❌ Error downloading {video_url}")
            return False
    
    except Exception as e:
        print(f"\n❌ Error downloading {video_url}: {str(e)}")
        return False

def main():
    """
    Main interactive function.
    
    @author: @abdansyakuro.id
    """
    print_header()
    
    # Ask for search keywords
    keyword = get_input("🔍 Enter your YouTube search keywords")
    while not keyword:
        print("Please enter search keywords.")
        keyword = get_input("🔍 Enter your YouTube search keywords")
    
    # Ask for max results
    max_results = get_input("📊 How many results would you like to fetch?", "10")
    try:
        max_results = int(max_results)
    except ValueError:
        print("Invalid number. Using default value of 10.")
        max_results = 10
    
    # Ask for where to save search results
    save_results = get_input("💾 Where would you like to save search results?", "youtube_results.csv")
    
    # Perform the search
    result_file = search_youtube(keyword, max_results, save_results)
    if not result_file:
        print("\n❌ Search failed. Exiting.")
        return
    
    # Display search results
    videos = display_search_results(result_file)
    if not videos:
        return
    
    # Ask if user wants to download videos
    download_option = get_input("📥 Would you like to download videos? (yes/no)", "yes").lower()
    if download_option not in ["yes", "y"]:
        print("\nThank you for using the tool!")
        return
    
    # Ask which videos to download
    selection = get_input("🔢 Enter video number to download, or 'all' for all videos, or range (e.g., 1-5)")
    
    # Ask for download location
    download_path = get_input("📂 Where would you like to save the downloaded videos?", "downloads")
    if not os.path.exists(download_path):
        os.makedirs(download_path)
        print(f"Created directory: {download_path}")
    
    # Ask for preferred quality
    quality_option = get_input("🎥 Select quality (1. Best Quality, 2. Audio Only, 3. Custom Resolution)", "1")
    
    resolution = None
    quality = "best"
    
    if quality_option == "2":
        quality = "audio"
    elif quality_option == "3":
        resolution_input = get_input("🖥️ Enter preferred resolution (e.g., 360, 720, 1080)", "720")
        try:
            resolution = int(resolution_input)
        except ValueError:
            print("Invalid resolution. Using 720p as default.")
            resolution = 720
    
    # Process the selection and download videos
    if selection.lower() == "all":
        print(f"\n⏳ Downloading all {len(videos)} videos...")
        for video in videos:
            print(f"\n⬇️ Downloading: {video['title']}")
            download_video(video['link'], download_path, quality, resolution)
    
    elif "-" in selection:
        try:
            start, end = map(int, selection.split("-"))
            if 1 <= start <= end <= len(videos):
                print(f"\n⏳ Downloading videos {start} to {end}...")
                for i in range(start - 1, end):
                    video = videos[i]
                    print(f"\n⬇️ Downloading: {video['title']}")
                    download_video(video['link'], download_path, quality, resolution)
            else:
                print(f"\n❌ Invalid range. Please choose numbers between 1 and {len(videos)}")
        except ValueError:
            print("\n❌ Invalid range format. Please use format like '1-5'")
    
    else:
        try:
            index = int(selection)
            if 1 <= index <= len(videos):
                video = videos[index - 1]
                print(f"\n⬇️ Downloading: {video['title']}")
                download_video(video['link'], download_path, quality, resolution)
            else:
                print(f"\n❌ Invalid selection. Please choose a number between 1 and {len(videos)}")
        except ValueError:
            print("\n❌ Invalid selection. Please enter a number, range, or 'all'")
    
    print("\n🎉 All done! Thank you for using the YouTube Search & Download Tool!")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user. Exiting...")
    except Exception as e:
        print(f"\n❌ An unexpected error occurred: {str(e)}")
