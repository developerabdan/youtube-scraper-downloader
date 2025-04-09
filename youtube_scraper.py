#!/usr/bin/env python3
"""
YouTube Scraper Script

This script allows users to search YouTube for videos using a keyword,
and saves the results (title, link, and duration) to a CSV file.

@author: @abdansyakuro.id
"""

import csv
import re
import time
import json
import os
import urllib.parse
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import argparse


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


def save_config(config, config_path="config.json"):
    """
    Save configuration to a JSON file.
    
    @author: @abdansyakuro.id
    
    Args:
        config (dict): Configuration values to save
        config_path (str): Path to the configuration file
        
    Returns:
        bool: True if saved successfully, False otherwise
    """
    try:
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=4)
        print(f"Configuration saved to {config_path}")
        return True
    except Exception as e:
        print(f"Error saving configuration: {e}")
        return False


def get_video_duration(video_url):
    """
    Get the actual duration of a YouTube video by accessing its page.
    
    @author: @abdansyakuro.id
    
    Args:
        video_url (str): URL of the YouTube video
        
    Returns:
        tuple: (duration_str, duration_minutes) where:
            - duration_str is the duration in format MM:SS or HH:MM:SS
            - duration_minutes is the total duration in minutes (float)
    """
    try:
        # Request the video page
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        }
        response = requests.get(video_url, headers=headers)
        
        if response.status_code != 200:
            return "Unknown", 0.0
        
        # Use regex to find the duration in the meta tags
        # Look for the ISO 8601 duration format in the page content
        duration_pattern = r'"lengthSeconds":"(\d+)"'
        match = re.search(duration_pattern, response.text)
        
        if match:
            seconds = int(match.group(1))
            # Calculate total minutes
            duration_minutes = seconds / 60.0
            
            # Convert seconds to HH:MM:SS format
            if seconds < 60:
                return f"0:{seconds:02d}", duration_minutes
            elif seconds < 3600:
                return f"{seconds // 60}:{seconds % 60:02d}", duration_minutes
            else:
                return f"{seconds // 3600}:{(seconds % 3600) // 60:02d}:{seconds % 60:02d}", duration_minutes
        
        return "Unknown", 0.0
    except Exception as e:
        print(f"Error getting video duration: {e}")
        return "Unknown", 0.0


def duration_to_minutes(duration_str):
    """
    Convert a duration string to total minutes.
    
    @author: @abdansyakuro.id
    
    Args:
        duration_str (str): Duration string in format HH:MM:SS or MM:SS
        
    Returns:
        float: Total duration in minutes
    """
    try:
        parts = duration_str.split(':')
        if len(parts) == 2:
            # MM:SS format
            minutes = int(parts[0])
            seconds = int(parts[1])
            return minutes + (seconds / 60.0)
        elif len(parts) == 3:
            # HH:MM:SS format
            hours = int(parts[0])
            minutes = int(parts[1])
            seconds = int(parts[2])
            return (hours * 60) + minutes + (seconds / 60.0)
        else:
            return 0.0
    except Exception:
        return 0.0


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
    
    # Make the request
    response = requests.get(url, headers=headers, cookies=cookies)
    
    if response.status_code != 200:
        print(f"Error fetching search results: HTTP {response.status_code}")
        return []
    
    # Use BeautifulSoup to parse HTML
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Extract video information using regex patterns
    results = []
    
    # Pattern to find video IDs and their metadata in the page
    video_id_pattern = r'"videoId":"([^"]+)"'
    title_pattern = r'"title":{"runs":\[{"text":"([^"]+)"\}\]'
    
    # Find all video IDs
    video_ids = re.findall(video_id_pattern, response.text)
    titles = re.findall(title_pattern, response.text)
    
    # Convert to set and back to list to remove duplicates
    video_ids = list(dict.fromkeys(video_ids))
    
    # Get only the required number of results
    count = 0
    
    for video_id in video_ids:
        if count >= max_results:
            break
            
        # Try to get title from the list of titles
        title = "Unknown"
        if count < len(titles):
            title = titles[count]
        
        # Get the actual video duration using the video page
        video_url = f"https://www.youtube.com/watch?v={video_id}"
        duration_str, duration_minutes = get_video_duration(video_url)
        
        results.append({
            "title": title,
            "link": video_url,
            "duration": duration_str,
            "minutes": f"{duration_minutes:.2f}"
        })
        
        print(f"Found video: {title} | {duration_str} | {video_url}")
        count += 1
    
    return results


def read_existing_csv(filename):
    """
    Read existing CSV file to get current entries.
    
    @author: @abdansyakuro.id
    
    Args:
        filename (str): Path to the CSV file
        
    Returns:
        dict: Dictionary of existing links and their data
    """
    existing_links = {}
    
    if os.path.exists(filename):
        try:
            with open(filename, 'r', newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    link = row.get('link')
                    if link:
                        # Add minutes field if it doesn't exist
                        if 'minutes' not in row and 'duration' in row:
                            row['minutes'] = f"{duration_to_minutes(row['duration']):.2f}"
                        existing_links[link] = row
            print(f"Read {len(existing_links)} existing entries from {filename}")
        except Exception as e:
            print(f"Error reading existing CSV file: {e}")
    
    return existing_links


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
    # Read existing entries to avoid duplicates
    existing_links = read_existing_csv(filename)
    
    # Identify new entries
    new_entries = []
    for result in results:
        link = result.get('link')
        if link and link not in existing_links:
            new_entries.append(result)
            existing_links[link] = result
    
    # Write all entries back to CSV
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['title', 'link', 'duration', 'minutes']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for entry in existing_links.values():
            writer.writerow(entry)
    
    return filename, len(new_entries)


def configure_youtube():
    """
    Interactive function to configure YouTube search settings.
    
    @author: @abdansyakuro.id
    
    Returns:
        dict: Updated configuration dictionary
    """
    config = load_config()
    
    print("\nYouTube Search Configuration")
    print("===========================")
    current_region = config.get('region', 'None')
    current_language = config.get('language', 'None')
    current_max = config.get('default_max_results', 10)
    current_csv = config.get('csv_filename', 'youtube_results.csv')
    
    print(f"Current Region: {current_region}")
    print(f"Current Language: {current_language}")
    print(f"Current Default Max Results: {current_max}")
    print(f"Current CSV Filename: {current_csv}")
    print("\nEnter new values (leave blank to keep current):")
    
    # Get new values
    new_region = input(f"Region (e.g., ES, US, JP) [{current_region}]: ").strip()
    new_language = input(f"Language (e.g., es, en, jp) [{current_language}]: ").strip()
    new_max = input(f"Default Max Results [{current_max}]: ").strip()
    new_csv = input(f"CSV Filename [{current_csv}]: ").strip()
    
    # Update config
    if new_region:
        config['region'] = new_region
    if new_language:
        config['language'] = new_language
    if new_max and new_max.isdigit():
        config['default_max_results'] = int(new_max)
    if new_csv:
        config['csv_filename'] = new_csv
    
    # Make sure CSV filename is set
    if 'csv_filename' not in config:
        config['csv_filename'] = 'youtube_results.csv'
    
    # Save config
    save_config(config)
    
    return config


def main():
    """
    Main function to execute the YouTube scraping process.
    
    @author: @abdansyakuro.id
    """
    # Load configuration
    config = load_config()
    
    # Make sure CSV filename is set
    if 'csv_filename' not in config:
        config['csv_filename'] = 'youtube_results.csv'
        save_config(config)
    
    # Set up command-line arguments
    parser = argparse.ArgumentParser(description='Scrape YouTube videos based on a search keyword')
    parser.add_argument('keyword', type=str, nargs='?', help='Keyword to search for on YouTube')
    parser.add_argument('--max', type=int, default=config.get('default_max_results', 10), 
                        help=f'Maximum number of results (default: {config.get("default_max_results", 10)})')
    parser.add_argument('--output', type=str, default=config.get('csv_filename'),
                        help=f'Output CSV filename (default: {config.get("csv_filename")})')
    parser.add_argument('--region', type=str, default=config.get('region'), 
                        help=f'Two-letter country code (default: {config.get("region", "None")})')
    parser.add_argument('--language', type=str, default=config.get('language'), 
                        help=f'Language code (default: {config.get("language", "None")})')
    parser.add_argument('--configure', action='store_true', help='Configure default settings')
    
    args = parser.parse_args()
    
    # Configure mode
    if args.configure:
        configure_youtube()
        return
    
    # Verify we have a keyword
    if not args.keyword:
        print("Error: Please provide a search keyword or use --configure to set defaults")
        parser.print_help()
        return
    
    # Run search
    results = search_youtube(args.keyword, args.max, args.region, args.language)
    
    if results:
        output_file, new_count = save_to_csv(results, args.output)
        total_count = len(read_existing_csv(args.output))
        print(f"Added {new_count} new results (total: {total_count}). Data saved to {output_file}")
    else:
        print("No results found.")


if __name__ == "__main__":
    main()
