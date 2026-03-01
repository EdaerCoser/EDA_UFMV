"""
纯Python约束求解器后端

使用随机采样+约束检查的算法，无需外部依赖
适用于中小规模约束问题
"""

import random
from typing import Any, Dict, List, Optional

from .backend_interface import SolverBackend
from ..constraints.expressions import BinaryOp, Expression
from ..constraints.base import Constraint
from ..utils.exceptions import UnsatisfiableError, SolverBackendError


class PurePythonBackend(SolverBackend):
    """
    纯Python约束求解器

    算法：随机采样 + 约束验证

    适用场景：
    - 中小规模约束问题（<10个变量，<20个约束）
    - 无外部依赖环境
    - 快速原型验证

    不适用：
    - 大规模约束问题
    - 复杂的数学约束
    """

    def __init__(self, max_iterations: int = 10000, seed: Optional[int] = None,
                 random_instance: Optional[random.Random] = None):
        """
        Args:
            max_iterations: 最大求解迭代次数
            seed: 随机数种子（用于可重复性）
            random_instance: Random实例（优先级高于seed）
        """
        super().__init__(seed, random_instance)
        self.max_iterations = max_iterations

        # 变量信息存储
        self.var_info: Dict[str, Dict[str, Any]] = {}

    def create_variable(
        self,
        name: str,
        var_type: str = "int",
        **kwargs,
    ) -> str:
        """
        创建变量

        Args:
            name: 变量名
            var_type: 变量类型
            **kwargs: 额外参数

        Returns:
            变量名（作为引用）
        """
        var_info = {
            "name": name,
            "type": var_type,
            "min": kwargs.get("min_val", 0),
            "max": kwargs.get("max_val", 255),
            "bit_width": kwargs.get("bit_width", 8),
            "enum_values": kwargs.get("enum_values"),
        }

        # 根据类型调整范围
        if var_type == "bool":
            var_info["min"] = 0
            var_info["max"] = 1
        elif var_type == "bit" or var_type == "logic":
            bit_width = kwargs.get("bit_width", 8)
            var_info["min"] = 0
            var_info["max"] = (1 << bit_width) - 1

        self.var_info[name] = var_info
        self.variables[name] = name  # 简单存储，返回变量名作为引用

        return name

    def add_constraint(self, constraint_expr: Any) -> None:
        """
        添加约束

        Args:
            constraint_expr: 可以是Expression对象或Constraint对象
        """
        self.constraints.append(constraint_expr)

    def solve(self) -> Optional[Dict[str, Any]]:
        """
        求解约束

        使用随机采样算法：
        1. 生成随机候选解
        2. 检查是否满足所有约束
        3. 重复直到找到解或达到最大迭代次数

        Returns:
            变量名到值的字典，无解返回None
        """
        if not self.var_info:
            return {}

        for iteration in range(self.max_iterations):
            candidate = self._generate_candidate()

            if self._check_constraints(candidate):
                return candidate

        # 未找到解
        return None

    def _generate_candidate(self) -> Dict[str, Any]:
        """
        生成随机候选解

        Returns:
            变量名到值的字典
        """
        candidate = {}

        for name, info in self.var_info.items():
            if info["enum_values"]:
                candidate[name] = self._random.choice(info["enum_values"])
            else:
                candidate[name] = self._random.randint(info["min"], info["max"])

        return candidate

    def _check_constraints(self, candidate: Dict[str, Any]) -> bool:
        """
        检查候选解是否满足所有约束

        Args:
            candidate: 候选解

        Returns:
            是否满足所有约束
        """
        for constraint in self.constraints:
            if isinstance(constraint, Constraint):
                if not constraint.check(candidate):
                    return False
            elif isinstance(constraint, Expression):
                result = constraint.eval(candidate)
                if not result:
                    return False

        return True

    def reset(self) -> None:
        """重置求解器"""
        self.var_info.clear()
        self.variables.clear()
        self.constraints.clear()

    def make_const(self, value: Any) -> Any:
        """创建常量"""
        return value

    def make_binary_expr(self, left: Any, op: BinaryOp, right: Any) -> Any:
        """
        创建二元表达式

        注意：PurePython后端不使用这个方法，
        它直接使用Expression对象进行求值
        """
        from ..constraints.expressions import BinaryExpr

        # 如果left/right是变量名字符串，转换为VariableExpr
        if isinstance(left, str):
            from ..constraints.expressions import VariableExpr
            left = VariableExpr(left)
        if isinstance(right, str):
            from ..constraints.expressions import VariableExpr
            right = VariableExpr(right)

        # 如果是常量，转换为ConstantExpr
        if not isinstance(left, Expression):
            from ..constraints.expressions import ConstantExpr
            left = ConstantExpr(left)
        if not isinstance(right, Expression):
            from ..constraints.expressions import ConstantExpr
            right = ConstantExpr(right)

        return BinaryExpr(left, op, right)

    def make_unary_expr(self, op: str, expr: Any) -> Any:
        """
        创建一元表达式

        注意：PurePython后端不使用这个方法
        """
        from ..constraints.expressions import UnaryExpr

        if isinstance(expr, str):
            from ..constraints.expressions import VariableExpr
            expr = VariableExpr(expr)

        if not isinstance(expr, Expression):
            from ..constraints.expressions import ConstantExpr
            expr = ConstantExpr(expr)

        return UnaryExpr(op, expr)

    def get_backend_name(self) -> str:
        return "PurePython"
