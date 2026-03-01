"""
APB Bus Adapter

支持APB（Advanced Peripheral Bus）总线协议的硬件访问。
"""

from typing import Optional
from .base import HardwareAdapter


class APBAdapter(HardwareAdapter):
    """
    APB总线适配器

    支持APB总线协议，常用于外设访问。

    Args:
        base_address: 基地址
        data_width: 数据位宽（默认32）

    Example:
        >>> adapter = APBAdapter(base_address=0x4000_0000)
        >>> adapter.set_driver(my_apb_driver)
        >>> value = adapter.read(0x4000_0000)
    """

    def __init__(self, base_address: int, data_width: int = 32):
        self.base_address = base_address
        self.data_width = data_width

        # 硬件接口
        self._driver = None

    def read(self, address: int) -> int:
        """APB读取事务"""
        if not self._driver:
            return 0

        offset = address - self.base_address
        return self._driver.apb_read(offset)

    def write(self, address: int, value: int) -> None:
        """APB写入事务"""
        if not self._driver:
            return

        offset = address - self.base_address
        self._driver.apb_write(offset, value)

    def is_connected(self) -> bool:
        """检查APB连接"""
        return self._driver is not None

    def set_driver(self, driver) -> None:
        """设置APB驱动"""
        self._driver = driver

    def __repr__(self) -> str:
        return (
            f"APBAdapter(base=0x{self.base_address:X}, "
            f"width={self.data_width}, connected={self.is_connected()})"
        )
