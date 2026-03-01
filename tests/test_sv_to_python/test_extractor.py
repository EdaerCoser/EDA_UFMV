# tests/test_sv_to_python/test_extractor.py
import pytest
from pathlib import Path

from sv_to_python.parser import SVParser
from sv_to_python.extractor import UVMOperationExtractor
from sv_to_python.ir import RegWrite, RegRead

FIXTURE_DIR = Path(__file__).parent.parent / "fixtures"

def test_extract_basic_write():
    """测试提取基本write操作"""
    parser = SVParser(FIXTURE_DIR / "uvm_tasks.sv")
    tasks = parser.get_tasks()

    extractor = UVMOperationExtractor()
    task = tasks["basic_write"]
    operations = extractor.extract(task, parser.source_text)

    assert len(operations) == 1
    assert isinstance(operations[0], RegWrite)
    assert operations[0].reg_path == ['REG_NAME']
    assert operations[0].backdoor is False

def test_extract_backdoor_write():
    """测试提取backdoor write"""
    parser = SVParser(FIXTURE_DIR / "uvm_tasks.sv")
    tasks = parser.get_tasks()

    extractor = UVMOperationExtractor()
    task = tasks["backdoor_write"]
    operations = extractor.extract(task, parser.source_text)

    assert len(operations) == 1
    assert operations[0].backdoor is True

def test_extract_array_write():
    """测试提取数组write"""
    parser = SVParser(FIXTURE_DIR / "uvm_tasks.sv")
    tasks = parser.get_tasks()

    extractor = UVMOperationExtractor()
    task = tasks["array_write"]
    operations = extractor.extract(task, parser.source_text)

    assert len(operations) == 1
    # reg_model.REG_CH[channel].write(...)
    assert 'REG_CH' in operations[0].reg_path
    assert 'channel' in operations[0].reg_path

def test_extract_init_dma():
    """测试提取完整DMA初始化task"""
    parser = SVParser(FIXTURE_DIR / "uvm_tasks.sv")
    tasks = parser.get_tasks()

    extractor = UVMOperationExtractor()
    task = tasks["init_dma"]
    operations = extractor.extract(task, parser.source_text)

    # 应该有4个write操作
    write_ops = [op for op in operations if isinstance(op, RegWrite)]
    assert len(write_ops) == 4

    # 检查路径
    assert any('DMA_CTRL' in str(op.reg_path) for op in write_ops)
    assert any('DMA_ADDR' in str(op.reg_path) for op in write_ops)
