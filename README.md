# AI Price Tracker

## Overview
This project demonstrates an AI-powered price tracker that uses OpenAI agents to extract product information, find relevant e-commerce sites, and scrape product prices.

## Limitations of LLM-Only Approach
OpenAI's GPT models (and similar LLMs) cannot directly execute code, run `curl`, or fetch live data from the internet. All web requests and scraping must be performed by your Python code, which then passes the data (such as HTML) to the LLM for analysis.

## For a More “Agentic” System
If you want a more agentic system—where the AI can autonomously browse, search, and interact with the web—you should look into frameworks like:

- [LangChain](https://python.langchain.com/docs/integrations/tools/browser/): Integrates LLMs with browser tools, allowing the agent to control a browser, click links, and extract data.
- [AutoGPT](https://github.com/Significant-Gravitas/Auto-GPT): An open-source project that combines LLMs with real-world tool use, including web browsing, file system access, and more.
- [CrewAI](https://github.com/joaomdmoura/crewAI): Another agentic framework for orchestrating LLMs and tools.

These frameworks allow you to build agents that can:
- Search the web
- Click links and navigate pages
- Extract structured data from real websites
- Chain together reasoning and tool use

**Note:** These systems still require your code to handle actual HTTP requests and browser automation. The LLM provides reasoning and decision-making, but does not execute code itself.

## Example: Using LangChain for Web Browsing
```python
from langchain.tools import DuckDuckGoSearchRun
search = DuckDuckGoSearchRun()
result = search.run("iPhone 16 Pro Amazon US")
print(result)
```

For more advanced use, see the [LangChain documentation](https://python.langchain.com/docs/integrations/tools/browser/).

---

## Usage
See `curl_requests.md` for example API calls.

---

## Security
- Do not commit your `.env` file or API keys to version control.
