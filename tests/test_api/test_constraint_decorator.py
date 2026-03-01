# tests/test_api/test_constraint_decorator.py
import pytest
from sv_randomizer import Randomizable
from sv_randomizer.api.annotations import rand, constraint

def test_simple_constraint():
    """测试简单约束"""
    x_rand = rand(int)(bits=8)

    class TestObj(Randomizable):
        x: x_rand

        @constraint
        def x_positive(self):
            return self.x > 0

    obj = TestObj()
    # 验证约束被注册
    assert obj.get_constraint('x_positive') is not None

    # 验证约束生效
    for _ in range(20):
        obj.randomize()
        assert obj.x > 0

def test_multiple_constraints():
    """测试多个约束"""
    x_rand = rand(int)(bits=8)
    y_rand = rand(int)(bits=8)

    class TestObj(Randomizable):
        x: x_rand
        y: y_rand

        @constraint
        def x_less_than_y(self):
            return self.x < self.y

        @constraint
        def sum_less_than_100(self):
            return self.x + self.y < 100

    obj = TestObj()
    for _ in range(20):
        obj.randomize()
        assert obj.x < obj.y
        assert obj.x + obj.y < 100

def test_and_constraint():
    """测试and逻辑"""
    x_rand = rand(int)(bits=8)

    class TestObj(Randomizable):
        x: x_rand

        @constraint
        def x_in_range(self):
            return self.x >= 10 and self.x <= 50

    obj = TestObj()
    for _ in range(20):
        obj.randomize()
        assert 10 <= obj.x <= 50
