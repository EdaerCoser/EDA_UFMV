"""
RGM API Package

寄存器模型系统的用户API层。
"""

from .decorators import (
    register_block,
    register,
    field,
    sub_block,
    create_field,
    create_register,
)

__all__ = [
    # Decorators
    "register_block",
    "register",
    "field",
    "sub_block",
    # Convenience functions
    "create_field",
    "create_register",
]
