# customers/services/crawler_service.py

import requests
import time
import random
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup

class CrawlerService:
    """网站爬取服务 - 增强版"""
    
    USER_AGENTS = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
    ]
    
    CONTACT_PATHS = [
        'contact', 'contact-us', 'contactus', 'about', 'about-us',
        'company', 'profile', '联系我们', '关于我们', '联系方式'
    ]
    
    def __init__(self, timeout=30, max_retries=2):
        self.timeout = timeout
        self.max_retries = max_retries
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': random.choice(self.USER_AGENTS)})
    
    def crawl(self, url):
        """爬取网页内容"""
        for attempt in range(self.max_retries):
            try:
                response = self.session.get(url, timeout=self.timeout, allow_redirects=True)
                response.raise_for_status()
                response.encoding = response.apparent_encoding or 'utf-8'
                return {
                    'success': True,
                    'content': response.text,
                    'url': response.url,
                }
            except Exception as e:
                if attempt == self.max_retries - 1:
                    return {'success': False, 'error': str(e)}
                time.sleep(2)
        return {'success': False, 'error': '未知错误'}
    
    def crawl_with_contact_pages(self, base_url):
        """爬取首页和联系页面"""
        results = {
            'home': None,
            'contact_pages': [],
            'all_content': ''
        }
        
        # 1. 爬取首页
        home_result = self.crawl(base_url)
        if home_result['success']:
            results['home'] = home_result['content']
            results['all_content'] += home_result['content']
        
        # 2. 寻找并爬取联系页面
        if home_result['success']:
            soup = BeautifulSoup(home_result['content'], 'html.parser')
            contact_urls = self._find_contact_urls(soup, base_url)
            
            for contact_url in contact_urls[:3]:  # 最多3个联系页面
                contact_result = self.crawl(contact_url)
                if contact_result['success']:
                    results['contact_pages'].append(contact_result['content'])
                    results['all_content'] += contact_result['content']
                time.sleep(0.5)
        
        return results
    
    def _find_contact_urls(self, soup, base_url):
        """从页面中寻找联系页面URL"""
        contact_urls = set()
        
        for link in soup.find_all('a', href=True):
            href = link['href']
            full_url = urljoin(base_url, href)
            
            # 只处理同域名链接
            if not full_url.startswith(base_url):
                continue
            
            # 检查是否包含联系关键词
            for path in self.CONTACT_PATHS:
                if path in href.lower():
                    contact_urls.add(full_url)
                    break
        
        return list(contact_urls)