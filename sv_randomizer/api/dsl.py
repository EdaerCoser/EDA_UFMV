"""
DSL语法糖

提供inside(), dist()函数和VarProxy类，简化约束定义
"""

from typing import Any, Dict, List, Tuple, Union

from ..constraints.expressions import (
    Expression,
    VariableExpr,
    ConstantExpr,
    BinaryExpr,
    BinaryOp,
)
from ..constraints.builders import InsideConstraint, DistConstraint


class Inside:
    """
    inside约束DSL

    SystemVerilog语法: x inside {[0:255], [500:600], 1000}

    Python用法:
        x.inside([(0, 255), (500, 600), 1000])
        或
        inside([(0, 255), 500, 600]) == VarProxy("x")
    """

    def __init__(self, *args: Union[Tuple[int, int], int]):
        """
        Args:
            *args: 范围元组 (low, high) 或单个值
        """
        self.ranges = list(args)

    def __eq__(self, other: Any) -> Expression:
        """
        创建inside约束表达式

        Args:
            other: 变量名或VariableExpr

        Returns:
            表达式对象
        """
        if isinstance(other, str):
            var_name = other
        elif isinstance(other, VariableExpr):
            var_name = other.name
        elif isinstance(other, VarProxy):
            var_name = other.name
        else:
            raise TypeError(f"inside requires a variable name or VarProxy, got {type(other)}")

        # 创建InsideConstraint，但这里我们返回表达式
        # 实际的约束需要在randomize时处理
        return self._build_expression(var_name)

    def _build_expression(self, var_name: str) -> Expression:
        """构建inside表达式"""
        var_expr = VariableExpr(var_name)
        conditions = []

        for item in self.ranges:
            if isinstance(item, tuple):
                low, high = item
                # (x >= low) && (x <= high)
                ge_cond = BinaryExpr(var_expr, BinaryOp.GE, ConstantExpr(low))
                le_cond = BinaryExpr(var_expr, BinaryOp.LE, ConstantExpr(high))
                range_cond = BinaryExpr(ge_cond, BinaryOp.AND, le_cond)
                conditions.append(range_cond)
            else:
                # x == value
                eq_cond = BinaryExpr(var_expr, BinaryOp.EQ, ConstantExpr(item))
                conditions.append(eq_cond)

        # 用 OR 连接所有条件
        if len(conditions) == 0:
            return ConstantExpr(True)
        elif len(conditions) == 1:
            return conditions[0]
        else:
            result = conditions[0]
            for cond in conditions[1:]:
                result = BinaryExpr(result, BinaryOp.OR, cond)
            return result


class Dist:
    """
    dist权重分布约束DSL

    SystemVerilog语法:
        addr dist {0 := 40, [1:10] := 60}
        value dist {0:/1, [1:9]:/2, [10:99]:/1}

    Python用法:
        dist({0: 40, (1, 10): 60})
    """

    def __init__(self, weights: Dict[Union[Tuple[int, int], int], int]):
        """
        Args:
            weights: 权重字典，key为范围或单个值，value为权重
        """
        self.weights = weights

    def __eq__(self, other: Any) -> "DistConstraint":
        """
        创建DistConstraint

        Args:
            other: 变量名或VarProxy

        Returns:
            DistConstraint对象
        """
        if isinstance(other, str):
            var_name = other
        elif isinstance(other, VarProxy):
            var_name = other.name
        else:
            raise TypeError(f"dist requires a variable name or VarProxy, got {type(other)}")

        # 注意：返回DistConstraint，不是Expression
        # 这是一个特殊约束，在求解时特殊处理
        return DistConstraint(f"_dist_{var_name}", var_name, self.weights)


class VarProxy:
    """
    变量代理类，支持运算符重载

    用于创建约束表达式的便捷方式

    示例:
        VarProxy("x") > 5
        VarProxy("addr") >= 0x1000
        (VarProxy("x") + VarProxy("y")) == 10
    """

    def __init__(self, name: str):
        """
        Args:
            name: 变量名
        """
        self.name = name
        self._expr = VariableExpr(name)

    def __eq__(self, other: Any) -> Expression:
        if isinstance(other, VarProxy):
            other = other._expr
        elif not isinstance(other, Expression):
            other = ConstantExpr(other)
        return BinaryExpr(self._expr, BinaryOp.EQ, other)

    def __ne__(self, other: Any) -> Expression:
        if isinstance(other, VarProxy):
            other = other._expr
        elif not isinstance(other, Expression):
            other = ConstantExpr(other)
        return BinaryExpr(self._expr, BinaryOp.NE, other)

    def __lt__(self, other: Any) -> Expression:
        if isinstance(other, VarProxy):
            other = other._expr
        elif not isinstance(other, Expression):
            other = ConstantExpr(other)
        return BinaryExpr(self._expr, BinaryOp.LT, other)

    def __le__(self, other: Any) -> Expression:
        if isinstance(other, VarProxy):
            other = other._expr
        elif not isinstance(other, Expression):
            other = ConstantExpr(other)
        return BinaryExpr(self._expr, BinaryOp.LE, other)

    def __gt__(self, other: Any) -> Expression:
        if isinstance(other, VarProxy):
            other = other._expr
        elif not isinstance(other, Expression):
            other = ConstantExpr(other)
        return BinaryExpr(self._expr, BinaryOp.GT, other)

    def __ge__(self, other: Any) -> Expression:
        if isinstance(other, VarProxy):
            other = other._expr
        elif not isinstance(other, Expression):
            other = ConstantExpr(other)
        return BinaryExpr(self._expr, BinaryOp.GE, other)

    def __add__(self, other: Any) -> Expression:
        if isinstance(other, VarProxy):
            other = other._expr
        elif not isinstance(other, Expression):
            other = ConstantExpr(other)
        return BinaryExpr(self._expr, BinaryOp.ADD, other)

    def __sub__(self, other: Any) -> Expression:
        if isinstance(other, VarProxy):
            other = other._expr
        elif not isinstance(other, Expression):
            other = ConstantExpr(other)
        return BinaryExpr(self._expr, BinaryOp.SUB, other)

    def __mul__(self, other: Any) -> Expression:
        if isinstance(other, VarProxy):
            other = other._expr
        elif not isinstance(other, Expression):
            other = ConstantExpr(other)
        return BinaryExpr(self._expr, BinaryOp.MUL, other)

    def __mod__(self, other: Any) -> Expression:
        if isinstance(other, VarProxy):
            other = other._expr
        elif not isinstance(other, Expression):
            other = ConstantExpr(other)
        return BinaryExpr(self._expr, BinaryOp.MOD, other)

    def __and__(self, other: Any) -> Expression:
        if isinstance(other, VarProxy):
            other = other._expr
        elif not isinstance(other, Expression):
            other = ConstantExpr(other)
        return BinaryExpr(self._expr, BinaryOp.AND, other)

    def __or__(self, other: Any) -> Expression:
        if isinstance(other, VarProxy):
            other = other._expr
        elif not isinstance(other, Expression):
            other = ConstantExpr(other)
        return BinaryExpr(self._expr, BinaryOp.OR, other)

    def implies(self, other: Any) -> Expression:
        """蕴含运算 (->)"""
        if isinstance(other, VarProxy):
            other = other._expr
        elif not isinstance(other, Expression):
            other = ConstantExpr(other)
        return BinaryExpr(self._expr, BinaryOp.IMPLIES, other)

    def __repr__(self) -> str:
        return f"VarProxy('{self.name}')"


# 便捷函数


def inside(*args: Union[Tuple[int, int], int]) -> Inside:
    """
    创建inside约束

    Args:
        *args: 范围元组或单个值

    Returns:
        Inside对象

    示例:
        inside((0, 255), 500, 1000)
    """
    return Inside(*args)


def dist(weights: Dict[Union[Tuple[int, int], int], int]) -> Dist:
    """
    创建dist权重分布约束

    Args:
        weights: 权重字典

    Returns:
        Dist对象

    示例:
        dist({0: 10, (1, 10): 30, (11, 100): 60})
    """
    return Dist(weights)


def var(name: str) -> VarProxy:
    """
    创建变量代理

    Args:
        name: 变量名

    Returns:
        VarProxy对象

    示例:
        var("x") > 5
    """
    return VarProxy(name)
