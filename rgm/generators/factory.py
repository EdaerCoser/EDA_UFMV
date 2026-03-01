"""
Code Generator Factory

代码生成器工厂（工厂模式）。
"""

from typing import Dict, Type
from .base import CodeGenerator
from .verilog_generator import VerilogGenerator
from .c_header_generator import CHeaderGenerator
from .python_generator import PythonGenerator


class GeneratorFactory:
    """
    代码生成器工厂

    支持的生成器：
    - "verilog": Verilog RTL
    - "c": C头文件
    - "python": Python模型
    - "systemverilog": SystemVerilog（未来）
    - "markdown": Markdown文档（未来）

    Args:
        **kwargs: 生成器特定参数

    Example:
        >>> from rgm.generators import GeneratorFactory
        >>>
        >>> # 获取生成器
        >>> gen = GeneratorFactory.get_generator("verilog")
        >>> code = gen.generate(block)
        >>>
        >>> # 或直接生成
        >>> code = GeneratorFactory.generate("c", block)
    """

    _generators: Dict[str, Type[CodeGenerator]] = {
        "verilog": VerilogGenerator,
        "v": VerilogGenerator,  # 别名
        "c": CHeaderGenerator,
        "h": CHeaderGenerator,  # 别名
        "python": PythonGenerator,
        "py": PythonGenerator,  # 别名
    }

    @classmethod
    def register_generator(cls, name: str, generator_class: Type[CodeGenerator]) -> None:
        """
        注册新的代码生成器

        Args:
            name: 生成器名称
            generator_class: 生成器类

        Example:
            >>> class MyGenerator(CodeGenerator):
            ...     pass
        >>> GeneratorFactory.register_generator("my", MyGenerator)
        """
        cls._generators[name] = generator_class

    @classmethod
    def get_generator(cls, name: str, **kwargs) -> CodeGenerator:
        """
        获取代码生成器实例

        Args:
            name: 生成器名称
            **kwargs: 传递给生成器构造函数的参数

        Returns:
            代码生成器实例

        Raises:
            ValueError: 生成器名称未知
        """
        if name not in cls._generators:
            raise ValueError(
                f"Unknown generator: {name}. "
                f"Available generators: {', '.join(cls.list_generators())}"
            )

        generator_class = cls._generators[name]
        return generator_class(**kwargs)

    @classmethod
    def generate(cls, name: str, block, **kwargs) -> str:
        """
        直接生成代码（便捷方法）

        Args:
            name: 生成器名称
            block: RegisterBlock实例
            **kwargs: 传递给生成器的参数

        Returns:
            生成的代码字符串
        """
        gen = cls.get_generator(name, **kwargs)
        return gen.generate(block)

    @classmethod
    def list_generators(cls) -> list:
        """
        列出所有可用的生成器

        Returns:
            生成器名称列表
        """
        return list(cls._generators.keys())

    @classmethod
    def get_file_extension(cls, name: str) -> str:
        """
        获取生成器的文件扩展名

        Args:
            name: 生成器名称

        Returns:
            文件扩展名（如".v", ".h", ".py"）
        """
        gen = cls.get_generator(name)
        return gen.get_file_extension()
