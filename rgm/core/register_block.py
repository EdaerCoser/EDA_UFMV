"""
RegisterBlock - 寄存器块类

支持层次化组织的寄存器容器，对应UVM的uvm_reg_block。
"""

from typing import Dict, List, Optional, Union
from .register import Register
from .field import Field, AccessType
from .register_map import RegisterMap


class RegisterBlock:
    """
    寄存器块

    对应SystemVerilog的模块定义和UVM的uvm_reg_block。

    SystemVerilog示例:
        module Peripherals @(0x4000_0000);
            logic [31:0] ctrl_reg;    // @0x00
            logic [31:0] status_reg;  // @0x04
        endmodule

    Args:
        name: 寄存器块名称
        base_address: 基地址
        description: 寄存器块描述

    Example:
        >>> block = RegisterBlock("UART", base_address=0x4000_0000)
        >>> ctrl = Register("CTRL", 0x00)
        >>> ctrl.add_field(Field("enable", 0, 1, AccessType.RW, 0))
        >>> block.add_register(ctrl)
        >>> status = Register("STATUS", 0x04)
        >>> block.add_register(status)
    """

    def __init__(
        self, name: str, base_address: int = 0, description: str = ""
    ):
        self.name = name
        self.base_address = base_address
        self.description = description

        # 层次化组织
        self._registers: Dict[str, Register] = {}
        self._blocks: Dict[str, "RegisterBlock"] = {}
        self._address_map: Dict[int, Union[Register, "RegisterBlock"]] = {}

        # UVM风格：默认映射和访问接口
        self._default_map: Optional[RegisterMap] = None
        self._backdoor = None  # 后门访问接口
        self._frontdoor = None  # 前门访问接口
        self._default_access = None

        # 创建默认映射
        self._default_map = RegisterMap(f"{name}_map", base_address)

    def _initialize_members(self, cls: type) -> None:
        """
        从装饰器类定义初始化成员（寄存器和子块）

        这个方法由装饰器API使用，用于处理类定义中的寄存器和子块。

        Args:
            cls: 使用@register_block等装饰器的类
        """
        for attr_name, attr_value in cls.__dict__.items():
            # 处理register包装器
            if hasattr(attr_value, '_rgm_is_register'):
                # 创建Register实例并添加
                meta = attr_value._rgm_meta
                reg = Register(
                    name=meta['name'],
                    offset=meta['offset'],
                    width=meta['width'],
                    reset_value=meta['reset_value'],
                    description=meta.get('description', '')
                )

                # 添加所有字段
                for field_meta in meta['fields']:
                    field_access = field_meta.get('access') or meta.get('access') or AccessType.RW
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

                self.add_register(reg)

            # 处理sub_block包装器
            elif hasattr(attr_value, '_rgm_is_sub_block'):
                meta = attr_value._rgm_meta
                sub_block = RegisterBlock(
                    name=meta['name'],
                    base_address=meta['offset']
                )
                sub_block._parent_block = self
                self.add_block(sub_block)

                # 如果子块有内部成员，递归初始化
                if hasattr(attr_value, '__dict__'):
                    for sub_attr_name, sub_attr_value in attr_value.__dict__.items():
                        if hasattr(sub_attr_value, '_rgm_is_register'):
                            sub_meta = sub_attr_value._rgm_meta
                            reg = Register(
                                name=sub_meta['name'],
                                offset=sub_meta['offset'],
                                width=sub_meta['width'],
                                reset_value=sub_meta['reset_value']
                            )
                            for field_meta in sub_meta['fields']:
                                field_access = field_meta.get('access') or sub_meta.get('access') or AccessType.RW
                                field = Field(
                                    name=field_meta['name'],
                                    bit_offset=field_meta['bit_offset'],
                                    bit_width=field_meta['bit_width'],
                                    access=field_access,
                                    reset_value=field_meta.get('reset_value', 0)
                                )
                                reg.add_field(field)
                            sub_block.add_register(reg)

    def add_register(self, register: Register) -> None:
        """
        添加寄存器

        Args:
            register: Register实例

        Raises:
            ValueError: 地址冲突
        """
        # 检查地址冲突
        abs_addr = self.base_address + register.offset
        if abs_addr in self._address_map:
            raise ValueError(
                f"Address conflict: 0x{abs_addr:X} already assigned to "
                f"{self._address_map[abs_addr].name}"
            )

        self._registers[register.name] = register
        register._parent_block = self
        self._address_map[abs_addr] = register

        # 添加到默认映射
        if self._default_map:
            self._default_map.add_reg(register, register.offset)

        # 设置默认访问接口
        if self._default_access:
            register._access_interface = self._default_access

    def add_block(self, block: "RegisterBlock") -> None:
        """
        添加子块（层次化）

        Args:
            block: RegisterBlock实例

        Raises:
            ValueError: 地址冲突
        """
        self._blocks[block.name] = block

        # 更新地址映射
        for addr, obj in block._address_map.items():
            if addr in self._address_map:
                raise ValueError(f"Address conflict at 0x{addr:X}")
            self._address_map[addr] = obj

    def get_register(self, path: str) -> Optional[Register]:
        """
        获取寄存器（支持层次化路径）

        Args:
            path: 寄存器路径，如 "UART.CTRL" 或 "CTRL"

        Returns:
            Register实例或None
        """
        if "." in path:
            # 层次化路径: "block.subblock.register"
            parts = path.split(".")
            current = self
            for part in parts[:-1]:
                if part not in current._blocks:
                    return None
                current = current._blocks[part]
            return current._registers.get(parts[-1])
        else:
            # 扁平路径
            return self._registers.get(path)

    def get_reg_by_offset(self, offset: int) -> Optional[Register]:
        """
        通过偏移地址获取寄存器（UVM风格）

        Args:
            offset: 相对于基地址的偏移

        Returns:
            Register实例或None
        """
        return self._default_map.get_reg_by_offset(offset) if self._default_map else None

    def get_registers(self) -> List[Register]:
        """
        获取所有寄存器（UVM风格）

        Returns:
            寄存器列表
        """
        return list(self._registers.values())

    def get_blocks(self) -> List["RegisterBlock"]:
        """
        获取所有子块（UVM风格）

        Returns:
            子块列表
        """
        return list(self._blocks.values())

    def get_block(self, name: str) -> Optional["RegisterBlock"]:
        """
        通过名称获取子块

        Args:
            name: 子块名称

        Returns:
            RegisterBlock实例或None
        """
        return self._blocks.get(name)

    def read(self, offset: Union[int, str]) -> int:
        """
        读取偏移地址或寄存器名称的值

        Args:
            offset: 相对于基地址的偏移(int) 或 寄存器名称(str)

        Returns:
            读取到的值
        """
        # Handle register name (string)
        if isinstance(offset, str):
            reg = self.get_register(offset)
            if reg:
                return reg.read()
            raise ValueError(f"Register '{offset}' not found")

        # Handle offset (int)
        reg = self.get_reg_by_offset(offset)
        if reg:
            return reg.read()

        # 使用默认访问接口
        if self._default_access:
            abs_addr = self.base_address + offset
            return self._default_access.read(abs_addr)

        return 0

    def write(self, offset: Union[int, str], value: int) -> None:
        """
        写入值到偏移地址或寄存器名称

        Args:
            offset: 相对于基地址的偏移(int) 或 寄存器名称(str)
            value: 要写入的值
        """
        # Handle register name (string)
        if isinstance(offset, str):
            reg = self.get_register(offset)
            if reg:
                reg.write(value)
                return
            raise ValueError(f"Register '{offset}' not found")

        # Handle offset (int)
        reg = self.get_reg_by_offset(offset)
        if reg:
            reg.write(value)
            return

        # 使用默认访问接口
        if self._default_access:
            abs_addr = self.base_address + offset
            self._default_access.write(abs_addr, value)

    def read_field(self, path: str, field_name: str) -> int:
        """
        读取字段值（支持层次化路径）

        Args:
            path: 寄存器路径
            field_name: 字段名称

        Returns:
            字段值
        """
        reg = self.get_register(path)
        if reg:
            return reg.read_field(field_name)
        raise ValueError(f"Register '{path}' not found")

    def write_field(self, path: str, field_name: str, value: int) -> None:
        """
        写入字段值（支持层次化路径）

        Args:
            path: 寄存器路径
            field_name: 字段名称
            value: 要写入的值
        """
        reg = self.get_register(path)
        if reg:
            reg.write_field(field_name, value)
            return
        raise ValueError(f"Register '{path}' not found")

    def set_access_interface(self, interface) -> None:
        """
        设置默认访问接口（策略模式）

        Args:
            interface: 访问接口实例
        """
        self._default_access = interface
        for reg in self._registers.values():
            reg._access_interface = interface

    def set_frontdoor(self, frontdoor) -> None:
        """
        设置前门访问接口（UVM风格）

        Args:
            frontdoor: 前门访问接口
        """
        self._frontdoor = frontdoor
        self.set_access_interface(frontdoor)

    def set_backdoor(self, backdoor) -> None:
        """
        设置后门访问接口（UVM风格）

        Args:
            backdoor: 后门访问接口
        """
        self._backdoor = backdoor

    def reset(self, kind: str = "SOFT") -> None:
        """
        复位寄存器块（UVM风格）

        Args:
            kind: "SOFT"（软复位，复位镜像值）或 "HARD"（硬复位，复位硬件）
        """
        for reg in self._registers.values():
            if kind == "SOFT":
                reg._mirrored_value = reg.reset_value
            else:  # HARD
                reg.write(reg.reset_value)
                reg._mirrored_value = reg.reset_value

    def get_default_map(self) -> Optional[RegisterMap]:
        """
        获取默认映射（UVM风格）

        Returns:
            RegisterMap实例
        """
        return self._default_map

    def get_summary(self) -> Dict:
        """
        获取寄存器块摘要

        Returns:
            摘要字典
        """
        return {
            "name": self.name,
            "base_address": f"0x{self.base_address:X}",
            "register_count": len(self._registers),
            "sub_blocks": len(self._blocks),
            "registers": [reg.name for reg in self._registers.values()],
            "blocks": [block.name for block in self._blocks.values()],
        }

    def __repr__(self) -> str:
        return (
            f"RegisterBlock(name='{self.name}', base=0x{self.base_address:X}, "
            f"registers={len(self._registers)}, blocks={len(self._blocks)})"
        )
