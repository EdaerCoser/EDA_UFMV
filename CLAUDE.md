# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

---

## Project Overview

**EDA_UFVM** is a Python-based FPGA/prototype verification framework that brings SystemVerilog verification capabilities to the Python ecosystem. The project consists of two independent top-level modules:

- **`sv_randomizer/`** - Core randomization framework with rand/randc variables, constraints, and dual solver architecture
- **`coverage/`** - SystemVerilog-compatible functional coverage system with CoverGroup/CoverPoint/Cross support

**Current Version**: v0.2.0 (Coverage System Complete)

---

## Common Development Commands

### Running Tests

```bash
# Run coverage system tests (141 tests)
python run_coverage_tests.py

# Run legacy randomization tests (36 tests)
python -m pytest tests/legacy/ -v

# Run specific test file
python -m pytest tests/test_coverage/test_covergroup.py -v

# Run with coverage reporting
python -m pytest tests/coverage/ --cov=coverage --cov-report=html
```

**Important**: Use `run_coverage_tests.py` for coverage tests because it disables the pytest-qt plugin which can cause import errors on Windows (QtCore DLL load failures).

### Development Setup

```bash
# Install in development mode
pip install -e .

# Install with Z3 solver backend (optional)
pip install -e ".[z3]"

# Install with development dependencies
pip install -e ".[dev]"
```

### Regression Testing

```bash
# Use the built-in test agent
python .claude/skills/test-agent/runner.py --all
```

---

## Module Architecture

### Design Patterns

This codebase consistently uses several design patterns across both modules:

| Pattern | Application | Example |
|:---|:---|:---|
| **Strategy Pattern** | Pluggable backends | SolverBackend (PurePython/Z3), CoverageDatabase (Memory/File) |
| **Decorator Pattern** | Clean API syntax | `@rand`, `@randc`, `@constraint`, `@covergroup`, `@coverpoint` |
| **Factory Pattern** | Object creation | SolverFactory, DatabaseFactory, ReportFactory |
| **Observer Pattern** | Callbacks | pre_randomize()/post_randomize(), sampling callbacks |
| **Composition Pattern** | Hierarchical structure | CompoundConstraint, CoverGroup containing CoverPoints |

### Module Independence

**Critical**: The `coverage/` module is now an independent top-level module (not under `sv_randomizer/`). This separation provides:
- Reusability outside EDA_UFVM
- Cleaner module boundaries
- Independent versioning

Import paths:
- Coverage system: `from coverage.core import CoverGroup, CoverPoint, Cross`
- Randomization: `from sv_randomizer import Randomizable, RandVar, RandCVar`

### sv_randomizer Module Structure

```
sv_randomizer/
├── core/              # Core framework
│   ├── randomizable.py    # Randomizable base class
│   ├── variables.py       # RandVar, RandCVar
│   └── seeding.py         # Seed management
├── constraints/       # Constraint system
│   ├── base.py            # Constraint base classes
│   ├── expressions.py     # Expression AST (VariableExpr, BinaryExpr, etc.)
│   ├── builders.py        # Constraint builders
│   ├── inside.py          # InsideConstraint (range constraints)
│   └── dist.py            # DistConstraint (weighted distribution)
├── solvers/           # Solver backends
│   ├── backend_interface.py   # SolverBackend interface
│   ├── pure_python.py         # Pure Python solver (no dependencies)
│   ├── z3_backend.py          # Z3 SMT solver (industrial grade)
│   └── solver_factory.py      # Factory for solver creation
├── api/               # User-facing API
│   ├── decorators.py      # @rand, @randc, @constraint decorators
│   └── dsl.py             # DSL syntax sugar (inside(), dist(), VarProxy)
└── utils/             # Utilities
    └── exceptions.py      # Custom exceptions
```

### coverage Module Structure

```
coverage/
├── core/              # Core coverage classes
│   ├── bin.py             # 6 bin types (ValueBin, RangeBin, WildcardBin, AutoBin, IgnoreBin, IllegalBin)
│   ├── coverpoint.py      # CoverPoint implementation
│   ├── covergroup.py      # CoverGroup container
│   └── cross.py           # Cross coverage (Cartesian product)
├── database/          # Database backends
│   ├── base.py            # CoverageDatabase interface
│   ├── memory_db.py       # In-memory database (fast, no persistence)
│   ├── file_db.py         # File-persistent database (JSON format)
│   └── factory.py         # DatabaseFactory
├── formatters/        # Report generators
│   ├── base.py            # CoverageReport interface
│   ├── html_report.py     # HTML reports (interactive)
│   ├── json_report.py     # JSON reports (CI/CD integration)
│   ├── ucis_report.py     # UCIS format (IEEE 1687 standard for EDA)
│   └── factory.py         # ReportFactory
└── api/               # SystemVerilog-style decorators
    └── decorators.py      # @covergroup, @coverpoint, @cross decorators
```

---

## Integration Between Modules

The coverage system integrates with `Randomizable` through automatic sampling:

```python
from sv_randomizer import Randomizable
from coverage.core import CoverGroup, CoverPoint

class MyTransaction(Randomizable):
    def __init__(self):
        super().__init__()

        # Add coverage group
        cg = CoverGroup("my_cg")
        cg.add_coverpoint(CoverPoint("cp", "value", bins={"values": [1,2,3]}))
        self.add_covergroup(cg)

# Usage
txn = MyTransaction()
txn.randomize()  # Automatically samples coverage
coverage = txn.get_total_coverage()  # Returns coverage percentage
```

**Integration Point**: `sv_randomizer/core/randomizable.py` imports `from coverage.core import CoverGroup` and calls `_sample_coverage()` in `post_randomize()` when `_coverage_auto_sample` is True.

---

## Architecture Principles

### Dual Backend Strategy

Both solvers and databases support pluggable backends:

**Solvers**:
- `pure_python` - No external dependencies, ~10K randomizations/sec
- `z3` - Industrial-grade SMT solver, better constraint handling

**Databases**:
- `memory` - Fast in-memory, suitable for single-run tests
- `file` - JSON persistence, supports merging multiple runs

### Lazy Loading for Performance

Large Cross coverage uses lazy loading to avoid generating all Cartesian products upfront:
```python
# Only generates bins on first access
def sample(self, **kwargs):
    if not self._bins_loaded:
        self._load_bins()
    # ... sampling logic
```

### Expression AST System

Constraints use an AST (Abstract Syntax Tree) representation:
- `VariableExpr` - Variable references
- `ConstantExpr` - Literal values
- `UnaryExpr` - NOT, negation
- `BinaryExpr` - AND, OR, comparisons, arithmetic
- `InsideConstraint` - Range/value membership
- `DistConstraint` - Weighted distributions

---

## Testing Strategy

### Test Structure

```
tests/
├── legacy/           # Original randomization tests (36 tests)
├── test_coverage/    # Coverage system tests (141 tests)
│   ├── test_bins.py
│   ├── test_coverpoint.py
│   ├── test_covergroup.py
│   ├── test_cross_and_reports.py
│   ├── test_database.py
│   ├── integration/
│   │   ├── test_integration.py
│   │   └── test_performance.py
│   └── examples/
│       └── test_examples.py
├── integration/      # Cross-module integration tests
├── performance/      # Performance benchmarks
└── unit/            # Legacy unit tests
```

### Performance Benchmarks

Current performance (v0.2.0):
- Simple sampling (<10 bins): ~246K samples/sec
- Complex sampling (>100 bins): ~84.5K samples/sec
- Target requirements: >10K/sec (simple), >1K/sec (complex)

---

## Version History

- **v0.1.0** (2026-02) - Basic randomization framework, 36 tests
- **v0.2.0** (Current) - Functional coverage system, 141 tests total

### Planned Versions

- **v0.3.0** - Register model system (RGM)
- **v0.4.0** - Coverage-guided randomization
- **v0.5.0** - DUT configuration parsing (Verilog → Python)
- **v1.0.0** - Complete platform with PyPI release

See [ROADMAP.md](docs/development/ROADMAP.md) for details.

---

## Common Issues and Solutions

### ImportError with pytest-qt

**Error**: `ImportError: DLL load failed while importing QtCore`

**Solution**: Use `python run_coverage_tests.py` instead of direct pytest, which disables the pytest-qt plugin.

### Import Path Updates

After the v0.2.0 restructuring, all coverage imports changed:
- Old: `from sv_randomizer.coverage.*`
- New: `from coverage.*`

If you see import errors, check that imports use the new paths.

---

## Development Guidelines

### Code Style

- Use type hints for public APIs
- Follow SystemVerilog terminology for coverage concepts (covergroup, coverpoint, bins)
- Maintain separation of concerns: core logic vs. API vs. database
- Use abstract base classes for pluggable components

### Adding New Features

1. **New Bin Type**: Extend `coverage/core/bin.py`, add tests in `test_bins.py`
2. **New Solver**: Implement `SolverBackend` interface, register in `SolverFactory`
3. **New Report Format**: Implement `CoverageReport` interface, register in `ReportFactory`
4. **New Database Backend**: Implement `CoverageDatabase` interface, register in `DatabaseFactory`

### Testing Requirements

- Unit tests for all new classes (>80% coverage target)
- Integration tests for cross-module features
- Performance tests for optimization work
- Example code for user-facing features

---

## Key Files to Understand

**For randomization framework**:
1. `sv_randomizer/core/randomizable.py` - Core randomization orchestration
2. `sv_randomizer/solvers/pure_python.py` - Constraint solving logic
3. `sv_randomizer/constraints/expressions.py` - AST representation

**For coverage system**:
1. `coverage/core/covergroup.py` - Coverage orchestration
2. `coverage/core/bin.py` - Bin type implementations
3. `coverage/core/cross.py` - Cartesian product calculation
4. `coverage/database/factory.py` - Database backend selection
5. `docs/product/SYSTEMVERILOG_COVERAGE_GUIDE.md` - SystemVerilog to Python migration guide

**For integration**:
1. `sv_randomizer/core/randomizable.py` (lines 62-509) - Coverage auto-sampling integration
2. `examples/coverage/basic_coverage.py` - Usage examples
3. `examples/coverage/advanced_coverage.py` - Complex scenarios
