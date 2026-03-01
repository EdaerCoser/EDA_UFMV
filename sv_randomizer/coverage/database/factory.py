"""
Coverage Database Factory

数据库工厂类，用于创建不同类型的覆盖率数据库实例。

对应设计模式：工厂模式
"""

from typing import Optional, Dict, Any

from .base import CoverageDatabase
from .memory_db import MemoryCoverageDatabase
from .file_db import FileCoverageDatabase


class DatabaseFactory:
    """
    数据库工厂类

    支持的数据库类型：
    - "memory": 内存数据库（默认）
    - "file": 文件持久化数据库
    - "auto": 自动选择（有filepath则用file，否则用memory）

    使用示例：
        # 创建内存数据库
        db = DatabaseFactory.get_database("memory")

        # 创建文件数据库
        db = DatabaseFactory.get_database("file", filepath="coverage.json")

        # 自动选择
        db = DatabaseFactory.get_database("auto", filepath="coverage.json")
    """

    # 注册的数据库类型
    _backends: Dict[str, type] = {
        "memory": MemoryCoverageDatabase,
        "file": FileCoverageDatabase,
        "auto": None  # 特殊处理
    }

    @classmethod
    def register_backend(cls, name: str, backend_class: type) -> None:
        """
        注册新的数据库后端

        Args:
            name: 后端名称
            backend_class: 数据库类，必须继承CoverageDatabase

        Raises:
            ValueError: 如果backend_class不是CoverageDatabase的子类
        """
        if not issubclass(backend_class, CoverageDatabase):
            raise ValueError(
                f"Backend class must inherit from CoverageDatabase, "
                f"got {backend_class}"
            )

        cls._backends[name] = backend_class

    @classmethod
    def get_available_backends(cls) -> list:
        """
        获取所有可用的数据库后端

        Returns:
            后端名称列表
        """
        return list(cls._backends.keys())

    @classmethod
    def get_database(
        cls,
        backend: str = "memory",
        **kwargs
    ) -> CoverageDatabase:
        """
        获取数据库实例

        Args:
            backend: 后端类型 ("memory", "file", "auto")
            **kwargs: 传递给数据库构造函数的参数

        Returns:
            数据库实例

        Raises:
            ValueError: 如果后端类型不存在

        常用参数：
            filepath: 文件路径（仅用于"file"后端）
        """
        # 处理"auto"后端
        if backend == "auto":
            filepath = kwargs.get("filepath")
            if filepath:
                backend = "file"
            else:
                backend = "memory"

        # 检查后端是否存在
        if backend not in cls._backends:
            raise ValueError(
                f"Unknown database backend: {backend}. "
                f"Available backends: {', '.join(cls.get_available_backends())}"
            )

        backend_class = cls._backends[backend]

        # 创建数据库实例
        return backend_class(**kwargs)

    @classmethod
    def create_memory_database(cls) -> MemoryCoverageDatabase:
        """
        创建内存数据库（便捷方法）

        Returns:
            内存数据库实例
        """
        return cls.get_database("memory")

    @classmethod
    def create_file_database(cls, filepath: str) -> FileCoverageDatabase:
        """
        创建文件数据库（便捷方法）

        Args:
            filepath: 数据库文件路径

        Returns:
            文件数据库实例
        """
        return cls.get_database("file", filepath=filepath)


# 便捷函数
def create_database(backend: str = "memory", **kwargs) -> CoverageDatabase:
    """
    创建数据库实例（便捷函数）

    Args:
        backend: 后端类型
        **kwargs: 数据库参数

    Returns:
        数据库实例
    """
    return DatabaseFactory.get_database(backend, **kwargs)


def create_memory_database() -> MemoryCoverageDatabase:
    """创建内存数据库"""
    return DatabaseFactory.create_memory_database()


def create_file_database(filepath: str) -> FileCoverageDatabase:
    """创建文件数据库"""
    return DatabaseFactory.create_file_database(filepath)
