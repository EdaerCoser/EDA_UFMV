"""
用户装饰器API

提供 @rand, @randc, @constraint 装饰器
"""

from functools import wraps
from typing import Any, Callable, List, Optional, Union

from ..core.variables import RandVar, RandCVar, VarType
from ..constraints.base import ExpressionConstraint
from ..constraints.expressions import Expression


def rand(bit_width: int = 32, min_val: int = 0, max_val: Optional[int] = None, enum_values: Optional[List[Any]] = None):
    """
    rand变量装饰器

    用于定义普通随机变量（值可重复）

    Args:
        bit_width: 位宽（用于bit/logic类型）
        min_val: 最小值
        max_val: 最大值
        enum_values: 枚举值列表

    示例:
        class Packet(Randomizable):
            @rand(bit_width=16)
            def addr(self):
                return 0  # 默认值

            @rand(enum_values=["READ", "WRITE"])
            def opcode(self):
                return "READ"
    """
    def decorator(func: Callable[[Any], Any]) -> property:
        @wraps(func)
        def getter(self) -> Any:
            var_name = func.__name__

            # 首次访问时创建RandVar
            if var_name not in self._rand_vars:
                var_type = VarType.INT

                # 根据enum_values判断类型
                if enum_values:
                    var_type = VarType.ENUM
                    var = RandVar(var_name, var_type, enum_values=enum_values)
                else:
                    # 确定最大值
                    actual_max_val = max_val if max_val is not None else (1 << bit_width) - 1
                    var = RandVar(var_name, var_type, bit_width=bit_width, min_val=min_val, max_val=actual_max_val)

                self._rand_vars[var_name] = var

            # 返回当前值或默认值
            if var_name in self.__dict__:
                return self.__dict__[var_name]
            return func(self)

        @wraps(func)
        def setter(self, value: Any):
            self.__dict__[func.__name__] = value

        return property(getter, setter)
    return decorator


def randc(bit_width: int = 8, enum_values: Optional[List[Any]] = None):
    """
    randc变量装饰器

    用于定义循环随机变量（遍历所有可能值后才重复）

    Args:
        bit_width: 位宽
        enum_values: 枚举值列表

    示例:
        class Packet(Randomizable):
            @randc(bit_width=4)  # 16个可能值，遍历完才重复
            def transaction_id(self):
                return 0

            @randc(enum_values=["A", "B", "C"])
            def mode(self):
                return "A"
    """
    def decorator(func: Callable[[Any], Any]) -> property:
        @wraps(func)
        def getter(self) -> Any:
            var_name = func.__name__

            # 首次访问时创建RandCVar
            if var_name not in self._randc_vars:
                var_type = VarType.BIT

                if enum_values:
                    var = RandCVar(var_name, VarType.ENUM, enum_values=enum_values)
                else:
                    var = RandCVar(var_name, var_type, bit_width=bit_width)

                self._randc_vars[var_name] = var

            # 返回当前值或默认值
            if var_name in self.__dict__:
                return self.__dict__[var_name]
            return func(self)

        @wraps(func)
        def setter(self, value: Any):
            self.__dict__[func.__name__] = value

        return property(getter, setter)
    return decorator


def constraint(name: str, expression: Optional[str] = None):
    """
    约束装饰器 - 支持字符串表达式和函数形式

    Args:
        name: 约束名称
        expression: 可选的字符串表达式

    示例:
        # 字符串形式 (新，推荐)
        class Packet(Randomizable):
            @rand(bit_width=16)
            def addr(self):
                return 0

            @constraint("valid_addr", "addr > 0x1000 && addr < 0xFFFF")
            def valid_addr_c(self):
                pass

        # 函数形式 (旧，向后兼容)
        class Packet(Randomizable):
            @rand(bit_width=16)
            def addr(self):
                return 0

            @constraint("valid_addr")
            def valid_addr_c(self):
                return VarProxy("addr") > 0x1000

        # 混合形式 (函数返回字符串)
        @constraint("valid")
        def valid_c(self):
            return "x > 10 && y < 20"
    """
    def decorator(func: Callable[[Any], Union[Expression, bool, str]]) -> None:
        @wraps(func)
        def wrapper(self) -> None:
            # 优先使用装饰器参数中的字符串表达式
            if expression is not None:
                # 字符串表达式模式
                from ..constraints.parser import parse_expression
                try:
                    expr = parse_expression(expression)
                except Exception as e:
                    raise ValueError(f"Failed to parse constraint expression '{expression}': {e}")
            else:
                # 函数模式 - 调用函数获取表达式
                result = func(self)
                if result is None:
                    return

                # 如果函数返回字符串，解析它
                if isinstance(result, str):
                    from ..constraints.parser import parse_expression
                    try:
                        expr = parse_expression(result)
                    except Exception as e:
                        raise ValueError(f"Failed to parse constraint expression '{result}': {e}")
                elif isinstance(result, Expression):
                    expr = result
                else:
                    # 其他值转换为常量
                    from ..constraints.expressions import ConstantExpr
                    expr = ConstantExpr(result)

            constraint_obj = ExpressionConstraint(name, expr)
            self.add_constraint(constraint_obj)

        # 将约束函数存储为特殊属性
        wrapper._is_constraint = True
        wrapper._constraint_name = name
        wrapper._constraint_expression = expression  # 存储字符串表达式
        return wrapper
    return decorator


# 便捷函数

def disable_constraint(obj: Any, name: str) -> None:
    """
    禁用约束

    Args:
        obj: Randomizable对象
        name: 约束名称
    """
    obj.constraint_mode(name, False)


def enable_constraint(obj: Any, name: str) -> None:
    """
    启用约束

    Args:
        obj: Randomizable对象
        name: 约束名称
    """
    obj.constraint_mode(name, True)


def disable_rand(obj: Any, name: str) -> None:
    """
    禁用随机变量

    Args:
        obj: Randomizable对象
        name: 变量名
    """
    obj.rand_mode(name, False)


def enable_rand(obj: Any, name: str) -> None:
    """
    启用随机变量

    Args:
        obj: Randomizable对象
        name: 变量名
    """
    obj.rand_mode(name, True)
