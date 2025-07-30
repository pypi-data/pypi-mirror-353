#!/bin/bash
set -e

echo "Building polars-gps-hilbert plugin with UV..."
echo "==========================================="

# Ensure UV is in PATH
export PATH="/Users/ryan/.local/bin:$PATH"

# Install UV if not already installed
if ! command -v uv &> /dev/null; then
    echo "Installing UV..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="/Users/ryan/.local/bin:$PATH"
fi

# Create virtual environment and install dependencies
echo "Setting up Python environment with UV..."
uv venv
source .venv/bin/activate

# Install all dependencies including dev dependencies
echo "Installing dependencies..."
uv sync --dev

# Build the plugin
echo -e "\n\nBuilding Rust extension..."
uv run maturin develop --release

# Generate test data
echo -e "\n\nGenerating test data..."
echo "======================="
cd examples
uv run python generate_sample_data.py

# Run basic tests
echo -e "\n\nRunning basic tests..."
echo "======================"
cd ..
uv run pytest tests/test_basic.py -v

# Run examples
echo -e "\n\nRunning examples..."
echo "=================="
cd examples
uv run python basic_usage.py

echo -e "\n\nBuild and test completed successfully!"
echo "Next steps:"
echo "  - Run 'pytest tests/' for full test suite"
echo "  - Run 'python examples/generate_sample_data.py --full' for 200M dataset"
echo "  - Run 'python examples/benchmark_200M.py' for large-scale benchmarks"