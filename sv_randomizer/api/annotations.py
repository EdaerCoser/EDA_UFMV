# sv_randomizer/api/annotations.py
"""
类型注解API - 提供rand/randc/randenum类型注解
"""
from typing import Annotated, TypeVar, Any, List
from typing_extensions import get_args, get_origin

T = TypeVar('T')

class Rand:
    """rand变量元数据"""
    def __init__(self, bits: int = 32, min: int = None, max: int = None):
        self.bits = bits
        self.min = min
        self.max = max

    def __repr__(self):
        return f"Rand(bits={self.bits}, min={self.min}, max={self.max})"

class RandC:
    """randc变量元数据"""
    def __init__(self, bits: int = 8):
        self.bits = bits

    def __repr__(self):
        return f"RandC(bits={self.bits})"

class RandEnum:
    """枚举类型随机变量元数据"""
    def __init__(self, *values: Any):
        self.values = list(values)

    def __repr__(self):
        return f"RandEnum({self.values})"

def rand(typ: type) -> type:
    """
    创建rand类型注解的辅助函数

    使用方式: rand[int](bits=16, min=0, max=100)
    """
    class _RandBuilder:
        def __call__(self, **kwargs):
            return Annotated[typ, Rand(**kwargs)]
    return _RandBuilder()

def randc(typ: type) -> type:
    """
    创建randc类型注解的辅助函数

    使用方式: randc[int](bits=4)
    """
    class _RandCBuilder:
        def __call__(self, **kwargs):
            return Annotated[typ, RandC(**kwargs)]
    return _RandCBuilder()

# 辅助函数：检查注解是否包含Rand/RandC
def is_rand_annotation(hint: Any) -> bool:
    """检查是否为rand类型注解"""
    origin = get_origin(hint)
    if origin is Annotated:
        args = get_args(hint)
        if len(args) > 1 and isinstance(args[1], Rand):
            return True
    return False

def is_randc_annotation(hint: Any) -> bool:
    """检查是否为randc类型注解"""
    origin = get_origin(hint)
    if origin is Annotated:
        args = get_args(hint)
        if len(args) > 1 and isinstance(args[1], RandC):
            return True
    return False

def is_rand_enum_annotation(hint: Any) -> bool:
    """检查是否为枚举类型注解"""
    origin = get_origin(hint)
    if origin is Annotated:
        args = get_args(hint)
        if len(args) > 1 and isinstance(args[1], RandEnum):
            return True
    return False

def extract_rand_metadata(hint: Any) -> Rand:
    """从注解中提取Rand元数据"""
    args = get_args(hint)
    return args[1]

def extract_randc_metadata(hint: Any) -> RandC:
    """从注解中提取RandC元数据"""
    args = get_args(hint)
    return args[1]


def constraint(func):
    """
    约束装饰器 - 标记约束方法

    使用方式:
        @constraint
        def my_constraint(self):
            return self.x > 0

    被装饰的方法将在Randomizable初始化时被解析，
    其返回的Python表达式会被转换为Expression对象
    """
    func._is_constraint = True
    return func


__all__ = ['Rand', 'RandC', 'RandEnum', 'rand', 'randc', 'constraint',
           'is_rand_annotation', 'is_randc_annotation', 'is_rand_enum_annotation',
           'extract_rand_metadata', 'extract_randc_metadata']
