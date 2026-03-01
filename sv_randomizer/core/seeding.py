"""
全局随机种子管理模块

提供全局随机种子的设置、获取和重置功能，用于控制整个SV Randomizer
的随机行为，确保测试的可重复性。
"""

from typing import Optional
import random


# 全局种子变量
_global_seed: Optional[int] = None


def set_global_seed(seed: Optional[int]) -> None:
    """
    设置全局随机种子

    影响所有后续创建的Randomizable对象（除非指定对象级种子）。

    Args:
        seed: 随机种子，None表示使用系统熵

    Example:
        >>> from sv_randomizer import set_global_seed
        >>> set_global_seed(42)
        >>> obj1 = MyPacket()  # 使用种子42
        >>> obj2 = MyPacket()  # 使用种子42，从同一序列继续
    """
    global _global_seed
    _global_seed = seed


def get_global_seed() -> Optional[int]:
    """
    获取当前全局种子设置

    Returns:
        当前全局种子，None表示未设置

    Example:
        >>> from sv_randomizer import get_global_seed
        >>> seed = get_global_seed()
        >>> print(f"Global seed: {seed}")
    """
    return _global_seed


def reset_global_seed() -> None:
    """
    重置全局种子为None

    重置后创建的对象将使用系统熵。

    Example:
        >>> from sv_randomizer import reset_global_seed
        >>> reset_global_seed()
        >>> obj = MyPacket()  # 使用系统熵
    """
    global _global_seed
    _global_seed = None


def create_random_instance(seed: Optional[int] = None) -> random.Random:
    """
    创建Random实例

    优先级: 传入seed > 全局种子 > 系统熵

    Args:
        seed: 随机种子，None则使用全局种子或系统熵

    Returns:
        Random实例

    Example:
        >>> from sv_randomizer.core.seeding import create_random_instance
        >>> rand = create_random_instance(42)
        >>> value = rand.randint(0, 100)
    """
    if seed is not None:
        return random.Random(seed)
    elif _global_seed is not None:
        return random.Random(_global_seed)
    else:
        return random.Random()
