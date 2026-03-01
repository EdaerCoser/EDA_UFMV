"""
RGM - Register Model System

EDA_UFMV寄存器模型系统（v0.3.0）

提供FPGA原型验证中的寄存器建模能力，支持：
- Field（字段）、Register（寄存器）、RegisterBlock（寄存器块）的层次化建模
- FrontDoor（前门访问）和BackDoor（后门访问）
- 硬件适配器（AXI、APB、UART、SSH等）
- 代码生成（Verilog RTL、C头文件、Python模型）
"""

from .core import Field, Register, RegisterBlock
from .core.field import AccessType
from .core.register_map import RegisterMap
from .access import FrontDoorAccess, BackDoorAccess
from .adapters import HardwareAdapter, AXIAdapter, APBAdapter, UARTAdapter, SSHAdapter
from .generators import CodeGenerator, VerilogGenerator, CHeaderGenerator, PythonGenerator, GeneratorFactory
from .api import register_block, register, field, sub_block, create_field, create_register

__version__ = "0.3.0"
__all__ = [
    # Core classes
    "Field",
    "Register",
    "RegisterBlock",
    "RegisterMap",
    "AccessType",
    # Access interfaces
    "FrontDoorAccess",
    "BackDoorAccess",
    # Hardware adapters
    "HardwareAdapter",
    "AXIAdapter",
    "APBAdapter",
    "UARTAdapter",
    "SSHAdapter",
    # Code generators
    "CodeGenerator",
    "VerilogGenerator",
    "CHeaderGenerator",
    "PythonGenerator",
    "GeneratorFactory",
    # Decorator API
    "register_block",
    "register",
    "field",
    "sub_block",
    "create_field",
    "create_register",
]
