# tests/test_api/test_ast_converter.py
import pytest
from sv_randomizer.api.expression import parse_python_expression
from sv_randomizer.constraints.expressions import (
    BinaryExpr, BinaryOp, VariableExpr, ConstantExpr
)

class MockInstance:
    """模拟Randomizable实例"""
    def __init__(self):
        self.x = 10
        self.y = 20

def test_parse_simple_comparison():
    """测试解析简单比较: self.x > 0"""
    instance = MockInstance()
    expr = parse_python_expression("self.x > 0", instance)

    assert isinstance(expr, BinaryExpr)
    assert isinstance(expr.left, VariableExpr)
    assert expr.left.name == "x"
    assert expr.op == BinaryOp.GT
    assert isinstance(expr.right, ConstantExpr)
    assert expr.right.value == 0

def test_parse_logical_and():
    """测试解析逻辑与: self.x > 0 and self.y < 100"""
    instance = MockInstance()
    expr = parse_python_expression("self.x > 0 and self.y < 100", instance)

    assert isinstance(expr, BinaryExpr)
    assert expr.op == BinaryOp.AND
    assert isinstance(expr.left, BinaryExpr)
    assert isinstance(expr.right, BinaryExpr)

def test_parse_arithmetic():
    """测试解析算术运算: self.x + self.y < 100"""
    instance = MockInstance()
    expr = parse_python_expression("self.x + self.y < 100", instance)

    # 应该解析为: (x + y) < 100
    assert isinstance(expr, BinaryExpr)
    assert expr.op == BinaryOp.LT

def test_parse_chained_comparison():
    """测试链式比较: 0 <= self.x <= 100"""
    instance = MockInstance()
    expr = parse_python_expression("0 <= self.x <= 100", instance)

    # 应该解析为: 0 <= x and x <= 100
    assert isinstance(expr, BinaryExpr)
    assert expr.op == BinaryOp.AND
