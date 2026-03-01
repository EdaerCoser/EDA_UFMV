"""
约束表达式AST系统

实现SystemVerilog约束表达式的抽象语法树
"""

from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Dict, List, Optional, Union


class BinaryOp(Enum):
    """二元运算符枚举"""

    # 关系运算符
    EQ = "=="  # 等于
    NE = "!="  # 不等于
    LT = "<"  # 小于
    LE = "<="  # 小于等于
    GT = ">"  # 大于
    GE = ">="  # 大于等于

    # 逻辑运算符
    AND = "&&"  # 逻辑与
    OR = "||"  # 逻辑或
    IMPLIES = "->"  # 蕴含 (P -> Q 等价于 !P || Q)
    XNOR = "=="  # 同或 (用于逻辑值)

    # 算术运算符
    ADD = "+"  # 加
    SUB = "-"  # 减
    MUL = "*"  # 乘
    DIV = "/"  # 除
    MOD = "%"  # 取模

    # 位运算符
    BIT_AND = "&"  # 按位与
    BIT_OR = "|"  # 按位或
    BIT_XOR = "^"  # 按位异或
    BIT_XNOR = "~^"  # 按位同或
    SHIFT_LEFT = "<<"  # 左移
    SHIFT_RIGHT = ">>"  # 右移


class Expression(ABC):
    """表达式基类"""

    @abstractmethod
    def eval(self, context: Dict[str, Any]) -> Any:
        """
        在给定上下文中求值

        Args:
            context: 变量名到值的映射

        Returns:
            求值结果
        """
        pass

    @abstractmethod
    def get_variables(self) -> List[str]:
        """
        获取表达式中涉及的所有变量名

        Returns:
            变量名列表
        """
        pass

    def __and__(self, other: "Expression") -> "BinaryExpr":
        """& 运算符重载"""
        return BinaryExpr(self, BinaryOp.AND, other)

    def __or__(self, other: "Expression") -> "BinaryExpr":
        """| 运算符重载"""
        return BinaryExpr(self, BinaryOp.OR, other)

    def __and__(self, other: "Expression") -> "BinaryExpr":
        """&& 运算符 (按位与)"""
        return BinaryExpr(self, BinaryOp.AND, other)

    def __or__(self, other: "Expression") -> "BinaryExpr":
        """|| 运算符"""
        return BinaryExpr(self, BinaryOp.OR, other)

    def implies(self, other: "Expression") -> "BinaryExpr":
        """蕴含运算 (->)"""
        return BinaryExpr(self, BinaryOp.IMPLIES, other)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}()"


class VariableExpr(Expression):
    """
    变量引用表达式

    示例: x, addr, data[0]
    """

    def __init__(self, name: str):
        self.name = name

    def eval(self, context: Dict[str, Any]) -> Any:
        return context.get(self.name)

    def get_variables(self) -> List[str]:
        return [self.name]

    def __eq__(self, other: Any) -> "BinaryExpr":
        """== 运算符"""
        if isinstance(other, Expression):
            return BinaryExpr(self, BinaryOp.EQ, other)
        return BinaryExpr(self, BinaryOp.EQ, ConstantExpr(other))

    def __ne__(self, other: Any) -> "BinaryExpr":
        """!= 运算符"""
        if isinstance(other, Expression):
            return BinaryExpr(self, BinaryOp.NE, other)
        return BinaryExpr(self, BinaryOp.NE, ConstantExpr(other))

    def __lt__(self, other: Any) -> "BinaryExpr":
        """< 运算符"""
        if isinstance(other, Expression):
            return BinaryExpr(self, BinaryOp.LT, other)
        return BinaryExpr(self, BinaryOp.LT, ConstantExpr(other))

    def __le__(self, other: Any) -> "BinaryExpr":
        """<= 运算符"""
        if isinstance(other, Expression):
            return BinaryExpr(self, BinaryOp.LE, other)
        return BinaryExpr(self, BinaryOp.LE, ConstantExpr(other))

    def __gt__(self, other: Any) -> "BinaryExpr":
        """> 运算符"""
        if isinstance(other, Expression):
            return BinaryExpr(self, BinaryOp.GT, other)
        return BinaryExpr(self, BinaryOp.GT, ConstantExpr(other))

    def __ge__(self, other: Any) -> "BinaryExpr":
        """>= 运算符"""
        if isinstance(other, Expression):
            return BinaryExpr(self, BinaryOp.GE, other)
        return BinaryExpr(self, BinaryOp.GE, ConstantExpr(other))

    def __add__(self, other: Any) -> "BinaryExpr":
        """+ 运算符"""
        if isinstance(other, Expression):
            return BinaryExpr(self, BinaryOp.ADD, other)
        return BinaryExpr(self, BinaryOp.ADD, ConstantExpr(other))

    def __sub__(self, other: Any) -> "BinaryExpr":
        """- 运算符"""
        if isinstance(other, Expression):
            return BinaryExpr(self, BinaryOp.SUB, other)
        return BinaryExpr(self, BinaryOp.SUB, ConstantExpr(other))

    def __mod__(self, other: Any) -> "BinaryExpr":
        """% 运算符"""
        if isinstance(other, Expression):
            return BinaryExpr(self, BinaryOp.MOD, other)
        return BinaryExpr(self, BinaryOp.MOD, ConstantExpr(other))

    def __repr__(self) -> str:
        return f"Var({self.name})"


class ConstantExpr(Expression):
    """
    常量表达式

    示例: 42, 3.14, "hello", True
    """

    def __init__(self, value: Any):
        self.value = value

    def eval(self, context: Dict[str, Any]) -> Any:
        return self.value

    def get_variables(self) -> List[str]:
        return []

    def __eq__(self, other: Any) -> "BinaryExpr":
        if isinstance(other, Expression):
            return BinaryExpr(self, BinaryOp.EQ, other)
        return BinaryExpr(self, BinaryOp.EQ, ConstantExpr(other))

    def __ne__(self, other: Any) -> "BinaryExpr":
        if isinstance(other, Expression):
            return BinaryExpr(self, BinaryOp.NE, other)
        return BinaryExpr(self, BinaryOp.NE, ConstantExpr(other))

    def __lt__(self, other: Any) -> "BinaryExpr":
        if isinstance(other, Expression):
            return BinaryExpr(self, BinaryOp.LT, other)
        return BinaryExpr(self, BinaryOp.LT, ConstantExpr(other))

    def __le__(self, other: Any) -> "BinaryExpr":
        if isinstance(other, Expression):
            return BinaryExpr(self, BinaryOp.LE, other)
        return BinaryExpr(self, BinaryOp.LE, ConstantExpr(other))

    def __gt__(self, other: Any) -> "BinaryExpr":
        if isinstance(other, Expression):
            return BinaryExpr(self, BinaryOp.GT, other)
        return BinaryExpr(self, BinaryOp.GT, ConstantExpr(other))

    def __ge__(self, other: Any) -> "BinaryExpr":
        if isinstance(other, Expression):
            return BinaryExpr(self, BinaryOp.GE, other)
        return BinaryExpr(self, BinaryOp.GE, ConstantExpr(other))

    def __repr__(self) -> str:
        return f"Const({self.value})"


class BinaryExpr(Expression):
    """
    二元运算表达式

    示例: x + y, x > 5, x && y
    """

    def __init__(self, left: Expression, op: BinaryOp, right: Expression):
        self.left = left
        self.op = op
        self.right = right

    def eval(self, context: Dict[str, Any]) -> Any:
        left_val = self.left.eval(context)
        right_val = self.right.eval(context)

        # 关系运算符
        if self.op == BinaryOp.EQ:
            return left_val == right_val
        elif self.op == BinaryOp.NE:
            return left_val != right_val
        elif self.op == BinaryOp.LT:
            return left_val < right_val
        elif self.op == BinaryOp.LE:
            return left_val <= right_val
        elif self.op == BinaryOp.GT:
            return left_val > right_val
        elif self.op == BinaryOp.GE:
            return left_val >= right_val

        # 逻辑运算符
        elif self.op == BinaryOp.AND:
            # 短路求值
            if not left_val:
                return False
            return bool(right_val)
        elif self.op == BinaryOp.OR:
            # 短路求值
            if left_val:
                return True
            return bool(right_val)
        elif self.op == BinaryOp.IMPLIES:
            # P -> Q 等价于 !P || Q
            return (not left_val) or right_val

        # 算术运算符
        elif self.op == BinaryOp.ADD:
            return left_val + right_val
        elif self.op == BinaryOp.SUB:
            return left_val - right_val
        elif self.op == BinaryOp.MUL:
            return left_val * right_val
        elif self.op == BinaryOp.DIV:
            if right_val == 0:
                raise ZeroDivisionError(f"Division by zero in expression: {self}")
            return left_val // right_val  # 整数除法
        elif self.op == BinaryOp.MOD:
            if right_val == 0:
                raise ZeroDivisionError(f"Modulo by zero in expression: {self}")
            return left_val % right_val

        # 位运算符
        elif self.op == BinaryOp.BIT_AND:
            return left_val & right_val
        elif self.op == BinaryOp.BIT_OR:
            return left_val | right_val
        elif self.op == BinaryOp.BIT_XOR:
            return left_val ^ right_val
        elif self.op == BinaryOp.SHIFT_LEFT:
            return left_val << right_val
        elif self.op == BinaryOp.SHIFT_RIGHT:
            return left_val >> right_val

        raise ValueError(f"Unknown operator: {self.op}")

    def get_variables(self) -> List[str]:
        return self.left.get_variables() + self.right.get_variables()

    def __repr__(self) -> str:
        return f"BinaryExpr({self.left} {self.op.value} {self.right})"


class UnaryExpr(Expression):
    """
    一元运算表达式

    示例: !x, -x, ~x
    """

    def __init__(self, op: str, expr: Expression):
        """
        Args:
            op: 运算符 ("!", "-", "~")
            expr: 操作数表达式
        """
        self.op = op
        self.expr = expr

    def eval(self, context: Dict[str, Any]) -> Any:
        val = self.expr.eval(context)

        if self.op == "!":
            return not val
        elif self.op == "-":
            return -val
        elif self.op == "~":
            return ~val

        raise ValueError(f"Unknown unary operator: {self.op}")

    def get_variables(self) -> List[str]:
        return self.expr.get_variables()

    def __repr__(self) -> str:
        return f"UnaryExpr({self.op}{self.expr})"


class SizeExpr(Expression):
    """
    size()函数表达式

    获取数组/列表的大小

    示例: arr.size()
    """

    def __init__(self, array_var: str):
        self.array_var = array_var

    def eval(self, context: Dict[str, Any]) -> Any:
        arr_val = context.get(self.array_var)
        if arr_val is None:
            return 0
        return len(arr_val)

    def get_variables(self) -> List[str]:
        return [self.array_var]

    def __repr__(self) -> str:
        return f"SizeExpr({self.array_var}.size())"


# 便捷函数


def var(name: str) -> VariableExpr:
    """创建变量表达式"""
    return VariableExpr(name)


def const(value: Any) -> ConstantExpr:
    """创建常量表达式"""
    return ConstantExpr(value)


def NOT(expr: Expression) -> UnaryExpr:
    """逻辑非 (!)"""
    return UnaryExpr("!", expr)


def NEG(expr: Expression) -> UnaryExpr:
    """算术负 (-)"""
    return UnaryExpr("-", expr)


def BIT_NOT(expr: Expression) -> UnaryExpr:
    """按位非 (~)"""
    return UnaryExpr("~", expr)
