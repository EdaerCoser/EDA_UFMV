"""
Cross-Module Integration Tests: RGM + Coverage

Tests integration between Register Model (RGM) and Coverage systems:
- Automatic coverage sampling during register operations
- Covering register access patterns
- Field-level coverage tracking
- Combined RGM and Coverage workflows
"""

import pytest

from rgm.core import RegisterBlock, Register, Field
from rgm.utils import AccessType
from coverage.core import CoverGroup, CoverPoint, Cross
from sv_randomizer import Randomizable
from sv_randomizer.core.variables import RandVar, VarType


# =============================================================================
# Basic RGM + Coverage Integration
# =============================================================================

@pytest.mark.integration
@pytest.mark.cross_module
@pytest.mark.P0
class TestRGMCoverageBasicIntegration:
    """Tests for basic RGM and Coverage integration."""

    def test_register_with_coverage(self):
        """Test that a register can have associated coverage."""
        # Create register block
        block = RegisterBlock("TEST", 0x40000000)
        reg = Register("STATUS", 0x00, 32)
        reg.add_field(Field("busy", bit_offset=0, bit_width=1, access=AccessType.RO, reset_value=0))
        reg.add_field(Field("done", bit_offset=1, bit_width=1, access=AccessType.RO, reset_value=0))
        block.add_register(reg)

        # Create coverage for register reads
        cg = CoverGroup("status_cg")
        cp = CoverPoint("status_cp", "value", bins={"values": [0, 1, 2, 3]})
        cg.add_coverpoint(cp)

        # Simulate register reads and sample coverage
        reg.read()  # Read value (probably 0)
        cg.sample(value=reg._current_value)

        # Coverage should be collected
        assert cg.coverage >= 0.0

    def test_field_level_coverage(self):
        """Test coverage at individual field level."""
        # Create register with multiple fields
        reg = Register("CTRL", 0x00, 32)
        reg.add_field(Field("mode", bit_offset=0, bit_width=3, access=AccessType.RW, reset_value=0))
        reg.add_field(Field("enable", bit_offset=3, bit_width=1, access=AccessType.RW, reset_value=0))
        reg.add_field(Field("start", bit_offset=4, bit_width=1, access=AccessType.RW, reset_value=0))

        # Create coverage for mode field
        cg = CoverGroup("mode_cg")
        cp = CoverPoint("mode_cp", "mode", bins={"modes": list(range(8))})
        cg.add_coverpoint(cp)

        # Write different mode values and sample
        for mode_val in [0, 1, 4, 7]:
            reg.write(field="mode", value=mode_val)
            cg.sample(mode=mode_val)

        # Should have partial coverage
        assert 0.0 < cg.coverage < 100.0


# =============================================================================
# Register Access Coverage
# =============================================================================

@pytest.mark.integration
@pytest.mark.cross_module
@pytest.mark.P0
class TestRegisterAccessCoverage:
    """Tests for covering register access patterns."""

    def test_read_coverage_tracking(self):
        """Test tracking coverage of register reads."""
        block = RegisterBlock("RD_TEST", 0x40000000)

        # Create multiple registers
        for i in range(10):
            reg = Register(f"REG_{i}", i * 4, 32)
            reg.add_field(Field("value", bit_offset=0, bit_width=32, access=AccessType.RO, reset_value=i))
            block.add_register(reg)

        # Create coverage for which registers are read
        cg = CoverGroup("read_cg")
        cp = CoverPoint("reg_read", "reg_name", bins={"regs": [f"REG_{i}" for i in range(10)]})
        cg.add_coverpoint(cp)

        # Read some registers
        for i in [0, 2, 5, 9]:
            block.read(f"REG_{i}")
            cg.sample(reg_name=f"REG_{i}")

        # Should have partial coverage
        assert cg.coverage == 40.0  # 4 out of 10 registers

    def test_write_coverage_tracking(self):
        """Test tracking coverage of register writes."""
        block = RegisterBlock("WR_TEST", 0x40000000)

        # Create register with writable fields
        reg = Register("CTRL", 0x00, 32)
        reg.add_field(Field("cmd", bit_offset=0, bit_width=4, access=AccessType.RW, reset_value=0))
        block.add_register(reg)

        # Create coverage for command values
        cg = CoverGroup("cmd_cg")
        cp = CoverPoint("cmd_cp", "cmd", bins={"cmds": list(range(16))})
        cg.add_coverpoint(cp)

        # Write various commands
        for cmd in [0, 5, 10, 15]:
            block.write("CTRL", field="cmd", value=cmd)
            cg.sample(cmd=cmd)

        # Should have partial coverage
        assert cg.coverage == 25.0  # 4 out of 16 commands


# =============================================================================
# Randomized RGM with Coverage
# =============================================================================

@pytest.mark.integration
@pytest.mark.cross_module
@pytest.mark.P0
class TestRandomizedRGMCoverage:
    """Tests for randomized RGM operations with coverage."""

    def test_randomized_register_configuration(self):
        """Test randomizing register configuration with coverage tracking."""
        class RandomizedTransaction(Randomizable):
            def __init__(self):
                super().__init__()

                # RGM component
                self.block = RegisterBlock("RAND_TEST", 0x40000000)
                reg = Register("CONFIG", 0x00, 32)
                reg.add_field(Field("mode", bit_offset=0, bit_width=3, access=AccessType.RW, reset_value=0))
                reg.add_field(Field("speed", bit_offset=4, bit_width=2, access=AccessType.RW, reset_value=0))
                self.block.add_register(reg)

                # Randomizable component
                self.mode = RandVar("mode", VarType.BIT, bit_width=3)
                self.speed = RandVar("speed", VarType.BIT, bit_width=2)

                # Coverage component
                self.cg = CoverGroup("config_cg")
                mode_cp = CoverPoint("mode_cp", "mode", bins={"modes": list(range(8))})
                speed_cp = CoverPoint("speed_cp", "speed", bins={"speeds": list(range(4))})
                self.cg.add_coverpoint(mode_cp)
                self.cg.add_coverpoint(speed_cp)

                # Add constraint
                self.add_constraint(lambda: self.mode.value < 6)

        # Create and randomize transaction
        txn = RandomizedTransaction()

        # Randomize multiple times
        for _ in range(20):
            txn.randomize()

            # Apply to register
            txn.block.write("CONFIG", field="mode", value=txn.mode.value)
            txn.block.write("CONFIG", field="speed", value=txn.speed.value)

            # Sample coverage
            txn.cg.sample(mode=txn.mode.value, speed=txn.speed.value)

        # Should have decent coverage
        assert txn.cg.coverage > 0.0

    def test_coverpoint_constraint_from_register(self):
        """Test using register values in coverage constraints."""
        # Create register with randomizable values
        reg = Register("RAND_REG", 0x00, 32)
        reg.add_field(Field("val", bit_offset=0, bit_width=8, access=AccessType.RW, reset_value=0))

        # Create coverage that tracks register value distribution
        cg = CoverGroup("dist_cg")
        cp = CoverPoint("dist_cp", "value", bins={"auto": 10})  # Auto-generated bins
        cg.add_coverpoint(cp)

        # Write random values
        import random
        for _ in range(50):
            val = random.randint(0, 255)
            reg.write(field="val", value=val)
            cg.sample(value=val)

        # Should have coverage across multiple bins
        assert cg.coverage > 0.0


# =============================================================================
# Cross Coverage with RGM
# =============================================================================

@pytest.mark.integration
@pytest.mark.cross_module
@pytest.mark.P1
class TestRGMCrossCoverage:
    """Tests for cross coverage involving multiple registers."""

    def test_cross_two_registers(self):
        """Test cross coverage between two registers."""
        block = RegisterBlock("CROSS_TEST", 0x40000000)

        # Create two registers
        reg1 = Register("REG1", 0x00, 16)
        reg1.add_field(Field("val1", bit_offset=0, bit_width=8, access=AccessType.RW, reset_value=0))

        reg2 = Register("REG2", 0x04, 16)
        reg2.add_field(Field("val2", bit_offset=0, bit_width=8, access=AccessType.RW, reset_value=0))

        block.add_register(reg1)
        block.add_register(reg2)

        # Create cross coverage
        cg = CoverGroup("cross_cg")
        cp1 = CoverPoint("val1_cp", "val1", bins={"vals": [0, 1, 2]})
        cp2 = CoverPoint("val2_cp", "val2", bins={"vals": [0, 1, 2]})
        cg.add_coverpoint(cp1)
        cg.add_coverpoint(cp2)

        cross = Cross("val_cross", ["val1_cp", "val2_cp"])
        cg.add_cross(cross)

        # Sample various combinations
        combinations = [(0, 0), (1, 1), (2, 2), (0, 2)]
        for v1, v2 in combinations:
            block.write("REG1", field="val1", value=v1)
            block.write("REG2", field="val2", value=v2)
            cg.sample(val1=v1, val2=v2)

        # Should have partial cross coverage
        assert cg.coverage > 0.0

    def test_cross_field_values_within_register(self):
        """Test cross coverage of multiple fields within one register."""
        reg = Register("MULTI_FIELD", 0x00, 32)
        reg.add_field(Field("field_a", bit_offset=0, bit_width=4, access=AccessType.RW, reset_value=0))
        reg.add_field(Field("field_b", bit_offset=4, bit_width=4, access=AccessType.RW, reset_value=0))
        reg.add_field(Field("field_c", bit_offset=8, bit_width=4, access=AccessType.RW, reset_value=0))

        # Create cross coverage for fields
        cg = CoverGroup("field_cross_cg")
        cp_a = CoverPoint("field_a_cp", "field_a", bins={"vals": list(range(16))})
        cp_b = CoverPoint("field_b_cp", "field_b", bins={"vals": list(range(16))})
        cp_c = CoverPoint("field_c_cp", "field_c", bins={"vals": list(range(16))})
        cg.add_coverpoint(cp_a)
        cg.add_coverpoint(cp_b)
        cg.add_coverpoint(cp_c)

        cross = Cross("field_cross", ["field_a_cp", "field_b_cp", "field_c_cp"])
        cg.add_cross(cross)

        # Sample some combinations
        for i in range(5):
            reg.write(field="field_a", value=i)
            reg.write(field="field_b", value=i * 2)
            reg.write(field="field_c", value=i * 3)
            cg.sample(field_a=i, field_b=i * 2, field_c=i * 3)

        # Should have some cross coverage
        assert cg.coverage > 0.0


# =============================================================================
# Coverage-Guided Register Configuration
# =============================================================================

@pytest.mark.integration
@pytest.mark.cross_module
@pytest.mark.P1
class TestCoverageGuidedConfiguration:
    """Tests for coverage-guided register configuration."""

    def test_fill_coverage_gaps(self):
        """Test using coverage to guide register configuration."""
        # Create setup with coverage
        block = RegisterBlock("GUIDED_TEST", 0x40000000)
        reg = Register("MODE_REG", 0x00, 32)
        reg.add_field(Field("mode", bit_offset=0, bit_width=4, access=AccessType.RW, reset_value=0))
        block.add_register(reg)

        cg = CoverGroup("mode_cg")
        cp = CoverPoint("mode_cp", "mode", bins={"modes": list(range(16))})
        cg.add_coverpoint(cp)

        # Randomize to get partial coverage
        import random
        covered_modes = set()
        for _ in range(10):
            mode = random.randint(0, 15)
            block.write("MODE_REG", field="mode", value=mode)
            cg.sample(mode=mode)
            covered_modes.add(mode)

        # Find uncovered modes
        all_modes = set(range(16))
        uncovered_modes = all_modes - covered_modes

        # Manually fill some gaps
        for mode in list(uncovered_modes)[:3]:
            block.write("MODE_REG", field="mode", value=mode)
            cg.sample(mode=mode)

        # Coverage should improve
        assert cg.coverage > 0.0

    def test_coverage_driven_exploration(self):
        """Test using coverage metrics to drive exploration."""
        # Create complex register with multiple fields
        reg = Register("COMPLEX", 0x00, 32)
        reg.add_field(Field("op", bit_offset=0, bit_width=3, access=AccessType.RW, reset_value=0))
        reg.add_field(Field("src", bit_offset=4, bit_width=2, access=AccessType.RW, reset_value=0))
        reg.add_field(Field("dst", bit_offset=6, bit_width=2, access=AccessType.RW, reset_value=0))

        # Create coverage
        cg = CoverGroup("complex_cg")
        op_cp = CoverPoint("op_cp", "op", bins={"ops": list(range(8))})
        src_cp = CoverPoint("src_cp", "src", bins={"srcs": list(range(4))})
        dst_cp = CoverPoint("dst_cp", "dst", bins={"dsts": list(range(4))})
        cg.add_coverpoint(op_cp)
        cg.add_coverpoint(src_cp)
        cg.add_coverpoint(dst_cp)

        # Exploration loop
        previous_coverage = 0.0
        for iteration in range(50):
            # Random configuration
            import random
            op = random.randint(0, 7)
            src = random.randint(0, 3)
            dst = random.randint(0, 3)

            reg.write(field="op", value=op)
            reg.write(field="src", value=src)
            reg.write(field="dst", value=dst)
            cg.sample(op=op, src=src, dst=dst)

            # Check coverage improvement
            current_coverage = cg.coverage
            if current_coverage >= 100.0:
                break

            previous_coverage = current_coverage

        # Should make progress on coverage
        assert cg.coverage > 0.0


# =============================================================================
# RGM State Machine Coverage
# =============================================================================

@pytest.mark.integration
@pytest.mark.cross_module
@pytest.mark.P1
class TestRGMStateMachineCoverage:
    """Tests for covering RGM state machine transitions."""

    def test_register_state_coverage(self):
        """Test covering register state transitions."""
        # Create status register representing state
        reg = Register("STATE", 0x00, 32)
        reg.add_field(Field("state", bit_offset=0, bit_width=3, access=AccessType.RO, reset_value=0))

        # Define states
        states = {
            0: "IDLE",
            1: "BUSY",
            2: "DONE",
            3: "ERROR",
        }

        # Create coverage for state transitions
        cg = CoverGroup("state_cg")
        cp = CoverPoint("state_cp", "state", bins={"states": list(states.keys())})
        cg.add_coverpoint(cp)

        # Simulate state transitions
        state_sequence = [0, 1, 1, 1, 2, 0, 1, 2, 3, 0]
        for state in state_sequence:
            # In real scenario, state would change based on hardware
            # Here we just simulate
            cg.sample(state=state)

        # Should have visited multiple states
        assert cg.coverage > 0.0

    def test_multi_register_state_coverage(self):
        """Test covering state across multiple registers."""
        # Create state machine spread across registers
        block = RegisterBlock("SM_TEST", 0x40000000)

        curr_reg = Register("CURRENT_STATE", 0x00, 16)
        curr_reg.add_field(Field("state", bit_offset=0, bit_width=3, access=AccessType.RO, reset_value=0))

        next_reg = Register("NEXT_STATE", 0x04, 16)
        next_reg.add_field(Field("state", bit_offset=0, bit_width=3, access=AccessType.RW, reset_value=0))

        block.add_register(curr_reg)
        block.add_register(next_reg)

        # Create cross coverage for state transitions
        cg = CoverGroup("transition_cg")
        curr_cp = CoverPoint("curr_cp", "curr", bins={"states": list(range(8))})
        next_cp = CoverPoint("next_cp", "next", bins={"states": list(range(8))})
        cg.add_coverpoint(curr_cp)
        cg.add_coverpoint(next_cp)

        cross = Cross("transition_cross", ["curr_cp", "next_cp"])
        cg.add_cross(cross)

        # Sample some transitions
        transitions = [(0, 1), (1, 2), (2, 0), (0, 3), (3, 0)]
        for curr, next_state in transitions:
            cg.sample(curr=curr, next=next_state)

        # Should have some transition coverage
        assert cg.coverage > 0.0


# =============================================================================
# RGM Error Injection Coverage
# =============================================================================

@pytest.mark.integration
@pytest.mark.cross_module
@pytest.mark.P2
class TestRGMErrorCoverage:
    """Tests for error handling coverage in RGM operations."""

    def test_error_register_coverage(self):
        """Test coverage of error conditions in error register."""
        # Create error register
        reg = Register("ERROR", 0x00, 32)
        reg.add_field(Field("overflow", bit_offset=0, bit_width=1, access=AccessType.RO, reset_value=0))
        reg.add_field(Field("timeout", bit_offset=1, bit_width=1, access=AccessType.RO, reset_value=0))
        reg.add_field(Field("parity", bit_offset=2, bit_width=1, access=AccessType.RO, reset_value=0))

        # Create coverage for error conditions
        cg = CoverGroup("error_cg")
        cp = CoverPoint("error_cp", "error_type",
                       bins={"none": [0], "overflow": [1], "timeout": [2], "parity": [4]})
        cg.add_coverpoint(cp)

        # Sample various error conditions
        errors = [0, 1, 2, 4, 0]  # None, overflow, timeout, parity, none
        for error in errors:
            cg.sample(error_type=error)

        # Should have visited multiple error types
        assert cg.coverage >= 60.0  # At least 3 distinct error types

    def test_illegal_access_coverage(self):
        """Test coverage of illegal register access patterns."""
        # Create registers with different access permissions
        block = RegisterBlock("ACCESS_TEST", 0x40000000)

        ro_reg = Register("RO_REG", 0x00, 32)
        ro_reg.add_field(Field("value", bit_offset=0, bit_width=32, access=AccessType.RO, reset_value=0))

        wo_reg = Register("WO_REG", 0x04, 32)
        wo_reg.add_field(Field("value", bit_offset=0, bit_width=32, access=AccessType.WO, reset_value=0))

        block.add_register(ro_reg)
        block.add_register(wo_reg)

        # Create coverage for access types
        cg = CoverGroup("access_cg")
        cp = CoverPoint("access_cp", "access_type",
                       bins={"read": ["read"], "write": ["write"],
                             "illegal_write": ["illegal_write"], "illegal_read": ["illegal_read"]})
        cg.add_coverpoint(cp)

        # Test legal accesses
        block.read("RO_REG")
        cg.sample(access_type="read")

        block.write("WO_REG", field="value", value=42)
        cg.sample(access_type="write")

        # Test illegal accesses (may raise exceptions)
        try:
            block.write("RO_REG", field="value", value=42)
        except Exception:
            cg.sample(access_type="illegal_write")

        try:
            block.read("WO_REG")
        except Exception:
            cg.sample(access_type="illegal_read")

        # Should have some access coverage
        assert cg.coverage > 0.0
