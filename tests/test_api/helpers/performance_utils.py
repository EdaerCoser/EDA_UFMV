"""
性能测试工具函数

提供随机化速率测量、内存使用测量和性能基线管理功能。
"""

import time
import json
import os
from typing import Dict, Any, Tuple, Optional


def measure_randomization_rate(obj, iterations: int = 1000, warmup: int = 100) -> float:
    """
    测量随机化速率

    Args:
        obj: Randomizable对象
        iterations: 测试迭代次数
        warmup: 预热次数

    Returns:
        float: 每秒随机化次数
    """
    # 预热
    for _ in range(warmup):
        obj.randomize()

    # 测量
    start = time.time()
    for _ in range(iterations):
        obj.randomize()
    elapsed = time.time() - start

    return iterations / elapsed


def measure_memory_usage(obj, iterations: int = 100) -> Tuple[int, int]:
    """
    测量内存使用

    Args:
        obj: Randomizable对象
        iterations: 测试迭代次数

    Returns:
        tuple: (当前内存, 峰值内存) bytes
    """
    import tracemalloc

    tracemalloc.start()
    try:
        for _ in range(iterations):
            obj.randomize()
        current, peak = tracemalloc.get_traced_memory()
        return current, peak
    finally:
        tracemalloc.stop()


class PerformanceBaseline:
    """
    性能基线管理

    管理性能基线数据的加载、保存和回归检测
    """

    def __init__(self, baseline_file: str = "baseline_data.json"):
        """
        Args:
            baseline_file: 基线数据文件路径
        """
        self.file = baseline_file
        self.data = self._load()

    def _load(self) -> Dict[str, Any]:
        """从文件加载基线数据"""
        if os.path.exists(self.file):
            try:
                with open(self.file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                import warnings
                warnings.warn(f"Failed to load baseline file {self.file}: {e}. Starting with empty baseline.")
                return {}
        return {}

    def save(self, data: Dict[str, Any]) -> None:
        """保存基线数据到文件"""
        try:
            # Create directory if it doesn't exist
            dir_path = os.path.dirname(self.file)
            if dir_path:
                os.makedirs(dir_path, exist_ok=True)
            with open(self.file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except (IOError, OSError) as e:
            import warnings
            warnings.warn(f"Failed to save baseline file {self.file}: {e}")

    def update(self, metric: str, value: float) -> None:
        """
        更新单个基线指标

        Args:
            metric: 指标名称
            value: 指标值
        """
        self.data[metric] = value
        self.save(self.data)

    def get(self, metric: str, default: Optional[float] = None) -> Optional[float]:
        """
        获取基线指标值

        Args:
            metric: 指标名称
            default: 默认值

        Returns:
            Optional[float]: 指标值，如果不存在则返回默认值
        """
        return self.data.get(metric, default)

    def check_regression(self, current_data: Dict[str, float], threshold: float = 0.1) -> None:
        """
        检查性能退化

        Args:
            current_data: 当前测试数据
            threshold: 退化阈值（默认10%）

        Raises:
            AssertionError: 性能退化超过阈值
        """
        import pytest

        for metric, baseline_val in self.data.items():
            current_val = current_data.get(metric)
            if current_val is None:
                continue

            # Skip zero values to avoid division by zero
            if baseline_val == 0 or current_val == 0:
                continue

            # 判断指标类型（速率越高越好，时间越低越好）
            if "rate" in metric or "throughput" in metric:
                ratio = current_val / baseline_val
            else:
                ratio = baseline_val / current_val

            if ratio < (1 - threshold):
                pytest.fail(
                    f"性能退化: {metric}\n"
                    f"  基线: {baseline_val:.2f}\n"
                    f"  当前: {current_val:.2f}\n"
                    f"  下降: {(1-ratio)*100:.1f}%"
                )
