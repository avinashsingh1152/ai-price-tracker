from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import List, Dict, Any
import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

from agents.normalizer import NormalizerAgent
from agents.search_strategist import SearchStrategistAgent
from agents.scraper_agent import ScraperAgent
from agents.verifier import VerifierAgent
from agents.ranker import RankerAgent

app = FastAPI()
templates = Jinja2Templates(directory="resource")

class ProductQuery(BaseModel):
    country: str
    query: str
    specific: bool

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "results": None, "error": None})

@app.post("/fetch-prices", response_class=JSONResponse)
def fetch_prices(query: ProductQuery):
    try:
        print("[Pipeline] Input:", query.dict())
        # Initialize agents
        normalizer = NormalizerAgent()
        strategist = SearchStrategistAgent()
        scraper = ScraperAgent()
        verifier = VerifierAgent()
        ranker = RankerAgent()

        normalized_info = {}
        if not query.specific:
            print("[Agent 1] Calling NormalizerAgent...")
            normalized_info = normalizer.check_query_specificity(query.query)
            print("[Agent 1] Normalized info:", normalized_info)

            if normalized_info.get("status")  == "generic":
                return normalized_info
        else:
            normalized_info["matched_product"] = query.query
        # Agent 2: Get relevant shopping URLs
        print("[Agent 2] Calling SearchStrategistAgent...")
        sites = strategist.get_sites(query.country, normalized_info.get("matched_product"))
        print("[Agent 2] Sites:", sites)
        # Agent 3 & 4: Scrape and verify products
        products = []
        for site_info in sites:
            site = site_info.get('site', 'unknown')
            url = site_info.get('url', '')
            print(f"[Agent 3] Scraping {site} at {url}...")
            product_list = scraper.fetch_product_data(site, url, normalized_info.get("matched_product"))
            print(f"[Agent 3] Scraped data from {site}:", product_list)
            if product_list:
                for product_item in product_list:  # Loop directly over each dictionary in the list
                    product_item["url"] = url
            products.append(product_list)
        # Agent 5: Rank products
        print("[Agent 4] Ranking products...")
        ranked_products = ranker.rank(products)
        print("[Agent 4] Ranked products:", ranked_products)
        return {"results": ranked_products}
    except Exception as e:
        print("[Pipeline] Error:", e)
        return JSONResponse(status_code=500, content={"error": str(e)})
