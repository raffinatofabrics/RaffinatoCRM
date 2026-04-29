# customers/services/proxy_service.py

import requests
import random

class ProxyService:
    """代理IP服务"""
    
    def __init__(self):
        self.proxies = []
    
    def fetch_free_proxies(self):
        """获取免费代理（稳定性一般）"""
        try:
            url = "https://api.proxyscrape.com/v2/?request=displayproxies&protocol=http&timeout=5000&country=all&ssl=all&anonymity=all"
            response = requests.get(url, timeout=10)
            proxies = response.text.strip().split('\r\n')
            self.proxies = [f"http://{p}" for p in proxies if p]
            print(f"获取到 {len(self.proxies)} 个代理")
            return self.proxies
        except Exception as e:
            print(f"获取代理失败: {e}")
            return []
    
    def get_random_proxy(self):
        """随机获取一个代理"""
        if self.proxies:
            return random.choice(self.proxies)
        return None
    
    def test_proxy(self, proxy):
        """测试代理是否可用"""
        try:
            response = requests.get(
                'http://www.baidu.com',
                proxies={'http': proxy, 'https': proxy},
                timeout=10
            )
            return response.status_code == 200
        except:
            return False