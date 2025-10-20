# Quickstart Guide: LLM-Powered Legal Agents

Your Themis legal agent system is now **powered by AI**! This guide will help you get it running in 5 minutes.

## What's New

Your three agents now use Claude AI to:
- **LDA (Legal Data Analyst)**: Extract facts from documents using natural language understanding
- **DEA (Doctrinal Expert)**: Identify legal issues and generate sophisticated legal analysis
- **LSA (Legal Strategist)**: Create comprehensive strategies and risk assessments

## Setup (5 minutes)

### 1. Get an Anthropic API Key

1. Go to: https://console.anthropic.com/
2. Sign up or log in
3. Navigate to "API Keys"
4. Create a new API key
5. Copy the key (starts with `sk-ant-...`)

### 2. Configure Your Environment

Edit the `.env` file in the project root:

```bash
# Replace 'your_api_key_here' with your actual API key
ANTHROPIC_API_KEY=sk-ant-api03-your-actual-key-here
```

### 3. Install Dependencies

```bash
# Install the package with new dependencies
pip install -e .
```

### 4. Run the Demo

```bash
python test_llm_agents.py
```

You should see:
- Facts being extracted from documents
- Legal issues being identified
- A comprehensive legal analysis being generated
- Strategic recommendations and risk assessment

## What Each Agent Does Now

### LDA - Legal Data Analyst
**Before:** Extracted pre-labeled facts from JSON
**Now:** Uses AI to:
- Read document text and extract key facts
- Identify parties mentioned
- Extract dates and timeline events
- Summarize documents intelligently

### DEA - Doctrinal Evaluation Agent
**Before:** Returned hardcoded legal issues
**Now:** Uses AI to:
- Spot legal issues from fact patterns
- Categorize issues by area of law (tort, contract, etc.)
- Assess strength of each issue (strong/moderate/weak)
- Write comprehensive legal analysis applying law to facts

### LSA - Legal Strategy Agent
**Before:** Used template-based strategy
**Now:** Uses AI to:
- Develop negotiation strategies
- Identify leverage points and concessions
- Create contingency plans
- Assess risks and confidence scores

## Next Steps

### Try Your Own Case

Edit `test_llm_agents.py` and modify the `matter` dictionary:

```python
matter = {
    "summary": "Your case summary here",
    "parties": ["Party 1", "Party 2"],
    "documents": [
        {
            "title": "Document Title",
            "content": "Document text content here...",
            "date": "2024-01-15",
        }
    ],
    # ... add your case details
}
```

### Add PDF Support

The system already supports PDFs! Just provide a file path:

```python
{
    "title": "Contract Agreement",
    "file_path": "/path/to/document.pdf",
    "date": "2024-01-15",
}
```

### Start the API Server

Run the full REST API:

```bash
uvicorn api.main:app --reload
```

Then visit: http://localhost:8000/docs to see the API documentation

### API Usage Example

```bash
# Create a plan
curl -X POST http://localhost:8000/orchestrator/plan \
  -H "Content-Type: application/json" \
  -d '{"summary": "Contract dispute case", "parties": ["Client", "Vendor"]}'

# Execute the plan (replace {plan_id} with actual ID)
curl -X POST http://localhost:8000/orchestrator/execute/{plan_id} \
  -H "Content-Type: application/json" \
  -d '{"summary": "Contract dispute case", "parties": ["Client", "Vendor"]}'

# Get results
curl http://localhost:8000/orchestrator/artifacts/{plan_id}
```

## Understanding the Code

### Key Files

- `tools/llm_client.py` - Wrapper for Anthropic Claude API
- `tools/document_parser.py` - PDF and text extraction with AI
- `agents/lda.py` - Legal Data Analyst with AI fact extraction
- `agents/dea.py` - Doctrinal Expert with AI legal analysis
- `agents/lsa.py` - Legal Strategist with AI strategy generation

### How It Works

1. **LLM Client** (`tools/llm_client.py`):
   - Connects to Anthropic's Claude API
   - Provides `generate_structured()` for JSON responses
   - Provides `generate_text()` for free-form analysis

2. **Document Parser** (`tools/document_parser.py`):
   - Extracts text from PDFs using `pypdf`
   - Sends content to Claude for intelligent fact extraction
   - Returns structured data (facts, dates, parties)

3. **Agents** use LLM in their tools:
   - Each agent has a system prompt defining its role
   - User prompts provide case context
   - Claude returns structured analysis
   - Fallback logic handles errors gracefully

### Example: How LDA Works

```python
# 1. Build context from the matter
context = {
    "summary": matter.get("summary"),
    "parties": matter.get("parties"),
}

# 2. Create system prompt (defines role)
system_prompt = """You are a legal document analyst.
Extract key facts from legal documents."""

# 3. Create user prompt (provides data)
user_prompt = f"""Analyze this document:
{document_content}

Extract: facts, dates, parties mentioned"""

# 4. Call LLM
result = await llm.generate_structured(
    system_prompt=system_prompt,
    user_prompt=user_prompt,
)
```

## Troubleshooting

### "ANTHROPIC_API_KEY not set"
- Make sure `.env` file exists and contains your API key
- Ensure the key starts with `sk-ant-`
- Don't use quotes around the key in `.env`

### "Rate limit exceeded"
- You're making too many API calls too quickly
- Anthropic has rate limits based on your plan tier
- Add delays between requests or upgrade your plan

### "Invalid API key"
- Your API key may be expired or invalid
- Generate a new key from console.anthropic.com
- Make sure you copied the entire key

### Import Errors
- Run `pip install -e .` to install all dependencies
- Make sure you're in the project root directory

### Empty/Poor Results
- Check that your matter has sufficient detail
- Provide document content, not just titles
- Include context (parties, dates, summary)

## Cost Considerations

Each API call costs money. Approximate costs (as of 2024):

- **LDA** (fact extraction): ~$0.01-0.05 per document
- **DEA** (legal analysis): ~$0.02-0.10 per matter
- **LSA** (strategy): ~$0.02-0.08 per matter
- **Full pipeline**: ~$0.05-0.25 per matter

Tips to reduce costs:
- Use smaller documents (truncate to 10,000 chars)
- Cache results to avoid re-processing
- Use Claude Haiku (cheaper) for simple tasks
- Monitor usage in Anthropic console

## What's Next?

Your system now has a "brain"! Here's what to build next:

1. **RAG Integration**: Add a vector database for legal case lookup
2. **Citation Verification**: Validate that cited cases actually exist
3. **Guardrails**: Add confidence thresholds before sending documents
4. **Web Interface**: Build a simple UI with Streamlit or Gradio
5. **Document Upload**: Add file upload endpoint to API
6. **Practice Packs**: Customize prompts for different practice areas

## Learn More

- Anthropic Documentation: https://docs.anthropic.com/
- Prompt Engineering Guide: https://docs.anthropic.com/claude/docs/prompt-engineering
- API Reference: https://docs.anthropic.com/claude/reference/

## Need Help?

- Check the full README.md for architecture details
- Review agent code in `/agents` directory
- Look at test files in `/tests` for examples
- Experiment with prompts in `test_llm_agents.py`

Happy coding! You now have an AI-powered legal assistant.
