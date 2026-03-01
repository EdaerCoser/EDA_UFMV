"""
Global pytest configuration and shared fixtures for EDA_UFMV tests.

This file provides common fixtures and configuration for all test modules:
- Coverage system fixtures
- Randomization framework fixtures
- RGM fixtures
- Test utilities and helpers
"""

import sys
import tempfile
import shutil
from pathlib import Path
from typing import Dict, Any, List
import pytest

# =============================================================================
# pytest Configuration
# =============================================================================

def pytest_configure(config):
    """Configure pytest with custom markers and plugin settings."""
    # Disable qt plugin (prevents DLL loading issues on Windows)
    if hasattr(config, 'pluginmanager'):
        config.pluginmanager.set_blocked('pytest-qt')

    # Register custom markers
    config.addinivalue_line("markers", "unit: 单元测试")
    config.addinivalue_line("markers", "integration: 集成测试")
    config.addinivalue_line("markers", "performance: 性能测试")
    config.addinivalue_line("markers", "benchmark: 基准测试")
    config.addinivalue_line("markers", "regression: 回归测试")
    config.addinivalue_line("markers", "P0: P0级关键测试")
    config.addinivalue_line("markers", "P1: P1级重要测试")
    config.addinivalue_line("markers", "P2: P2级增强测试")
    config.addinivalue_line("markers", "slow: 慢速测试")
    config.addinivalue_line("markers", "error_handling: 异常处理测试")
    config.addinivalue_line("markers", "boundary: 边界情况测试")
    config.addinivalue_line("markers", "cross_module: 跨模块集成测试")
    config.addinivalue_line("markers", "end_to_end: 端到端工作流测试")


# =============================================================================
# Path Fixtures
# =============================================================================

@pytest.fixture(scope="session")
def project_root() -> Path:
    """Return the project root directory."""
    return Path(__file__).parent.parent


@pytest.fixture(scope="session")
def tests_dir(project_root: Path) -> Path:
    """Return the tests directory."""
    return project_root / "tests"


@pytest.fixture(scope="session")
def fixtures_dir(tests_dir: Path) -> Path:
    """Return the test fixtures directory."""
    return tests_dir / "fixtures"


@pytest.fixture(scope="function")
def temp_dir() -> Path:
    """Create a temporary directory for test files."""
    temp_path = Path(tempfile.mkdtemp())
    yield temp_path
    # Cleanup after test
    if temp_path.exists():
        shutil.rmtree(temp_path)


# =============================================================================
# Coverage System Fixtures
# =============================================================================

@pytest.fixture(scope="function")
def sample_bins() -> Dict[str, List[int]]:
    """Provide sample bin configurations for testing."""
    return {
        "simple_values": [1, 2, 3, 4, 5],
        "range_bins": [(1, 10), (20, 30), (40, 50)],
        "wildcard_bins": ["4'b00??", "4'b1???", "4'b?1?1"],
        "auto_bins": {"auto": 10},  # 10 automatic bins
        "ignore_bins": [0, -1],
        "illegal_bins": [999, 1000],
    }


@pytest.fixture(scope="function")
def sample_covergroup():
    """Create a sample CoverGroup for testing."""
    from coverage.core import CoverGroup, CoverPoint

    cg = CoverGroup("test_cg")

    # Add a simple coverpoint
    cp1 = CoverPoint(
        "cp_values",
        "value",
        bins={"values": [1, 2, 3, 4, 5]}
    )
    cg.add_coverpoint(cp1)

    # Add a range coverpoint
    cp2 = CoverPoint(
        "cp_range",
        "value",
        bins={"range": [(0, 10), (11, 20), (21, 30)]}
    )
    cg.add_coverpoint(cp2)

    return cg


@pytest.fixture(scope="function")
def sample_cross_coverage():
    """Create sample Cross coverage for testing."""
    from coverage.core import CoverGroup, CoverPoint, Cross

    cg = CoverGroup("cross_cg")

    # Add coverpoints for cross
    cp1 = CoverPoint("cp_a", "a", bins={"values": [0, 1]})
    cp2 = CoverPoint("cp_b", "b", bins={"values": [0, 1]})
    cg.add_coverpoint(cp1)
    cg.add_coverpoint(cp2)

    # Create cross
    cross = Cross("cross_ab", ["cp_a", "cp_b"])
    cg.add_cross(cross)

    return cg


# =============================================================================
# Randomization Framework Fixtures
# =============================================================================

@pytest.fixture(scope="function")
def sample_randomizable():
    """Create a sample Randomizable object for testing."""
    from sv_randomizer import Randomizable
    from sv_randomizer.core.variables import RandVar, RandCVar, VarType

    class TestRandomizable(Randomizable):
        def __init__(self):
            super().__init__()
            self.rand_var = RandVar("rand_var", VarType.BIT, bit_width=8)
            self.randc_var = RandCVar("randc_var", VarType.BIT, bit_width=4)

    return TestRandomizable()


@pytest.fixture(scope="function")
def sample_constraint_data() -> Dict[str, Any]:
    """Provide sample constraint data for testing."""
    return {
        "simple_constraint": {"value": 10},
        "range_constraint": {"value": (1, 100)},
        "list_constraint": {"value": [1, 2, 3, 5, 8, 13]},
        "dist_constraint": {"value": [(1, 10), (2, 20), (3, 70)]},
    }


# =============================================================================
# RGM Fixtures
# =============================================================================

@pytest.fixture(scope="function")
def sample_register_block():
    """Create a sample RegisterBlock for testing."""
    from rgm.core import RegisterBlock, Register, Field
    from rgm.utils import AccessType

    block = RegisterBlock("UART", 0x40000000)

    # Create a control register
    ctrl_reg = Register("CTRL", 0x00, 32)
    ctrl_reg.add_field(Field("enable", 0, 1, AccessType.RW, reset_value=0))
    ctrl_reg.add_field(Field("start", 1, 1, AccessType.RW, reset_value=0))
    ctrl_reg.add_field(Field("stop", 2, 1, AccessType.RW, reset_value=0))
    block.add_register(ctrl_reg)

    # Create a status register
    status_reg = Register("STATUS", 0x04, 32)
    status_reg.add_field(Field("busy", 0, 1, AccessType.RO, reset_value=0))
    status_reg.add_field(Field("done", 1, 1, AccessType.RO, reset_value=0))
    block.add_register(status_reg)

    # Create a data register
    data_reg = Register("DATA", 0x08, 32)
    data_reg.add_field(Field("value", 0, 32, AccessType.RW, reset_value=0))
    block.add_register(data_reg)

    return block


@pytest.fixture(scope="function")
def sample_memory_map():
    """Create a sample memory map for testing."""
    return {
        "UART": 0x40000000,
        "SPI": 0x40001000,
        "I2C": 0x40002000,
        "GPIO": 0x40003000,
    }


# =============================================================================
# Test Data Fixtures
# =============================================================================

@pytest.fixture(scope="session")
def boundary_values() -> Dict[str, Any]:
    """Provide boundary values for testing edge cases."""
    return {
        # Numeric boundaries
        "max_uint8": 255,
        "max_uint16": 65535,
        "max_uint32": 4294967295,
        "max_int8": 127,
        "min_int8": -128,
        "max_int16": 32767,
        "min_int16": -32768,

        # Special floating point values
        "float_nan": float('nan'),
        "float_inf": float('inf'),
        "float_neg_inf": float('-inf'),

        # String boundaries
        "empty_string": "",
        "long_string": "a" * 10000,

        # Collection boundaries
        "empty_list": [],
        "single_item": [1],
        "large_list": list(range(1000)),
    }


@pytest.fixture(scope="session")
def performance_baselines() -> Dict[str, float]:
    """Provide performance baseline values (minimum operations per second)."""
    return {
        # Coverage sampling baselines
        "simple_sampling": 10000,    # ops/sec for <10 bins
        "complex_sampling": 1000,    # ops/sec for >100 bins
        "cross_sampling": 500,       # ops/sec for cross coverage

        # Randomization baselines
        "simple_randomize": 10000,   # ops/sec for simple constraints
        "complex_randomize": 1000,   # ops/sec for complex constraints

        # RGM baselines
        "register_read": 50000,      # ops/sec
        "register_write": 50000,     # ops/sec
        "block_access": 10000,       # ops/sec
    }


# =============================================================================
# Exception Test Fixtures
# =============================================================================

@pytest.fixture(scope="session")
def exception_test_cases() -> Dict[str, List[Dict[str, Any]]]:
    """Provide test cases for exception handling tests."""
    return {
        "coverage": [
            {"exception": "CoverGroupError", "trigger": "duplicate_name"},
            {"exception": "CoverPointError", "trigger": "invalid_bins"},
            {"exception": "CrossError", "trigger": "invalid_coverpoint"},
            {"exception": "BinError", "trigger": "invalid_range"},
            {"exception": "DatabaseError", "trigger": "save_failure"},
            {"exception": "ReportError", "trigger": "invalid_format"},
        ],
        "rgm": [
            {"exception": "RegisterBlockError", "trigger": "duplicate_register"},
            {"exception": "RegisterError", "trigger": "invalid_offset"},
            {"exception": "FieldError", "trigger": "bit_overlap"},
            {"exception": "AccessError", "trigger": "invalid_access_type"},
            {"exception": "AdapterError", "trigger": "connection_failure"},
            {"exception": "MemoryMapError", "trigger": "address_conflict"},
        ],
        "randomizer": [
            {"exception": "RandomizationError", "trigger": "constraint_conflict"},
            {"exception": "ConstraintError", "trigger": "invalid_expression"},
            {"exception": "SolverError", "trigger": "no_solution"},
            {"exception": "SeedError", "trigger": "invalid_seed"},
            {"exception": "VariableError", "trigger": "invalid_type"},
        ],
    }


# =============================================================================
# Helper Functions
# =============================================================================

@pytest.fixture(scope="session")
def test_helpers():
    """Provide helper functions for tests."""
    class Helpers:
        @staticmethod
        def assert_exception_contains(exc_info, expected_substring: str):
            """Assert that exception message contains expected substring."""
            assert expected_substring.lower() in str(exc_info.value).lower(), \
                f"Expected '{expected_substring}' in exception message: {exc_info.value}"

        @staticmethod
        def count_covered_bins(covergroup) -> int:
            """Count total covered bins in a covergroup."""
            total = 0
            for cp in covergroup._coverpoints.values():
                total += cp.coverage
            return total

        @staticmethod
        def verify_performance(actual_ops: float, baseline: float, threshold: float = 0.1):
            """Verify performance is within acceptable threshold of baseline."""
            min_ops = baseline * (1.0 - threshold)
            assert actual_ops >= min_ops, \
                f"Performance {actual_ops} below baseline {baseline} by more than {threshold*100}%"

    return Helpers


# =============================================================================
# Benchmark Fixtures
# =============================================================================

@pytest.fixture(scope="session")
def benchmark_iterations():
    """Provide iteration counts for different benchmark types."""
    return {
        "quick": 100,
        "normal": 1000,
        "extended": 10000,
    }


@pytest.fixture(scope="function")
def benchmark_timer():
    """Provide a simple timer for manual benchmarking."""
    import time

    class Timer:
        def __init__(self):
            self.start_time = None
            self.end_time = None

        def start(self):
            self.start_time = time.perf_counter()

        def stop(self):
            self.end_time = time.perf_counter()

        @property
        def elapsed(self) -> float:
            if self.start_time is None or self.end_time is None:
                raise RuntimeError("Timer not started/stopped properly")
            return self.end_time - self.start_time

        @property
        def ops_per_sec(self, iterations: int) -> float:
            return iterations / self.elapsed if self.elapsed > 0 else 0

    return Timer


# =============================================================================
# Integration Test Fixtures
# =============================================================================

@pytest.fixture(scope="function")
def integrated_rgm_coverage():
    """Create an integrated RGM + Coverage test setup."""
    from rgm.core import RegisterBlock, Register, Field
    from rgm.utils import AccessType
    from coverage.core import CoverGroup, CoverPoint
    from sv_randomizer import Randomizable
    from sv_randomizer.core.variables import RandVar, VarType

    class IntegratedTestTransaction(Randomizable):
        def __init__(self):
            super().__init__()

            # RGM component
            self.block = RegisterBlock("TEST", 0x40000000)
            reg = Register("CTRL", 0x00, 32)
            reg.add_field(Field("mode", 0, 3, AccessType.RW, reset_value=0))
            reg.add_field(Field("enable", 3, 1, AccessType.RW, reset_value=0))
            self.block.add_register(reg)

            # Coverage component
            self.cg = CoverGroup("transaction_cg")
            cp = CoverPoint("mode_cp", "mode", bins={"modes": list(range(8))})
            self.cg.add_coverpoint(cp)

            # Add coverage to auto-sampling
            self.add_covergroup(self.cg)

            # Randomizable component
            self.mode = RandVar("mode", VarType.BIT, bit_width=3)
            self.enable = RandVar("enable", VarType.BIT, bit_width=1)

            # Add constraint
            self.add_constraint(lambda: self.mode.value < 5)

    return IntegratedTestTransaction()


# =============================================================================
# Markers for Slow Tests
# =============================================================================

def pytest_addoption(parser):
    """Add custom command line options."""
    parser.addoption(
        "--include-slow",
        action="store_true",
        default=False,
        help="Include slow tests in test run"
    )


def pytest_collection_modifyitems(config, items):
    """Modify collected tests based on markers and options."""
    if not config.getoption("--include-slow"):
        skip_slow = pytest.mark.skip(reason="Slow test skipped (use --include-slow to run)")
        for item in items:
            if "slow" in item.keywords:
                item.add_marker(skip_slow)
