"""
Coverage System Exceptions

定义覆盖率系统中使用的所有异常类型。

异常层次结构:
    CoverageError
    ├── CoverGroupError
    │   ├── InvalidCoverPointError
    │   ├── SamplingError
    │   └── CoverageMergeError
    ├── CoverPointError
    │   ├── BinDefinitionError
    │   ├── BinOverlapError
    │   └── InvalidSampleError
    ├── CrossError
    │   ├── InvalidCrossError
    │   └── CrossBinOverflowError
    ├── DatabaseError
    │   ├── DatabaseConnectionError
    │   ├── DatabaseWriteError
    │   └── DatabaseReadError
    └── ReportError
        ├── ReportGenerationError
        └── InvalidReportFormatError
"""


class CoverageError(Exception):
    """覆盖率系统基础异常

    所有覆盖率相关异常的基类。
    """

    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


class CoverGroupError(CoverageError):
    """CoverGroup相关异常

    当CoverGroup定义或操作出现问题时抛出。
    """

    def __init__(self, message: str, covergroup_name: str = None):
        self.covergroup_name = covergroup_name
        super().__init__(message)


class InvalidCoverPointError(CoverGroupError):
    """无效CoverPoint异常

    当尝试添加无效的CoverPoint到CoverGroup时抛出。
    """

    def __init__(self, message: str, coverpoint_name: str = None):
        self.coverpoint_name = coverpoint_name
        super().__init__(message)


class SamplingError(CoverGroupError):
    """采样异常

    当覆盖率采样失败时抛出。
    """

    def __init__(self, message: str, sample_value=None):
        self.sample_value = sample_value
        super().__init__(message)


class CoverageMergeError(CoverGroupError):
    """覆盖率合并异常

    当合并多个覆盖率数据失败时抛出。
    """

    def __init__(self, message: str, source_files: list = None):
        self.source_files = source_files or []
        super().__init__(message)


class CoverPointError(CoverageError):
    """CoverPoint相关异常

    当CoverPoint定义或操作出现问题时抛出。
    """

    def __init__(self, message: str, coverpoint_name: str = None):
        self.coverpoint_name = coverpoint_name
        super().__init__(message)


class BinDefinitionError(CoverPointError):
    """Bin定义异常

    当Bin定义不合法时抛出。
    """

    def __init__(self, message: str, bin_name: str = None):
        self.bin_name = bin_name
        super().__init__(message)


class BinOverlapError(CoverPointError):
    """Bin重叠异常

    当检测到Bin之间存在重叠时抛出。
    """

    def __init__(self, message: str, bin1: str = None, bin2: str = None):
        self.bin1 = bin1
        self.bin2 = bin2
        super().__init__(message)


class InvalidSampleError(CoverPointError):
    """无效采样值异常

    当采样值不在任何Bin范围内时抛出。
    """

    def __init__(self, message: str, sample_value=None):
        self.sample_value = sample_value
        super().__init__(message)


class CrossError(CoverageError):
    """Cross覆盖率相关异常

    当Cross覆盖率定义或操作出现问题时抛出。
    """

    def __init__(self, message: str, cross_name: str = None):
        self.cross_name = cross_name
        super().__init__(message)


class InvalidCrossError(CrossError):
    """无效Cross异常

    当Cross定义不合法时抛出（例如：引用的CoverPoint不存在）。
    """

    def __init__(self, message: str, coverpoint_names: list = None):
        self.coverpoint_names = coverpoint_names or []
        super().__init__(message)


class CrossBinOverflowError(CrossError):
    """Cross Bin溢出异常

    当Cross生成的Bin数量超过限制时抛出。
    """

    def __init__(self, message: str, bin_count: int = None, max_allowed: int = None):
        self.bin_count = bin_count
        self.max_allowed = max_allowed
        super().__init__(message)


class DatabaseError(CoverageError):
    """数据库相关异常

    当数据库操作出现问题时抛出。
    """

    def __init__(self, message: str, database_path: str = None):
        self.database_path = database_path
        super().__init__(message)


class DatabaseConnectionError(DatabaseError):
    """数据库连接异常

    当无法连接到数据库时抛出。
    """

    def __init__(self, message: str, database_path: str = None):
        super().__init__(message, database_path)


class DatabaseWriteError(DatabaseError):
    """数据库写入异常

    当写入数据库失败时抛出。
    """

    def __init__(self, message: str, data=None):
        self.data = data
        super().__init__(message)


class DatabaseReadError(DatabaseError):
    """数据库读取异常

    当从数据库读取失败时抛出。
    """

    def __init__(self, message: str, key=None):
        self.key = key
        super().__init__(message)


class ReportError(CoverageError):
    """报告生成相关异常

    当报告生成出现问题时抛出。
    """

    def __init__(self, message: str, report_format: str = None):
        self.report_format = report_format
        super().__init__(message)


class ReportGenerationError(ReportError):
    """报告生成异常

    当生成报告内容失败时抛出。
    """

    def __init__(self, message: str, output_path: str = None):
        self.output_path = output_path
        super().__init__(message)


class InvalidReportFormatError(ReportError):
    """无效报告格式异常

    当请求的报告格式不支持时抛出。
    """

    def __init__(self, message: str, requested_format: str = None):
        self.requested_format = requested_format
        super().__init__(message)
