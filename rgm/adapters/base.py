"""
Hardware Adapter Base Classes

硬件适配器抽象基类。
"""

from abc import ABC, abstractmethod


class HardwareAdapter(ABC):
    """
    硬件适配器抽象基类

    所有硬件接口适配器必须实现此接口。

    用于FPGA"上板"测试中的实际硬件访问。
    """

    @abstractmethod
    def read(self, address: int) -> int:
        """
        读取硬件寄存器

        Args:
            address: 物理地址

        Returns:
            读取到的值
        """
        pass

    @abstractmethod
    def write(self, address: int, value: int) -> None:
        """
        写入硬件寄存器

        Args:
            address: 物理地址
            value: 要写入的值
        """
        pass

    @abstractmethod
    def is_connected(self) -> bool:
        """
        检查硬件连接状态

        Returns:
            True if connected, False otherwise
        """
        pass
