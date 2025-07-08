# AI Price Tracker

## Overview
AI Price Tracker is a web application that uses OpenAI-powered agents to extract product information, find relevant e-commerce sites, and scrape product prices globally. It features a FastAPI backend and a simple HTML/JS frontend.

---

## Features
- Enter a product query and country to search for product prices across multiple e-commerce sites.
- Uses LLMs to normalize queries, find relevant sites, and extract product/price data from HTML.
- Handles generic and specific queries, and displays all results (including errors/warnings) in the UI.

---

## Setup Instructions

### 1. Clone the Repository
```bash
git clone <your-repo-url>
cd ai-price-tracker
```

### 2. Install Python Dependencies
It is recommended to use a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Set Up Environment Variables
Create a `.env` file in the project root with your OpenAI API key (and optional scraping API keys):
```
OPENAI_API_KEY=your-openai-api-key
SCRAPING_API_KEY=your-scrapingbee-api-key   # Optional, for scraping
SCRAPERAPI_KEY=your-scraperapi-key          # Optional, fallback for scraping
```
**Do not commit your `.env` file or API keys to version control.**

### 4. Run the Backend Server
Start the FastAPI server using Uvicorn:
```bash
uvicorn main:app --reload
```
- The API will be available at: `http://localhost:8000/`
- The frontend HTML page is at: `resource/index.html` (open in your browser)

### 5. Using the Frontend
- Open `resource/index.html` in your browser.
- Enter a product query and select a country.
- Click "Search Prices" to view results.

### 6. Example API Usage
You can also use `curl` to test the API:
```bash
curl -X POST http://localhost:8000/fetch-prices \
  -H "Content-Type: application/json" \
  -d '{"country": "US", "query": "iPhone 16 Pro, 128GB"}'
```

---

## Troubleshooting
- **No results or errors?**
  - Check your API keys in `.env`.
  - Ensure you have internet access.
  - Some sites may block scraping; warnings will be shown in the UI.
- **CORS issues?**
  - If you want to serve the frontend via FastAPI, you can add a static files route in `main.py`.
- **LLM errors?**
  - Make sure your OpenAI API key is valid and has quota.

---

## Security
- Never commit your `.env` or API keys.
- This project is for demonstration and research purposes only.

---

## Credits
- Built with FastAPI, OpenAI, BeautifulSoup, and DuckDuckGo Search.
- See `requirements.txt` for all dependencies.
