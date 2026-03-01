"""
Cross Coverage Implementation

实现多变量交叉覆盖率，对应SystemVerilog的cross coverage。

Cross Coverage是两个或多个CoverPoint的笛卡尔积，
用于验证变量组合的覆盖情况。
"""

from typing import Any, Dict, List, Optional, Callable, Tuple
from collections import defaultdict
from itertools import product


class Cross:
    """
    Cross覆盖率实现

    对应SystemVerilog:
        cross addr_cross;
            bins cross_bins[] = binsof cp1 X cp2;

    特性：
    - 计算CoverPoint的笛卡尔积
    - 支持过滤函数
    - 懒加载优化（大规模Cross）
    - 组合命中统计
    """

    def __init__(
        self,
        name: str,
        coverpoints: List[str],
        cross_filter: Optional[Callable[[Tuple[Any, ...]], bool]] = None
    ):
        """
        初始化Cross

        Args:
            name: Cross名称
            coverpoints: 涉及的CoverPoint名称列表
            cross_filter: 可选的过滤函数，返回True表示包含该组合
        """
        self.name = name
        self._coverpoint_names = coverpoints
        self._cross_filter = cross_filter

        # 状态
        self._enabled = True
        self._parent = None  # Set by parent CoverGroup
        self._database = None

        # Bin管理（懒加载）
        self._bins: Dict[Tuple[Any, ...], int] = defaultdict(int)
        self._bins_loaded = False
        self._total_bins = 0
        self._sample_count = 0

    def _set_parent(self, parent) -> None:
        """
        设置父CoverGroup（内部使用）

        Args:
            parent: 父CoverGroup实例
        """
        self._parent = parent

    def set_database(self, database) -> None:
        """
        设置覆盖率数据库（内部使用）

        Args:
            database: CoverageDatabase实例
        """
        self._database = database

    def _get_coverpoints(self) -> List:
        """
        获取关联的CoverPoint实例

        Returns:
            CoverPoint实例列表
        """
        if not self._parent:
            return []

        coverpoints = []
        for cp_name in self._coverpoint_names:
            cp = self._parent.get_coverpoint(cp_name)
            if cp:
                coverpoints.append(cp)
        return coverpoints

    def _initialize_bins(self) -> None:
        """
        初始化所有可能的bin组合（笛卡尔积）

        懒加载：只在需要时才计算所有组合
        """
        if self._bins_loaded:
            return

        coverpoints = self._get_coverpoints()
        if not coverpoints:
            return

        # 获取每个CoverPoint的所有bin名称
        all_bins = []
        for cp in coverpoints:
            bin_names = list(cp._bins.keys())
            if not bin_names:
                # 如果CoverPoint没有bins，使用空列表
                bin_names = ['']
            all_bins.append(bin_names)

        # 计算笛卡尔积
        total_combinations = 1
        for bins in all_bins:
            total_combinations *= len(bins)

        # 如果组合数太大，使用懒加载策略
        if total_combinations > 10000:
            # 大规模Cross：不预生成所有组合
            self._total_bins = total_combinations
            self._bins_loaded = True
            return

        # 小规模Cross：预生成所有组合
        for bin_tuple in product(*all_bins):
            # 应用过滤函数
            if self._cross_filter and not self._cross_filter(bin_tuple):
                continue

            self._bins[bin_tuple] = 0

        self._total_bins = len(self._bins)
        self._bins_loaded = True

    def sample(self, **kwargs) -> None:
        """
        触发Cross采样

        Args:
            **kwargs: 变量名到值的映射
        """
        if not self._enabled:
            return

        # 确保bins已初始化
        if not self._bins_loaded:
            self._initialize_bins()

        # 获取各个CoverPoint的bin名称
        bin_names = []
        coverpoints = self._get_coverpoints()

        if len(coverpoints) != len(self._coverpoint_names):
            # CoverPoint不完整，跳过采样
            return

        # 收集每个CoverPoint命中的bin名称
        for cp in coverpoints:
            matched_bin = None

            # 检查哪个bin匹配当前值
            for bin_name, bin_obj in cp._bins.items():
                # 从kwargs获取采样值
                sample_expr = cp._sample_expr
                if callable(sample_expr):
                    sample_value = sample_expr(kwargs)
                else:
                    sample_value = kwargs.get(sample_expr)

                if sample_value is not None and bin_obj.match(sample_value):
                    matched_bin = bin_name
                    break

            if matched_bin is None:
                # 没有匹配的bin，跳过此次采样
                return

            bin_names.append(matched_bin)

        # 构造bin元组
        bin_tuple = tuple(bin_names)

        # 应用过滤函数
        if self._cross_filter and not self._cross_filter(bin_tuple):
            return

        # 懒加载模式下，首次遇到组合时添加
        if len(self._bins) < self._total_bins and bin_tuple not in self._bins:
            self._bins[bin_tuple] = 0

        # 增加命中计数
        if bin_tuple in self._bins:
            self._bins[bin_tuple] += 1
            self._sample_count += 1

            # 更新数据库
            if self._database:
                self._database.record_cross_sample(
                    self.name,
                    bin_tuple,
                    self._parent.name if self._parent else ""
                )

    def get_coverage(self) -> float:
        """
        计算Cross覆盖率百分比

        Returns:
            覆盖率百分比 (0.0 - 100.0)
        """
        if not self._bins_loaded:
            self._initialize_bins()

        if self._total_bins == 0:
            return 100.0  # 空Cross

        covered_bins = sum(1 for count in self._bins.values() if count > 0)
        return (covered_bins / self._total_bins) * 100.0

    def get_bin_counts(self) -> tuple[int, int]:
        """
        获取bin计数统计

        Returns:
            Tuple of (total_bins, covered_bins)
        """
        if not self._bins_loaded:
            self._initialize_bins()

        covered_bins = sum(1 for count in self._bins.values() if count > 0)
        return self._total_bins, covered_bins

    def get_coverage_details(self) -> Dict[str, Any]:
        """
        获取详细的覆盖率信息

        Returns:
            包含详细信息的字典
        """
        if not self._bins_loaded:
            self._initialize_bins()

        total_bins, covered_bins = self.get_bin_counts()

        # 获取命中组合详情（最多显示前100个）
        bins_details = {}
        for i, (bin_tuple, count) in enumerate(list(self._bins.items())[:100]):
            bins_details[str(bin_tuple)] = {
                'hit_count': count,
                'covered': count > 0
            }

        return {
            'name': self.name,
            'coverage': self.get_coverage(),
            'total_bins': total_bins,
            'covered_bins': covered_bins,
            'sample_count': self._sample_count,
            'coverpoints': self._coverpoint_names,
            'bins': bins_details,
            'is_lazy_loaded': len(self._bins) < self._total_bins
        }

    def is_enabled(self) -> bool:
        """检查是否启用"""
        return self._enabled

    def enable(self) -> None:
        """启用Cross"""
        self._enabled = True

    def disable(self) -> None:
        """禁用Cross"""
        self._enabled = False

    def __repr__(self) -> str:
        return (
            f"Cross(name='{self.name}', "
            f"coverage={self.get_coverage():.2f}%, "
            f"coverpoints={len(self._coverpoint_names)}, "
            f"bins={self._total_bins})"
        )


class CrossBuilder:
    """
    Cross构建器 - 简化Cross对象的创建

    使用构建器模式可以链式调用配置Cross
    """

    def __init__(self, name: str):
        """
        初始化构建器

        Args:
            name: Cross名称
        """
        self._name = name
        self._coverpoints: List[str] = []
        self._cross_filter: Optional[Callable] = None

    def add_coverpoint(self, coverpoint_name: str) -> 'CrossBuilder':
        """
        添加CoverPoint

        Args:
            coverpoint_name: CoverPoint名称

        Returns:
            self，支持链式调用
        """
        self._coverpoints.append(coverpoint_name)
        return self

    def add_coverpoints(self, *coverpoint_names: str) -> 'CrossBuilder':
        """
        添加多个CoverPoint

        Args:
            *coverpoint_names: CoverPoint名称列表

        Returns:
            self，支持链式调用
        """
        self._coverpoints.extend(coverpoint_names)
        return self

    def with_filter(self, filter_func: Callable[[Tuple[Any, ...]], bool]) -> 'CrossBuilder':
        """
        设置过滤函数

        Args:
            filter_func: 过滤函数，返回True表示包含该组合

        Returns:
            self，支持链式调用
        """
        self._cross_filter = filter_func
        return self

    def build(self) -> Cross:
        """
        构建Cross对象

        Returns:
            Cross实例
        """
        if not self._coverpoints:
            raise ValueError(f"Cross '{self._name}' must have at least one coverpoint")

        return Cross(
            name=self._name,
            coverpoints=self._coverpoints,
            cross_filter=self._cross_filter
        )


def create_cross(name: str, *coverpoints: str) -> CrossBuilder:
    """
    创建Cross的便捷函数

    Args:
        name: Cross名称
        *coverpoints: CoverPoint名称列表

    Returns:
        CrossBuilder实例

    Example:
        cross = create_cross("addr_data_cross", "addr_cp", "data_cp")
                  .with_filter(lambda bins: bins[0] != "illegal")
                  .build()
    """
    builder = CrossBuilder(name)
    return builder.add_coverpoints(*coverpoints)
