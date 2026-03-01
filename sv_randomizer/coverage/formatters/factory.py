"""
Coverage Report Factory

报告生成器工厂，用于创建不同格式的覆盖率报告。
"""

from typing import Optional, Dict

from .base import CoverageReport
from .html_report import HTMLCoverageReport
from .json_report import JSONCoverageReport
from .ucis_report import UCISCoverageReport, UCISJSONReport


class ReportFactory:
    """
    报告生成器工厂类

    支持的报告类型：
    - "html": HTML可视化报告
    - "json": JSON机器可读报告
    - "ucis": UCIS XML报告（IEEE 1687）
    - "ucis_json": UCIS JSON报告
    """

    _formatters: Dict[str, type] = {
        "html": HTMLCoverageReport,
        "json": JSONCoverageReport,
        "ucis": UCISCoverageReport,
        "ucis_json": UCISJSONReport
    }

    @classmethod
    def get_reporter(
        cls,
        format: str = "html",
        title: str = "Coverage Report"
    ) -> CoverageReport:
        """
        获取报告生成器实例

        Args:
            format: 报告格式 ("html", "json", "ucis", "ucis_json")
            title: 报告标题

        Returns:
            报告生成器实例

        Raises:
            ValueError: 如果格式不支持
        """
        format_lower = format.lower()

        if format_lower not in cls._formatters:
            raise ValueError(
                f"Unknown report format: {format}. "
                f"Available formats: {', '.join(cls.get_available_formats())}"
            )

        reporter_class = cls._formatters[format_lower]
        return reporter_class(title=title)

    @classmethod
    def get_available_formats(cls) -> list:
        """
        获取所有可用的报告格式

        Returns:
            格式名称列表
        """
        return list(cls._formatters.keys())

    @classmethod
    def register_formatter(cls, format: str, formatter_class: type) -> None:
        """
        注册自定义报告格式

        Args:
            format: 格式名称
            formatter_class: 报告生成器类，必须继承CoverageReport

        Raises:
            ValueError: 如果formatter_class不是CoverageReport的子类
        """
        if not issubclass(formatter_class, CoverageReport):
            raise ValueError(
                f"Formatter class must inherit from CoverageReport, "
                f"got {formatter_class}"
            )

        cls._formatters[format.lower()] = formatter_class

    @classmethod
    def create_html_report(cls, title: str = "Coverage Report") -> HTMLCoverageReport:
        """创建HTML报告生成器（便捷方法）"""
        return cls.get_reporter("html", title)

    @classmethod
    def create_json_report(cls, title: str = "Coverage Report") -> JSONCoverageReport:
        """创建JSON报告生成器（便捷方法）"""
        return cls.get_reporter("json", title)

    @classmethod
    def create_ucis_report(cls, title: str = "Coverage Report") -> UCISCoverageReport:
        """创建UCIS报告生成器（便捷方法）"""
        return cls.get_reporter("ucis", title)


# 便捷函数
def create_report(format: str = "html", title: str = "Coverage Report") -> CoverageReport:
    """
    创建报告生成器（便捷函数）

    Args:
        format: 报告格式
        title: 报告标题

    Returns:
        报告生成器实例
    """
    return ReportFactory.get_reporter(format, title)


def generate_report(
    data: Dict,
    format: str = "html",
    filepath: Optional[str] = None,
    title: str = "Coverage Report"
) -> str:
    """
    生成并保存报告（便捷函数）

    Args:
        data: 覆盖率数据
        format: 报告格式
        filepath: 可选的文件路径
        title: 报告标题

    Returns:
        报告内容字符串
    """
    reporter = create_report(format, title)
    content = reporter.generate(data)

    if filepath:
        reporter.save(content, filepath)

    return content
