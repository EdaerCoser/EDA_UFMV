"""
Coverage Report Formatters Module

覆盖率报告生成器模块，支持多种报告格式。
"""

from .base import CoverageReport
from .html_report import HTMLCoverageReport
from .json_report import JSONCoverageReport
from .ucis_report import UCISCoverageReport, UCISJSONReport
from .factory import (
    ReportFactory,
    create_report,
    generate_report
)

__all__ = [
    # 基础接口
    "CoverageReport",

    # 报告生成器
    "HTMLCoverageReport",
    "JSONCoverageReport",
    "UCISCoverageReport",
    "UCISJSONReport",

    # 工厂和便捷函数
    "ReportFactory",
    "create_report",
    "generate_report",
]
