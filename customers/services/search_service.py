# customers/services/search_service.py

import requests
import time
import random
from urllib.parse import quote
from bs4 import BeautifulSoup
from django.conf import settings
from .baidu_search import BaiduSearchService

class SearchService:
    """搜索服务 - 支持Google(SerpAPI)和百度(直接爬取)"""
    
    USER_AGENTS = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
    ]
    
    # 国家代码映射
    COUNTRY_CODES = {
        '美国': 'us', '英国': 'uk', '德国': 'de', '法国': 'fr',
        '意大利': 'it', '日本': 'jp', '韩国': 'kr', '中国': 'cn',
        '加拿大': 'ca', '澳大利亚': 'au', '西班牙': 'es', '荷兰': 'nl',
        '巴西': 'br', '印度': 'in', '俄罗斯': 'ru', '墨西哥': 'mx',
        '土耳其': 'tr', '瑞士': 'ch', '瑞典': 'se', '挪威': 'no',
        '丹麦': 'dk', '芬兰': 'fi', '波兰': 'pl', '奥地利': 'at',
        '比利时': 'be', '爱尔兰': 'ie', '葡萄牙': 'pt', '希腊': 'gr',
        '南非': 'za', '阿联酋': 'ae', '沙特': 'sa', '新加坡': 'sg',
        '马来西亚': 'my', '泰国': 'th', '越南': 'vn', '印尼': 'id',
    }
    
    def __init__(self, business_type='international'):
        self.business_type = business_type
        self.serpapi_key = getattr(settings, 'SERPAPI_KEY', None)
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': random.choice(self.USER_AGENTS)})
    
    def search(self, keyword, max_results=50, exclude_words=None, domain_suffix=None, target_country=None):
        """执行搜索，支持国家限定"""
        if self.business_type == 'international':
            return self._search_google(keyword, max_results, target_country)
        else:
            return self._search_baidu(keyword, max_results, exclude_words, domain_suffix, target_country)
    
    def _search_google(self, keyword, max_results, target_country=None):
        """Google搜索 - 支持国家限定"""
        if not self.serpapi_key:
            print("未配置 SerpAPI Key，使用模拟数据")
            return self._get_mock_results(keyword, max_results, target_country)
        
        all_results = []
        current_page = 0
        results_per_page = 10
        max_pages = min((max_results + results_per_page - 1) // results_per_page, 5)
        
        # 获取国家代码
        gl_code = None
        hl_code = 'en'
        if target_country and target_country in self.COUNTRY_CODES:
            gl_code = self.COUNTRY_CODES[target_country]
            print(f"限定搜索国家: {target_country} ({gl_code})")
        
        while len(all_results) < max_results and current_page < max_pages:
            params = {
                'q': keyword,
                'api_key': self.serpapi_key,
                'num': results_per_page,
                'start': current_page * results_per_page,
                'engine': 'google',
            }
            
            # 添加国家限定参数
            if gl_code:
                params['gl'] = gl_code  # 国家/地区
                params['hl'] = hl_code  # 语言
            
            try:
                response = requests.get("https://serpapi.com/search", params=params, timeout=30)
                data = response.json()
                
                if 'error' in data:
                    print(f"SerpAPI错误: {data['error']}")
                    break
                
                batch = data.get('organic_results', [])
                if not batch:
                    break
                
                for item in batch:
                    all_results.append({
                        'url': item.get('link', ''),
                        'title': item.get('title', ''),
                        'snippet': item.get('snippet', ''),
                    })
                
                current_page += 1
                
            except Exception as e:
                print(f"Google搜索失败: {e}")
                break
        
        print(f"Google搜索完成，共获取 {len(all_results)} 条结果")
        return all_results[:max_results]
    
    def _search_baidu(self, keyword, max_results, exclude_words, domain_suffix, target_country=None):
        """百度搜索 - 使用增强版"""
        # 使用增强版百度搜索
        baidu = BaiduSearchService()
        
        # 如果有省份限定
        province = None
        city = None
        if target_country:
            province = target_country
        
        results = baidu.search(
            keyword=keyword,
            max_results=max_results,
            province=province,
            city=city
        )
        
        # 格式化结果
        formatted_results = []
        for r in results:
            formatted_results.append({
                'url': r.get('url', ''),
                'title': r.get('title', ''),
                'snippet': r.get('snippet', ''),
            })
        
        return formatted_results
    
    def _get_mock_results(self, keyword, max_results, target_country=None):
        """模拟搜索结果"""
        mock_results = []
        country_suffix = f" in {target_country}" if target_country else ""
        
        for i in range(1, min(max_results, 20) + 1):
            mock_results.append({
                'url': f'https://example-company-{i}.com',
                'title': f'{keyword} - 示例公司{i}{country_suffix}',
                'snippet': f'专业{keyword}供应商，欢迎联系合作。'
            })
        return mock_results