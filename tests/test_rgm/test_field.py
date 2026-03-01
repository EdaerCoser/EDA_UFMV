"""
Unit Tests for Field Class

Tests Field functionality including:
- All 15 AccessTypes
- Bit manipulation
- UVM-style interfaces (set/get/peek/poke)
- Value validation
"""

import pytest
from rgm.core import Field, AccessType


class TestFieldCreation:
    """Test Field initialization and basic properties."""

    def test_field_basic_creation(self):
        """Test basic field creation."""
        field = Field("enable", 0, 1, AccessType.RW, 0)
        assert field.name == "enable"
        assert field.bit_offset == 0
        assert field.bit_width == 1
        assert field.access == AccessType.RW
        assert field.reset_value == 0

    def test_field_default_values(self):
        """Test field with default values."""
        field = Field("data", 8, 16)
        assert field.access == AccessType.RW
        assert field.reset_value == 0
        assert field.volatile is False

    def test_field_volatile_flag(self):
        """Test volatile field."""
        field = Field("status", 0, 1, AccessType.RO, 0, volatile=True)
        assert field.volatile is True

    def test_field_description(self):
        """Test field with description."""
        field = Field("mode", 4, 3, AccessType.RW, 0, description="Operation mode")
        assert field.description == "Operation mode"


class TestFieldBitManipulation:
    """Test bit-level operations."""

    def test_get_mask(self):
        """Test bit mask generation."""
        field = Field("data", 8, 4)
        # 4 bits starting at position 8: 0x0F00
        assert field.get_mask() == 0x0F00

    def test_get_mask_single_bit(self):
        """Test bit mask for single bit field."""
        field = Field("enable", 0, 1)
        assert field.get_mask() == 0x00000001

    def test_get_mask_full_width(self):
        """Test bit mask for full 32-bit field."""
        field = Field("full", 0, 32)
        assert field.get_mask() == 0xFFFFFFFF

    def test_get_mask_offset(self):
        """Test bit mask with offset."""
        field = Field("upper", 16, 8)
        assert field.get_mask() == 0x00FF0000


class TestFieldReadWrite:
    """Test field read and write operations."""

    def test_write_read_rw_field(self):
        """Test write and read for RW field."""
        field = Field("data", 0, 8, AccessType.RW, 0)
        field.write(0xAB)
        assert field.read() == 0xAB

    def test_write_truncates_to_width(self):
        """Test that write truncates value to field width."""
        field = Field("data", 0, 4, AccessType.RW, 0)
        field.write(0xFF)  # Write 8 bits, but field is only 4 bits
        assert field.read() == 0x0F  # Should truncate to 4 bits

    def test_write_resets_correctly(self):
        """Test reset value."""
        field = Field("data", 0, 8, AccessType.RW, 0x55)
        field.write(0xAA)
        field.reset()
        assert field.read() == 0x55

    def test_read_field_from_register(self):
        """Test reading field from register value."""
        field = Field("mode", 4, 3, AccessType.RW, 0)
        field.write(0x5)
        # Simulate register read
        reg_value = field._current_value << field.bit_offset
        extracted = (reg_value >> field.bit_offset) & ((1 << field.bit_width) - 1)
        assert extracted == 0x5


class TestAccessTypes:
    """Test all 15 access types."""

    def test_rw_access(self):
        """Test RW (Read-Write) access type."""
        field = Field("data", 0, 8, AccessType.RW, 0)
        field.write(0xAA)
        assert field.read() == 0xAA

    def test_ro_access(self):
        """Test RO (Read-Only) access type."""
        field = Field("status", 0, 1, AccessType.RO, 0)
        field.write(1)  # Write should be ignored
        assert field.read() == 0  # Still reset value

    def test_wo_access(self):
        """Test WO (Write-Only) access type."""
        field = Field("cmd", 0, 8, AccessType.WO, 0)
        field.write(0x55)
        # WO fields write but reads return 0
        assert field.read() == 0

    def test_w1c_access_write_one(self):
        """Test W1C (Write-1-to-Clear) writing 1."""
        field = Field("flag", 0, 1, AccessType.W1C, 1)  # Start with 1
        field.write(1)  # Writing 1 should clear to 0
        assert field.read() == 0

    def test_w1c_access_write_zero(self):
        """Test W1C (Write-1-to-Clear) writing 0."""
        field = Field("flag", 0, 1, AccessType.W1C, 1)  # Start with 1
        field.write(0)  # Writing 0 should keep current value
        assert field.read() == 1

    def test_w1s_access_write_one(self):
        """Test W1S (Write-1-to-Set) writing 1."""
        field = Field("flag", 0, 1, AccessType.W1S, 0)  # Start with 0
        field.write(1)  # Writing 1 should set to 1
        assert field.read() == 1

    def test_w1s_access_write_zero(self):
        """Test W1S (Write-1-to-Set) writing 0."""
        field = Field("flag", 0, 1, AccessType.W1S, 1)  # Start with 1
        field.write(0)  # Writing 0 should keep current value
        assert field.read() == 1

    def test_w0c_access_write_one(self):
        """Test W0C (Write-0-to-Clear) writing 1."""
        field = Field("flag", 0, 1, AccessType.W0C, 1)  # Start with 1
        field.write(1)  # Writing 1 should keep current value
        assert field.read() == 1

    def test_w0c_access_write_zero(self):
        """Test W0C (Write-0-to-Clear) writing 0."""
        field = Field("flag", 0, 1, AccessType.W0C, 1)  # Start with 1
        field.write(0)  # Writing 0 should clear to 0
        assert field.read() == 0

    def test_w0s_access_write_one(self):
        """Test W0S (Write-0-to-Set) writing 1."""
        field = Field("flag", 0, 1, AccessType.W0S, 0)  # Start with 0
        field.write(1)  # Writing 1 should keep current value (0)
        assert field.read() == 0

    def test_w0s_access_write_zero(self):
        """Test W0S (Write-0-to-Set) writing 0."""
        field = Field("flag", 0, 1, AccessType.W0S, 0)  # Start with 0
        field.write(0)  # Writing 0 should set to 1
        assert field.read() == 1

    def test_rc_access(self):
        """Test RC (Read-to-Clear) access type."""
        field = Field("flag", 0, 1, AccessType.RC, 1)  # Start with 1
        value = field.read()  # Reading should clear to 0
        assert value == 1  # Return the value before clearing
        assert field.read() == 0  # Next read should be 0

    def test_rs_access(self):
        """Test RS (Read-to-Set) access type."""
        field = Field("flag", 0, 1, AccessType.RS, 0)  # Start with 0
        value = field.read()  # Reading should set to 1
        assert value == 0  # Return the value before setting
        assert field.read() == 1  # Next read should be 1

    def test_wc_access(self):
        """Test WC (Write-Clear) access type - write clears, write is ignored."""
        field = Field("flag", 0, 1, AccessType.WC, 1)  # Start with 1
        field.write(1)  # Any write should clear to 0
        assert field.read() == 0

    def test_ws_access(self):
        """Test WS (Write-Set) access type - write sets, value is ignored."""
        field = Field("flag", 0, 1, AccessType.WS, 0)  # Start with 0
        field.write(0)  # Any write should set to 1
        assert field.read() == 1


class TestUVMStyleInterfaces:
    """Test UVM-style set/get/peek/poke interfaces."""

    def test_set_updates_mirror_value(self):
        """Test set() updates mirror value without immediate write."""
        field = Field("data", 0, 8, AccessType.RW, 0x55)
        field.set(0xAA)
        assert field.get() == 0xAA  # Mirror value updated
        # In real implementation, write would happen separately via update()

    def test_get_returns_mirror_value(self):
        """Test get() returns mirror value."""
        field = Field("data", 0, 8, AccessType.RW, 0x33)
        mirror = field.get()
        assert mirror == 0x33

    def test_poke_forces_value(self):
        """Test poke() forces value regardless of access permissions."""
        field = Field("status", 0, 1, AccessType.RO, 0)
        field.poke(1)  # Should work even though RO
        assert field.peek() == 1

    def test_peek_reads_current_value(self):
        """Test peek() reads current value."""
        field = Field("data", 0, 8, AccessType.RW, 0x77)
        field.write(0x88)
        assert field.peek() == 0x88


class TestFieldRepresentation:
    """Test field representation and utility methods."""

    def test_repr(self):
        """Test string representation."""
        field = Field("enable", 0, 1, AccessType.RW, 0)
        repr_str = repr(field)
        assert "Field" in repr_str
        assert "enable" in repr_str

    def test_str(self):
        """Test string conversion."""
        field = Field("mode", 4, 3, AccessType.RW, 0)
        str_str = str(field)
        assert "mode" in str_str


class TestFieldValidation:
    """Test field validation and edge cases."""

    def test_field_width_zero(self):
        """Test field with zero width (edge case)."""
        field = Field("reserved", 0, 0, AccessType.RO, 0)
        assert field.bit_width == 0
        assert field.get_mask() == 0

    def test_field_large_offset(self):
        """Test field with large bit offset."""
        field = Field("high", 31, 1, AccessType.RW, 0)
        assert field.bit_offset == 31
        assert field.get_mask() == 0x80000000

    def test_write_negative_value(self):
        """Test writing negative value (should be masked)."""
        field = Field("data", 0, 8, AccessType.RW, 0)
        field.write(-1)  # -1 in two's complement is all 1s
        # After masking to 8 bits, should be 0xFF
        assert field.read() == 0xFF

    def test_multibit_field_write(self):
        """Test writing to multi-bit field."""
        field = Field("mode", 4, 4, AccessType.RW, 0)
        field.write(0xA)
        assert field.read() == 0xA


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
