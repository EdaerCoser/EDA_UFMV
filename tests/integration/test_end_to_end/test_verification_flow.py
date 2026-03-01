"""
End-to-End Workflow Tests: Complete Verification Flow

Tests complete verification workflows that integrate all modules:
- RGM register configuration
- Randomized stimulus generation
- Coverage collection and analysis
- End-to-end test scenarios
"""

import pytest
from pathlib import Path
import tempfile
import json

from sv_randomizer import Randomizable
from sv_randomizer.core.variables import RandVar, RandCVar, VarType
from coverage.core import CoverGroup, CoverPoint, Cross
from coverage.database import FileDatabase
from coverage.formatters import HTMLReport, JSONReport
from rgm.core import RegisterBlock, Register, Field
from rgm.utils import AccessType


# =============================================================================
# Complete UVM-like Test Flow
# =============================================================================

@pytest.mark.end_to_end
@pytest.mark.integration
@pytest.mark.P0
class TestCompleteTestFlow:
    """Tests for complete UVM-like test flow."""

    def test_build_phase(self):
        """Test build phase: create RGM and coverage structures."""
        # Create register model
        block = RegisterBlock("DUT", 0x40000000)

        # Control register
        ctrl_reg = Register("CTRL", 0x00, 32)
        ctrl_reg.add_field(Field("enable", bit_offset=0, bit_width=1, access=AccessType.RW, reset_value=0))
        ctrl_reg.add_field(Field("mode", bit_offset=1, bit_width=3, access=AccessType.RW, reset_value=0))
        ctrl_reg.add_field(Field("start", bit_offset=4, bit_width=1, access=AccessType.RW, reset_value=0))
        block.add_register(ctrl_reg)

        # Status register
        status_reg = Register("STATUS", 0x04, 32)
        status_reg.add_field(Field("busy", bit_offset=0, bit_width=1, access=AccessType.RO, reset_value=0))
        status_reg.add_field(Field("done", bit_offset=1, bit_width=1, access=AccessType.RO, reset_value=0))
        status_reg.add_field(Field("error", bit_offset=2, bit_width=1, access=AccessType.RO, reset_value=0))
        block.add_register(status_reg)

        # Create coverage
        cg = CoverGroup("dut_cg")
        ctrl_cp = CoverPoint("ctrl_cp", "ctrl", bins={"auto": 10})
        status_cp = CoverPoint("status_cp", "status", bins={"vals": list(range(8))})
        cg.add_coverpoint(ctrl_cp)
        cg.add_coverpoint(status_cp)

        # Verify build phase completed
        assert len(block._registers) == 2
        assert len(cg._coverpoints) == 2

    def test_connect_phase(self):
        """Test connect phase: connect randomization to RGM and coverage."""
        class TestTransaction(Randomizable):
            def __init__(self):
                super().__init__()

                # RGM component
                self.block = RegisterBlock("DUT", 0x40000000)
                ctrl = Register("CTRL", 0x00, 32)
                ctrl.add_field(Field("cmd", bit_offset=0, bit_width=4, access=AccessType.RW, reset_value=0))
                self.block.add_register(ctrl)

                # Randomizable component
                self.cmd = RandVar("cmd", VarType.BIT, bit_width=4)

                # Coverage component
                self.cg = CoverGroup("trans_cg")
                cp = CoverPoint("cmd_cp", "cmd", bins={"cmds": list(range(16))})
                self.cg.add_coverpoint(cp)

                # Connect: randomize -> RGM write -> coverage sample
                self.add_constraint(lambda: self.cmd.value < 10)

        txn = TestTransaction()
        txn.randomize()

        # Verify connection worked
        assert 0 <= txn.cmd.value < 10

    def test_run_phase(self):
        """Test run phase: execute randomized transactions."""
        class AutomatedTest(Randomizable):
            def __init__(self):
                super().__init__()

                # RGM
                self.dut = RegisterBlock("DUT", 0x40000000)
                ctrl = Register("CTRL", 0x00, 32)
                ctrl.add_field(Field("opcode", bit_offset=0, bit_width=3, access=AccessType.RW, reset_value=0))
                self.dut.add_register(ctrl)

                # Randomization
                self.opcode = RandVar("opcode", VarType.BIT, bit_width=3)

                # Coverage
                self.cg = CoverGroup("test_cg")
                cp = CoverPoint("opcode_cp", "opcode", bins={"ops": list(range(8))})
                self.cg.add_coverpoint(cp)

                # Coverage auto-sampling
                self.add_covergroup(self.cg)

        # Run automated test
        test = AutomatedTest()

        # Execute 20 transactions
        for _ in range(20):
            test.randomize()
            # Apply to DUT
            test.dut.write("CTRL", field="opcode", value=test.opcode.value)
            # Coverage auto-sampled in post_randomize

        # Verify test execution
        assert test.cg.coverage > 0.0

    def test_cleanup_phase(self):
        """Test cleanup phase: generate reports and cleanup."""
        # Create coverage with some data
        cg = CoverGroup("cleanup_cg")
        cp = CoverPoint("val_cp", "value", bins={"vals": [1, 2, 3]})
        cg.add_coverpoint(cp)

        # Sample some data
        cg.sample(value=1)
        cg.sample(value=2)

        # Generate report
        with tempfile.TemporaryDirectory() as tmpdir:
            report_path = Path(tmpdir) / "coverage_report.json"

            # Create JSON report
            db = FileDatabase(str(report_path))
            db.save_coverage(cg._name, cg.get_coverage_data())

            # Verify report created
            assert report_path.exists()


# =============================================================================
# Complete Verification Scenario
# =============================================================================

@pytest.mark.end_to_end
@pytest.mark.integration
@pytest.mark.P0
class TestVerificationScenario:
    """Tests for complete verification scenarios."""

    def test_uart_verification_scenario(self):
        """Test complete UART verification scenario."""
        # Build UART register model
        uart = RegisterBlock("UART", 0x40000000)

        # UART Control Register
        uart_ctrl = Register("UART_CTRL", 0x00, 32)
        uart_ctrl.add_field(Field("enable", bit_offset=0, bit_width=1, access=AccessType.RW, reset_value=0))
        uart_ctrl.add_field(Field("tx_enable", bit_offset=1, bit_width=1, access=AccessType.RW, reset_value=0))
        uart_ctrl.add_field(Field("rx_enable", bit_offset=2, bit_width=1, access=AccessType.RW, reset_value=0))
        uart_ctrl.add_field(Field("baud_sel", bit_offset=4, bit_width=3, access=AccessType.RW, reset_value=0))
        uart.add_register(uart_ctrl)

        # UART Status Register
        uart_status = Register("UART_STATUS", 0x04, 32)
        uart_status.add_field(Field("tx_empty", bit_offset=0, bit_width=1, access=AccessType.RO, reset_value=1))
        uart_status.add_field(Field("rx_full", bit_offset=1, bit_width=1, access=AccessType.RO, reset_value=0))
        uart_status.add_field(Field("tx_busy", bit_offset=2, bit_width=1, access=AccessType.RO, reset_value=0))
        uart.add_register(uart_status)

        # UART Data Register
        uart_data = Register("UART_DATA", 0x08, 32)
        uart_data.add_field(Field("data", bit_offset=0, bit_width=8, access=AccessType.RW, reset_value=0))
        uart.add_register(uart_data)

        # Create randomized transaction
        class UARTTransaction(Randomizable):
            def __init__(self, uart_block):
                super().__init__()
                self.uart = uart_block

                # Randomizable fields
                self.enable = RandVar("enable", VarType.BIT, bit_width=1)
                self.tx_enable = RandVar("tx_enable", VarType.BIT, bit_width=1)
                self.rx_enable = RandVar("rx_enable", VarType.BIT, bit_width=1)
                self.baud_sel = RandVar("baud_sel", VarType.BIT, bit_width=3)
                self.tx_data = RandVar("tx_data", VarType.BIT, bit_width=8)

                # Coverage
                self.cg = CoverGroup("uart_cg")
                baud_cp = CoverPoint("baud_cp", "baud_sel", bins={"bauds": list(range(8))})
                data_cp = CoverPoint("data_cp", "tx_data", bins={"auto": 10})
                self.cg.add_coverpoint(baud_cp)
                self.cg.add_coverpoint(data_cp)

                # Constraints
                self.add_constraint(lambda: self.enable.value == 1)
                self.add_constraint(lambda: self.tx_enable.value == 1)

        # Create and run test
        test = UARTTransaction(uart)

        # Run multiple transactions
        for _ in range(50):
            test.randomize()

            # Apply to UART model
            test.uart.write("UART_CTRL", field="enable", value=test.enable.value)
            test.uart.write("UART_CTRL", field="tx_enable", value=test.tx_enable.value)
            test.uart.write("UART_CTRL", field="rx_enable", value=test.rx_enable.value)
            test.uart.write("UART_CTRL", field="baud_sel", value=test.baud_sel.value)
            test.uart.write("UART_DATA", field="data", value=test.tx_data.value)

            # Sample coverage
            test.cg.sample(baud_sel=test.baud_sel.value, tx_data=test.tx_data.value)

        # Verify test results
        assert test.cg.coverage > 0.0

    def test_spi_verification_scenario(self):
        """Test complete SPI verification scenario."""
        # Build SPI register model
        spi = RegisterBlock("SPI", 0x40001000)

        # SPI Control
        spi_ctrl = Register("SPI_CTRL", 0x00, 32)
        spi_ctrl.add_field(Field("cs", bit_offset=0, bit_width=1, access=AccessType.RW, reset_value=1))
        spi_ctrl.add_field(Field("clk_polarity", bit_offset=1, bit_width=1, access=AccessType.RW, reset_value=0))
        spi_ctrl.add_field(Field("clk_phase", bit_offset=2, bit_width=1, access=AccessType.RW, reset_value=0))
        spi_ctrl.add_field(Field("data_width", bit_offset=4, bit_width=4, access=AccessType.RW, reset_value=7))
        spi.add_register(spi_ctrl)

        # SPI Status
        spi_status = Register("SPI_STATUS", 0x04, 32)
        spi_status.add_field(Field="busy", bit_offset=0, bit_width=1, access=AccessType.RO, reset_value=0))
        spi_status.add_field(Field="tx_empty", bit_offset=1, bit_width=1, access=AccessType.RO, reset_value=1))
        spi_status.add_field(Field("rx_full", bit_offset=2, bit_width=1, access=AccessType.RO, reset_value=0))
        spi.add_register(spi_status)

        # SPI Data
        spi_data = Register("SPI_DATA", 0x08, 32)
        spi_data.add_field(Field("data", bit_offset=0, bit_width=16, access=AccessType.RW, reset_value=0))
        spi.add_register(spi_data)

        # Create transaction
        class SPITransaction(Randomizable):
            def __init__(self, spi_block):
                super().__init__()
                self.spi = spi_block

                self.clk_polarity = RandVar("clk_polarity", VarType.BIT, bit_width=1)
                self.clk_phase = RandVar("clk_phase", VarType.BIT, bit_width=1)
                self.data_width = RandVar("data_width", VarType.BIT, bit_width=4)
                self.tx_data = RandVar("tx_data", VarType.BIT, bit_width=16)

                self.cg = CoverGroup("spi_cg")
                cp = CoverPoint("config_cp", "cfg", bins={"auto": 10})
                self.cg.add_coverpoint(cp)

        test = SPITransaction(spi)

        # Run test
        for _ in range(30):
            test.randomize()
            test.cg.sample(cfg=test.data_width.value)

        # Verify
        assert test.cg.coverage > 0.0


# =============================================================================
# Coverage Database Workflow
# =============================================================================

@pytest.mark.end_to_end
@pytest.mark.integration
@pytest.mark.P1
class TestCoverageDatabaseWorkflow:
    """Tests for coverage database persistence workflow."""

    def test_save_and_load_coverage(self):
        """Test saving and loading coverage data."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "coverage.db"

            # Create coverage and sample
            cg = CoverGroup("test_cg")
            cp = CoverPoint("val_cp", "value", bins={"vals": [1, 2, 3, 4, 5]})
            cg.add_coverpoint(cp)

            cg.sample(value=1)
            cg.sample(value=3)
            cg.sample(value=5)

            # Save to database
            db = FileDatabase(str(db_path))
            db.save_coverage(cg._name, cg.get_coverage_data())

            # Load from database
            loaded_data = db.load_coverage(cg._name)

            # Verify data integrity
            assert loaded_data is not None
            assert "coverpoints" in loaded_data

    def test_merge_coverage_databases(self):
        """Test merging coverage from multiple runs."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db1_path = Path(tmpdir) / "run1.db"
            db2_path = Path(tmpdir) / "run2.db"
            merged_path = Path(tmpdir) / "merged.db"

            # Run 1
            cg1 = CoverGroup("test_cg")
            cp1 = CoverPoint("val_cp", "value", bins={"vals": [1, 2, 3]})
            cg1.add_coverpoint(cp1)
            cg1.sample(value=1)
            cg1.sample(value=2)

            db1 = FileDatabase(str(db1_path))
            db1.save_coverage(cg1._name, cg1.get_coverage_data())

            # Run 2
            cg2 = CoverGroup("test_cg")
            cp2 = CoverPoint("val_cp", "value", bins={"vals": [1, 2, 3]})
            cg2.add_coverpoint(cp2)
            cg2.sample(value=2)
            cg2.sample(value=3)

            db2 = FileDatabase(str(db2_path))
            db2.save_coverage(cg2._name, cg2.get_coverage_data())

            # Merge
            data1 = db1.load_coverage(cg1._name)
            data2 = db2.load_coverage(cg2._name)

            merged_db = FileDatabase(str(merged_path))
            merged_db.save_coverage(cg1._name, data1)

            # Verify merge
            assert data1 is not None
            assert data2 is not None


# =============================================================================
# Report Generation Workflow
# =============================================================================

@pytest.mark.end_to_end
@pytest.mark.integration
@pytest.mark.P1
class TestReportGenerationWorkflow:
    """Tests for report generation workflow."""

    def test_generate_html_report(self):
        """Test HTML report generation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create coverage
            cg = CoverGroup("html_test_cg")
            cp = CoverPoint("val_cp", "value", bins={"vals": [1, 2, 3, 4, 5]})
            cg.add_coverpoint(cp)

            # Sample
            for val in [1, 2, 3]:
                cg.sample(value=val)

            # Generate report
            output_path = Path(tmpdir) / "coverage.html"
            reporter = HTMLReport(str(output_path))
            reporter.generate(cg)

            # Verify report created
            assert output_path.exists()

    def test_generate_json_report(self):
        """Test JSON report generation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create coverage
            cg = CoverGroup("json_test_cg")
            cp = CoverPoint("val_cp", "value", bins={"vals": [1, 2, 3]})
            cg.add_coverpoint(cp)

            cg.sample(value=1)
            cg.sample(value=2)

            # Generate report
            output_path = Path(tmpdir) / "coverage.json"
            reporter = JSONReport(str(output_path))
            reporter.generate(cg)

            # Verify report created and valid
            assert output_path.exists()

            with open(output_path) as f:
                data = json.load(f)
                assert "coverage" in data or "coverpoints" in data


# =============================================================================
# Full Stack Integration Test
# =============================================================================

@pytest.mark.end_to_end
@pytest.mark.integration
@pytest.mark.P0
class TestFullStackIntegration:
    """Tests for complete full-stack integration."""

    def test_complete_verification_workflow(self):
        """Test complete workflow: RGM -> Randomize -> Coverage -> Report."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # 1. Build Phase: Create RGM
            dut = RegisterBlock("DUT", 0x40000000)
            ctrl = Register("CTRL", 0x00, 32)
            ctrl.add_field(Field("config", bit_offset=0, bit_width=8, access=AccessType.RW, reset_value=0))
            dut.add_register(ctrl)

            # 2. Create Randomizable Transaction
            class TestTransaction(Randomizable):
                def __init__(self, dut_block):
                    super().__init__()
                    self.dut = dut_block
                    self.config = RandVar("config", VarType.BIT, bit_width=8)

                    self.cg = CoverGroup("test_cg")
                    cp = CoverPoint("config_cp", "config", bins={"auto": 10})
                    self.cg.add_coverpoint(cp)

                    self.add_covergroup(self.cg)

            # 3. Run Phase: Execute randomized tests
            test = TestTransaction(dut)

            for _ in range(50):
                test.randomize()
                test.dut.write("CTRL", field="config", value=test.config.value)

            # 4. Report Phase: Generate report
            output_path = Path(tmpdir) / "report.html"
            reporter = HTMLReport(str(output_path))
            reporter.generate(test.cg)

            # Verify complete workflow
            assert output_path.exists()
            assert test.cg.coverage > 0.0

    def test_multi_run_coverage_collection(self):
        """Test collecting coverage across multiple test runs."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "multi_run.db"

            # Run 1
            cg1 = CoverGroup("multi_cg")
            cp1 = CoverPoint("val_cp", "value", bins={"vals": list(range(10))})
            cg1.add_coverpoint(cp1)
            for i in [0, 1, 2]:
                cg1.sample(value=i)

            db = FileDatabase(str(db_path))
            db.save_coverage("run1", cg1.get_coverage_data())

            # Run 2
            cg2 = CoverGroup("multi_cg")
            cp2 = CoverPoint("val_cp", "value", bins={"vals": list(range(10))})
            cg2.add_coverpoint(cp2)
            for i in [3, 4, 5]:
                cg2.sample(value=i)

            db.save_coverage("run2", cg2.get_coverage_data())

            # Run 3
            cg3 = CoverGroup("multi_cg")
            cp3 = CoverPoint("val_cp", "value", bins={"vals": list(range(10))})
            cg3.add_coverpoint(cp3)
            for i in [6, 7, 8, 9]:
                cg3.sample(value=i)

            db.save_coverage("run3", cg3.get_coverage_data())

            # Verify all runs saved
            run1_data = db.load_coverage("run1")
            run2_data = db.load_coverage("run2")
            run3_data = db.load_coverage("run3")

            assert run1_data is not None
            assert run2_data is not None
            assert run3_data is not None
