# sv_to_python/ir.py
"""
中间表示 - 操作序列定义
"""
from dataclasses import dataclass, field
from typing import List, Any, Optional

@dataclass
class Operation:
    """操作基类"""
    line_no: int
    original_source: str

@dataclass
class RegWrite(Operation):
    """寄存器写入操作"""
    reg_path: List[str]   # ['DMA_BLOCK', 'channel', 'ch', 'ctrl']
    value: Any
    backdoor: bool = False

@dataclass
class RegRead(Operation):
    """寄存器读取操作"""
    reg_path: List[str]
    backdoor: bool = False

@dataclass
class RegSet(Operation):
    """设置模型值（不写硬件）"""
    reg_path: List[str]
    value: Any

@dataclass
class RegGet(Operation):
    """获取模型值（不读硬件）"""
    reg_path: List[str]

@dataclass
class RegReset(Operation):
    """复位寄存器"""
    reg_path: List[str]
    kind: str = "HARD"

@dataclass
class RegRandomize(Operation):
    """随机化寄存器"""
    reg_path: List[str]
    constraints: Optional[List[str]] = None

@dataclass
class Comment(Operation):
    """注释"""
    text: str

@dataclass
class Todo(Operation):
    """需要手动实现的操作"""
    reason: str

@dataclass
class TaskInfo:
    """Task分析结果"""
    name: str
    parameters: List[tuple]  # (name, type) tuples
    operations: List[Operation]
    line_no: int = 0
