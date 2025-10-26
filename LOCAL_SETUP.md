# Themis Framework - Local Setup Guide

This guide will help you set up and run Themis on your local machine.

## Quick Setup (Automated)

We've created an automated setup script for you:

```bash
# 1. Clone the repository (if you haven't already)
git clone https://github.com/themis-agentic-system/themis-framework.git
cd themis-framework

# 2. Checkout the branch with the landing page
git checkout claude/setup-project-environment-011CUV8WXPndZLw1DMkX4tzj

# 3. Run the setup script
./setup-local.sh
```

The script will:
- ✅ Create a Python virtual environment
- ✅ Install all dependencies
- ✅ Create your `.env` configuration file
- ✅ Optionally configure your Anthropic API key

## Manual Setup

If you prefer to set up manually:

### 1. Create Virtual Environment

```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install -e .
```

### 3. Configure Environment

```bash
cp .env.example .env
```

Edit `.env` and add your Anthropic API key:

```bash
ANTHROPIC_API_KEY=sk-ant-api03-your-key-here
```

## Running Themis

### Start the Server

```bash
# Make sure virtual environment is activated
source .venv/bin/activate

# Start the server
uvicorn api.main:app --reload
```

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
```

### Access the Interface

Open your browser to:

- **Landing Page**: http://localhost:8000
  - Beautiful UI with document upload and case intake form

- **API Documentation**: http://localhost:8000/docs
  - Interactive Swagger UI to test API endpoints

- **API Reference**: http://localhost:8000/redoc
  - Clean documentation in ReDoc format

- **Health Check**: http://localhost:8000/health
  - Quick system status check

## Using the Landing Page

The landing page provides a user-friendly interface to submit legal matters to Themis:

### Required Information:
- **Case Summary** (minimum 10 characters)
- **At least one Party** name

### Optional Information:
- Jurisdiction (defaults to California)
- Cause of Action
- Documents (upload or describe)
- Damages (special, general, punitive)

### Submission Process:

1. Fill out the case information form
2. Add parties involved
3. Upload documents or describe them manually
4. Enter damages if applicable
5. Click "🚀 Submit to Themis"

The AI agents will analyze your matter and return:
- ✅ Factual analysis (LDA)
- ✅ Legal doctrinal analysis (DEA)
- ✅ Strategic recommendations (LSA)
- ✅ Draft documents (DDA)

## Troubleshooting

### Port Already in Use

If port 8000 is already in use:

```bash
uvicorn api.main:app --reload --port 8080
```

Then access at http://localhost:8080

### Virtual Environment Issues

On some systems, you may need to use `python` instead of `python3`:

```bash
python -m venv .venv
```

### Missing Dependencies

If you encounter import errors:

```bash
source .venv/bin/activate
pip install --upgrade pip
pip install -e .
```

## Development Mode

The server runs in development mode with auto-reload enabled. Any changes to the code will automatically restart the server.

To run in production mode:

```bash
uvicorn api.main:app --host 0.0.0.0 --port 8000
```

## Next Steps

- 📖 Read the [QUICKSTART.md](QUICKSTART.md) for usage examples
- 📚 Check [DEPLOYMENT_GUIDE.md](docs/DEPLOYMENT_GUIDE.md) for production deployment
- 🐳 Use Docker: `docker-compose up` for containerized deployment

## Need Help?

- Check the main [README.md](README.md) for detailed documentation
- Visit the API docs at http://localhost:8000/docs when the server is running
- Review practice pack examples in `packs/personal_injury/` and `packs/criminal_defense/`

---

⚖️ Happy analyzing with Themis!
