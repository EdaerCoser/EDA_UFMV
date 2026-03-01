# sv_randomizer/api/annotations.py
"""
类型注解API - 提供rand/randc/randenum类型注解和DSL语法糖
"""
from typing import Annotated, TypeVar, Any, List, Union, Tuple
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


# ============================================================================
# DSL语法糖 - VarProxy, inside, dist（向后兼容）
# ============================================================================

class VarProxy:
    """
    变量代理类 - 用于表达式中的变量引用

    使用方式:
        VarProxy("x") > 0
    """

    def __init__(self, name: str):
        self.name = name

    def __repr__(self):
        return f"VarProxy({self.name})"

    def __eq__(self, other):
        """支持 == 比较"""
        from ..constraints.expressions import BinaryExpr, BinaryOp, ConstantExpr, VariableExpr
        if isinstance(other, VarProxy):
            return BinaryExpr(VariableExpr(self.name), BinaryOp.EQ, VariableExpr(other.name))
        elif isinstance(other, (int, float)):
            return BinaryExpr(VariableExpr(self.name), BinaryOp.EQ, ConstantExpr(other))
        return NotImplemented

    def __lt__(self, other):
        """支持 < 比较"""
        from ..constraints.expressions import BinaryExpr, BinaryOp, ConstantExpr, VariableExpr
        if isinstance(other, VarProxy):
            return BinaryExpr(VariableExpr(self.name), BinaryOp.LT, VariableExpr(other.name))
        elif isinstance(other, (int, float)):
            return BinaryExpr(VariableExpr(self.name), BinaryOp.LT, ConstantExpr(other))
        return NotImplemented

    def __le__(self, other):
        """支持 <= 比较"""
        from ..constraints.expressions import BinaryExpr, BinaryOp, ConstantExpr, VariableExpr
        if isinstance(other, VarProxy):
            return BinaryExpr(VariableExpr(self.name), BinaryOp.LE, VariableExpr(other.name))
        elif isinstance(other, (int, float)):
            return BinaryExpr(VariableExpr(self.name), BinaryOp.LE, ConstantExpr(other))
        return NotImplemented

    def __gt__(self, other):
        """支持 > 比较"""
        from ..constraints.expressions import BinaryExpr, BinaryOp, ConstantExpr, VariableExpr
        if isinstance(other, VarProxy):
            return BinaryExpr(VariableExpr(self.name), BinaryOp.GT, VariableExpr(other.name))
        elif isinstance(other, (int, float)):
            return BinaryExpr(VariableExpr(self.name), BinaryOp.GT, ConstantExpr(other))
        return NotImplemented

    def __ge__(self, other):
        """支持 >= 比较"""
        from ..constraints.expressions import BinaryExpr, BinaryOp, ConstantExpr, VariableExpr
        if isinstance(other, VarProxy):
            return BinaryExpr(VariableExpr(self.name), BinaryOp.GE, VariableExpr(other.name))
        elif isinstance(other, (int, float)):
            return BinaryExpr(VariableExpr(self.name), BinaryOp.GE, ConstantExpr(other))
        return NotImplemented

    def __add__(self, other):
        """支持 + 运算"""
        from ..constraints.expressions import BinaryExpr, BinaryOp, ConstantExpr, VariableExpr
        if isinstance(other, VarProxy):
            return BinaryExpr(VariableExpr(self.name), BinaryOp.ADD, VariableExpr(other.name))
        elif isinstance(other, (int, float)):
            return BinaryExpr(VariableExpr(self.name), BinaryOp.ADD, ConstantExpr(other))
        return NotImplemented

    def __sub__(self, other):
        """支持 - 运算"""
        from ..constraints.expressions import BinaryExpr, BinaryOp, ConstantExpr, VariableExpr
        if isinstance(other, VarProxy):
            return BinaryExpr(VariableExpr(self.name), BinaryOp.SUB, VariableExpr(other.name))
        elif isinstance(other, (int, float)):
            return BinaryExpr(VariableExpr(self.name), BinaryOp.SUB, ConstantExpr(other))
        return NotImplemented

    def __mul__(self, other):
        """支持 * 运算"""
        from ..constraints.expressions import BinaryExpr, BinaryOp, ConstantExpr, VariableExpr
        if isinstance(other, VarProxy):
            return BinaryExpr(VariableExpr(self.name), BinaryOp.MUL, VariableExpr(other.name))
        elif isinstance(other, (int, float)):
            return BinaryExpr(VariableExpr(self.name), BinaryOp.MUL, ConstantExpr(other))
        return NotImplemented

    def __and__(self, other):
        """支持 && 运算"""
        from ..constraints.expressions import BinaryExpr, BinaryOp, ConstantExpr, VariableExpr
        if isinstance(other, VarProxy):
            return BinaryExpr(VariableExpr(self.name), BinaryOp.AND, VariableExpr(other.name))
        return NotImplemented


def inside(*ranges: Union[Tuple[int, int], int]) -> '_InsideHelper':
    """
    inside约束DSL函数

    SystemVerilog语法: x inside {[0:255], [500:600], 1000}

    Python用法:
        inside([(0, 255), (500, 600), 1000]) == VarProxy("x")

    简化用法（推荐）:
        self.x.in_([(0, 255), (500, 600), 1000])

    Args:
        *ranges: 范围元组 (low, high) 或单个值

    Returns:
        _InsideHelper对象，支持 == 操作符
    """
    return _InsideHelper(ranges)


class _InsideHelper:
    """inside约束辅助类"""

    def __init__(self, ranges: list):
        self.ranges = list(ranges)

    def __eq__(self, other: Any) -> 'InExpression':
        """
        创建inside约束表达式

        Args:
            other: 变量名或VariableExpr或VarProxy

        Returns:
            表达式对象
        """
        from ..constraints.expressions import BinaryExpr, BinaryOp, ConstantExpr, VariableExpr, Expression

        if isinstance(other, str):
            var_name = other
            var_expr = VariableExpr(var_name)
        elif isinstance(other, VariableExpr):
            var_name = other.name
            var_expr = other
        elif isinstance(other, VarProxy):
            var_name = other.name
            var_expr = VariableExpr(var_name)
        else:
            raise TypeError(f"inside requires a variable name or VarProxy, got {type(other)}")

        # 构建OR条件的所有范围
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
            raise ValueError("inside requires at least one range or value")

        result = conditions[0]
        for cond in conditions[1:]:
            result = BinaryExpr(result, BinaryOp.OR, cond)

        return result


def dist(*weights: Union[Tuple[Any, int], int]) -> '_DistHelper':
    """
    dist约束DSL函数 - 权重分布

    SystemVerilog语法:
        x dist {[0:10]:=20, [10:100]:=80}

    Python用法:
        dist([(0, 10, 20), (10, 100, 80)]) == VarProxy("x")

    Args:
        *weights: (min, max, weight) 元组或列表

    Returns:
        _DistHelper对象，支持 == 操作符
    """
    return _DistHelper(list(weights))


class _DistHelper:
    """dist约束辅助类"""

    def __init__(self, weights: list):
        self.weights = weights

    def __eq__(self, other: Any) -> Any:
        """
        创建dist约束表达式（返回DistConstraint对象）

        Args:
            other: 变量名或VarProxy

        Returns:
            DistConstraint对象
        """
        from ..constraints.builders import DistConstraint

        if isinstance(other, str):
            var_name = other
        elif isinstance(other, VarProxy):
            var_name = other.name
        else:
            raise TypeError(f"dist requires a variable name or VarProxy, got {type(other)}")

        return DistConstraint(var_name, self.weights)


__all__ = [
    # 类型注解
    'Rand', 'RandC', 'RandEnum', 'rand', 'randc', 'constraint',

    # DSL语法糖
    'VarProxy', 'inside', 'dist',

    # 辅助函数
    'is_rand_annotation', 'is_randc_annotation', 'is_rand_enum_annotation',
    'extract_rand_metadata', 'extract_randc_metadata',
]

