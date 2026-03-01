"""
约束基类

定义约束的抽象接口和基础实现
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from .expressions import Expression


class Constraint(ABC):
    """
    约束基类

    SystemVerilog中的约束块对应这个类
    """

    def __init__(self, name: str, expr: Optional[Expression] = None):
        """
        Args:
            name: 约束名称
            expr: 约束表达式（可选，某些约束类型不需要表达式）
        """
        self.name = name
        self.expr = expr
        self.enabled = True

    @abstractmethod
    def check(self, context: Dict[str, Any]) -> bool:
        """
        检查约束是否满足

        Args:
            context: 变量名到值的映射

        Returns:
            True if constraint is satisfied, False otherwise
        """
        pass

    def get_variables(self) -> List[str]:
        """
        获取约束涉及的所有变量名

        Returns:
            变量名列表
        """
        if self.expr:
            return self.expr.get_variables()
        return []

    def enable(self) -> None:
        """启用此约束"""
        self.enabled = True

    def disable(self) -> None:
        """禁用此约束"""
        self.enabled = False

    def is_enabled(self) -> bool:
        """检查约束是否启用"""
        return self.enabled

    def __repr__(self) -> str:
        status = "enabled" if self.enabled else "disabled"
        return f"Constraint(name='{self.name}', {status}, expr={self.expr})"


class ExpressionConstraint(Constraint):
    """
    基于表达式的约束

    最常见的约束类型，直接使用表达式来定义约束
    """

    def __init__(self, name: str, expr: Expression):
        super().__init__(name, expr)

    def check(self, context: Dict[str, Any]) -> bool:
        if not self.enabled:
            return True
        if self.expr is None:
            return True

        result = self.expr.eval(context)
        return bool(result)


class CompoundConstraint(Constraint):
    """
    复合约束

    由多个子约束组合而成
    """

    def __init__(self, name: str, constraints: List[Constraint], mode: str = "AND"):
        """
        Args:
            name: 约束名称
            constraints: 子约束列表
            mode: 组合模式 ("AND" 或 "OR")
        """
        super().__init__(name)
        self.constraints = constraints
        self.mode = mode.upper()

    def check(self, context: Dict[str, Any]) -> bool:
        if not self.enabled:
            return True

        results = [c.check(context) for c in self.constraints]

        if self.mode == "AND":
            return all(results)
        elif self.mode == "OR":
            return any(results)
        else:
            raise ValueError(f"Unknown compound mode: {self.mode}")

    def get_variables(self) -> List[str]:
        vars_list = []
        for c in self.constraints:
            vars_list.extend(c.get_variables())
        return list(set(vars_list))  # 去重

    def __repr__(self) -> str:
        status = "enabled" if self.enabled else "disabled"
        return f"CompoundConstraint(name='{self.name}', {status}, mode={self.mode}, count={len(self.constraints)})"
