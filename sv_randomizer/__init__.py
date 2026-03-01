"""
SV Randomizer - SystemVerilog风格随机约束求解器

一个Python实现的SystemVerilog风格随机化工具，支持：
- rand/randc变量
- 约束系统 (inside, dist, 关系/逻辑运算符)
- 可插拔求解器后端 (PurePython / Z3)
- 仿真器格式输出 (Verilog/VHDL)
"""

__version__ = "0.3.0"

# 核心导出
from .core.randomizable import Randomizable
from .core.variables import RandVar, RandCVar, VarType
from .core.seeding import set_global_seed, get_global_seed, reset_global_seed

# 约束导出
from .constraints.expressions import (
    Expression, VariableExpr, ConstantExpr,
    BinaryExpr, UnaryExpr, BinaryOp
)
from .constraints.base import Constraint
from .constraints.builders import InsideConstraint, DistConstraint

# 求解器导出
from .solvers.solver_factory import SolverFactory

# API导出
from .api.decorators import rand, randc, constraint
from .api.dsl import inside, dist, VarProxy

__all__ = [
    # 核心类
    "Randomizable",
    "RandVar",
    "RandCVar",
    "VarType",

    # 约束
    "Expression",
    "VariableExpr",
    "ConstantExpr",
    "BinaryExpr",
    "UnaryExpr",
    "BinaryOp",
    "Constraint",
    "InsideConstraint",
    "DistConstraint",

    # 求解器
    "SolverFactory",

    # 用户API
    "rand",
    "randc",
    "constraint",
    "inside",
    "dist",
    "VarProxy",

    # 种子控制
    "set_global_seed",
    "get_global_seed",
    "reset_global_seed",
]
