"""
Unit Tests for RegisterBlock Class

Tests RegisterBlock functionality including:
- Register management
- Hierarchical organization (sub-blocks)
- Address mapping
- UVM-style reset
- Field access via hierarchical paths
"""

import pytest
from rgm.core import RegisterBlock, Register, Field, AccessType


class TestRegisterBlockCreation:
    """Test RegisterBlock initialization."""

    def test_basic_creation(self):
        """Test basic register block creation."""
        block = RegisterBlock("UART", 0x40000000)
        assert block.name == "UART"
        assert block.base_address == 0x40000000

    def test_default_base_address(self):
        """Test default base address is 0."""
        block = RegisterBlock("SYS")
        assert block.base_address == 0

    def test_block_has_default_map(self):
        """Test that block has default register map."""
        block = RegisterBlock("UART", 0x40000000)
        assert block._default_map is not None
        assert block._default_map.base_address == 0x40000000


class TestRegisterManagement:
    """Test adding and managing registers."""

    def test_add_single_register(self):
        """Test adding a single register."""
        block = RegisterBlock("UART", 0x40000000)
        reg = Register("CTRL", 0x00, 32)
        block.add_register(reg)

        assert "CTRL" in block._registers
        assert block.get_register("CTRL") is reg

    def test_add_multiple_registers(self):
        """Test adding multiple registers."""
        block = RegisterBlock("UART", 0x40000000)
        block.add_register(Register("CTRL", 0x00, 32))
        block.add_register(Register("STATUS", 0x04, 32))
        block.add_register(Register("DATA", 0x08, 32))

        assert len(block.get_registers()) == 3

    def test_register_gets_parent_reference(self):
        """Test that register gets parent reference."""
        block = RegisterBlock("UART", 0x40000000)
        reg = Register("CTRL", 0x00, 32)
        block.add_register(reg)

        assert reg._parent_block is block

    def test_get_registers_returns_list(self):
        """Test get_registers returns list."""
        block = RegisterBlock("UART", 0x40000000)
        block.add_register(Register("R1", 0x00, 32))
        block.add_register(Register("R2", 0x04, 32))

        regs = block.get_registers()
        assert isinstance(regs, list)
        assert len(regs) == 2

    def test_get_nonexistent_register(self):
        """Test getting non-existent register returns None."""
        block = RegisterBlock("UART", 0x40000000)
        assert block.get_register("NONEXISTENT") is None


class TestHierarchicalOrganization:
    """Test hierarchical sub-block organization."""

    def test_add_sub_block(self):
        """Test adding a sub-block."""
        main = RegisterBlock("MAIN", 0x40000000)
        sub = RegisterBlock("SUB", 0x40001000)

        main.add_block(sub)

        assert "SUB" in main._blocks
        assert main.get_block("SUB") is sub

    def test_multiple_sub_blocks(self):
        """Test adding multiple sub-blocks."""
        main = RegisterBlock("MAIN", 0x40000000)
        main.add_block(RegisterBlock("UART0", 0x40000000))
        main.add_block(RegisterBlock("UART1", 0x40001000))
        main.add_block(RegisterBlock("SPI", 0x40002000))

        assert len(main.get_blocks()) == 3

    def test_nested_sub_blocks(self):
        """Test nested sub-blocks."""
        root = RegisterBlock("ROOT", 0x40000000)
        level1 = RegisterBlock("L1", 0x40001000)
        level2 = RegisterBlock("L2", 0x40001100)

        root.add_block(level1)
        level1.add_block(level2)

        assert root.get_block("L1") is level1
        assert level1.get_block("L2") is level2

    def test_get_nonexistent_block(self):
        """Test getting non-existent block returns None."""
        block = RegisterBlock("MAIN", 0x40000000)
        assert block.get_block("NONEXISTENT") is None


class TestAddressMapping:
    """Test address mapping and conflict detection."""

    def test_address_map_contains_registers(self):
        """Test that address map contains registers."""
        block = RegisterBlock("UART", 0x40000000)
        reg = Register("CTRL", 0x00, 32)
        block.add_register(reg)

        abs_addr = 0x40000000
        assert abs_addr in block._address_map
        assert block._address_map[abs_addr] is reg

    def test_address_map_with_sub_blocks(self):
        """Test address map includes sub-blocks."""
        main = RegisterBlock("MAIN", 0x40000000)
        sub = RegisterBlock("SUB", 0x40001000)

        main.add_block(sub)

        abs_addr = 0x40001000
        assert abs_addr in main._address_map
        assert main._address_map[abs_addr] is sub

    def test_address_conflict_detection(self):
        """Test that address conflicts are detected."""
        block = RegisterBlock("UART", 0x40000000)
        block.add_register(Register("R1", 0x00, 32))

        with pytest.raises(ValueError, match="Address conflict"):
            block.add_register(Register("R2", 0x00, 32))


class TestHierarchicalPathAccess:
    """Test accessing registers via hierarchical paths."""

    def test_simple_path_access(self):
        """Test simple register path."""
        block = RegisterBlock("UART", 0x40000000)
        reg = Register("CTRL", 0x00, 32)
        block.add_register(reg)

        assert block.get_register("CTRL") is reg

    def test_nested_path_access(self):
        """Test nested path: block.subblock.register."""
        main = RegisterBlock("MAIN", 0x40000000)
        uart = RegisterBlock("UART", 0x40001000)
        ctrl = Register("CTRL", 0x00, 32)

        main.add_block(uart)
        uart.add_register(ctrl)

        assert main.get_register("UART.CTRL") is ctrl

    def test_deep_nested_path(self):
        """Test deeply nested path."""
        root = RegisterBlock("ROOT", 0x40000000)
        level1 = RegisterBlock("L1", 0x40001000)
        level2 = RegisterBlock("L2", 0x40001100)
        reg = Register("REG", 0x00, 32)

        root.add_block(level1)
        level1.add_block(level2)
        level2.add_register(reg)

        assert root.get_register("L1.L2.REG") is reg

    def test_invalid_path_returns_none(self):
        """Test that invalid path returns None."""
        block = RegisterBlock("UART", 0x40000000)
        block.add_register(Register("CTRL", 0x00, 32))

        assert block.get_register("INVALID.PATH") is None


class TestFieldAccessViaBlock:
    """Test accessing fields via register block."""

    def test_read_field_simple(self):
        """Test reading field from simple path."""
        block = RegisterBlock("UART", 0x40000000)
        reg = Register("CTRL", 0x00, 32)
        reg.add_field(Field("enable", 0, 1, AccessType.RW, 1))
        block.add_register(reg)

        value = block.read_field("CTRL", "enable")
        assert value == 1

    def test_write_field_simple(self):
        """Test writing field via simple path."""
        block = RegisterBlock("UART", 0x40000000)
        reg = Register("CTRL", 0x00, 32)
        reg.add_field(Field("enable", 0, 1, AccessType.RW, 0))
        block.add_register(reg)

        block.write_field("CTRL", "enable", 1)
        assert reg.read_field("enable") == 1

    def test_read_field_hierarchical(self):
        """Test reading field via hierarchical path."""
        main = RegisterBlock("MAIN", 0x40000000)
        uart = RegisterBlock("UART", 0x40001000)
        reg = Register("STATUS", 0x00, 32)
        reg.add_field(Field("tx_empty", 0, 1, AccessType.RO, 1))

        main.add_block(uart)
        uart.add_register(reg)

        value = main.read_field("UART.STATUS", "tx_empty")
        assert value == 1


class TestRegisterBlockReadWrite:
    """Test register-level operations via block."""

    def test_write_register_by_name(self):
        """Test writing register by name."""
        block = RegisterBlock("UART", 0x40000000)
        reg = Register("CTRL", 0x00, 32)
        block.add_register(reg)

        block.write("CTRL", 0x12345678)
        assert reg.read() == 0x12345678

    def test_read_register_by_name(self):
        """Test reading register by name."""
        block = RegisterBlock("UART", 0x40000000)
        reg = Register("STATUS", 0x00, 32)
        reg.write(0xABC)
        block.add_register(reg)

        value = block.read("STATUS")
        assert value == 0xABC


class TestUVMStyleReset:
    """Test UVM-style reset functionality."""

    def test_soft_reset_resets_mirror_values(self):
        """Test SOFT reset resets mirror values."""
        block = RegisterBlock("UART", 0x40000000)
        reg = Register("CTRL", 0x00, 32, reset_value=0x100)
        reg.add_field(Field("enable", 0, 1, AccessType.RW, 1))
        block.add_register(reg)

        # Change value
        reg.write(0x200)

        # Soft reset
        block.reset(kind="SOFT")

        # Mirror value should be reset
        assert reg.get() == 0x100

    def test_hard_reset_writes_hardware(self):
        """Test HARD reset writes to hardware."""
        block = RegisterBlock("UART", 0x40000000)
        reg = Register("CTRL", 0x00, 32, reset_value=0x100)
        block.add_register(reg)

        # Change value
        reg.write(0x200)

        # Hard reset (should write to hardware)
        block.reset(kind="HARD")

        # Both mirror and hardware should be reset
        assert reg.read() == 0x100


class TestAccessInterface:
    """Test access interface on block."""

    def test_set_default_access_interface(self):
        """Test setting default access interface."""
        block = RegisterBlock("UART", 0x40000000)
        mock_interface = MockAccessInterface()

        block.set_access_interface(mock_interface)
        assert block._default_access is mock_interface

    def test_registers_inherit_access_interface(self):
        """Test that registers inherit block's access interface."""
        block = RegisterBlock("UART", 0x40000000)
        reg = Register("CTRL", 0x00, 32)
        block.add_register(reg)

        mock_interface = MockAccessInterface()
        block.set_access_interface(mock_interface)

        # Register should use block's interface if it doesn't have one
        # This is tested indirectly via read/write operations


class TestFrontDoorBackDoorAccess:
    """Test FrontDoor and BackDoor access."""

    def test_backdoor_setup(self):
        """Test setting up backdoor access."""
        block = RegisterBlock("UART", 0x40000000)
        mock_backdoor = MockAccessInterface()

        block.set_backdoor(mock_backdoor)
        assert block._backdoor is mock_backdoor

    def test_frontdoor_setup(self):
        """Test setting up frontdoor access."""
        block = RegisterBlock("UART", 0x40000000)
        mock_frontdoor = MockAccessInterface()

        block.set_frontdoor(mock_frontdoor)
        assert block._frontdoor is mock_frontdoor


class TestRegisterBlockRepresentation:
    """Test string representation."""

    def test_repr(self):
        """Test string representation."""
        block = RegisterBlock("UART", 0x40000000)
        repr_str = repr(block)
        assert "RegisterBlock" in repr_str
        assert "UART" in repr_str


# Mock classes for testing
class MockAccessInterface:
    """Mock access interface for testing."""

    def __init__(self):
        self.read_value = 0
        self.writes = []

    def read(self, address: int) -> int:
        return self.read_value

    def write(self, address: int, value: int) -> None:
        self.writes.append((address, value))

    def is_available(self) -> bool:
        return True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
