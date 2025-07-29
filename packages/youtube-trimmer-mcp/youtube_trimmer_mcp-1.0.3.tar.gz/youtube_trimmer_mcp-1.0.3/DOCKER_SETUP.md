# YouTube Trimmer MCP Server - Docker Setup

This guide explains how to run the YouTube Trimmer MCP Server in a Docker container.

## Prerequisites

- Docker installed and running
- Docker Desktop (recommended for macOS)

## Quick Start

1. **Build the Docker image:**
   ```bash
   docker build -t youtube-trimmer-mcp .
   ```

2. **Test the server:**
   ```bash
   echo "test" | docker run -i --rm youtube-trimmer-mcp
   ```

3. **Run with output volume mounted:**
   ```bash
   docker run -i --rm \
     -v "$(pwd)/output:/app/output" \
     youtube-trimmer-mcp
   ```

## Using with MCP Clients (like Cursor)

### Option 1: Direct Docker Command

Configure your MCP client to use this command:
```bash
docker run -i --rm --name youtube-trimmer-mcp-session -v /path/to/output:/app/output youtube-trimmer-mcp
```

### Option 2: Using the Shell Script

Use the provided script:
```bash
./run-mcp-docker.sh
```

### Option 3: Docker Compose

For persistent deployment:
```bash
docker-compose up -d
```

## MCP Configuration for Cursor

Add this to your MCP configuration:

```json
{
  "mcpServers": {
    "youtube-trimmer": {
      "command": "docker",
      "args": [
        "run",
        "-i",
        "--rm",
        "--name", "youtube-trimmer-mcp-session",
        "-v", "/Users/manuelgomez/Documents/YotubeTrimmer/output:/app/output",
        "youtube-trimmer-mcp"
      ],
      "description": "YouTube Trimmer MCP Server running in Docker"
    }
  }
}
```

## Available Tools

The Docker container provides these MCP tools:

- `trim_youtube_video` - Download and trim YouTube videos
- `get_youtube_video_info` - Get video information without downloading
- `convert_timestamp_to_seconds` - Convert timestamp strings to seconds
- `download_full_youtube_video` - Download complete videos

## Output Files

All downloaded and trimmed videos are saved to the `output/` directory, which is mounted as a volume from your host system.

## Troubleshooting

1. **Permission Issues**: Make sure the output directory is writable
2. **Port Conflicts**: If using docker-compose, change the port mapping in `docker-compose.yml`
3. **Container Already Running**: Use `docker stop youtube-trimmer-mcp-session` to stop any running instances

## Development

To rebuild after code changes:
```bash
docker build --no-cache -t youtube-trimmer-mcp .
``` 