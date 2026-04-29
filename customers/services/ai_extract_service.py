import json
import requests
from django.conf import settings

class AIExtractService:
    """AI信息提取服务"""
    
    def __init__(self):
        self.api_key = getattr(settings, 'OPENAI_API_KEY', None)
    
    def is_available(self):
        return self.api_key is not None and len(self.api_key) > 0
    
    def extract_business_info(self, html_content, url):
        """从网页提取公司信息"""
        if not self.is_available():
            return self._get_mock_extraction(url)
        
        # 限制内容长度
        content = html_content[:8000]
        
        prompt = f"""从以下网页内容中提取公司信息，返回JSON格式：
网页URL: {url}
内容: {content}

提取字段：company_name（公司名）、email（邮箱）、phone（电话）、contact_person（联系人）、industry（行业）

只返回JSON，不要其他内容。"""
        
        try:
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
                json={
                    "model": "gpt-3.5-turbo",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.1
                },
                timeout=60
            )
            result = response.json()
            content = result['choices'][0]['message']['content']
            return json.loads(content)
        except Exception as e:
            print(f"AI提取失败: {e}")
            return self._get_mock_extraction(url)
    
    def _get_mock_extraction(self, url):
        """模拟提取数据"""
        return {
            'company_name': '',
            'email': '',
            'phone': '',
            'contact_person': '',
            'industry': '',
        }
    
def generate_email(self, customer_data, style='formal', language='english'):
    """生成开发信 - 支持多语言"""
    if not self.is_available():
        return self._get_mock_email(customer_data, style, language)
    
    style_desc = {
        'formal': '正式专业',
        'friendly': '友好亲切',
        'concise': '简洁明了'
    }.get(style, '正式专业')
    
    lang_map = {
        'english': 'English',
        'chinese': 'Chinese',
        'italian': 'Italian',
        'german': 'German',
        'french': 'French',
        'spanish': 'Spanish'
    }
    
    prompt = f"""
请根据以下客户信息，生成一封{style_desc}的{lang_map.get(language, 'English')}开发信邮件。

客户信息:
- 公司名称: {customer_data.get('company_name', '贵公司')}
- 联系人: {customer_data.get('contact_person', '先生/女士')}
- 行业: {customer_data.get('industry', '未知')}
- 国家: {customer_data.get('country', '未知')}

返回JSON格式:
{{"subject": "邮件标题", "body": "邮件正文"}}

不要有其他内容。
"""
    
    result = self._call_openai(prompt)
    
    if result:
        return result
    
    return self._get_mock_email(customer_data, style, language)

def _get_mock_email(self, customer_data, style='formal', language='english'):
    """模拟邮件模板"""
    company = customer_data.get('company_name', 'your esteemed company')
    contact = customer_data.get('contact_person', 'Sir/Madam')
    
    if language == 'chinese':
        subject = f'合作机会 - {company}'
        body = f'尊敬的{contact}：\n\n我们非常欣赏贵公司的成就，希望能探讨合作机会。\n\n期待您的回复！'
    else:
        subject = f'Business Cooperation Opportunity - {company}'
        body = f'Dear {contact},\n\nWe are writing to introduce our company and explore potential cooperation opportunities.\n\nLooking forward to your reply.\n\nBest regards,\n[Your Company Name]'
    
    return {'subject': subject, 'body': body}