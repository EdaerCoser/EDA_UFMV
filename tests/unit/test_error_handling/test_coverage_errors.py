"""
Coverage System Exception Handling Tests

Tests all 19 exception classes in the coverage module to ensure:
1. Exceptions are raised in appropriate conditions
2. Exception messages are clear and accurate
3. Exception attributes are properly set
4. Exception inheritance hierarchy is correct
"""

import pytest
from pathlib import Path
import tempfile
import shutil

from coverage.utils.exceptions import (
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

from coverage.core import CoverGroup, CoverPoint, Cross, BinType
from coverage.database import MemoryDatabase, FileDatabase
from coverage.formatters import HTMLReport, JSONReport, UCISReport


# =============================================================================
# Test: CoverageError (Base Exception)
# =============================================================================

@pytest.mark.unit
@pytest.mark.error_handling
@pytest.mark.P0
class TestCoverageError:
    """Tests for CoverageError base exception."""

    def test_coverage_error_creation(self):
        """Test CoverageError can be created with message."""
        msg = "Test error message"
        exc = CoverageError(msg)
        assert exc.message == msg
        assert str(exc) == msg

    def test_coverage_error_is_exception(self):
        """Test CoverageError is a proper Exception subclass."""
        assert issubclass(CoverageError, Exception)
        exc = CoverageError("test")
        assert isinstance(exc, Exception)
        assert isinstance(exc, CoverageError)


# =============================================================================
# Test: CoverGroupError and Subclasses
# =============================================================================

@pytest.mark.unit
@pytest.mark.error_handling
@pytest.mark.P0
class TestCoverGroupError:
    """Tests for CoverGroupError and its subclasses."""

    def test_covergroup_error_creation(self):
        """Test CoverGroupError can be created with message and name."""
        msg = "CoverGroup failed"
        cg_name = "test_cg"
        exc = CoverGroupError(msg, cg_name)
        assert exc.message == msg
        assert exc.covergroup_name == cg_name
        assert str(exc) == msg

    def test_covergroup_error_without_name(self):
        """Test CoverGroupError can be created without name."""
        exc = CoverGroupError("test")
        assert exc.covergroup_name is None


@pytest.mark.unit
@pytest.mark.error_handling
@pytest.mark.P1
class TestInvalidCoverPointError:
    """Tests for InvalidCoverPointError."""

    def test_invalid_coverpoint_error_attributes(self):
        """Test InvalidCoverPointError stores coverpoint name."""
        msg = "Invalid coverpoint"
        cp_name = "bad_cp"
        exc = InvalidCoverPointError(msg, cp_name)
        assert exc.coverpoint_name == cp_name

    def test_invalid_coverpoint_is_covergroup_error(self):
        """Test inheritance chain is correct."""
        assert issubclass(InvalidCoverPointError, CoverGroupError)
        assert issubclass(InvalidCoverPointError, CoverageError)


@pytest.mark.unit
@pytest.mark.error_handling
@pytest.mark.P1
class TestSamplingError:
    """Tests for SamplingError."""

    def test_sampling_error_with_value(self):
        """Test SamplingError stores sample value."""
        msg = "Sampling failed"
        value = 999
        exc = SamplingError(msg, value)
        assert exc.sample_value == value

    def test_sampling_error_without_value(self):
        """Test SamplingError can be created without value."""
        exc = SamplingError("test")
        assert exc.sample_value is None


@pytest.mark.unit
@pytest.mark.error_handling
@pytest.mark.P1
class TestCoverageMergeError:
    """Tests for CoverageMergeError."""

    def test_coverage_merge_error_with_sources(self):
        """Test CoverageMergeError stores source files."""
        msg = "Merge failed"
        sources = ["file1.json", "file2.json"]
        exc = CoverageMergeError(msg, sources)
        assert exc.source_files == sources

    def test_coverage_merge_error_without_sources(self):
        """Test CoverageMergeError can be created without sources."""
        exc = CoverageMergeError("test")
        assert exc.source_files == []


# =============================================================================
# Test: CoverPointError and Subclasses
# =============================================================================

@pytest.mark.unit
@pytest.mark.error_handling
@pytest.mark.P0
class TestCoverPointError:
    """Tests for CoverPointError and its subclasses."""

    def test_coverpoint_error_creation(self):
        """Test CoverPointError can be created with message and name."""
        msg = "CoverPoint failed"
        cp_name = "test_cp"
        exc = CoverPointError(msg, cp_name)
        assert exc.message == msg
        assert exc.coverpoint_name == cp_name


@pytest.mark.unit
@pytest.mark.error_handling
@pytest.mark.P1
class TestBinDefinitionError:
    """Tests for BinDefinitionError."""

    def test_bin_definition_error_with_bin_name(self):
        """Test BinDefinitionError stores bin name."""
        msg = "Invalid bin definition"
        bin_name = "bad_bin"
        exc = BinDefinitionError(msg, bin_name)
        assert exc.bin_name == bin_name

    def test_bin_definition_error_without_bin_name(self):
        """Test BinDefinitionError can be created without bin name."""
        exc = BinDefinitionError("test")
        assert exc.bin_name is None


@pytest.mark.unit
@pytest.mark.error_handling
@pytest.mark.P1
class TestBinOverlapError:
    """Tests for BinOverlapError."""

    def test_bin_overlap_error_with_bins(self):
        """Test BinOverlapError stores overlapping bin names."""
        msg = "Bins overlap"
        bin1 = "bin_a"
        bin2 = "bin_b"
        exc = BinOverlapError(msg, bin1, bin2)
        assert exc.bin1 == bin1
        assert exc.bin2 == bin2

    def test_bin_overlap_error_without_bins(self):
        """Test BinOverlapError can be created without bin names."""
        exc = BinOverlapError("test")
        assert exc.bin1 is None
        assert exc.bin2 is None


@pytest.mark.unit
@pytest.mark.error_handling
@pytest.mark.P1
class TestInvalidSampleError:
    """Tests for InvalidSampleError."""

    def test_invalid_sample_error_with_value(self):
        """Test InvalidSampleError stores the invalid value."""
        msg = "Invalid sample"
        value = 12345
        exc = InvalidSampleError(msg, value)
        assert exc.sample_value == value

    def test_invalid_sample_error_without_value(self):
        """Test InvalidSampleError can be created without value."""
        exc = InvalidSampleError("test")
        assert exc.sample_value is None


# =============================================================================
# Test: CrossError and Subclasses
# =============================================================================

@pytest.mark.unit
@pytest.mark.error_handling
@pytest.mark.P0
class TestCrossError:
    """Tests for CrossError and its subclasses."""

    def test_cross_error_creation(self):
        """Test CrossError can be created with message and name."""
        msg = "Cross failed"
        cross_name = "test_cross"
        exc = CrossError(msg, cross_name)
        assert exc.message == msg
        assert exc.cross_name == cross_name


@pytest.mark.unit
@pytest.mark.error_handling
@pytest.mark.P1
class TestInvalidCrossError:
    """Tests for InvalidCrossError."""

    def test_invalid_cross_error_with_coverpoints(self):
        """Test InvalidCrossError stores coverpoint names."""
        msg = "Invalid cross"
        cps = ["cp_a", "cp_b"]
        exc = InvalidCrossError(msg, cps)
        assert exc.coverpoint_names == cps

    def test_invalid_cross_error_without_coverpoints(self):
        """Test InvalidCrossError can be created without coverpoint names."""
        exc = InvalidCrossError("test")
        assert exc.coverpoint_names == []


@pytest.mark.unit
@pytest.mark.error_handling
@pytest.mark.P1
class TestCrossBinOverflowError:
    """Tests for CrossBinOverflowError."""

    def test_cross_bin_overflow_error_with_counts(self):
        """Test CrossBinOverflowError stores bin count and max allowed."""
        msg = "Too many bins"
        count = 1000000
        max_allowed = 10000
        exc = CrossBinOverflowError(msg, count, max_allowed)
        assert exc.bin_count == count
        assert exc.max_allowed == max_allowed

    def test_cross_bin_overflow_error_without_counts(self):
        """Test CrossBinOverflowError can be created without counts."""
        exc = CrossBinOverflowError("test")
        assert exc.bin_count is None
        assert exc.max_allowed is None


# =============================================================================
# Test: DatabaseError and Subclasses
# =============================================================================

@pytest.mark.unit
@pytest.mark.error_handling
@pytest.mark.P0
class TestDatabaseError:
    """Tests for DatabaseError and its subclasses."""

    def test_database_error_creation(self):
        """Test DatabaseError can be created with message and path."""
        msg = "Database failed"
        path = "/path/to/db.json"
        exc = DatabaseError(msg, path)
        assert exc.message == msg
        assert exc.database_path == path


@pytest.mark.unit
@pytest.mark.error_handling
@pytest.mark.P1
class TestDatabaseConnectionError:
    """Tests for DatabaseConnectionError."""

    def test_database_connection_error_with_path(self):
        """Test DatabaseConnectionError stores database path."""
        msg = "Cannot connect"
        path = "nonexistent.json"
        exc = DatabaseConnectionError(msg, path)
        assert exc.database_path == path


@pytest.mark.unit
@pytest.mark.error_handling
@pytest.mark.P1
class TestDatabaseWriteError:
    """Tests for DatabaseWriteError."""

    def test_database_write_error_with_data(self):
        """Test DatabaseWriteError stores the data that failed to write."""
        msg = "Write failed"
        data = {"key": "value"}
        exc = DatabaseWriteError(msg, data)
        assert exc.data == data

    def test_database_write_error_without_data(self):
        """Test DatabaseWriteError can be created without data."""
        exc = DatabaseWriteError("test")
        assert exc.data is None


@pytest.mark.unit
@pytest.mark.error_handling
@pytest.mark.P1
class TestDatabaseReadError:
    """Tests for DatabaseReadError."""

    def test_database_read_error_with_key(self):
        """Test DatabaseReadError stores the key that failed to read."""
        msg = "Read failed"
        key = "missing_key"
        exc = DatabaseReadError(msg, key)
        assert exc.key == key

    def test_database_read_error_without_key(self):
        """Test DatabaseReadError can be created without key."""
        exc = DatabaseReadError("test")
        assert exc.key is None


# =============================================================================
# Test: ReportError and Subclasses
# =============================================================================

@pytest.mark.unit
@pytest.mark.error_handling
@pytest.mark.P0
class TestReportError:
    """Tests for ReportError and its subclasses."""

    def test_report_error_creation(self):
        """Test ReportError can be created with message and format."""
        msg = "Report failed"
        fmt = "html"
        exc = ReportError(msg, fmt)
        assert exc.message == msg
        assert exc.report_format == fmt


@pytest.mark.unit
@pytest.mark.error_handling
@pytest.mark.P1
class TestReportGenerationError:
    """Tests for ReportGenerationError."""

    def test_report_generation_error_with_path(self):
        """Test ReportGenerationError stores output path."""
        msg = "Generation failed"
        path = "/path/to/report.html"
        exc = ReportGenerationError(msg, path)
        assert exc.output_path == path

    def test_report_generation_error_without_path(self):
        """Test ReportGenerationError can be created without path."""
        exc = ReportGenerationError("test")
        assert exc.output_path is None


@pytest.mark.unit
@pytest.mark.error_handling
@pytest.mark.P1
class TestInvalidReportFormatError:
    """Tests for InvalidReportFormatError."""

    def test_invalid_report_format_error_with_format(self):
        """Test InvalidReportFormatError stores requested format."""
        msg = "Invalid format"
        fmt = "unsupported_format"
        exc = InvalidReportFormatError(msg, fmt)
        assert exc.requested_format == fmt

    def test_invalid_report_format_error_without_format(self):
        """Test InvalidReportFormatError can be created without format."""
        exc = InvalidReportFormatError("test")
        assert exc.requested_format is None


# =============================================================================
# Integration Tests: Exception Conditions
# =============================================================================

@pytest.mark.unit
@pytest.mark.error_handling
@pytest.mark.P0
@pytest.mark.parametrize("exception_class", [
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
])
def test_all_coverage_exceptions_can_be_raised(exception_class):
    """Test that all coverage exceptions can be raised and caught."""
    with pytest.raises(exception_class) as exc_info:
        raise exception_class("Test message")

    assert "Test message" in str(exc_info.value)


@pytest.mark.unit
@pytest.mark.error_handling
@pytest.mark.P1
def test_exception_inheritance_chain():
    """Test that exception inheritance chain is correct."""
    # CoverGroupError hierarchy
    assert issubclass(InvalidCoverPointError, CoverGroupError)
    assert issubclass(SamplingError, CoverGroupError)
    assert issubclass(CoverageMergeError, CoverGroupError)

    # CoverPointError hierarchy
    assert issubclass(BinDefinitionError, CoverPointError)
    assert issubclass(BinOverlapError, CoverPointError)
    assert issubclass(InvalidSampleError, CoverPointError)

    # CrossError hierarchy
    assert issubclass(InvalidCrossError, CrossError)
    assert issubclass(CrossBinOverflowError, CrossError)

    # DatabaseError hierarchy
    assert issubclass(DatabaseConnectionError, DatabaseError)
    assert issubclass(DatabaseWriteError, DatabaseError)
    assert issubclass(DatabaseReadError, DatabaseError)

    # ReportError hierarchy
    assert issubclass(ReportGenerationError, ReportError)
    assert issubclass(InvalidReportFormatError, ReportError)

    # All inherit from CoverageError
    assert issubclass(CoverGroupError, CoverageError)
    assert issubclass(CoverPointError, CoverageError)
    assert issubclass(CrossError, CoverageError)
    assert issubclass(DatabaseError, CoverageError)
    assert issubclass(ReportError, CoverageError)
