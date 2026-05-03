from django import template

register = template.Library()

@register.filter
def chinese_amount(value):
    """将数字转换为中文大写金额"""
    if not value:
        return '零元整'
    
    try:
        num = float(value)
    except:
        return str(value)
    
    # 中文大写数字
    chinese_num = ['零', '壹', '贰', '叁', '肆', '伍', '陆', '柒', '捌', '玖']
    chinese_unit = ['', '拾', '佰', '仟']
    chinese_big_unit = ['', '万', '亿']
    
    # 分离整数和小数
    integer_part = int(num)
    decimal_part = int(round((num - integer_part) * 100))
    
    # 转换整数部分
    if integer_part == 0:
        integer_str = '零'
    else:
        integer_str = ''
        num_str = str(integer_part)
        length = len(num_str)
        for i, digit in enumerate(num_str):
            d = int(digit)
            if d != 0:
                integer_str += chinese_num[d] + chinese_unit[(length - i - 1) % 4]
            else:
                # 处理连续的零
                if i < length - 1 and int(num_str[i + 1]) != 0:
                    integer_str += '零'
        
        # 添加万、亿单位
        if length > 8:
            integer_str = integer_str[:-4] + '万' + integer_str[-4:]
        elif length > 4:
            integer_str = integer_str[:-4] + '万' + integer_str[-4:]
    
    # 转换小数部分
    if decimal_part == 0:
        decimal_str = '整'
    else:
        jiao = decimal_part // 10
        fen = decimal_part % 10
        decimal_str = ''
        if jiao > 0:
            decimal_str += chinese_num[jiao] + '角'
        if fen > 0:
            decimal_str += chinese_num[fen] + '分'
    
    result = integer_str + '元' + decimal_str
    return result

@register.filter(name='smart_number')
def smart_number(value):
    """去掉无意义的 .0，不四舍五入"""
    if value is None:
        return ''
    try:
        # 如果是整数（如 7.0 或 7.00）
        if value == int(value):
            return str(int(value))
        else:
            # 保留原小数，去掉末尾多余的 0
            s = f'{value:.10f}'.rstrip('0').rstrip('.')
            return s
    except (ValueError, TypeError):
        return value