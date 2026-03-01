"""
约束构建器

实现SystemVerilog风格的约束构建器：inside, dist等
"""

import random
from typing import Any, Dict, List, Tuple, Union, Optional

from .base import ExpressionConstraint
from .expressions import (
    Expression,
    VariableExpr,
    ConstantExpr,
    BinaryExpr,
    BinaryOp,
)


class InsideConstraint(ExpressionConstraint):
    """
    inside约束实现

    SystemVerilog语法: x inside {[0:255], [500:600], 1000, 2000}

    示例:
        InsideConstraint("addr_range", "addr", [(0, 255), (500, 600), 1000])
    """

    def __init__(
        self,
        name: str,
        variable: str,
        ranges: List[Union[Tuple[int, int], int]],
    ):
        """
        Args:
            name: 约束名称
            variable: 变量名
            ranges: 范围列表，每个元素是 (low, high) 元组或单个值
        """
        self.variable = variable
        self.ranges = ranges
        expr = self._build_expression()
        super().__init__(name, expr)

    def _build_expression(self) -> Expression:
        """构建inside约束的表达式"""
        var_expr = VariableExpr(self.variable)
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
                # 单个值: x == value
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

    def get_allowed_values(self) -> List[int]:
        """
        获取所有允许的值（对于小范围）

        Returns:
            允许的值列表（如果范围太大则返回空列表）
        """
        values = []
        total_estimate = 0

        for item in self.ranges:
            if isinstance(item, tuple):
                low, high = item
                total_estimate += high - low + 1
                if total_estimate > 1000:  # 范围太大
                    return []
            else:
                total_estimate += 1

        if total_estimate > 1000:
            return []

        for item in self.ranges:
            if isinstance(item, tuple):
                low, high = item
                values.extend(range(low, high + 1))
            else:
                values.append(item)

        return values

    def __repr__(self) -> str:
        return f"InsideConstraint(name='{self.name}', var='{self.variable}', ranges={self.ranges})"


class DistConstraint(ExpressionConstraint):
    """
    dist权重分布约束

    SystemVerilog语法:
        addr dist {0 := 40, [1:10] := 60}
        value dist {0:/1, [1:9]:/2, [10:99]:/1}

    示例:
        DistConstraint("addr_weight", "addr", {0: 40, (1, 10): 60})
    """

    def __init__(
        self,
        name: str,
        variable: str,
        weights: Dict[Union[Tuple[int, int], int], int],
    ):
        """
        Args:
            name: 约束名称
            variable: 变量名
            weights: 权重字典，key为范围或单个值，value为权重
        """
        self.variable = variable
        self.weights = weights
        self.total_weight = sum(weights.values())
        self.cumulative = self._build_cumulative()
        # dist约束不需要表达式，直接采样
        super().__init__(name, None)

    def _build_cumulative(self) -> List[Tuple[int, int, Any]]:
        """
        构建累积分布表

        Returns:
            [(start, end, value_or_range), ...] 列表
        """
        result = []
        current = 0

        for value_or_range, weight in self.weights.items():
            start = current
            end = current + weight
            current = end
            result.append((start, end, value_or_range))

        return result

    def sample(self, rand: Optional[random.Random] = None) -> Any:
        """
        根据权重采样一个值

        Args:
            rand: Random实例，None则使用全局random模块

        Returns:
            采样得到的值
        """
        # 向后兼容：如果未提供rand，使用全局random模块
        rand_instance = rand if rand is not None else random

        rand_val = rand_instance.randint(0, self.total_weight - 1)

        for start, end, value_or_range in self.cumulative:
            if start <= rand_val < end:
                if isinstance(value_or_range, tuple):
                    # 范围，随机选择一个值
                    low, high = value_or_range
                    return rand_instance.randint(low, high)
                else:
                    # 单个值
                    return value_or_range

        return None

    def get_weight(self, value: int) -> int:
        """
        获取特定值的权重

        Args:
            value: 要查询的值

        Returns:
            该值的权重，如果值不在定义中则返回0
        """
        for value_or_range, weight in self.weights.items():
            if isinstance(value_or_range, tuple):
                low, high = value_or_range
                if low <= value <= high:
                    return weight
            elif value_or_range == value:
                return weight
        return 0

    def get_ranges(self) -> List[Tuple[Union[Tuple[int, int], int], int]]:
        """
        获取权重范围列表

        Returns:
            [(value_or_range, weight), ...] 列表
        """
        return list(self.weights.items())

    def check(self, context: Dict[str, Any]) -> bool:
        """
        dist约束的检查总是返回True，因为它只影响分布

        Args:
            context: 变量上下文

        Returns:
            总是返回True
        """
        # dist约束不影响约束满足性，只影响采样分布
        return True

    def __repr__(self) -> str:
        return f"DistConstraint(name='{self.name}', var='{self.variable}', weights={self.weights})"


class ArrayConstraint(ExpressionConstraint):
    """
    数组约束

    支持size(), foreach, unique等SystemVerilog数组约束

    示例:
        ArrayConstraint.size("arr_size", "data", min_size=1, max_size=10)
        ArrayConstraint.foreach("arr_positive", "data", lambda i: f"arr[{i}] > 0")
        ArrayConstraint.unique("arr_unique", ["data[0]", "data[1]", "data[2]"])
    """

    def __init__(
        self,
        name: str,
        array_var: str,
        constraint_type: str,
        **kwargs,
    ):
        """
        Args:
            name: 约束名称
            array_var: 数组变量名
            constraint_type: 约束类型 ("size", "foreach", "unique")
            **kwargs: 额外参数
        """
        self.array_var = array_var
        self.constraint_type = constraint_type.lower()
        self.params = kwargs
        expr = self._build_expression()
        super().__init__(name, expr)

    def _build_expression(self) -> Expression:
        if self.constraint_type == "size":
            return self._build_size_expression()
        elif self.constraint_type == "foreach":
            # foreach需要在求值时动态处理
            return ConstantExpr(True)
        elif self.constraint_type == "unique":
            return self._build_unique_expression()
        else:
            raise ValueError(f"Unknown array constraint type: {self.constraint_type}")

    def _build_size_expression(self) -> Expression:
        """构建size约束表达式"""
        from .expressions import SizeExpr

        size_expr = SizeExpr(self.array_var)
        min_size = self.params.get("min_size")
        max_size = self.params.get("max_size")

        if min_size is not None and max_size is not None:
            min_cond = BinaryExpr(size_expr, BinaryOp.GE, ConstantExpr(min_size))
            max_cond = BinaryExpr(size_expr, BinaryOp.LE, ConstantExpr(max_size))
            return BinaryExpr(min_cond, BinaryOp.AND, max_cond)
        elif min_size is not None:
            return BinaryExpr(size_expr, BinaryOp.GE, ConstantExpr(min_size))
        elif max_size is not None:
            return BinaryExpr(size_expr, BinaryOp.LE, ConstantExpr(max_size))
        else:
            return ConstantExpr(True)

    def _build_unique_expression(self) -> Expression:
        """构建unique约束表达式"""
        elements = self.params.get("elements", [])
        if len(elements) < 2:
            return ConstantExpr(True)

        # 生成所有配对的 != 约束
        conditions = []
        for i in range(len(elements)):
            for j in range(i + 1, len(elements)):
                elem_i = VariableExpr(elements[i])
                elem_j = VariableExpr(elements[j])
                ne_expr = BinaryExpr(elem_i, BinaryOp.NE, elem_j)
                conditions.append(ne_expr)

        # AND 所有条件
        if len(conditions) == 0:
            return ConstantExpr(True)
        elif len(conditions) == 1:
            return conditions[0]
        else:
            result = conditions[0]
            for cond in conditions[1:]:
                result = BinaryExpr(result, BinaryOp.AND, cond)
            return result

    def check(self, context: Dict[str, Any]) -> bool:
        """检查数组约束"""
        if self.constraint_type == "size":
            return super().check(context)
        elif self.constraint_type == "foreach":
            return self._check_foreach(context)
        elif self.constraint_type == "unique":
            return super().check(context)
        return True

    def _check_foreach(self, context: Dict[str, Any]) -> bool:
        """检查foreach约束"""
        arr = context.get(self.array_var, [])
        if not arr:
            return True

        condition = self.params.get("condition")
        if condition is None:
            return True

        # 对每个元素检查条件
        index_var = self.params.get("index_var", "i")
        for i, val in enumerate(arr):
            local_context = {**context, index_var: i, f"{self.array_var}[{i}]": val}
            # 这里简化处理，实际应该解析条件表达式
            # 暂时返回True
            pass

        return True

    def __repr__(self) -> str:
        return f"ArrayConstraint(name='{self.name}', type='{self.constraint_type}', arr='{self.array_var}')"
