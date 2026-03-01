"""
RGM Utilities - 工具模块

包含自定义异常和辅助函数。
"""

class RGMError(Exception):
    """RGM基础异常"""
    pass


class FieldOverlapError(RGMError):
    """字段重叠异常"""
    pass


class AddressConflictError(RGMError):
    """地址冲突异常"""
    pass


class InvalidAccessError(RGMError):
    """无效访问异常"""
    pass


class RegisterNotFoundError(RGMError):
    """寄存器未找到异常"""
    pass


class FieldNotFoundError(RGMError):
    """字段未找到异常"""
    pass
