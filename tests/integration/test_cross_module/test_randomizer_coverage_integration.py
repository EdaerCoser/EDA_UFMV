"""
Cross-Module Integration Tests: Randomizer + Coverage

Tests integration between Randomization and Coverage systems:
- Automatic coverage sampling during randomization
- Covering randomization distributions
- Constraint-guided coverage
- Combined randomization and coverage workflows
"""

import pytest

from sv_randomizer import Randomizable
from sv_randomizer.core.variables import RandVar, RandCVar, VarType
from coverage.core import CoverGroup, CoverPoint, Cross
from sv_randomizer.constraints.inside import InsideConstraint


# =============================================================================
# Basic Randomizer + Coverage Integration
# =============================================================================

@pytest.mark.integration
@pytest.mark.cross_module
@pytest.mark.P0
class TestRandomizerCoverageBasicIntegration:
    """Tests for basic Randomizer and Coverage integration."""

    def test_randomizable_with_covergroup(self):
        """Test that Randomizable can have associated covergroups."""
        class TestTransaction(Randomizable):
            def __init__(self):
                super().__init__()

                # Randomizable component
                self.addr = RandVar("addr", VarType.BIT, bit_width=8)
                self.data = RandVar("data", VarType.BIT, bit_width=16)

                # Coverage component
                self.cg = CoverGroup("trans_cg")
                addr_cp = CoverPoint("addr_cp", "addr", bins={"auto": 10})
                data_cp = CoverPoint("data_cp", "data", bins={"auto": 10})
                self.cg.add_coverpoint(addr_cp)
                self.cg.add_coverpoint(data_cp)

                # Add coverage to auto-sampling
                self.add_covergroup(self.cg)

        # Create and randomize
        txn = TestTransaction()
        for _ in range(10):
            txn.randomize()
            # Coverage is automatically sampled in post_randomize()

        # Should have collected coverage
        assert txn.cg.coverage > 0.0

    def test_manual_coverage_sampling_after_randomize(self):
        """Test manual coverage sampling after randomization."""
        class TestObj(Randomizable):
            def __init__(self):
                super().__init__()
                self.x = RandVar("x", VarType.BIT, bit_width=8)
                self.y = RandVar("y", VarType.BIT, bit_width=8)

                self.cg = CoverGroup("obj_cg")
                cp = CoverPoint("xy_cp", "x,y", bins={"auto": 10})
                self.cg.add_coverpoint(cp)

        obj = TestObj()

        # Randomize and manually sample
        for _ in range(20):
            obj.randomize()
            obj.cg.sample(x=obj.x.value, y=obj.y.value)

        # Should have coverage
        assert obj.cg.coverage > 0.0


# =============================================================================
# Distribution Coverage
# =============================================================================

@pytest.mark.integration
@pytest.mark.cross_module
@pytest.mark.P0
class TestDistributionCoverage:
    """Tests for covering randomization distributions."""

    def test_uniform_distribution_coverage(self):
        """Test coverage of uniform distribution randomization."""
        class UniformTransaction(Randomizable):
            def __init__(self):
                super().__init__()
                self.value = RandVar("value", VarType.BIT, bit_width=4)  # 0-15

                self.cg = CoverGroup("uniform_cg")
                cp = CoverPoint("value_cp", "value", bins={"vals": list(range(16))})
                self.cg.add_coverpoint(cp)

                self.add_covergroup(self.cg)

        txn = UniformTransaction()

        # Randomize many times to get uniform distribution
        for _ in range(100):
            txn.randomize()

        # With 100 samples over 16 bins, should hit most bins
        # Expected: ~6 hits per bin, so should cover most
        assert txn.cg.coverage > 50.0  # At least 50% coverage

    def test_constrained_distribution_coverage(self):
        """Test coverage of constrained distribution."""
        class ConstrainedTransaction(Randomizable):
            def __init__(self):
                super().__init__()
                self.value = RandVar("value", VarType.BIT, bit_width=8)  # 0-255

                # Add constraint to limit range
                self.add_constraint(lambda: 50 <= self.value.value < 100)

                self.cg = CoverGroup("constrained_cg")
                cp = CoverPoint("value_cp", "value", bins={"auto": 10})
                self.cg.add_coverpoint(cp)

                self.add_covergroup(self.cg)

        txn = ConstrainedTransaction()

        # Randomize with constraint
        for _ in range(50):
            txn.randomize()

        # All values should be in constrained range
        # Verify by checking actual values
        for _ in range(10):
            txn.randomize()
            assert 50 <= txn.value.value < 100

        # Coverage should reflect constraint
        assert txn.cg.coverage > 0.0


# =============================================================================
# Constraint Coverage
# =============================================================================

@pytest.mark.integration
@pytest.mark.cross_module
@pytest.mark.P1
class TestConstraintCoverage:
    """Tests for covering constraint satisfaction."""

    def test_constraint_space_coverage(self):
        """Test coverage over constraint solution space."""
        class ConstraintTransaction(Randomizable):
            def __init__(self):
                super().__init__()
                self.x = RandVar("x", VarType.BIT, bit_width=4)
                self.y = RandVar("y", VarType.BIT, bit_width=4)

                # Add constraints
                self.add_constraint(lambda: self.x.value < self.y.value)
                self.add_constraint(lambda: self.y.value - self.x.value > 2)

                self.cg = CoverGroup("constraint_cg")
                x_cp = CoverPoint("x_cp", "x", bins={"vals": list(range(16))})
                y_cp = CoverPoint("y_cp", "y", bins={"vals": list(range(16))})
                self.cg.add_coverpoint(x_cp)
                self.cg.add_coverpoint(y_cp)

                cross = Cross("xy_cross", ["x_cp", "y_cp"])
                self.cg.add_cross(cross)

        txn = ConstraintTransaction()

        # Randomize with constraints
        for _ in range(30):
            txn.randomize()

        # Should only generate valid constraint combinations
        for _ in range(10):
            txn.randomize()
            assert txn.x.value < txn.y.value
            assert txn.y.value - txn.x.value > 2

        # Coverage should reflect constraint space
        assert txn.cg.coverage > 0.0

    def test_multiple_constraint_coverage(self):
        """Test coverage with multiple disjoint constraints."""
        class MultiConstraintTransaction(Randomizable):
            def __init__(self):
                super().__init__()
                self.mode = RandVar("mode", VarType.BIT, bit_width=3)  # 0-7

                # Create disjoint valid ranges
                self.add_constraint(lambda: self.mode.value in [0, 1, 2])

                self.cg = CoverGroup("mode_cg")
                cp = CoverPoint("mode_cp", "mode", bins={"modes": list(range(8))})
                self.cg.add_coverpoint(cp)

        txn = MultiConstraintTransaction()

        # Randomize many times
        for _ in range(30):
            txn.randomize()

            # Verify constraint
            assert txn.mode.value in [0, 1, 2]

        # Coverage should only show valid modes
        # Should hit 0, 1, 2 but not 3-7
        assert txn.cg.coverage > 0.0


# =============================================================================
# Cross Coverage with Randomization
# =============================================================================

@pytest.mark.integration
@pytest.mark.cross_module
@pytest.mark.P0
class TestRandomizerCrossCoverage:
    """Tests for cross coverage with randomized variables."""

    def test_two_variable_cross_coverage(self):
        """Test cross coverage between two randomized variables."""
        class CrossTransaction(Randomizable):
            def __init__(self):
                super().__init__()
                self.a = RandVar("a", VarType.BIT, bit_width=2)  # 0-3
                self.b = RandVar("b", VarType.BIT, bit_width=2)  # 0-3

                self.cg = CoverGroup("cross_cg")
                a_cp = CoverPoint("a_cp", "a", bins={"vals": list(range(4))})
                b_cp = CoverPoint("b_cp", "b", bins={"vals": list(range(4))})
                self.cg.add_coverpoint(a_cp)
                self.cg.add_coverpoint(b_cp)

                cross = Cross("ab_cross", ["a_cp", "b_cp"])
                self.cg.add_cross(cross)

                self.add_covergroup(self.cg)

        txn = CrossTransaction()

        # Randomize to get cross coverage
        for _ in range(50):
            txn.randomize()

        # 16 possible combinations (4x4)
        # With 50 samples, should get decent coverage
        assert txn.cg.coverage > 0.0

    def test_three_variable_cross_coverage(self):
        """Test cross coverage with three randomized variables."""
        class ThreeVarTransaction(Randomizable):
            def __init__(self):
                super().__init__()
                self.x = RandVar("x", VarType.BIT, bit_width=2)  # 0-3
                self.y = RandVar("y", VarType.BIT, bit_width=2)  # 0-3
                self.z = RandVar("z", VarType.BIT, bit_width=2)  # 0-3

                self.cg = CoverGroup("three_cross_cg")
                x_cp = CoverPoint("x_cp", "x", bins={"vals": list(range(4))})
                y_cp = CoverPoint("y_cp", "y", bins={"vals": list(range(4))})
                z_cp = CoverPoint("z_cp", "z", bins={"vals": list(range(4))})
                self.cg.add_coverpoint(x_cp)
                self.cg.add_coverpoint(y_cp)
                self.cg.add_coverpoint(z_cp)

                cross = Cross("xyz_cross", ["x_cp", "y_cp", "z_cp"])
                self.cg.add_cross(cross)

        txn = ThreeVarTransaction()

        # Randomize
        for _ in range(100):
            txn.randomize()
            txn.cg.sample(x=txn.x.value, y=txn.y.value, z=txn.z.value)

        # 64 possible combinations (4x4x4)
        # With 100 samples, might get reasonable coverage
        assert txn.cg.coverage > 0.0


# =============================================================================
# Coverage-Guided Randomization
# =============================================================================

@pytest.mark.integration
@pytest.mark.cross_module
@pytest.mark.P1
class TestCoverageGuidedRandomization:
    """Tests for coverage-guided randomization strategies."""

    def test_fill_coverage_gaps_randomly(self):
        """Test using coverage metrics to guide randomization."""
        class GapFillingTransaction(Randomizable):
            def __init__(self):
                super().__init__()
                self.value = RandVar("value", VarType.BIT, bit_width=4)  # 0-15

                self.cg = CoverGroup("gap_cg")
                cp = CoverPoint("value_cp", "value", bins={"vals": list(range(16))})
                self.cg.add_coverpoint(cp)

                # Track which values have been covered
                self._covered_values = set()

            def randomize(self):
                # Override to guide toward uncovered values
                super().randomize()

                # Record coverage
                self._covered_values.add(self.value.value)
                self.cg.sample(value=self.value.value)

                # Check if we need to target uncovered values
                if len(self._covered_values) < 16:
                    uncovered = set(range(16)) - self._covered_values
                    if uncovered and len(self._covered_values) < 12:
                        # 25% chance to target an uncovered value
                        import random
                        if random.random() < 0.25:
                            target = random.choice(list(uncovered))
                            self.value._value = target
                            self._covered_values.add(target)
                            self.cg.sample(value=target)

        txn = GapFillingTransaction()

        # Randomize many times
        for _ in range(100):
            txn.randomize()

        # Should get better coverage with guided approach
        assert txn.cg.coverage > 70.0  # Most values covered

    def test_biased_randomization_for_coverage(self):
        """Test biased randomization to improve coverage."""
        class BiasedTransaction(Randomizable):
            def __init__(self):
                super().__init__()
                self.value = RandVar("value", VarType.BIT, bit_width=4)

                self.cg = CoverGroup("biased_cg")
                cp = CoverPoint("value_cp", "value", bins={"vals": list(range(16))})
                self.cg.add_coverpoint(cp)

                # Track coverage
                self._coverage_counts = {i: 0 for i in range(16)}

            def randomize_with_bias(self):
                """Randomize with bias toward less-covered values."""
                super().randomize()

                # Find least-covered values
                min_count = min(self._coverage_counts.values())
                under_covered = [v for v, c in self._coverage_counts.items() if c == min_count]

                # 50% chance to pick from under-covered
                import random
                if random.random() < 0.5 and under_covered:
                    target = random.choice(under_covered)
                    self.value._value = target

                # Record and sample
                self._coverage_counts[self.value.value] += 1
                self.cg.sample(value=self.value.value)

        txn = BiasedTransaction()

        # Randomize with bias
        for _ in range(80):
            txn.randomize_with_bias()

        # Should get better distribution
        assert txn.cg.coverage > 70.0


# =============================================================================
# RandC Variable Coverage
# =============================================================================

@pytest.mark.integration
@pytest.mark.cross_module
@pytest.mark.P1
class TestRandCCoverage:
    """Tests for covering RandC (cyclic randomization) variables."""

    def test_randc_complete_coverage(self):
        """Test that RandC cycles through all values."""
        class RandCTransaction(Randomizable):
            def __init__(self):
                super().__init__()
                self.counter = RandCVar("counter", VarType.BIT, bit_width=3)  # 0-7

                self.cg = CoverGroup("randc_cg")
                cp = CoverPoint("counter_cp", "counter", bins={"vals": list(range(8))})
                self.cg.add_coverpoint(cp)

        txn = RandCTransaction()

        # Randomize 8 times (should cycle through all values)
        for _ in range(8):
            txn.randomize()
            txn.cg.sample(counter=txn.counter.value)

        # RandC should cycle through all values
        # Note: starting point is random, but after 8 iterations should cover all
        assert txn.cg.coverage >= 87.5  # At least 7 of 8 values

    def test_randc_no_duplicates_in_cycle(self):
        """Test that RandC doesn't repeat within cycle."""
        class RandCTransaction(Randomizable):
            def __init__(self):
                super().__init__()
                self.counter = RandCVar("counter", VarType.BIT, bit_width=3)  # 0-7

        txn = RandCTransaction()

        # Collect 8 values
        values = []
        for _ in range(8):
            txn.randomize()
            values.append(txn.counter.value)

        # Should have 8 unique values
        assert len(set(values)) == 8
        assert set(values) == set(range(8))


# =============================================================================
# Complex Integration Scenarios
# =============================================================================

@pytest.mark.integration
@pytest.mark.cross_module
@pytest.mark.P2
class TestComplexIntegrationScenarios:
    """Tests for complex integration scenarios."""

    def test_transaction_with_multiple_covergroups(self):
        """Test transaction with multiple independent covergroups."""
        class ComplexTransaction(Randomizable):
            def __init__(self):
                super().__init__()

                # Randomizable fields
                self.addr = RandVar("addr", VarType.BIT, bit_width=8)
                self.data = RandVar("data", VarType.BIT, bit_width=16)
                self.cmd = RandVar("cmd", VarType.BIT, bit_width=4)

                # Multiple covergroups
                self.addr_cg = CoverGroup("addr_cg")
                addr_cp = CoverPoint("addr_cp", "addr", bins={"auto": 10})
                self.addr_cg.add_coverpoint(addr_cp)

                self.data_cg = CoverGroup("data_cg")
                data_cp = CoverPoint("data_cp", "data", bins={"auto": 10})
                self.data_cg.add_coverpoint(data_cp)

                self.cmd_cg = CoverGroup("cmd_cg")
                cmd_cp = CoverPoint("cmd_cp", "cmd", bins={"cmds": list(range(16))})
                self.cmd_cg.add_coverpoint(cmd_cp)

        txn = ComplexTransaction()

        # Randomize and sample all covergroups
        for _ in range(30):
            txn.randomize()
            txn.addr_cg.sample(addr=txn.addr.value)
            txn.data_cg.sample(data=txn.data.value)
            txn.cmd_cg.sample(cmd=txn.cmd.value)

        # All covergroups should have coverage
        assert txn.addr_cg.coverage > 0.0
        assert txn.data_cg.coverage > 0.0
        assert txn.cmd_cg.coverage > 0.0

    def test_hierarchical_coverage(self):
        """Test coverage in hierarchical randomizable structure."""
        class InnerTransaction(Randomizable):
            def __init__(self):
                super().__init__()
                self.inner_val = RandVar("inner_val", VarType.BIT, bit_width=4)

                self.inner_cg = CoverGroup("inner_cg")
                cp = CoverPoint("inner_cp", "inner_val", bins={"vals": list(range(16))})
                self.inner_cg.add_coverpoint(cp)

        class OuterTransaction(Randomizable):
            def __init__(self):
                super().__init__()
                self.outer_val = RandVar("outer_val", VarType.BIT, bit_width=4)
                self.inner = InnerTransaction()

                self.outer_cg = CoverGroup("outer_cg")
                cp = CoverPoint("outer_cp", "outer_val", bins={"vals": list(range(16))})
                self.outer_cg.add_coverpoint(cp)

        txn = OuterTransaction()

        # Randomize both levels
        for _ in range(30):
            txn.outer_val.randomize()
            txn.inner.randomize()
            txn.outer_cg.sample(outer_val=txn.outer_val.value)
            txn.inner.inner_cg.sample(inner_val=txn.inner.inner_val.value)

        # Both levels should have coverage
        assert txn.outer_cg.coverage > 0.0
        assert txn.inner.inner_cg.coverage > 0.0
