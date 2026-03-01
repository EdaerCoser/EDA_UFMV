"""
Unit tests for CoverGroup system

Tests CoverGroup functionality including coverpoint management,
sampling coordination, coverage calculation, and callbacks.
"""

import pytest
from coverage.core.covergroup import CoverGroup
from coverage.core.coverpoint import CoverPoint


class TestCoverGroupInit:
    """Test CoverGroup initialization."""

    def test_basic_init(self):
        """Test basic CoverGroup initialization."""
        cg = CoverGroup("test_cg")
        assert cg.name == "test_cg"
        assert cg._sampling_enabled is True
        assert cg._instance_count == 0

    def test_init_with_sample_event(self):
        """Test initialization with sample event."""
        event_func = lambda: {"value": 42}
        cg = CoverGroup("event_cg", sample_event=event_func)
        assert cg._sample_event == event_func

    def test_init_auto_sample_disabled(self):
        """Test initialization with auto_sample disabled."""
        cg = CoverGroup("manual_cg", auto_sample=False)
        assert cg._auto_sample is False


class TestCoverpointManagement:
    """Test coverpoint management."""

    def test_add_coverpoint(self):
        """Test adding a coverpoint."""
        cg = CoverGroup("test_cg")
        cp = CoverPoint("test_cp", "value", bins={"values": [1, 2, 3]})

        cg.add_coverpoint(cp)

        assert "test_cp" in cg._coverpoints
        assert cg._coverpoints["test_cp"] == cp

    def test_add_multiple_coverpoints(self):
        """Test adding multiple coverpoints."""
        cg = CoverGroup("multi_cg")

        cp1 = CoverPoint("cp1", "value1", bins={"values": [1, 2]})
        cp2 = CoverPoint("cp2", "value2", bins={"values": [3, 4]})
        cp3 = CoverPoint("cp3", "value3", bins={"values": [5, 6]})

        cg.add_coverpoint(cp1)
        cg.add_coverpoint(cp2)
        cg.add_coverpoint(cp3)

        assert len(cg._coverpoints) == 3

    def test_parent_set_on_add(self):
        """Test that parent is set when adding coverpoint."""
        cg = CoverGroup("parent_cg")
        cp = CoverPoint("child_cp", "value", bins={"values": [1, 2]})

        cg.add_coverpoint(cp)

        assert cp._parent == cg

    def test_get_coverpoint(self):
        """Test getting a coverpoint by name."""
        cg = CoverGroup("test_cg")
        cp = CoverPoint("test_cp", "value", bins={"values": [1, 2]})

        cg.add_coverpoint(cp)

        retrieved = cg.get_coverpoint("test_cp")
        assert retrieved == cp

    def test_get_nonexistent_coverpoint(self):
        """Test getting non-existent coverpoint returns None."""
        cg = CoverGroup("test_cg")
        assert cg.get_coverpoint("nonexistent") is None

    def test_list_coverpoints(self):
        """Test listing coverpoint names."""
        cg = CoverGroup("list_cg")

        cg.add_coverpoint(CoverPoint("cp1", "v1", bins={"values": [1]}))
        cg.add_coverpoint(CoverPoint("cp2", "v2", bins={"values": [2]}))

        names = cg.list_coverpoints()
        assert set(names) == {"cp1", "cp2"}


class TestSampling:
    """Test sampling functionality."""

    def test_sample_propagates_to_coverpoints(self):
        """Test that sampling propagates to all coverpoints."""
        cg = CoverGroup("sample_cg")

        cp1 = CoverPoint("cp1", "val1", bins={"values": [1, 2]})
        cp2 = CoverPoint("cp2", "val2", bins={"values": [3, 4]})

        cg.add_coverpoint(cp1)
        cg.add_coverpoint(cp2)

        cg.sample(val1=1, val2=3)

        assert cp1._sample_count == 1
        assert cp2._sample_count == 1

    def test_sample_increments_instance_count(self):
        """Test that sampling increments instance count."""
        cg = CoverGroup("count_cg")
        cp = CoverPoint("cp", "val", bins={"values": [1]})

        cg.add_coverpoint(cp)

        assert cg._instance_count == 0

        cg.sample(val=1)
        assert cg._instance_count == 1

        cg.sample(val=1)
        assert cg._instance_count == 2

    def test_sample_with_disabled_coverpoint(self):
        """Test sampling with disabled coverpoint."""
        cg = CoverGroup("disabled_cg")

        cp1 = CoverPoint("cp1", "val1", bins={"values": [1]})
        cp2 = CoverPoint("cp2", "val2", bins={"values": [2]})

        cg.add_coverpoint(cp1)
        cg.add_coverpoint(cp2)

        cp2.disable()

        cg.sample(val1=1, val2=2)

        assert cp1._sample_count == 1
        assert cp2._sample_count == 0  # Disabled, not sampled

    def test_sample_when_disabled(self):
        """Test that sampling when disabled does nothing."""
        cg = CoverGroup("disabled_cg")
        cp = CoverPoint("cp", "val", bins={"values": [1]})

        cg.add_coverpoint(cp)
        cg.disable_sampling()

        cg.sample(val=1)

        assert cp._sample_count == 0
        assert cg._instance_count == 0

    def test_sample_with_event_function(self):
        """Test sampling with sample event function."""
        event_values = {"value": 42}
        cg = CoverGroup("event_cg", sample_event=lambda: event_values)

        cp = CoverPoint("cp", "value", bins={"values": [42]})

        cg.add_coverpoint(cp)

        cg.sample()  # No kwargs needed, event provides values

        assert cp._sample_count == 1


class TestCoverageCalculation:
    """Test coverage calculation."""

    def test_empty_covergroup_coverage(self):
        """Test that empty covergroup has 100% coverage."""
        cg = CoverGroup("empty_cg")
        assert cg.get_coverage() == 100.0

    def test_single_coverpoint_coverage(self):
        """Test coverage with single coverpoint."""
        cg = CoverGroup("single_cg")

        cp = CoverPoint("cp", "val", bins={"values": [1, 2, 3, 4]})
        cg.add_coverpoint(cp)

        # No samples = 0%
        assert cg.get_coverage() == 0.0

        # Sample 2 out of 4 bins
        cg.sample(val=1)
        cg.sample(val=3)

        assert cg.get_coverage() == 50.0

    def test_multiple_coverpoint_coverage(self):
        """Test coverage with multiple coverpoints."""
        cg = CoverGroup("multi_cg")

        cp1 = CoverPoint("cp1", "val1", bins={"values": [1, 2]})
        cp2 = CoverPoint("cp2", "val2", bins={"values": [3, 4, 5]})

        cg.add_coverpoint(cp1)
        cg.add_coverpoint(cp2)

        # Sample all bins in cp1, none in cp2
        cg.sample(val1=1, val2=3)
        cg.sample(val1=2)

        # cp1: 2/2 = 100%, cp2: 1/3 = 33.3%
        # Total: (2 + 1) / (2 + 3) = 3/5 = 60%
        assert cg.get_coverage() == pytest.approx(60.0, rel=0.1)

    def test_full_coverage(self):
        """Test 100% coverage."""
        cg = CoverGroup("full_cg")

        cp1 = CoverPoint("cp1", "val1", bins={"values": [1, 2]})
        cp2 = CoverPoint("cp2", "val2", bins={"values": [3, 4]})

        cg.add_coverpoint(cp1)
        cg.add_coverpoint(cp2)

        # Sample all bins
        cg.sample(val1=1, val2=3)
        cg.sample(val1=2, val2=4)

        assert cg.get_coverage() == 100.0


class TestCoverageDetails:
    """Test coverage details reporting."""

    def test_get_coverage_details(self):
        """Test get_coverage_details method."""
        cg = CoverGroup("detail_cg")

        cp1 = CoverPoint("cp1", "val1", bins={"values": [1, 2]})
        cp2 = CoverPoint("cp2", "val2", bins={"values": [3, 4]})

        cg.add_coverpoint(cp1)
        cg.add_coverpoint(cp2)

        cg.sample(val1=1)

        details = cg.get_coverage_details()

        assert details['name'] == "detail_cg"
        assert details['coverage'] == pytest.approx(25.0, rel=0.1)  # 1/4 bins
        assert details['sample_count'] == 1
        assert 'coverpoints' in details
        assert 'cp1' in details['coverpoints']
        assert 'cp2' in details['coverpoints']


class TestCallbacks:
    """Test callback functionality."""

    def test_pre_sample_callback(self):
        """Test pre-sample callback."""
        cg = CoverGroup("callback_cg")

        callback_called = []

        def pre_callback(covergroup, kwargs):
            callback_called.append("pre")
            callback_called.append(kwargs)

        cg.register_pre_sample(pre_callback)

        cp = CoverPoint("cp", "val", bins={"values": [1]})
        cg.add_coverpoint(cp)

        cg.sample(val=1)

        assert "pre" in callback_called
        assert {"val": 1} in callback_called

    def test_post_sample_callback(self):
        """Test post-sample callback."""
        cg = CoverGroup("callback_cg")

        callback_called = []

        def post_callback(covergroup, kwargs):
            callback_called.append("post")

        cg.register_post_sample(post_callback)

        cp = CoverPoint("cp", "val", bins={"values": [1]})
        cg.add_coverpoint(cp)

        cg.sample(val=1)

        assert "post" in callback_called

    def test_callback_order(self):
        """Test that callbacks are called in correct order."""
        cg = CoverGroup("order_cg")

        order = []

        def pre_callback(cg, kwargs):
            order.append("pre")

        def post_callback(cg, kwargs):
            order.append("post")

        cg.register_pre_sample(pre_callback)
        cg.register_post_sample(post_callback)

        cp = CoverPoint("cp", "val", bins={"values": [1]})
        cg.add_coverpoint(cp)

        cg.sample(val=1)

        assert order == ["pre", "post"]


class TestDatabaseIntegration:
    """Test database integration."""

    def test_set_database_propagates(self):
        """Test that set_database propagates to coverpoints."""
        cg = CoverGroup("db_cg")

        mock_db = type('MockDB', (), {
            'record_sample': lambda *args: None
        })()

        cp = CoverPoint("cp", "val", bins={"values": [1]})
        cg.add_coverpoint(cp)

        cg.set_database(mock_db)

        assert cp._database == mock_db


class TestEnableDisable:
    """Test enable/disable functionality."""

    def test_default_enabled(self):
        """Test that sampling is enabled by default."""
        cg = CoverGroup("test_cg")
        assert cg.is_sampling_enabled() is True

    def test_disable_sampling(self):
        """Test disabling sampling."""
        cg = CoverGroup("test_cg")
        cg.disable_sampling()

        assert cg.is_sampling_enabled() is False

    def test_enable_after_disable(self):
        """Test re-enabling sampling."""
        cg = CoverGroup("test_cg")
        cg.disable_sampling()
        cg.enable_sampling()

        assert cg.is_sampling_enabled() is True


class TestContextManager:
    """Test context manager functionality."""

    def test_context_manager(self):
        """Test using covergroup as context manager."""
        mock_db = type('MockDB', (), {
            'save': lambda self: None
        })()

        cg = CoverGroup("context_cg")
        cg.set_database(mock_db)

        with cg:
            # Inside context
            assert cg is not None

        # Database save should be called on exit
        # (we can't verify the call, but no exception should be raised)


class TestStringRepresentation:
    """Test string representation."""

    def test_repr(self):
        """Test __repr__ method."""
        cg = CoverGroup("test_cg")

        cp1 = CoverPoint("cp1", "val1", bins={"values": [1]})
        cg.add_coverpoint(cp1)

        repr_str = repr(cg)
        assert "CoverGroup" in repr_str
        assert "test_cg" in repr_str
        assert "coverpoints=1" in repr_str


class TestCrossCoverage:
    """Test cross coverage placeholders."""

    def test_add_cross(self):
        """Test adding cross coverage."""
        cg = CoverGroup("cross_cg")

        mock_cross = type('MockCross', (), {
            'name': 'test_cross',
            '_set_parent': lambda self, parent: None,
            'is_enabled': lambda self: True,
            'sample': lambda **kwargs: None,
            'get_bin_counts': lambda self: (0, 0)
        })()

        cg.add_cross(mock_cross)

        assert "test_cross" in cg._crosses


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
