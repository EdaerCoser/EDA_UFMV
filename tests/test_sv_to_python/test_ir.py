# tests/test_sv_to_python/test_ir.py
import pytest
from dataclasses import dataclass, field
from typing import List, Any

from sv_to_python.ir import (
    Operation, RegWrite, RegRead, RegSet, RegGet,
    RegReset, Comment, Todo
)

def test_reg_write_creation():
    """测试RegWrite创建"""
    op = RegWrite(
        line_no=10,
        original_source="model.REG.write(status, 32'h0001)",
        reg_path=['REG'],
        value=0x0001,
        backdoor=False
    )
    assert op.line_no == 10
    assert op.reg_path == ['REG']
    assert op.value == 0x0001
    assert op.backdoor is False

def test_reg_read_creation():
    """测试RegRead创建"""
    op = RegRead(
        line_no=20,
        original_source="model.REG.read(status, value)",
        reg_path=['REG'],
        backdoor=False
    )
    assert op.reg_path == ['REG']

def test_comment_creation():
    """测试Comment创建"""
    op = Comment(
        line_no=5,
        original_source="// Enable DMA",
        text="Enable DMA"
    )
    assert op.text == "Enable DMA"

def test_todo_creation():
    """测试Todo创建"""
    op = Todo(
        line_no=100,
        original_source="model.custom_method()",
        reason="Custom UVM extension method"
    )
    assert "Custom UVM extension" in op.reason
