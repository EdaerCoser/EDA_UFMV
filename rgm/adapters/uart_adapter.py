"""
UART Serial Adapter

支持UART串行接口的硬件访问。
"""

from typing import Optional
from .base import HardwareAdapter


class UARTAdapter(HardwareAdapter):
    """
    UART串行适配器

    通过UART串口访问硬件寄存器。

    Args:
        port: 串口设备路径（如"/dev/ttyUSB0"或"COM3"）
        baudrate: 波特率（默认115200）

    Example:
        >>> adapter = UARTAdapter(port="/dev/ttyUSB0", baudrate=115200)
        >>> adapter.connect()
        >>> value = adapter.read(0x4000_0000)
    """

    def __init__(self, port: str, baudrate: int = 115200):
        self.port = port
        self.baudrate = baudrate

        # UART连接
        self._connection = None

    def connect(self) -> bool:
        """
        连接到UART串口

        Returns:
            True if successful, False otherwise
        """
        try:
            # 这里可以集成pyserial或其他UART库
            # import serial
            # self._connection = serial.Serial(self.port, self.baudrate)
            # return True
            pass
        except Exception:
            return False
        return True

    def disconnect(self) -> None:
        """断开UART连接"""
        if self._connection:
            self._connection.close()
            self._connection = None

    def read(self, address: int) -> int:
        """
        通过UART读取寄存器

        Args:
            address: 物理地址

        Returns:
            读取到的值
        """
        if not self._connection:
            raise RuntimeError("UART not connected")

        # 发送读命令
        # self._connection.write(f"RD {address:08X}\n".encode())
        # response = self._connection.readline()
        # return int(response, 16)
        return 0

    def write(self, address: int, value: int) -> None:
        """
        通过UART写入寄存器

        Args:
            address: 物理地址
            value: 要写入的值
        """
        if not self._connection:
            raise RuntimeError("UART not connected")

        # 发送写命令
        # self._connection.write(f"WR {address:08X} {value:08X}\n".encode())
        pass

    def is_connected(self) -> bool:
        """检查UART连接状态"""
        return self._connection is not None

    def __repr__(self) -> str:
        return (
            f"UARTAdapter(port={self.port}, baudrate={self.baudrate}, "
            f"connected={self.is_connected()})"
        )
