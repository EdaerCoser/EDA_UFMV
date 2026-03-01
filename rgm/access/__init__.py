"""
Access - 访问接口

包含FrontDoor和BackDoor访问接口实现。
"""

from .base import AccessInterface
from .frontdoor import FrontDoorAccess
from .backdoor import BackDoorAccess

__all__ = [
    "AccessInterface",
    "FrontDoorAccess",
    "BackDoorAccess",
]
