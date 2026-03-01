# tests/test_sv_to_python/test_parser.py
import pytest
from pathlib import Path

from sv_to_python.parser import SVParser

FIXTURE_DIR = Path(__file__).parent.parent / "fixtures"

def test_parser_basic():
    """测试基础解析功能"""
    parser = SVParser(FIXTURE_DIR / "simple_tasks.sv")
    source = parser.parse()

    assert source is not None
    assert len(source) > 0
    assert parser.source_text is not None

def test_get_tasks_simple():
    """测试提取简单tasks"""
    parser = SVParser(FIXTURE_DIR / "simple_tasks.sv")
    tasks = parser.get_tasks()

    assert len(tasks) >= 3
    assert "simple_write" in tasks
    assert "write_register" in tasks
    assert "multiple_ops" in tasks

def test_get_tasks_uvm():
    """测试提取UVM tasks"""
    parser = SVParser(FIXTURE_DIR / "uvm_tasks.sv")
    tasks = parser.get_tasks()

    assert len(tasks) >= 7
    assert "basic_write" in tasks
    assert "init_dma" in tasks

def test_task_params():
    """测试task参数提取"""
    parser = SVParser(FIXTURE_DIR / "uvm_tasks.sv")
    tasks = parser.get_tasks()

    init_dma = tasks["init_dma"]
    assert len(init_dma.parameters) == 3
    param_names = [p[0] for p in init_dma.parameters]
    assert "channel" in param_names
    assert "base_addr" in param_names
    assert "length" in param_names
