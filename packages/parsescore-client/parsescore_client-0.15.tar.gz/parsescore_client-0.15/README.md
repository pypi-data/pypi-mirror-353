# ParseScore

ParseScore is a system for collecting, processing, and displaying player performance data from Warcraft Logs.

## Components

The system consists of three main components:

2. **Client**: Fetches data from the server and converts it to a format usable by the addon


### Features

- Scheduled data collection that runs hourly
- Error recovery mechanisms for API outages and rate limiting
- Comprehensive logging system
- Data validation for consistency and quality
- Configuration system for customizable collection parameters

### Setup

1. Ensure you have Python 3.14 or later installed
2. Create a virtual environment:
   ```
   uv venv
   ```
3. Activate the virtual environment:
   ```
   # On Windows (PowerShell):
   .\.venv\Scripts\Activate.ps1
   # On Windows (Command Prompt):
   .venv\Scripts\activate
   # On Unix/MacOS:
   source .venv/bin/activate
   ```
4. Install dependencies:
   ```
   uv sync
   ```
5. Set up environment variables in a `.env` file:
   ```
   WCL_CLIENT_ID=your_client_id
   WCL_CLIENT_SECRET=your_client_secret
   WCL_TOKEN=your_token
   WCL_RECENT_REPORTS_URL=your_reports_url
   ```

### Configuration

The server can be configured using a `config.yaml` file in the project root. If this file doesn't exist, a default one
will be created when the server is first run.

The configuration file has the following sections:

- **api**: API-related settings (rate limits, timeouts, etc.)
- **data_collection**: Settings for the data collection process
- **database**: Database settings
- **logging**: Logging configuration
- **urls**: URL settings
- **zones**: Zone ID settings

Example configuration:

```yaml
api:
  rate_limit: 9000
  rate_limit_threshold: 8500
  max_retries: 5
  timeout: 60
  batch_interval: 1
data_collection:
  schedule_interval_seconds: 3600  # 1 hour
  max_reports_to_process: 10
  concurrent_requests: 5
database:
  path: db.sqlite3
  backup_interval_days: 7
  max_backups: 5
logging:
  file: logs/server.log
  rotation: 10 MB
  retention: 1 week
  format: "{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}"
  level: INFO
urls:
  recent_reports: https://www.example.com/reports
  api_endpoint: https://www.warcraftlogs.com/api/v2/client
zones:
  current_zone_id: 43
```

### Running the Server

To run the server with the default scheduled task system:

```
python -m src.server.main
```

To run the data collection task once and exit:

```
python -m src.server.main --run-once
```

To test the configuration system:

```
python -m src.server.main --test-config
```

Alternatively, you can use the test script:

```
python -m tests.test_config
```

## Client

The client is a Python application that fetches data from the server and converts it to a format usable by the addon.

*Client implementation is in progress.*

## Addon

The addon is a World of Warcraft addon that displays player performance data in-game.

*Addon implementation is in progress.*

## Development

### Running Tests

To run the tests:

```
python -m pytest
```

### Code Style

The project uses `ruff` for linting and formatting:

```
# Check for linting errors and apply automatic fixes
ruff check --fix .

# Format all files
ruff format .
```

### Type Checking

The project uses `ty` for static type checking:

```
ty check .
```
