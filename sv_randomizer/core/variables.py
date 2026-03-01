"""
随机变量定义

实现SystemVerilog风格的rand和randc变量
"""

import random
from enum import Enum
from typing import Any, List, Optional, Union


class VarType(Enum):
    """变量类型枚举"""

    INT = "int"
    BIT = "bit"
    LOGIC = "logic"
    BOOL = "bool"
    ENUM = "enum"
    ARRAY = "array"


class RandVar:
    """
    普通随机变量，类似SystemVerilog的rand

    特性：每次randomize()独立生成，值可以重复

    示例：
        var = RandVar("addr", VarType.BIT, bit_width=16, min_val=0, max_val=65535)
        value = var.generate_unconstrained()
    """

    def __init__(
        self,
        name: str,
        var_type: VarType = VarType.INT,
        bit_width: Optional[int] = None,
        min_val: Optional[int] = None,
        max_val: Optional[int] = None,
        enum_values: Optional[List[Any]] = None,
    ):
        self.name = name
        self.var_type = var_type
        self.bit_width = bit_width
        self.min_val = min_val
        self.max_val = max_val
        self.enum_values = enum_values
        self.current_value: Optional[Any] = None

    def generate_unconstrained(self, rand: Optional[random.Random] = None) -> Any:
        """
        无约束时生成随机值

        Args:
            rand: Random实例，None则使用全局random模块

        Returns:
            随机生成的值
        """
        # 向后兼容：如果未提供rand，使用全局random模块
        rand_instance = rand if rand is not None else random

        if self.var_type == VarType.BOOL:
            return rand_instance.choice([True, False])

        elif self.var_type == VarType.ENUM:
            if not self.enum_values:
                raise ValueError(f"Enum variable '{self.name}' has no enum_values defined")
            return rand_instance.choice(self.enum_values)

        elif self.var_type in (VarType.BIT, VarType.LOGIC):
            if self.bit_width is not None:
                max_val = (1 << self.bit_width) - 1
                min_val = 0
            elif self.min_val is not None and self.max_val is not None:
                min_val = self.min_val
                max_val = self.max_val
            else:
                # 默认32位
                max_val = (1 << 32) - 1
                min_val = 0
            return rand_instance.randint(min_val, max_val)

        elif self.var_type == VarType.INT:
            if self.min_val is not None and self.max_val is not None:
                return rand_instance.randint(self.min_val, self.max_val)
            else:
                # 默认范围
                min_val = self.min_val if self.min_val is not None else 0
                max_val = self.max_val if self.max_val is not None else (1 << 32) - 1
                return rand_instance.randint(min_val, max_val)

        # 默认情况
        return rand_instance.randint(0, (1 << 32) - 1)

    def get_range(self) -> tuple[int, int]:
        """
        获取变量的取值范围

        Returns:
            (min_value, max_value) 元组
        """
        if self.var_type == VarType.ENUM:
            if self.enum_values:
                return (min(self.enum_values), max(self.enum_values))
            return (0, 0)

        min_val = self.min_val if self.min_val is not None else 0

        if self.bit_width is not None:
            max_val = (1 << self.bit_width) - 1
        elif self.max_val is not None:
            max_val = self.max_val
        else:
            max_val = (1 << 32) - 1

        return (min_val, max_val)

    def __repr__(self) -> str:
        type_str = f"{self.var_type.value}"
        if self.bit_width:
            type_str += f"[{self.bit_width - 1}:0]"
        return f"RandVar(name='{self.name}', type={type_str})"


class RandCVar:
    """
    循环随机变量，类似SystemVerilog的randc

    特性：遍历所有可能值后才重复，像洗牌一样

    示例：
        var = RandCVar("id", VarType.BIT, bit_width=4)  # 16个可能值
        # 前16次调用返回不重复的值
        # 第17次开始新的循环
    """

    def __init__(
        self,
        name: str,
        var_type: VarType = VarType.BIT,
        bit_width: Optional[int] = None,
        enum_values: Optional[List[Any]] = None,
    ):
        self.name = name
        self.var_type = var_type
        self.bit_width = bit_width
        self.enum_values = enum_values
        self.current_value: Optional[Any] = None
        self._value_pool: List[Any] = []
        self._random: Optional[random.Random] = None
        self._initialize_pool()

    def _initialize_pool(self) -> None:
        """初始化值池并打乱顺序"""
        if self.var_type == VarType.ENUM:
            if not self.enum_values:
                raise ValueError(f"Enum variable '{self.name}' has no enum_values defined")
            self._value_pool = self.enum_values.copy()
        elif self.bit_width is not None:
            pool_size = 1 << self.bit_width  # 2^bit_width
            self._value_pool = list(range(pool_size))
        else:
            # 默认8位
            pool_size = 1 << 8
            self._value_pool = list(range(pool_size))

        # 打乱顺序，使用指定的Random实例或全局random
        rand_instance = self._random if self._random is not None else random
        rand_instance.shuffle(self._value_pool)

    def get_next(self) -> Any:
        """
        获取下一个值

        如果值池为空，则重新初始化并洗牌

        Returns:
            下一个随机值
        """
        if not self._value_pool:
            self._initialize_pool()

        self.current_value = self._value_pool.pop()
        return self.current_value

    def set_random(self, rand: random.Random) -> None:
        """
        设置Random实例

        Args:
            rand: Random实例

        注意: 只有当Random实例真正改变时才重置值池
        """
        # 只有Random实例真正改变时才重置值池
        if self._random is not rand:
            self._random = rand
            self._initialize_pool()

    def reset(self) -> None:
        """重置值池，重新开始循环"""
        self._initialize_pool()

    def peek_remaining(self) -> int:
        """
        查看剩余未使用的值数量

        Returns:
            剩余值数量
        """
        return len(self._value_pool)

    def get_total_count(self) -> int:
        """
        获取总可能值数量

        Returns:
            总可能值数量
        """
        if self.var_type == VarType.ENUM:
            return len(self.enum_values) if self.enum_values else 0
        elif self.bit_width is not None:
            return 1 << self.bit_width
        return 1 << 8  # 默认8位

    def __repr__(self) -> str:
        type_str = f"{self.var_type.value}"
        if self.bit_width:
            type_str += f"[{self.bit_width - 1}:0]"
        remaining = self.peek_remaining()
        total = self.get_total_count()
        return f"RandCVar(name='{self.name}', type={type_str}, remaining={remaining}/{total})"


# 用于变量类型推断的辅助函数


def infer_var_type(value: Any) -> VarType:
    """
    根据值推断变量类型

    Args:
        value: 要推断的值

    Returns:
        推断出的VarType
    """
    if isinstance(value, bool):
        return VarType.LOGIC
    elif isinstance(value, int):
        return VarType.INT
    elif isinstance(value, str):
        return VarType.ENUM
    elif isinstance(value, (list, tuple)):
        return VarType.ARRAY
    else:
        return VarType.INT
