"""
Code Generator Base Classes

代码生成器抽象基类。
"""

from abc import ABC, abstractmethod


class CodeGenerator(ABC):
    """
    代码生成器抽象基类

    支持生成多种格式的代码：
    - Verilog RTL
    - C头文件
    - Python模型
    - SystemVerilog
    - 文档
    """

    @abstractmethod
    def generate(self, block, **kwargs) -> str:
        """
        生成代码

        Args:
            block: RegisterBlock实例
            **kwargs: 生成器特定参数

        Returns:
            生成的代码字符串
        """
        pass

    @abstractmethod
    def get_file_extension(self) -> str:
        """
        获取生成文件的扩展名

        Returns:
            文件扩展名（如".v", ".h", ".py"）
        """
        pass
