# customers/utils/duplicate_checker.py

import re
from urllib.parse import urlparse
from django.db.models import Q
from ..models import Customer

class DuplicateChecker:
    """重复客户检测器"""
    
    @staticmethod
    def extract_domain(email_or_url):
        """从邮箱或URL提取域名"""
        if not email_or_url:
            return None
        
        # 如果是邮箱
        if '@' in email_or_url:
            domain = email_or_url.split('@')[-1].lower()
            return domain
        
        # 如果是URL
        try:
            parsed = urlparse(email_or_url)
            domain = parsed.netloc or email_or_url
            # 去掉 www. 前缀
            domain = re.sub(r'^www\.', '', domain)
            return domain.lower()
        except:
            return None
    
    @staticmethod
    def normalize_company_name(name):
        """标准化公司名称（用于比较）"""
        if not name:
            return ""
        # 转小写
        name = name.lower()
        # 移除常见后缀
        suffixes = [
            ' co.', ' co', ' corp', ' corporation', ' inc', ' incorporated',
            ' ltd', ' limited', ' llc', ' llp', ' plc', ' group', ' holdings',
            '有限公司', '股份', '集团', '公司'
        ]
        for suffix in suffixes:
            name = name.replace(suffix, '')
        # 移除标点符号和多余空格
        name = re.sub(r'[^\w\s]', '', name)
        name = ' '.join(name.split())
        return name
    
    @staticmethod
    def check_duplicate(email=None, company_name=None, url=None):
        """
        检查是否存在重复客户
        返回: {'is_duplicate': bool, 'existing_customer': obj, 'match_type': str}
        """
        # 1. 通过邮箱检查
        if email:
            existing = Customer.objects.filter(email=email).first()
            if existing:
                return {
                    'is_duplicate': True,
                    'existing_customer': existing,
                    'match_type': 'email'
                }
        
        # 2. 通过域名检查（从邮箱或URL提取）
        domain = None
        if email:
            domain = DuplicateChecker.extract_domain(email)
        elif url:
            domain = DuplicateChecker.extract_domain(url)
        
        if domain:
            # 查找邮箱域名相同的客户
            existing = Customer.objects.filter(email__endswith=f'@{domain}').first()
            if existing:
                return {
                    'is_duplicate': True,
                    'existing_customer': existing,
                    'match_type': 'domain'
                }
        
        # 3. 通过公司名称检查（模糊匹配）
        if company_name:
            normalized = DuplicateChecker.normalize_company_name(company_name)
            if len(normalized) > 3:  # 名称足够长才进行模糊匹配
                all_customers = Customer.objects.all()
                for customer in all_customers:
                    existing_normalized = DuplicateChecker.normalize_company_name(customer.company_name)
                    if existing_normalized and normalized == existing_normalized:
                        return {
                            'is_duplicate': True,
                            'existing_customer': customer,
                            'match_type': 'company_name'
                        }
                    # 部分匹配（一个包含另一个）
                    if len(normalized) > 5 and len(existing_normalized) > 5:
                        if normalized in existing_normalized or existing_normalized in normalized:
                            return {
                                'is_duplicate': True,
                                'existing_customer': customer,
                                'match_type': 'company_name_partial'
                            }
        
        return {
            'is_duplicate': False,
            'existing_customer': None,
            'match_type': None
        }