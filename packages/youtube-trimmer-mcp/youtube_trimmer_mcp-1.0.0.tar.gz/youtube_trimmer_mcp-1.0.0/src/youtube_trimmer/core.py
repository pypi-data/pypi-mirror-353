#!/usr/bin/env python3
"""
Core YouTube Trimmer functionality.
"""
import contextlib
import os
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile
from typing import Optional, Tuple

import yt_dlp


@contextlib.contextmanager
def suppress_output():
    """Context manager to completely suppress stdout and stderr."""
    with open(os.devnull, 'w') as devnull:
        old_stdout = sys.stdout
        old_stderr = sys.stderr
        try:
            sys.stdout = devnull
            sys.stderr = devnull
            yield
        finally:
            sys.stdout = old_stdout
            sys.stderr = old_stderr


class YoutubeTrimmer:
    """Core class for downloading and trimming YouTube videos."""
    
    def __init__(self, quiet: bool = False, mcp_mode: bool = False, output_dir: Optional[str] = None):
        """Initialize the YouTube trimmer.
        
        Args:
            quiet: If True, suppress most output
            mcp_mode: If True, use extra suppression for MCP protocol compatibility
            output_dir: Default output directory (defaults to ./output)
        """
        self.quiet = quiet
        self.mcp_mode = mcp_mode
        self.output_dir = pathlib.Path(output_dir) if output_dir else pathlib.Path.cwd() / "output"
        # Ensure output directory exists
        self.output_dir.mkdir(exist_ok=True, parents=True)

    @staticmethod
    def to_seconds(ts: str) -> float:
        """Convert a timestamp (SS, MM:SS, or HH:MM:SS[.ms]) to seconds."""
        parts = list(map(float, ts.split(":")))
        return sum(p * 60 ** i for i, p in enumerate(reversed(parts)))

    def progress_hook(self, d):
        """Display download progress."""
        if self.quiet:
            return
            
        if d['status'] == 'downloading':
            percent = d.get('_percent_str', 'unknown')
            speed = d.get('_speed_str', 'unknown speed')
            eta = d.get('_eta_str', 'unknown ETA')
            print(f"\rDownloading: {percent} at {speed} (ETA: {eta})", end='', flush=True)
        elif d['status'] == 'finished':
            print("\nDownload completed. Starting video trimming...")

    def trim_video(
        self,
        url: str,
        start_time: str,
        end_time: str,
        output_path: Optional[str] = None,
        keep_temp: bool = False
    ) -> str:
        """Download and trim a YouTube video.
        
        Args:
            url: YouTube video URL
            start_time: Start timestamp (HH:MM:SS[.ms])
            end_time: End timestamp (HH:MM:SS[.ms])
            output_path: Output filename (optional, auto-generated if not provided)
            keep_temp: Whether to keep the full downloaded file
            
        Returns:
            Path to the trimmed video file
            
        Raises:
            ValueError: If timestamps are invalid
            RuntimeError: If download or trimming fails
        """
        # Convert timestamps to seconds
        start, end = self.to_seconds(start_time), self.to_seconds(end_time)
        if start >= end:
            raise ValueError("Start timestamp must be less than end timestamp")

        # Create temporary directory and download the video
        with tempfile.TemporaryDirectory() as tmpdir:
            if not self.quiet:
                print(f"Downloading video from {url}...")
                
            ydl_opts = {
                "outtmpl": f"{tmpdir}/full.%(ext)s",
                "quiet": self.quiet or self.mcp_mode,
                "no_warnings": self.quiet or self.mcp_mode,
                "format": "best",
                "progress_hooks": [self.progress_hook] if not self.quiet else []
            }
            
            # Add extra suppression for MCP mode to prevent JSON protocol interference
            if self.mcp_mode:
                ydl_opts.update({
                    "noprogress": True,
                    "no_color": True,
                    "extract_flat": False,
                    "writeinfojson": False,
                    "writedescription": False,
                    "writesubtitles": False,
                    "writeautomaticsub": False,
                })
            
            try:
                ydl = yt_dlp.YoutubeDL(ydl_opts)
                
                # Use output suppression in MCP mode to prevent JSON protocol interference
                if self.mcp_mode:
                    with suppress_output():
                        info = ydl.extract_info(url, download=True)
                else:
                    info = ydl.extract_info(url, download=True)
                    
                video_id = info.get('id', 'video')
                video_title = info.get('title', 'video')
                video_duration = info.get('duration')
                
                # Check if timestamps are within video duration
                if video_duration and (start > video_duration or end > video_duration):
                    raise ValueError(f"Timestamp(s) exceed video duration ({video_duration} seconds)")
                
                # Find the downloaded file
                src = next(pathlib.Path(tmpdir).glob("full.*"))
                
                # Determine output filename if not specified
                if not output_path:
                    sanitized_title = re.sub(r'[^\w\-_\. ]', '_', video_title)
                    start_str = start_time.replace(':', '-')
                    end_str = end_time.replace(':', '-')
                    filename = f"clip_{sanitized_title}_{start_str}-{end_str}.mp4"
                    output_path = str(self.output_dir / filename)
                
                out = pathlib.Path(output_path)
                
                if not self.quiet:
                    print(f"Trimming video from {start_time} to {end_time}...")
                    
                # Trim the video with FFmpeg
                subprocess.run(
                    ["ffmpeg", "-y", "-ss", str(start), "-to", str(end),
                     "-i", str(src), "-c", "copy", "-loglevel", "error", str(out)],
                    check=True
                )
                
                if keep_temp:
                    temp_copy = f"{video_id}_full{src.suffix}"
                    shutil.copy(src, temp_copy)
                    if not self.quiet:
                        print(f"Full video saved as {temp_copy}")
                
                result_path = str(out.resolve())
                if not self.quiet:
                    print(f"Trimmed video saved to: {result_path}")
                
                return result_path
                
            except yt_dlp.utils.DownloadError as e:
                raise RuntimeError(f"Error downloading video: {e}")
            except subprocess.CalledProcessError as e:
                raise RuntimeError(f"Error trimming video: {e}")
            except Exception as e:
                raise RuntimeError(f"Error: {e}")

    def get_video_info(self, url: str) -> dict:
        """Get information about a YouTube video without downloading.
        
        Args:
            url: YouTube video URL
            
        Returns:
            Dictionary with video information
        """
        ydl_opts = {
            "quiet": True,
            "no_warnings": True,
        }
        
        # Add extra suppression for MCP mode to prevent JSON protocol interference
        if self.mcp_mode:
            ydl_opts.update({
                "noprogress": True,
                "no_color": True,
                "extract_flat": False,
                "writeinfojson": False,
                "writedescription": False,
                "writesubtitles": False,
                "writeautomaticsub": False,
            })
        
        try:
            ydl = yt_dlp.YoutubeDL(ydl_opts)
            
            # Use output suppression in MCP mode to prevent JSON protocol interference
            if self.mcp_mode:
                with suppress_output():
                    info = ydl.extract_info(url, download=False)
            else:
                info = ydl.extract_info(url, download=False)
            
            return {
                "id": info.get('id'),
                "title": info.get('title'),
                "duration": info.get('duration'),
                "description": info.get('description'),
                "uploader": info.get('uploader'),
                "upload_date": info.get('upload_date'),
                "view_count": info.get('view_count'),
                "thumbnail": info.get('thumbnail')
            }
        except Exception as e:
            raise RuntimeError(f"Error getting video info: {e}") 