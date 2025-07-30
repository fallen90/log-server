# Log Server

A FastAPI-based log aggregation server that accepts log messages via HTTP and provides endpoints for searching and retrieving logs.

## Features

- **Log Ingestion**: Accept log messages via HTTP POST with custom program identification
- **Real-time Writing**: Asynchronous log writing to daily log files
- **Log Retrieval**: Get the last N lines from today's logs
- **Search**: Search through logs with case-insensitive text matching
- **Log Management**: List available log files

## Installation

This project uses [uv](https://github.com/astral-sh/uv) for dependency management.

```bash
# Clone the repository
git clone <your-repo-url>
cd log-server

# Install dependencies
uv sync
```

## Usage

### Starting the Server

```bash
# Using uv
uv run python main.py

# Or using uvicorn directly
uv run uvicorn main:app --host 0.0.0.0 --port 8000
```

The server will start on `http://localhost:8000` by default.

### API Endpoints

#### POST `/log` - Send Log Message

Send a log message to be stored.

**Headers:**
- `X-Program` (optional): Name of the program sending the log (defaults to "unknown")

**Body:** Raw text log message

**Example:**
```bash
curl -X POST http://localhost:8000/log \
  -H "X-Program: myapp" \
  -d "This is a log message"
```

**Response:**
```json
{"status": "queued"}
```

#### GET `/tail?lines=N` - Get Recent Logs

Retrieve the last N lines from today's log file.

**Parameters:**
- `lines` (optional): Number of lines to retrieve (default: 50)

**Example:**
```bash
curl "http://localhost:8000/tail?lines=100"
```

**Response:**
```json
[
  "[2024-01-15T10:30:00.000000] [myapp] This is a log message",
  "[2024-01-15T10:31:00.000000] [webapp] Another log entry"
]
```

#### GET `/search?q=query` - Search Logs

Search through today's logs for a specific term (case-insensitive).

**Parameters:**
- `q`: Search query string

**Example:**
```bash
curl "http://localhost:8000/search?q=error"
```

**Response:**
```json
[
  "[2024-01-15T10:30:00.000000] [myapp] Error: Connection failed",
  "[2024-01-15T10:35:00.000000] [database] SQL error occurred"
]
```

#### GET `/logs` - List Log Files

Get a list of available log files.

**Example:**
```bash
curl http://localhost:8000/logs
```

**Response:**
```json
[
  "2024-01-14.log",
  "2024-01-15.log"
]
```

## Log Format

Logs are stored in the `./logs/` directory with the following format:

- **Filename**: `YYYY-MM-DD.log` (one file per day)
- **Entry Format**: `[timestamp] [source] message`
- **Example**: `[2024-01-15T10:30:00.000000] [myapp] Application started`

## Configuration

The server can be configured by modifying the following variables in `main.py`:

- `LOG_DIR`: Directory where log files are stored (default: "./logs")
- Host and port can be changed in the `uvicorn.run()` call

## Development

### Requirements

- Python >= 3.11
- FastAPI >= 0.116.1
- uvicorn >= 0.30.0

### Project Structure
