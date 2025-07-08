class RankerAgent:
    def __init__(self):
        pass

    def rank(self, products: list) -> list:
        try:
            # Step 1: Flatten the incoming list of lists into a single list of dictionaries
            flat_products = []
            for sublist_or_product in products:
                if isinstance(sublist_or_product, list):
                    # If it's a sublist, iterate through its items
                    for item in sublist_or_product:
                        if isinstance(item, dict):
                            flat_products.append(item)
                        else:
                            print(f"Warning: Found non-dictionary item in sublist: {type(item)}")
                elif isinstance(sublist_or_product, dict):
                    # If it's already a dictionary (meaning the list might not be nested or partially flat)
                    flat_products.append(sublist_or_product)
                else:
                    print(f"Warning: Found unexpected type in products list: {type(sublist_or_product)}")

            # Step 2: Process each product in the now flat list
            processed_products = []
            for product_dict in flat_products:  # Now 'product_dict' is guaranteed to be a dictionary
                current_product = product_dict.copy()

                price_val = current_product.get('price')

                if price_val == "0":
                    current_product['price'] = "Sold out"
                    current_product['currency'] = None
                elif price_val is None or str(price_val).strip() == '':
                    current_product['price'] = None
                    current_product['currency'] = None

                processed_products.append(current_product)

            # Step 3: Define the safe_price key for sorting
            def safe_price_for_sorting(product_item):
                price_str = product_item.get('price')
                try:
                    if price_str is None or price_str == "Sold out":
                        return float('inf')
                    return float(price_str)
                except (ValueError, TypeError):
                    return float('inf')

            # Step 4: Sort the processed list
            return sorted(processed_products, key=safe_price_for_sorting)
        except Exception as e:
            return products