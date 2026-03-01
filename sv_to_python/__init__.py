# sv_to_python/__init__.py
"""
SV to Python - SystemVerilog到Python配置脚本转换器
"""

__version__ = "0.1.0"

# 导出主要类
from .parser import SVParser
from .extractor import UVMOperationExtractor
from .generator import PythonGenerator
from .ir import (
    Operation, RegWrite, RegRead, RegSet, RegGet,
    RegReset, RegRandomize, Comment, Todo, TaskInfo
)
from .errors import (
    ConversionError, ParseError, ExtractionError, GenerationError
)

__all__ = [
    'SVParser',
    'UVMOperationExtractor',
    'PythonGenerator',
    'Operation',
    'RegWrite',
    'RegRead',
    'RegSet',
    'RegGet',
    'RegReset',
    'RegRandomize',
    'Comment',
    'Todo',
    'TaskInfo',
    'ConversionError',
    'ParseError',
    'ExtractionError',
    'GenerationError'
]

