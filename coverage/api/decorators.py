"""
Coverage Decorator API

Provides SystemVerilog-style decorators for defining coverage groups,
coverpoints, and cross coverage.

Usage:
    @covergroup("packet_cg", sample_event="clk")
    class PacketCoverage:
        @coverpoint("addr_cp", bins={"ranges": [[0, 0xFF]]})
        def addr(self):
            return self._packet.addr
"""

from functools import wraps
from typing import Any, Callable, Dict, List, Optional, Union

from ..core.covergroup import CoverGroup
from ..core.coverpoint import CoverPoint


def covergroup(
    name: str,
    sample_event: Optional[str] = None,
    auto_sample: bool = True
):
    """
    Decorator to define a CoverGroup.

    Corresponds to SystemVerilog:
        covergroup name @(event);
            // coverpoints and crosses
        endgroup

    Args:
        name: CoverGroup name
        sample_event: Name of sampling event (like "@(posedge clk)")
        auto_sample: Whether to auto-sample with Randomizable

    Returns:
        Decorator function

    Example:
        @covergroup("packet_cg", sample_event="clk")
        class PacketCoverage:
            @coverpoint("addr_cp")
            def addr(self):
                return self.packet.addr
    """
    def decorator(cls):
        # Create CoverGroup instance
        class CoverGroupWrapper(CoverGroup):
            def __init__(self):
                super().__init__(
                    name=name,
                    sample_event=None,  # Will be set later if needed
                    auto_sample=auto_sample
                )

                # Initialize members from class definition
                self._initialize_members(cls)

        # Preserve class metadata
        CoverGroupWrapper.__name__ = cls.__name__
        CoverGroupWrapper.__doc__ = cls.__doc__
        CoverGroupWrapper.__module__ = cls.__module__

        return CoverGroupWrapper

    return decorator


def coverpoint(
    name: str,
    bins: Optional[Dict[str, Any]] = None,
    auto_bin_max: Optional[int] = None,
    weight: float = 1.0,
    comment: str = ""
):
    """
    Decorator to define a CoverPoint.

    Corresponds to SystemVerilog:
        coverpoint name;
            bins bins_array[] = {...};
            ignore_bins ignore_array[] = {...};
            illegal_bins illegal_array[] = {...};

    Args:
        name: CoverPoint name
        bins: Bin definition dictionary with keys:
            - "values": list of single values
            - "ranges": list of [low, high] pairs
            - "wildcards": list of wildcard patterns
            - "auto": number of auto bins
            - "ignore": list of values to ignore
            - "illegal": list of illegal values
        auto_bin_max: Maximum number of auto bins (default: 64)
        weight: Weight for weighted coverage (default: 1.0)
        comment: Documentation comment

    Returns:
        Decorator function

    Example:
        @coverpoint("addr_cp",
                     bins={"ranges": [[0, 0xFF], [0x100, 0x1FF]]})
        def addr(self):
            return self._packet.addr
    """
    def decorator(func: Callable) -> property:
        @property
        @wraps(func)
        def wrapper(self):
            # Create CoverPoint instance
            cp = CoverPoint(
                name=name,
                sample_expr=func,
                bins=bins,
                auto_bin_max=auto_bin_max,
                weight=weight,
                comment=comment
            )

            # If self is a CoverGroup, add the coverpoint
            if hasattr(self, 'add_coverpoint'):
                self.add_coverpoint(cp)

            return cp

        return wrapper

    return decorator


def cross(
    name: str,
    coverpoints: List[str],
    cross_filter: Optional[callable] = None
):
    """
    Decorator to define Cross coverage.

    Corresponds to SystemVerilog:
        cross name;
            bins cross_bins[] = binsof cp1 X cp2;

    Args:
        name: Cross name
        coverpoints: List of coverpoint names to cross
        cross_filter: Optional filter function for combinations

    Returns:
        Decorator function

    Note:
        Full cross implementation will be completed in M3.
        Currently creates a placeholder.
    """
    def decorator(func: Callable) -> property:
        @property
        @wraps(func)
        def wrapper(self):
            # Placeholder for M3 implementation
            # For now, create a simple cross object
            class CrossPlaceholder:
                def __init__(self, name, cp_names):
                    self.name = name
                    self._coverpoint_names = cp_names
                    self._parent = None

                def _set_parent(self, parent):
                    self._parent = parent

                def sample(self, **kwargs):
                    # Placeholder - will be implemented in M3
                    pass

                def is_enabled(self):
                    return True

                def get_bin_counts(self):
                    # Placeholder
                    return 0, 0

                def get_coverage(self):
                    # Placeholder
                    return 0.0

                def get_coverage_details(self):
                    return {
                        'name': self.name,
                        'coverage': 0.0,
                        'coverpoints': self._coverpoint_names
                    }

                def set_database(self, db):
                    pass

            cross_obj = CrossPlaceholder(name, coverpoints)

            # If self is a CoverGroup, add the cross
            if hasattr(self, 'add_cross'):
                self.add_cross(cross_obj)

            return cross_obj

        return wrapper

    return decorator


# Convenience functions for common operations


def get_coverage(covergroup_or_obj) -> float:
    """
    Get coverage percentage from a CoverGroup or object with covergroups.

    Args:
        covergroup_or_obj: CoverGroup instance or object with _covergroups

    Returns:
        Coverage percentage
    """
    if isinstance(covergroup_or_obj, CoverGroup):
        return covergroup_or_obj.get_coverage()
    elif hasattr(covergroup_or_obj, 'get_total_coverage'):
        return covergroup_or_obj.get_total_coverage()
    else:
        raise TypeError(f"Cannot get coverage from {type(covergroup_or_obj)}")


def sample_coverage(covergroup_or_obj, **kwargs) -> None:
    """
    Manually trigger coverage sampling.

    Args:
        covergroup_or_obj: CoverGroup instance or object with _covergroups
        **kwargs: Variable values to sample
    """
    if isinstance(covergroup_or_obj, CoverGroup):
        covergroup_or_obj.sample(**kwargs)
    elif hasattr(covergroup_or_obj, '_sample_coverage'):
        covergroup_or_obj._sample_coverage(**kwargs)
    else:
        raise TypeError(f"Cannot sample coverage from {type(covergroup_or_obj)}")
