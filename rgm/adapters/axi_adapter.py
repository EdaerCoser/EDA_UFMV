"""
AXI4 Bus Adapter

支持AXI4总线协议的硬件访问。
"""

from typing import Optional
from .base import HardwareAdapter


class AXIAdapter(HardwareAdapter):
    """
    AXI4总线适配器

    支持AXI4-Lite和AXI4协议。

    Args:
        base_address: 基地址
        data_width: 数据位宽（默认32）
        interface_type: 接口类型（"AXI4-Lite"或"AXI4"）

    Example:
        >>> adapter = AXIAdapter(
        ...     base_address=0x4000_0000,
        ...     data_width=32,
        ...     interface_type="AXI4-Lite"
        ... )
        >>> # 注入硬件驱动
        >>> adapter.set_driver(my_axi_driver)
        >>> value = adapter.read(0x4000_0000)
    """

    def __init__(
        self,
        base_address: int,
        data_width: int = 32,
        interface_type: str = "AXI4-Lite",
    ):
        self.base_address = base_address
        self.data_width = data_width
        self.interface_type = interface_type

        # 硬件接口（由用户或测试框架注入）
        self._driver = None

    def read(self, address: int) -> int:
        """
        AXI读取事务

        Args:
            address: 物理地址

        Returns:
            读取到的值
        """
        if not self._driver:
            # 仿真模式：返回模拟值
            return 0

        # 实际硬件访问
        offset = address - self.base_address
        return self._driver.axi_read(offset)

    def write(self, address: int, value: int) -> None:
        """
        AXI写入事务

        Args:
            address: 物理地址
            value: 要写入的值
        """
        if not self._driver:
            return

        offset = address - self.base_address
        self._driver.axi_write(offset, value)

    def is_connected(self) -> bool:
        """
        检查AXI连接

        Returns:
            True if connected, False otherwise
        """
        return self._driver is not None

    def set_driver(self, driver) -> None:
        """
        设置AXI驱动（由测试框架注入）

        Args:
            driver: AXI驱动实例
        """
        self._driver = driver

    def get_driver(self):
        """
        获取AXI驱动

        Returns:
            当前驱动实例
        """
        return self._driver

    def __repr__(self) -> str:
        return (
            f"AXIAdapter(base=0x{self.base_address:X}, "
            f"width={self.data_width}, type={self.interface_type}, "
            f"connected={self.is_connected()})"
        )
