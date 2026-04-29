# customers/services/ai_scoring.py

import json
from django.utils import timezone
from django.db.models import Sum
from ..models import Customer, CommunicationLog, Order

# 导入 SendLog（如果存在）
try:
    from send_logs.models import SendLog
except ImportError:
    SendLog = None
    print("Warning: SendLog model not found")


class AIScoringService:
    """AI客户评分服务 - 双维度"""
    
    def __init__(self):
        from .ai_service import AIService
        self.ai_service = AIService()
    
    def calculate_ai_score(self, customer):
        """计算AI意向评分 (0-100) - 基于互动行为"""
        score = 0
        reasons = []
        
        # 1. 基础信息完整度 (0-20分)
        completeness = 0
        if customer.company_name and customer.company_name != '待完善':
            completeness += 5
            reasons.append("公司名称完整")
        if customer.email:
            completeness += 5
            reasons.append("有邮箱")
        if customer.phone:
            completeness += 5
            reasons.append("有电话")
        if customer.country:
            completeness += 5
            reasons.append("有国家信息")
        score += completeness
        
        # 2. 邮件互动 (0-40分)
        if SendLog is not None:
            email_logs = SendLog.objects.filter(customer=customer)
            total_sent = email_logs.count()
            if total_sent > 0:
                reasons.append(f"发送过{total_sent}封邮件")
                # 有回复加分
                replied = email_logs.filter(has_replied=True).count()
                if replied > 0:
                    score += min(20, replied * 10)
                    reasons.append(f"有{replied}次回复")
                # 打开率加分
                opened = email_logs.filter(opened=True).count()
                if opened > 0:
                    score += min(15, opened * 5)
                    reasons.append(f"打开过{opened}封邮件")
        else:
            reasons.append("邮件追踪模块未安装")
        
        # 3. 沟通记录 (0-20分)
        comm_count = CommunicationLog.objects.filter(customer=customer).count()
        if comm_count > 0:
            score += min(15, comm_count * 3)
            reasons.append(f"有{comm_count}条沟通记录")
        
        # 4. 客户等级基础分 (0-20分)
        level_scores = {
            'vip': 20,
            'advanced': 15,
            'intermediate': 10,
            'potential': 5,
        }
        score += level_scores.get(customer.level, 0)
        reasons.append(f"客户等级: {customer.level}")
        
        # 5. 最近活跃度 (0-10分)
        if customer.last_contact_time:
            days_since = (timezone.now() - customer.last_contact_time).days
            if days_since <= 7:
                score += 10
                reasons.append("最近一周有联系")
            elif days_since <= 30:
                score += 5
                reasons.append("最近一个月有联系")
        
        # 限制最高100分
        score = min(100, score)
        
        return {
            'score': score,
            'reasons': reasons
        }
    
    def calculate_order_score(self, customer):
        """计算订单价值评分 (0-100) - 基于订单数据"""
        orders = Order.objects.filter(customer=customer)
        order_count = orders.count()
        
        if order_count == 0:
            return {
                'score': 0,
                'level': '新客户',
                'total_amount': 0,
                'order_count': 0,
                'avg_amount': 0,
                'reasons': ['暂无订单']
            }
        
        # 计算总金额
        total_amount = orders.aggregate(total=Sum('total_cost'))['total'] or 0
        avg_amount = total_amount / order_count
        
        # 最近订单时间
        latest_order = orders.order_by('-created_at').first()
        days_since_last = (timezone.now() - latest_order.created_at).days if latest_order else 999
        
        # 评分计算
        score = 0
        reasons = []
        
        # 1. 订单数量 (0-30分)
        if order_count >= 10:
            score += 30
            reasons.append(f"订单数: {order_count}次 (高频)")
        elif order_count >= 5:
            score += 20
            reasons.append(f"订单数: {order_count}次 (中频)")
        elif order_count >= 1:
            score += 10
            reasons.append(f"订单数: {order_count}次")
        
        # 2. 总金额 (0-40分)
        if total_amount >= 100000:
            score += 40
            reasons.append(f"总金额: ¥{total_amount:,.0f} (大客户)")
        elif total_amount >= 50000:
            score += 30
            reasons.append(f"总金额: ¥{total_amount:,.0f}")
        elif total_amount >= 10000:
            score += 20
            reasons.append(f"总金额: ¥{total_amount:,.0f}")
        elif total_amount > 0:
            score += 10
            reasons.append(f"总金额: ¥{total_amount:,.0f}")
        
        # 3. 平均订单金额 (0-20分)
        if avg_amount >= 10000:
            score += 20
            reasons.append(f"客单价: ¥{avg_amount:,.0f} (高)")
        elif avg_amount >= 5000:
            score += 15
            reasons.append(f"客单价: ¥{avg_amount:,.0f}")
        elif avg_amount >= 1000:
            score += 10
            reasons.append(f"客单价: ¥{avg_amount:,.0f}")
        
        # 4. 最近活跃度 (0-10分)
        if days_since_last <= 30:
            score += 10
            reasons.append(f"最近{days_since_last}天内有订单")
        elif days_since_last <= 90:
            score += 5
            reasons.append(f"最近{days_since_last}天内有订单")
        
        # 确定等级
        if score >= 80:
            level = '核心客户'
        elif score >= 60:
            level = '重要客户'
        elif score >= 40:
            level = '普通客户'
        elif score > 0:
            level = '潜力客户'
        else:
            level = '新客户'
        
        return {
            'score': score,
            'level': level,
            'total_amount': total_amount,
            'order_count': order_count,
            'avg_amount': avg_amount,
            'days_since_last': days_since_last,
            'reasons': reasons
        }
    
    def get_customer_type(self, ai_score, order_score):
        """根据双维度确定客户类型"""
        # 判断高低（以50分为界）
        ai_high = ai_score >= 50
        order_high = order_score >= 50
        
        if ai_high and order_high:
            return {
                'name': '核心客户',
                'icon': '⭐',
                'color': 'danger',
                'strategy': '重点维护，定期回访，提升复购率'
            }
        elif ai_high and not order_high:
            return {
                'name': '潜力股',
                'icon': '🚀',
                'color': 'warning',
                'strategy': '促进转化，发送优惠信息，推动首单'
            }
        elif not ai_high and order_high:
            return {
                'name': '存量客户',
                'icon': '📦',
                'color': 'info',
                'strategy': '激活唤醒，发送新品推荐，提升互动'
            }
        else:
            return {
                'name': '需培育',
                'icon': '🌱',
                'color': 'secondary',
                'strategy': '长期跟进，发送有价值内容，逐步建立信任'
            }
    
    def generate_tags(self, customer, ai_score, order_score):
        """AI 生成客户标签"""
        if not self.ai_service.is_available():
            return self._get_mock_tags(customer, ai_score, order_score)
        
        comm_count = CommunicationLog.objects.filter(customer=customer).count()
        order_count = Order.objects.filter(customer=customer).count()
        
        customer_type = self.get_customer_type(ai_score, order_score)
        
        prompt = f"""
根据以下客户信息，生成3-5个标签，返回 JSON 数组格式。

客户信息：
- 公司名称：{customer.company_name}
- 国家：{customer.country or '未知'}
- AI意向评分：{ai_score}
- 订单价值评分：{order_score}
- 客户类型：{customer_type['name']}
- 沟通记录数：{comm_count}
- 订单数量：{order_count}

标签类型包括：行业特征、规模特征、行为特征、价值特征等。

只返回 JSON 数组，例如：["高意向", "有回复", "需跟进"]
"""
        
        result = self.ai_service._call_openai(prompt, max_tokens=200)
        if result:
            try:
                tags = json.loads(result)
                if isinstance(tags, list):
                    return tags
            except:
                pass
        
        return self._get_mock_tags(customer, ai_score, order_score)
    
    def _get_mock_tags(self, customer, ai_score, order_score):
        """模拟标签"""
        tags = []
        
        if ai_score >= 70:
            tags.append("高意向")
        elif ai_score >= 40:
            tags.append("中等意向")
        else:
            tags.append("低意向")
        
        if order_score >= 70:
            tags.append("高价值")
        elif order_score >= 40:
            tags.append("中等价值")
        elif order_score > 0:
            tags.append("有成交")
        
        customer_type = self.get_customer_type(ai_score, order_score)
        tags.append(customer_type['name'])
        
        if customer.country:
            tags.append("海外客户")
        
        return tags[:5]
    
    def analyze_customer(self, customer):
        """综合分析客户（双维度）"""
        # 计算两个评分
        ai_result = self.calculate_ai_score(customer)
        order_result = self.calculate_order_score(customer)
        
        # 确定客户类型
        customer_type = self.get_customer_type(ai_result['score'], order_result['score'])
        
        # 生成标签
        tags = self.generate_tags(customer, ai_result['score'], order_result['score'])
        
        # 更新客户（只保存AI评分）
        customer.ai_score = ai_result['score']
        customer.ai_tags = json.dumps(tags, ensure_ascii=False)
        customer.last_ai_analysis = timezone.now()
        customer.save()
        
        return {
            'ai_score': ai_result['score'],
            'ai_reasons': ai_result['reasons'],
            'order_score': order_result['score'],
            'order_reasons': order_result['reasons'],
            'order_stats': {
                'total_amount': order_result['total_amount'],
                'order_count': order_result['order_count'],
                'avg_amount': order_result['avg_amount']
            },
            'customer_type': customer_type,
            'tags': tags
        }