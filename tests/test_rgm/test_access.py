"""
Unit Tests for Access Interfaces

Tests FrontDoor and BackDoor access interfaces including:
- Read/write operations
- Availability checks
- Adapter integration
"""

import pytest
from rgm.access import FrontDoorAccess, BackDoorAccess
from rgm.adapters import AXIAdapter


class MockAdapter:
    """Mock adapter for testing."""

    def __init__(self):
        self.memory = {}
        self.read_count = 0
        self.write_count = 0

    def read(self, address: int) -> int:
        self.read_count += 1
        return self.memory.get(address, 0)

    def write(self, address: int, value: int) -> None:
        self.write_count += 1
        self.memory[address] = value

    def is_connected(self) -> bool:
        return True


class TestFrontDoorAccess:
    """Test FrontDoor (bus-based) access."""

    def test_frontdoor_creation(self):
        """Test creating FrontDoor access."""
        mock_adapter = MockAdapter()
        frontdoor = FrontDoorAccess(mock_adapter)

        assert frontdoor._adapter is mock_adapter
        assert frontdoor._transaction_count == 0

    def test_frontdoor_read_delegates_to_adapter(self):
        """Test that read delegates to adapter."""
        mock_adapter = MockAdapter()
        mock_adapter.memory[0x1000] = 0x1234

        frontdoor = FrontDoorAccess(mock_adapter)
        value = frontdoor.read(0x1000)

        assert value == 0x1234
        assert mock_adapter.read_count == 1

    def test_frontdoor_write_delegates_to_adapter(self):
        """Test that write delegates to adapter."""
        mock_adapter = MockAdapter()
        frontdoor = FrontDoorAccess(mock_adapter)

        frontdoor.write(0x2000, 0x5678)

        assert mock_adapter.write_count == 1
        assert mock_adapter.memory[0x2000] == 0x5678

    def test_frontdoor_is_available(self):
        """Test is_available checks adapter connection."""
        mock_adapter = MockAdapter()
        frontdoor = FrontDoorAccess(mock_adapter)

        assert frontdoor.is_available() is True

    def test_frontdoor_is_available_disconnected(self):
        """Test is_available when adapter disconnected."""
        mock_adapter = MockAdapter()
        # Simulate disconnected adapter
        mock_adapter.is_connected = lambda: False

        frontdoor = FrontDoorAccess(mock_adapter)
        assert frontdoor.is_available() is False

    def test_frontdoor_tracks_transaction_count(self):
        """Test that transaction count is tracked."""
        mock_adapter = MockAdapter()
        frontdoor = FrontDoorAccess(mock_adapter)

        frontdoor.read(0x1000)
        frontdoor.write(0x2000, 0x1234)
        frontdoor.read(0x3000)

        assert frontdoor._transaction_count == 3

    def test_frontdoor_get_transaction_count(self):
        """Test getting transaction count."""
        mock_adapter = MockAdapter()
        frontdoor = FrontDoorAccess(mock_adapter)

        frontdoor.read(0x1000)
        frontdoor.write(0x2000, 0x1234)

        assert frontdoor.get_transaction_count() == 2

    def test_frontdoor_reset_transaction_count(self):
        """Test resetting transaction count."""
        mock_adapter = MockAdapter()
        frontdoor = FrontDoorAccess(mock_adapter)

        frontdoor.read(0x1000)
        frontdoor.reset_transaction_count()

        assert frontdoor.get_transaction_count() == 0

    def test_frontdoor_repr(self):
        """Test string representation."""
        mock_adapter = MockAdapter()
        frontdoor = FrontDoorAccess(mock_adapter)

        repr_str = repr(frontdoor)
        assert "FrontDoorAccess" in repr_str


class TestBackDoorAccess:
    """Test BackDoor (direct memory) access."""

    def test_backdoor_creation_empty(self):
        """Test creating BackDoor with empty memory."""
        backdoor = BackDoorAccess()

        assert backdoor._memory_map == {}
        assert backdoor._read_func is None
        assert backdoor._write_func is None

    def test_backdoor_creation_with_memory_map(self):
        """Test creating BackDoor with initial memory."""
        memory = {0x1000: 0x1234, 0x2000: 0x5678}
        backdoor = BackDoorAccess(memory_map=memory)

        assert backdoor._memory_map == memory

    def test_backdoor_creation_with_functions(self):
        """Test creating BackDoor with read/write functions."""
        read_func = lambda addr: 0xAA
        write_func = lambda addr, val: None

        backdoor = BackDoorAccess(
            memory_map={},
            read_func=read_func,
            write_func=write_func
        )

        assert backdoor._read_func is read_func
        assert backdoor._write_func is write_func

    def test_backdoor_read_from_memory_map(self):
        """Test reading from memory map."""
        memory = {0x1000: 0x1234}
        backdoor = BackDoorAccess(memory_map=memory)

        value = backdoor.read(0x1000)
        assert value == 0x1234

    def test_backdoor_read_missing_address(self):
        """Test reading address not in memory map."""
        backdoor = BackDoorAccess()

        value = backdoor.read(0x1000)
        assert value == 0

    def test_backdoor_read_uses_function(self):
        """Test reading uses custom read function."""
        read_func = lambda addr: 0xABCD if addr == 0x1000 else 0
        backdoor = BackDoorAccess(read_func=read_func)

        value = backdoor.read(0x1000)
        assert value == 0xABCD

    def test_backdoor_write_to_memory_map(self):
        """Test writing to memory map."""
        backdoor = BackDoorAccess()
        backdoor.write(0x2000, 0x5678)

        assert backdoor._memory_map[0x2000] == 0x5678

    def test_backdoor_write_uses_function(self):
        """Test writing uses custom write function."""
        writes = []
        write_func = lambda addr, val: writes.append((addr, val))

        backdoor = BackDoorAccess(write_func=write_func)
        backdoor.write(0x3000, 0x9999)

        assert writes == [(0x3000, 0x9999)]

    def test_backdoor_is_available(self):
        """Test is_available always returns True."""
        backdoor = BackDoorAccess()
        assert backdoor.is_available() is True

    def test_backdoor_set_memory_map(self):
        """Test setting memory map."""
        backdoor = BackDoorAccess()
        memory = {0x1000: 0x1111}

        backdoor.set_memory_map(memory)
        assert backdoor.read(0x1000) == 0x1111

    def test_backdoor_get_memory_map(self):
        """Test getting memory map."""
        memory = {0x1000: 0x2222}
        backdoor = BackDoorAccess(memory_map=memory)

        assert backdoor.get_memory_map() == memory

    def test_backdoor_repr(self):
        """Test string representation."""
        backdoor = BackDoorAccess()
        repr_str = repr(backdoor)
        assert "BackDoorAccess" in repr_str


class TestAccessIntegration:
    """Test integration of access interfaces with adapters."""

    def test_frontdoor_with_axi_adapter(self):
        """Test FrontDoor with AXI adapter."""
        axi = AXIAdapter(base_address=0x40000000)
        mock_driver = MockAXIDriver()
        axi.set_driver(mock_driver)

        frontdoor = FrontDoorAccess(axi)
        value = frontdoor.read(0x40000000)

        # Should calculate offset and call driver
        assert value == 0
        assert mock_driver.last_read_offset == 0

    def test_backdoor_for_simulation(self):
        """Test BackDoor for simulation environment."""
        # Simulation memory
        sim_memory = {}

        def sim_read(addr):
            return sim_memory.get(addr, 0)

        def sim_write(addr, val):
            sim_memory[addr] = val

        backdoor = BackDoorAccess(
            memory_map=sim_memory,
            read_func=sim_read,
            write_func=sim_write
        )

        backdoor.write(0x1000, 0x1234)
        value = backdoor.read(0x1000)

        assert value == 0x1234

    def test_frontdoor_and_backdoor_same_addresses(self):
        """Test that FrontDoor and BackDoor can access same addresses."""
        # FrontDoor: via adapter
        mock_adapter = MockAdapter()
        frontdoor = FrontDoorAccess(mock_adapter)

        # BackDoor: direct memory
        backdoor = BackDoorAccess()
        backdoor.write(0x1000, 0xAAAA)

        # FrontDoor reads from adapter (not backdoor)
        adapter_value = frontdoor.read(0x1000)
        # BackDoor reads from direct memory
        backdoor_value = backdoor.read(0x1000)

        # Values should be different
        assert adapter_value == 0
        assert backdoor_value == 0xAAAA


class TestAccessInterfaceErrorHandling:
    """Test error handling in access interfaces."""

    def test_frontdoor_read_without_adapter(self):
        """Test FrontDoor read when adapter is None."""
        frontdoor = FrontDoorAccess(None)

        with pytest.raises(RuntimeError, match="No adapter configured"):
            frontdoor.read(0x1000)

    def test_frontdoor_write_without_adapter(self):
        """Test FrontDoor write when adapter is None."""
        frontdoor = FrontDoorAccess(None)

        with pytest.raises(RuntimeError, match="No adapter configured"):
            frontdoor.write(0x1000, 0x1234)

    def test_frontdoor_is_available_without_adapter(self):
        """Test FrontDoor is_available when adapter is None."""
        frontdoor = FrontDoorAccess(None)
        assert frontdoor.is_available() is False


# Mock AXI driver for testing
class MockAXIDriver:
    """Mock AXI driver for testing."""

    def __init__(self):
        self.memory = {}
        self.last_read_offset = None
        self.last_write_offset = None
        self.last_write_value = None

    def axi_read(self, offset: int) -> int:
        self.last_read_offset = offset
        return self.memory.get(offset, 0)

    def axi_write(self, offset: int, value: int) -> None:
        self.last_write_offset = offset
        self.last_write_value = value
        self.memory[offset] = value


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
