# sv_to_python/errors.py
"""
异常定义
"""
class ConversionError(Exception):
    """转换错误基类"""
    pass

class ParseError(ConversionError):
    """解析错误"""
    pass

class ExtractionError(ConversionError):
    """提取错误"""
    pass

class GenerationError(ConversionError):
    """生成错误"""
    pass
