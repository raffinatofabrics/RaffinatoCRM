# customers/services/ai_service.py

import json
import requests
from django.conf import settings

class AIService:
    """AI 服务类 - 支持 OpenAI API"""
    
    def __init__(self):
        self.api_key = getattr(settings, 'OPENAI_API_KEY', None)
        self.api_base = getattr(settings, 'OPENAI_API_BASE', 'https://api.openai.com/v1')
        self.model = getattr(settings, 'OPENAI_MODEL', 'gpt-3.5-turbo')
    
    def is_available(self):
        """检查 API 是否可用"""
        return self.api_key is not None and len(self.api_key) > 0
    
    def _infer_country_from_url(self, url):
        """从 URL 推断国家"""
        country_map = {
            '.us': '美国', '.uk': '英国', '.de': '德国', '.fr': '法国',
            '.it': '意大利', '.jp': '日本', '.kr': '韩国', '.cn': '中国',
            '.ca': '加拿大', '.au': '澳大利亚', '.ru': '俄罗斯', '.br': '巴西',
            '.in': '印度', '.es': '西班牙', '.nl': '荷兰', '.ch': '瑞士',
            '.sg': '新加坡', '.nz': '新西兰', '.ie': '爱尔兰', '.se': '瑞典'
        }
        url_lower = url.lower()
        for suffix, country in country_map.items():
            if url_lower.endswith(suffix) or suffix in url_lower:
                return country
        return None
    
    def _call_openai(self, prompt, max_tokens=800):
        """调用 OpenAI API"""
        if not self.is_available():
            print("OpenAI API Key 未配置")
            return None
        
        url = f"{self.api_base}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.1,
            "max_tokens": max_tokens
        }
        
        try:
            response = requests.post(url, headers=headers, json=data, timeout=60)
            response.raise_for_status()
            result = response.json()
            content = result['choices'][0]['message']['content']
            return content
        except Exception as e:
            print(f"OpenAI API 调用失败: {e}")
            return None
    
    def extract_business_info(self, html_content, url):
        """从网页提取公司商业信息"""
        if not self.is_available():
            return self._get_mock_extraction()
        
        content_preview = html_content[:8000]
        
        prompt = f"""
请从以下网页内容中提取公司信息，返回 JSON 格式。

网页 URL: {url}

网页内容:
{content_preview}

请提取以下字段:
{{
    "company_name": "公司全称",
    "contact_person": "联系人姓名",
    "country": "所在国家",
    "city": "所在城市",
    "industry": "行业分类",
    "description": "公司简介（50字以内）",
    "founded_year": "成立年份",
    "employee_count": "员工规模"
}}

如果某个字段无法提取，请设为 null。只返回 JSON，不要其他内容。
"""
        
        result_str = self._call_openai(prompt, max_tokens=800)
        
        if result_str:
            try:
                data = json.loads(result_str)
            except json.JSONDecodeError:
                import re
                json_match = re.search(r'\{.*\}', result_str, re.DOTALL)
                if json_match:
                    try:
                        data = json.loads(json_match.group())
                    except:
                        data = self._get_mock_extraction()
                else:
                    data = self._get_mock_extraction()
        else:
            data = self._get_mock_extraction()
        
        if data.get('country') is None and url:
            inferred_country = self._infer_country_from_url(url)
            if inferred_country:
                data['country'] = inferred_country
                print(f"从 URL 推断国家: {inferred_country}")
        
        return data
    
    def _get_mock_extraction(self):
        """模拟提取数据"""
        return {
            'company_name': '',
            'contact_person': '',
            'country': '',
            'city': '',
            'industry': '',
            'description': '',
            'founded_year': None,
            'employee_count': ''
        }
    
    def generate_email(self, customer_info, style='formal', language='english'):
        """AI 生成开发信"""
        if not self.is_available():
            return self._get_mock_email(customer_info)
        
        style_desc = {
            'formal': '正式专业',
            'friendly': '友好亲切',
            'concise': '简洁明了'
        }.get(style, '正式专业')
        
        language_map = {
            'english': 'English',
            'chinese': 'Chinese',
            'italian': 'Italian',
            'german': 'German',
            'french': 'French',
            'spanish': 'Spanish'
        }
        
        prompt = f"""
请为客户生成一封 {language_map.get(language, 'English')} 语言的开发信邮件。
邮件风格：{style_desc}

客户信息：
- 公司名称：{customer_info.get('company_name', '贵公司')}
- 联系人：{customer_info.get('contact_person', '先生/女士')}
- 行业：{customer_info.get('industry', '未知')}
- 国家：{customer_info.get('country', '未知')}

请返回 JSON 格式：
{{"subject": "邮件标题", "body": "邮件正文"}}
"""
        
        result_str = self._call_openai(prompt, max_tokens=600)
        
        if result_str:
            try:
                return json.loads(result_str)
            except:
                pass
        
        return self._get_mock_email(customer_info)
    
    def _get_mock_email(self, customer_info):
        """模拟邮件模板"""
        company = customer_info.get('company_name', 'your esteemed company')
        contact = customer_info.get('contact_person', 'Sir/Madam')
        
        return {
            'subject': f'Business Cooperation Opportunity - {company}',
            'body': f'Dear {contact},\n\nWe are writing to introduce our company and explore potential cooperation opportunities.\n\nLooking forward to your reply.\n\nBest regards,\n[Your Company Name]'
        }
    
    def generate_email_by_subject(self, customer_info, style='formal', language='english'):
        """根据用户输入的主题生成邮件"""
        if not self.is_available():
            return self._get_mock_email_by_subject(customer_info, style, language)
        
        style_desc = {
            'formal': '正式专业',
            'friendly': '友好亲切',
            'concise': '简洁明了'
        }.get(style, '正式专业')
        
        language_map = {
            'english': 'English',
            'chinese': 'Chinese',
            'italian': 'Italian',
            'german': 'German',
            'french': 'French',
            'spanish': 'Spanish'
        }
        
        company = customer_info.get('company_name', '贵公司')
        contact = customer_info.get('contact_person') or '先生/女士'
        subject_input = customer_info.get('subject', '商务合作')
        
        prompt = f"""
请根据以下要求，生成一封 {language_map.get(language, 'English')} 语言的商务邮件。

客户信息：
- 公司名称：{company}
- 联系人：{contact}

用户指定的邮件主题：{subject_input}

邮件风格：{style_desc}

请直接返回 JSON 格式，不要有任何其他文字：
{{"subject": "邮件标题", "body": "邮件正文"}}
"""
        
        result_str = self._call_openai(prompt, max_tokens=800)
        print(f"AI 返回原始内容: {result_str}")
        
        if result_str:
            try:
                import re
                result_str = result_str.strip()
                if result_str.startswith('```json'):
                    result_str = result_str[7:]
                if result_str.startswith('```'):
                    result_str = result_str[3:]
                if result_str.endswith('```'):
                    result_str = result_str[:-3]
                result_str = result_str.strip()
                
                data = json.loads(result_str)
                print(f"解析成功: {data}")
                return data
            except json.JSONDecodeError as e:
                print(f"JSON解析失败: {e}")
        
        return self._get_mock_email_by_subject(customer_info, style, language)
    
    def _get_mock_email_by_subject(self, customer_info, style='formal', language='english'):
        """模拟邮件模板"""
        company = customer_info.get('company_name', '贵公司')
        contact = customer_info.get('contact_person') or '先生/女士'
        subject_input = customer_info.get('subject', '商务合作')
        
        if language == 'chinese':
            return {
                'subject': subject_input,
                'body': f'尊敬的{contact}：\n\n关于"{subject_input}"，我们希望能与贵公司进一步沟通。\n\n期待您的回复！'
            }
        else:
            return {
                'subject': subject_input,
                'body': f'Dear {contact},\n\nRegarding "{subject_input}", we would like to discuss this further with your company.\n\nLooking forward to your reply.'
            }