"""
File-Persistent Coverage Database Implementation

文件持久化数据库实现，支持将覆盖率数据保存到文件。

特点：
- JSON格式持久化
- 支持增量保存
- 支持数据合并
- 适用于长期存储和跨测试运行
"""

import json
import os
from typing import Any, Dict, List, Optional
from datetime import datetime
from pathlib import Path

from .base import (
    CoverageDatabase,
    DatabaseError,
    DatabaseMergeError,
    DatabaseLoadError,
    DatabaseSaveError
)
from .memory_db import MemoryCoverageDatabase


class FileCoverageDatabase(MemoryCoverageDatabase):
    """
    文件持久化覆盖率数据库实现

    继承MemoryCoverageDatabase，添加文件持久化功能。

    文件格式：JSON
    {
        "version": "1.0",
        "created_at": "ISO 8601 timestamp",
        "updated_at": "ISO 8601 timestamp",
        "data": {
            covergroup_name: {
                "coverpoints": {...},
                "crosses": {...},
                "sample_count": int,
                "timestamp": "ISO 8601 timestamp"
            }
        }
    }
    """

    VERSION = "1.0"

    def __init__(self, filepath: Optional[str] = None):
        """
        初始化文件数据库

        Args:
            filepath: 数据库文件路径，None表示使用默认路径
        """
        super().__init__()
        self._filepath = filepath
        self._dirty = False  # 标记数据是否已修改

    def set_filepath(self, filepath: str) -> None:
        """设置数据库文件路径"""
        self._filepath = filepath

    def get_filepath(self) -> Optional[str]:
        """获取数据库文件路径"""
        return self._filepath

    def record_sample(
        self,
        coverpoint_name: str,
        value: Any,
        covergroup_name: str,
        timestamp: Optional[datetime] = None
    ) -> None:
        """记录单个采样数据"""
        super().record_sample(coverpoint_name, value, covergroup_name, timestamp)
        self._dirty = True

    def record_cross_sample(
        self,
        cross_name: str,
        bin_tuple: tuple,
        covergroup_name: str,
        timestamp: Optional[datetime] = None
    ) -> None:
        """记录交叉覆盖率采样数据"""
        super().record_cross_sample(cross_name, bin_tuple, covergroup_name, timestamp)
        self._dirty = True

    def save(self, filepath: Optional[str] = None) -> None:
        """
        保存数据库到文件

        Args:
            filepath: 可选的文件路径，None使用当前设置的路径

        Raises:
            DatabaseSaveError: 保存失败
        """
        target_path = filepath or self._filepath

        if not target_path:
            raise DatabaseSaveError("No filepath specified")

        try:
            # 确保目录存在
            Path(target_path).parent.mkdir(parents=True, exist_ok=True)

            # 准备数据
            save_data = {
                'version': self.VERSION,
                'created_at': self._created_at.isoformat(),
                'updated_at': datetime.now().isoformat(),
                'data': self._serialize_data()
            }

            # 写入临时文件
            temp_path = target_path + '.tmp'
            with open(temp_path, 'w', encoding='utf-8') as f:
                json.dump(save_data, f, indent=2, ensure_ascii=False)

            # 原子性替换
            if os.path.exists(target_path):
                os.replace(temp_path, target_path)
            else:
                os.rename(temp_path, target_path)

            self._dirty = False

        except Exception as e:
            raise DatabaseSaveError(f"Failed to save database: {e}")

    def load(self, filepath: Optional[str] = None) -> None:
        """
        从文件加载数据库

        Args:
            filepath: 可选的文件路径，None使用当前设置的路径

        Raises:
            DatabaseLoadError: 加载失败
        """
        target_path = filepath or self._filepath

        if not target_path:
            raise DatabaseLoadError("No filepath specified")

        if not os.path.exists(target_path):
            raise DatabaseLoadError(f"File not found: {target_path}")

        try:
            with open(target_path, 'r', encoding='utf-8') as f:
                save_data = json.load(f)

            # 验证版本
            if save_data.get('version') != self.VERSION:
                # 可以在这里添加版本迁移逻辑
                pass

            # 恢复数据
            self._data = self._deserialize_data(save_data.get('data', {}))
            self._created_at = datetime.fromisoformat(
                save_data.get('created_at', datetime.now().isoformat())
            )
            self._dirty = False

        except json.JSONDecodeError as e:
            raise DatabaseLoadError(f"Invalid JSON format: {e}")
        except Exception as e:
            raise DatabaseLoadError(f"Failed to load database: {e}")

    def merge(self, other: 'CoverageDatabase') -> None:
        """合并另一个数据库"""
        super().merge(other)
        self._dirty = True

    def clear(self) -> None:
        """清空所有数据"""
        super().clear()
        self._dirty = True

    def _serialize_data(self) -> Dict:
        """
        序列化数据为JSON兼容格式

        Returns:
            可序列化的字典
        """
        serialized = {}

        for cg_name, cg_data in self._data.items():
            serialized[cg_name] = {
                'coverpoints': {},
                'crosses': {},
                'sample_count': cg_data['sample_count'],
                'timestamp': cg_data['timestamp'].isoformat() if cg_data['timestamp'] else None
            }

            # 序列化coverpoints
            for cp_name, cp_data in cg_data['coverpoints'].items():
                serialized[cg_name]['coverpoints'][cp_name] = {
                    'bins': dict(cp_data['bins']),  # defaultdict转普通dict
                    'total_samples': cp_data['total_samples'],
                    'timestamp': cp_data['timestamp'].isoformat() if cp_data['timestamp'] else None
                }

            # 序列化crosses
            for cross_name, cross_data in cg_data['crosses'].items():
                # 将元组键转换为字符串键（JSON不支持元组键）
                bins_serialized = {
                    str(k): v for k, v in cross_data['bins'].items()
                }
                serialized[cg_name]['crosses'][cross_name] = {
                    'bins': bins_serialized,
                    'total_samples': cross_data['total_samples'],
                    'timestamp': cross_data['timestamp'].isoformat() if cross_data['timestamp'] else None
                }

        return serialized

    def _deserialize_data(self, data: Dict) -> Dict:
        """
        从JSON格式反序列化数据

        Args:
            data: 序列化的数据字典

        Returns:
            反序列化后的数据结构
        """
        from collections import defaultdict

        deserialized = {}

        for cg_name, cg_data in data.items():
            deserialized[cg_name] = {
                'coverpoints': {},
                'crosses': {},
                'sample_count': cg_data['sample_count'],
                'timestamp': datetime.fromisoformat(cg_data['timestamp']) if cg_data.get('timestamp') else None
            }

            # 反序列化coverpoints
            for cp_name, cp_data in cg_data.get('coverpoints', {}).items():
                deserialized[cg_name]['coverpoints'][cp_name] = {
                    'bins': defaultdict(int, cp_data.get('bins', {})),
                    'total_samples': cp_data.get('total_samples', 0),
                    'timestamp': datetime.fromisoformat(cp_data['timestamp']) if cp_data.get('timestamp') else None
                }

            # 反序列化crosses
            for cross_name, cross_data in cg_data.get('crosses', {}).items():
                # 将字符串键转换回元组键
                bins_deserialized = {}
                for bin_str, count in cross_data.get('bins', {}).items():
                    try:
                        # 尝试解析元组字符串 "(1, 2, 3)"
                        bin_tuple = eval(bin_str)
                        bins_deserialized[bin_tuple] = count
                    except:
                        # 如果解析失败，使用字符串键
                        bins_deserialized[bin_str] = count

                deserialized[cg_name]['crosses'][cross_name] = {
                    'bins': defaultdict(int, bins_deserialized),
                    'total_samples': cross_data.get('total_samples', 0),
                    'timestamp': datetime.fromisoformat(cross_data['timestamp']) if cross_data.get('timestamp') else None
                }

        return deserialized

    def is_dirty(self) -> bool:
        """检查数据是否有未保存的修改"""
        return self._dirty

    def auto_save(self) -> None:
        """
        自动保存（如果数据有修改且设置了文件路径）
        """
        if self._dirty and self._filepath:
            self.save()
