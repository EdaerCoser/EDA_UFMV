"""
RGM Decorator API

提供装饰器API用于定义寄存器模型，与sv_randomizer和coverage模块风格一致。

Usage:
    @register_block("UART", base_address=0x40000000)
    class UARTBlock:
        @register("CTRL", offset=0x00, width=32)
        class ctrl_reg:
            @field(bit_offset=0, bit_width=1, access=AccessType.RW)
            def enable(self):
                return 1  # reset value
"""

from functools import wraps
from typing import Any, Callable, Dict, List, Optional, Union

from ..core.register_block import RegisterBlock
from ..core.register import Register
from ..core.field import Field, AccessType


def register_block(
    name: str,
    base_address: int,
    description: str = ""
):
    """
    装饰器：定义RegisterBlock

    对应SystemVerilog:
        module UART_BLOCK #(base_address = 0x40000000);
            // registers and sub-blocks
        endmodule

    Args:
        name: 寄存器块名称
        base_address: 基地址
        description: 描述信息

    Returns:
        装饰器函数

    Example:
        @register_block("UART", base_address=0x40000000)
        class UARTBlock:
            @register("CTRL", offset=0x00, width=32)
            class ctrl:
                @field(bit_offset=0, bit_width=1, access=AccessType.RW)
                def enable(self):
                    return 1

            @register("STATUS", offset=0x04, width=32)
            class status:
                @field(bit_offset=0, bit_width=1, access=AccessType.RO)
                def ready(self):
                    return 0
    """
    def decorator(cls):
        # 创建RegisterBlock子类
        class RegisterBlockWrapper(RegisterBlock):
            def __init__(self):
                super().__init__(name=name, base_address=base_address)

                # 从类定义初始化成员
                self._initialize_members(cls)

        # 保留类元数据
        RegisterBlockWrapper.__name__ = cls.__name__
        RegisterBlockWrapper.__doc__ = cls.__doc__
        RegisterBlockWrapper.__module__ = cls.__module__

        return RegisterBlockWrapper

    return decorator


def register(
    name: str,
    offset: int,
    width: int = 32,
    reset_value: int = 0,
    access: Optional[AccessType] = None,
    description: str = ""
):
    """
    装饰器：在RegisterBlock中定义Register

    对应SystemVerilog:
        logic [width-1:0] name @ offset;

    Args:
        name: 寄存器名称
        offset: 相对于RegisterBlock的偏移地址
        width: 寄存器位宽（默认32）
        reset_value: 复位值（默认0）
        access: 默认访问类型（应用于所有字段）
        description: 描述信息

    Returns:
        装饰器函数

    Example:
        @register("CTRL", offset=0x00, width=32)
        class ctrl_reg:
            @field(bit_offset=0, bit_width=1, access=AccessType.RW, reset_value=1)
            def enable(self):
                pass

            @field(bit_offset=1, bit_width=3, access=AccessType.RW)
            def mode(self):
                return 0
    """
    def decorator(inner_cls):
        # 存储寄存器元数据
        inner_cls._rgm_register_meta = {
            'name': name,
            'offset': offset,
            'width': width,
            'reset_value': reset_value,
            'access': access,
            'description': description,
            'fields': []
        }

        # 收集所有字段定义
        for attr_name, attr_value in inner_cls.__dict__.items():
            if hasattr(attr_value, '_rgm_field_meta'):
                field_meta = attr_value._rgm_field_meta
                field_meta['name'] = attr_name
                inner_cls._rgm_register_meta['fields'].append(field_meta)

        # 包装类，使其在RegisterBlock初始化时被识别
        class RegisterWrapper:
            def __init__(self, parent_block):
                # 创建Register实例
                reg = Register(
                    name=name,
                    offset=offset,
                    width=width,
                    reset_value=reset_value,
                    description=description
                )

                # 添加所有字段
                for field_meta in inner_cls._rgm_register_meta['fields']:
                    field_access = field_meta.get('access') or access or AccessType.RW
                    field = Field(
                        name=field_meta['name'],
                        bit_offset=field_meta['bit_offset'],
                        bit_width=field_meta['bit_width'],
                        access=field_access,
                        reset_value=field_meta.get('reset_value', 0),
                        volatile=field_meta.get('volatile', False),
                        description=field_meta.get('description', '')
                    )
                    reg.add_field(field)

                # 将寄存器添加到父块
                parent_block.add_register(reg)

                # 存储引用，便于后续访问
                self._register = reg

            def __getattr__(self, item):
                return getattr(self._register, item)

        RegisterWrapper.__name__ = inner_cls.__name__
        RegisterWrapper._rgm_is_register = True
        RegisterWrapper._rgm_meta = inner_cls._rgm_register_meta

        return RegisterWrapper

    return decorator


def field(
    bit_offset: int,
    bit_width: int,
    access: AccessType = AccessType.RW,
    reset_value: int = 0,
    volatile: bool = False,
    description: str = ""
):
    """
    装饰器：定义Field（寄存器字段）

    对应SystemVerilog:
        bit [bit_offset + bit_width - 1 : bit_offset] field_name;

    Args:
        bit_offset: 字段在寄存器中的位偏移
        bit_width: 字段位宽
        access: 访问类型（默认RW）
        reset_value: 复位值（默认0）
        volatile: 是否为易失性字段
        description: 描述信息

    Returns:
        装饰器函数

    Example:
        @field(bit_offset=0, bit_width=1, access=AccessType.RW, reset_value=1)
        def enable(self):
            pass  # 返回值由reset_value参数指定

        @field(bit_offset=8, bit_width=4, access=AccessType.RO)
        def status(self):
            return 0xF  # 也可以在函数中返回复位值
    """
    def decorator(func: Callable) -> property:
        # 存储字段元数据
        func._rgm_field_meta = {
            'bit_offset': bit_offset,
            'bit_width': bit_width,
            'access': access,
            'reset_value': reset_value,
            'volatile': volatile,
            'description': description
        }

        @wraps(func)
        def wrapper(self):
            # 这个包装器主要用于存储元数据
            # 实际的Field对象会在@register装饰器中创建
            return func(self)

        return wrapper

    return decorator


# 子块装饰器（用于层次化组织）

def sub_block(
    name: str,
    offset: int,
    block_class: Optional[type] = None
):
    """
    装饰器：在RegisterBlock中定义子块

    用于创建层次化的寄存器结构。

    Args:
        name: 子块名称
        offset: 相对于父块的偏移地址
        block_class: 可选的RegisterBlock类（用于复用）

    Returns:
        装饰器函数

    Example:
        @register_block("SYSTEM", base_address=0x40000000)
        class SystemBlock:
            @sub_block("UART", offset=0x1000)
            class uart:
                @register("CTRL", offset=0x00, width=32)
                class ctrl:
                    @field(bit_offset=0, bit_width=1, access=AccessType.RW)
                    def enable(self):
                        return 1
    """
    def decorator(inner_cls):
        # 如果block_class未指定，创建新的RegisterBlock
        if block_class is None:
            block_class = type(
                inner_cls.__name__,
                (RegisterBlock,),
                {
                    '__module__': inner_cls.__module__,
                    '__doc__': inner_cls.__doc__,
                }
            )

        # 包装类，使其在RegisterBlock初始化时被识别
        class SubBlockWrapper:
            def __init__(self, parent_block):
                # 创建子块实例
                sub_block = RegisterBlock(name=name, base_address=offset)
                sub_block._parent_block = parent_block

                # 将子块添加到父块
                parent_block.add_block(sub_block)

                # 存储引用
                self._sub_block = sub_block

            def __getattr__(self, item):
                return getattr(self._sub_block, item)

        SubBlockWrapper.__name__ = inner_cls.__name__
        SubBlockWrapper._rgm_is_sub_block = True
        SubBlockWrapper._rgm_meta = {
            'name': name,
            'offset': offset,
            'block_class': block_class
        }

        return SubBlockWrapper

    return decorator


# 便捷函数

def create_field(
    name: str,
    bit_offset: int,
    bit_width: int,
    access: AccessType = AccessType.RW,
    reset_value: int = 0,
    **kwargs
) -> Field:
    """
    便捷函数：创建Field实例

    Args:
        name: 字段名称
        bit_offset: 位偏移
        bit_width: 位宽
        access: 访问类型
        reset_value: 复位值
        **kwargs: 其他Field参数

    Returns:
        Field实例
    """
    return Field(
        name=name,
        bit_offset=bit_offset,
        bit_width=bit_width,
        access=access,
        reset_value=reset_value,
        **kwargs
    )


def create_register(
    name: str,
    offset: int,
    width: int = 32,
    reset_value: int = 0,
    fields: Optional[List[Field]] = None,
    **kwargs
) -> Register:
    """
    便捷函数：创建Register实例

    Args:
        name: 寄存器名称
        offset: 偏移地址
        width: 位宽
        reset_value: 复位值
        fields: 字段列表
        **kwargs: 其他Register参数

    Returns:
        Register实例
    """
    reg = Register(
        name=name,
        offset=offset,
        width=width,
        reset_value=reset_value,
        **kwargs
    )

    if fields:
        for field in fields:
            reg.add_field(field)

    return reg
