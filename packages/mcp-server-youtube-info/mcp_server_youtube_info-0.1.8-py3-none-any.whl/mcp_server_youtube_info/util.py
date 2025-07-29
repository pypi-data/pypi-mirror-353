#!/usr/bin/env python3
"""
YouTube Video Metadata Retrieval Sample

This script is a sample for retrieving metadata of YouTube videos.
It only retrieves information without actual downloading.
"""

import sys
from typing import Dict, Any, Optional
import yt_dlp


class VideoInfoExtractor:
    """Class for retrieving YouTube video metadata"""

    def __init__(self):
        # yt-dlp settings (no download configuration)
        self.ydl_opts = {
            'quiet': True,                    # Suppress logs
            'no_warnings': False,             # Show warnings
            'extract_flat': False,            # Get detailed information
            'simulate': True,                 # Simulation mode (no download)
            'skip_download': True,            # Skip download
        }

    def get_video_info(self, video_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve video information for the specified video ID

        Args:
            video_id (str): YouTube video ID

        Returns:
            Dict[str, Any]: Video information dictionary, None if error occurs
        """
        try:
            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                # Get video information
                url = f"https://www.youtube.com/watch?v={video_id}"
                info = ydl.extract_info(url, download=False)
                return info
        except Exception as e:
            print(f"An error occurred: {e}", file=sys.stderr)
            return None

    def format_info(self, info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format and return the retrieved information

        Args:
            info (Dict[str, Any]): Raw information retrieved from yt-dlp

        Returns:
            Dict[str, Any]: Formatted information
        """
        if not info:
            return {}

        # Extract basic information
        formatted_info = {
            'title': info.get('title', 'N/A'),
            'uploader': info.get('uploader', 'N/A'),
            'upload_date': info.get('upload_date', 'N/A'),
            'duration': info.get('duration', 0),
            'view_count': info.get('view_count', 0),
            'like_count': info.get('like_count', 0),
            'description': info.get('description', 'N/A')[:200] + '...' if info.get('description') else 'N/A',
            'tags': info.get('tags', []),
            'categories': info.get('categories', []),
            'webpage_url': info.get('webpage_url', 'N/A'),
            'thumbnail': info.get('thumbnail', 'N/A'),
        }

        # Available format information
        formats = info.get('formats', [])
        if formats:
            # Summarize video format information concisely
            video_formats = []
            audio_formats = []

            for fmt in formats:
                if fmt.get('vcodec') != 'none' and fmt.get('acodec') != 'none':
                    # Video + Audio
                    video_formats.append({
                        'format_id': fmt.get('format_id'),
                        'ext': fmt.get('ext'),
                        'resolution': f"{fmt.get('width', 'N/A')}x{fmt.get('height', 'N/A')}",
                        'fps': fmt.get('fps'),
                        'filesize': fmt.get('filesize'),
                    })
                elif fmt.get('acodec') != 'none':
                    # Audio only
                    audio_formats.append({
                        'format_id': fmt.get('format_id'),
                        'ext': fmt.get('ext'),
                        'abr': fmt.get('abr'),
                        'filesize': fmt.get('filesize'),
                    })

            formatted_info['available_formats'] = {
                'video_count': len(video_formats),
                'audio_count': len(audio_formats),
                'video_formats': video_formats[:5],  # Show only the first 5
                'audio_formats': audio_formats[:5],  # Show only the first 5
            }

        return formatted_info

    def print_info(self, info: Dict[str, Any]) -> None:
        """
        Format and display information

        Args:
            info (Dict[str, Any]): Information to display
        """
        if not info:
            print("Could not retrieve information.")
            return

        print("=" * 60)
        print(f"Title: {info['title']}")
        print(f"Uploader: {info['uploader']}")
        print(f"Upload Date: {info['upload_date']}")
        print(
            f"Duration: {info['duration']} seconds ({info['duration']//60} min {info['duration'] % 60} sec)")
        print(f"View Count: {info['view_count']:,}")
        print(f"Like Count: {info['like_count']:,}")
        print(f"URL: {info['webpage_url']}")
        print("-" * 60)
        print(f"Description: {info['description']}")
        print("-" * 60)

        if info['tags']:
            print(f"Tags: {', '.join(info['tags'][:10])}")  # First 10 tags

        if info['categories']:
            print(f"Categories: {', '.join(info['categories'])}")

        # Format information
        if 'available_formats' in info:
            formats = info['available_formats']
            print("  Available formats:")
            print(f"  Video format count: {formats['video_count']}")
            print(f"  Audio format count: {formats['audio_count']}")

            if formats['video_formats']:
                print("  Main video formats:")
                for fmt in formats['video_formats']:
                    size_info = f" ({fmt['filesize']//1024//1024}MB)" if fmt['filesize'] else ""
                    print(
                        f"    - {fmt['format_id']}: {fmt['ext']}, {fmt['resolution']}, {fmt['fps']}fps{size_info}")

        print("=" * 60)
