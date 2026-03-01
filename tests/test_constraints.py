"""
约束系统单元测试
"""

import sys
import os
import unittest

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sv_randomizer.constraints.expressions import (
    VariableExpr, ConstantExpr, BinaryExpr, UnaryExpr, BinaryOp
)
from sv_randomizer.constraints.builders import InsideConstraint, DistConstraint
from sv_randomizer.constraints.base import ExpressionConstraint


class TestExpressions(unittest.TestCase):
    """测试表达式系统"""

    def test_variable_expr(self):
        """测试变量表达式"""
        expr = VariableExpr("x")
        context = {"x": 42}
        self.assertEqual(expr.eval(context), 42)
        self.assertEqual(expr.get_variables(), ["x"])

    def test_constant_expr(self):
        """测试常量表达式"""
        expr = ConstantExpr(100)
        self.assertEqual(expr.eval({}), 100)
        self.assertEqual(expr.get_variables(), [])

    def test_binary_expr_arithmetic(self):
        """测试二元算术表达式"""
        left = ConstantExpr(10)
        right = ConstantExpr(5)

        add_expr = BinaryExpr(left, BinaryOp.ADD, right)
        self.assertEqual(add_expr.eval({}), 15)

        sub_expr = BinaryExpr(left, BinaryOp.SUB, right)
        self.assertEqual(sub_expr.eval({}), 5)

        mul_expr = BinaryExpr(left, BinaryOp.MUL, right)
        self.assertEqual(mul_expr.eval({}), 50)

    def test_binary_expr_relational(self):
        """测试关系表达式"""
        left = ConstantExpr(10)
        right = ConstantExpr(5)

        gt_expr = BinaryExpr(left, BinaryOp.GT, right)
        self.assertTrue(gt_expr.eval({}))

        lt_expr = BinaryExpr(left, BinaryOp.LT, right)
        self.assertFalse(lt_expr.eval({}))

        eq_expr = BinaryExpr(ConstantExpr(5), BinaryOp.EQ, right)
        self.assertTrue(eq_expr.eval({}))

    def test_binary_expr_logical(self):
        """测试逻辑表达式"""
        t = ConstantExpr(True)
        f = ConstantExpr(False)

        and_expr = BinaryExpr(t, BinaryOp.AND, t)
        self.assertTrue(and_expr.eval({}))

        and_expr2 = BinaryExpr(t, BinaryOp.AND, f)
        self.assertFalse(and_expr2.eval({}))

        or_expr = BinaryExpr(t, BinaryOp.OR, f)
        self.assertTrue(or_expr.eval({}))

    def test_implication(self):
        """测试蕴含运算 (P -> Q 等价于 !P || Q)"""
        # True -> True = True
        expr1 = BinaryExpr(ConstantExpr(True), BinaryOp.IMPLIES, ConstantExpr(True))
        self.assertTrue(expr1.eval({}))

        # True -> False = False
        expr2 = BinaryExpr(ConstantExpr(True), BinaryOp.IMPLIES, ConstantExpr(False))
        self.assertFalse(expr2.eval({}))

        # False -> True = True (前件为假，蕴含成立)
        expr3 = BinaryExpr(ConstantExpr(False), BinaryOp.IMPLIES, ConstantExpr(True))
        self.assertTrue(expr3.eval({}))

        # False -> False = True
        expr4 = BinaryExpr(ConstantExpr(False), BinaryOp.IMPLIES, ConstantExpr(False))
        self.assertTrue(expr4.eval({}))

    def test_unary_expr(self):
        """测试一元表达式"""
        # 逻辑非
        not_expr = UnaryExpr("!", ConstantExpr(True))
        self.assertFalse(not_expr.eval({}))

        # 算术负
        neg_expr = UnaryExpr("-", ConstantExpr(42))
        self.assertEqual(neg_expr.eval({}), -42)

    def test_expr_with_variables(self):
        """测试带变量的表达式"""
        x = VariableExpr("x")
        y = VariableExpr("y")

        # x + y
        add_expr = BinaryExpr(x, BinaryOp.ADD, y)
        context = {"x": 10, "y": 20}
        self.assertEqual(add_expr.eval(context), 30)

        # x > 5
        gt_expr = BinaryExpr(x, BinaryOp.GT, ConstantExpr(5))
        context = {"x": 10}
        self.assertTrue(gt_expr.eval(context))


class TestInsideConstraint(unittest.TestCase):
    """测试inside约束"""

    def test_single_range(self):
        """测试单个范围"""
        constraint = InsideConstraint("test", "x", [(0, 100)])

        # 测试满足约束的值
        self.assertTrue(constraint.check({"x": 50}))
        self.assertTrue(constraint.check({"x": 0}))
        self.assertTrue(constraint.check({"x": 100}))

        # 测试不满足的值
        self.assertFalse(constraint.check({"x": -1}))
        self.assertFalse(constraint.check({"x": 101}))

    def test_multiple_ranges(self):
        """测试多个范围"""
        constraint = InsideConstraint("test", "x", [(0, 10), (50, 60), 100])

        self.assertTrue(constraint.check({"x": 5}))
        self.assertTrue(constraint.check({"x": 55}))
        self.assertTrue(constraint.check({"x": 100}))

        self.assertFalse(constraint.check({"x": 20}))
        self.assertFalse(constraint.check({"x": 70}))

    def test_get_allowed_values(self):
        """测试获取允许值列表"""
        # 小范围
        constraint = InsideConstraint("test", "x", [(0, 2), 5])
        values = constraint.get_allowed_values()

        self.assertEqual(len(values), 4)  # 0, 1, 2, 5
        self.assertIn(0, values)
        self.assertIn(1, values)
        self.assertIn(2, values)
        self.assertIn(5, values)

        # 大范围应返回空列表
        large_constraint = InsideConstraint("test", "x", [(0, 2000)])
        large_values = large_constraint.get_allowed_values()
        self.assertEqual(len(large_values), 0)


class TestDistConstraint(unittest.TestCase):
    """测试dist权重约束"""

    def test_sampling(self):
        """测试权重采样"""
        # 简单权重: 0和1各50%
        constraint = DistConstraint("test", "x", {0: 50, 1: 50})

        values = []
        for _ in range(100):
            val = constraint.sample()
            self.assertIn(val, [0, 1])
            values.append(val)

        # 检查两者都有出现
        self.assertIn(0, values)
        self.assertIn(1, values)

    def test_range_sampling(self):
        """测试范围采样"""
        constraint = DistConstraint("test", "x", {
            0: 10,       # 10% 权重
            (1, 10): 30, # 30% 权重
            (11, 20): 60 # 60% 权重
        })

        values = []
        for _ in range(100):
            val = constraint.sample()
            self.assertGreaterEqual(val, 0)
            self.assertLessEqual(val, 20)
            values.append(val)

        # 检查采样值在正确的范围内
        in_range1 = sum(1 for v in values if v == 0)
        in_range2 = sum(1 for v in values if 1 <= v <= 10)
        in_range3 = sum(1 for v in values if 11 <= v <= 20)

        # 第三个范围应该最多
        self.assertGreater(in_range3, in_range2)
        self.assertGreater(in_range3, in_range1)

    def test_get_weight(self):
        """测试获取权重"""
        constraint = DistConstraint("test", "x", {
            0: 10,
            (1, 10): 30,
            (11, 20): 60
        })

        self.assertEqual(constraint.get_weight(0), 10)
        self.assertEqual(constraint.get_weight(5), 30)  # 在范围(1, 10)内
        self.assertEqual(constraint.get_weight(15), 60)  # 在范围(11, 20)内
        self.assertEqual(constraint.get_weight(100), 0)  # 不在任何范围内


class TestExpressionConstraint(unittest.TestCase):
    """测试表达式约束"""

    def test_basic_constraint(self):
        """测试基本约束"""
        expr = BinaryExpr(VariableExpr("x"), BinaryOp.GT, ConstantExpr(10))
        constraint = ExpressionConstraint("test", expr)

        self.assertTrue(constraint.check({"x": 20}))
        self.assertFalse(constraint.check({"x": 5}))

    def test_enable_disable(self):
        """测试启用/禁用"""
        expr = BinaryExpr(VariableExpr("x"), BinaryOp.GT, ConstantExpr(10))
        constraint = ExpressionConstraint("test", expr)

        self.assertTrue(constraint.is_enabled())
        self.assertTrue(constraint.check({"x": 20}))

        constraint.disable()
        self.assertFalse(constraint.is_enabled())
        # 禁用后总是返回True
        self.assertTrue(constraint.check({"x": 5}))

        constraint.enable()
        self.assertTrue(constraint.is_enabled())
        self.assertFalse(constraint.check({"x": 5}))


if __name__ == "__main__":
    unittest.main()
