"""
求解器后端抽象接口

定义所有求解器后端必须实现的接口
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
import random

from ..constraints.expressions import BinaryOp, Expression


class SolverBackend(ABC):
    """
    求解器后端抽象接口

    所有求解器实现（PurePython, Z3等）必须继承此类并实现其方法
    """

    def __init__(self, seed: Optional[int] = None, random_instance: Optional[random.Random] = None):
        """
        初始化求解器

        Args:
            seed: 随机种子
            random_instance: Random实例（优先级高于seed）
        """
        if random_instance is not None:
            self._random = random_instance
        elif seed is not None:
            self._random = random.Random(seed)
        else:
            self._random = random.Random()

        self.variables: Dict[str, Any] = {}
        self.constraints: List[Any] = []

    @abstractmethod
    def create_variable(
        self,
        name: str,
        var_type: str = "int",
        **kwargs,
    ) -> Any:
        """
        创建求解器变量

        Args:
            name: 变量名
            var_type: 变量类型 ("int", "bool", "bit", "enum")
            **kwargs: 额外参数 (bit_width, min_val, max_val, enum_values等)

        Returns:
            求解器特定的变量对象
        """
        pass

    @abstractmethod
    def add_constraint(self, constraint_expr: Any) -> None:
        """
        添加约束到求解器

        Args:
            constraint_expr: 约束表达式（求解器特定格式）
        """
        pass

    @abstractmethod
    def solve(self) -> Optional[Dict[str, Any]]:
        """
        求解约束

        Returns:
            变量名到值的字典，如果无解返回None
        """
        pass

    @abstractmethod
    def reset(self) -> None:
        """重置求解器状态，清除所有变量和约束"""
        pass

    @abstractmethod
    def make_const(self, value: Any) -> Any:
        """
        创建常量表达式

        Args:
            value: 常量值

        Returns:
            求解器特定的常量表达式
        """
        pass

    @abstractmethod
    def make_binary_expr(self, left: Any, op: BinaryOp, right: Any) -> Any:
        """
        创建二元运算表达式

        Args:
            left: 左操作数
            op: 运算符
            right: 右操作数

        Returns:
            求解器特定的二元表达式
        """
        pass

    @abstractmethod
    def make_unary_expr(self, op: str, expr: Any) -> Any:
        """
        创建一元运算表达式

        Args:
            op: 运算符 ("!", "-", "~")
            expr: 操作数

        Returns:
            求解器特定的一元表达式
        """
        pass

    def get_variable_names(self) -> List[str]:
        """
        获取所有已注册的变量名

        Returns:
            变量名列表
        """
        return list(self.variables.keys())

    def has_variable(self, name: str) -> bool:
        """
        检查变量是否存在

        Args:
            name: 变量名

        Returns:
            变量是否存在
        """
        return name in self.variables

    def get_variable(self, name: str) -> Any:
        """
        获取求解器变量对象

        Args:
            name: 变量名

        Returns:
            求解器变量对象
        """
        return self.variables.get(name)

    def is_available(self) -> bool:
        """
        检查求解器后端是否可用

        Returns:
            后端是否可用（例如Z3是否已安装）
        """
        return True

    def get_backend_name(self) -> str:
        """
        获取后端名称

        Returns:
            后端名称字符串
        """
        return self.__class__.__name__

    def __repr__(self) -> str:
        return f"{self.get_backend_name()}(vars={len(self.variables)}, constraints={len(self.constraints)})"
