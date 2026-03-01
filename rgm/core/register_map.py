"""
RegisterMap - 寄存器地址映射类

对应UVM的uvm_reg_map，管理寄存器到物理地址的映射关系。
"""

from typing import Dict, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .register import Register


class RegisterMap:
    """
    寄存器地址映射

    对应UVM的uvm_reg_map，管理寄存器到物理地址的映射关系。

    Args:
        name: 映射名称
        base_address: 基地址

    Example:
        >>> reg_map = RegisterMap("default_map", base_address=0x4000_0000)
        >>> reg_map.add_reg(ctrl_reg, offset=0x00)
        >>> reg_map.add_reg(status_reg, offset=0x04)
        >>> reg = reg_map.get_reg_by_offset(0x00)
    """

    def __init__(self, name: str, base_address: int):
        self.name = name
        self.base_address = base_address
        self._registers: Dict[int, "Register"] = {}
        self._system_map = None  # 上层映射（用于层次化）
        self._sequencer = None  # 序列器（用于高级事务）

    def add_reg(self, register: "Register", offset: int) -> None:
        """
        添加寄存器到映射

        Args:
            register: Register实例
            offset: 相对于基地址的偏移

        Raises:
            ValueError: 地址冲突
        """
        abs_addr = self.base_address + offset
        if abs_addr in self._registers:
            raise ValueError(
                f"Address conflict: 0x{abs_addr:X} already assigned to "
                f"{self._registers[abs_addr].name}"
            )

        self._registers[abs_addr] = register

    def get_reg_by_offset(self, offset: int) -> Optional["Register"]:
        """
        通过偏移获取寄存器

        Args:
            offset: 相对于基地址的偏移

        Returns:
            Register实例或None
        """
        return self._registers.get(self.base_address + offset)

    def get_reg_by_name(self, name: str) -> Optional["Register"]:
        """
        通过名称获取寄存器

        Args:
            name: 寄存器名称

        Returns:
            Register实例或None
        """
        for reg in self._registers.values():
            if reg.name == name:
                return reg
        return None

    def get_phys_address(self, offset: int) -> int:
        """
        获取物理地址

        Args:
            offset: 相对于基地址的偏移

        Returns:
            物理地址
        """
        return self.base_address + offset

    def set_sequencer(self, sequencer) -> None:
        """
        设置序列器（用于高级事务）

        Args:
            sequencer: 序列器实例
        """
        self._sequencer = sequencer

    def get_sequencer(self):
        """
        获取序列器

        Returns:
            序列器实例
        """
        return self._sequencer

    def get_registers(self):
        """
        获取所有寄存器

        Returns:
            寄存器字典
        """
        return self._registers.copy()

    def __repr__(self) -> str:
        return (
            f"RegisterMap(name='{self.name}', base=0x{self.base_address:X}, "
            f"registers={len(self._registers)})"
        )
