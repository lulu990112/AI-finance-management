import json
import requests
from django.conf import settings
from datetime import datetime
import logging
import openai

logger = logging.getLogger(__name__)

class GPTEmailParser:
    """GPT邮件解析服务"""
    
    def __init__(self):
        self.api_key = settings.OPENAI_API_KEY
        self.base_url = "https://api.openai.com/v1/chat/completions"
        
    def parse_email_content(self, subject, sender, body):
        """
        使用GPT解析邮件内容，提取交易信息
        
        Args:
            subject (str): 邮件主题
            sender (str): 发件人
            body (str): 邮件正文
            
        Returns:
            dict: 解析结果，包含交易信息或None
        """
        # Check API KEY
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not configured")
            
        # 构建 prompt
        prompt = self._build_prompt(subject, sender, body)
        # 请求 GPT，并处理响应
        try:
            response = self._call_gpt_api(prompt)
            return self._parse_gpt_response(response)
        except Exception as e:
            logger.error(f"GPT API调用失败: {e}")
            return {"has_transaction": False, "error": str(e)}
    
    def _build_prompt(self, subject, sender, body):
        return f"""
请仔细分析以下邮件内容，提取所有实际购买的商品信息。必须从邮件中提取真实的商品数据，不要生成示例数据。

邮件主题：{subject}
发件人：{sender}
邮件内容：{body}

**重要：必须从邮件内容中提取实际商品，不要生成示例数据！**

每个商品输出如下字段，字段名必须完全一致：
item_name, amount, currency, vendor, category, subcategory, item_brand, item_quantity, item_unit_price, transaction_date

**分类规则（必须使用英文，且只能用下列预设值）：**
- Dining: Daily meal, Snack, Restaurant, Drink
- Shopping: Clothing, Shoes, Electronics, Household, Cosmetic
- Healthcare: Medicine, Medical
- Transport: Bus, Train, Taxi, Subway, Plane
- Entertainment: Game, Movie, KTV
- Other: User defined

**分类映射示例：**
- 水果/蔬菜/主食 → category: "Dining", subcategory: "Daily meal"
- 饮料/水/果汁 → category: "Dining", subcategory: "Drink"
- 零食/糖果/饼干 → category: "Dining", subcategory: "Snack"
- 清洁用品/湿巾/消毒液 → category: "Shopping", subcategory: "Household"
- 服装/鞋子/配饰 → category: "Shopping", subcategory: "Clothing"
- 电子产品/电器 → category: "Shopping", subcategory: "Electronics"
- 其他无法分类 → category: "Other", subcategory: "User defined"

**禁止：**
- 禁止输出邮件中的原生分类标签（如"Fruit & Vegetables"、"Bakery & Patisserie"等）
- 每个商品都必须有category和subcategory字段，且必须用英文预设值
- 只识别实际购买的商品，不要识别以下内容："Unavailable Items"、"Out of Stock"、"Cancelled Items"、"Refunded Items"、"Substitutions"
- 绝对不要生成示例数据，必须从邮件中提取真实商品信息

**输出格式（严格如下，transactions为数组，每个商品一个对象）：**
{{
  "transactions": [
    {{
      "item_name": "从邮件中提取的真实商品名称",
      "amount": 从邮件中提取的真实金额,
      "currency": "从邮件中提取的货币",
      "vendor": "从邮件中提取的供应商",
      "category": "根据商品属性分类",
      "subcategory": "根据商品属性分类",
      "item_brand": "从邮件中提取的品牌",
      "item_quantity": 从邮件中提取的数量,
      "item_unit_price": 从邮件中提取的单价,
      "transaction_date": "从邮件中提取的日期"
    }}
  ]
}}
"""
    
    def _get_schema(self):
        """获取JSON Schema定义"""
        return {
            "type": "object",
            "properties": {
                "has_transaction": {
                    "type": "boolean",
                    "description": "是否包含交易信息"
                },
                "transactions": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "amount": {
                                "type": "number",
                                "description": "交易金额（单价 × 数量）"
                            },
                            "currency": {
                                "type": "string",
                                "description": "货币代码（如USD、CNY、GBP）"
                            },
                            "vendor": {
                                "type": "string",
                                "description": "商家名称"
                            },
                            "transaction_date": {
                                "type": "string",
                                "description": "交易日期（YYYY-MM-DD格式）"
                            },
                            "category": {
                                "type": "string",
                                "enum": ["Dining", "Shopping", "Healthcare", "Transport", "Entertainment", "Other"],
                                "description": "主分类"
                            },
                            "subcategory": {
                                "type": "string",
                                "description": "子分类，必须从预设选项中选择"
                            },
                            "item_name": {
                                "type": "string",
                                "description": "商品名称"
                            },
                            "item_brand": {
                                "type": "string",
                                "description": "品牌"
                            },
                            "item_quantity": {
                                "type": "number",
                                "description": "数量"
                            },
                            "item_unit_price": {
                                "type": "number",
                                "description": "单价"
                            },
                            "item_description": {
                                "type": "string",
                                "description": "商品描述"
                            },
                            "note": {
                                "type": "string",
                                "description": "备注信息"
                            }
                        },
                        "required": ["amount", "currency", "vendor", "category", "subcategory", "item_name", "item_quantity", "item_unit_price"]
                    }
                }
            },
            "required": ["has_transaction"]
        }
    
    def _clean_email_content(self, content):
        """清理邮件内容，移除HTML标签和特殊字符"""
        import re
        
        if not content:
            return ""
        
        # 移除HTML标签
        content = re.sub(r'<[^>]+>', '', content)
        
        # 移除多余的空格和换行
        content = re.sub(r'\s+', ' ', content)
        
        # 移除特殊字符（保留基本的标点符号）
        content = re.sub(r'[^\w\s\-.,!?@#$%&*()+=:;"\'<>/\\|]', '', content)
        
        # 移除过多的重复字符（超过10个相同字符）
        content = re.sub(r'(.)\1{10,}', r'\1', content)
        
        # 移除过多的重复空格
        content = re.sub(r' {2,}', ' ', content)
        
        return content.strip()
    
    def _call_gpt_api(self, prompt):
        """调用GPT API"""
        try:
            import logging
            logger = logging.getLogger(__name__)
            
            # 预处理邮件内容，移除特殊字符和HTML标签
            cleaned_prompt = self._clean_email_content(prompt)
            
            # 记录发送给GPT的内容
            logger.info(f"发送给GPT的内容长度: {len(cleaned_prompt)} 字符")
            logger.info(f"发送给GPT的内容前1000字符: {cleaned_prompt[:1000]}...")
            
            # 如果内容过长，进行截断，但保留更多内容
            if len(cleaned_prompt) > 6000:
                logger.warning(f"邮件内容过长 ({len(cleaned_prompt)} 字符)，进行截断")
                cleaned_prompt = cleaned_prompt[:6000] + "\n\n[内容已截断...]"
            
            # 使用requests直接调用OpenAI API
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": "gpt-3.5-turbo",
                "messages": [
                    {"role": "system", "content": "你是邮件交易信息提取助手。必须从邮件内容中提取真实的商品交易信息，不要生成示例数据。按预设分类体系分类。每个商品必须包含item_name、amount、currency、vendor、category、subcategory、item_brand、item_quantity、item_unit_price、transaction_date字段。输出JSON格式的transactions数组。"},
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
            
            # 记录GPT的原始响应
            logger.info(f"GPT原始响应: {gpt_response}")
            
            return gpt_response
            
        except Exception as e:
            logger.error(f"GPT API调用失败: {e}")
            return None
    
    def _parse_gpt_response(self, gpt_response):
        """解析GPT响应"""
        try:
            if not gpt_response:
                return {"has_transaction": False, "error": "Empty response"}
            
            # 如果gpt_response是字符串，尝试直接解析JSON
            if isinstance(gpt_response, str):
                try:
                    # 首先尝试解析为单个JSON对象
                    parsed_content = json.loads(gpt_response)
                    return self._convert_any_format_to_standard(parsed_content)
                except json.JSONDecodeError:
                    # 如果失败，尝试解析多个独立的JSON对象
                    try:
                        return self._parse_multiple_json_objects(gpt_response)
                    except Exception as e:
                        logger.error(f"解析多个JSON对象失败: {e}")
                        return {"has_transaction": False, "error": "Invalid JSON format"}
            
            # 如果gpt_response是字典
            elif isinstance(gpt_response, dict):
                return self._convert_any_format_to_standard(gpt_response)
            
            return {"has_transaction": False, "error": "Invalid response format"}
            
        except Exception as e:
            logger.error(f"解析失败，尝试启发式解析: {e}")
            return self._heuristic_parse(gpt_response)
    

    
    def _correct_category(self, wrong_category, item_name):
        """自动修正错误的分类"""
        item_name_lower = item_name.lower()
        
        # 食物相关分类修正
        food_keywords = ['fruit', 'vegetable', 'watermelon', 'bread', 'cake', 'egg', 'meat', 'beef', 'chicken', 'fish', 'milk', 'cheese', 'sauce', 'soy', 'sweet', 'biscuit', 'chocolate', 'water', 'drink', 'juice', 'coffee', 'tea']
        if any(keyword in item_name_lower for keyword in food_keywords):
            return "Dining"
        
        # 清洁用品分类修正
        cleaning_keywords = ['wipe', 'antiseptic', 'cleaning', 'kitchen roll', 'tissue', 'bathroom', 'detergent']
        if any(keyword in item_name_lower for keyword in cleaning_keywords):
            return "Shopping"
        
        # 其他分类修正
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
            return "Dining"  # 大部分是食物
        
        return None
    
    def _infer_subcategory(self, category, item_name):
        """根据category和商品名称推断subcategory"""
        item_name_lower = item_name.lower()
        
        if category == "Dining":
            # 主食相关
            meal_keywords = ['watermelon', 'bread', 'cake', 'egg', 'meat', 'beef', 'chicken', 'fish', 'milk', 'cheese', 'sauce', 'soy']
            if any(keyword in item_name_lower for keyword in meal_keywords):
                return "Daily meal"
            
            # 饮料相关
            drink_keywords = ['water', 'juice', 'coffee', 'tea', 'mineral']
            if any(keyword in item_name_lower for keyword in drink_keywords):
                return "Drink"
            
            # 零食相关
            snack_keywords = ['sweet', 'biscuit', 'chocolate', 'nibble', 'snack']
            if any(keyword in item_name_lower for keyword in snack_keywords):
                return "Snack"
            
            return "Daily meal"  # 默认
        
        elif category == "Shopping":
            # 家居用品
            household_keywords = ['wipe', 'antiseptic', 'cleaning', 'kitchen roll', 'tissue', 'bathroom', 'detergent']
            if any(keyword in item_name_lower for keyword in household_keywords):
                return "Household"
            
            # 服装/鞋子
            clothing_keywords = ['shirt', 'pants', 'dress', 'shoes', 'boots', 'sneakers', 'hat', 'cap', 'yeezy', 
                               'sweatshirt', 'jacket', 'coat', 'sweater', 'hoodie', 't-shirt', 'tshirt', 'jeans', 
                               'trousers', 'shorts', 'skirt', 'blouse', 'top', 'jumper', 'cardigan', 'vest', 
                               'polo', 'tnf', 'north face', 'adidas', 'nike', 'puma', 'reebok', 'converse', 
                               'vans', 'timberland', 'dr martens', 'clarks', 'h&m', 'zara', 'uniqlo', 'gap']
            if any(keyword in item_name_lower for keyword in clothing_keywords):
                return "Clothing"
            
            return "Household"  # 默认
        
        return "User defined"  # 默认
    
    def _correct_subcategory(self, category, wrong_subcategory, item_name):
        """自动修正错误的子分类"""
        item_name_lower = item_name.lower()
        
        if category == "Dining":
            # 主食相关
            meal_keywords = ['watermelon', 'bread', 'cake', 'egg', 'meat', 'beef', 'chicken', 'fish', 'milk', 'cheese', 'sauce', 'soy']
            if any(keyword in item_name_lower for keyword in meal_keywords):
                return "Daily meal"
            
            # 饮料相关
            drink_keywords = ['water', 'juice', 'coffee', 'tea', 'mineral']
            if any(keyword in item_name_lower for keyword in drink_keywords):
                return "Drink"
            
            # 零食相关
            snack_keywords = ['sweet', 'biscuit', 'chocolate', 'nibble', 'snack']
            if any(keyword in item_name_lower for keyword in snack_keywords):
                return "Snack"
            
            return "Daily meal"  # 默认
        
        elif category == "Shopping":
            # 家居用品
            household_keywords = ['wipe', 'antiseptic', 'cleaning', 'kitchen roll', 'tissue', 'bathroom', 'detergent']
            if any(keyword in item_name_lower for keyword in household_keywords):
                return "Household"
            
            # 服装/鞋子
            clothing_keywords = ['shirt', 'pants', 'dress', 'shoes', 'boots', 'sneakers', 'hat', 'cap', 
                               'sweatshirt', 'jacket', 'coat', 'sweater', 'hoodie', 't-shirt', 'tshirt', 'jeans', 
                               'trousers', 'shorts', 'skirt', 'blouse', 'top', 'jumper', 'cardigan', 'vest', 
                               'polo', 'tnf', 'north face', 'adidas', 'nike', 'puma', 'reebok', 'converse', 
                               'vans', 'timberland', 'dr martens', 'clarks', 'h&m', 'zara', 'uniqlo', 'gap']
            if any(keyword in item_name_lower for keyword in clothing_keywords):
                return "Clothing"
            
            return "Household"  # 默认
        
        return None
    
    def _convert_transaction_format(self, trans):
        """转换单个交易记录格式"""
        try:
            import re
            
            # 处理商品名称 - 支持多种字段名
            item_name = (trans.get('item_name') or trans.get('item') or 
                        trans.get('product_name') or trans.get('product') or 
                        trans.get('name') or trans.get('product') or 'Unknown Item')
            
            # 处理金额和货币分离
            amount_str = (trans.get('amount') or trans.get('price') or 
                         trans.get('price_per_item') or trans.get('total_price') or 
                         trans.get('price_per_item') or '0')
            
            # 如果金额是字符串格式如 "38.00 GBP"，提取数字和货币
            if isinstance(amount_str, str):
                # 匹配数字和货币格式
                match = re.search(r'(\d+\.?\d*)\s*([A-Z]{3})', amount_str)
                if match:
                    amount = float(match.group(1))
                    currency = match.group(2)
                else:
                    # 尝试提取纯数字
                    num_match = re.search(r'(\d+\.?\d*)', amount_str)
                    if num_match:
                        amount = float(num_match.group(1))
                        currency = 'GBP'  # 默认货币
                    else:
                        amount = 0
                        currency = 'GBP'
            else:
                amount = float(amount_str) if amount_str else 0
                currency = trans.get('currency', 'GBP')
            
            # 处理数量 - 确保是数字
            quantity = trans.get('item_quantity') or trans.get('quantity') or trans.get('quantity') or 1
            if isinstance(quantity, str):
                # 如果是字符串，尝试提取数字
                num_match = re.search(r'(\d+)', quantity)
                if num_match:
                    item_quantity = int(num_match.group(1))
                else:
                    item_quantity = 1
            else:
                item_quantity = int(quantity) if quantity else 1
            
            # 处理其他字段
            category = trans.get('category', 'Shopping')
            subcategory = trans.get('subcategory', 'Clothing')
            vendor = trans.get('vendor', 'Unknown')
            item_brand = trans.get('item_brand') or trans.get('brand') or ''
            item_unit_price = trans.get('item_unit_price') or trans.get('unit_price') or amount
            transaction_date = trans.get('transaction_date') or datetime.now().strftime('%Y-%m-%d')
            note = trans.get('note', '')
            
            # 如果category包含子分类信息，提取出来
            if ' - ' in category:
                parts = category.split(' - ', 1)
                category = parts[0]
                subcategory = parts[1]
            
            # 验证分类
            allowed_categories = ["Dining", "Shopping", "Healthcare", "Transport", "Entertainment", "Other"]
            allowed_subcategories = ["Daily meal", "Snack", "Restaurant", "Drink",
                                   "Clothing", "Shoes", "Electronics", "Household", "Cosmetic",
                                   "Medicine", "Medical", "Bus", "Train", "Taxi", "Subway", "Plane",
                                   "Game", "Movie", "KTV", "User defined"]
            
            if category not in allowed_categories:
                logger.error(f"非法主分类: {category}, 商品: {item_name}")
            
            if subcategory not in allowed_subcategories:
                logger.error(f"非法子分类: {subcategory}, 商品: {item_name}")
            
            # 如果没有subcategory或subcategory无效，根据category和商品名称推断
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
            logger.error(f"转换交易格式失败: {e}")
            return None
    
    def _heuristic_parse(self, response_text):
        """当标准解析失败时使用的备选解析方案"""
        import re
        
        try:
            logger.info("开始启发式解析...")
            
            # 定义关键词模式
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
            
            # 查找所有可能的交易数据
            transactions = []
            
            # 使用正则表达式查找JSON对象
            json_pattern = r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}'
            json_objects = re.findall(json_pattern, response_text)
            
            for json_str in json_objects:
                try:
                    # 尝试解析JSON
                    item = json.loads(json_str)
                    if 'item_name' in item and 'amount' in item:
                        converted = self._convert_transaction_format(item)
                        if converted:
                            transactions.append(converted)
                except json.JSONDecodeError:
                    # 如果JSON解析失败，尝试使用正则表达式提取
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
                logger.info(f"启发式解析成功，找到 {len(transactions)} 个交易")
                return {
                    'has_transaction': True,
                    'transactions': transactions
                }
            else:
                logger.warning("启发式解析未找到有效交易")
                return {"has_transaction": False, "error": "No valid transactions found in heuristic parsing"}
                
        except Exception as e:
            logger.error(f"启发式解析失败: {e}")
            return {"has_transaction": False, "error": f"Heuristic parsing failed: {e}"}
    
    def _parse_multiple_json_objects(self, gpt_response):
        """解析多个独立的JSON对象"""
        import re
        
        try:
            # 使用正则表达式匹配JSON对象
            json_pattern = r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}'
            json_objects = re.findall(json_pattern, gpt_response)
            
            if not json_objects:
                return {"has_transaction": False, "error": "No JSON objects found"}
            
            transactions = []
            for json_str in json_objects:
                try:
                    # 解析每个JSON对象
                    item = json.loads(json_str)
                    converted = self._convert_transaction_format(item)
                    if converted:
                        transactions.append(converted)
                except json.JSONDecodeError as e:
                    logger.warning(f"解析JSON对象失败: {e}, JSON: {json_str}")
                    continue
            
            if transactions:
                return {
                    'has_transaction': True,
                    'transactions': transactions
                }
            else:
                return {"has_transaction": False, "error": "No valid transactions found"}
                
        except Exception as e:
            logger.error(f"解析多个JSON对象失败: {e}")
            return {"has_transaction": False, "error": f"Multiple JSON parsing failed: {e}"}
    
    def _convert_any_format_to_standard(self, data):
        """转换任何格式的数据为标准格式"""
        try:
            transactions = []
            
            # 定义允许的分类
            allowed_categories = ["Dining", "Shopping", "Healthcare", "Transport", "Entertainment", "Other"]
            allowed_subcategories = {
                "Dining": ["Daily meal", "Snack", "Restaurant", "Drink"],
                "Shopping": ["Clothing", "Electronics", "Household", "Cosmetic"],
                "Healthcare": ["Medicine", "Medical"],
                "Transport": ["Bus", "Train", "Taxi", "Subway"],
                "Entertainment": ["Game", "Movie", "KTV"],
                "Other": ["User defined"]
            }
            
            # 处理不同的数据结构
            if 'transactions' in data:
                items = data['transactions']
                # 检查是否是嵌套结构（transactions包含items数组）
                if items and isinstance(items[0], dict) and 'items' in items[0]:
                    # 处理嵌套结构：transactions[0].items
                    all_items = []
                    for transaction in items:
                        if 'items' in transaction:
                            all_items.extend(transaction['items'])
                    items = all_items
            elif 'transaction' in data:  # 添加对单数字段的支持
                items = data['transaction']
            elif 'items' in data:
                items = data['items']
            elif 'products' in data:
                items = data['products']
            elif 'purchased_items' in data:
                items = data['purchased_items']
            # 处理嵌套结构
            elif 'order_details' in data and 'items' in data['order_details']:
                items = data['order_details']['items']
            elif 'order_details' in data and 'products' in data['order_details']:
                items = data['order_details']['products']
            else:
                return {"has_transaction": False, "error": "No transaction data found"}
            
            for item in items:
                converted = self._convert_transaction_format(item)
                if converted:
                    # 检查分类是否合法
                    category = converted.get('category', '')
                    subcategory = converted.get('subcategory', '')
                    
                    if category not in allowed_categories:
                        logger.error(f"非法分类: {category}, 商品: {converted.get('item_name')}")
                        # 尝试自动修正分类
                        corrected_category = self._correct_category(category, converted.get('item_name'))
                        if corrected_category:
                            converted['category'] = corrected_category
                            logger.info(f"自动修正分类: {category} -> {corrected_category}")
                        else:
                            logger.warning(f"无法修正分类: {category}, 跳过该商品")
                            continue
                    
                    if category in allowed_subcategories and subcategory not in allowed_subcategories[category]:
                        logger.error(f"非法子分类: {subcategory}, 主分类: {category}, 商品: {converted.get('item_name')}")
                        # 尝试自动修正子分类
                        corrected_subcategory = self._correct_subcategory(category, subcategory, converted.get('item_name'))
                        if corrected_subcategory:
                            converted['subcategory'] = corrected_subcategory
                            logger.info(f"自动修正子分类: {subcategory} -> {corrected_subcategory}")
                        else:
                            logger.warning(f"无法修正子分类: {subcategory}, 跳过该商品")
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
            logger.error(f"转换格式失败: {e}")
            return {"has_transaction": False, "error": f"Format conversion failed: {e}"}
    


def parse_single_email(email_obj):
    """解析单个邮件"""
    try:
        logger.info(f"开始解析邮件 ID: {email_obj.id}, 主题: {email_obj.subject}")
        logger.info(f"邮件发件人: {email_obj.sender}")
        logger.info(f"邮件内容长度: {len(email_obj.body) if email_obj.body else 0} 字符")
        logger.info(f"邮件内容前500字符: {email_obj.body[:500] if email_obj.body else 'None'}...")
        
        parser = GPTEmailParser()
        result = parser.parse_email_content(email_obj.subject, email_obj.sender, email_obj.body)
        
        logger.info(f"邮件解析结果: {result}")
        
        return result
        
    except Exception as e:
        logger.error(f"解析邮件失败 (邮件ID: {email_obj.id}): {e}")
        return {
            'has_transaction': False,
            'transactions': [],
            'error': str(e)
        } 