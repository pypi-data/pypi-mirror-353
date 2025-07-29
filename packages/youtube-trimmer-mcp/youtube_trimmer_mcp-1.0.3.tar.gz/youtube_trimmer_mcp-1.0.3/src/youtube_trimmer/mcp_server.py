#!/usr/bin/env python3
"""
YouTube Trimmer MCP Server - FastMCP Implementation

This server provides tools for downloading and trimming YouTube videos
using the Model Context Protocol (MCP) with FastMCP.
"""

import logging
import sys
from pathlib import Path
from typing import Any, Dict, Optional

from mcp.server.fastmcp import FastMCP

from .core import YoutubeTrimmer

# Set up logging to stderr explicitly to avoid interfering with MCP JSON protocol on stdout
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stderr)],  # Explicitly use stderr
)

logger = logging.getLogger(__name__)

# Create the FastMCP server
mcp = FastMCP("youtube-trimmer")

# Initialize output directory at startup
# Use a user-writable directory instead of potentially read-only paths
try:
    # Try to use a project-specific directory
    project_root = Path(__file__).resolve().parent.parent.parent  # Go up from src/youtube_trimmer/
    GLOBAL_OUTPUT_DIR = project_root / "output"
except Exception:
    # Fallback to user's home directory
    GLOBAL_OUTPUT_DIR = Path.home() / "youtube_trimmer_output"

GLOBAL_OUTPUT_DIR.mkdir(exist_ok=True, parents=True)
logger.info(f"Initialized output directory: {GLOBAL_OUTPUT_DIR}")


def _get_output_dir() -> Path:
    """Get the absolute path to the output directory."""
    return GLOBAL_OUTPUT_DIR


@mcp.tool()
def trim_youtube_video(
    url: str,
    start_time: str,
    end_time: str,
    output_path: Optional[str] = None,
    keep_temp: bool = False
) -> str:
    """Download and trim a YouTube video to a specific timeframe.
    
    Args:
        url: YouTube video URL (e.g., "https://www.youtube.com/watch?v=dQw4w9WgXcQ")
        start_time: Start timestamp in HH:MM:SS[.ms] format (e.g., "0:30", "1:25:30")
        end_time: End timestamp in HH:MM:SS[.ms] format (e.g., "0:45", "1:27:00")
        output_path: Optional output filename. If not provided, auto-generated from video title and timestamps
        keep_temp: Whether to keep the full downloaded video file (default: False)
        
    Returns:
        Path to the trimmed video file
        
    Raises:
        ValueError: If timestamps are invalid (start >= end or exceed video duration)
        RuntimeError: If download or trimming fails
    """
    try:
        # Convert to absolute path if output_path is provided
        if output_path:
            output_path = str(Path(output_path).resolve())
            # Ensure output directory exists
            output_dir = Path(output_path).parent
            output_dir.mkdir(exist_ok=True, parents=True)
        
        trimmer = YoutubeTrimmer(quiet=True, mcp_mode=True)  # Use MCP mode for maximum output suppression
        result_path = trimmer.trim_video(
            url=url,
            start_time=start_time,
            end_time=end_time,
            output_path=output_path,
            keep_temp=keep_temp
        )
        
        logger.info(f"Successfully trimmed video: {result_path}")
        return result_path
        
    except Exception as e:
        logger.error(f"Error trimming YouTube video: {e}")
        raise RuntimeError(f"Failed to trim YouTube video: {e}")


@mcp.tool()
def get_youtube_video_info(url: str) -> Dict[str, Any]:
    """Get information about a YouTube video without downloading it.
    
    Args:
        url: YouTube video URL
        
    Returns:
        Dictionary containing video information including:
        - id: Video ID
        - title: Video title
        - duration: Duration in seconds
        - description: Video description
        - uploader: Channel name
        - upload_date: Upload date
        - view_count: Number of views
        - thumbnail: Thumbnail URL
    """
    try:
        trimmer = YoutubeTrimmer(quiet=True, mcp_mode=True)
        info = trimmer.get_video_info(url)
        
        logger.info(f"Retrieved info for video: {info.get('title', 'Unknown')}")
        return info
        
    except Exception as e:
        logger.error(f"Error getting YouTube video info: {e}")
        raise RuntimeError(f"Failed to get video info: {e}")


@mcp.tool()
def convert_timestamp_to_seconds(timestamp: str) -> float:
    """Convert a timestamp string to seconds.
    
    Args:
        timestamp: Timestamp in SS, MM:SS, or HH:MM:SS[.ms] format
        
    Returns:
        Time in seconds as a float
        
    Examples:
        - "30" -> 30.0
        - "1:30" -> 90.0
        - "1:25:30" -> 5130.0
        - "0:30.5" -> 30.5
    """
    try:
        seconds = YoutubeTrimmer.to_seconds(timestamp)
        logger.info(f"Converted {timestamp} to {seconds} seconds")
        return seconds
        
    except Exception as e:
        logger.error(f"Error converting timestamp: {e}")
        raise ValueError(f"Invalid timestamp format: {timestamp}")


@mcp.tool()
def download_full_youtube_video(
    url: str,
    output_path: Optional[str] = None
) -> str:
    """Download a full YouTube video without trimming.
    
    Args:
        url: YouTube video URL
        output_path: Optional output filename. If not provided, auto-generated from video title
        
    Returns:
        Path to the downloaded video file
    """
    try:
        # Get video info to determine duration
        trimmer = YoutubeTrimmer(quiet=True, mcp_mode=True)
        info = trimmer.get_video_info(url)
        duration = info.get('duration', 0)
        
        if not duration:
            raise RuntimeError("Could not determine video duration")
        
        # Download the full video by trimming from 0 to duration
        result_path = trimmer.trim_video(
            url=url,
            start_time="0",
            end_time=str(duration),
            output_path=output_path,
            keep_temp=False
        )
        
        logger.info(f"Successfully downloaded full video: {result_path}")
        return result_path
        
    except Exception as e:
        logger.error(f"Error downloading YouTube video: {e}")
        raise RuntimeError(f"Failed to download video: {e}")


def main():
    """Entry point for the MCP server."""
    logger.info("Starting YouTube Trimmer MCP Server...")
    mcp.run()


if __name__ == "__main__":
    logger.info("Starting YouTube Trimmer MCP Server...")
    mcp.run() 