"""
Access Interface Base Classes

定义访问接口的抽象基类（策略模式）。
"""

from abc import ABC, abstractmethod


class AccessInterface(ABC):
    """
    访问接口抽象基类

    所有访问后端（FrontDoor、BackDoor、硬件适配器）必须实现此接口。

    对应UVM的uvm_reg_frontdoor和uvm_reg_backdoor基类。
    """

    @abstractmethod
    def read(self, address: int) -> int:
        """
        读取指定地址的值

        Args:
            address: 绝对地址

        Returns:
            读取到的值（通常为32位）
        """
        pass

    @abstractmethod
    def write(self, address: int, value: int) -> None:
        """
        写入值到指定地址

        Args:
            address: 绝对地址
            value: 要写入的值
        """
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """
        检查此访问接口是否可用

        Returns:
            True if available, False otherwise
        """
        pass
