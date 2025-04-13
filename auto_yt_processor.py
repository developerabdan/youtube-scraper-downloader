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
        'download_resolution': '720'
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
        
        # Execute the youtube_scraper.py script
        cmd = [
            "python", "youtube_scraper.py", 
            query,
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
            logging.info(f"Search completed! Results saved to: {output_file}")
            return output_file
        else:
            logging.error(f"Error searching YouTube: {process.stderr}")
            return None
    
    except Exception as e:
        logging.error(f"Error searching YouTube: {str(e)}")
        return None

def download_videos_from_csv(csv_file, download_dir, quality, resolution):
    """
    Download videos from the CSV file.
    
    @author: @abdansyakuro.id
    
    Args:
        csv_file (str): Path to the CSV file with search results
        download_dir (str): Directory to save downloaded videos
        quality (str): Quality of videos to download (best, worst, audio)
        resolution (str): Resolution to download (e.g., 720, 1080)
        
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
        
        # Format parameter for yt-dlp
        format_option = "best"  # Default
        if quality == "audio":
            format_option = "bestaudio"
        elif quality == "worst":
            format_option = "worst"
        elif resolution:
            format_option = f"bestvideo[height<={resolution}]+bestaudio/best[height<={resolution}]"
        
        # Download each video
        successful_downloads = 0
        for i, video in enumerate(videos, 1):
            video_url = video['link']
            logging.info(f"Downloading video {i}/{len(videos)}: {video['title']}")
            
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
    
    # Search YouTube
    csv_file = search_youtube(query, max_results, results_dir)
    if not csv_file:
        logging.error(f"Failed to get search results for '{query}'")
        return False
    
    # Download videos if auto_download is enabled
    if auto_download:
        downloaded = download_videos_from_csv(csv_file, download_dir, quality, resolution)
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
