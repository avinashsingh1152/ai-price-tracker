import os
import openai
import json
from typing import Dict

class NormalizerAgent:
    def __init__(self, openai_client=None):
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.openai_client = openai_client or openai

    def check_query_specificity(self, query: str) -> dict:
        prompt = f"""
            You are a smart product classification agent.
        
            Your task is to analyze this product query: "{query}"
        
            1. If it is **generic** (e.g. "iPhone", "AirPods", "MacBook"), respond:
            {{
              "status": "generic",
              "base_product": "iPhone",
              "suggested_variants": ["iPhone 14", "iPhone 15 Pro", "iPhone 16 Pro Max"]
            }}
        
            2. If it is **specific** (e.g. "iPhone 16 Pro, 256GB"), respond:
            {{
              "status": "specific",
              "matched_product": "iPhone 16 Pro, 256GB"
            }}
        
            Do NOT explain your answer. Just return the JSON result.
        
            Now evaluate the following product query:
            "{query}"
        """

        output = None
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=512,
                temperature=0.2,
            )
            output = response.choices[0].message.content
            start_index = output.find('{')
            end_index = output.rfind('}') + 1

            # Extract just the JSON part
            raw_json_content = output[start_index:end_index]

            # Convert the JSON string to a Python dictionary
            python_dict = json.loads(raw_json_content)
            return python_dict
        except Exception as e:
            return {"error": "Failed to parse LLM output", "raw": output}
