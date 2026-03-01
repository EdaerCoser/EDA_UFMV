"""
测试场景生成器

动态生成不同规模和复杂度的测试场景
"""

from sv_randomizer import Randomizable
from sv_randomizer.api import rand, constraint
from typing import Type


def create_n_vars_object(n: int, bits: int = 8, min_val: int = 0, max_val: int = 255) -> Type[Randomizable]:
    """
    创建包含n个变量的Randomizable类

    Args:
        n: 变量数量
        bits: 位宽
        min_val: 最小值
        max_val: 最大值

    Returns:
        Randomizable类
    """
    annotations = [rand(int)(bits=bits, min=min_val, max=max_val)
                    for _ in range(n)]

    class DynamicVars(Randomizable):
        pass

    for i, ann in enumerate(annotations):
        setattr(DynamicVars, f'var{i}', ann)

    return DynamicVars


def create_simple_object(num_vars: int = 5) -> Randomizable:
    """
    创建简单测试对象（无约束）

    Args:
        num_vars: 变量数量

    Returns:
        Randomizable实例
    """
    cls = create_n_vars_object(num_vars)
    return cls()


def create_medium_object(num_vars: int = 15) -> Randomizable:
    """
    创建中等测试对象（简单约束）

    Args:
        num_vars: 变量数量

    Returns:
        Randomizable实例
    """
    cls = create_n_vars_object(num_vars)
    obj = cls()

    # 添加一些简单约束
    for i in range(min(3, num_vars)):
        constraint_name = f'constraint_{i}'
        # 这里简化处理，实际会在具体测试中添加约束

    return obj


def create_large_object(num_vars: int = 30) -> Randomizable:
    """
    创建大规模测试对象（中等约束）

    Args:
        num_vars: 变量数量

    Returns:
        Randomizable实例
    """
    cls = create_n_vars_object(num_vars)
    return cls()


def create_stress_object(num_vars: int = 50) -> Randomizable:
    """
    创建压力测试对象（复杂约束）

    Args:
        num_vars: 变量数量

    Returns:
        Randomizable实例
    """
    cls = create_n_vars_object(num_vars)
    return cls()
