"""
Core - RGM核心类

包含Field、Register、RegisterBlock和RegisterMap等核心类。
"""

from .field import Field, AccessType
from .register import Register
from .register_block import RegisterBlock
from .register_map import RegisterMap

__all__ = [
    "Field",
    "AccessType",
    "Register",
    "RegisterBlock",
    "RegisterMap",
]
