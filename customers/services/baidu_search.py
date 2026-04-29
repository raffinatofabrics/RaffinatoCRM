# customers/services/baidu_search.py

import requests
import time
import random
import re
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

class BaiduSearchService:
    """百度搜索服务 - 增强版"""
    
    def __init__(self, use_proxy=False, proxy_list=None):
        self.session = requests.Session()
        self.ua = UserAgent()
        self.use_proxy = use_proxy
        self.proxy_list = proxy_list or []
        
        # 设置默认请求头
        self._update_headers()
    
    def _update_headers(self):
        """更新请求头，模拟真实浏览器"""
        self.session.headers.update({
            'User-Agent': self.ua.random,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0',
        })
    
    def _get_proxy(self):
        """获取代理"""
        if self.use_proxy and self.proxy_list:
            return {'http': random.choice(self.proxy_list), 'https': random.choice(self.proxy_list)}
        return None
    
    def _random_delay(self):
        """随机延时"""
        time.sleep(random.uniform(1, 3))
    
    def search(self, keyword, max_results=50, province=None, city=None):
        """
        百度搜索
        keyword: 关键词
        max_results: 最大结果数
        province: 省份限定
        city: 城市限定
        """
        all_results = []
        pages_needed = min((max_results + 9) // 10, 5)  # 最多5页
        
        # 构建搜索词
        search_keyword = keyword
        if province:
            search_keyword = f"{keyword} {province}"
        if city:
            search_keyword = f"{keyword} {city}"
        
        for page in range(pages_needed):
            pn = page * 10
            url = f"https://www.baidu.com/s?wd={self._encode_keyword(search_keyword)}&pn={pn}"
            
            try:
                # 每次请求前更新 User-Agent
                self._update_headers()
                
                response = self.session.get(url, timeout=30, proxies=self._get_proxy())
                response.encoding = 'utf-8'
                
                if response.status_code == 200:
                    results = self._parse_results(response.text)
                    all_results.extend(results)
                    
                    if len(all_results) >= max_results:
                        break
                    
                    self._random_delay()
                else:
                    print(f"百度搜索返回状态码: {response.status_code}")
                    break
                    
            except Exception as e:
                print(f"百度搜索失败: {e}")
                continue
        
        return all_results[:max_results]
    
    def _encode_keyword(self, keyword):
        """编码关键词"""
        from urllib.parse import quote
        return quote(keyword)
    
    def _parse_results(self, html):
        """解析百度搜索结果"""
        results = []
        soup = BeautifulSoup(html, 'html.parser')
        
        # 方法1：使用百度结果容器
        result_containers = soup.select('.c-container') or soup.select('.result')
        
        for container in result_containers:
            # 提取标题和链接
            title_elem = container.select_one('h3 a, .t a')
            if not title_elem:
                continue
            
            title = title_elem.get_text().strip()
            url = title_elem.get('href', '')
            
            # 解析真实 URL
            if url.startswith('/url?q='):
                match = re.search(r'/url\?q=([^&]+)', url)
                if match:
                    url = match.group(1)
            
            # 过滤无效结果
            if not url or not title:
                continue
            if 'baidu.com' in url and 'link?url=' not in url:
                continue
            if len(title) < 5:
                continue
            
            # 提取摘要
            snippet_elem = container.select_one('.c-abstract, .content-right, .c-span-last')
            snippet = snippet_elem.get_text().strip() if snippet_elem else ''
            
            # 提取可能的企业信息
            company_info = self._extract_company_info(container)
            
            results.append({
                'url': url,
                'title': title,
                'snippet': snippet,
                'company_name': company_info.get('name', ''),
                'phone': company_info.get('phone', ''),
            })
        
        return results
    
    def _extract_company_info(self, container):
        """从搜索结果中提取企业信息"""
        info = {'name': '', 'phone': ''}
        
        # 提取公司名称
        company_elem = container.select_one('.c-showurl, .c-gap-top-small a')
        if company_elem:
            text = company_elem.get_text()
            # 提取域名作为公司名参考
            if 'http' in text:
                match = re.search(r'//([^/]+)', text)
                if match:
                    domain = match.group(1).replace('www.', '')
                    info['name'] = domain.split('.')[0].capitalize()
        
        # 提取电话
        phone_pattern = r'1[3-9]\d{9}|0\d{2,3}[- ]?\d{7,8}'
        text = container.get_text()
        phones = re.findall(phone_pattern, text)
        if phones:
            info['phone'] = phones[0]
        
        return info


class BaiduSearchWithCookies(BaiduSearchService):
    """使用 Cookie 的百度搜索（更稳定）"""
    
    def __init__(self, cookies=None, **kwargs):
        super().__init__(**kwargs)
        if cookies:
            self.session.cookies.update(cookies)
    
    def get_cookies_from_browser(self):
        """从浏览器获取 Cookie（需要手动操作）"""
        print("请按以下步骤获取百度 Cookie：")
        print("1. 在浏览器中登录百度账号")
        print("2. 打开开发者工具 (F12)")
        print("3. 切换到 Network 标签")
        print("4. 访问 www.baidu.com")
        print("5. 复制请求头中的 Cookie 值")
        return None