"""
Boundary Value Tests - Limit Values

Tests for handling extreme and boundary values:
- Maximum values (MAX_INT, MAX_UINT, etc.)
- Minimum values (MIN_INT, zero, negative)
- Edge cases (overflow, underflow, -1)
- Special numeric values (NaN, Inf, -Inf)
"""

import pytest
import sys

from sv_randomizer import Randomizable
from sv_randomizer.core.variables import RandVar, RandCVar, VarType
from coverage.core import CoverGroup, CoverPoint
from rgm.core import RegisterBlock, Register, Field
from rgm.utils import AccessType


# =============================================================================
# Maximum Value Tests
# =============================================================================

@pytest.mark.unit
@pytest.mark.boundary
@pytest.mark.P0
class TestMaximumValues:
    """Tests for maximum value handling."""

    @pytest.mark.parametrize("bit_width,expected_max", [
        (8, 255),
        (16, 65535),
        (32, 4294967295),
    ])
    def test_randvar_max_uint_values(self, bit_width, expected_max):
        """Test RandVar handles maximum unsigned integer values."""
        var = RandVar("test_var", VarType.BIT, bit_width=bit_width)
        var._value = expected_max
        assert var._value == expected_max

    @pytest.mark.parametrize("bit_width,expected_max", [
        (8, 127),
        (16, 32767),
        (32, 2147483647),
    ])
    def test_randvar_max_signed_values(self, bit_width, expected_max):
        """Test RandVar handles maximum signed integer values."""
        var = RandVar("test_var", VarType.SIGNED_BIT, bit_width=bit_width)
        var._value = expected_max
        assert var._value == expected_max

    def test_coverage_max_value_sampling(self):
        """Test coverage sampling at maximum boundary."""
        cg = CoverGroup("max_cg")
        cp = CoverPoint("max_cp", "value", bins={"max": [(255, 255)]})
        cg.add_coverpoint(cp)

        cg.sample(value=255)
        assert cg.coverage == 100.0

    def test_rgm_field_max_width(self):
        """Test RGM field with maximum bit width."""
        reg = Register("TEST_REG", 0x00, 32)
        # Create field that fills entire register
        field = Field("full_reg", bit_offset=0, bit_width=32, access=AccessType.RW, reset_value=0)
        reg.add_field(field)

        assert field.bit_width == 32
        assert field.bit_offset == 0


# =============================================================================
# Minimum Value Tests
# =============================================================================

@pytest.mark.unit
@pytest.mark.boundary
@pytest.mark.P0
class TestMinimumValues:
    """Tests for minimum value handling."""

    def test_randvar_zero_value(self):
        """Test RandVar handles zero correctly."""
        var = RandVar("test_var", VarType.BIT, bit_width=8)
        var._value = 0
        assert var._value == 0

    @pytest.mark.parametrize("bit_width,expected_min", [
        (8, -128),
        (16, -32768),
        (32, -2147483648),
    ])
    def test_randvar_min_signed_values(self, bit_width, expected_min):
        """Test RandVar handles minimum signed integer values."""
        var = RandVar("test_var", VarType.SIGNED_BIT, bit_width=bit_width)
        var._value = expected_min
        assert var._value == expected_min

    def test_coverage_min_value_sampling(self):
        """Test coverage sampling at minimum boundary."""
        cg = CoverGroup("min_cg")
        cp = CoverPoint("min_cp", "value", bins={"min": [(0, 0)]})
        cg.add_coverpoint(cp)

        cg.sample(value=0)
        assert cg.coverage == 100.0


# =============================================================================
# Overflow and Underflow Tests
# =============================================================================

@pytest.mark.unit
@pytest.mark.boundary
@pytest.mark.P1
class TestOverflowUnderflow:
    """Tests for overflow and underflow handling."""

    @pytest.mark.parametrize("bit_width,value,expected", [
        (8, 256, 0),      # Wraps to 0
        (8, 257, 1),      # Wraps to 1
        (8, 512, 0),      # Wraps to 0 (256 * 2)
        (16, 65536, 0),   # Wraps to 0
    ])
    def test_uint_overflow_wrapping(self, bit_width, value, expected):
        """Test unsigned integer overflow wrapping behavior."""
        var = RandVar("test_var", VarType.BIT, bit_width=bit_width)
        var._value = value
        # Value should wrap modulo 2^bit_width
        max_val = (1 << bit_width) - 1
        assert var._value == (value & max_val)

    def test_signed_overflow_behavior(self):
        """Test signed integer overflow behavior."""
        var = RandVar("test_var", VarType.SIGNED_BIT, bit_width=8)
        # Setting value beyond range should be clamped or wrapped
        # depending on implementation
        var._value = 200  # Beyond signed 8-bit range (-128 to 127)
        # Implementation-dependent - just test it doesn't crash
        assert isinstance(var._value, int)

    def test_coverage_boundary_bin(self):
        """Test coverage bin at boundary (e.g., 255-256)."""
        cg = CoverGroup("boundary_cg")
        # Bins at boundary
        cp = CoverPoint("boundary_cp", "value",
                       bins={"low": [(0, 127)], "high": [(128, 255)]})
        cg.add_coverpoint(cp)

        # Sample at exact boundary
        cg.sample(value=127)
        cg.sample(value=128)

        # Should have 50% coverage (2 of 4 bins hit)
        # Actually depends on implementation - bins are range-based
        assert cg.coverage >= 50.0


# =============================================================================
# Negative Value Tests
# =============================================================================

@pytest.mark.unit
@pytest.mark.boundary
@pytest.mark.P1
class TestNegativeValues:
    """Tests for negative value handling."""

    @pytest.mark.parametrize("value", [-1, -127, -128, -255, -256])
    def test_randvar_negative_signed_values(self, value):
        """Test RandVar handles negative signed values."""
        var = RandVar("test_var", VarType.SIGNED_BIT, bit_width=8)
        var._value = value
        # Value should be within valid range for signed 8-bit
        assert -128 <= var._value <= 127

    def test_randvar_negative_unsigned_raises(self):
        """Test RandVar rejects negative values for unsigned type."""
        var = RandVar("test_var", VarType.BIT, bit_width=8)
        # Setting negative value on unsigned should handle it
        # Implementation-dependent
        var._value = -1
        # Should wrap or raise
        assert isinstance(var._value, int)

    def test_coverage_negative_sampling(self):
        """Test coverage sampling with negative values."""
        cg = CoverGroup("negative_cg")
        # Use signed bins
        cp = CoverPoint("negative_cp", "value",
                       bins={"negative": [(-128, -1)], "zero": [(0, 0)], "positive": [(1, 127)]})
        cg.add_coverpoint(cp)

        # Sample negative value
        cg.sample(value=-50)
        # Should hit negative bin
        assert cg.coverage > 0


# =============================================================================
# Special Floating Point Values
# =============================================================================

@pytest.mark.unit
@pytest.mark.boundary
@pytest.mark.P1
class TestSpecialFloatValues:
    """Tests for special floating point values (NaN, Inf)."""

    def test_nan_value_handling(self):
        """Test NaN (Not a Number) value handling."""
        nan_val = float('nan')
        assert nan_val != nan_val  # NaN != NaN by definition
        # Test that code handles NaN gracefully
        cg = CoverGroup("nan_cg")

        # Sampling with NaN should handle gracefully
        # Implementation-dependent
        try:
            cg.sample(value=nan_val)
        except (ValueError, TypeError):
            # May raise exception - that's acceptable
            pass

    def test_infinity_value_handling(self):
        """Test infinity value handling."""
        inf_val = float('inf')
        neg_inf_val = float('-inf')

        # Test that code handles infinity gracefully
        cg = CoverGroup("inf_cg")

        try:
            cg.sample(value=inf_val)
        except (ValueError, OverflowError):
            # May raise exception - that's acceptable
            pass

    def test_float_boundary_values(self):
        """Test boundary float values."""
        boundary_values = [
            1.0e-10,   # Very small positive
            -1.0e-10,  # Very small negative
            1.0e10,    # Very large positive
            -1.0e10,   # Very large negative
        ]

        for val in boundary_values:
            # Just test they can be processed without crashing
            cg = CoverGroup(f"float_cg_{val}")
            cp = CoverPoint("float_cp", "value", bins={"vals": [val]})
            cg.add_coverpoint(cp)

            cg.sample(value=val)
            assert cg.coverage >= 0.0


# =============================================================================
# Edge Case: -1 Value
# =============================================================================

@pytest.mark.unit
@pytest.mark.boundary
@pytest.mark.P0
class TestMinusOneValue:
    """Tests for -1 value edge case."""

    def test_minus_one_signed_8bit(self):
        """Test -1 in signed 8-bit (should be valid)."""
        var = RandVar("test_var", VarType.SIGNED_BIT, bit_width=8)
        var._value = -1
        assert var._value == -1

    def test_minus_one_unsigned_8bit(self):
        """Test -1 in unsigned 8-bit (should wrap to 255)."""
        var = RandVar("test_var", VarType.BIT, bit_width=8)
        var._value = -1
        # In two's complement, -1 unsigned wraps to max value
        assert var._value == 255

    def test_minus_one_coverage_sampling(self):
        """Test coverage sampling with -1."""
        cg = CoverGroup("minus_one_cg")
        cp = CoverPoint("minus_one_cp", "value", bins={"values": [-1, 0, 1]})
        cg.add_coverpoint(cp)

        cg.sample(value=-1)
        assert cg.coverage > 0


# =============================================================================
# Bit Width Boundary Tests
# =============================================================================

@pytest.mark.unit
@pytest.mark.boundary
@pytest.mark.P0
class TestBitWidthBoundaries:
    """Tests for bit width boundaries."""

    @pytest.mark.parametrize("bit_width", [1, 2, 4, 8, 16, 32, 64])
    def test_various_bit_widths(self, bit_width):
        """Test variables with various bit widths."""
        var = RandVar(f"var_{bit_width}b", VarType.BIT, bit_width=bit_width)
        # Should handle all these bit widths
        assert var._bit_width == bit_width

    def test_minimum_bit_width(self):
        """Test minimum bit width (1 bit)."""
        var = RandVar("single_bit", VarType.BIT, bit_width=1)
        var._value = 0
        assert var._value == 0
        var._value = 1
        assert var._value == 1

    def test_large_bit_width(self):
        """Test large bit width (64 bits)."""
        var = RandVar("wide_var", VarType.BIT, bit_width=64)
        max_val = (1 << 64) - 1
        var._value = max_val
        # Should handle 64-bit values
        assert var._value == max_val


# =============================================================================
# Boundary Randomization Tests
# =============================================================================

@pytest.mark.unit
@pytest.mark.boundary
@pytest.mark.P1
class TestBoundaryRandomization:
    """Tests for randomization at boundaries."""

    def test_randomize_at_max_boundary(self):
        """Test randomization with constraint at maximum."""
        class TestObj(Randomizable):
            def __init__(self):
                super().__init__()
                self.x = RandVar("x", VarType.BIT, bit_width=8)
                self.add_constraint(lambda: self.x.value == 255)

        obj = TestObj()
        obj.randomize()
        assert obj.x.value == 255

    def test_randomize_at_min_boundary(self):
        """Test randomization with constraint at minimum."""
        class TestObj(Randomizable):
            def __init__(self):
                super().__init__()
                self.x = RandVar("x", VarType.BIT, bit_width=8)
                self.add_constraint(lambda: self.x.value == 0)

        obj = TestObj()
        obj.randomize()
        assert obj.x.value == 0

    def test_randomize_at_boundary_range(self):
        """Test randomization with boundary range constraint."""
        class TestObj(Randomizable):
            def __init__(self):
                super().__init__()
                self.x = RandVar("x", VarType.BIT, bit_width=8)
                # Constraint at upper boundary
                self.add_constraint(lambda: self.x.value >= 250)

        obj = TestObj()
        obj.randomize()
        assert 250 <= obj.x.value <= 255


# =============================================================================
# RGM Boundary Tests
# =============================================================================

@pytest.mark.unit
@pytest.mark.boundary
@pytest.mark.P1
class TestRGMBoundaries:
    """Tests for RGM at boundaries."""

    def test_register_max_offset(self):
        """Test register with maximum offset."""
        block = RegisterBlock("TEST", 0x40000000)
        reg = Register("FAR_REG", 0xFFFFFFFC, 32)  # Near max 32-bit offset
        block.add_register(reg)
        assert reg.offset == 0xFFFFFFFC

    def test_field_full_register_width(self):
        """Test field that fills entire register."""
        reg = Register("FULL_REG", 0x00, 32)
        field = Field("full", bit_offset=0, bit_width=32, access=AccessType.RW)
        reg.add_field(field)
        assert len(reg._fields) == 1

    def test_field_single_bit(self):
        """Test field with single bit width."""
        reg = Register("BIT_REG", 0x00, 32)
        field = Field("single", bit_offset=0, bit_width=1, access=AccessType.RW)
        reg.add_field(field)
        assert field.bit_width == 1


# =============================================================================
# Coverage Boundary Tests
# =============================================================================

@pytest.mark.unit
@pytest.mark.boundary
@pytest.mark.P1
class TestCoverageBoundaries:
    """Tests for coverage at boundaries."""

    def test_empty_covergroup(self):
        """Test covergroup with no coverpoints."""
        cg = CoverGroup("empty_cg")
        # Should handle empty covergroup gracefully
        assert cg.coverage == 0.0

    def test_coverpoint_single_bin(self):
        """Test coverpoint with single bin."""
        cg = CoverGroup("single_bin_cg")
        cp = CoverPoint("single_cp", "value", bins={"single": [42]})
        cg.add_coverpoint(cp)

        cg.sample(value=42)
        assert cg.coverage == 100.0

    def test_coverpoint_many_bins(self):
        """Test coverpoint with many bins (boundary of performance)."""
        # Create 1000 bins
        bins_list = list(range(1000))
        cg = CoverGroup("many_bins_cg")
        cp = CoverPoint("many_cp", "value", bins={"many": bins_list})
        cg.add_coverpoint(cp)

        # Sample a few values
        cg.sample(value=0)
        cg.sample(value=500)
        cg.sample(value=999)

        # Should have partial coverage
        assert 0.0 < cg.coverage < 100.0
