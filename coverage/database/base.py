"""
Coverage Database Base Interface

定义覆盖率数据库的抽象接口，支持多种后端实现。

对应设计模式：策略模式
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Tuple, Optional
from datetime import datetime


class CoverageDatabase(ABC):
    """
    覆盖率数据库抽象接口

    定义所有覆盖率数据库后端必须实现的方法。

    支持的功能：
    - 记录采样数据
    - 查询命中次数
    - 获取覆盖率数据
    - 持久化和加载
    - 数据库合并
    """

    @abstractmethod
    def record_sample(
        self,
        coverpoint_name: str,
        value: Any,
        covergroup_name: str,
        timestamp: Optional[datetime] = None
    ) -> None:
        """
        记录单个采样数据

        Args:
            coverpoint_name: CoverPoint名称
            value: 采样值
            covergroup_name: CoverGroup名称
            timestamp: 可选的时间戳，默认为当前时间
        """
        pass

    @abstractmethod
    def record_cross_sample(
        self,
        cross_name: str,
        bin_tuple: Tuple[Any, ...],
        covergroup_name: str,
        timestamp: Optional[datetime] = None
    ) -> None:
        """
        记录交叉覆盖率采样数据

        Args:
            cross_name: Cross名称
            bin_tuple: bin值元组（对应各个CoverPoint的bin）
            covergroup_name: CoverGroup名称
            timestamp: 可选的时间戳
        """
        pass

    @abstractmethod
    def get_hit_count(
        self,
        coverpoint_name: str,
        bin_name: Optional[str] = None,
        covergroup_name: Optional[str] = None
    ) -> int:
        """
        获取命中次数

        Args:
            coverpoint_name: CoverPoint名称
            bin_name: 可选的bin名称，None表示所有bins
            covergroup_name: 可选的CoverGroup名称

        Returns:
            命中次数
        """
        pass

    @abstractmethod
    def get_coverage_data(
        self,
        covergroup_name: str
    ) -> Dict[str, Any]:
        """
        获取覆盖率数据

        Args:
            covergroup_name: CoverGroup名称

        Returns:
            包含以下键的字典：
            - 'covergroup': CoverGroup名称
            - 'coverpoints': CoverPoint数据字典
            - 'sample_count': 总采样次数
            - 'timestamp': 最后更新时间
        """
        pass

    @abstractmethod
    def get_bin_hits(
        self,
        coverpoint_name: str,
        covergroup_name: str
    ) -> Dict[str, int]:
        """
        获取指定CoverPoint的所有bin命中次数

        Args:
            coverpoint_name: CoverPoint名称
            covergroup_name: CoverGroup名称

        Returns:
            bin名称到命中次数的映射
        """
        pass

    @abstractmethod
    def get_cross_data(
        self,
        cross_name: str,
        covergroup_name: str
    ) -> Dict[str, Any]:
        """
        获取交叉覆盖率数据

        Args:
            cross_name: Cross名称
            covergroup_name: CoverGroup名称

        Returns:
            包含交叉覆盖率数据的字典
        """
        pass

    @abstractmethod
    def save(self, filepath: Optional[str] = None) -> None:
        """
        保存数据库到持久化存储

        Args:
            filepath: 可选的文件路径，None表示使用默认路径
        """
        pass

    @abstractmethod
    def load(self, filepath: Optional[str] = None) -> None:
        """
        从持久化存储加载数据库

        Args:
            filepath: 可选的文件路径，None表示使用默认路径
        """
        pass

    @abstractmethod
    def merge(self, other: 'CoverageDatabase') -> None:
        """
        合并另一个数据库

        用于合并多个测试运行的覆盖率数据

        Args:
            other: 要合并的另一个数据库实例
        """
        pass

    @abstractmethod
    def clear(self) -> None:
        """
        清空所有数据
        """
        pass

    @abstractmethod
    def get_statistics(self) -> Dict[str, Any]:
        """
        获取数据库统计信息

        Returns:
            包含统计信息的字典：
            - 'total_samples': 总采样次数
            - 'total_covergroups': CoverGroup数量
            - 'total_coverpoints': CoverPoint数量
            - 'total_bins': 总bin数量
            - 'memory_usage': 内存使用（字节）
        """
        pass

    @abstractmethod
    def create_snapshot(self) -> Dict[str, Any]:
        """
        创建数据库快照

        用于保存当前状态，以便后续恢复

        Returns:
            包含数据库状态的字典
        """
        pass

    @abstractmethod
    def restore_snapshot(self, snapshot: Dict[str, Any]) -> None:
        """
        从快照恢复数据库状态

        Args:
            snapshot: 之前创建的快照
        """
        pass


class DatabaseError(Exception):
    """数据库操作错误"""
    pass


class DatabaseMergeError(DatabaseError):
    """数据库合并错误"""
    pass


class DatabaseLoadError(DatabaseError):
    """数据库加载错误"""
    pass


class DatabaseSaveError(DatabaseError):
    """数据库保存错误"""
    pass
