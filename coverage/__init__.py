"""
EDA_UFMV Coverage System

功能覆盖率系统实现，支持SystemVerilog风格的覆盖率定义。
"""

__version__ = "0.2.0"

# Core classes
from .core.covergroup import CoverGroup
from .core.coverpoint import CoverPoint
from .core.cross import Cross
from .core.bin import (
    ValueBin,
    RangeBin,
    WildcardBin,
    AutoBin,
    IgnoreBin,
    IllegalBin,
)

# Database classes
from .database.base import CoverageDatabase
from .database.memory_db import MemoryCoverageDatabase
from .database.file_db import FileCoverageDatabase
from .database.factory import DatabaseFactory

# Report classes
from .formatters.base import CoverageReport
from .formatters.html_report import HTMLCoverageReport
from .formatters.json_report import JSONCoverageReport
from .formatters.ucis_report import UCISCoverageReport
from .formatters.factory import ReportFactory

# API decorators
from .api.decorators import covergroup, coverpoint, cross

# Exceptions
from .utils.exceptions import (
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
    # Version
    "__version__",
    # Core classes
    "CoverGroup",
    "CoverPoint",
    "Cross",
    # Bin types
    "ValueBin",
    "RangeBin",
    "WildcardBin",
    "AutoBin",
    "IgnoreBin",
    "IllegalBin",
    # Database classes
    "CoverageDatabase",
    "MemoryCoverageDatabase",
    "FileCoverageDatabase",
    "DatabaseFactory",
    # Report classes
    "CoverageReport",
    "HTMLCoverageReport",
    "JSONCoverageReport",
    "UCISCoverageReport",
    "ReportFactory",
    # API decorators
    "covergroup",
    "coverpoint",
    "cross",
    # Exceptions
    "CoverageError",
    "CoverGroupError",
    "InvalidCoverPointError",
    "SamplingError",
    "CoverageMergeError",
    "CoverPointError",
    "BinDefinitionError",
    "BinOverlapError",
    "InvalidSampleError",
    "CrossError",
    "InvalidCrossError",
    "CrossBinOverflowError",
    "DatabaseError",
    "DatabaseConnectionError",
    "DatabaseWriteError",
    "DatabaseReadError",
    "ReportError",
    "ReportGenerationError",
    "InvalidReportFormatError",
]
