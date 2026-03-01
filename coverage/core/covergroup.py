"""
CoverGroup Implementation

Implements a coverage group that organizes coverpoints and cross coverage.
Corresponds to SystemVerilog covergroup.
"""

from typing import Dict, List, Optional, Callable, Any

from .coverpoint import CoverPoint


class CoverGroup:
    """
    CoverGroup implementation.

    Corresponds to SystemVerilog covergroup:

        covergroup cg @(posedge clk);
            coverpoint cp;
            cross cp_cross;
        endgroup

    Manages coverpoints and cross coverage, coordinates sampling,
    and calculates overall coverage.
    """

    def __init__(
        self,
        name: str,
        sample_event: Optional[Callable[[], Any]] = None,
        auto_sample: bool = True
    ):
        """
        Initialize a CoverGroup.

        Args:
            name: CoverGroup name (corresponds to 'covergroup name;')
            sample_event: Optional sampling event function that returns values
                        (corresponds to '@(event)' in SV)
            auto_sample: Whether to automatically sample with Randomizable
        """
        self.name = name
        self._sample_event = sample_event
        self._auto_sample = auto_sample

        # Core components
        self._coverpoints: Dict[str, CoverPoint] = {}
        self._crosses: Dict[str, Any] = {}  # Cross objects (to be implemented in M3)
        self._covergroups: Dict[str, 'CoverGroup'] = {}  # Nested support

        # Sampling callbacks (Observer pattern)
        self._pre_sample_callbacks: List[Callable] = []
        self._post_sample_callbacks: List[Callable] = []

        # Database backend (Strategy pattern)
        self._database = None

        # State
        self._sampling_enabled = True
        self._instance_count = 0

    def add_coverpoint(self, coverpoint: CoverPoint) -> None:
        """
        Add a coverpoint to this covergroup.

        Args:
            coverpoint: CoverPoint instance to add
        """
        self._coverpoints[coverpoint.name] = coverpoint
        coverpoint._set_parent(self)

        # Propagate database to coverpoint
        if self._database:
            coverpoint.set_database(self._database)

    def add_cross(self, cross) -> None:
        """
        Add cross coverage to this covergroup.

        Args:
            cross: Cross instance to add (to be implemented in M3)
        """
        self._crosses[cross.name] = cross
        cross._set_parent(self)

    def sample(self, **kwargs) -> None:
        """
        Trigger sampling for all coverpoints and crosses.

        Args:
            **kwargs: Variable name to value mapping
        """
        if not self._sampling_enabled:
            return

        # Pre-sample callbacks
        for callback in self._pre_sample_callbacks:
            callback(self, kwargs)

        # Call sample event if provided
        if self._sample_event:
            sample_values = self._sample_event()
            if isinstance(sample_values, dict):
                kwargs.update(sample_values)

        # Sample all coverpoints
        for coverpoint in self._coverpoints.values():
            if coverpoint.is_enabled():
                coverpoint.sample(**kwargs)

        # Sample all crosses
        for cross in self._crosses.values():
            if cross.is_enabled():
                cross.sample(**kwargs)

        # Post-sample callbacks
        for callback in self._post_sample_callbacks:
            callback(self, kwargs)

        self._instance_count += 1

    def get_coverage(self) -> float:
        """
        Calculate total coverage percentage.

        Returns:
            Overall coverage percentage (0.0 - 100.0)
        """
        total_bins = 0
        covered_bins = 0

        # CoverPoint coverage
        for cp in self._coverpoints.values():
            cp_total, cp_covered = cp.get_bin_counts()
            total_bins += cp_total
            covered_bins += cp_covered

        # Cross coverage (to be implemented in M3)
        for cross in self._crosses.values():
            cross_total, cross_covered = cross.get_bin_counts()
            total_bins += cross_total
            covered_bins += cross_covered

        if total_bins == 0:
            return 100.0  # Empty covergroup is 100% covered

        return (covered_bins / total_bins) * 100.0

    def get_coverage_details(self) -> Dict[str, Any]:
        """
        Get detailed coverage information.

        Returns:
            Dictionary with comprehensive coverage details
        """
        return {
            'name': self.name,
            'coverage': self.get_coverage(),
            'sample_count': self._instance_count,
            'coverpoints': {
                name: cp.get_coverage_details()
                for name, cp in self._coverpoints.items()
            },
            'crosses': {
                name: cross.get_coverage_details()
                for name, cross in self._crosses.items()
            }
        }

    def register_pre_sample(self, callback: Callable) -> None:
        """
        Register a pre-sample callback.

        Args:
            callback: Function to call before sampling
        """
        self._pre_sample_callbacks.append(callback)

    def register_post_sample(self, callback: Callable) -> None:
        """
        Register a post-sample callback.

        Args:
            callback: Function to call after sampling
        """
        self._post_sample_callbacks.append(callback)

    def set_database(self, database) -> None:
        """
        Set coverage database for this covergroup.

        Args:
            database: CoverageDatabase instance
        """
        self._database = database
        # Propagate to all coverpoints
        for cp in self._coverpoints.values():
            cp.set_database(database)

    def enable_sampling(self) -> None:
        """Enable sampling for this covergroup."""
        self._sampling_enabled = True

    def disable_sampling(self) -> None:
        """Disable sampling for this covergroup."""
        self._sampling_enabled = False

    def is_sampling_enabled(self) -> bool:
        """Check if sampling is enabled."""
        return self._sampling_enabled

    def get_coverpoint(self, name: str) -> Optional[CoverPoint]:
        """
        Get a coverpoint by name.

        Args:
            name: Coverpoint name

        Returns:
            CoverPoint instance or None if not found
        """
        return self._coverpoints.get(name)

    def list_coverpoints(self) -> List[str]:
        """
        List all coverpoint names.

        Returns:
            List of coverpoint names
        """
        return list(self._coverpoints.keys())

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - auto-save and cleanup."""
        if self._database:
            self._database.save()
        return False

    def __repr__(self) -> str:
        return (f"CoverGroup(name='{self.name}', coverage={self.get_coverage():.2f}%, "
                f"coverpoints={len(self._coverpoints)}, crosses={len(self._crosses)})")
