#!/usr/bin/env python3
"""
Fix YouTube Video Durations Script

This script updates the durations for existing YouTube videos in the CSV file.

@author: @abdansyakuro.id
"""

import csv
import re
import os
import requests
import time

def get_video_duration(video_url):
    """
    Get the actual duration of a YouTube video by accessing its page.
    
    @author: @abdansyakuro.id
    
    Args:
        video_url (str): URL of the YouTube video
        
    Returns:
        str: Duration of the video in format MM:SS or HH:MM:SS
    """
    try:
        # Request the video page
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        }
        response = requests.get(video_url, headers=headers)
        
        if response.status_code != 200:
            return "Unknown"
        
        # Use regex to find the duration in the meta tags
        duration_pattern = r'"lengthSeconds":"(\d+)"'
        match = re.search(duration_pattern, response.text)
        
        if match:
            seconds = int(match.group(1))
            # Convert seconds to HH:MM:SS format
            if seconds < 60:
                return f"0:{seconds:02d}"
            elif seconds < 3600:
                return f"{seconds // 60}:{seconds % 60:02d}"
            else:
                return f"{seconds // 3600}:{(seconds % 3600) // 60:02d}:{seconds % 60:02d}"
        
        return "Unknown"
    except Exception as e:
        print(f"Error getting video duration: {e}")
        return "Unknown"

def fix_csv_durations(csv_filename="youtube_results.csv"):
    """
    Fix durations for all videos in the CSV file.
    
    @author: @abdansyakuro.id
    
    Args:
        csv_filename (str): Name of the CSV file to fix
    """
    if not os.path.exists(csv_filename):
        print(f"Error: File {csv_filename} not found.")
        return
    
    # Read existing entries
    entries = []
    with open(csv_filename, 'r', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            entries.append(row)
    
    # Process each entry
    total = len(entries)
    updated = 0
    
    print(f"Starting to fix durations for {total} videos...")
    for i, entry in enumerate(entries):
        # Check if we need to update the duration
        if entry['duration'] == "0:00" or entry['duration'] == "Unknown":
            print(f"[{i+1}/{total}] Updating duration for: {entry['title']}")
            new_duration = get_video_duration(entry['link'])
            entry['duration'] = new_duration
            updated += 1
            # Sleep briefly to avoid YouTube rate limits
            time.sleep(1)
        else:
            print(f"[{i+1}/{total}] Keeping existing duration ({entry['duration']}) for: {entry['title']}")
    
    # Write the updated entries back to the CSV
    with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['title', 'link', 'duration']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for entry in entries:
            writer.writerow(entry)
    
    print(f"Updated {updated} out of {total} entries in {csv_filename}")

if __name__ == "__main__":
    fix_csv_durations()
