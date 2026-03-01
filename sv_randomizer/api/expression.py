# sv_randomizer/api/expression.py
"""
Python表达式AST转换器

将原生Python表达式转换为框架的Expression AST
"""
import ast
from ..constraints.expressions import (
    BinaryExpr, BinaryOp, UnaryExpr,
    VariableExpr, ConstantExpr, Expression
)


class PythonExpressionConverter(ast.NodeVisitor):
    """
    Python AST → Expression AST 转换器

    支持的Python语法：
    - 比较运算: ==, !=, <, >, <=, >=
    - 逻辑运算: and, or, not
    - 算术运算: +, -, *, /, %, **
    - 位运算: &, |, ^, ~, <<, >>
    - 属性访问: self.xxx
    - 常量: 数字, 字符串, 布尔值
    """

    def __init__(self, instance):
        """
        Args:
            instance: Randomizable实例（用于验证属性名）
        """
        self.instance = instance

    def visit(self, node):
        """入口方法"""
        if node is None:
            return ConstantExpr(None)
        return super().visit(node)

    def visit_Compare(self, node):
        """
        处理比较运算

        支持链式比较: a < x < b → (a < x) and (x < b)
        """
        left = self.visit(node.left)

        # 处理链式比较
        if len(node.comparators) > 1:
            # a op1 b op2 c → (a op1 b) and (b op2 c)
            result = BinaryExpr(
                left,
                self._convert_cmp_op(node.ops[0]),
                self.visit(node.comparators[0])
            )

            for i in range(1, len(node.comparators)):
                next_left = self.visit(node.comparators[i-1])
                next_right = self.visit(node.comparators[i])
                next_op = self._convert_cmp_op(node.ops[i])

                next_expr = BinaryExpr(next_left, next_op, next_right)
                result = BinaryExpr(result, BinaryOp.AND, next_expr)

            return result

        # 单个比较
        op = self._convert_cmp_op(node.ops[0])
        right = self.visit(node.comparators[0])
        return BinaryExpr(left, op, right)

    def visit_BoolOp(self, node):
        """处理逻辑运算: and, or"""
        if isinstance(node.op, ast.And):
            op = BinaryOp.AND
        elif isinstance(node.op, ast.Or):
            op = BinaryOp.OR
        else:
            raise ValueError(f"Unsupported boolean operator: {type(node.op)}")

        result = self.visit(node.values[0])
        for value in node.values[1:]:
            result = BinaryExpr(result, op, self.visit(value))
        return result

    def visit_UnaryOp(self, node):
        """处理一元运算: not, -, ~"""
        op = self._convert_unary_op(node.op)
        operand = self.visit(node.operand)
        return UnaryExpr(op, operand)

    def visit_BinOp(self, node):
        """处理二元运算: +, -, *, /, %, etc."""
        left = self.visit(node.left)
        op = self._convert_bin_op(node.op)
        right = self.visit(node.right)
        return BinaryExpr(left, op, right)

    def visit_Attribute(self, node):
        """
        处理属性访问: self.xxx

        只支持self.xxx形式，不支持嵌套属性
        """
        if isinstance(node.value, ast.Name) and node.value.id == 'self':
            # 验证属性是否存在
            attr_name = node.attr
            if not hasattr(self.instance, attr_name):
                raise AttributeError(
                    f"'{self.instance.__class__.__name__}' has no attribute '{attr_name}'"
                )
            return VariableExpr(attr_name)

        raise ValueError(
            f"Only 'self.xxx' attributes are supported, got: {ast.dump(node)}"
        )

    def visit_Name(self, node):
        """处理变量名: True, False, None"""
        if node.id == 'True':
            return ConstantExpr(True)
        elif node.id == 'False':
            return ConstantExpr(False)
        elif node.id == 'None':
            return ConstantExpr(None)
        else:
            # 其他名称作为变量处理
            return VariableExpr(node.id)

    def visit_Constant(self, node):
        """处理常量: 数字, 字符串, 布尔值"""
        return ConstantExpr(node.value)

    def visit_Num(self, node):
        """Python 3.7兼容: 处理数字常量"""
        return ConstantExpr(node.n)

    def visit_Str(self, node):
        """Python 3.7兼容: 处理字符串常量"""
        return ConstantExpr(node.s)

    def visit_NameConstant(self, node):
        """Python 3.7兼容: 处理True/False/None"""
        return ConstantExpr(node.value)

    def _convert_cmp_op(self, op) -> BinaryOp:
        """转换Python比较运算符到BinaryOp"""
        mapping = {
            ast.Eq: BinaryOp.EQ,
            ast.NotEq: BinaryOp.NE,
            ast.Lt: BinaryOp.LT,
            ast.LtE: BinaryOp.LE,
            ast.Gt: BinaryOp.GT,
            ast.GtE: BinaryOp.GE,
        }
        op_type = type(op)
        if op_type not in mapping:
            raise ValueError(f"Unsupported comparison operator: {op_type}")
        return mapping[op_type]

    def _convert_bin_op(self, op) -> BinaryOp:
        """转换Python二元运算符到BinaryOp"""
        mapping = {
            ast.Add: BinaryOp.ADD,
            ast.Sub: BinaryOp.SUB,
            ast.Mult: BinaryOp.MUL,
            ast.Div: BinaryOp.DIV,
            ast.Mod: BinaryOp.MOD,
            ast.FloorDiv: BinaryOp.DIV,
            ast.BitAnd: BinaryOp.BIT_AND,
            ast.BitOr: BinaryOp.BIT_OR,
            ast.BitXor: BinaryOp.BIT_XOR,
            ast.LShift: BinaryOp.SHIFT_LEFT,
            ast.RShift: BinaryOp.SHIFT_RIGHT,
        }
        op_type = type(op)
        if op_type not in mapping:
            raise ValueError(f"Unsupported binary operator: {op_type}")
        return mapping[op_type]

    def _convert_unary_op(self, op) -> str:
        """转换Python一元运算符到字符串"""
        mapping = {
            ast.Not: "!",
            ast.USub: "-",
            ast.UAdd: "+",
            ast.Invert: "~",
        }
        op_type = type(op)
        if op_type not in mapping:
            raise ValueError(f"Unsupported unary operator: {op_type}")
        return mapping[op_type]


def parse_python_expression(source_code: str, instance) -> Expression:
    """
    将Python表达式字符串转换为框架Expression对象

    Args:
        source_code: Python表达式代码（如 "self.x > 0 and self.y < 100"）
        instance: Randomizable实例（用于属性验证）

    Returns:
        Expression对象

    Raises:
        ValueError: 表达式语法不支持
        SyntaxError: 表达式语法错误
    """
    # 解析为AST
    try:
        tree = ast.parse(source_code, mode='eval')
    except SyntaxError as e:
        raise SyntaxError(f"Invalid Python expression: {e}")

    # 转换为Expression
    converter = PythonExpressionConverter(instance)
    try:
        return converter.visit(tree.body)
    except Exception as e:
        raise ValueError(f"Failed to convert expression: {e}")


__all__ = ['PythonExpressionConverter', 'parse_python_expression']
