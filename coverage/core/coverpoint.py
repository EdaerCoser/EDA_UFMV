"""
CoverPoint Implementation

Implements a single coverage point that samples a variable or expression
and tracks which bins have been hit.
"""

from typing import Any, Dict, List, Optional, Callable, Union
from enum import Enum

from .bin import (
    Bin, ValueBin, RangeBin, WildcardBin, AutoBin,
    IgnoreBin, IllegalBin, IllegalBinHitError
)


class BinType(Enum):
    """Enumeration of bin types."""
    VALUE = "value"
    RANGE = "range"
    WILDCARD = "wildcard"
    AUTO = "auto"
    IGNORE = "ignore"
    ILLEGAL = "illegal"


class CoverPoint:
    """
    CoverPoint implementation.

    Corresponds to SystemVerilog coverpoint:

        coverpoint cp;
            bins low[] = {[0:127]};
            bins mid[] = {[128:255]};
            bins high[] = {[256:511]};
            ignore_bins reserved[] = {0};
            illegal_bins error[] = {512};
    """

    def __init__(
        self,
        name: str,
        sample_expr: Union[str, Callable],
        bins: Optional[Dict[str, Any]] = None,
        auto_bin_max: Optional[int] = None,
        weight: float = 1.0,
        comment: str = ""
    ):
        """
        Initialize a CoverPoint.

        Args:
            name: CoverPoint name (corresponds to 'coverpoint name;')
            sample_expr: Sample expression - can be:
                - str: Variable name (e.g., "addr")
                - callable: Function that returns sampled value
            bins: Bin definition dictionary with keys:
                - "values": list of single values -> ValueBin
                - "ranges": list of [low, high] pairs -> RangeBin
                - "wildcards": list of wildcard patterns -> WildcardBin
                - "auto": number of auto bins -> AutoBin
                - "ignore": list of values to ignore -> IgnoreBin
                - "illegal": list of illegal values -> IllegalBin
            auto_bin_max: Maximum number of auto bins (default: 64)
            weight: CoverPoint weight for weighted coverage (default: 1.0)
            comment: Documentation comment
        """
        self.name = name
        self._sample_expr = sample_expr
        self._weight = weight
        self._comment = comment

        # Bin management
        self._bins: Dict[str, Bin] = {}
        self._auto_bin_max = auto_bin_max or 64
        self._ignore_bins: List[Bin] = []
        self._illegal_bins: List[Bin] = []

        # Initialize bins if provided
        if bins:
            self._initialize_bins(bins)

        # State
        self._enabled = True
        self._parent = None  # Set by parent CoverGroup
        self._database = None  # Set by set_database()

        # Statistics
        self._sample_count = 0

    def _initialize_bins(self, bins: Dict[str, Any]) -> None:
        """
        Initialize bins from bin definition dictionary.

        Supports SystemVerilog-style bin definitions:

        Args:
            bins: Dictionary with bin definitions
        """
        # Value bins: "values": [1, 2, 3]
        if 'values' in bins:
            for i, value in enumerate(bins['values']):
                bin_name = f"value_{i}"
                self._bins[bin_name] = ValueBin(bin_name, value)

        # Range bins: "ranges": [[0, 10], [20, 30]]
        if 'ranges' in bins:
            for i, (low, high) in enumerate(bins['ranges']):
                bin_name = f"range_{i}"
                self._bins[bin_name] = RangeBin(bin_name, low, high)

        # Wildcard bins: "wildcards": ["8???", "10??"]
        if 'wildcards' in bins:
            for i, pattern in enumerate(bins['wildcards']):
                bin_name = f"wildcard_{i}"
                self._bins[bin_name] = WildcardBin(bin_name, pattern)

        # Auto bins: "auto": 16
        if 'auto' in bins:
            num_bins = bins['auto']
            self._create_auto_bins(num_bins)

        # Ignore bins: "ignore": [100, 200]
        if 'ignore' in bins:
            for value in bins['ignore']:
                self._ignore_bins.append(IgnoreBin(f"ignore_{value}", value))

        # Illegal bins: "illegal": [255]
        if 'illegal' in bins:
            for value in bins['illegal']:
                self._illegal_bins.append(IllegalBin(f"illegal_{value}", value))

    def _create_auto_bins(self, num_bins: int) -> None:
        """
        Create auto bins that divide the range into equal-width bins.

        Args:
            num_bins: Number of bins to create
        """
        for i in range(num_bins):
            bin_name = f"auto_{i}"
            self._bins[bin_name] = AutoBin(bin_name, i, num_bins)

    def sample(self, **kwargs) -> None:
        """
        Sample the current value and update bin hit counts.

        Args:
            **kwargs: Variable name to value mapping

        Raises:
            IllegalBinHitError: If sample hits an illegal bin
        """
        if not self._enabled:
            return

        # Get sampled value
        if callable(self._sample_expr):
            sample_value = self._sample_expr(kwargs)
        else:
            sample_value = kwargs.get(self._sample_expr)

        if sample_value is None:
            return

        # Check illegal bins first
        for illegal_bin in self._illegal_bins:
            if illegal_bin.match(sample_value):
                raise IllegalBinHitError(
                    f"Value {sample_value} hit illegal bin '{illegal_bin.name}' "
                    f"in coverpoint '{self.name}'"
                )

        # Check ignore bins
        for ignore_bin in self._ignore_bins:
            if ignore_bin.match(sample_value):
                return  # Skip sampling

        # Match and update bins
        hit = False
        for bin in self._bins.values():
            if bin.match(sample_value):
                bin.increment_hit()
                hit = True
                break

        self._sample_count += 1

        # Update database if set
        if self._database:
            self._database.record_sample(
                self.name, sample_value,
                self._parent.name if self._parent else ""
            )

    def get_coverage(self) -> float:
        """
        Calculate coverage percentage.

        Returns:
            Coverage percentage (0.0 - 100.0)
        """
        if not self._bins:
            return 100.0

        total_bins = len(self._bins)
        covered_bins = sum(1 for bin in self._bins.values() if bin.get_hit_count() > 0)

        return (covered_bins / total_bins) * 100.0

    def get_weighted_coverage(self) -> float:
        """
        Calculate weighted coverage.

        Returns:
            Weighted coverage percentage
        """
        return self.get_coverage() * self._weight

    def get_bin_counts(self) -> tuple[int, int]:
        """
        Get bin count statistics.

        Returns:
            Tuple of (total_bins, covered_bins)
        """
        total = len(self._bins)
        covered = sum(1 for bin in self._bins.values() if bin.get_hit_count() > 0)
        return total, covered

    def get_coverage_details(self) -> Dict[str, Any]:
        """
        Get detailed coverage information.

        Returns:
            Dictionary with coverage details
        """
        return {
            'name': self.name,
            'coverage': self.get_coverage(),
            'weighted_coverage': self.get_weighted_coverage(),
            'weight': self._weight,
            'sample_count': self._sample_count,
            'total_bins': len(self._bins),
            'covered_bins': sum(1 for b in self._bins.values() if b.get_hit_count() > 0),
            'bins': {
                name: {
                    'type': bin.__class__.__name__,
                    'hit_count': bin.get_hit_count(),
                    'definition': str(bin)
                }
                for name, bin in self._bins.items()
            }
        }

    def is_enabled(self) -> bool:
        """Check if sampling is enabled for this coverpoint."""
        return self._enabled

    def enable(self) -> None:
        """Enable sampling for this coverpoint."""
        self._enabled = True

    def disable(self) -> None:
        """Disable sampling for this coverpoint."""
        self._enabled = False

    def _set_parent(self, parent) -> None:
        """
        Set parent CoverGroup (internal use).

        Args:
            parent: Parent CoverGroup instance
        """
        self._parent = parent

    def set_database(self, database) -> None:
        """
        Set coverage database (internal use).

        Args:
            database: CoverageDatabase instance
        """
        self._database = database

    def __repr__(self) -> str:
        return (f"CoverPoint(name='{self.name}', coverage={self.get_coverage():.2f}%, "
                f"samples={self._sample_count}, bins={len(self._bins)})")
