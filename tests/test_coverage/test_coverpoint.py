"""
Unit tests for CoverPoint system

Tests CoverPoint functionality including bin management,
sampling, coverage calculation, and ignore/illegal bins.
"""

import pytest
from sv_randomizer.coverage.core.coverpoint import CoverPoint, BinType
from sv_randomizer.coverage.core.bin import IllegalBinHitError


class TestCoverPointInit:
    """Test CoverPoint initialization."""

    def test_basic_init(self):
        """Test basic CoverPoint initialization."""
        cp = CoverPoint("test_cp", "addr")
        assert cp.name == "test_cp"
        assert cp._sample_expr == "addr"
        assert cp.is_enabled() is True

    def test_init_with_bins(self):
        """Test initialization with bins."""
        bins = {
            "values": [1, 2, 3],
            "ranges": [[10, 20], [30, 40]]
        }
        cp = CoverPoint("test_cp", "value", bins=bins)
        assert len(cp._bins) == 3 + 2  # 3 values + 2 ranges

    def test_init_with_weight(self):
        """Test initialization with weight."""
        cp = CoverPoint("weighted_cp", "value", weight=2.0)
        assert cp._weight == 2.0

    def test_init_with_comment(self):
        """Test initialization with comment."""
        cp = CoverPoint("commented_cp", "value", comment="Test coverpoint")
        assert cp._comment == "Test coverpoint"


class TestBinInitialization:
    """Test bin initialization from bin definition dictionary."""

    def test_value_bins(self):
        """Test value bins initialization."""
        bins = {"values": [10, 20, 30]}
        cp = CoverPoint("value_cp", "value", bins=bins)

        assert "value_0" in cp._bins
        assert "value_1" in cp._bins
        assert "value_2" in cp._bins

    def test_range_bins(self):
        """Test range bins initialization."""
        bins = {"ranges": [[0, 10], [20, 30]]}
        cp = CoverPoint("range_cp", "value", bins=bins)

        assert "range_0" in cp._bins
        assert "range_1" in cp._bins

    def test_wildcard_bins(self):
        """Test wildcard bins initialization."""
        bins = {"wildcards": ["8???", "F???"]}
        cp = CoverPoint("wild_cp", "value", bins=bins)

        assert "wildcard_0" in cp._bins
        assert "wildcard_1" in cp._bins

    def test_auto_bins(self):
        """Test auto bins initialization."""
        bins = {"auto": 16}
        cp = CoverPoint("auto_cp", "value", bins=bins)

        assert len(cp._bins) == 16
        assert "auto_0" in cp._bins
        assert "auto_15" in cp._bins

    def test_ignore_bins(self):
        """Test ignore bins initialization."""
        bins = {"ignore": [0, 255]}
        cp = CoverPoint("ignore_cp", "value", bins=bins)

        assert len(cp._ignore_bins) == 2

    def test_illegal_bins(self):
        """Test illegal bins initialization."""
        bins = {"illegal": [512]}
        cp = CoverPoint("illegal_cp", "value", bins=bins)

        assert len(cp._illegal_bins) == 1
        assert cp._illegal_bins[0].value == 512


class TestSampling:
    """Test CoverPoint sampling functionality."""

    def test_sample_string_expr(self):
        """Test sampling with string expression."""
        bins = {"values": [10, 20, 30]}
        cp = CoverPoint("test_cp", "value", bins=bins)

        # Sample with value
        cp.sample(value=10)
        assert cp._bins["value_0"].get_hit_count() == 1

        # Sample with different value
        cp.sample(value=20)
        assert cp._bins["value_1"].get_hit_count() == 1

    def test_sample_callable_expr(self):
        """Test sampling with callable expression."""
        bins = {"values": [1, 2, 3]}
        cp = CoverPoint("call_cp", lambda kwargs: kwargs.get("x") * 10, bins=bins)

        # Callable should multiply x by 10
        cp.sample(x=1)  # 1 * 10 = 10 (not in bins)
        cp.sample(x=2)  # 2 * 10 = 20 (not in bins)

        # Add matching bins
        bins2 = {"values": [10, 20]}
        cp2 = CoverPoint("call_cp2", lambda kwargs: kwargs.get("y", 0), bins=bins2)
        cp2.sample(y=10)
        assert cp2._bins["value_0"].get_hit_count() == 1

    def test_sample_ignores_none(self):
        """Test that None values are ignored."""
        cp = CoverPoint("test_cp", "missing_value", bins={"values": [1, 2, 3]})
        cp.sample(other_value=100)  # missing_value not in kwargs

        # No bins should be hit
        for bin in cp._bins.values():
            assert bin.get_hit_count() == 0

    def test_sample_hit_count_increments(self):
        """Test that hit count increments correctly."""
        bins = {"values": [42]}
        cp = CoverPoint("hit_cp", "value", bins=bins)

        # Multiple samples of same value
        cp.sample(value=42)
        cp.sample(value=42)
        cp.sample(value=42)

        assert cp._bins["value_0"].get_hit_count() == 3
        assert cp._sample_count == 3


class TestIgnoreBins:
    """Test ignore bin functionality."""

    def test_ignore_bin_skips_sampling(self):
        """Test that ignore bins skip sampling."""
        bins = {
            "values": [10, 20, 30],
            "ignore": [20]
        }
        cp = CoverPoint("ignore_cp", "value", bins=bins)

        # Sample ignored value
        cp.sample(value=20)

        # Sample count should not increment
        assert cp._sample_count == 0

        # Sample normal value
        cp.sample(value=10)
        assert cp._sample_count == 1

    def test_multiple_ignore_bins(self):
        """Test multiple ignore bins."""
        bins = {
            "values": [10, 20, 30, 40],
            "ignore": [10, 30]
        }
        cp = CoverPoint("multi_ignore_cp", "value", bins=bins)

        cp.sample(value=10)  # Ignored
        cp.sample(value=20)  # Counted
        cp.sample(value=30)  # Ignored
        cp.sample(value=40)  # Counted

        assert cp._sample_count == 2


class TestIllegalBins:
    """Test illegal bin functionality."""

    def test_illegal_bin_raises_error(self):
        """Test that illegal bin raises error."""
        bins = {
            "values": [10, 20, 30],
            "illegal": [999]
        }
        cp = CoverPoint("illegal_cp", "value", bins=bins)

        with pytest.raises(IllegalBinHitError, match="Value 999 hit illegal bin"):
            cp.sample(value=999)

    def test_illegal_bin_before_normal_bins(self):
        """Test that illegal bins are checked before normal bins."""
        bins = {
            "values": [100],
            "illegal": [100]  # Same value as normal bin
        }
        cp = CoverPoint("conflict_cp", "value", bins=bins)

        # Illegal should take precedence
        with pytest.raises(IllegalBinHitError):
            cp.sample(value=100)


class TestCoverageCalculation:
    """Test coverage calculation."""

    def test_basic_coverage(self):
        """Test basic coverage percentage calculation."""
        bins = {"values": [1, 2, 3, 4]}
        cp = CoverPoint("cov_cp", "value", bins=bins)

        # No samples = 0% coverage
        assert cp.get_coverage() == 0.0

        # Sample 2 out of 4 bins
        cp.sample(value=1)
        cp.sample(value=3)
        assert cp.get_coverage() == 50.0

        # Sample all bins
        cp.sample(value=2)
        cp.sample(value=4)
        assert cp.get_coverage() == 100.0

    def test_range_coverage(self):
        """Test coverage with range bins."""
        bins = {"ranges": [[0, 10], [20, 30]]}
        cp = CoverPoint("range_cov_cp", "value", bins=bins)

        # Sample each range once
        cp.sample(value=5)
        cp.sample(value=25)
        assert cp.get_coverage() == 100.0

    def test_empty_coverpoint_coverage(self):
        """Test that empty coverpoint has 100% coverage."""
        cp = CoverPoint("empty_cp", "value", bins=None)
        assert cp.get_coverage() == 100.0

    def test_weighted_coverage(self):
        """Test weighted coverage calculation."""
        bins = {"values": [1, 2, 3]}
        cp = CoverPoint("weighted_cp", "value", bins=bins, weight=2.0)

        cp.sample(value=1)
        cp.sample(value=2)

        # Normal coverage: 2/3 = 66.67%
        # Weighted coverage: 66.67% * 2.0 = 133.33%
        assert cp.get_weighted_coverage() == pytest.approx(133.33, rel=0.01)

    def test_bin_counts(self):
        """Test get_bin_counts method."""
        bins = {"values": [1, 2, 3, 4, 5]}
        cp = CoverPoint("count_cp", "value", bins=bins)

        total, covered = cp.get_bin_counts()
        assert total == 5
        assert covered == 0

        cp.sample(value=1)
        cp.sample(value=3)
        cp.sample(value=5)

        total, covered = cp.get_bin_counts()
        assert total == 5
        assert covered == 3


class TestCoverpointDetails:
    """Test coverpoint coverage details."""

    def test_get_coverage_details(self):
        """Test get_coverage_details method."""
        bins = {"values": [1, 2, 3]}
        cp = CoverPoint("detail_cp", "value", bins=bins, weight=1.5)

        cp.sample(value=1)
        cp.sample(value=2)

        details = cp.get_coverage_details()

        assert details['name'] == "detail_cp"
        assert details['coverage'] == pytest.approx(66.67, rel=0.01)
        assert details['weighted_coverage'] == pytest.approx(100.0, rel=0.01)
        assert details['weight'] == 1.5
        assert details['sample_count'] == 2
        assert details['total_bins'] == 3
        assert details['covered_bins'] == 2
        assert 'bins' in details


class TestEnableDisable:
    """Test enable/disable functionality."""

    def test_default_enabled(self):
        """Test that coverpoint is enabled by default."""
        cp = CoverPoint("test_cp", "value")
        assert cp.is_enabled() is True

    def test_disable_sampling(self):
        """Test disabling sampling."""
        bins = {"values": [1, 2, 3]}
        cp = CoverPoint("test_cp", "value", bins=bins)

        cp.disable()
        assert cp.is_enabled() is False

        # Sample should not increment
        cp.sample(value=1)
        assert cp._sample_count == 0

    def test_enable_sampling(self):
        """Test re-enabling sampling."""
        bins = {"values": [1, 2, 3]}
        cp = CoverPoint("test_cp", "value", bins=bins)

        cp.disable()
        cp.enable()

        assert cp.is_enabled() is True

        # Sample should work now
        cp.sample(value=1)
        assert cp._sample_count == 1


class TestParentAndDatabase:
    """Test parent and database integration."""

    def test_set_parent(self):
        """Test setting parent covergroup."""
        cp = CoverPoint("test_cp", "value")
        mock_parent = type('MockParent', (), {'name': 'parent_cg'})()

        cp._set_parent(mock_parent)
        assert cp._parent == mock_parent

    def test_set_database(self):
        """Test setting database."""
        cp = CoverPoint("test_cp", "value")
        mock_db = type('MockDB', (), {'record_sample': lambda *args: None})()

        cp.set_database(mock_db)
        assert cp._database == mock_db


class TestStringRepresentation:
    """Test string representation."""

    def test_repr(self):
        """Test __repr__ method."""
        bins = {"values": [1, 2, 3]}
        cp = CoverPoint("test_cp", "value", bins=bins)

        repr_str = repr(cp)
        assert "CoverPoint" in repr_str
        assert "test_cp" in repr_str
        assert "bins=3" in repr_str


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
