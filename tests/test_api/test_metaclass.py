# tests/test_api/test_metaclass.py
import pytest
from sv_randomizer import Randomizable
from sv_randomizer.api.annotations import rand, randc
from sv_randomizer.core.variables import RandVar, RandCVar, VarType

def test_metaclass_creates_rand_vars():
    """测试元类从类型注解创建RandVar"""
    # 使用变量存储注解，避免类型注解求值问题
    int_8_rand_v1 = rand(int)(bits=8)

    class TestClass1(Randomizable):
        value: int_8_rand_v1

    # 验证_rand_vars被正确创建
    assert 'value' in TestClass1._rand_vars
    assert isinstance(TestClass1._rand_vars['value'], RandVar)
    assert TestClass1._rand_vars['value'].bit_width == 8

def test_metaclass_creates_randc_vars():
    """测试元类从类型注解创建RandCVar"""
    int_4_randc_v1 = randc(int)(bits=4)

    class TestClass2(Randomizable):
        value: int_4_randc_v1

    # 验证_randc_vars被正确创建
    assert 'value' in TestClass2._randc_vars
    assert isinstance(TestClass2._randc_vars['value'], RandCVar)
    assert TestClass2._randc_vars['value'].bit_width == 4

def test_metaclass_with_min_max():
    """测试带min/max的变量"""
    int_16_rand_v2 = rand(int)(bits=16, min=100, max=200)

    class TestClass3(Randomizable):
        value: int_16_rand_v2

    var = TestClass3._rand_vars['value']
    assert var.min_val == 100
    assert var.max_val == 200

def test_metaclass_multiple_vars():
    """测试多个变量"""
    int_8_rand_v2 = rand(int)(bits=8)
    int_4_randc_v2 = randc(int)(bits=4)
    int_16_rand_v3 = rand(int)(bits=16, min=0, max=100)

    class TestClass4(Randomizable):
        a: int_8_rand_v2
        b: int_4_randc_v2
        c: int_16_rand_v3

    assert len(TestClass4._rand_vars) == 2
    assert len(TestClass4._randc_vars) == 1
    assert 'a' in TestClass4._rand_vars
    assert 'b' in TestClass4._randc_vars
    assert 'c' in TestClass4._rand_vars
