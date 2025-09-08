"""
gpt_service.py

This module extracts structured transaction data from raw emails with GPT and
normalizes the result for downstream creation of `Transaction` records.

The service is responsible for:
- Constructing strict prompts and constraints for transaction extraction
- Cleaning and truncating long email content before LLM calls
- Invoking the OpenAI API and handling failures gracefully
- Parsing JSON or mixed responses and heuristically recovering when needed
- Normalizing categories/subcategories and autocorrecting obvious mislabels
- Providing a simple function to parse a single email object end-to-end
"""

import json
import requests
from django.conf import settings
from datetime import datetime
import logging
import openai

logger = logging.getLogger(__name__)

class GPTEmailParser:
    """GPT email parsing service"""
    
    def __init__(self):
        self.api_key = settings.OPENAI_API_KEY
        self.base_url = "https://api.openai.com/v1/chat/completions"
        
    def parse_email_content(self, subject, sender, body):
        """
        Parse email content using GPT and extract transaction information.
        
        Args:
            subject (str): Email subject
            sender (str): Sender
            body (str): Email body
            
        Returns:
            dict: Parsed result containing transaction information or None
        """
        # Check API KEY
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not configured")
            
        # Build prompt
        prompt = self._build_prompt(subject, sender, body)

        # Request GPT and handle response
        try:
            response = self._call_gpt_api(prompt)
            return self._parse_gpt_response(response)
        except Exception as e:
            logger.error(f"GPT API call failed: {e}")
            return {"has_transaction": False, "error": str(e)}
    
    # I write!!!
    def _build_prompt(self, subject, sender, body):
        return f"""
Please carefully analyze the following email content and extract all actually purchased items. You must extract real product data from the email; do not generate example data.

Email Subject: {subject}
Sender: {sender}
Email Body: {body}

Important: You must extract actual items from the email and MUST NOT generate example data!

For each item output the following fields with exact field names:
item_name, amount, currency, vendor, category, subcategory, item_brand, item_quantity, item_unit_price, transaction_date

Classification rules (must use English and only the predefined values below):
- Dining: Daily meal, Snack, Restaurant, Drink
- Shopping: Clothing, Shoes, Electronics, Household, Cosmetic
- Healthcare: Medicine, Medical
- Transport: Bus, Train, Taxi, Subway, Plane
- Entertainment: Game, Movie, KTV
- Other: User defined

Classification mapping examples:
- Fruits/Vegetables/Staple foods → category: "Dining", subcategory: "Daily meal"
- Beverages/Water/Juice → category: "Dining", subcategory: "Drink"
- Snacks/Candy/Biscuits → category: "Dining", subcategory: "Snack"
- Cleaning supplies/Wet wipes/Disinfectant → category: "Shopping", subcategory: "Household"
- Clothing/Shoes/Accessories → category: "Shopping", subcategory: "Clothing"
- Electronics/Appliances → category: "Shopping", subcategory: "Electronics"
- Others not classifiable → category: "Other", subcategory: "User defined"

Forbidden:
- Do NOT output native category labels from the email (e.g., "Fruit & Vegetables", "Bakery & Patisserie", etc.)
- Every item MUST have category and subcategory fields with the predefined English values
- Only recognize items actually purchased; do not include: "Unavailable Items", "Out of Stock", "Cancelled Items", "Refunded Items", "Substitutions"
- Absolutely do not generate example data; extract real item information from the email

Output format (strictly as below; transactions is an array, one object per item):
{{
  "transactions": [
    {{
      "item_name": "Real product name extracted from the email",
      "amount": Real amount extracted from the email,
      "currency": "Currency extracted from the email",
      "vendor": "Vendor extracted from the email",
      "category": "Category based on the product nature",
      "subcategory": "Subcategory based on the product nature",
      "item_brand": "Brand extracted from the email",
      "item_quantity": Quantity extracted from the email,
      "item_unit_price": Unit price extracted from the email,
      "transaction_date": "Date extracted from the email"
    }}
  ]
}}
"""
    
    
    
    # AI write!!!
    def _clean_email_content(self, content):
        """Clean email content by removing HTML tags and special characters"""
        import re
        
        if not content:
            return ""
        
        # try to preserve line breaks: replace block-level tags with line breaks, then remove other tags
        content = re.sub(r'(?i)</?(br|p|div|li|tr|td|th|h[1-6])[^>]*>', '\n', content)
        content = re.sub(r'<[^>]+>', '', content)
        # standardize line breaks, avoid collapsing all to single space
        content = content.replace('\r\n', '\n').replace('\r', '\n')
        # collapse consecutive spaces, but preserve line breaks
        content = re.sub(r'[ \t\u00A0]{2,}', ' ', content)
        content = re.sub(r'\n{3,}', '\n\n', content)
        
        # remove special characters (preserve basic punctuation)
        content = re.sub(r'[^\w\s\-.,!?@#$%&*()+=:;"\'<>/\\|]', '', content)
        
        # remove excessive repeated characters (more than 10 identical characters)
        content = re.sub(r'(.)\1{10,}', r'\1', content)
        
        # remove excessive repeated spaces
        content = re.sub(r' {2,}', ' ', content)
        
        return content.strip()
    
    # I write!!!
    def _call_gpt_api(self, prompt):
        """Call GPT API"""
        try:
            import logging
            logger = logging.getLogger(__name__)
            
            # Preprocess email content: remove special characters and HTML tags
            cleaned_prompt = self._clean_email_content(prompt)
            
            # If content is too long, truncate while trying to preserve structure
            if len(cleaned_prompt) > 6000:
                logger.warning(f"Email content too long ({len(cleaned_prompt)} chars), truncating")
                cleaned_prompt = cleaned_prompt[:6000] + "\n\n[Content truncated...]"
            
            # Use requests to directly call the OpenAI API
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": "gpt-3.5-turbo",
                "messages": [
                    {"role": "system", "content": "You are an assistant that extracts transaction information from emails. You MUST extract real purchased items from the email and must not fabricate data. Classify items according to the predefined taxonomy. Each item must include item_name, amount, currency, vendor, category, subcategory, item_brand, item_quantity, item_unit_price, transaction_date. Output a JSON object with a transactions array. If the email contains multiple items separated by pipes or newlines (for example, a list or table including Quantity and Price), parse them one by one and output each item as an independent object in transactions. Items related to beauty/skin care/hair care (such as shampoo, conditioner, toner, serum, cleanser, moisturizer, skincare, cosmetic, makeup, salicylic acid) should be classified as Shopping/Cosmetic."},
                    {"role": "user", "content": cleaned_prompt}
                ],
                "response_format": {"type": "json_object"},
                "temperature": 0.0,
                "max_tokens": 2000
            }
            
            response = requests.post(self.base_url, headers=headers, json=data, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            gpt_response = result['choices'][0]['message']['content'].strip()
            
            # Log raw GPT response
            logger.info(f"Raw GPT response: {gpt_response}")
            
            return gpt_response
            
        except Exception as e:
            logger.error(f"GPT API call failed: {e}")
            return None
    
    def _parse_gpt_response(self, gpt_response):
        """Parse GPT response"""
        try:
            if not gpt_response:
                return {"has_transaction": False, "error": "Empty response"}
            
            # If gpt_response is a string, try parsing JSON directly
            if isinstance(gpt_response, str):
                try:
                    # First try to parse as a single JSON object
                    parsed_content = json.loads(gpt_response)
                    return self._convert_any_format_to_standard(parsed_content)
                except json.JSONDecodeError:
                    # If failed, try parsing multiple standalone JSON objects
                    try:
                        return self._parse_multiple_json_objects(gpt_response)
                    except Exception as e:
                        logger.error(f"Failed to parse multiple JSON objects: {e}")
                        return {"has_transaction": False, "error": "Invalid JSON format"}
            
            # If gpt_response is a dict
            elif isinstance(gpt_response, dict):
                return self._convert_any_format_to_standard(gpt_response)
            
            return {"has_transaction": False, "error": "Invalid response format"}
            
        except Exception as e:
            logger.error(f"Parsing failed, try heuristic parsing: {e}")
            return self._heuristic_parse(gpt_response)
    

    
    def _correct_category(self, wrong_category, item_name):
        """自动修正错误的分类"""
        item_name_lower = item_name.lower()
        
        # 食物相关分类修正
        food_keywords = ['fruit', 'vegetable', 'watermelon', 'bread', 'cake', 'egg', 'meat', 'beef', 'chicken', 'fish', 'milk', 'cheese', 'sauce', 'soy', 'sweet', 'biscuit', 'chocolate', 'water', 'drink', 'juice', 'coffee', 'tea']
        if any(keyword in item_name_lower for keyword in food_keywords):
            return "Dining"
        
        # Household cleaning-related correction
        cleaning_keywords = ['wipe', 'antiseptic', 'cleaning', 'kitchen roll', 'tissue', 'bathroom', 'detergent']
        if any(keyword in item_name_lower for keyword in cleaning_keywords):
            return "Shopping"
        
        # Other corrections
        if 'fruit' in wrong_category.lower() or 'vegetable' in wrong_category.lower():
            return "Dining"
        elif 'bakery' in wrong_category.lower() or 'patisserie' in wrong_category.lower():
            return "Dining"
        elif 'dairy' in wrong_category.lower() or 'delicatessen' in wrong_category.lower():
            return "Dining"
        elif 'meat' in wrong_category.lower() or 'fish' in wrong_category.lower() or 'poultry' in wrong_category.lower():
            return "Dining"
        elif 'household' in wrong_category.lower() or 'petcare' in wrong_category.lower():
            return "Shopping"
        elif 'cupboard' in wrong_category.lower() or 'store' in wrong_category.lower():
            return "Dining"  # mostly food
        
        return None
    
    def _infer_subcategory(self, category, item_name):
        """Infer subcategory based on category and item name"""
        item_name_lower = item_name.lower()
        
        if category == "Dining":
            # Staple/meal related
            meal_keywords = ['watermelon', 'bread', 'cake', 'egg', 'meat', 'beef', 'chicken', 'fish', 'milk', 'cheese', 'sauce', 'soy']
            if any(keyword in item_name_lower for keyword in meal_keywords):
                return "Daily meal"
            
            # Drink related
            drink_keywords = ['water', 'juice', 'coffee', 'tea', 'mineral']
            if any(keyword in item_name_lower for keyword in drink_keywords):
                return "Drink"
            
            # Snack related
            snack_keywords = ['sweet', 'biscuit', 'chocolate', 'nibble', 'snack']
            if any(keyword in item_name_lower for keyword in snack_keywords):
                return "Snack"
            
            return "Daily meal"  # default
        
        elif category == "Shopping":
            # Cosmetics/Skincare
            cosmetic_keywords = ['cosmetic', 'makeup', 'skincare', 'skin care', 'toner', 'serum', 'cleanser', 'moisturizer', 'lotion', 'cream', 'mask', 'shampoo', 'conditioner', 'hair', 'gel', 'salicylic', 'acid', 'retinol', 'vitamin c', 'hyaluronic']
            if any(keyword in item_name_lower for keyword in cosmetic_keywords):
                return "Cosmetic"

            # Household items
            household_keywords = ['wipe', 'antiseptic', 'cleaning', 'kitchen roll', 'tissue', 'bathroom', 'detergent']
            if any(keyword in item_name_lower for keyword in household_keywords):
                return "Household"
            
            # Clothing/Shoes
            clothing_keywords = ['shirt', 'pants', 'dress', 'shoes', 'boots', 'sneakers', 'hat', 'cap', 'yeezy', 
                               'sweatshirt', 'jacket', 'coat', 'sweater', 'hoodie', 't-shirt', 'tshirt', 'jeans', 
                               'trousers', 'shorts', 'skirt', 'blouse', 'top', 'jumper', 'cardigan', 'vest', 
                               'polo', 'tnf', 'north face', 'adidas', 'nike', 'puma', 'reebok', 'converse', 
                               'vans', 'timberland', 'dr martens', 'clarks', 'h&m', 'zara', 'uniqlo', 'gap']
            if any(keyword in item_name_lower for keyword in clothing_keywords):
                return "Clothing"
            
            return "Household"  # default
        
        return "User defined"  # default
    
    def _correct_subcategory(self, category, wrong_subcategory, item_name):
        """Automatically correct invalid subcategory"""
        item_name_lower = item_name.lower()
        
        if category == "Dining":
            # Staple/meal related
            meal_keywords = ['watermelon', 'bread', 'cake', 'egg', 'meat', 'beef', 'chicken', 'fish', 'milk', 'cheese', 'sauce', 'soy']
            if any(keyword in item_name_lower for keyword in meal_keywords):
                return "Daily meal"
            
            # Drink related
            drink_keywords = ['water', 'juice', 'coffee', 'tea', 'mineral']
            if any(keyword in item_name_lower for keyword in drink_keywords):
                return "Drink"
            
            # Snack related
            snack_keywords = ['sweet', 'biscuit', 'chocolate', 'nibble', 'snack']
            if any(keyword in item_name_lower for keyword in snack_keywords):
                return "Snack"
            
            return "Daily meal"  # default
        
        elif category == "Shopping":
            # Cosmetics/Skincare
            cosmetic_keywords = ['cosmetic', 'makeup', 'skincare', 'skin care', 'toner', 'serum', 'cleanser', 'moisturizer', 'lotion', 'cream', 'mask', 'shampoo', 'conditioner', 'hair', 'gel', 'salicylic', 'acid', 'retinol', 'vitamin c', 'hyaluronic']
            if any(keyword in item_name_lower for keyword in cosmetic_keywords):
                return "Cosmetic"

            # Household items
            household_keywords = ['wipe', 'antiseptic', 'cleaning', 'kitchen roll', 'tissue', 'bathroom', 'detergent']
            if any(keyword in item_name_lower for keyword in household_keywords):
                return "Household"
            
            # Clothing/Shoes
            clothing_keywords = ['shirt', 'pants', 'dress', 'shoes', 'boots', 'sneakers', 'hat', 'cap', 
                               'sweatshirt', 'jacket', 'coat', 'sweater', 'hoodie', 't-shirt', 'tshirt', 'jeans', 
                               'trousers', 'shorts', 'skirt', 'blouse', 'top', 'jumper', 'cardigan', 'vest', 
                               'polo', 'tnf', 'north face', 'adidas', 'nike', 'puma', 'reebok', 'converse', 
                               'vans', 'timberland', 'dr martens', 'clarks', 'h&m', 'zara', 'uniqlo', 'gap']
            if any(keyword in item_name_lower for keyword in clothing_keywords):
                return "Clothing"
            
            return "Household"  # default
        
        return None
    
    def _convert_transaction_format(self, trans):
        """转换单个交易记录格式"""
        try:
            import re
            
            # 处理商品名称 - 支持多种字段名
            item_name = (trans.get('item_name') or trans.get('item') or 
                        trans.get('product_name') or trans.get('product') or 
                        trans.get('name') or trans.get('product') or 'Unknown Item')
            
            # Handle amount and currency extraction
            amount_str = (trans.get('amount') or trans.get('price') or 
                         trans.get('price_per_item') or trans.get('total_price') or 
                         trans.get('price_per_item') or '0')
            
            # If the amount is a string like "38.00 GBP", extract number and currency
            if isinstance(amount_str, str):
                # Match number and currency pattern
                match = re.search(r'(\d+\.?\d*)\s*([A-Z]{3})', amount_str)
                if match:
                    amount = float(match.group(1))
                    currency = match.group(2)
                else:
                    # Try to extract numeric part only
                    num_match = re.search(r'(\d+\.?\d*)', amount_str)
                    if num_match:
                        amount = float(num_match.group(1))
                        currency = 'GBP'  # default currency
                    else:
                        amount = 0
                        currency = 'GBP'
            else:
                amount = float(amount_str) if amount_str else 0
                currency = trans.get('currency', 'GBP')
            
            # Handle quantity - ensure numeric
            quantity = trans.get('item_quantity') or trans.get('quantity') or trans.get('quantity') or 1
            if isinstance(quantity, str):
                # If string, try extracting digits
                num_match = re.search(r'(\d+)', quantity)
                if num_match:
                    item_quantity = int(num_match.group(1))
                else:
                    item_quantity = 1
            else:
                item_quantity = int(quantity) if quantity else 1
            
            # Other fields
            category = trans.get('category', 'Shopping')
            subcategory = trans.get('subcategory', 'Clothing')
            vendor = trans.get('vendor', 'Unknown')
            item_brand = trans.get('item_brand') or trans.get('brand') or ''
            item_unit_price = trans.get('item_unit_price') or trans.get('unit_price') or amount
            transaction_date = trans.get('transaction_date') or datetime.now().strftime('%Y-%m-%d')
            note = trans.get('note', '')
            
            # If category includes subcategory info, split it
            if ' - ' in category:
                parts = category.split(' - ', 1)
                category = parts[0]
                subcategory = parts[1]
            
            # Validate category
            allowed_categories = ["Dining", "Shopping", "Healthcare", "Transport", "Entertainment", "Other"]
            allowed_subcategories = ["Daily meal", "Snack", "Restaurant", "Drink",
                                   "Clothing", "Shoes", "Electronics", "Household", "Cosmetic",
                                   "Medicine", "Medical", "Bus", "Train", "Taxi", "Subway", "Plane",
                                   "Game", "Movie", "KTV", "User defined"]
            
            if category not in allowed_categories:
                logger.error(f"Invalid main category: {category}, item: {item_name}")
            
            if subcategory not in allowed_subcategories:
                logger.error(f"Invalid subcategory: {subcategory}, item: {item_name}")
            
            # If subcategory is missing/invalid, infer from category and item name
            if not subcategory or subcategory == 'User defined' or subcategory not in allowed_subcategories:
                subcategory = self._infer_subcategory(category, item_name)
            
            return {
                'amount': amount,
                'currency': currency,
                'vendor': vendor,
                'transaction_date': transaction_date,
                'category': category,
                'subcategory': subcategory,
                'item_name': item_name,
                'item_brand': item_brand,
                'item_quantity': item_quantity,
                'item_unit_price': item_unit_price,
                'item_description': '',
                'note': note
            }
        except Exception as e:
            logger.error(f"Failed to convert transaction format: {e}")
            return None
    
    # Mostly AI write
    def _heuristic_parse(self, response_text):
        """Fallback parsing when standard parsing fails"""
        import re
        
        try:
            logger.info("Starting heuristic parsing...")
            
            # Define key patterns
            patterns = {
                'item_name': r'"item_name"\s*:\s*"([^"]+)"',
                'amount': r'"amount"\s*:\s*(\d+\.?\d*)',
                'currency': r'"currency"\s*:\s*"([^"]+)"',
                'vendor': r'"vendor"\s*:\s*"([^"]+)"',
                'category': r'"category"\s*:\s*"([^"]+)"',
                'subcategory': r'"subcategory"\s*:\s*"([^"]+)"',
                'item_brand': r'"item_brand"\s*:\s*"([^"]+)"',
                'item_quantity': r'"item_quantity"\s*:\s*(\d+)',
                'item_unit_price': r'"item_unit_price"\s*:\s*(\d+\.?\d*)',
                'transaction_date': r'"transaction_date"\s*:\s*"([^"]+)"'
            }
            
            # Find all possible transaction data
            transactions = []
            
            # Find JSON objects using regex
            json_pattern = r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}'
            json_objects = re.findall(json_pattern, response_text)
            
            for json_str in json_objects:
                try:
                    # Try to parse JSON
                    item = json.loads(json_str)
                    if 'item_name' in item and 'amount' in item:
                        converted = self._convert_transaction_format(item)
                        if converted:
                            transactions.append(converted)
                except json.JSONDecodeError:
                    # If JSON parsing fails, try extracting with regex
                    extracted_item = {}
                    
                    for field, pattern in patterns.items():
                        match = re.search(pattern, json_str)
                        if match:
                            if field in ['amount', 'item_quantity', 'item_unit_price']:
                                extracted_item[field] = float(match.group(1))
                            else:
                                extracted_item[field] = match.group(1)
                    
                    if 'item_name' in extracted_item and 'amount' in extracted_item:
                        converted = self._convert_transaction_format(extracted_item)
                        if converted:
                            transactions.append(converted)
            
            if transactions:
                logger.info(f"Heuristic parsing succeeded, found {len(transactions)} transactions")
                return {
                    'has_transaction': True,
                    'transactions': transactions
                }
            else:
                logger.warning("Heuristic parsing found no valid transactions")
                return {"has_transaction": False, "error": "No valid transactions found in heuristic parsing"}
                
        except Exception as e:
            logger.error(f"Heuristic parsing failed: {e}")
            return {"has_transaction": False, "error": f"Heuristic parsing failed: {e}"}
    

    
    def _parse_multiple_json_objects(self, gpt_response):
        """Parse multiple standalone JSON objects"""
        import re
        
        try:
            # Use regex to match JSON objects
            json_pattern = r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}'
            json_objects = re.findall(json_pattern, gpt_response)
            
            if not json_objects:
                return {"has_transaction": False, "error": "No JSON objects found"}
            
            transactions = []
            for json_str in json_objects:
                try:
                    # Parse each JSON object
                    item = json.loads(json_str)
                    converted = self._convert_transaction_format(item)
                    if converted:
                        transactions.append(converted)
                except json.JSONDecodeError as e:
                    logger.warning(f"Failed to parse JSON object: {e}, JSON: {json_str}")
                    continue
            
            if transactions:
                return {
                    'has_transaction': True,
                    'transactions': transactions
                }
            else:
                return {"has_transaction": False, "error": "No valid transactions found"}
                
        except Exception as e:
            logger.error(f"Failed to parse multiple JSON objects: {e}")
            return {"has_transaction": False, "error": f"Multiple JSON parsing failed: {e}"}
    
    def _convert_any_format_to_standard(self, data):
        """Convert any format of data into the standard format"""
        try:
            transactions = []
            
            # Define allowed categories
            allowed_categories = ["Dining", "Shopping", "Healthcare", "Transport", "Entertainment", "Other"]
            allowed_subcategories = {
                "Dining": ["Daily meal", "Snack", "Restaurant", "Drink"],
                "Shopping": ["Clothing", "Electronics", "Household", "Cosmetic"],
                "Healthcare": ["Medicine", "Medical"],
                "Transport": ["Bus", "Train", "Taxi", "Subway"],
                "Entertainment": ["Game", "Movie", "KTV"],
                "Other": ["User defined"]
            }
            
            # Handle different data structures
            if 'transactions' in data:
                items = data['transactions']
                # Check nested structure (transactions contains items arrays)
                if items and isinstance(items[0], dict) and 'items' in items[0]:
                    # Handle nested structure: transactions[0].items
                    all_items = []
                    for transaction in items:
                        if 'items' in transaction:
                            all_items.extend(transaction['items'])
                    items = all_items
            elif 'transaction' in data:  # Add support for single item field
                items = data['transaction']
            elif 'items' in data:
                items = data['items']
            elif 'products' in data:
                items = data['products']
            elif 'purchased_items' in data:
                items = data['purchased_items']
            # Handle nested structures
            elif 'order_details' in data and 'items' in data['order_details']:
                items = data['order_details']['items']
            elif 'order_details' in data and 'products' in data['order_details']:
                items = data['order_details']['products']
            else:
                return {"has_transaction": False, "error": "No transaction data found"}
            
            for item in items:
                converted = self._convert_transaction_format(item)
                if converted:
                    # Validate categories
                    category = converted.get('category', '')
                    subcategory = converted.get('subcategory', '')
                    
                    if category not in allowed_categories:
                        logger.error(f"Invalid category: {category}, item: {converted.get('item_name')}")
                        # Try to auto-correct category
                        corrected_category = self._correct_category(category, converted.get('item_name'))
                        if corrected_category:
                            converted['category'] = corrected_category
                            logger.info(f"Auto-corrected category: {category} -> {corrected_category}")
                        else:
                            logger.warning(f"Cannot correct category: {category}, skipping this item")
                            continue
                    
                    if category in allowed_subcategories and subcategory not in allowed_subcategories[category]:
                        logger.error(f"Invalid subcategory: {subcategory}, category: {category}, item: {converted.get('item_name')}")
                        # Try to auto-correct subcategory
                        corrected_subcategory = self._correct_subcategory(category, subcategory, converted.get('item_name'))
                        if corrected_subcategory:
                            converted['subcategory'] = corrected_subcategory
                            logger.info(f"Auto-corrected subcategory: {subcategory} -> {corrected_subcategory}")
                        else:
                            logger.warning(f"Cannot correct subcategory: {subcategory}, skipping this item")
                            continue
                    
                    transactions.append(converted)
            
            if transactions:
                return {
                    'has_transaction': True,
                    'transactions': transactions
                }
            else:
                return {"has_transaction": False, "error": "No valid transactions found"}
                
        except Exception as e:
            logger.error(f"Format conversion failed: {e}")
            return {"has_transaction": False, "error": f"Format conversion failed: {e}"}
    


def parse_single_email(email_obj):
    """Parse a single email"""
    try:
        # ！！(AI write) Observation/Debug Log: Before actually calling GPT for parsing, record the key metadata of this email.
        logger.info(f"Start parsing email ID: {email_obj.id}, subject: {email_obj.subject}")
        logger.info(f"Email sender: {email_obj.sender}")
        logger.info(f"Email body length: {len(email_obj.body) if email_obj.body else 0} characters")
        logger.info(f"First 500 chars of email body: {email_obj.body[:500] if email_obj.body else 'None'}...")
        # I write!!!
        parser = GPTEmailParser()
        result = parser.parse_email_content(email_obj.subject, email_obj.sender, email_obj.body)
        
        logger.info(f"Email parsing result: {result}")
        
        return result
        
    except Exception as e:
        logger.error(f"Failed to parse email (email ID: {email_obj.id}): {e}")
        return {
            'has_transaction': False,
            'transactions': [],
            'error': str(e)
        } 