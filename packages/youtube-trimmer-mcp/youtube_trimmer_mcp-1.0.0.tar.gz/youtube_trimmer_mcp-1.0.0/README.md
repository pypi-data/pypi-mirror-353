# YouTube Trimmer

A command-line tool that downloads YouTube videos, trims them to a specific timeframe, and saves the clip. Now with **MCP (Model Context Protocol) server** support for natural language interaction!

## Features

- 📺 Download and trim YouTube videos to specific timeframes
- ⚡ Fast, lossless trimming using FFmpeg (no re-encoding)
- 🤖 **MCP Server** for natural language interaction
- 📊 Get video information without downloading
- 🔧 Both CLI and programmatic interfaces

## Prerequisites

| Dependency | Purpose | Installation (Ubuntu) | Installation (macOS) | Installation (Windows) |
|------------|---------|----------------------|----------------------|------------------------|
| Python ≥ 3.8 | Runtime | `sudo apt install python3` | `brew install python` | Download from [python.org](https://www.python.org/downloads/) |
| FFmpeg | Video trimming | `sudo apt install ffmpeg` | `brew install ffmpeg` | Download the [static build](https://ffmpeg.org/download.html) and add to PATH |

## Installation

### 🚀 Super Easy Installation (Recommended)

**The easiest way to install is directly from PyPI:**

```bash
# Install the complete package with MCP support
pip install youtube-trimmer-mcp
```

That's it! The package will be available globally with all dependencies.

### Alternative Installation Methods

#### From Source (Development)
```bash
# Clone the repository
git clone https://github.com/manuelgomez/youtube-trimmer-mcp.git
cd youtube-trimmer-mcp

# Install in development mode
pip install -e ".[dev]"
```

#### Using pipx (Isolated Installation)
```bash
# Install in isolated environment (recommended for CLI tools)
pipx install youtube-trimmer-mcp
```

## Usage

### 1. Command Line Interface

#### Trim a video:
```bash
youtube-trimmer trim <youtube_url> -s <start_time> -e <end_time> [-o output.mp4] [--keep-temp]
```

#### Get video information:
```bash
youtube-trimmer info <youtube_url>
```

#### Start MCP server:
```bash
youtube-trimmer mcp-server
```

### 2. MCP Server (NEW!) 🚀

The YouTube Trimmer now supports the Model Context Protocol, allowing you to trim videos using natural language through any MCP-compatible client!

#### Starting the MCP Server

```bash
# Using the CLI command
youtube-trimmer mcp-server

# Or using the direct entry point
youtube-trimmer-mcp
```

#### MCP Client Configuration

Add this to your MCP client configuration (e.g., in Claude Desktop):

```json
{
  "mcpServers": {
    "youtube-trimmer": {
      "command": "youtube-trimmer-mcp",
      "args": [],
      "env": {}
    }
  }
}
```

**Alternative configuration using the module:**
```json
{
  "mcpServers": {
    "youtube-trimmer": {
      "command": "python",
      "args": ["-m", "youtube_trimmer.mcp_server"],
      "env": {}
    }
  }
}
```

#### MCP Tools Available

- **trim_youtube_video**: Download and trim YouTube videos
- **get_youtube_video_info**: Get video information without downloading
- **convert_timestamp_to_seconds**: Convert timestamps to seconds
- **download_full_youtube_video**: Download complete videos

### Arguments and Options:

- `<youtube_url>`: Any normal or shortened YouTube link
- `-s, --start`: Start timestamp (HH:MM:SS[.ms] format)
- `-e, --end`: End timestamp (HH:MM:SS[.ms] format)  
- `-o, --output`: Output filename (auto-generated if not provided)
- `--keep-temp`: Keep the full downloaded file
- `--quiet`: Suppress most output

### Examples:

#### CLI Examples:

```bash
# Trim from 1 minute to 2 minutes
youtube-trimmer trim "https://www.youtube.com/watch?v=dQw4w9WgXcQ" -s 1:00 -e 2:00

# Get video information
youtube-trimmer info "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

# Custom output filename
youtube-trimmer trim "https://www.youtube.com/watch?v=dQw4w9WgXcQ" -s 1:00 -e 2:00 -o my_clip.mp4
```

#### MCP Natural Language Examples:

With the MCP server running, you can use natural language:
- "Trim the YouTube video at https://youtube.com/watch?v=abc123 from 1:30 to 2:45"
- "Get information about this YouTube video: https://youtube.com/watch?v=xyz789"
- "Download the first 30 seconds of https://youtube.com/watch?v=example"

## Project Structure

```
YotubeTrimmer/
├─ src/
│  └─ youtube_trimmer/
│     ├─ __init__.py          # Package initialization
│     ├─ core.py              # Core trimming functionality  
│     ├─ cli.py               # Command-line interface
│     └─ mcp_server.py        # MCP server for natural language
├─ setup.py                   # Package setup
├─ pyproject.toml            # Modern Python packaging
├─ requirements.txt          # Dependencies
└─ README.md                 # This file
```

## Development

### Running Tests
```bash
# Install in development mode
pip install -e ".[mcp]"

# Test the CLI
youtube-trimmer trim "https://www.youtube.com/watch?v=jNQXAC9IVRw" -s 0:00 -e 0:05

# Test the MCP server
youtube-trimmer mcp-server
```

## Notes

- Timestamp formats: `SS`, `MM:SS`, or `HH:MM:SS[.ms]`
- Uses FFmpeg's copy mode (fast and lossless)
- Auto-generates output filenames from video title and timestamps
- MCP server runs on stdio for seamless integration

## Legal Notice

Downloading YouTube videos may violate YouTube's Terms of Service. This tool is for educational purposes only. Users are responsible for how they use this software.