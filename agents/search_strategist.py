import os
import re
from ddgs import DDGS
import openai
import json

class SearchStrategistAgent:
    def __init__(self, openai_client=None):
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.openai_client = openai_client or openai

    def get_sites(self, country: str, product_name: str):
        query = f"{product_name} in {country} "
        print("[DDGS] DuckDuckGo search query:", query)
        urls = []
        with DDGS() as ddgs:
            results = ddgs.text(query, max_results=50)
            for r in results:
                if 'href' in r:
                    urls.append(r['href'])
        print("[DDGS] DuckDuckGo found URLs:", urls)
        # Use OpenAI to filter for ALL real product pages
        prompt = (
            f"Given this list of URLs, which ones are real product pages for buying {product_name} ?   date: {urls}"
            f"Return a JSON array of ALL relevant product page URLs (not just the best one) and each url must be unique website"
        )
        filtered_urls = []
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=512,
                temperature=0.2,
            )
            content = response.choices[0].message.content
            print("[OpenAI] Filtering URLs response:", content)
            # Try to extract JSON array from response
            try:
                filtered_urls = json.loads(content)
            except Exception:
                match = re.search(r'\[(.*?)\]', content, re.DOTALL)
                if match:
                    filtered_urls = json.loads('[' + match.group(1) + ']')
            print("[OpenAI] Filtered product URLs:", filtered_urls)
        except Exception as e:
            print(f"[OpenAI] Error filtering URLs: {e}")
        # Fallback: if OpenAI returns nothing, use all DuckDuckGo URLs
        if not filtered_urls:
            print("[Strategist] OpenAI returned no URLs, using all DuckDuckGo URLs.")
            filtered_urls = urls
        sites = [{"site": re.sub(r"https?://(www\.)?", "", url).split("/")[0], "url": url} for url in filtered_urls]
        print("[Strategist] Final product sites:", sites)
        return sites
