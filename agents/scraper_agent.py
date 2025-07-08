import os
import requests
import json
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import openai
import re

class ScraperAgent:
    def __init__(self):
        self.scraping_api_key = os.getenv("SCRAPING_API_KEY")
        self.api_endpoint = "https://api.scrapingbee.com/v1/"  # Example for ScrapingBee
        self.scraperapi_key = os.getenv("SCRAPERAPI_KEY")  # Optional fallback
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.openai_client = openai

    def _add_search_param(self, url, normalized_info):
        parsed = urlparse(url)
        query = normalized_info.get('model', '')
        if normalized_info.get('storage'):
            query += f" {normalized_info.get('storage')}"
        query = query.strip().replace(' ', '+')
        if parsed.query or any(x in url for x in ['search', 'product', 'item', 'dp/', 'sku=', 'asin=']):
            return url
        netloc = parsed.netloc.lower()
        if 'amazon.' in netloc:
            return f"{parsed.scheme}://{netloc}/s?k={query}"
        if 'flipkart.' in netloc:
            return f"{parsed.scheme}://{netloc}/search?q={query}"
        if 'reliancedigital.' in netloc:
            return f"{parsed.scheme}://{netloc}/search?q={query}"
        if 'walmart.' in netloc:
            return f"{parsed.scheme}://{netloc}/search/?query={query}"
        if 'bestbuy.' in netloc:
            return f"{parsed.scheme}://{netloc}/site/searchpage.jsp?st={query}"
        if 'ebay.' in netloc:
            return f"{parsed.scheme}://{netloc}/sch/i.html?_nkw={query}"
        if 'aliexpress.' in netloc:
            return f"{parsed.scheme}://{netloc}/wholesale?SearchText={query}"
        if 'cdiscount.' in netloc:
            return f"{parsed.scheme}://{netloc}/search/10/{query}.html"
        if 'carrefour.' in netloc:
            return f"{parsed.scheme}://{netloc}/s/?q={query}"
        if 'rakuten.' in netloc:
            return f"{parsed.scheme}://{netloc}/search/{query}"
        if 'mercadolivre.' in netloc or 'mercadolibre.' in netloc:
            return f"{parsed.scheme}://{netloc}/jms/mlb/ml/search?as_word={query}"
        if url.endswith('/'):
            return url + f"search?q={query}"
        else:
            return url + f"/search?q={query}"

    def fetch_html(self, url, headers=None, proxies=None):
        try:
            # Example headers to mimic a browser
            default_headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'DNT': '1',  # Do Not Track Request Header
            }
            if headers:
                default_headers.update(headers)

            response = requests.get(url, headers=default_headers, proxies=proxies, timeout=30)
            response.raise_for_status()  # Raise an exception for HTTP errors (4xx or 5xx)
            print(f"[fetch_html_direct] Successfully fetched HTML from {url}")
            return response.text, None
        except requests.exceptions.RequestException as e:
            print(f"[fetch_html_direct] Error fetching {url}: {e}")
            return None, f"Request error: {e}"
        except Exception as e:
            print(f"[fetch_html_direct] An unexpected error occurred: {e}")
            return None, f"Unexpected error: {e}"

    def fetch_product_data(self, site: str, url: str, product: str):
        try:
            if not url.startswith('http'):
                print(f"[ScraperAgent] Invalid URL: {url}")
                return [{
                    'link': url, 'productName': None, 'price': None, 'currency': None, 'site': site, 'warning': f'Invalid URL: {url}', 'url': url
                }]
            html_content, warning = self.fetch_html(url)
            if not html_content:
                return [{
                    'link': url, 'productName': None, 'price': None, 'currency': None, 'site': site, 'warning': warning, 'url': url
                }]

            data = self.clean_html_to_text(html_content)
            print(data)
            extracted_data = self._extract_with_openai_multi(data, product)
            return extracted_data
        except Exception as e:
            print(f"[ScraperAgent] General error for {url}: {e}")
            return []

    def _extract_with_bs(self, html_content, url):
        soup = BeautifulSoup(html_content, 'html.parser')
        product_name = None
        product_price = None
        currency = None
        # Try common selectors for product name
        name_selectors = [
            '[itemprop="name"]', 'h1.product-title', 'h1[itemprop="name"]', '.product-name', '.item-name', 'meta[property="og:title"]', 'title'
        ]
        for selector in name_selectors:
            if selector == 'title':
                title_tag = soup.find('title')
                if title_tag:
                    product_name = title_tag.get_text(strip=True)
                    break
            else:
                name_element = soup.select_one(selector)
                if name_element:
                    product_name = name_element.get_text(strip=True) if hasattr(name_element, 'get_text') else name_element.get('content', '')
                    break
        # Aggressive selectors for price
        price_selectors = [
            '[itemprop="price"]', '.product-price', '.price', '.product__price', '.item-price',
            'span.price-new', 'div.amount', 'span[data-price]', 'meta[property="product:price:amount"]',
            'span[class*="price"]', 'div[class*="price"]', 'p[class*="price"]', 'span[class*="amount"]',
            'div[class*="amount"]', 'span[class*="cost"]', 'div[class*="cost"]', 'span[class*="value"]',
            'div[class*="value"]', 'span[class*="offer"]', 'div[class*="offer"]',
        ]
        for selector in price_selectors:
            price_element = soup.select_one(selector)
            if price_element:
                price_text = price_element.get_text(strip=True) if hasattr(price_element, 'get_text') else price_element.get('content', '')
                match = re.search(r'([\$₹€£])?\s*([0-9][0-9\.,]*)', price_text)
                if match:
                    currency = match.group(1) if match.group(1) else None
                    product_price = match.group(2)
                    break
        return {'productName': product_name, 'price': product_price, 'currency': currency, 'url': url}

    def _extract_with_openai_multi(self, html_content, product):
        prompt = f'''
You are an AI agent that reads e-commerce product pages in HTML format and extracts structured data.

You will be given the HTML content of a product page. Your task is to:
- Extract all product names/titles and their prices (with currency) found on the page.
- If there are multiple products (e.g., variants/models), extract each with its price and name.
- Provide the original URL (if available) for each product.

**Your ONLY output must be a JSON array.**
**DO NOT include any introductory text, concluding remarks, explanations, markdown code block delimiters (like ```json or ```), or any other extraneous characters. The output must be valid JSON and nothing else.**

The JSON array should contain one or more JSON objects, where each object represents a product found on the page and must have the following structure:
```json
[
  {{
    "productName": "...",  // The full, specific name or title of the product/variant.
    "price": "...",      // The numerical price of the product (as a string, without currency symbols, e.g., "1299.99").
    "currency": "...",   // The currency symbol or ISO 4217 code (e.g., "USD", "€", "₹", "$", "£").
    "url": "..."         // The direct URL to this specific product or variant's page, if clearly identifiable.
  }}
]

If price or product name is not available, use 0 for that field.

HTML source:
{html_content} and product name is {product}
        '''
        print("[OpenAI] Prompt sent to LLM (truncated):", prompt)
        data = []
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,
            )
            content = response.choices[0].message.content
            data = json.loads(content)
        except Exception:
            data = []
        return data

    def clean_html_to_text(self, html_content):
        """
        Cleans HTML content to extract main readable text,
        removing scripts, styles, and excess whitespace.
        """
        if not html_content:
            return ""

        soup = BeautifulSoup(html_content, 'lxml')

        # Remove all script and style elements
        for script_or_style in soup(['script', 'style', 'noscript', 'head', 'footer', 'nav', 'header', 'form', 'img']):
            script_or_style.decompose()

        # Get text from the body (or a more specific main content div if you know it)
        # A common approach is to find the largest text block or specific product details
        # For now, let's get all visible text
        text = soup.get_text(separator=' ', strip=True)

        # Remove extra whitespace (multiple spaces, newlines, tabs)
        text = re.sub(r'\s+', ' ', text).strip()

        # Optional: Further filter common website elements if they clutter the output
        # E.g., legal text, "add to cart" without context, etc.
        # This might require more advanced NLP or heuristic rules based on website commonalities.

        # Example: Limit the text length to avoid token issues, keep it around ~10,000 characters
        # (Roughly 1 character is 0.25 tokens for English, so 10k chars is 2.5k tokens, well within 30k limit)
        max_chars = 10000
        if len(text) > max_chars:
            # Try to cut at a sentence boundary if possible
            truncated_text = text[:max_chars]
            last_period_index = truncated_text.rfind('.')
            if last_period_index != -1 and last_period_index > max_chars * 0.8:  # Ensure it's not too short
                text = truncated_text[:last_period_index + 1]
            else:
                text = truncated_text + "..."  # Just truncate

        return text