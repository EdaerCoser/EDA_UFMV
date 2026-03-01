"""
In-Memory Coverage Database Implementation

内存数据库实现，提供快速的覆盖率数据存储和查询。

特点：
- 无需持久化，数据存储在内存中
- 快速访问和更新
- 适用于短期测试和开发环境
"""

import sys
from typing import Any, Dict, List, Tuple, Optional
from datetime import datetime
from collections import defaultdict

from .base import (
    CoverageDatabase,
    DatabaseError,
    DatabaseMergeError,
    DatabaseLoadError,
    DatabaseSaveError
)


class MemoryCoverageDatabase(CoverageDatabase):
    """
    内存覆盖率数据库实现

    数据结构：
    {
        covergroup_name: {
            'coverpoints': {
                coverpoint_name: {
                    'bins': {bin_name: hit_count},
                    'total_samples': int,
                    'timestamp': datetime
                }
            },
            'crosses': {
                cross_name: {
                    'bins': {(bin1, bin2, ...): hit_count},
                    'total_samples': int,
                    'timestamp': datetime
                }
            },
            'sample_count': int,
            'timestamp': datetime
        }
    }
    """

    def __init__(self):
        """初始化内存数据库"""
        self._data: Dict[str, Dict] = {}
        self._created_at = datetime.now()

    def record_sample(
        self,
        coverpoint_name: str,
        value: Any,
        covergroup_name: str,
        timestamp: Optional[datetime] = None
    ) -> None:
        """记录单个采样数据"""
        if covergroup_name not in self._data:
            self._data[covergroup_name] = {
                'coverpoints': {},
                'crosses': {},
                'sample_count': 0,
                'timestamp': timestamp or datetime.now()
            }

        cg_data = self._data[covergroup_name]

        if coverpoint_name not in cg_data['coverpoints']:
            cg_data['coverpoints'][coverpoint_name] = {
                'bins': defaultdict(int),
                'total_samples': 0,
                'timestamp': timestamp or datetime.now()
            }

        cp_data = cg_data['coverpoints'][coverpoint_name]

        # 假设value已经是对应的bin名称
        # 在实际使用中，CoverPoint会先确定bin，然后调用此方法
        bin_name = str(value)
        cp_data['bins'][bin_name] += 1
        cp_data['total_samples'] += 1
        cg_data['sample_count'] += 1
        cg_data['timestamp'] = timestamp or datetime.now()

    def record_cross_sample(
        self,
        cross_name: str,
        bin_tuple: Tuple[Any, ...],
        covergroup_name: str,
        timestamp: Optional[datetime] = None
    ) -> None:
        """记录交叉覆盖率采样数据"""
        if covergroup_name not in self._data:
            self._data[covergroup_name] = {
                'coverpoints': {},
                'crosses': {},
                'sample_count': 0,
                'timestamp': timestamp or datetime.now()
            }

        cg_data = self._data[covergroup_name]

        if cross_name not in cg_data['crosses']:
            cg_data['crosses'][cross_name] = {
                'bins': defaultdict(int),
                'total_samples': 0,
                'timestamp': timestamp or datetime.now()
            }

        cross_data = cg_data['crosses'][cross_name]

        # 使用元组作为键
        cross_data['bins'][bin_tuple] += 1
        cross_data['total_samples'] += 1
        cg_data['sample_count'] += 1
        cg_data['timestamp'] = timestamp or datetime.now()

    def get_hit_count(
        self,
        coverpoint_name: str,
        bin_name: Optional[str] = None,
        covergroup_name: Optional[str] = None
    ) -> int:
        """获取命中次数"""
        if covergroup_name and covergroup_name not in self._data:
            return 0

        if covergroup_name:
            cg_data = self._data[covergroup_name]

            if coverpoint_name not in cg_data['coverpoints']:
                return 0

            cp_data = cg_data['coverpoints'][coverpoint_name]

            if bin_name:
                return cp_data['bins'].get(bin_name, 0)
            else:
                return cp_data['total_samples']
        else:
            # 搜索所有covergroup
            total = 0
            for cg_data in self._data.values():
                if coverpoint_name in cg_data['coverpoints']:
                    cp_data = cg_data['coverpoints'][coverpoint_name]
                    if bin_name:
                        total += cp_data['bins'].get(bin_name, 0)
                    else:
                        total += cp_data['total_samples']
            return total

    def get_coverage_data(
        self,
        covergroup_name: str
    ) -> Dict[str, Any]:
        """获取覆盖率数据"""
        if covergroup_name not in self._data:
            return {
                'covergroup': covergroup_name,
                'coverpoints': {},
                'sample_count': 0,
                'timestamp': None
            }

        cg_data = self._data[covergroup_name]

        return {
            'covergroup': covergroup_name,
            'coverpoints': {
                cp_name: {
                    'bins': dict(cp_data['bins']),
                    'total_samples': cp_data['total_samples'],
                    'timestamp': cp_data['timestamp']
                }
                for cp_name, cp_data in cg_data['coverpoints'].items()
            },
            'sample_count': cg_data['sample_count'],
            'timestamp': cg_data['timestamp']
        }

    def get_bin_hits(
        self,
        coverpoint_name: str,
        covergroup_name: str
    ) -> Dict[str, int]:
        """获取指定CoverPoint的所有bin命中次数"""
        if covergroup_name not in self._data:
            return {}

        cg_data = self._data[covergroup_name]

        if coverpoint_name not in cg_data['coverpoints']:
            return {}

        return dict(cg_data['coverpoints'][coverpoint_name]['bins'])

    def get_cross_data(
        self,
        cross_name: str,
        covergroup_name: str
    ) -> Dict[str, Any]:
        """获取交叉覆盖率数据"""
        if covergroup_name not in self._data:
            return {
                'cross': cross_name,
                'bins': {},
                'total_samples': 0,
                'timestamp': None
            }

        cg_data = self._data[covergroup_name]

        if cross_name not in cg_data['crosses']:
            return {
                'cross': cross_name,
                'bins': {},
                'total_samples': 0,
                'timestamp': None
            }

        cross_data = cg_data['crosses'][cross_name]

        return {
            'cross': cross_name,
            'bins': dict(cross_data['bins']),
            'total_samples': cross_data['total_samples'],
            'timestamp': cross_data['timestamp']
        }

    def save(self, filepath: Optional[str] = None) -> None:
        """
        保存数据库（内存数据库不支持持久化）

        Args:
            filepath: 忽略，保持接口一致性

        Raises:
            DatabaseSaveError: 内存数据库不支持保存到文件
        """
        # 内存数据库不支持持久化
        # 如果需要持久化，应该使用FileCoverageDatabase
        pass

    def load(self, filepath: Optional[str] = None) -> None:
        """
        加载数据库（内存数据库不支持从文件加载）

        Args:
            filepath: 忽略，保持接口一致性

        Raises:
            DatabaseLoadError: 内存数据库不支持从文件加载
        """
        # 内存数据库不支持从文件加载
        pass

    def merge(self, other: 'CoverageDatabase') -> None:
        """合并另一个数据库"""
        if not isinstance(other, MemoryCoverageDatabase):
            raise DatabaseMergeError(
                f"Cannot merge {type(other).__name__} with MemoryCoverageDatabase"
            )

        # 合并数据
        for cg_name, cg_data in other._data.items():
            if cg_name not in self._data:
                # 直接复制整个covergroup
                self._data[cg_name] = cg_data.copy()
            else:
                # 合并coverpoints
                my_cg = self._data[cg_name]
                for cp_name, cp_data in cg_data['coverpoints'].items():
                    if cp_name not in my_cg['coverpoints']:
                        my_cg['coverpoints'][cp_name] = cp_data.copy()
                    else:
                        # 合并bins
                        my_cp = my_cg['coverpoints'][cp_name]
                        for bin_name, count in cp_data['bins'].items():
                            my_cp['bins'][bin_name] += count
                        my_cp['total_samples'] += cp_data['total_samples']

                # 合并crosses
                for cross_name, cross_data in cg_data['crosses'].items():
                    if cross_name not in my_cg['crosses']:
                        my_cg['crosses'][cross_name] = cross_data.copy()
                    else:
                        # 合并cross bins
                        my_cross = my_cg['crosses'][cross_name]
                        for bin_tuple, count in cross_data['bins'].items():
                            my_cross['bins'][bin_tuple] += count
                        my_cross['total_samples'] += cross_data['total_samples']

                my_cg['sample_count'] += cg_data['sample_count']

    def clear(self) -> None:
        """清空所有数据"""
        self._data.clear()

    def get_statistics(self) -> Dict[str, Any]:
        """获取数据库统计信息"""
        total_samples = 0
        total_covergroups = len(self._data)
        total_coverpoints = 0
        total_bins = 0

        for cg_data in self._data.values():
            total_samples += cg_data['sample_count']
            total_coverpoints += len(cg_data['coverpoints'])

            for cp_data in cg_data['coverpoints'].values():
                total_bins += len(cp_data['bins'])

        # 估算内存使用
        memory_usage = sys.getsizeof(self._data)
        for cg_data in self._data.values():
            memory_usage += sys.getsizeof(cg_data)
            memory_usage += sys.getsizeof(cg_data['coverpoints'])
            memory_usage += sys.getsizeof(cg_data['crosses'])

        return {
            'total_samples': total_samples,
            'total_covergroups': total_covergroups,
            'total_coverpoints': total_coverpoints,
            'total_bins': total_bins,
            'memory_usage': memory_usage,
            'created_at': self._created_at
        }

    def create_snapshot(self) -> Dict[str, Any]:
        """创建数据库快照"""
        return {
            'data': {
                cg_name: {
                    'coverpoints': {
                        cp_name: {
                            'bins': dict(cp_data['bins']),
                            'total_samples': cp_data['total_samples'],
                            'timestamp': cp_data['timestamp']
                        }
                        for cp_name, cp_data in cg_data['coverpoints'].items()
                    },
                    'crosses': {
                        cross_name: {
                            'bins': dict(cross_data['bins']),
                            'total_samples': cross_data['total_samples'],
                            'timestamp': cross_data['timestamp']
                        }
                        for cross_name, cross_data in cg_data['crosses'].items()
                    },
                    'sample_count': cg_data['sample_count'],
                    'timestamp': cg_data['timestamp']
                }
                for cg_name, cg_data in self._data.items()
            },
            'created_at': self._created_at,
            'snapshot_time': datetime.now()
        }

    def restore_snapshot(self, snapshot: Dict[str, Any]) -> None:
        """从快照恢复数据库状态"""
        if 'data' not in snapshot:
            raise DatabaseLoadError("Invalid snapshot format")

        # 深度复制数据
        self._data = {}
        for cg_name, cg_data in snapshot['data'].items():
            self._data[cg_name] = {
                'coverpoints': {},
                'crosses': {},
                'sample_count': cg_data['sample_count'],
                'timestamp': cg_data['timestamp']
            }

            for cp_name, cp_data in cg_data['coverpoints'].items():
                self._data[cg_name]['coverpoints'][cp_name] = {
                    'bins': defaultdict(int, cp_data['bins']),
                    'total_samples': cp_data['total_samples'],
                    'timestamp': cp_data['timestamp']
                }

            for cross_name, cross_data in cg_data['crosses'].items():
                self._data[cg_name]['crosses'][cross_name] = {
                    'bins': defaultdict(int, cross_data['bins']),
                    'total_samples': cross_data['total_samples'],
                    'timestamp': cross_data['timestamp']
                }

        self._created_at = snapshot.get('created_at', datetime.now())
