#!/bin/bash
# Themis Framework - Local Setup Script
# This script sets up the Themis framework on your local machine

set -e  # Exit on any error

echo "🚀 Themis Framework - Local Setup"
echo "=================================="
echo ""

# Check if we're in the right directory
if [ ! -f "pyproject.toml" ]; then
    echo "❌ Error: Please run this script from the themis-framework directory"
    exit 1
fi

# Step 1: Create virtual environment
echo "📦 Step 1: Creating virtual environment..."
if [ -d ".venv" ]; then
    echo "✓ Virtual environment already exists"
else
    python3 -m venv .venv
    echo "✓ Virtual environment created"
fi

# Step 2: Activate virtual environment and install dependencies
echo ""
echo "📚 Step 2: Installing dependencies..."
source .venv/bin/activate
pip install --upgrade pip > /dev/null 2>&1
pip install -e .
echo "✓ Dependencies installed"

# Step 3: Configure environment
echo ""
echo "⚙️  Step 3: Configuring environment..."
if [ -f ".env" ]; then
    echo "✓ .env file already exists"
else
    cp .env.example .env
    echo "✓ .env file created from template"
fi

# Step 4: Check for API key
echo ""
echo "🔑 Step 4: Checking API configuration..."
if grep -q "ANTHROPIC_API_KEY=replace-me" .env; then
    echo "⚠️  WARNING: ANTHROPIC_API_KEY is not configured in .env"
    echo ""
    read -p "Do you want to enter your Anthropic API key now? (y/n) " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        read -p "Enter your Anthropic API key: " api_key
        # Use sed to replace the API key on macOS and Linux
        if [[ "$OSTYPE" == "darwin"* ]]; then
            sed -i '' "s/ANTHROPIC_API_KEY=replace-me/ANTHROPIC_API_KEY=$api_key/" .env
        else
            sed -i "s/ANTHROPIC_API_KEY=replace-me/ANTHROPIC_API_KEY=$api_key/" .env
        fi
        echo "✓ API key configured"
    else
        echo "⚠️  You can add it later by editing .env"
    fi
else
    echo "✓ API key is configured"
fi

echo ""
echo "✅ Setup Complete!"
echo ""
echo "To start the Themis server:"
echo "  1. Activate the virtual environment:"
echo "     source .venv/bin/activate"
echo ""
echo "  2. Start the server:"
echo "     uvicorn api.main:app --reload"
echo ""
echo "  3. Open your browser to:"
echo "     http://localhost:8000"
echo ""
echo "Happy analyzing! ⚖️"
