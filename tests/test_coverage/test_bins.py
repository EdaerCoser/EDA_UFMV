"""
Unit tests for Bin system

Tests all 6 bin types: ValueBin, RangeBin, WildcardBin, AutoBin,
IgnoreBin, and IllegalBin.
"""

import pytest
from coverage.core.bin import (
    Bin, ValueBin, RangeBin, WildcardBin, AutoBin,
    IgnoreBin, IllegalBin, IllegalBinHitError
)


class TestValueBin:
    """Test ValueBin functionality."""

    def test_exact_match(self):
        """Test that ValueBin matches exact values."""
        bin = ValueBin("test_bin", 42)
        assert bin.match(42) is True
        assert bin.match(43) is False
        assert bin.match(0) is False

    def test_hit_count(self):
        """Test hit count tracking."""
        bin = ValueBin("test_bin", 100)
        assert bin.get_hit_count() == 0

        bin.increment_hit()
        assert bin.get_hit_count() == 1

        bin.increment_hit()
        bin.increment_hit()
        assert bin.get_hit_count() == 3

    def test_string_value(self):
        """Test ValueBin with string values."""
        bin = ValueBin("str_bin", "hello")
        assert bin.match("hello") is True
        assert bin.match("world") is False

    def test_repr(self):
        """Test string representation."""
        bin = ValueBin("test", 42)
        assert "ValueBin" in repr(bin)
        assert "test" in repr(bin)
        assert "42" in repr(bin)


class TestRangeBin:
    """Test RangeBin functionality."""

    def test_range_match(self):
        """Test that RangeBin matches values within range."""
        bin = RangeBin("range_bin", 10, 20)
        assert bin.match(10) is True  # Lower bound
        assert bin.match(15) is True  # Middle
        assert bin.match(20) is True  # Upper bound
        assert bin.match(9) is False
        assert bin.match(21) is False

    def test_negative_range(self):
        """Test RangeBin with negative values."""
        bin = RangeBin("neg_bin", -10, 10)
        assert bin.match(-10) is True
        assert bin.match(0) is True
        assert bin.match(10) is True
        assert bin.match(-11) is False
        assert bin.match(11) is False

    def test_single_value_range(self):
        """Test RangeBin with same low and high values."""
        bin = RangeBin("single", 5, 5)
        assert bin.match(5) is True
        assert bin.match(4) is False
        assert bin.match(6) is False

    def test_invalid_range_raises_error(self):
        """Test that invalid range raises ValueError."""
        with pytest.raises(ValueError, match="Invalid range"):
            RangeBin("invalid", 20, 10)  # low > high

    def test_hit_count(self):
        """Test hit count tracking."""
        bin = RangeBin("range", 0, 100)
        bin.increment_hit()
        bin.increment_hit()
        assert bin.get_hit_count() == 2


class TestWildcardBin:
    """Test WildcardBin functionality."""

    def test_hex_wildcard_match(self):
        """Test hex wildcard matching."""
        bin = WildcardBin("wild", "8???", is_hex=True)
        assert bin.match(0x8000) is True
        assert bin.match(0x8FFF) is True
        assert bin.match(0x7000) is False
        assert bin.match(0x9000) is False

    def test_hex_pattern_mixed(self):
        """Test hex pattern with mixed digits and wildcards."""
        bin = WildcardBin("mixed", "A?B?", is_hex=True)
        assert bin.match(0xA0B0) is True
        assert bin.match(0xAFBF) is True
        assert bin.match(0xB0B0) is False

    def test_generic_wildcard(self):
        """Test generic wildcard matching (non-hex)."""
        bin = WildcardBin("generic", "test???", is_hex=False)
        assert bin.match("test123") is True
        assert bin.match("testABC") is True
        assert bin.match("fail123") is False

    def test_int_to_hex_conversion(self):
        """Test that int values are converted to hex strings."""
        bin = WildcardBin("hex_bin", "FF??", is_hex=True)
        assert bin.match(0xFF00) is True
        assert bin.match(0xFFFF) is True


class TestAutoBin:
    """Test AutoBin functionality."""

    def test_bin_bounds_calculation(self):
        """Test that bin bounds are calculated correctly."""
        bin = AutoBin("auto_0", 0, 10)  # First bin in 10-bin set
        bin._initialize_range(100)  # Range 0-100

        # After initialization, bin should have bounds
        assert bin._bin_low is not None
        assert bin._bin_high is not None

    def test_match_after_initialization(self):
        """Test matching after range initialization."""
        bin = AutoBin("auto_0", 0, 10)
        bin._initialize_range(100)

        # First sample should match first bin
        assert bin.match(5) is True

    def test_different_bins(self):
        """Test that different bins have different ranges."""
        bin0 = AutoBin("bin_0", 0, 4)
        bin1 = AutoBin("bin_1", 1, 4)
        bin2 = AutoBin("bin_2", 2, 4)
        bin3 = AutoBin("bin_3", 3, 4)

        # Initialize with range 0-100
        for bin in [bin0, bin1, bin2, bin3]:
            bin._initialize_range(100)

        # Test values match appropriate bins
        value = 25
        matches = [bin.match(value) for bin in [bin0, bin1, bin2, bin3]]
        # Exactly one bin should match
        assert sum(matches) == 1

    def test_repr_initialized(self):
        """Test string representation when initialized."""
        bin = AutoBin("auto", 0, 10)
        bin._initialize_range(100)
        repr_str = repr(bin)
        assert "AutoBin" in repr_str
        assert "range=" in repr_str


class TestIgnoreBin:
    """Test IgnoreBin functionality."""

    def test_ignore_match(self):
        """Test that IgnoreBin matches specific values."""
        bin = IgnoreBin("ignore", 0)
        assert bin.match(0) is True
        assert bin.match(1) is False

    def test_increment_does_nothing(self):
        """Test that increment_hit does nothing for ignore bins."""
        bin = IgnoreBin("ignore", 100)
        bin.increment_hit()
        bin.increment_hit()
        assert bin.get_hit_count() == 0  # Hit count stays 0

    def test_multiple_ignore_values(self):
        """Test multiple ignore bins."""
        ignore_0 = IgnoreBin("ignore_0", 0)
        ignore_255 = IgnoreBin("ignore_255", 255)

        assert ignore_0.match(0) is True
        assert ignore_0.match(255) is False
        assert ignore_255.match(255) is True
        assert ignore_255.match(0) is False


class TestIllegalBin:
    """Test IllegalBin functionality."""

    def test_illegal_match(self):
        """Test that IllegalBin matches specific values."""
        bin = IllegalBin("illegal", 512)
        assert bin.match(512) is True
        assert bin.match(511) is False

    def test_increment_raises_error(self):
        """Test that increment_hit raises IllegalBinHitError."""
        bin = IllegalBin("illegal", 255)

        with pytest.raises(IllegalBinHitError, match="Illegal bin"):
            bin.increment_hit()

    def test_error_message(self):
        """Test that error message contains useful information."""
        bin = IllegalBin("bad_value", 999)

        with pytest.raises(IllegalBinHitError) as exc_info:
            bin.increment_hit()

        assert "bad_value" in str(exc_info.value)
        assert "999" in str(exc_info.value)


class TestCoveragePercentage:
    """Test coverage percentage calculation."""

    def test_coverage_calculation(self):
        """Test coverage percentage calculation."""
        bin = ValueBin("test", 42)

        # 0 hits out of 10 samples = 0%
        assert bin.get_coverage_percentage(10) == 0.0

        # 5 hits out of 10 samples = 50%
        for _ in range(5):
            bin.increment_hit()
        assert bin.get_coverage_percentage(10) == 50.0

        # 10 hits out of 10 samples = 100%
        for _ in range(5):
            bin.increment_hit()
        assert bin.get_coverage_percentage(10) == 100.0

    def test_zero_samples(self):
        """Test coverage percentage with zero samples."""
        bin = ValueBin("test", 42)
        assert bin.get_coverage_percentage(0) == 0.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
