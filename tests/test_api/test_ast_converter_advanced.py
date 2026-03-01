# tests/test_api/test_ast_converter_advanced.py
import pytest
from sv_randomizer.api.expression import parse_python_expression
from sv_randomizer.constraints.expressions import BinaryExpr, BinaryOp, UnaryExpr

class MockInstance:
    def __init__(self):
        self.x = 10
        self.y = 20
        self.z = 5

def test_modulo_operator():
    """测试取模运算: self.x % 2 == 0"""
    expr = parse_python_expression("self.x % 2 == 0", MockInstance())
    assert expr.op == BinaryOp.EQ

def test_bitwise_operators():
    """测试位运算"""
    expr = parse_python_expression("self.x & 0xFF", MockInstance())
    assert expr.op == BinaryOp.BIT_AND

def test_complex_expression():
    """测试复杂表达式: (self.x + self.y) * 2 > self.z"""
    expr = parse_python_expression("(self.x + self.y) * 2 > self.z", MockInstance())
    assert expr.op == BinaryOp.GT

def test_not_operator():
    """测试not运算: not (self.x > 100)"""
    expr = parse_python_expression("not (self.x > 100)", MockInstance())
    # not会被转换为UnaryExpr，使用字符串op
    assert isinstance(expr, UnaryExpr)
    assert expr.op == "!"

def test_or_operator():
    """测试or运算: self.x < 0 or self.x > 100"""
    expr = parse_python_expression("self.x < 0 or self.x > 100", MockInstance())
    assert expr.op == BinaryOp.OR

def test_negation_operator():
    """测试负号运算: -self.x"""
    expr = parse_python_expression("-self.x", MockInstance())
    assert isinstance(expr, UnaryExpr)
    assert expr.op == "-"

def test_bitwise_not():
    """测试位取反运算: ~self.x"""
    expr = parse_python_expression("~self.x", MockInstance())
    assert isinstance(expr, UnaryExpr)
    assert expr.op == "~"
