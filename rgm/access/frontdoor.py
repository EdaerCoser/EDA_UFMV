"""
FrontDoor Access - 前门访问（通过总线协议）

支持AXI、APB、AHB等总线协议的前门访问。
"""

from typing import Optional
from .base import AccessInterface


class FrontDoorAccess(AccessInterface):
    """
    前门访问 - 通过总线协议访问硬件寄存器

    对应UVM的uvm_reg_frontdoor访问机制。
    适用于功能验证，遵循总线协议规范。

    Args:
        bus_adapter: 总线适配器实例（AXIAdapter, APBAdapter等）

    Example:
        >>> from rgm.adapters import AXIAdapter
        >>> adapter = AXIAdapter(base_address=0x4000_0000)
        >>> front_door = FrontDoorAccess(adapter)
        >>> block.set_access_interface(front_door)
    """

    def __init__(self, bus_adapter):
        """
        初始化FrontDoor访问

        Args:
            bus_adapter: 总线适配器实例
        """
        self._adapter = bus_adapter
        self._transaction_count = 0

    def read(self, address: int) -> int:
        """
        通过总线读取

        Args:
            address: 绝对地址

        Returns:
            读取到的值
        """
        self._transaction_count += 1
        return self._adapter.read(address)

    def write(self, address: int, value: int) -> None:
        """
        通过总线写入

        Args:
            address: 绝对地址
            value: 要写入的值
        """
        self._transaction_count += 1
        self._adapter.write(address, value)

    def is_available(self) -> bool:
        """
        检查总线适配器是否可用

        Returns:
            True if connected, False otherwise
        """
        return self._adapter.is_connected()

    def get_transaction_count(self) -> int:
        """
        获取事务计数

        Returns:
            总事务数量
        """
        return self._transaction_count

    def reset_transaction_count(self) -> None:
        """重置事务计数"""
        self._transaction_count = 0

    def __repr__(self) -> str:
        return f"FrontDoorAccess(adapter={self._adapter}, transactions={self._transaction_count})"
