# sv_randomizer/api/__init__.py
"""
新API导出 - 类型注解和约束装饰器
"""

# 类型注解和装饰器
from .annotations import rand, randc, constraint

# DSL便捷函数（向后兼容）
from .annotations import inside, dist, VarProxy

# Seed控制（从seeding模块导入）
from ..core.seeding import set_global_seed as seed
from ..core.seeding import get_global_seed

# 便捷函数
from .annotations import (
    is_rand_annotation, is_randc_annotation,
    extract_rand_metadata, extract_randc_metadata
)

__all__ = [
    # 类型注解
    'rand', 'randc', 'constraint',

    # DSL便捷函数
    'inside', 'dist', 'VarProxy',

    # Seed控制
    'seed',
    'get_global_seed',

    # 内部API（用于高级用法）
    'is_rand_annotation', 'is_randc_annotation',
    'extract_rand_metadata', 'extract_randc_metadata',
]

# 注意: Randomizable 应从顶层导入: from sv_randomizer import Randomizable
# 避免循环导入问题
