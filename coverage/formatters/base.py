"""
Coverage Report Base Interface

定义覆盖率报告生成的抽象接口。
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from pathlib import Path


class CoverageReport(ABC):
    """
    覆盖率报告基类

    定义所有报告生成器必须实现的方法。

    支持的格式：
    - HTML: 可视化网页报告
    - JSON: 机器可读的JSON报告
    - UCIS: EDA行业标准格式（IEEE 1687）
    """

    def __init__(self, title: str = "Coverage Report"):
        """
        初始化报告生成器

        Args:
            title: 报告标题
        """
        self.title = title
        self._data: Optional[Dict[str, Any]] = None

    @abstractmethod
    def generate(self, coverage_data: Dict[str, Any]) -> str:
        """
        生成报告内容

        Args:
            coverage_data: 覆盖率数据字典

        Returns:
            报告内容字符串
        """
        pass

    @abstractmethod
    def get_format(self) -> str:
        """
        获取报告格式

        Returns:
            格式名称 ("html", "json", "ucis")
        """
        pass

    def save(
        self,
        content: str,
        filepath: Optional[str] = None,
        auto_open: bool = False
    ) -> str:
        """
        保存报告到文件

        Args:
            content: 报告内容
            filepath: 文件路径，None表示自动生成
            auto_open: 是否自动打开文件（仅HTML）

        Returns:
            保存的文件路径
        """
        if filepath is None:
            filepath = f"coverage_report.{self.get_format()}"

        # 确保目录存在
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)

        # 写入文件
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

        # 自动打开（如果需要）
        if auto_open and self.get_format() == "html":
            import webbrowser
            import os
            webbrowser.open(f"file://{os.path.abspath(filepath)}")

        return filepath

    def _format_percentage(self, value: float) -> str:
        """
        格式化百分比显示

        Args:
            value: 百分比值

        Returns:
            格式化后的字符串
        """
        return f"{value:.2f}%"

    def _get_coverage_color(self, coverage: float) -> str:
        """
        根据覆盖率获取颜色代码

        Args:
            coverage: 覆盖率百分比

        Returns:
            颜色代码（HTML格式）
        """
        if coverage >= 90:
            return "#28a745"  # 绿色
        elif coverage >= 70:
            return "#ffc107"  # 黄色
        elif coverage >= 50:
            return "#fd7e14"  # 橙色
        else:
            return "#dc3545"  # 红色
