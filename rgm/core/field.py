"""
Field - 寄存器字段类

对应SystemVerilog的字段定义和UVM的uvm_reg_field。
支持多种访问类型（RW, RO, WO, W1C, W1S等）。
"""

from enum import Enum
from typing import Optional


class AccessType(Enum):
    """字段访问类型（对应UVM uvm_reg_field的访问权限）"""

    RW = "RW"  # Read-Write
    RO = "RO"  # Read-Only
    WO = "WO"  # Write-Only
    W1C = "W1C"  # Write-1-to-Clear
    W1S = "W1S"  # Write-1-to-Set
    W1T = "W1T"  # Write-1-to-Toggle
    W0C = "W0C"  # Write-0-to-Clear
    W0S = "W0S"  # Write-0-to-Set
    W0T = "W0T"  # Write-0-to-Toggle
    RC = "RC"  # Read-to-Clear
    RS = "RS"  # Read-to-Set
    WC = "WC"  # Write-Clear
    WS = "WS"  # Write-Set
    WRC = "WRC"  # Write with Read-Only
    WRS = "WRS"  # Write with Read-Set
    WSRC = "WSRC"  # Write-Set with Read-Clear
    WCRS = "WCRS"  # Write-Clear with Read-Set
    WAT = "WAT"  # Write-Always
    WAT1 = "WAT1"  # Write-Always-1


class Field:
    """
    寄存器字段

    对应SystemVerilog的字段定义和UVM的uvm_reg_field。

    SystemVerilog示例:
        typedef struct packed {
            bit [7:0]   reserved;
            bit [15:8]  data;      // RW
            bit [16]     enable;    // RO
            bit [31:17] status;     // W1C
        } my_field_t;

    Args:
        name: 字段名称
        bit_offset: 字段在寄存器中的位偏移
        bit_width: 字段位宽
        access: 访问类型（默认RW）
        reset_value: 复位值（默认0）
        volatile: 是否为易失性字段（硬件可能随时改变）
        description: 字段描述

    Example:
        >>> field = Field(
        ...     name="data",
        ...     bit_offset=8,
        ...     bit_width=8,
        ...     access=AccessType.RW,
        ...     reset_value=0x00,
        ...     description="Data register field"
        ... )
        >>> field.write(0x5A)
        >>> value = field.read()
    """

    def __init__(
        self,
        name: str,
        bit_offset: int,
        bit_width: int,
        access: AccessType = AccessType.RW,
        reset_value: int = 0,
        volatile: bool = False,
        description: str = "",
    ):
        self.name = name
        self.bit_offset = bit_offset
        self.bit_width = bit_width
        self.access = access
        self.reset_value = reset_value
        self.volatile = volatile
        self.description = description

        # 运行时状态
        self._current_value = reset_value
        self._mirrored_value = reset_value  # UVM风格：镜像值
        self._parent_register = None

    def get_mask(self) -> int:
        """
        获取字段的位掩码

        Returns:
            字段的位掩码（例如bit_offset=8, bit_width=8返回0xFF00）
        """
        return ((1 << self.bit_width) - 1) << self.bit_offset

    def read(self) -> int:
        """
        读取字段值（从硬件）

        Returns:
            当前字段值
        """
        # RC (Read-to-Clear): 返回当前值后清零
        if self.access == AccessType.RC:
            value_before_clear = self._current_value
            self._current_value = 0
            self._mirrored_value = 0
            return value_before_clear

        # RS (Read-to-Set): 返回当前值后设置为全1
        if self.access == AccessType.RS:
            value_before_set = self._current_value
            self._current_value = (1 << self.bit_width) - 1
            self._mirrored_value = self._current_value
            return value_before_set

        # WO (Write-Only): 读返回0
        if self.access == AccessType.WO:
            return 0

        # 如果有父寄存器，从寄存器读取
        if self._parent_register:
            reg_value = self._parent_register.read()
            return (reg_value >> self.bit_offset) & ((1 << self.bit_width) - 1)
        return self._current_value

    def write(self, value: int) -> None:
        """
        写入字段值（根据access类型处理）

        Args:
            value: 要写入的值

        根据访问类型处理写操作：
        - RW/WO: 直接写入
        - W1C: 写1清除对应位
        - W1S: 写1设置对应位
        - W0C: 写0清除对应位
        - W0S: 写0设置对应位
        - WC: 任何写入都清零
        - WS: 任何写入都置为全1
        - RO: 忽略写入
        - RC/RS: 写入操作无特殊处理（清除/设置在读取时发生）
        """
        masked_value = value & ((1 << self.bit_width) - 1)

        if self.access == AccessType.RO:
            return  # 忽略写入

        elif self.access == AccessType.W1C:
            # 写1清除对应位，写0保持不变
            # 清除被写1的位
            self._current_value &= ~masked_value

        elif self.access == AccessType.W1S:
            # 写1设置对应位，写0保持不变
            # 设置被写1的位
            self._current_value |= masked_value

        elif self.access == AccessType.W0C:
            # 写0清除对应位，写1保持不变
            # 反转掩码，清除被写0的位
            self._current_value &= masked_value | ~((1 << self.bit_width) - 1)

        elif self.access == AccessType.W0S:
            # 写0设置对应位，写1保持不变
            # 对于写0的位，设置为1；对于写1的位，保持原值
            if masked_value == 0:
                # 写0：所有位都设置为1
                self._current_value = (1 << self.bit_width) - 1
            else:
                # 写非0值：保持当前值不变
                pass  # 不修改_current_value

        elif self.access == AccessType.WC:
            # 任何写入都清零
            self._current_value = 0

        elif self.access == AccessType.WS:
            # 任何写入都置为全1
            self._current_value = (1 << self.bit_width) - 1

        elif self.access == AccessType.RC or self.access == AccessType.RS:
            # RC/RS的清除/设置在读取时发生，写操作正常写入
            self._current_value = masked_value

        else:  # RW, WO, WAT, WAT1, etc.
            # 直接写入
            self._current_value = masked_value

        # 更新镜像值
        self._mirrored_value = self._current_value

    def reset(self) -> None:
        """重置字段值为复位值"""
        self._current_value = self.reset_value
        self._mirrored_value = self.reset_value

    def get_max_value(self) -> int:
        """
        获取字段最大值

        Returns:
            字段能表示的最大值
        """
        return (1 << self.bit_width) - 1

    # ========== UVM风格接口 ==========

    def set(self, value: int) -> None:
        """
        设置字段期望值（UVM风格）- 不立即写入硬件

        Args:
            value: 期望值
        """
        masked = value & ((1 << self.bit_width) - 1)
        self._mirrored_value = masked

    def get(self) -> int:
        """
        获取字段镜像值（UVM风格）

        Returns:
            镜像值
        """
        return self._mirrored_value & ((1 << self.bit_width) - 1)

    def peek(self) -> int:
        """
        后门读取字段值（UVM风格）

        Returns:
            字段当前值
        """
        return self.read()

    def poke(self, value: int) -> None:
        """
        后门写入字段值（UVM风格）- 强制写入，忽略访问权限

        Args:
            value: 要写入的值
        """
        masked = value & ((1 << self.bit_width) - 1)
        self._current_value = masked
        self._mirrored_value = masked

    def __repr__(self) -> str:
        return (
            f"Field(name='{self.name}', offset={self.bit_offset}, "
            f"width={self.bit_width}, access={self.access.value}, "
            f"value=0x{self._current_value:X})"
        )
