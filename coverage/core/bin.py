"""
Bin System for Coverage Points

Defines the abstract Bin interface and concrete implementations
for different bin types (value, range, wildcard, auto, ignore, illegal).
"""

from abc import ABC, abstractmethod
from typing import Any
import re


class Bin(ABC):
    """
    Abstract base class for all Bin types.

    All bin types must implement match() and increment_hit() methods.
    Corresponds to SystemVerilog bin functionality.
    """

    def __init__(self, name: str):
        """
        Initialize a Bin.

        Args:
            name: Bin identifier name
        """
        self.name = name
        self._hit_count = 0

    @abstractmethod
    def match(self, value: Any) -> bool:
        """
        Check if a value matches this bin.

        Args:
            value: The value to check

        Returns:
            True if the value matches this bin
        """
        pass

    def increment_hit(self) -> None:
        """Increment the hit count for this bin."""
        self._hit_count += 1

    def get_hit_count(self) -> int:
        """Get the current hit count."""
        return self._hit_count

    def get_coverage_percentage(self, total_samples: int) -> float:
        """
        Calculate coverage percentage.

        Args:
            total_samples: Total number of samples

        Returns:
            Coverage percentage (0-100)
        """
        if total_samples == 0:
            return 0.0
        return (self._hit_count / total_samples) * 100.0

    def __repr__(self) -> str:
        return f"Bin(name='{self.name}', hits={self._hit_count})"


class ValueBin(Bin):
    """
    Value Bin - matches exact values.

    Corresponds to SystemVerilog:
        bins value_bin = {15};
    """

    def __init__(self, name: str, value: Any):
        """
        Initialize a ValueBin.

        Args:
            name: Bin identifier name
            value: The exact value to match
        """
        super().__init__(name)
        self.value = value

    def match(self, value: Any) -> bool:
        """Check if value exactly matches the bin value."""
        return value == self.value

    def __repr__(self) -> str:
        return f"ValueBin(name='{self.name}', value={self.value}, hits={self._hit_count})"


class RangeBin(Bin):
    """
    Range Bin - matches values within a range [low, high].

    Corresponds to SystemVerilog:
        bins range_bin[] = {[0:127], [256:511]};
    """

    def __init__(self, name: str, low: Any, high: Any):
        """
        Initialize a RangeBin.

        Args:
            name: Bin identifier name
            low: Lower bound (inclusive)
            high: Upper bound (inclusive)

        Raises:
            ValueError: If low > high
        """
        super().__init__(name)
        self.low = low
        self.high = high

        if low > high:
            raise ValueError(f"Invalid range: low ({low}) > high ({high})")

    def match(self, value: Any) -> bool:
        """
        Check if value is within range [low, high].

        Args:
            value: The value to check

        Returns:
            True if low <= value <= high
        """
        try:
            return self.low <= value <= self.high
        except TypeError:
            return False

    def __repr__(self) -> str:
        return f"RangeBin(name='{self.name}', range=[{self.low}, {self.high}], hits={self._hit_count})"


class WildcardBin(Bin):
    """
    Wildcard Bin - matches patterns using wildcards.

    Corresponds to SystemVerilog:
        bins wild_bin[] = {8'b0000????};

    Supports:
    - '?' : matches any single character (hex digit or generic character)
    - For hex values: "8???" matches 0x8000-0x8FFF

    Args:
        name: Bin identifier name
        pattern: Wildcard pattern (e.g., "8???")
        is_hex: Whether to interpret as hexadecimal (default: True)
    """

    def __init__(self, name: str, pattern: str, is_hex: bool = True):
        """
        Initialize a WildcardBin.

        Args:
            name: Bin identifier name
            pattern: Wildcard pattern with '?' as wildcard
            is_hex: Whether to treat as hexadecimal (default True)
        """
        super().__init__(name)
        self.pattern = pattern
        self.is_hex = is_hex
        self._compile_pattern()

    def _compile_pattern(self) -> None:
        """
        Compile wildcard pattern to regex.

        Converts SystemVerilog wildcard to Python regex:
        - '?' -> '[0-9A-Fa-f]' for hex or '.' for generic
        """
        if self.is_hex:
            regex_pattern = self.pattern.replace('?', '[0-9A-Fa-f]')
        else:
            regex_pattern = self.pattern.replace('?', '.')

        self._regex = re.compile(f'^{regex_pattern}$', re.IGNORECASE if self.is_hex else 0)

    def match(self, value: Any) -> bool:
        """
        Check if value matches the wildcard pattern.

        Args:
            value: The value to check (int or str)

        Returns:
            True if value matches the pattern
        """
        if self.is_hex and isinstance(value, int):
            # Convert to hex string without '0x' prefix
            value_str = format(value, 'X')
        else:
            value_str = str(value)

        return bool(self._regex.match(value_str))

    def __repr__(self) -> str:
        return f"WildcardBin(name='{self.name}', pattern='{self.pattern}', hits={self._hit_count})"


class AutoBin(Bin):
    """
    Auto Bin - automatically divides value range into equal-width bins.

    Corresponds to SystemVerilog:
        coverpoint cp;
            bins auto_bins[] = {[0:255]} with 16;

    Strategy:
    1. On first sample, record min and max values
    2. Calculate bin width based on total range
    3. Map subsequent samples to appropriate bin
    """

    def __init__(self, name: str, bin_index: int, total_bins: int):
        """
        Initialize an AutoBin.

        Args:
            name: Bin identifier name
            bin_index: This bin's index (0-based)
            total_bins: Total number of auto bins
        """
        super().__init__(name)
        self.bin_index = bin_index
        self.total_bins = total_bins
        self._min_value: Any = None
        self._max_value: Any = None
        self._range_initialized = False
        self._bin_low: Any = None
        self._bin_high: Any = None

    def _initialize_range(self, value: int) -> None:
        """
        Initialize value range on first sample.

        Args:
            value: First sampled value
        """
        if self._range_initialized:
            return

        # Set initial range estimate
        self._min_value = 0
        self._max_value = max(value * 2, 100) if value > 0 else 100
        self._range_initialized = True

        self._calculate_bin_bounds()

    def _calculate_bin_bounds(self) -> None:
        """Calculate the boundaries for this bin."""
        if self._min_value is None or self._max_value is None:
            return

        total_range = self._max_value - self._min_value + 1
        bin_width = total_range / self.total_bins

        self._bin_low = int(self._min_value + self.bin_index * bin_width)
        self._bin_high = int(self._min_value + (self.bin_index + 1) * bin_width - 1)

    def match(self, value: Any) -> bool:
        """
        Check if value falls within this bin's range.

        Args:
            value: The value to check

        Returns:
            True if value is within this bin's bounds
        """
        if not isinstance(value, int):
            return False

        if not self._range_initialized:
            self._initialize_range(value)
            # First sample always matches first bin temporarily
            return self.bin_index == 0

        if self._bin_low is None or self._bin_high is None:
            return False

        return self._bin_low <= value <= self._bin_high

    def __repr__(self) -> str:
        if self._bin_low is not None and self._bin_high is not None:
            return f"AutoBin(name='{self.name}', range=[{self._bin_low}, {self._bin_high}], hits={self._hit_count})"
        return f"AutoBin(name='{self.name}', uninitialized, hits={self._hit_count})"


class IgnoreBin(Bin):
    """
    Ignore Bin - marks values to be excluded from coverage.

    Corresponds to SystemVerilog:
        ignore_bins ignore_vals[] = {0, 7};

    Values matching ignore bins are not counted in coverage calculations.
    """

    def __init__(self, name: str, value: Any):
        """
        Initialize an IgnoreBin.

        Args:
            name: Bin identifier name
            value: The value to ignore
        """
        super().__init__(name)
        self.value = value

    def match(self, value: Any) -> bool:
        """Check if value matches the ignore bin."""
        return value == self.value

    def increment_hit(self) -> None:
        """Ignore bins do not count hits."""
        pass  # Intentionally does nothing

    def __repr__(self) -> str:
        return f"IgnoreBin(name='{self.name}', value={self.value})"


class IllegalBin(Bin):
    """
    Illegal Bin - marks illegal values that should never occur.

    Corresponds to SystemVerilog:
        illegal_bins illegal_vals[] = {255};

    Hitting an illegal bin indicates an error condition.
    """

    def __init__(self, name: str, value: Any):
        """
        Initialize an IllegalBin.

        Args:
            name: Bin identifier name
            value: The illegal value
        """
        super().__init__(name)
        self.value = value

    def match(self, value: Any) -> bool:
        """Check if value matches the illegal bin."""
        return value == self.value

    def increment_hit(self) -> None:
        """Illegal bin hit should raise an exception."""
        raise IllegalBinHitError(
            f"Illegal bin '{self.name}' hit with value {self.value}"
        )

    def __repr__(self) -> str:
        return f"IllegalBin(name='{self.name}', value={self.value})"


# Custom Exceptions


class IllegalBinHitError(Exception):
    """Raised when a sample hits an illegal bin."""
    pass
