# customers/utils/extractors.py

import re
from bs4 import BeautifulSoup

def extract_emails(html_content):
    """增强版邮箱提取"""
    # 更多邮箱匹配模式
    patterns = [
        # 标准邮箱
        r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
        # 带 mailto: 前缀
        r'mailto:([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})',
        # 在文本中被括号或空格包围的邮箱
        r'[\s\(\)\[\]]([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})[\s\(\)\[\]]',
    ]
    
    # 过滤公共邮箱
    common_domains = [
        'gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com',
        'qq.com', '163.com', '126.com', 'sina.com', 'foxmail.com',
        'msn.com', 'live.com', 'aol.com', 'protonmail.com'
    ]
    
    all_emails = set()
    for pattern in patterns:
        matches = re.findall(pattern, html_content, re.IGNORECASE)
        all_emails.update(matches)
    
    # 过滤并排序（优先显示企业邮箱）
    valid_emails = []
    for email in all_emails:
        email = email.lower().strip()
        domain = email.split('@')[-1]
        if domain not in common_domains and len(domain.split('.')) >= 2:
            valid_emails.append(email)
    
    # 去重并返回
    seen = set()
    unique_emails = []
    for email in valid_emails:
        if email not in seen:
            seen.add(email)
            unique_emails.append(email)
    
    return unique_emails[:5]  # 最多5个


def extract_phones(html_content):
    """增强版电话提取"""
    patterns = [
        # 国际格式: +86 123-4567-8901
        r'\+\d{1,3}[\s\-]?\(?\d{1,4}\)?[\s\-]?\d{3,4}[\s\-]?\d{3,4}',
        # 中国手机: 13812345678
        r'1[3-9]\d{9}',
        # 中国固话: 0755-12345678
        r'0\d{2,3}[\s\-]?\d{7,8}',
        # 北美格式: (123) 456-7890
        r'\(?\d{3}\)?[\s\-]?\d{3}[\s\-]?\d{4}',
        # 常见显示格式: 123.456.7890
        r'\d{3}[\.\s\-]\d{3}[\.\s\-]\d{4}',
    ]
    
    phones = set()
    for pattern in patterns:
        matches = re.findall(pattern, html_content)
        phones.update(matches)
    
    # 清理格式
    clean_phones = []
    for phone in phones:
        clean = re.sub(r'[^\d+]', '', phone)
        if 8 <= len(clean) <= 15:
            clean_phones.append(clean)
    
    # 去重
    seen = set()
    unique_phones = []
    for phone in clean_phones:
        if phone not in seen:
            seen.add(phone)
            unique_phones.append(phone)
    
    return unique_phones[:5]


def extract_company_name(html_content, url):
    """增强版公司名提取"""
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # 1. 从 title 提取
    if soup.title:
        title = soup.title.string
        if title:
            # 常见分隔符
            for sep in ['|', '-', '—', '–', '·', '»', '|', '_', ':']:
                if sep in title:
                    title = title.split(sep)[0].strip()
                    break
            if 2 < len(title) < 50:
                return title.strip()
    
    # 2. 从 h1 提取
    h1 = soup.find('h1')
    if h1:
        text = h1.get_text().strip()
        if 2 < len(text) < 50:
            return text
    
    # 3. 从 domain 提取
    from urllib.parse import urlparse
    parsed = urlparse(url)
    domain = parsed.netloc.replace('www.', '').replace('.com', '').replace('.cn', '')
    parts = domain.split('.')
    if parts:
        company = parts[0].capitalize()
        if len(company) > 2:
            return company
    
    return ''