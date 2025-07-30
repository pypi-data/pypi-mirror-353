# VM Balancer - Installation and Usage Guide

## Installation

### From Source (Recommended for Development)

1. Clone the repository:
```bash
git clone https://github.com/vmbalancer/vm-balancer.git
cd vm-balancer
```

2. Create a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install in development mode:
```bash
pip install -e .
```

### Using pip (Production)

```bash
pip install vm-balancer
```

### Using pyproject.toml (Modern Python)

```bash
pip install .
```

## Configuration

1. Copy the example configuration:
```bash
cp config.env.example .env
```

2. Edit `.env` with your VMManager credentials and settings.

## Usage

### Command Line Interface

After installation, you can run the balancer using any of these methods:

1. **Using the installed console script:**
```bash
vm-balancer --once --dry-run
```

2. **Using Python module:**
```bash
python -m vm_balancer --once --dry-run
```

3. **Using the main script directly:**
```bash
python main.py --once --dry-run
```

### Common Usage Examples

```bash
# Test run without migrations
vm-balancer --once --dry-run

# Run continuously every 10 minutes
vm-balancer --interval 600

# Process specific clusters only
vm-balancer --cluster-ids 1 2 3

# Enable SSH monitoring and notifications
vm-balancer --ssh-enabled --notifications

# Custom thresholds
vm-balancer --cpu-overload-threshold 8.0 --memory-overload-threshold 75.0
```

### Programmatic Usage

```python
from vm_balancer import VMBalancer, VMManagerAPI, TelegramNotifier, SSHMonitor

# Initialize API client
api = VMManagerAPI(
    host="https://your-vmmanager.com",
    username="admin",
    password="your_password"
)

# Authenticate
api.authenticate()

# Initialize optional components
telegram = TelegramNotifier(bot_token="...", chat_id="...")
ssh_monitor = SSHMonitor(username="root", private_key_path="/path/to/key")

# Initialize balancer
balancer = VMBalancer(
    api=api,
    dry_run=False,
    telegram_notifier=telegram,
    ssh_monitor=ssh_monitor
)

# Run balance cycle
balancer.run_balance_cycle()
```

## Package Structure

```
vm_balancer/
├── __init__.py          # Main package exports
├── __main__.py          # Module entry point
├── api/                 # VMManager API client
│   ├── __init__.py
│   └── client.py
├── core/                # Core balancing logic
│   ├── __init__.py
│   └── balancer.py
├── models/              # Data models
│   ├── __init__.py
│   ├── cluster.py
│   ├── node.py
│   └── vm.py
├── monitoring/          # Monitoring components
│   ├── __init__.py
│   └── ssh.py
├── notifications/       # Notification systems
│   ├── __init__.py
│   └── telegram.py
└── utils/               # Utility functions
    ├── __init__.py
    └── env.py
```

## Development

### Setup Development Environment

```bash
# Install with development dependencies
pip install -e ".[dev]"

# Or using pyproject.toml
pip install -e ".[dev,test]"
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=vm_balancer

# Run specific test file
pytest tests/test_balancer.py
```

### Code Quality

```bash
# Format code
black src/vm_balancer/

# Sort imports
isort src/vm_balancer/

# Lint code
flake8 src/vm_balancer/

# Type checking
mypy src/vm_balancer/
```

## Migration from Monolithic Version

If you're migrating from the old monolithic `vm_balancer.py` script:

1. **Backup your current configuration** and logs
2. **Install the new package** using one of the methods above
3. **Update your configuration** to use the new `.env` format
4. **Update your scripts** to use the new CLI interface
5. **Test thoroughly** in dry-run mode before production use

### Key Changes

- **Modular structure**: Code is now organized into logical modules
- **Proper packaging**: Can be installed via pip
- **Improved CLI**: Better argument handling and help text
- **Type hints**: Better IDE support and error catching
- **Configuration**: Environment-based configuration
- **Testing**: Proper test structure and coverage

## Troubleshooting

### Import Errors

If you get import errors, ensure the package is properly installed:

```bash
pip install -e .  # Development mode
# or
pip install .     # Regular installation
```

### Path Issues

For development, you can add the src directory to Python path:

```python
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
```

### Environment Variables

Ensure your `.env` file is in the correct location and has proper formatting.

## Support

- **Documentation**: See README.md and individual module documentation
- **Issues**: Report bugs on GitHub
- **Security**: See SECURITY.md for security-related issues
