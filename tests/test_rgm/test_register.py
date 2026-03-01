"""
Unit Tests for Register Class

Tests Register functionality including:
- Field management
- Register read/write
- UVM-style interfaces (set/get/update/mirror/poke/peek)
- Address calculation
"""

import pytest
from rgm.core import Register, Field, AccessType


class TestRegisterCreation:
    """Test Register initialization and basic properties."""

    def test_register_basic_creation(self):
        """Test basic register creation."""
        reg = Register("CTRL", 0x00, 32)
        assert reg.name == "CTRL"
        assert reg.offset == 0x00
        assert reg.width == 32
        assert reg.reset_value == 0

    def test_register_custom_reset_value(self):
        """Test register with custom reset value."""
        reg = Register("STATUS", 0x04, 32, reset_value=0xDEADBEEF)
        assert reg.reset_value == 0xDEADBEEF

    def test_register_different_widths(self):
        """Test registers with different widths."""
        reg8 = Register("REG8", 0x00, 8)
        reg16 = Register("REG16", 0x01, 16)
        reg32 = Register("REG32", 0x02, 32)
        reg64 = Register("REG64", 0x03, 64)

        assert reg8.width == 8
        assert reg16.width == 16
        assert reg32.width == 32
        assert reg64.width == 64


class TestRegisterFieldManagement:
    """Test adding and managing fields."""

    def test_add_single_field(self):
        """Test adding a single field."""
        reg = Register("CTRL", 0x00, 32)
        field = Field("enable", 0, 1, AccessType.RW, 0)
        reg.add_field(field)

        assert "enable" in reg._fields
        assert reg.get_field("enable") is field

    def test_add_multiple_fields(self):
        """Test adding multiple fields."""
        reg = Register("CTRL", 0x00, 32)
        reg.add_field(Field("enable", 0, 1, AccessType.RW, 0))
        reg.add_field(Field("mode", 1, 3, AccessType.RW, 0))
        reg.add_field(Field("reserved", 4, 28, AccessType.RO, 0))

        assert len(reg.get_fields()) == 3

    def test_field_parent_reference(self):
        """Test that field gets parent reference."""
        reg = Register("CTRL", 0x00, 32)
        field = Field("enable", 0, 1, AccessType.RW, 0)
        reg.add_field(field)

        assert field._parent_register is reg

    def test_get_nonexistent_field(self):
        """Test getting a field that doesn't exist."""
        reg = Register("CTRL", 0x00, 32)
        assert reg.get_field("nonexistent") is None

    def test_get_fields_returns_all(self):
        """Test get_fields returns all fields."""
        reg = Register("CTRL", 0x00, 32)
        reg.add_field(Field("f1", 0, 1, AccessType.RW, 0))
        reg.add_field(Field("f2", 1, 1, AccessType.RW, 0))

        fields = reg.get_fields()
        assert len(fields) == 2


class TestRegisterReadWrite:
    """Test register read and write operations."""

    def test_write_read_register(self):
        """Test basic register write and read."""
        reg = Register("DATA", 0x00, 32)
        reg.write(0x12345678)
        assert reg.read() == 0x12345678

    def test_write_masks_to_width(self):
        """Test that write masks value to register width."""
        reg = Register("DATA", 0x00, 16)  # 16-bit register
        reg.write(0xFFFFFFFF)  # Try to write 32 bits
        assert reg.read() == 0xFFFF  # Should be masked to 16 bits

    def test_write_truncates_negative(self):
        """Test writing negative value."""
        reg = Register("DATA", 0x00, 32)
        reg.write(-1)  # Two's complement all 1s
        assert reg.read() == 0xFFFFFFFF

    def test_read_field_from_register(self):
        """Test reading a field value from register."""
        reg = Register("CTRL", 0x00, 32)
        reg.add_field(Field("enable", 0, 1, AccessType.RW, 0))
        reg.add_field(Field("mode", 1, 3, AccessType.RW, 0))

        # Write 0b1010 to register
        reg.write(0xA)

        # Read fields
        assert reg.read_field("enable") == 0
        assert reg.read_field("mode") == 5  # 0b101 = 5

    def test_write_field_to_register(self):
        """Test writing a field value."""
        reg = Register("CTRL", 0x00, 32)
        reg.add_field(Field("enable", 0, 1, AccessType.RW, 0))
        reg.add_field(Field("mode", 1, 3, AccessType.RW, 0))

        # Write individual fields
        reg.write_field("enable", 1)
        reg.write_field("mode", 7)  # 0b111

        # Read full register
        value = reg.read()
        assert value == 0xE  # 0b1110


class TestRegisterFieldReadModifyWrite:
    """Test read-modify-write behavior for field writes."""

    def test_read_modify_write_preserves_other_bits(self):
        """Test that writing a field preserves other bits."""
        reg = Register("CTRL", 0x00, 32)
        reg.add_field(Field("enable", 0, 1, AccessType.RW, 0))
        reg.add_field(Field("mode", 4, 3, AccessType.RW, 0))

        # Set initial value: 0x123
        reg.write(0x123)

        # Write mode field (bits 4-6)
        reg.write_field("mode", 5)

        # Check that enable (bit 0) is preserved
        assert reg.read_field("enable") == 1  # 0x123 has bit 0 set
        assert reg.read_field("mode") == 5

    def test_write_ro_field_does_not_modify(self):
        """Test that writing RO field doesn't modify register."""
        reg = Register("STATUS", 0x00, 32)
        reg.add_field(Field("flag", 0, 1, AccessType.RO, 0))

        reg.write(0xFFFFFFFF)
        reg.write_field("flag", 1)  # Should have no effect
        assert reg.read_field("flag") == 0


class TestRegisterReset:
    """Test register reset functionality."""

    def test_reset_to_reset_value(self):
        """Test reset restores reset value."""
        reg = Register("CTRL", 0x00, 32, reset_value=0x55AA55AA)
        reg.write(0xFFFFFFFF)
        reg.reset()
        assert reg.read() == 0x55AA55AA

    def test_reset_fields_also(self):
        """Test that reset also resets field values."""
        reg = Register("CTRL", 0x00, 32)
        reg.add_field(Field("enable", 0, 1, AccessType.RW, 0))

        reg.write_field("enable", 1)
        reg.reset()
        assert reg.read_field("enable") == 0


class TestUVMStyleInterfaces:
    """Test UVM-style interfaces: set/get/update/mirror/poke/peek."""

    def test_set_updates_desired_value(self):
        """Test set() updates desired value."""
        reg = Register("CTRL", 0x00, 32)
        reg.set(0xABCDEF00)
        assert reg._desired_value == 0xABCDEF00
        # Mirror value not updated yet
        assert reg.get() == 0

    def test_get_returns_mirror_value(self):
        """Test get() returns mirror value."""
        reg = Register("CTRL", 0x00, 32, reset_value=0x11111111)
        assert reg.get() == 0x11111111

    def test_update_writes_desired_to_hardware(self):
        """Test update() writes desired value."""
        reg = Register("CTRL", 0x00, 32)
        reg.set(0x12345678)
        reg.update()  # Should write desired value
        assert reg.read() == 0x12345678

    def test_mirror_syncs_hardware_to_mirror(self):
        """Test mirror() syncs hardware value."""
        reg = Register("CTRL", 0x00, 32)
        reg.set(0xAAA)  # Set mirror
        # Simulate hardware having different value
        reg._actual_value = 0xBBB

        # Mirror should sync actual to mirror
        value = reg.mirror(check=False)
        assert value == 0xBBB
        assert reg.get() == 0xBBB

    def test_mirror_with_check_raises_on_mismatch(self):
        """Test mirror with check raises on mismatch."""
        reg = Register("CTRL", 0x00, 32)
        reg.set(0xAAA)  # Mirror value
        reg._actual_value = 0xBBB  # Different actual value

        with pytest.raises(ValueError, match="mismatch"):
            reg.mirror(check=True)

    def test_poke_forces_write(self):
        """Test poke() forces write ignoring permissions."""
        reg = Register("STATUS", 0x00, 32)
        reg.add_field(Field("flag", 0, 1, AccessType.RO, 0))

        # Even with RO field, poke should work
        reg.poke(0xFFFFFFFF)
        assert reg.peek() == 0xFFFFFFFF

    def test_peek_reads_value(self):
        """Test peek() reads value."""
        reg = Register("CTRL", 0x00, 32)
        reg.write(0x12345678)
        assert reg.peek() == 0x12345678


class TestRegisterAccessInterface:
    """Test register with access interface."""

    def test_set_access_interface(self):
        """Test setting access interface."""
        reg = Register("CTRL", 0x00, 32)
        mock_interface = MockAccessInterface()
        reg.set_access_interface(mock_interface)
        assert reg._access_interface is mock_interface

    def test_write_uses_access_interface(self):
        """Test that write uses access interface."""
        reg = Register("CTRL", 0x00, 32, reset_value=0x1000)
        mock_interface = MockAccessInterface()
        reg.set_access_interface(mock_interface)

        reg.write(0x2000)
        assert mock_interface.last_write_addr == 0x00
        assert mock_interface.last_write_value == 0x2000

    def test_read_uses_access_interface(self):
        """Test that read uses access interface."""
        reg = Register("CTRL", 0x00, 32)
        mock_interface = MockAccessInterface()
        mock_interface.read_value = 0x1234
        reg.set_access_interface(mock_interface)

        value = reg.read()
        assert value == 0x1234
        assert mock_interface.last_read_addr == 0x00


class TestRegisterAddressCalculation:
    """Test address calculation methods."""

    def test_get_address_no_parent(self):
        """Test get_address without parent."""
        reg = Register("CTRL", 0x00, 32)
        assert reg.get_address() == 0x00

    def test_get_address_with_parent(self):
        """Test get_address with parent block."""
        reg = Register("CTRL", 0x00, 32)
        # Parent would set base address
        # This is tested in register_block tests
        pass


class TestRegisterRepresentation:
    """Test register representation."""

    def test_repr(self):
        """Test string representation."""
        reg = Register("CTRL", 0x00, 32)
        repr_str = repr(reg)
        assert "Register" in repr_str
        assert "CTRL" in repr_str


# Mock access interface for testing
class MockAccessInterface:
    """Mock access interface for testing."""

    def __init__(self):
        self.read_value = 0
        self.last_read_addr = None
        self.last_write_addr = None
        self.last_write_value = None

    def read(self, address: int) -> int:
        self.last_read_addr = address
        return self.read_value

    def write(self, address: int, value: int) -> None:
        self.last_write_addr = address
        self.last_write_value = value

    def is_available(self) -> bool:
        return True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
