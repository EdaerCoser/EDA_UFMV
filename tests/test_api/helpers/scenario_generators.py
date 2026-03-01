"""
测试场景生成器

动态生成不同规模和复杂度的测试场景
"""

from sv_randomizer import Randomizable
from sv_randomizer.api import rand, constraint
from sv_randomizer.core.randomizable import _process_annotations
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
    # 创建类型注解字典
    annotations = {f'var{i}': rand(int)(bits=bits, min=min_val, max=max_val)
                   for i in range(n)}

    class DynamicVars(Randomizable):
        pass

    # 设置类型注解
    DynamicVars.__annotations__ = annotations

    # 手动触发注解处理
    _process_annotations(DynamicVars, annotations)

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

    添加简单的排序约束，确保变量之间有基本的顺序关系

    Args:
        num_vars: 变量数量

    Returns:
        Randomizable实例
    """
    cls = create_n_vars_object(num_vars)

    # 添加简单排序约束: var0 < var1 < var2
    if num_vars >= 3:
        @constraint
        def simple_ordering(self):
            return self.var0 < self.var1 and self.var1 < self.var2

        setattr(cls, 'simple_ordering', simple_ordering)

    return cls()


def create_large_object(num_vars: int = 30) -> Randomizable:
    """
    创建大规模测试对象（中等约束）

    添加求和约束和范围约束，增加约束复杂度

    Args:
        num_vars: 变量数量

    Returns:
        Randomizable实例
    """
    cls = create_n_vars_object(num_vars)

    # 添加求和约束: 前几个变量的和不超过特定值
    if num_vars >= 5:
        @constraint
        def sum_constraint(self):
            return (self.var0 + self.var1 + self.var2 + self.var3) < 500

        setattr(cls, 'sum_constraint', sum_constraint)

    # 添加范围约束: 某个变量在特定范围内
    if num_vars >= 10:
        @constraint
        def range_constraint(self):
            return self.var5 >= 50 and self.var5 <= 150

        setattr(cls, 'range_constraint', range_constraint)

    return cls()


def create_stress_object(num_vars: int = 50) -> Randomizable:
    """
    创建压力测试对象（复杂约束）

    添加多个相互依赖的复杂约束，测试约束求解器的能力

    Args:
        num_vars: 变量数量

    Returns:
        Randomizable实例
    """
    cls = create_n_vars_object(num_vars)

    # 添加多个复杂的相互依赖约束
    if num_vars >= 10:
        # 约束1: 多变量排序
        @constraint
        def complex_ordering(self):
            return self.var0 < self.var1 and self.var1 < self.var2 and self.var2 < self.var3

        setattr(cls, 'complex_ordering', complex_ordering)

        # 约束2: 加权求和约束
        @constraint
        def weighted_sum(self):
            return (self.var0 * 2 + self.var1 * 3 + self.var2) < 400

        setattr(cls, 'weighted_sum', weighted_sum)

        # 约束3: 范围限制
        @constraint
        def range_limits(self):
            return self.var4 >= 20 and self.var4 <= 100 and self.var5 >= 30 and self.var5 <= 120

        setattr(cls, 'range_limits', range_limits)

        # 约束4: 逻辑组合约束
        @constraint
        def logical_combination(self):
            return (self.var6 + self.var7 < 200) and (self.var8 > self.var9)

        setattr(cls, 'logical_combination', logical_combination)

    return cls()
