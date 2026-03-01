# tests/test_api/test_integration_basic.py
import pytest
from sv_randomizer import Randomizable, set_global_seed
from sv_randomizer.api.annotations import rand, randc

def test_basic_randomization():
    """测试基础随机化功能"""
    int_8_rand = rand(int)(bits=8)

    class TestObj(Randomizable):
        value: int_8_rand

    obj = TestObj()
    for _ in range(10):
        obj.randomize()
        assert 0 <= obj.value <= 255

def test_randc_randomization():
    """测试randc循环随机"""
    int_4_randc = randc(int)(bits=4)

    class TestObj(Randomizable):
        value: int_4_randc

    obj = TestObj()
    seen = set()
    for _ in range(16):
        obj.randomize()
        seen.add(obj.value)
        assert 0 <= obj.value <= 15

    # 4位randc应该产生16个唯一值
    assert len(seen) == 16

def test_multiple_variables():
    """测试多变量随机化"""
    int_8_rand = rand(int)(bits=8)
    int_16_rand = rand(int)(bits=16, min=1000, max=2000)
    int_2_randc = randc(int)(bits=2)

    class TestObj(Randomizable):
        a: int_8_rand
        b: int_16_rand
        c: int_2_randc

    obj = TestObj()
    obj.randomize()

    assert 0 <= obj.a <= 255
    assert 1000 <= obj.b <= 2000
    assert 0 <= obj.c <= 3

def test_seed_control():
    """测试seed控制"""
    int_8_rand = rand(int)(bits=8)

    class TestObj(Randomizable):
        value: int_8_rand

    set_global_seed(12345)
    obj1 = TestObj()
    obj1.randomize()
    val1 = obj1.value

    set_global_seed(12345)
    obj2 = TestObj()
    obj2.randomize()
    val2 = obj2.value

    assert val1 == val2

def test_instance_seed():
    """测试实例级seed"""
    int_8_rand = rand(int)(bits=8)

    class TestObj(Randomizable):
        value: int_8_rand

    obj = TestObj()
    obj.randomize(seed=42)
    val1 = obj.value

    obj.randomize(seed=42)
    val2 = obj.value

    assert val1 == val2
