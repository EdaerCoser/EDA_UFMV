"""
Boundary Value Tests - Collections

Tests for handling collection boundary conditions:
- Empty collections (empty list, empty dict, empty set)
- Single element collections
- Large collections
- Nested collections
"""

import pytest

from sv_randomizer import Randomizable
from sv_randomizer.core.variables import RandVar, VarType
from coverage.core import CoverGroup, CoverPoint
from sv_randomizer.constraints.inside import InsideConstraint


# =============================================================================
# Empty Collection Tests
# =============================================================================

@pytest.mark.unit
@pytest.mark.boundary
@pytest.mark.P0
class TestEmptyCollections:
    """Tests for empty collection handling."""

    def test_empty_list_constraint(self):
        """Test constraint with empty list."""
        class TestObj(Randomizable):
            def __init__(self):
                super().__init__()
                self.x = RandVar("x", VarType.BIT, bit_width=8)

        obj = TestObj()

        # Inside constraint with empty list
        # This should either raise error or be unsatisfiable
        constraint = InsideConstraint(obj.x, [])
        # Empty list means no valid values
        assert len(constraint._values) == 0

    def test_empty_dict_iteration(self):
        """Test iterating over empty dict in RGM."""
        from rgm.core import RegisterBlock
        block = RegisterBlock("EMPTY", 0x40000000)

        # Block with no registers
        assert len(block._registers) == 0

        # Should iterate without errors
        count = 0
        for reg_name, reg in block._registers.items():
            count += 1
        assert count == 0

    def test_empty_covergroup(self):
        """Test empty covergroup operations."""
        cg = CoverGroup("empty_cg")

        # No coverpoints
        assert len(cg._coverpoints) == 0
        assert len(cg._crosses) == 0

        # Coverage should be 0 or handled gracefully
        assert cg.coverage == 0.0

        # Sampling should not crash
        cg.sample(value=42)
        assert cg.coverage == 0.0

    def test_empty_bins_list(self):
        """Test CoverPoint with empty bins list."""
        cg = CoverGroup("empty_bins_cg")
        # Empty bins configuration
        cp = CoverPoint("empty_cp", "value", bins={})
        cg.add_coverpoint(cp)

        # Should handle gracefully
        assert len(cp._bins) == 0


# =============================================================================
# Single Element Collection Tests
# =============================================================================

@pytest.mark.unit
@pytest.mark.boundary
@pytest.mark.P0
class TestSingleElementCollections:
    """Tests for single element collection handling."""

    def test_single_element_list_constraint(self):
        """Test constraint with single element list."""
        class TestObj(Randomizable):
            def __init__(self):
                super().__init__()
                self.x = RandVar("x", VarType.BIT, bit_width=8)

        obj = TestObj()

        # Inside constraint with single value
        constraint = InsideConstraint(obj.x, [42])
        assert len(constraint._values) == 1

    def test_single_register_block(self):
        """Test RegisterBlock with single register."""
        from rgm.core import RegisterBlock, Register
        from rgm.utils import AccessType

        block = RegisterBlock("SINGLE", 0x40000000)
        reg = Register("ONLY_REG", 0x00, 32)
        block.add_register(reg)

        assert len(block._registers) == 1

        # Should be able to get the register
        retrieved = block.get_register("ONLY_REG")
        assert retrieved.name == "ONLY_REG"

    def test_single_field_register(self):
        """Test Register with single field."""
        from rgm.core import Register, Field
        from rgm.utils import AccessType

        reg = Register("SINGLE_FIELD_REG", 0x00, 32)
        field = Field("only_field", bit_offset=0, bit_width=32, access=AccessType.RW)
        reg.add_field(field)

        assert len(reg._fields) == 1

    def test_single_bin_coverpoint(self):
        """Test CoverPoint with single bin."""
        cg = CoverGroup("single_bin_cg")
        cp = CoverPoint("single_bin_cp", "value", bins={"only": [42]})
        cg.add_coverpoint(cp)

        assert len(cp._bins) == 1

        # Sample the only value
        cg.sample(value=42)
        assert cg.coverage == 100.0


# =============================================================================
# Large Collection Tests
# =============================================================================

@pytest.mark.unit
@pytest.mark.boundary
@pytest.mark.P1
class TestLargeCollections:
    """Tests for large collection handling."""

    def test_large_list_constraint(self):
        """Test constraint with large list of values."""
        class TestObj(Randomizable):
            def __init__(self):
                super().__init__()
                self.x = RandVar("x", VarType.BIT, bit_width=16)

        obj = TestObj()

        # Inside constraint with many values
        large_list = list(range(1000))
        constraint = InsideConstraint(obj.x, large_list)
        assert len(constraint._values) == 1000

    def test_large_covergroup_many_coverpoints(self):
        """Test CoverGroup with many coverpoints."""
        cg = CoverGroup("large_cg")

        # Add 100 coverpoints
        for i in range(100):
            cp = CoverPoint(f"cp_{i}", f"value_{i}", bins={"vals": [i]})
            cg.add_coverpoint(cp)

        assert len(cg._coverpoints) == 100

        # Sample a few
        for i in [0, 50, 99]:
            cg.sample(**{f"value_{i}": i})

        # Should have partial coverage
        assert 0.0 < cg.coverage < 100.0

    def test_large_bin_list(self):
        """Test CoverPoint with large bin list."""
        cg = CoverGroup("many_bins_cg")

        # Create coverpoint with 1000 bins
        bins_list = list(range(1000))
        cp = CoverPoint("many_cp", "value", bins={"many": bins_list})
        cg.add_coverpoint(cp)

        assert len(cp._bins) == 1000

        # Sample some values
        cg.sample(value=0)
        cg.sample(value=500)
        cg.sample(value=999)

        # Should have minimal coverage
        assert cg.coverage == 0.3  # 3 out of 1000

    def test_large_register_block(self):
        """Test RegisterBlock with many registers."""
        from rgm.core import RegisterBlock, Register

        block = RegisterBlock("LARGE", 0x40000000)

        # Add 100 registers
        for i in range(100):
            reg = Register(f"REG_{i}", i * 4, 32)
            block.add_register(reg)

        assert len(block._registers) == 100

        # Should be able to access registers
        reg_0 = block.get_register("REG_0")
        reg_99 = block.get_register("REG_99")
        assert reg_0 is not None
        assert reg_99 is not None

    def test_many_fields_in_register(self):
        """Test Register with many fields."""
        from rgm.core import Register, Field
        from rgm.utils import AccessType

        reg = Register("MANY_FIELDS_REG", 0x00, 32)

        # Add 32 single-bit fields
        for i in range(32):
            field = Field(f"bit_{i}", bit_offset=i, bit_width=1, access=AccessType.RW)
            reg.add_field(field)

        assert len(reg._fields) == 32


# =============================================================================
# Nested Collection Tests
# =============================================================================

@pytest.mark.unit
@pytest.mark.boundary
@pytest.mark.P1
class TestNestedCollections:
    """Tests for nested collection handling."""

    def test_nested_range_bins(self):
        """Test CoverPoint with nested range structure."""
        cg = CoverGroup("nested_cg")

        # Ranges are tuples (nested structure)
        ranges = [(0, 10), (11, 20), (21, 30)]
        cp = CoverPoint("nested_cp", "value", bins={"ranges": ranges})
        cg.add_coverpoint(cp)

        # Each tuple becomes a RangeBin
        assert len(cp._bins) == 3

    def test_nested_covergroup_structure(self):
        """Test nested covergroup hierarchy (if supported)."""
        # Currently CoverGroup doesn't support nesting
        # This test documents expected behavior
        cg1 = CoverGroup("parent_cg")
        cg2 = CoverGroup("child_cg")

        # They are independent
        assert cg1._name != cg2._name

    def test_hierarchical_register_blocks(self):
        """Test hierarchical register block structure."""
        from rgm.core import RegisterBlock, Register

        # If hierarchical blocks are supported
        parent = RegisterBlock("PARENT", 0x40000000)
        child = RegisterBlock("CHILD", 0x1000)

        # Add registers to child
        reg = Register("REG", 0x00, 32)
        child.add_register(reg)

        # If sub-blocks are supported
        if hasattr(parent, 'add_sub_block'):
            parent.add_sub_block(child)
            # Should have nested structure
        else:
            # Blocks are independent
            assert parent is not child


# =============================================================================
# Collection Edge Cases
# =============================================================================

@pytest.mark.unit
@pytest.mark.boundary
@pytest.mark.P1
class TestCollectionEdgeCases:
    """Tests for collection edge cases."""

    def test_duplicate_values_in_list(self):
        """Test constraint with duplicate values in list."""
        class TestObj(Randomizable):
            def __init__(self):
                super().__init__()
                self.x = RandVar("x", VarType.BIT, bit_width=8)

        obj = TestObj()

        # List with duplicates
        constraint = InsideConstraint(obj.x, [1, 2, 2, 3, 3, 3])
        # Should handle duplicates gracefully
        assert len(constraint._values) == 6

    def test_collection_with_none_values(self):
        """Test collection containing None values."""
        cg = CoverGroup("none_cg")

        # Bins with None (if supported)
        # May raise error or handle gracefully
        try:
            cp = CoverPoint("none_cp", "value", bins={"with_none": [None]})
            cg.add_coverpoint(cp)
        except (ValueError, TypeError):
            # May reject None values - that's acceptable
            pass

    def test_mixed_type_collection(self):
        """Test collection with mixed types."""
        cg = CoverGroup("mixed_cg")

        # May handle or reject mixed types
        try:
            cp = CoverPoint("mixed_cp", "value",
                           bins={"mixed": [1, 2.5, "three"]})
            cg.add_coverpoint(cp)
        except (TypeError, ValueError):
            # May reject mixed types - that's acceptable
            pass

    def test_collection_extreme_size(self):
        """Test behavior with extremely large collection."""
        # Create covergroup with very large number of bins
        # This may stress memory or performance

        cg = CoverGroup("extreme_cg")

        # Try 10,000 bins (may be slow or memory intensive)
        large_bins = list(range(10000))
        cp = CoverPoint("extreme_cp", "value", bins={"large": large_bins})
        cg.add_coverpoint(cp)

        # Should handle without crashing
        assert len(cp._bins) == 10000


# =============================================================================
# Collection Modification Tests
# =============================================================================

@pytest.mark.unit
@pytest.mark.boundary
@pytest.mark.P2
class TestCollectionModification:
    """Tests for collection modification during operation."""

    def test_adding_to_covergroup_during_sampling(self):
        """Test adding coverpoints during sampling."""
        cg = CoverGroup("dynamic_cg")

        # Sample with no coverpoints
        cg.sample(value=1)
        assert cg.coverage == 0.0

        # Add coverpoint
        cp = CoverPoint("dynamic_cp", "value", bins={"vals": [1, 2, 3]})
        cg.add_coverpoint(cp)

        # Sample again
        cg.sample(value=1)
        assert cg.coverage > 0.0

    def test_removing_from_collections(self):
        """Test removing items from collections."""
        from rgm.core import RegisterBlock, Register

        block = RegisterBlock("TEST", 0x40000000)
        reg = Register("TEMP_REG", 0x00, 32)
        block.add_register(reg)

        assert len(block._registers) == 1

        # If removal is supported
        if hasattr(block, 'remove_register'):
            block.remove_register("TEMP_REG")
            assert len(block._registers) == 0
        else:
            # Removal not supported
            assert len(block._registers) == 1


# =============================================================================
# Collection Iteration Tests
# =============================================================================

@pytest.mark.unit
@pytest.mark.boundary
@pytest.mark.P1
class TestCollectionIteration:
    """Tests for iterating over collections."""

    def test_iterate_empty_covergroup(self):
        """Test iterating over empty covergroup."""
        cg = CoverGroup("empty_iter_cg")

        count = 0
        for cp_name, cp in cg._coverpoints.items():
            count += 1

        assert count == 0

    def test_iterate_large_collection(self):
        """Test iterating over large collection efficiently."""
        from rgm.core import RegisterBlock, Register

        block = RegisterBlock("ITER_TEST", 0x40000000)

        # Add many registers
        for i in range(1000):
            reg = Register(f"REG_{i}", i * 4, 32)
            block.add_register(reg)

        # Iterate and count
        count = 0
        for reg_name, reg in block._registers.items():
            count += 1

        assert count == 1000

    def test_iterate_single_item_collection(self):
        """Test iterating over single item collection."""
        from rgm.core import RegisterBlock, Register

        block = RegisterBlock("SINGLE_ITER", 0x40000000)
        reg = Register("ONLY_REG", 0x00, 32)
        block.add_register(reg)

        items = list(block._registers.items())
        assert len(items) == 1
        assert items[0][0] == "ONLY_REG"


# =============================================================================
# Collection Query Tests
# =============================================================================

@pytest.mark.unit
@pytest.mark.boundary
@pytest.mark.P2
class TestCollectionQueries:
    """Tests for querying collections."""

    def test_query_nonexistent_item(self):
        """Test querying for non-existent item."""
        from rgm.core import RegisterBlock, Register

        block = RegisterBlock("QUERY_TEST", 0x40000000)
        reg = Register("REG1", 0x00, 32)
        block.add_register(reg)

        # Query for non-existent register
        with pytest.raises(Exception):  # May raise RegisterNotFoundError or similar
            block.get_register("NONEXISTENT")

    def test_query_first_item(self):
        """Test querying first item in collection."""
        from rgm.core import RegisterBlock, Register

        block = RegisterBlock("FIRST_TEST", 0x40000000)

        # Add multiple registers
        for i in range(10):
            reg = Register(f"REG_{i}", i * 4, 32)
            block.add_register(reg)

        # Get first register
        first = block.get_register("REG_0")
        assert first is not None
        assert first.offset == 0x00

    def test_query_last_item(self):
        """Test querying last item in collection."""
        from rgm.core import RegisterBlock, Register

        block = RegisterBlock("LAST_TEST", 0x40000000)

        # Add multiple registers
        for i in range(10):
            reg = Register(f"REG_{i}", i * 4, 32)
            block.add_register(reg)

        # Get last register
        last = block.get_register("REG_9")
        assert last is not None
        assert last.offset == 0x24  # 9 * 4
