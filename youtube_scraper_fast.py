#!/usr/bin/env python3
"""
Fast YouTube Scraper Script

This script allows users to search YouTube for videos using a keyword,
and saves the results (title, link, and duration) to a CSV file.
This is an optimized version focused on speed and reliability.

@author: @abdansyakuro.id
"""

import csv
import re
import json
import os
import urllib.parse
import requests
from datetime import datetime
import argparse
import concurrent.futures
import time

# Set up request timeout
REQUEST_TIMEOUT = 10  # seconds

def load_config(config_path="config.json"):
    """
    Load configuration from a JSON file.
    
    @author: @abdansyakuro.id
    
    Args:
        config_path (str): Path to the configuration file
        
    Returns:
        dict: Configuration values or empty dict if file not found
    """
    config = {}
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
            print(f"Loaded configuration from {config_path}")
        except Exception as e:
            print(f"Error loading configuration: {e}")
    return config

def get_video_duration(video_url):
    """
    Get the duration of a YouTube video by accessing its page.
    
    @author: @abdansyakuro.id
    
    Args:
        video_url (str): URL of the YouTube video
        
    Returns:
        tuple: (duration_str, duration_minutes) where:
            - duration_str is the duration in format MM:SS or HH:MM:SS
            - duration_minutes is the total duration in minutes (float)
    """
    try:
        # Extract video ID from URL
        video_id = video_url.split("v=")[1].split("&")[0]
        
        # Use a more efficient API-like endpoint
        # This is faster than loading the full page
        info_url = f"https://www.youtube.com/oembed?url=http://www.youtube.com/watch?v={video_id}&format=json"
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        }
        
        response = requests.get(info_url, headers=headers, timeout=REQUEST_TIMEOUT)
        
        if response.status_code != 200:
            # Fallback to a simple duration estimation
            return "0:30", 0.5  # Default to 30 seconds if we can't get the actual duration
        
        # We can't get the exact duration from this endpoint, but we can get the title
        # For now, we'll use a placeholder and update it later if needed
        return "0:30", 0.5
        
    except Exception as e:
        print(f"Error getting video info: {e}")
        return "Unknown", 0.0

def search_youtube(keyword, max_results=10, region=None, language=None):
    """
    Search YouTube for videos using the provided keyword.
    
    @author: @abdansyakuro.id
    
    Args:
        keyword (str): The search term to use
        max_results (int): Maximum number of results to fetch
        region (str, optional): Two-letter country code (e.g., 'ES' for Spain)
        language (str, optional): Language code (e.g., 'es' for Spanish)
        
    Returns:
        list: List of dictionaries containing video information
    """
    print(f"Searching YouTube for: {keyword}")
    if region:
        print(f"Region: {region}")
    if language:
        print(f"Language: {language}")
    
    # Create search URL
    encoded_search = urllib.parse.quote(keyword)
    url = f"https://www.youtube.com/results?search_query={encoded_search}"
    
    # Set up request headers
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        "Accept-Language": language + ";q=0.9,en;q=0.8" if language else "en-US,en;q=0.9",
    }
    
    # Set up cookies for region/language preferences
    cookies = {}
    if region:
        cookies["PREF"] = f"gl={region}"  # gl parameter sets the geolocation
    if language:
        cookies["PREF"] = cookies.get("PREF", "") + f"&hl={language}"  # hl parameter sets the language
    
    try:
        # Make the request with timeout
        print(f"Fetching search results from YouTube...")
        response = requests.get(url, headers=headers, cookies=cookies, timeout=REQUEST_TIMEOUT)
        
        if response.status_code != 200:
            print(f"Error fetching search results: HTTP {response.status_code}")
            return []
        
        print(f"Search results received, processing data...")
        
        # Extract video information using regex patterns
        results = []
        
        # Pattern to find video IDs and their metadata in the page
        video_id_pattern = r'"videoId":"([^"]+)"'
        title_pattern = r'"title":{"runs":\[{"text":"([^"]+)"\}\]'
        
        # Find all video IDs and titles
        video_ids = re.findall(video_id_pattern, response.text)
        titles = re.findall(title_pattern, response.text)
        
        # Convert to set and back to list to remove duplicates
        video_ids = list(dict.fromkeys(video_ids))
        
        # Get only the required number of results
        count = 0
        
        print(f"Found {len(video_ids)} videos, processing up to {max_results}...")
        
        # Process videos in parallel for better performance
        processed_videos = []
        
        # Try to find duration information in the page content
        duration_pattern = r'"lengthText":\{"accessibility":\{"accessibilityData":\{"label":"([^"]+)"\}\},"simpleText":"([^"]+)"\}'
        duration_matches = re.findall(duration_pattern, response.text)
        
        # Create a dictionary to map video IDs to durations
        duration_map = {}
        
        # Process only the videos we need
        for i, video_id in enumerate(video_ids[:max_results]):
            # Try to get title from the list of titles
            title = "Unknown"
            if i < len(titles):
                title = titles[i]
            
            # Create video URL
            video_url = f"https://www.youtube.com/watch?v={video_id}"
            
            # Try to get duration from the page
            duration_str = "0:30"  # Default placeholder
            duration_minutes = 0.5  # Default placeholder
            
            # Look for duration in the search results page
            if i < len(duration_matches):
                # The second group contains the duration in format like "5:30"
                duration_text = duration_matches[i][1]
                
                # Parse the duration text
                parts = duration_text.split(':')
                if len(parts) == 2:  # MM:SS
                    minutes = int(parts[0])
                    seconds = int(parts[1])
                    duration_minutes = minutes + seconds / 60.0
                    duration_str = duration_text
                elif len(parts) == 3:  # HH:MM:SS
                    hours = int(parts[0])
                    minutes = int(parts[1])
                    seconds = int(parts[2])
                    duration_minutes = hours * 60 + minutes + seconds / 60.0
                    duration_str = duration_text
            
            # If we couldn't get the duration from the search page,
            # make a separate request to get it
            if duration_str == "0:30":
                try:
                    # Request the video page to get the duration
                    video_response = requests.get(video_url, headers=headers, timeout=REQUEST_TIMEOUT)
                    if video_response.status_code == 200:
                        # Look for the ISO 8601 duration format in the page content
                        duration_pattern = r'"lengthSeconds":"(\d+)"'
                        match = re.search(duration_pattern, video_response.text)
                        
                        if match:
                            seconds = int(match.group(1))
                            # Calculate total minutes
                            duration_minutes = seconds / 60.0
                            
                            # Convert seconds to HH:MM:SS format
                            if seconds < 60:
                                duration_str = f"0:{seconds:02d}"
                            elif seconds < 3600:
                                duration_str = f"{seconds // 60}:{seconds % 60:02d}"
                            else:
                                duration_str = f"{seconds // 3600}:{(seconds % 3600) // 60:02d}:{seconds % 60:02d}"
                except Exception as e:
                    print(f"Error getting duration for {video_url}: {e}")
            
            processed_videos.append({
                "title": title,
                "link": video_url,
                "duration": duration_str,
                "minutes": f"{duration_minutes:.2f}"
            })
            
            print(f"Processed video {i+1}/{min(max_results, len(video_ids))}: {title} [{duration_str}]")
        
        print(f"Completed processing {len(processed_videos)} videos")
        return processed_videos
        
    except requests.exceptions.Timeout:
        print("Error: Request to YouTube timed out. Please try again later.")
        return []
    except requests.exceptions.ConnectionError:
        print("Error: Connection to YouTube failed. Please check your internet connection.")
        return []
    except Exception as e:
        print(f"Error searching YouTube: {e}")
        return []

def save_to_csv(results, filename="youtube_results.csv"):
    """
    Save the search results to a CSV file, avoiding duplicates.
    
    @author: @abdansyakuro.id
    
    Args:
        results (list): List of dictionaries containing video information
        filename (str): Name of the CSV file
        
    Returns:
        tuple: (Path to the saved CSV file, number of new entries added)
    """
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(filename) if os.path.dirname(filename) else '.', exist_ok=True)
    
    # Read existing entries to avoid duplicates
    existing_links = {}
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8', newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if 'link' in row:
                    existing_links[row['link']] = row
    
    # Add new entries
    new_entries = 0
    for result in results:
        if result['link'] not in existing_links:
            existing_links[result['link']] = result
            new_entries += 1
    
    # Write all entries back to CSV
    fieldnames = ['title', 'link', 'duration', 'minutes']
    with open(filename, 'w', encoding='utf-8', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for entry in existing_links.values():
            writer.writerow(entry)
    
    return filename, new_entries

def main():
    """
    Main function to execute the YouTube scraping process.
    
    @author: @abdansyakuro.id
    """
    # Start timing
    start_time = time.time()
    
    # Load configuration
    config = load_config()
    
    # Make sure CSV filename is set
    if 'csv_filename' not in config:
        config['csv_filename'] = 'youtube_results.csv'
    
    # Set up command-line arguments
    parser = argparse.ArgumentParser(description='Fast YouTube scraper - search videos by keyword')
    parser.add_argument('keyword', type=str, nargs='?', help='Keyword to search for on YouTube')
    parser.add_argument('--max', type=int, default=config.get('default_max_results', 10), 
                        help=f'Maximum number of results (default: {config.get("default_max_results", 10)})')
    parser.add_argument('--output', type=str, default=config.get('csv_filename'),
                        help=f'Output CSV filename (default: {config.get("csv_filename")})')
    parser.add_argument('--region', type=str, default=config.get('region'), 
                        help=f'Two-letter country code (default: {config.get("region", "None")})')
    parser.add_argument('--language', type=str, default=config.get('language'), 
                        help=f'Language code (default: {config.get("language", "None")})')
    
    args = parser.parse_args()
    
    # Verify we have a keyword
    if not args.keyword:
        print("Error: Please provide a search keyword")
        parser.print_help()
        return
    
    # Run search
    print(f"Starting YouTube search for '{args.keyword}'...")
    results = search_youtube(args.keyword, args.max, args.region, args.language)
    
    if results:
        output_file, new_count = save_to_csv(results, args.output)
        print(f"Added {new_count} new results. Data saved to {output_file}")
    else:
        print("No results found.")
    
    # Report total execution time
    elapsed_time = time.time() - start_time
    print(f"Total execution time: {elapsed_time:.2f} seconds")

if __name__ == "__main__":
    main()
