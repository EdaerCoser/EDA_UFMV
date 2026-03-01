"""
Coverage Utils Package

覆盖率系统工具模块。
"""

from .exceptions import (
    CoverageError,
    CoverGroupError,
    InvalidCoverPointError,
    SamplingError,
    CoverageMergeError,
    CoverPointError,
    BinDefinitionError,
    BinOverlapError,
    InvalidSampleError,
    CrossError,
    InvalidCrossError,
    CrossBinOverflowError,
    DatabaseError,
    DatabaseConnectionError,
    DatabaseWriteError,
    DatabaseReadError,
    ReportError,
    ReportGenerationError,
    InvalidReportFormatError,
)

__all__ = [
    # Base exception
    "CoverageError",
    # CoverGroup exceptions
    "CoverGroupError",
    "InvalidCoverPointError",
    "SamplingError",
    "CoverageMergeError",
    # CoverPoint exceptions
    "CoverPointError",
    "BinDefinitionError",
    "BinOverlapError",
    "InvalidSampleError",
    # Cross exceptions
    "CrossError",
    "InvalidCrossError",
    "CrossBinOverflowError",
    # Database exceptions
    "DatabaseError",
    "DatabaseConnectionError",
    "DatabaseWriteError",
    "DatabaseReadError",
    # Report exceptions
    "ReportError",
    "ReportGenerationError",
    "InvalidReportFormatError",
]
