# shapi
from shell to api


# shapi - Shell to API Service Generator

Transform your bash scripts into production-ready APIs with REST, WebRTC, and gRPC support.




# shapi - Shell to API Service Generator

Transform your bash scripts into production-ready APIs with REST, WebRTC, and gRPC support.

## Features

- 🚀 **Instant API Generation**: Convert any shell script into a REST API with a single command
- 🐳 **Docker Ready**: Automatic Dockerfile and docker-compose.yml generation
- 🧪 **Testing Included**: Generated test suites and Ansible playbooks
- 🔄 **Multiple Protocols**: Support for REST, WebRTC, and gRPC
- 📊 **Health Monitoring**: Built-in health checks and status endpoints
- 🔧 **Production Ready**: Makefile, monitoring, and deployment configurations

## Quick Start

### Installation

```bash
pip install shapi
```

### Generate API Service

```bash
# Generate complete service structure
shapi generate /path/to/your/script.sh --name my-service

# Or serve directly
shapi serve /path/to/your/script.sh --name my-service --port 8000
```

### Generated Structure

```
my-service/
├── main.py              # FastAPI service
├── Dockerfile           # Container configuration
├── docker-compose.yml   # Multi-service setup
├── Makefile            # Build and deployment commands
├── requirements.txt     # Python dependencies
├── test_service.py     # Test suite
├── ansible/
│   └── test.yml        # Infrastructure tests
└── script.sh           # Your original script
```

## Usage Examples

### Basic Script Conversion

```bash
#!/bin/bash
# hello.sh
echo "Hello, $1!"
```

Generate the service:
```bash
shapi generate hello.sh --name greeting-service
cd greeting-service
python main.py
```

Access your API:
- **Health Check**: `GET http://localhost:8000/health`
- **Documentation**: `GET http://localhost:8000/docs`
- **Execute Script**: `POST http://localhost:8000/run`

### API Endpoints

Every generated service includes:

- `GET /health` - Service health check
- `GET /info` - Script information
- `POST /run` - Execute script (sync/async)
- `GET /status/{task_id}` - Check async task status
- `GET /docs` - Interactive API documentation

### Example API Request

```json
POST /run
{
  "parameters": {
    "name": "World",
    "verbose": true
  },
  "async_execution": false
}
```

### Docker Deployment

```bash
# Build and run with Docker
make docker-build
make docker-run

# Or use docker-compose
docker-compose up -d
```

### Testing

```bash
# Run tests
make test

# Or directly
python -m pytest test_service.py -v
```

## Configuration

Create a `config.yaml` file for advanced configuration:

```yaml
service:
  name: "my-advanced-service"
  description: "Advanced shell script API"
  version: "1.0.0"
  
protocols:
  rest: true
  grpc: true
  webrtc: true
  
security:
  auth_required: false
  cors_enabled: true
  
monitoring:
  health_check_interval: 30
  metrics_enabled: true
```

## CLI Commands

```bash
# Generate service structure
shapi generate script.sh --name service-name --output ./output

# Serve script directly
shapi serve script.sh --host 0.0.0.0 --port 8000

# Test generated service
shapi test ./generated/service-name

# Build Docker image
shapi build ./generated/service-name
```

## Advanced Features

### Async Execution

```python
# Enable async execution for long-running scripts
response = requests.post("/run", json={
    "parameters": {"input": "data"},
    "async_execution": True
})

task_id = response.json()["task_id"]

# Check status
status = requests.get(f"/status/{task_id}")
```

### Multiple Protocols

The generated service supports multiple communication protocols:

- **REST API**: Standard HTTP endpoints
- **WebRTC**: Real-time data streaming
- **gRPC**: High-performance RPC calls

### Production Deployment

```bash
# Using Makefile
make deploy

# Manual deployment
docker-compose up -d
```

## Requirements

- Python 3.8+
- Docker (optional, for containerization)
- Bash (for shell script execution)

## Contributing

Contributions are welcome! Please see our [Contributing Guidelines](CONTRIBUTING.md).

## License

Apache License 2.0 - see [LICENSE](LICENSE) file for details.

## Support

- 📖 [Documentation](https://wronai.github.io/shapi)
- 🐛 [Issue Tracker](https://github.com/wronai/shapi/issues)
- 💬 [Discussions](https://github.com/wronai/shapi/discussions)

---

**shapi** - From shell to service in seconds! 🚀







# Contributing Guidelines
# CONTRIBUTING.md
"""
# Contributing to shapi

We welcome contributions to shapi! This document provides guidelines for contributing.

## Development Setup

1. Clone the repository:
```bash
git clone https://github.com/wronai/shapi.git
cd shapi
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install in development mode:
```bash
pip install -e .[dev]
```

## Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=shapi

# Run specific test file
pytest tests/test_core.py -v
```

## Code Style

We use black for code formatting and flake8 for linting:

```bash
# Format code
black shapi/

# Check linting
flake8 shapi/
```

## Submitting Changes

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## Reporting Issues

Please use the GitHub issue tracker to report bugs or request features.
"""