import os
import openai

class VerifierAgent:
    def __init__(self, openai_client=None):
        pass

    def verify(self, normalized_info: dict, product_data: dict) -> bool:
        # Generic: check if model is in productName, but handle missing/nulls
        model = (normalized_info.get('model') or '').lower()
        product_name = (product_data.get('productName') or '').lower()
        if not model or not product_name:
            return False
        return model in product_name
