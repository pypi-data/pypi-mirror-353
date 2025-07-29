#!/usr/bin/env python3
"""
Command-line interface for YouTube Trimmer.
"""
import argparse
import sys
from typing import Optional

from .core import YoutubeTrimmer


def trim_command():
    """Main CLI command for trimming YouTube videos."""
    parser = argparse.ArgumentParser(description="Download and trim YouTube videos")
    parser.add_argument("url", help="YouTube video URL")
    parser.add_argument("-s", "--start", required=True, help="Start timestamp (HH:MM:SS[.ms])")
    parser.add_argument("-e", "--end", required=True, help="End timestamp (HH:MM:SS[.ms])")
    parser.add_argument("-o", "--output", help="Output filename (default: clip_<videoid>_<start>-<end>.mp4)")
    parser.add_argument("--keep-temp", action="store_true", help="Don't delete the full downloaded file")
    parser.add_argument("--quiet", action="store_true", help="Suppress most output")
    
    args = parser.parse_args()
    
    try:
        trimmer = YoutubeTrimmer(quiet=args.quiet)
        result_path = trimmer.trim_video(
            url=args.url,
            start_time=args.start,
            end_time=args.end,
            output_path=args.output,
            keep_temp=args.keep_temp
        )
        
        if not args.quiet:
            print(f"✅ Successfully trimmed video: {result_path}")
        
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


def mcp_server_command():
    """Command to start the MCP server."""
    try:
        from .mcp_server import main
        main()
    except ImportError:
        print(
            "❌ MCP dependencies not installed. Install with: pip install -e '.[mcp]'",
            file=sys.stderr
        )
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error starting MCP server: {e}", file=sys.stderr)
        sys.exit(1)


def info_command():
    """Command to get YouTube video information."""
    parser = argparse.ArgumentParser(description="Get YouTube video information")
    parser.add_argument("url", help="YouTube video URL")
    
    args = parser.parse_args()
    
    try:
        trimmer = YoutubeTrimmer(quiet=True)
        info = trimmer.get_video_info(args.url)
        
        print(f"Title: {info.get('title', 'Unknown')}")
        print(f"Duration: {info.get('duration', 'Unknown')} seconds")
        print(f"Uploader: {info.get('uploader', 'Unknown')}")
        print(f"Views: {info.get('view_count', 'Unknown')}")
        print(f"Upload Date: {info.get('upload_date', 'Unknown')}")
        print(f"Video ID: {info.get('id', 'Unknown')}")
        
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    """Main entry point that dispatches to subcommands."""
    parser = argparse.ArgumentParser(
        description="YouTube Trimmer - Download and trim YouTube videos",
        prog="youtube-trimmer"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Trim command
    trim_parser = subparsers.add_parser("trim", help="Trim a YouTube video")
    trim_parser.add_argument("url", help="YouTube video URL")
    trim_parser.add_argument("-s", "--start", required=True, help="Start timestamp (HH:MM:SS[.ms])")
    trim_parser.add_argument("-e", "--end", required=True, help="End timestamp (HH:MM:SS[.ms])")
    trim_parser.add_argument("-o", "--output", help="Output filename")
    trim_parser.add_argument("--keep-temp", action="store_true", help="Keep the full downloaded file")
    trim_parser.add_argument("--quiet", action="store_true", help="Suppress most output")
    
    # Info command
    info_parser = subparsers.add_parser("info", help="Get video information")
    info_parser.add_argument("url", help="YouTube video URL")
    
    # MCP server command
    mcp_parser = subparsers.add_parser("mcp-server", help="Start the MCP server")
    
    args = parser.parse_args()
    
    if args.command == "trim":
        try:
            trimmer = YoutubeTrimmer(quiet=args.quiet)
            result_path = trimmer.trim_video(
                url=args.url,
                start_time=args.start,
                end_time=args.end,
                output_path=args.output,
                keep_temp=args.keep_temp
            )
            
            if not args.quiet:
                print(f"✅ Successfully trimmed video: {result_path}")
                
        except Exception as e:
            print(f"❌ Error: {e}", file=sys.stderr)
            sys.exit(1)
            
    elif args.command == "info":
        try:
            trimmer = YoutubeTrimmer(quiet=True)
            info = trimmer.get_video_info(args.url)
            
            print(f"Title: {info.get('title', 'Unknown')}")
            print(f"Duration: {info.get('duration', 'Unknown')} seconds")
            print(f"Uploader: {info.get('uploader', 'Unknown')}")
            print(f"Views: {info.get('view_count', 'Unknown')}")
            print(f"Upload Date: {info.get('upload_date', 'Unknown')}")
            print(f"Video ID: {info.get('id', 'Unknown')}")
            
        except Exception as e:
            print(f"❌ Error: {e}", file=sys.stderr)
            sys.exit(1)
            
    elif args.command == "mcp-server":
        try:
            from .mcp_server import main as mcp_main
            print("🚀 Starting YouTube Trimmer MCP Server...")
            mcp_main()
        except ImportError:
            print(
                "❌ MCP dependencies not installed. Install with: pip install -e '.[mcp]'",
                file=sys.stderr
            )
            sys.exit(1)
        except KeyboardInterrupt:
            print("\n🛑 MCP Server stopped")
        except Exception as e:
            print(f"❌ Error starting MCP server: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        parser.print_help()


if __name__ == "__main__":
    main() 