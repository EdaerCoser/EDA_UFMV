"""
格式化器基类
"""

from abc import ABC, abstractmethod
from typing import Any


class Formatter(ABC):
    """格式化器抽象基类"""

    @abstractmethod
    def format(self, obj: Any) -> str:
        """
        格式化对象

        Args:
            obj: 要格式化的对象

        Returns:
            格式化后的字符串
        """
        pass
