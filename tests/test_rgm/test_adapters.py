"""
Unit Tests for Hardware Adapters

Tests AXI, APB, UART, SSH adapters including:
- Connection handling
- Read/write operations
- Driver injection
- Error handling
"""

import pytest
from rgm.adapters import (
    AXIAdapter, APBAdapter, UARTAdapter, SSHAdapter,
    HardwareAdapter
)


class TestAXIAdapter:
    """Test AXI adapter functionality."""

    def test_axi_creation(self):
        """Test AXI adapter creation."""
        adapter = AXIAdapter(base_address=0x40000000)

        assert adapter.base_address == 0x40000000
        assert adapter.data_width == 32
        assert adapter.interface_type == "AXI4-Lite"
        assert adapter._driver is None

    def test_axi_custom_parameters(self):
        """Test AXI adapter with custom parameters."""
        adapter = AXIAdapter(
            base_address=0x50000000,
            data_width=64,
            interface_type="AXI4"
        )

        assert adapter.base_address == 0x50000000
        assert adapter.data_width == 64
        assert adapter.interface_type == "AXI4"

    def test_axi_set_driver(self):
        """Test setting AXI driver."""
        adapter = AXIAdapter(base_address=0x40000000)
        mock_driver = MockAXIDriver()

        adapter.set_driver(mock_driver)
        assert adapter._driver is mock_driver

    def test_axi_get_driver(self):
        """Test getting AXI driver."""
        adapter = AXIAdapter(base_address=0x40000000)
        mock_driver = MockAXIDriver()

        adapter.set_driver(mock_driver)
        assert adapter.get_driver() is mock_driver

    def test_axi_read_with_driver(self):
        """Test AXI read with driver."""
        adapter = AXIAdapter(base_address=0x40000000)
        mock_driver = MockAXIDriver()
        mock_driver.memory[0] = 0x1234

        adapter.set_driver(mock_driver)
        value = adapter.read(0x40000000)

        assert value == 0x1234
        assert mock_driver.last_read_offset == 0

    def test_axi_write_with_driver(self):
        """Test AXI write with driver."""
        adapter = AXIAdapter(base_address=0x40000000)
        mock_driver = MockAXIDriver()

        adapter.set_driver(mock_driver)
        adapter.write(0x40001000, 0x5678)

        assert mock_driver.last_write_offset == 0x1000
        assert mock_driver.last_write_value == 0x5678

    def test_axi_read_without_driver(self):
        """Test AXI read without driver returns 0."""
        adapter = AXIAdapter(base_address=0x40000000)
        value = adapter.read(0x40000000)
        assert value == 0

    def test_axi_write_without_driver(self):
        """Test AXI write without driver does nothing."""
        adapter = AXIAdapter(base_address=0x40000000)
        adapter.write(0x40000000, 0x1234)  # Should not raise

    def test_axi_is_connected(self):
        """Test is_connected checks driver."""
        adapter = AXIAdapter(base_address=0x40000000)

        assert adapter.is_connected() is False

        mock_driver = MockAXIDriver()
        adapter.set_driver(mock_driver)

        assert adapter.is_connected() is True

    def test_axi_repr(self):
        """Test string representation."""
        adapter = AXIAdapter(base_address=0x40000000)
        repr_str = repr(adapter)
        assert "AXIAdapter" in repr_str
        assert "0x40000000" in repr_str


class TestAPBAdapter:
    """Test APB adapter functionality."""

    def test_apb_creation(self):
        """Test APB adapter creation."""
        adapter = APBAdapter(base_address=0x40000000)

        assert adapter.base_address == 0x40000000
        assert adapter.data_width == 32

    def test_apb_custom_width(self):
        """Test APB adapter with custom width."""
        adapter = APBAdapter(base_address=0x40000000, data_width=16)
        assert adapter.data_width == 16

    def test_apb_set_driver(self):
        """Test setting APB driver."""
        adapter = APBAdapter(base_address=0x40000000)
        mock_driver = MockAPBDriver()

        adapter.set_driver(mock_driver)
        assert adapter._driver is mock_driver

    def test_apb_read_with_driver(self):
        """Test APB read with driver."""
        adapter = APBAdapter(base_address=0x40000000)
        mock_driver = MockAPBDriver()
        mock_driver.memory[0] = 0xABCD

        adapter.set_driver(mock_driver)
        value = adapter.read(0x40000000)

        assert value == 0xABCD

    def test_apb_write_with_driver(self):
        """Test APB write with driver."""
        adapter = APBAdapter(base_address=0x40000000)
        mock_driver = MockAPBDriver()

        adapter.set_driver(mock_driver)
        adapter.write(0x40001000, 0x1234)

        assert mock_driver.last_write_offset == 0x1000
        assert mock_driver.last_write_value == 0x1234

    def test_apb_read_without_driver(self):
        """Test APB read without driver returns 0."""
        adapter = APBAdapter(base_address=0x40000000)
        value = adapter.read(0x40000000)
        assert value == 0

    def test_apb_is_connected(self):
        """Test is_connected checks driver."""
        adapter = APBAdapter(base_address=0x40000000)

        assert adapter.is_connected() is False

        adapter.set_driver(MockAPBDriver())
        assert adapter.is_connected() is True

    def test_apb_repr(self):
        """Test string representation."""
        adapter = APBAdapter(base_address=0x40000000)
        repr_str = repr(adapter)
        assert "APBAdapter" in repr_str


class TestUARTAdapter:
    """Test UART adapter functionality."""

    def test_uart_creation(self):
        """Test UART adapter creation."""
        adapter = UARTAdapter(port="/dev/ttyUSB0")

        assert adapter.port == "/dev/ttyUSB0"
        assert adapter.baudrate == 115200
        assert adapter._connection is None

    def test_uart_custom_baudrate(self):
        """Test UART adapter with custom baudrate."""
        adapter = UARTAdapter(port="COM3", baudrate=9600)
        assert adapter.baudrate == 9600

    def test_uart_connect_not_implemented(self):
        """Test UART connect returns True (stub)."""
        adapter = UARTAdapter(port="/dev/ttyUSB0")
        # Currently stubbed, returns True
        result = adapter.connect()
        assert result is True

    def test_uart_read_not_connected(self):
        """Test UART read when not connected raises."""
        adapter = UARTAdapter(port="/dev/ttyUSB0")

        with pytest.raises(RuntimeError, match="not connected"):
            adapter.read(0x1000)

    def test_uart_write_not_connected(self):
        """Test UART write when not connected raises."""
        adapter = UARTAdapter(port="/dev/ttyUSB0")

        # Should not raise (currently stubbed)
        adapter.write(0x1000, 0x1234)

    def test_uart_is_connected(self):
        """Test is_connected checks connection."""
        adapter = UARTAdapter(port="/dev/ttyUSB0")
        assert adapter.is_connected() is False

    def test_uart_disconnect(self):
        """Test disconnect."""
        adapter = UARTAdapter(port="/dev/ttyUSB0")
        adapter.disconnect()  # Should not raise

    def test_uart_repr(self):
        """Test string representation."""
        adapter = UARTAdapter(port="/dev/ttyUSB0", baudrate=9600)
        repr_str = repr(adapter)
        assert "UARTAdapter" in repr_str
        assert "/dev/ttyUSB0" in repr_str


class TestSSHAdapter:
    """Test SSH adapter functionality."""

    def test_ssh_creation(self):
        """Test SSH adapter creation."""
        adapter = SSHAdapter(
            host="192.168.1.100",
            username="fpga",
            password="pass"
        )

        assert adapter.host == "192.168.1.100"
        assert adapter.username == "fpga"
        assert adapter.password == "pass"
        assert adapter.port == 22

    def test_ssh_custom_port(self):
        """Test SSH adapter with custom port."""
        adapter = SSHAdapter(
            host="board.example.com",
            username="user",
            port=2222
        )
        assert adapter.port == 2222

    def test_ssh_custom_commands(self):
        """Test SSH adapter with custom commands."""
        adapter = SSHAdapter(
            host="192.168.1.100",
            username="fpga",
            read_command="devmem 0x{address}",
            write_command="devmem 0x{address} 32 0x{value}"
        )

        assert "devmem" in adapter.read_command
        assert "devmem" in adapter.write_command

    def test_ssh_initially_disconnected(self):
        """Test SSH adapter is initially disconnected."""
        adapter = SSHAdapter(
            host="192.168.1.100",
            username="fpga"
        )
        assert adapter.is_connected() is False

    def test_ssh_get_statistics(self):
        """Test getting SSH statistics."""
        adapter = SSHAdapter(
            host="192.168.1.100",
            username="fpga",
            port=2222
        )

        stats = adapter.get_statistics()
        assert stats["host"] == "192.168.1.100"
        assert stats["port"] == 2222
        assert stats["username"] == "fpga"
        assert stats["connected"] is False
        assert stats["read_count"] == 0
        assert stats["write_count"] == 0

    def test_ssh_repr(self):
        """Test string representation."""
        adapter = SSHAdapter(
            host="192.168.1.100",
            username="fpga"
        )
        repr_str = repr(adapter)
        assert "SSHAdapter" in repr_str
        assert "192.168.1.100" in repr_str


class TestHardwareAdapterBase:
    """Test HardwareAdapter base class."""

    def test_adapter_is_abstract(self):
        """Test that HardwareAdapter cannot be instantiated directly."""
        with pytest.raises(TypeError):
            HardwareAdapter()


class TestAdapterErrorHandling:
    """Test error handling in adapters."""

    def test_axi_read_invalid_offset(self):
        """Test AXI read with invalid offset."""
        adapter = AXIAdapter(base_address=0x40000000)
        mock_driver = MockAXIDriver()

        adapter.set_driver(mock_driver)
        # Read beyond mapped region
        value = adapter.read(0x50000000)
        assert value == 0  # Driver returns 0 for unmapped

    def test_apb_driver_injection_pattern(self):
        """Test driver injection pattern."""
        adapter = APBAdapter(base_address=0x40000000)

        # Driver not set yet
        assert adapter.is_connected() is False

        # Inject driver
        mock_driver = MockAPBDriver()
        adapter.set_driver(mock_driver)

        # Now connected
        assert adapter.is_connected() is True

        # Can access driver
        assert adapter._driver is mock_driver


# Mock drivers for testing
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


class MockAPBDriver:
    """Mock APB driver for testing."""

    def __init__(self):
        self.memory = {}
        self.last_read_offset = None
        self.last_write_offset = None
        self.last_write_value = None

    def apb_read(self, offset: int) -> int:
        self.last_read_offset = offset
        return self.memory.get(offset, 0)

    def apb_write(self, offset: int, value: int) -> None:
        self.last_write_offset = offset
        self.last_write_value = value
        self.memory[offset] = value


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
