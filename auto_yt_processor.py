#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
YouTube Automatic Query Processor

This script automatically:
1. Reads search queries from query.txt
2. Searches YouTube for each query
3. Downloads the videos from the search results

Designed to run as a background service or scheduled task.

@author: @abdansyakuro.id
"""

def show_project_support():
    """Display project support message and get user feedback"""
    print("\n⭐ If you find this project helpful, please consider giving it a star!")
    print("🐛 Found a bug? Please open an issue at: https://github.com/developerabdan/youtube-scraper-downloader/issues")
    feedback = input("Did you find this project helpful? (Y/N): ").strip().upper()
    if feedback == 'Y':
        print("Thank you for your support! Don't forget to star the project! 🌟")
    print()

import os
import csv
import time
import logging
import subprocess
import configparser
from datetime import datetime

# ========== CONFIGURATION ==========

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('auto_yt_processor.log'),
        logging.StreamHandler()
    ]
)

# Default configuration
DEFAULT_CONFIG = {
    'General': {
        'query_file': 'query.txt',
        'results_dir': 'results',
        'download_dir': 'downloads',
        'processed_queries_file': 'processed_queries.txt',
        'check_interval_minutes': '60',
        'max_results_per_query': '5',
        'auto_download': 'yes',
        'download_quality': 'best',
        'download_resolution': '720',
        'min_duration_minutes': '0',
        'max_duration_minutes': '0'
    }
}

def load_config():
    """
    Load configuration from config.ini or create default if not exists.
    
    @author: @abdansyakuro.id
    
    Returns:
        configparser.ConfigParser: Configuration object
    """
    config = configparser.ConfigParser()
    
    # If config file exists, load it
    if os.path.exists('config.ini'):
        config.read('config.ini')
    else:
        # Use default config
        config.read_dict(DEFAULT_CONFIG)
        
        # Save default config
        with open('config.ini', 'w') as configfile:
            config.write(configfile)
        logging.info("Created default configuration file: config.ini")
    
    return config

def read_query_file(filename):
    """
    Read queries from a file, one per line.
    
    @author: @abdansyakuro.id
    
    Args:
        filename (str): Path to the query file
        
    Returns:
        list: List of queries (strings)
    """
    if not os.path.exists(filename):
        logging.error(f"Query file not found: {filename}")
        return []
    
    with open(filename, 'r', encoding='utf-8') as f:
        queries = [line.strip() for line in f.readlines() if line.strip()]
    
    return queries

def get_processed_queries(filename):
    """
    Get list of already processed queries.
    
    @author: @abdansyakuro.id
    
    Args:
        filename (str): Path to the processed queries file
        
    Returns:
        list: List of processed queries
    """
    if not os.path.exists(filename):
        return []
    
    with open(filename, 'r', encoding='utf-8') as f:
        processed = [line.strip() for line in f.readlines() if line.strip()]
    
    return processed

def mark_query_as_processed(query, filename):
    """
    Mark a query as processed by adding it to the processed queries file.
    
    @author: @abdansyakuro.id
    
    Args:
        query (str): The query that was processed
        filename (str): Path to the processed queries file
    """
    with open(filename, 'a', encoding='utf-8') as f:
        f.write(f"{query}\n")

def search_youtube(query, max_results, output_dir):
    """
    Search YouTube for videos based on query.
    
    @author: @abdansyakuro.id
    
    Args:
        query (str): Search query
        max_results (int): Maximum number of results
        output_dir (str): Directory to save CSV results
        
    Returns:
        str: Path to the results CSV file, or None if failed
    """
    # Create timestamp for unique filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Create output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Sanitize query for filename
    safe_query = "".join(c if c.isalnum() else "_" for c in query)
    output_file = f"{output_dir}/{safe_query}_{timestamp}.csv"
    
    try:
        logging.info(f"Searching YouTube for: '{query}'")
        logging.info(f"Fetching up to {max_results} results...")
        
        # Execute the youtube_scraper_fast.py script (using the faster version)
        cmd = [
            "python3", "youtube_scraper_fast.py", 
            query,
            "--max", str(max_results),
            "--output", output_file
        ]
        
        # Run the command and capture output
        process = subprocess.run(
            cmd, 
            capture_output=True,
            text=True
        )
        
        # Log the output for debugging
        if process.stdout:
            logging.info(f"Scraper stdout: {process.stdout}")
        if process.stderr:
            logging.error(f"Scraper stderr: {process.stderr}")
        
        if process.returncode == 0:
            logging.info(f"Search completed! Results saved to: {output_file}")
            return output_file
        else:
            logging.error(f"YouTube scraper failed with exit code {process.returncode}")
            return None
    
    except Exception as e:
        logging.error(f"Error searching YouTube: {str(e)}")
        return None

def download_videos_from_csv(csv_file, download_dir, quality, resolution, min_duration=0, max_duration=0):
    """
    Download videos from the CSV file.
    
    @author: @abdansyakuro.id
    
    Args:
        csv_file (str): Path to the CSV file with search results
        download_dir (str): Directory to save downloaded videos
        quality (str): Quality of videos to download (best, worst, audio)
        resolution (str): Resolution to download (e.g., 720, 1080)
        min_duration (float): Minimum duration in minutes (0 = no minimum)
        max_duration (float): Maximum duration in minutes (0 = no maximum)
        
    Returns:
        int: Number of videos downloaded successfully
    """
    if not os.path.exists(csv_file):
        logging.error(f"CSV file not found: {csv_file}")
        return 0
    
    # Create download directory if it doesn't exist
    if not os.path.exists(download_dir):
        os.makedirs(download_dir)
    
    # Get query name from CSV filename
    query_name = os.path.basename(csv_file).split('_')[0]
    query_dir = f"{download_dir}/{query_name}"
    
    # Create query-specific download directory
    if not os.path.exists(query_dir):
        os.makedirs(query_dir)
    
    try:
        # Read videos from CSV
        videos = []
        with open(csv_file, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            videos = list(reader)
        
        if not videos:
            logging.warning(f"No videos found in {csv_file}")
            return 0
        
        # Apply duration filter if specified
        filtered_videos = []
        for video in videos:
            # Convert duration to minutes
            try:
                # Check if 'minutes' column exists, otherwise calculate from 'duration'
                if 'minutes' in video and video['minutes']:
                    duration_minutes = float(video['minutes'])
                else:
                    # Parse duration format like "1:30" to minutes
                    duration_parts = video['duration'].split(':')
                    if len(duration_parts) == 2:  # MM:SS
                        duration_minutes = float(duration_parts[0]) + float(duration_parts[1]) / 60
                    elif len(duration_parts) == 3:  # HH:MM:SS
                        duration_minutes = float(duration_parts[0]) * 60 + float(duration_parts[1]) + float(duration_parts[2]) / 60
                    else:
                        duration_minutes = 0
                
                # Apply duration filter
                if min_duration > 0 and duration_minutes < min_duration:
                    logging.info(f"Skipping video (too short): {video['title']} ({duration_minutes:.2f} min)")
                    continue
                if max_duration > 0 and duration_minutes > max_duration:
                    logging.info(f"Skipping video (too long): {video['title']} ({duration_minutes:.2f} min)")
                    continue
                
                filtered_videos.append(video)
            except (ValueError, KeyError) as e:
                logging.warning(f"Could not parse duration for video: {video.get('title', 'Unknown')}. Error: {str(e)}")
                # Include video if we can't determine duration
                filtered_videos.append(video)
        
        if not filtered_videos:
            logging.warning(f"No videos match the duration filter (min: {min_duration}, max: {max_duration})")
            return 0
        
        logging.info(f"Found {len(filtered_videos)} videos matching duration filter out of {len(videos)} total")
        
        # Format parameter for yt-dlp
        format_option = "best"  # Default
        if quality == "audio":
            format_option = "bestaudio"
        elif quality == "worst":
            format_option = "worst"
        elif resolution:
            # Use a format that doesn't require merging if possible
            format_option = f"best[height<={resolution}]/bestvideo[height<={resolution}]+bestaudio"
        
        # Download each video
        successful_downloads = 0
        for i, video in enumerate(filtered_videos, 1):
            video_url = video['link']
            logging.info(f"Downloading video {i}/{len(filtered_videos)}: {video['title']}")
            
            try:
                # Prepare the command
                cmd = [
                    "yt-dlp",
                    "-f", format_option,
                    "--newline",
                    "--progress",
                    "-o", f"{query_dir}/%(title)s.%(ext)s",
                    video_url
                ]
                
                # Execute the command
                process = subprocess.run(cmd, check=True)
                
                if process.returncode == 0:
                    logging.info(f"Successfully downloaded: {video_url}")
                    successful_downloads += 1
                else:
                    logging.error(f"Error downloading {video_url}")
            
            except Exception as e:
                logging.error(f"Error downloading {video_url}: {str(e)}")
        
        return successful_downloads
    
    except Exception as e:
        logging.error(f"Error processing CSV file: {str(e)}")
        return 0

def process_query(query, config):
    """
    Process a single query: search and download.
    
    @author: @abdansyakuro.id
    
    Args:
        query (str): Search query
        config (configparser.ConfigParser): Configuration
        
    Returns:
        bool: True if successful, False otherwise
    """
    logging.info(f"Processing query: '{query}'")
    
    # Get configuration values
    results_dir = config['General']['results_dir']
    download_dir = config['General']['download_dir']
    max_results = int(config['General']['max_results_per_query'])
    auto_download = config['General']['auto_download'].lower() in ('yes', 'true', '1', 'y')
    quality = config['General']['download_quality']
    resolution = config['General']['download_resolution']
    
    # Get duration filter settings
    min_duration = float(config['General'].get('min_duration_minutes', 0))
    max_duration = float(config['General'].get('max_duration_minutes', 0))
    
    # Log duration filter if active
    if min_duration > 0 or max_duration > 0:
        duration_filter = []
        if min_duration > 0:
            duration_filter.append(f">= {min_duration} minutes")
        if max_duration > 0:
            duration_filter.append(f"<= {max_duration} minutes")
        logging.info(f"Duration filter active: {' and '.join(duration_filter)}")
    
    # Search YouTube
    csv_file = search_youtube(query, max_results, results_dir)
    if not csv_file:
        logging.error(f"Failed to get search results for '{query}'")
        return False
    
    # Download videos if auto_download is enabled
    if auto_download:
        downloaded = download_videos_from_csv(
            csv_file, download_dir, quality, resolution, min_duration, max_duration
        )
        logging.info(f"Downloaded {downloaded} videos for query: '{query}'")
    
    return True

def main():
    """
    Main function to run the automatic YouTube processor.
    
    @author: @abdansyakuro.id
    """
    logging.info("Starting YouTube Automatic Query Processor")
    
    # Load configuration
    config = load_config()
    
    # Get configuration values
    query_file = config['General']['query_file']
    processed_file = config['General']['processed_queries_file']
    check_interval = int(config['General']['check_interval_minutes'])
    
    logging.info(f"Configuration loaded. Using query file: {query_file}")
    logging.info(f"Check interval: {check_interval} minutes")
    
    try:
        while True:
            # Read queries and already processed queries
            queries = read_query_file(query_file)
            processed_queries = get_processed_queries(processed_file)
            
            # Find new queries to process
            new_queries = [q for q in queries if q not in processed_queries]
            
            if new_queries:
                logging.info(f"Found {len(new_queries)} new queries to process")
                
                for query in new_queries:
                    success = process_query(query, config)
                    if success:
                        mark_query_as_processed(query, processed_file)
                        logging.info(f"Query marked as processed: '{query}'")
            else:
                logging.info("No new queries to process")
            
            # Sleep for the configured interval
            next_check = datetime.now().timestamp() + (check_interval * 60)
            next_check_time = datetime.fromtimestamp(next_check).strftime('%H:%M:%S')
            logging.info(f"Next check scheduled at: {next_check_time}")
            time.sleep(check_interval * 60)
    
    except KeyboardInterrupt:
        logging.info("Process interrupted by user")
    except Exception as e:
        logging.error(f"An unexpected error occurred: {str(e)}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    exit(exit_code)
