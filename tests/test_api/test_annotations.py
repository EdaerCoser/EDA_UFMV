# tests/test_api/test_annotations.py
import pytest
from typing import get_type_hints, Annotated
from sv_randomizer.api.annotations import Rand, RandC, RandEnum, rand, randc

def test_rand_class():
    """测试Rand类"""
    rand_meta = Rand(bits=16, min=0x1000, max=0xFFFF)
    assert rand_meta.bits == 16
    assert rand_meta.min == 0x1000
    assert rand_meta.max == 0xFFFF

def test_randc_class():
    """测试RandC类"""
    randc_meta = RandC(bits=4)
    assert randc_meta.bits == 4

def test_rand_enum_class():
    """测试RandEnum类"""
    enum_meta = RandEnum("READ", "WRITE", "ACK")
    assert enum_meta.values == ["READ", "WRITE", "ACK"]

def test_rand_builder_syntax():
    """测试rand[int](bits=16)语法"""
    # rand[int] 返回一个builder
    builder = rand(int)
    # builder(**kwargs) 返回 Annotated[int, Rand(...)]
    annotation = builder(bits=16)

    # 验证结构
    assert hasattr(annotation, '__metadata__')
    metadata = annotation.__metadata__[0]
    assert isinstance(metadata, Rand)
    assert metadata.bits == 16

def test_randc_builder_syntax():
    """测试randc[int](bits=4)语法"""
    builder = randc(int)
    annotation = builder(bits=4)

    assert hasattr(annotation, '__metadata__')
    metadata = annotation.__metadata__[0]
    assert isinstance(metadata, RandC)
    assert metadata.bits == 4
