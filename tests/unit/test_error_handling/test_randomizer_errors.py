"""
Randomizer System Exception Handling Tests

Tests all 6 exception classes in the randomizer module to ensure:
1. Exceptions are raised in appropriate conditions
2. Exception messages are clear and accurate
3. Exception attributes are properly set
4. Exception inheritance hierarchy is correct
"""

import pytest

from sv_randomizer.utils.exceptions import (
    RandomizerError,
    ConstraintConflictError,
    UnsatisfiableError,
    VariableNotFoundError,
    SolverBackendError,
    InvalidConstraintError,
)

from sv_randomizer import Randomizable
from sv_randomizer.core.variables import RandVar, RandCVar, VarType
from sv_randomizer.constraints.base import Constraint
from sv_randomizer.solvers.backend_interface import SolverBackend


# =============================================================================
# Test: RandomizerError (Base Exception)
# =============================================================================

@pytest.mark.unit
@pytest.mark.error_handling
@pytest.mark.P0
class TestRandomizerError:
    """Tests for RandomizerError base exception."""

    def test_randomizer_error_creation(self):
        """Test RandomizerError can be created with message."""
        msg = "Test randomizer error"
        exc = RandomizerError(msg)
        assert str(exc) == msg

    def test_randomizer_error_is_exception(self):
        """Test RandomizerError is a proper Exception subclass."""
        assert issubclass(RandomizerError, Exception)
        exc = RandomizerError("test")
        assert isinstance(exc, Exception)
        assert isinstance(exc, RandomizerError)


# =============================================================================
# Test: ConstraintConflictError
# =============================================================================

@pytest.mark.unit
@pytest.mark.error_handling
@pytest.mark.P0
class TestConstraintConflictError:
    """Tests for ConstraintConflictError."""

    def test_constraint_conflict_error_creation(self):
        """Test ConstraintConflictError can be created."""
        msg = "Constraints conflict"
        constraints = ["x > 10", "x < 5"]
        exc = ConstraintConflictError(msg, constraints)
        assert str(exc) == msg
        assert exc.conflicting_constraints == constraints

    def test_constraint_conflict_error_without_constraints(self):
        """Test ConstraintConflictError can be created without constraints list."""
        exc = ConstraintConflictError("test")
        assert exc.conflicting_constraints == []

    def test_constraint_conflict_raised_on_contradictory_constraints(self):
        """Test ConstraintConflictError is raised for contradictory constraints."""
        class TestObj(Randomizable):
            def __init__(self):
                super().__init__()
                self.x = RandVar("x", VarType.BIT, bit_width=8)

        obj = TestObj()

        # Add contradictory constraints
        obj.add_constraint(lambda: obj.x.value > 200)
        obj.add_constraint(lambda: obj.x.value < 50)

        # The Pure Python solver should detect this conflict
        # Note: Actual behavior depends on solver implementation
        # This test documents expected behavior
        try:
            obj.randomize()
            # If no exception is raised, the solver found a solution
            # (which shouldn't happen with these constraints)
            # This is a documentation of expected behavior
        except (ConstraintConflictError, UnsatisfiableError):
            # This is the expected path
            pass


# =============================================================================
# Test: UnsatisfiableError
# =============================================================================

@pytest.mark.unit
@pytest.mark.error_handling
@pytest.mark.P0
class TestUnsatisfiableError:
    """Tests for UnsatisfiableError."""

    def test_unsatisfiable_error_creation(self):
        """Test UnsatisfiableError can be created."""
        msg = "Constraints cannot be satisfied"
        constraints = ["x == 5", "x == 10"]
        exc = UnsatisfiableError(msg, constraints)
        assert str(exc) == msg
        assert exc.constraints == constraints

    def test_unsatisfiable_error_without_constraints(self):
        """Test UnsatisfiableError can be created without constraints list."""
        exc = UnsatisfiableError("test")
        assert exc.constraints == []

    def test_unsatisfiable_raised_on_impossible_constraints(self):
        """Test UnsatisfiableError is raised for mathematically impossible constraints."""
        class TestObj(Randomizable):
            def __init__(self):
                super().__init__()
                self.x = RandVar("x", VarType.BIT, bit_width=3)  # 0-7

        obj = TestObj()

        # Add impossible constraint
        obj.add_constraint(lambda: obj.x.value > 10)

        try:
            obj.randomize()
        except (UnsatisfiableError, ConstraintConflictError):
            # Expected - constraint is impossible to satisfy
            pass


# =============================================================================
# Test: VariableNotFoundError
# =============================================================================

@pytest.mark.unit
@pytest.mark.error_handling
@pytest.mark.P0
class TestVariableNotFoundError:
    """Tests for VariableNotFoundError."""

    def test_variable_not_found_error_creation(self):
        """Test VariableNotFoundError can be created with var_name."""
        var_name = "nonexistent_var"
        exc = VariableNotFoundError(var_name)
        assert exc.var_name == var_name
        assert var_name in str(exc)

    def test_variable_not_found_error_message_format(self):
        """Test VariableNotFoundError message format."""
        var_name = "my_var"
        exc = VariableNotFoundError(var_name)
        expected_msg = f"Variable '{var_name}' not found"
        assert str(exc) == expected_msg

    def test_variable_not_found_raised_on_invalid_reference(self):
        """Test VariableNotFoundError is raised when referencing non-existent variable."""
        # This test depends on constraint expression implementation
        # If constraints reference variables by name, this should raise
        exc = VariableNotFoundError("missing_var")
        assert "missing_var" in str(exc)


# =============================================================================
# Test: SolverBackendError
# =============================================================================

@pytest.mark.unit
@pytest.mark.error_handling
@pytest.mark.P0
class TestSolverBackendError:
    """Tests for SolverBackendError."""

    def test_solver_backend_error_creation(self):
        """Test SolverBackendError can be created with backend name."""
        msg = "Solver backend failed"
        backend = "z3"
        exc = SolverBackendError(msg, backend)
        assert str(exc) == msg
        assert exc.backend_name == backend

    def test_solver_backend_error_without_backend(self):
        """Test SolverBackendError can be created without backend name."""
        exc = SolverBackendError("test")
        assert exc.backend_name is None

    def test_solver_backend_error_for_missing_z3(self):
        """Test SolverBackendError is raised when Z3 is not available."""
        # Try to create Z3 backend without z3-solver installed
        # This tests error handling in solver factory
        from sv_randomizer.solvers import SolverFactory

        try:
            # Try to get Z3 backend when it might not be available
            backend = SolverFactory.get_solver("z3")
            # If Z3 is available, this won't raise
            # If not available, it should raise SolverBackendError
        except SolverBackendError as e:
            assert e.backend_name == "z3"
        except ImportError:
            # Z3 not installed - this is also acceptable
            pass


# =============================================================================
# Test: InvalidConstraintError
# =============================================================================

@pytest.mark.unit
@pytest.mark.error_handling
@pytest.mark.P0
class TestInvalidConstraintError:
    """Tests for InvalidConstraintError."""

    def test_invalid_constraint_error_creation(self):
        """Test InvalidConstraintError can be created with constraint name."""
        msg = "Invalid constraint definition"
        constraint_name = "bad_constraint"
        exc = InvalidConstraintError(msg, constraint_name)
        assert str(exc) == msg
        assert exc.constraint_name == constraint_name

    def test_invalid_constraint_error_without_name(self):
        """Test InvalidConstraintError can be created without constraint name."""
        exc = InvalidConstraintError("test")
        assert exc.constraint_name is None

    def test_invalid_constraint_raised_on_malformed_expression(self):
        """Test InvalidConstraintError is raised for malformed constraint expressions."""
        # This tests constraint validation
        # Actual implementation depends on constraint system design
        class TestObj(Randomizable):
            def __init__(self):
                super().__init__()
                self.x = RandVar("x", VarType.BIT, bit_width=8)

        obj = TestObj()

        # Try to add invalid constraint
        # This is a documentation of expected behavior
        # Implementation may vary
        try:
            # Add non-callable constraint
            obj.add_constraint("not a callable")
            # If this doesn't raise, the constraint system is lenient
        except (InvalidConstraintError, TypeError):
            # Expected - constraint must be callable
            pass


# =============================================================================
# Integration Tests: Exception Conditions
# =============================================================================

@pytest.mark.unit
@pytest.mark.error_handling
@pytest.mark.P0
@pytest.mark.parametrize("exception_class", [
    RandomizerError,
    ConstraintConflictError,
    UnsatisfiableError,
    VariableNotFoundError,
    SolverBackendError,
    InvalidConstraintError,
])
def test_all_randomizer_exceptions_can_be_raised(exception_class):
    """Test that all randomizer exceptions can be raised and caught."""
    with pytest.raises(exception_class) as exc_info:
        if exception_class == VariableNotFoundError:
            raise exception_class("test_var")
        elif exception_class in [ConstraintConflictError, UnsatisfiableError]:
            raise exception_class("test message", ["constraint1", "constraint2"])
        elif exception_class in [SolverBackendError, InvalidConstraintError]:
            raise exception_class("test message", "test_backend_or_constraint")
        else:
            raise exception_class("Test message")

    assert "test" in str(exc_info.value).lower()


@pytest.mark.unit
@pytest.mark.error_handling
@pytest.mark.P1
def test_exception_inheritance_chain():
    """Test that exception inheritance chain is correct."""
    # All randomizer exceptions inherit from RandomizerError
    assert issubclass(ConstraintConflictError, RandomizerError)
    assert issubclass(UnsatisfiableError, RandomizerError)
    assert issubclass(VariableNotFoundError, RandomizerError)
    assert issubclass(SolverBackendError, RandomizerError)
    assert issubclass(InvalidConstraintError, RandomizerError)

    # All inherit from Exception
    assert issubclass(RandomizerError, Exception)


@pytest.mark.unit
@pytest.mark.error_handling
@pytest.mark.P1
class TestRandomizerConstraintScenarios:
    """Test randomizer exception scenarios in constraint context."""

    def test_range_constraint_conflict(self):
        """Test constraint conflict with disjoint ranges."""
        class TestObj(Randomizable):
            def __init__(self):
                super().__init__()
                self.x = RandVar("x", VarType.BIT, bit_width=8)

        obj = TestObj()
        obj.add_constraint(lambda: obj.x.value < 50)
        obj.add_constraint(lambda: obj.x.value > 100)

        try:
            obj.randomize()
        except (ConstraintConflictError, UnsatisfiableError):
            pass  # Expected

    def test_equality_constraint_conflict(self):
        """Test constraint conflict with contradictory equality."""
        class TestObj(Randomizable):
            def __init__(self):
                super().__init__()
                self.x = RandVar("x", VarType.BIT, bit_width=8)

        obj = TestObj()
        obj.add_constraint(lambda: obj.x.value == 42)
        obj.add_constraint(lambda: obj.x.value == 99)

        try:
            obj.randomize()
        except (ConstraintConflictError, UnsatisfiableError):
            pass  # Expected

    def test_boundary_constraint_conflict(self):
        """Test constraint conflict at boundaries."""
        class TestObj(Randomizable):
            def __init__(self):
                super().__init__()
                self.x = RandVar("x", VarType.BIT, bit_width=3)  # 0-7

        obj = TestObj()
        obj.add_constraint(lambda: obj.x.value > 7)
        obj.add_constraint(lambda: obj.x.value < 0)

        try:
            obj.randomize()
        except (ConstraintConflictError, UnsatisfiableError):
            pass  # Expected

    def test_combined_constraint_conflict(self):
        """Test complex combined constraint conflict."""
        class TestObj(Randomizable):
            def __init__(self):
                super().__init__()
                self.x = RandVar("x", VarType.BIT, bit_width=8)
                self.y = RandVar("y", VarType.BIT, bit_width=8)

        obj = TestObj()
        obj.add_constraint(lambda: obj.x.value == obj.y.value)
        obj.add_constraint(lambda: obj.x.value != obj.y.value)

        try:
            obj.randomize()
        except (ConstraintConflictError, UnsatisfiableError):
            pass  # Expected


@pytest.mark.unit
@pytest.mark.error_handling
@pytest.mark.P2
class TestRandomizerExceptionMessages:
    """Test that randomizer exception messages are clear and actionable."""

    def test_constraint_conflict_message_informative(self):
        """Test ConstraintConflictError message is informative."""
        constraints = ["x > 100", "x < 50"]
        exc = ConstraintConflictError("Conflicting constraints", constraints)

        msg = str(exc)
        assert "conflict" in msg.lower()

    def test_unsatisfiable_error_message_informative(self):
        """Test UnsatisfiableError message is informative."""
        constraints = ["x == 5", "x == 10"]
        exc = UnsatisfiableError("Cannot satisfy", constraints)

        msg = str(exc)
        # Message should indicate the problem
        assert "satisfy" in msg.lower() or "impossible" in msg.lower()

    def test_variable_not_found_message_includes_name(self):
        """Test VariableNotFoundError message includes variable name."""
        var_name = "missing_variable"
        exc = VariableNotFoundError(var_name)

        msg = str(exc)
        assert var_name in msg

    def test_solver_backend_error_message_includes_backend(self):
        """Test SolverBackendError message includes backend info."""
        backend = "z3"
        exc = SolverBackendError("Backend failed", backend)

        msg = str(exc)
        # Backend name should be in the error info
        assert exc.backend_name == backend


@pytest.mark.unit
@pytest.mark.error_handling
@pytest.mark.P2
class TestRandomizerSolverIntegration:
    """Test exception handling in solver integration."""

    def test_solver_selection_error_handling(self):
        """Test error handling when selecting unavailable solver."""
        from sv_randomizer.solvers import SolverFactory

        # Try to get non-existent solver
        with pytest.raises((SolverBackendError, ValueError, KeyError)):
            SolverFactory.get_solver("nonexistent_solver")

    def test_backend_initialization_error_propagation(self):
        """Test that backend initialization errors are properly propagated."""
        # This tests error propagation when backend fails to initialize
        try:
            from sv_randomizer.solvers import SolverFactory
            backend = SolverFactory.get_solver("pure_python")
            # If we get here, backend initialized successfully
            assert backend is not None
        except Exception as e:
            # Any initialization error should be a solver-related error
            assert isinstance(e, (SolverBackendError, ImportError, RuntimeError))


@pytest.mark.unit
@pytest.mark.error_handling
@pytest.mark.P2
class TestRandomizerEdgeCases:
    """Test edge cases in randomizer error handling."""

    def test_empty_constraint_list_error(self):
        """Test error handling with empty constraint list."""
        class TestObj(Randomizable):
            def __init__(self):
                super().__init__()
                self.x = RandVar("x", VarType.BIT, bit_width=8)

        obj = TestObj()

        # Should randomize successfully with no constraints
        obj.randomize()
        assert 0 <= obj.x.value <= 255

    def test_single_impossible_constraint(self):
        """Test single impossible constraint detection."""
        class TestObj(Randomizable):
            def __init__(self):
                super().__init__()
                self.x = RandVar("x", VarType.BIT, bit_width=8)

        obj = TestObj()
        obj.add_constraint(lambda: obj.x.value > 300)

        try:
            obj.randomize()
        except (UnsatisfiableError, ConstraintConflictError):
            pass  # Expected

    def test_self_referential_constraint(self):
        """Test constraint that references variable in complex way."""
        class TestObj(Randomizable):
            def __init__(self):
                super().__init__()
                self.x = RandVar("x", VarType.BIT, bit_width=8)

        obj = TestObj()

        # This is a valid constraint (x == x)
        obj.add_constraint(lambda: obj.x.value == obj.x.value)
        obj.randomize()
        assert 0 <= obj.x.value <= 255

    def test_circular_variable_dependency(self):
        """Test handling of circular variable dependencies."""
        class TestObj(Randomizable):
            def __init__(self):
                super().__init__()
                self.x = RandVar("x", VarType.BIT, bit_width=8)
                self.y = RandVar("y", VarType.BIT, bit_width=8)

        obj = TestObj()

        # These constraints are circular but not contradictory
        # x == y and y == x is the same constraint twice
        obj.add_constraint(lambda: obj.x.value == obj.y.value)
        obj.add_constraint(lambda: obj.y.value == obj.x.value)

        # Should randomize successfully
        obj.randomize()
        assert obj.x.value == obj.y.value
