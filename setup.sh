
#!/bin/bash

# Exit on error
set -e

echo "Setting up FastAPI Test Pipeline project..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is required but not installed. Please install Python 3.8 or higher."
    exit 1
fi

# Check if Poetry is installed
if ! command -v poetry &> /dev/null; then
    echo "Installing Poetry..."
    curl -sSL https://install.python-poetry.org | python3 -
fi

# Install dependencies
echo "Installing project dependencies..."
poetry install

# Create necessary directories if they don't exist
mkdir -p logs
mkdir -p tests/data

echo "Setup complete! You can now:"
echo "1. Run the development server: poetry run uvicorn app.main:app --reload"
echo "2. Run tests: poetry run pytest"
echo "3. Run linting: poetry run flake8 app tests"
echo "4. Run type checking: poetry run mypy app tests" 
