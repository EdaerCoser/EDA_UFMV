# tests/test_sv_to_python/test_cli.py
import pytest
import subprocess
import sys
import tempfile
from pathlib import Path

FIXTURE_DIR = Path(__file__).parent.parent / "fixtures"

def test_cli_help():
    """测试CLI帮助"""
    result = subprocess.run(
        [sys.executable, "-m", "sv_to_python", "--help"],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0
    assert "convert" in result.stdout
    assert "list" in result.stdout

def test_cli_list_tasks():
    """测试list命令"""
    result = subprocess.run(
        [sys.executable, "-m", "sv_to_python", "list",
         str(FIXTURE_DIR / "uvm_tasks.sv")],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0
    assert "init_dma" in result.stdout
    assert "basic_write" in result.stdout

def test_cli_convert():
    """测试convert命令"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        output_file = f.name

    try:
        result = subprocess.run(
            [sys.executable, "-m", "sv_to_python", "convert",
             str(FIXTURE_DIR / "uvm_tasks.sv"),
             "-o", output_file],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0

        # 检查输出文件
        content = Path(output_file).read_text()
        assert "def init_dma(" in content
        assert "dma_ctrl" in content.lower()
    finally:
        Path(output_file).unlink()
