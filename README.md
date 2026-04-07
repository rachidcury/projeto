<h1 align="center"> DevLinks + Research Assistant </h1>

<p align="center">
  <img alt="License" src="https://img.shields.io/static/v1?label=license&message=MIT&color=49AA26&labelColor=000000">
</p>

This repository contains two projects:

1. **DevLinks** — a link aggregator page (HTML/CSS/JS)
2. **Research Assistant** — a Python CLI tool powered by [notebooklm-py](https://github.com/teng-lin/notebooklm-py) to automate Google NotebookLM workflows

---

## Research Assistant

A Python project that wraps `notebooklm-py` to provide a high-level interface for automating research with Google NotebookLM.

### Features

- Create notebooks and add sources (URLs, files, text)
- Ask questions against your sources with citations
- Generate AI summaries of notebooks
- Generate audio podcasts from your research
- Generate written reports (briefing docs, study guides, blog posts)
- Generate quizzes with configurable difficulty
- Export Q&A results as JSON
- Full CLI for all operations

### Requirements

- Python 3.10+
- A Google account with access to NotebookLM

### Installation

```bash
# Install the package
pip install -e .

# For browser-based login support
pip install -e ".[browser]"
playwright install chromium
```

### Authentication

Log in to NotebookLM via the CLI:

```bash
notebooklm login
```

### CLI Usage

```bash
# List all notebooks
research-assistant list

# Create a notebook with URL sources
research-assistant create "My Research" --url "https://example.com" --url "https://example2.com"

# Create a notebook with local files
research-assistant create "Paper Review" --file ./paper.pdf

# Ask questions
research-assistant ask <notebook_id> "What are the key findings?" "What methodology was used?"

# Ask questions and save results as JSON
research-assistant ask <notebook_id> "Summarize the main points" -o results.json

# Get a summary
research-assistant summary <notebook_id>

# Generate a podcast
research-assistant podcast <notebook_id> -o my_podcast.mp3 --instructions "Make it fun"

# Generate a report
research-assistant report <notebook_id> -o report.txt --template study_guide

# Generate a quiz
research-assistant quiz <notebook_id> -n 15 --difficulty hard -o quiz.json

# Delete a notebook
research-assistant delete <notebook_id>
```

### Python API

```python
import asyncio
from research_assistant import ResearchAssistant

async def main():
    async with ResearchAssistant() as ra:
        # Create a notebook with sources
        nb_id = await ra.create_project(
            "AI Research",
            urls=["https://en.wikipedia.org/wiki/Artificial_intelligence"],
        )

        # Ask questions
        result = await ra.ask(nb_id, "What are the main branches of AI?")
        print(result.answer)

        # Generate a podcast
        await ra.generate_podcast(nb_id, "podcast.mp3")

asyncio.run(main())
```

See the `examples/` directory for more usage patterns.

### Project Structure

```
src/research_assistant/
    __init__.py          # Package exports
    app.py               # Core ResearchAssistant class
    cli.py               # CLI entry-point
examples/
    quick_start.py       # Basic usage
    generate_podcast.py  # Podcast generation
    batch_research.py    # Batch Q&A with JSON export
```

---

## DevLinks

O DevLinks e um agregador de links para usar como cartao de visitas online.

### Tecnologias

- HTML e CSS
- JavaScript
- Git e Github

## Licenca

Esse projeto esta sob a licenca MIT.