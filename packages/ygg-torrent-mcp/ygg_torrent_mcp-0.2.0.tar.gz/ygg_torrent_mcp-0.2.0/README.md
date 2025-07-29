# YggTorrent MCP Server & Wrapper

This repository provides a Python wrapper for the YggTorrent website and an MCP (Model Context Protocol) server to interact with it programmatically. This allows for easy integration of YggTorrent functionalities into other applications or services.



## Features

-   API wrapper for [YggAPI](https://yggapi.eu/), an unofficial API for YggTorrent.
-   **Your Ygg passkey is not exposed, but injected locally in the torrent file/magnet link instead.**
-   MCP server interface for standardized communication.
-   Search for torrents on YggTorrent (MCP tool).
-   Get details for a specific torrent (MCP tool).
-   Retrieve magnet links (MCP tool).
-   Retrieve torrent files (wrapper only).
-   Retrieve torrent categories (MCP resource).

## Setup

There are two primary ways to set up and run this project: using a local Python environment or using Docker.

### Prerequisites

-   Python 3.10+ (for local Python setup)
-   pip (Python package installer, for local Python setup)
-   Docker and Docker Compose (for Docker setup)

### 0. Install from PyPI

```bash
pip install ygg-torrent-mcp
```

### 1. Local Python Environment Setup

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/philogicae/ygg-torrent-mcp.git
    cd ygg-torrent-mcp
    ```

2.  **Create and activate a virtual environment (recommended):**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    # On Windows, use: venv\Scripts\activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -e .
    ```

4.  **Configure environment variables (if any):**
    Copy the `.env.example` file to `.env` and fill in the required variables (Ygg passkey).

5.  **Run the MCP Server:**
    ```bash
    python -m ygg_torrent.mcp_server
    ```
    The MCP server will be accessible locally on port 8000.

### 2. Docker Setup

This project includes a `Dockerfile` and `docker-compose.yaml` for easy containerization.

1.  **Clone the repository (if you haven't already):**
    ```bash
    git clone https://github.com/philogicae/ygg-torrent-mcp.git
    cd ygg-torrent-mcp
    ```

2.  **Build and run the Docker container using Docker Compose:**
    Run:
    ```bash
    docker-compose -f docker/compose.yaml up --build
    ```
    This command will build the Docker image (if it doesn't exist) and start the service on port 8765.

3.  **Accessing the server:**
    The MCP server will be accessible on port 8765.

## Usage

### As Python Wrapper

```python
from ygg_torrent_mcp import ygg_api

results = ygg_api.search_torrents('...')
for torrent in results:
    print(torrent.name, torrent.size, torrent.seeders)
```

### As MCP Server

```python
from ygg_torrent_mcp import ygg_mcp

ygg_mcp.run(transport="sse", host="0.0.0.0", port=8000)
```

### Via MCP Clients

Once the MCP server is running, you can interact with it using any MCP-compatible client. The server will expose endpoints for:

-   `search_torrents`: Search for torrents.
-   `get_torrent_details`: Get details of a specific torrent.
-   `get_magnet_link`: Get the magnet link for a torrent.

#### Example for Windsurf

```
{
  "mcpServers": {
    "mcp-ygg-torrent": {
      "serverUrl": "http://127.0.0.1:8000/sse"
    }
  }
}

```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request or open an Issue.