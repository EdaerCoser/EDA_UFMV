"""
Performance Benchmark Tests

Establishes performance baselines for critical operations:
- Coverage sampling speed
- Randomization throughput
- RGM access operations
- Cross-module performance

Note: These tests establish baselines and should be run regularly
to detect performance regressions.
"""

import pytest
import time

from sv_randomizer import Randomizable
from sv_randomizer.core.variables import RandVar, RandCVar, VarType
from coverage.core import CoverGroup, CoverPoint, Cross
from rgm.core import RegisterBlock, Register, Field
from rgm.utils import AccessType


# =============================================================================
# Performance Baseline Values (minimum ops/sec)
# =============================================================================

PERFORMANCE_BASELINES = {
    # Coverage sampling
    "simple_sampling": 10000,      # ops/sec for <10 bins
    "complex_sampling": 1000,      # ops/sec for >100 bins
    "cross_sampling": 500,         # ops/sec for cross coverage

    # Randomization
    "simple_randomize": 10000,     # ops/sec for simple constraints
    "complex_randomize": 1000,     # ops/sec for complex constraints
    "randc_cycle": 5000,           # ops/sec for RandC cycling

    # RGM operations
    "register_read": 50000,        # ops/sec
    "register_write": 50000,       # ops/sec
    "field_access": 100000,        # ops/sec
    "block_access": 10000,         # ops/sec
}

# Performance regression threshold (10%)
REGRESSION_THRESHOLD = 0.10


# =============================================================================
# Coverage Sampling Benchmarks
# =============================================================================

@pytest.mark.performance
@pytest.mark.benchmark
@pytest.mark.P0
class TestCoverageSamplingPerformance:
    """Performance tests for coverage sampling."""

    def test_simple_sampling_performance(self):
        """Benchmark simple coverage sampling (< 10 bins)."""
        cg = CoverGroup("simple_cg")
        cp = CoverPoint("simple_cp", "value", bins={"vals": list(range(10))})
        cg.add_coverpoint(cp)

        # Warm-up
        for i in range(100):
            cg.sample(value=i % 10)

        # Benchmark
        iterations = 10000
        start = time.perf_counter()

        for i in range(iterations):
            cg.sample(value=i % 10)

        elapsed = time.perf_counter() - start
        ops_per_sec = iterations / elapsed

        # Verify performance meets baseline
        baseline = PERFORMANCE_BASELINES["simple_sampling"]
        min_ops = baseline * (1.0 - REGRESSION_THRESHOLD)

        assert ops_per_sec >= min_ops, \
            f"Simple sampling performance {ops_per_sec:.0f} ops/sec below baseline {baseline}"

        print(f"\nSimple sampling: {ops_per_sec:.0f} ops/sec")

    def test_complex_sampling_performance(self):
        """Benchmark complex coverage sampling (> 100 bins)."""
        cg = CoverGroup("complex_cg")
        cp = CoverPoint("complex_cp", "value", bins={"vals": list(range(200))})
        cg.add_coverpoint(cp)

        # Warm-up
        for i in range(100):
            cg.sample(value=i % 200)

        # Benchmark
        iterations = 5000
        start = time.perf_counter()

        for i in range(iterations):
            cg.sample(value=i % 200)

        elapsed = time.perf_counter() - start
        ops_per_sec = iterations / elapsed

        # Verify performance
        baseline = PERFORMANCE_BASELINES["complex_sampling"]
        min_ops = baseline * (1.0 - REGRESSION_THRESHOLD)

        assert ops_per_sec >= min_ops, \
            f"Complex sampling performance {ops_per_sec:.0f} ops/sec below baseline {baseline}"

        print(f"Complex sampling: {ops_per_sec:.0f} ops/sec")

    def test_cross_sampling_performance(self):
        """Benchmark cross coverage sampling."""
        cg = CoverGroup("cross_cg")
        cp1 = CoverPoint("cp1", "a", bins={"vals": list(range(10))})
        cp2 = CoverPoint("cp2", "b", bins={"vals": list(range(10))})
        cg.add_coverpoint(cp1)
        cg.add_coverpoint(cp2)

        cross = Cross("cross", ["cp1", "cp2"])
        cg.add_cross(cross)

        # Warm-up
        for i in range(100):
            cg.sample(a=i % 10, b=(i * 2) % 10)

        # Benchmark
        iterations = 3000
        start = time.perf_counter()

        for i in range(iterations):
            cg.sample(a=i % 10, b=(i * 2) % 10)

        elapsed = time.perf_counter() - start
        ops_per_sec = iterations / elapsed

        # Verify performance
        baseline = PERFORMANCE_BASELINES["cross_sampling"]
        min_ops = baseline * (1.0 - REGRESSION_THRESHOLD)

        assert ops_per_sec >= min_ops, \
            f"Cross sampling performance {ops_per_sec:.0f} ops/sec below baseline {baseline}"

        print(f"Cross sampling: {ops_per_sec:.0f} ops/sec")


# =============================================================================
# Randomization Benchmarks
# =============================================================================

@pytest.mark.performance
@pytest.mark.benchmark
@pytest.mark.P0
class TestRandomizationPerformance:
    """Performance tests for randomization."""

    def test_simple_randomization_performance(self):
        """Benchmark simple randomization (no constraints)."""
        class SimpleRandomizable(Randomizable):
            def __init__(self):
                super().__init__()
                self.x = RandVar("x", VarType.BIT, bit_width=8)
                self.y = RandVar("y", VarType.BIT, bit_width=16)

        obj = SimpleRandomizable()

        # Warm-up
        for _ in range(100):
            obj.randomize()

        # Benchmark
        iterations = 10000
        start = time.perf_counter()

        for _ in range(iterations):
            obj.randomize()

        elapsed = time.perf_counter() - start
        ops_per_sec = iterations / elapsed

        # Verify performance
        baseline = PERFORMANCE_BASELINES["simple_randomize"]
        min_ops = baseline * (1.0 - REGRESSION_THRESHOLD)

        assert ops_per_sec >= min_ops, \
            f"Simple randomization performance {ops_per_sec:.0f} ops/sec below baseline {baseline}"

        print(f"Simple randomization: {ops_per_sec:.0f} ops/sec")

    def test_constrained_randomization_performance(self):
        """Benchmark constrained randomization."""
        class ConstrainedRandomizable(Randomizable):
            def __init__(self):
                super().__init__()
                self.x = RandVar("x", VarType.BIT, bit_width=8)
                self.y = RandVar("y", VarType.BIT, bit_width=8)

                self.add_constraint(lambda: self.x.value < 100)
                self.add_constraint(lambda: self.y.value > self.x.value)

        obj = ConstrainedRandomizable()

        # Warm-up
        for _ in range(100):
            obj.randomize()

        # Benchmark
        iterations = 2000
        start = time.perf_counter()

        for _ in range(iterations):
            obj.randomize()

        elapsed = time.perf_counter() - start
        ops_per_sec = iterations / elapsed

        # Verify performance
        baseline = PERFORMANCE_BASELINES["complex_randomize"]
        min_ops = baseline * (1.0 - REGRESSION_THRESHOLD)

        assert ops_per_sec >= min_ops, \
            f"Constrained randomization performance {ops_per_sec:.0f} ops/sec below baseline {baseline}"

        print(f"Constrained randomization: {ops_per_sec:.0f} ops/sec")

    def test_randc_performance(self):
        """Benchmark RandC (cyclic) randomization."""
        class RandCRandomizable(Randomizable):
            def __init__(self):
                super().__init__()
                self.counter = RandCVar("counter", VarType.BIT, bit_width=8)

        obj = RandCRandomizable()

        # Warm-up
        for _ in range(100):
            obj.randomize()

        # Benchmark
        iterations = 5000
        start = time.perf_counter()

        for _ in range(iterations):
            obj.randomize()

        elapsed = time.perf_counter() - start
        ops_per_sec = iterations / elapsed

        # Verify performance
        baseline = PERFORMANCE_BASELINES["randc_cycle"]
        min_ops = baseline * (1.0 - REGRESSION_THRESHOLD)

        assert ops_per_sec >= min_ops, \
            f"RandC performance {ops_per_sec:.0f} ops/sec below baseline {baseline}"

        print(f"RandC cycling: {ops_per_sec:.0f} ops/sec")


# =============================================================================
# RGM Access Benchmarks
# =============================================================================

@pytest.mark.performance
@pytest.mark.benchmark
@pytest.mark.P0
class TestRGMPerformance:
    """Performance tests for RGM operations."""

    def test_register_read_performance(self):
        """Benchmark register read operations."""
        block = RegisterBlock("TEST", 0x40000000)
        reg = Register("TEST_REG", 0x00, 32)
        reg.add_field(Field("value", bit_offset=0, bit_width=32, access=AccessType.RO, reset_value=42))
        block.add_register(reg)

        # Warm-up
        for _ in range(100):
            block.read("TEST_REG")

        # Benchmark
        iterations = 50000
        start = time.perf_counter()

        for _ in range(iterations):
            block.read("TEST_REG")

        elapsed = time.perf_counter() - start
        ops_per_sec = iterations / elapsed

        # Verify performance
        baseline = PERFORMANCE_BASELINES["register_read"]
        min_ops = baseline * (1.0 - REGRESSION_THRESHOLD)

        assert ops_per_sec >= min_ops, \
            f"Register read performance {ops_per_sec:.0f} ops/sec below baseline {baseline}"

        print(f"Register read: {ops_per_sec:.0f} ops/sec")

    def test_register_write_performance(self):
        """Benchmark register write operations."""
        block = RegisterBlock("TEST", 0x40000000)
        reg = Register("TEST_REG", 0x00, 32)
        reg.add_field(Field("value", bit_offset=0, bit_width=32, access=AccessType.RW, reset_value=0))
        block.add_register(reg)

        # Warm-up
        for _ in range(100):
            block.write("TEST_REG", field="value", value=42)

        # Benchmark
        iterations = 50000
        start = time.perf_counter()

        for _ in range(iterations):
            block.write("TEST_REG", field="value", value=42)

        elapsed = time.perf_counter() - start
        ops_per_sec = iterations / elapsed

        # Verify performance
        baseline = PERFORMANCE_BASELINES["register_write"]
        min_ops = baseline * (1.0 - REGRESSION_THRESHOLD)

        assert ops_per_sec >= min_ops, \
            f"Register write performance {ops_per_sec:.0f} ops/sec below baseline {baseline}"

        print(f"Register write: {ops_per_sec:.0f} ops/sec")

    def test_field_access_performance(self):
        """Benchmark field-level access."""
        reg = Register("FIELD_REG", 0x00, 32)
        for i in range(8):
            field = Field(f"field_{i}", bit_offset=i * 4, bit_width=4, access=AccessType.RW, reset_value=0)
            reg.add_field(field)

        # Warm-up
        for _ in range(100):
            for i in range(8):
                reg.read(field=f"field_{i}")

        # Benchmark
        iterations = 100000
        start = time.perf_counter()

        for _ in range(iterations):
            for i in range(8):
                reg.read(field=f"field_{i}")

        elapsed = time.perf_counter() - start
        ops_per_sec = (iterations * 8) / elapsed

        # Verify performance
        baseline = PERFORMANCE_BASELINES["field_access"]
        min_ops = baseline * (1.0 - REGRESSION_THRESHOLD)

        assert ops_per_sec >= min_ops, \
            f"Field access performance {ops_per_sec:.0f} ops/sec below baseline {baseline}"

        print(f"Field access: {ops_per_sec:.0f} ops/sec")

    def test_block_access_performance(self):
        """Benchmark block-level access with multiple registers."""
        block = RegisterBlock("MULTI_REG", 0x40000000)
        for i in range(10):
            reg = Register(f"REG_{i}", i * 4, 32)
            reg.add_field(Field("value", bit_offset=0, bit_width=32, access=AccessType.RW, reset_value=0))
            block.add_register(reg)

        # Warm-up
        for _ in range(100):
            for i in range(10):
                block.read(f"REG_{i}")

        # Benchmark
        iterations = 10000
        start = time.perf_counter()

        for _ in range(iterations):
            for i in range(10):
                block.read(f"REG_{i}")

        elapsed = time.perf_counter() - start
        ops_per_sec = (iterations * 10) / elapsed

        # Verify performance
        baseline = PERFORMANCE_BASELINES["block_access"]
        min_ops = baseline * (1.0 - REGRESSION_THRESHOLD)

        assert ops_per_sec >= min_ops, \
            f"Block access performance {ops_per_sec:.0f} ops/sec below baseline {baseline}"

        print(f"Block access: {ops_per_sec:.0f} ops/sec")


# =============================================================================
# Cross-Module Performance
# =============================================================================

@pytest.mark.performance
@pytest.mark.benchmark
@pytest.mark.P1
class TestCrossModulePerformance:
    """Performance tests for cross-module operations."""

    def test_randomize_with_coverage_performance(self):
        """Benchmark randomization with automatic coverage sampling."""
        class IntegratedTransaction(Randomizable):
            def __init__(self):
                super().__init__()
                self.x = RandVar("x", VarType.BIT, bit_width=8)
                self.y = RandVar("y", VarType.BIT, bit_width=8)

                self.cg = CoverGroup("integrated_cg")
                x_cp = CoverPoint("x_cp", "x", bins={"auto": 10})
                y_cp = CoverPoint("y_cp", "y", bins={"auto": 10})
                self.cg.add_coverpoint(x_cp)
                self.cg.add_coverpoint(y_cp)

                self.add_covergroup(self.cg)

        txn = IntegratedTransaction()

        # Warm-up
        for _ in range(100):
            txn.randomize()

        # Benchmark
        iterations = 5000
        start = time.perf_counter()

        for _ in range(iterations):
            txn.randomize()

        elapsed = time.perf_counter() - start
        ops_per_sec = iterations / elapsed

        # Integrated operation should be reasonably fast
        min_ops = 1000 * (1.0 - REGRESSION_THRESHOLD)

        assert ops_per_sec >= min_ops, \
            f"Integrated randomize+coverage performance {ops_per_sec:.0f} ops/sec below minimum"

        print(f"Randomize + coverage: {ops_per_sec:.0f} ops/sec")

    def test_rgm_write_with_coverage_performance(self):
        """Benchmark RGM write with coverage sampling."""
        # Setup RGM
        block = RegisterBlock("PERF_TEST", 0x40000000)
        reg = Register("CTRL", 0x00, 32)
        reg.add_field(Field("cmd", bit_offset=0, bit_width=8, access=AccessType.RW, reset_value=0))
        block.add_register(reg)

        # Setup Coverage
        cg = CoverGroup("cmd_cg")
        cp = CoverPoint("cmd_cp", "cmd", bins={"cmds": list(range(256))})
        cg.add_coverpoint(cp)

        # Warm-up
        for i in range(100):
            block.write("CTRL", field="cmd", value=i % 256)
            cg.sample(cmd=i % 256)

        # Benchmark
        iterations = 20000
        start = time.perf_counter()

        for i in range(iterations):
            block.write("CTRL", field="cmd", value=i % 256)
            cg.sample(cmd=i % 256)

        elapsed = time.perf_counter() - start
        ops_per_sec = iterations / elapsed

        # Combined operation should be fast
        min_ops = 5000 * (1.0 - REGRESSION_THRESHOLD)

        assert ops_per_sec >= min_ops, \
            f"RGM write + coverage performance {ops_per_sec:.0f} ops/sec below minimum"

        print(f"RGM write + coverage: {ops_per_sec:.0f} ops/sec")


# =============================================================================
# Scalability Tests
# =============================================================================

@pytest.mark.performance
@pytest.mark.benchmark
@pytest.mark.P1
class TestScalability:
    """Tests for performance scalability with size."""

    def test_coverage_scalability_with_bins(self):
        """Test coverage sampling performance vs number of bins."""
        bin_counts = [10, 50, 100, 500, 1000]
        results = {}

        for num_bins in bin_counts:
            cg = CoverGroup(f"scale_{num_bins}")
            cp = CoverPoint("cp", "value", bins={"vals": list(range(num_bins))})
            cg.add_coverpoint(cp)

            # Benchmark
            iterations = 1000
            start = time.perf_counter()

            for i in range(iterations):
                cg.sample(value=i % num_bins)

            elapsed = time.perf_counter() - start
            ops_per_sec = iterations / elapsed
            results[num_bins] = ops_per_sec

            print(f"Coverage with {num_bins} bins: {ops_per_sec:.0f} ops/sec")

        # Performance should degrade gracefully (not exponentially)
        # 1000 bins should be at least 20% of 10 bins performance
        ratio = results[1000] / results[10]
        assert ratio > 0.2, f"Coverage scalability poor: {ratio:.2%} of base performance"

    def test_rgm_scalability_with_registers(self):
        """Test RGM access performance vs number of registers."""
        register_counts = [1, 10, 50, 100]
        results = {}

        for num_regs in register_counts:
            block = RegisterBlock(f"SCALE_{num_regs}", 0x40000000)
            for i in range(num_regs):
                reg = Register(f"REG_{i}", i * 4, 32)
                reg.add_field(Field("value", bit_offset=0, bit_width=32, access=AccessType.RW, reset_value=0))
                block.add_register(reg)

            # Benchmark
            iterations = 1000
            start = time.perf_counter()

            for i in range(iterations):
                reg_idx = i % num_regs
                block.read(f"REG_{reg_idx}")

            elapsed = time.perf_counter() - start
            ops_per_sec = iterations / elapsed
            results[num_regs] = ops_per_sec

            print(f"RGM with {num_regs} registers: {ops_per_sec:.0f} ops/sec")

        # Performance should scale reasonably
        # 100 registers should be at least 30% of 1 register
        ratio = results[100] / results[1]
        assert ratio > 0.3, f"RGM scalability poor: {ratio:.2%} of base performance"


# =============================================================================
# Memory Performance Tests
# =============================================================================

@pytest.mark.performance
@pytest.mark.benchmark
@pytest.mark.P2
class TestMemoryPerformance:
    """Tests for memory efficiency and object creation."""

    def test_coverage_object_creation(self):
        """Benchmark coverage object creation overhead."""
        iterations = 1000

        start = time.perf_counter()

        for i in range(iterations):
            cg = CoverGroup(f"temp_cg_{i}")
            cp = CoverPoint("cp", "value", bins={"vals": list(range(10))})
            cg.add_coverpoint(cp)
            cg.sample(value=i % 10)

        elapsed = time.perf_counter() - start
        ops_per_sec = iterations / elapsed

        print(f"Coverage object creation: {ops_per_sec:.0f} ops/sec")

        # Should be able to create objects quickly
        assert ops_per_sec > 100, "Coverage object creation too slow"

    def test_randomizable_object_creation(self):
        """Benchmark Randomizable object creation overhead."""
        iterations = 1000

        start = time.perf_counter()

        for _ in range(iterations):
            class TempRandomizable(Randomizable):
                def __init__(self):
                    super().__init__()
                    self.x = RandVar("x", VarType.BIT, bit_width=8)

            obj = TempRandomizable()
            obj.randomize()

        elapsed = time.perf_counter() - start
        ops_per_sec = iterations / elapsed

        print(f"Randomizable object creation: {ops_per_sec:.0f} ops/sec")

        # Should be able to create and randomize quickly
        assert ops_per_sec > 100, "Randomizable object creation too slow"


# =============================================================================
# Performance Summary
# =============================================================================

@pytest.mark.performance
@pytest.mark.benchmark
@pytest.mark.P1
def test_performance_summary():
    """Print summary of all performance benchmarks."""
    print("\n" + "=" * 70)
    print("PERFORMANCE BASELINES")
    print("=" * 70)

    for operation, baseline in PERFORMANCE_BASELINES.items():
        print(f"{operation:30s}: {baseline:>10.0f} ops/sec")

    print("=" * 70)
    print(f"Regression Threshold: {REGRESSION_THRESHOLD:.1%}")
    print("=" * 70)
