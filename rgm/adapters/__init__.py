"""
Adapters - 硬件适配器

包含AXI、APB、UART、SSH等硬件适配器实现。
"""

from .base import HardwareAdapter
from .axi_adapter import AXIAdapter
from .apb_adapter import APBAdapter
from .uart_adapter import UARTAdapter
from .ssh_adapter import SSHAdapter

__all__ = [
    "HardwareAdapter",
    "AXIAdapter",
    "APBAdapter",
    "UARTAdapter",
    "SSHAdapter",
]
