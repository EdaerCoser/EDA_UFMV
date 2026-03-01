"""
Coverage Database Module

覆盖率数据库模块，提供多种数据库后端实现。
"""

from .base import (
    CoverageDatabase,
    DatabaseError,
    DatabaseMergeError,
    DatabaseLoadError,
    DatabaseSaveError
)
from .memory_db import MemoryCoverageDatabase
from .file_db import FileCoverageDatabase
from .factory import (
    DatabaseFactory,
    create_database,
    create_memory_database,
    create_file_database
)

__all__ = [
    # 基础接口
    "CoverageDatabase",
    "DatabaseError",
    "DatabaseMergeError",
    "DatabaseLoadError",
    "DatabaseSaveError",

    # 数据库实现
    "MemoryCoverageDatabase",
    "FileCoverageDatabase",

    # 工厂和便捷函数
    "DatabaseFactory",
    "create_database",
    "create_memory_database",
    "create_file_database",
]
