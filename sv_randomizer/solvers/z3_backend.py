"""
Z3 SMT求解器后端

使用微软Z3求解器提供工业级约束求解能力
"""

from typing import Any, Dict, List, Optional
import random

try:
    from z3 import Solver, Int, BitVec, Bool, BoolVal, IntVal, BitVecVal, And, Or, Not, Implies, sat, unsat
    Z3_AVAILABLE = True
except ImportError:
    Z3_AVAILABLE = False
    Solver = None

from .backend_interface import SolverBackend
from ..constraints.expressions import BinaryOp, Expression
from ..constraints.base import Constraint
from ..utils.exceptions import SolverBackendError


class Z3Backend(SolverBackend):
    """
    Z3 SMT求解器后端

    使用微软的Z3定理证明器作为后端，提供强大的约束求解能力

    优点：
    - 工业级性能和可靠性
    - 支持复杂约束
    - 自动求解，无需手动调参

    缺点：
    - 需要安装z3-solver包
    - 内存占用较大
    """

    def __init__(self, seed: Optional[int] = None, random_instance: Optional[random.Random] = None):
        """
        初始化Z3后端

        Args:
            seed: 随机种子（Z3不直接使用，但为接口一致性保留）
            random_instance: Random实例（Z3不直接使用，但为接口一致性保留）
        """
        super().__init__(seed, random_instance)

        if not Z3_AVAILABLE:
            raise SolverBackendError(
                "Z3 solver is not available. "
                "Install with: pip install z3-solver",
                backend_name="Z3"
            )

        self.solver = Solver()
        self.z3_vars: Dict[str, Any] = {}

    def create_variable(
        self,
        name: str,
        var_type: str = "int",
        **kwargs,
    ) -> Any:
        """
        创建Z3变量

        Args:
            name: 变量名
            var_type: 变量类型 ("int", "bool", "bit", "enum")
            **kwargs: 额外参数

        Returns:
            Z3变量对象
        """
        bit_width = kwargs.get("bit_width", 32)

        if var_type == "bool":
            z3_var = Bool(name)
        elif var_type == "bit" or var_type == "logic":
            z3_var = BitVec(name, bit_width)
        elif var_type == "enum":
            # 枚举类型用整数表示
            enum_values = kwargs.get("enum_values", [])
            z3_var = Int(name)
            # 添加枚举值约束
            if enum_values:
                for i, val in enumerate(enum_values):
                    # 为每个枚举值创建一个约束
                    pass  # 简化处理
        else:  # int
            if bit_width <= 32:
                z3_var = Int(name)
            else:
                z3_var = BitVec(name, bit_width)

        self.z3_vars[name] = z3_var
        self.variables[name] = z3_var

        # 添加范围约束
        min_val = kwargs.get("min_val")
        max_val = kwargs.get("max_val")
        if min_val is not None or max_val is not None:
            if var_type in ("int", "enum"):
                if min_val is not None and max_val is not None:
                    self.solver.add(z3_var >= min_val, z3_var <= max_val)
                elif min_val is not None:
                    self.solver.add(z3_var >= min_val)
                elif max_val is not None:
                    self.solver.add(z3_var <= max_val)

        return z3_var

    def add_constraint(self, constraint_expr: Any) -> None:
        """
        添加约束

        Args:
            constraint_expr: 约束表达式
        """
        # 如果是Constraint对象，需要先提取表达式
        if isinstance(constraint_expr, Constraint):
            if hasattr(constraint_expr, 'expr') and constraint_expr.expr is not None:
                z3_expr = self._convert_to_z3(constraint_expr.expr)
                if z3_expr is not None:
                    self.solver.add(z3_expr)
        elif isinstance(constraint_expr, Expression):
            z3_expr = self._convert_to_z3(constraint_expr)
            if z3_expr is not None:
                self.solver.add(z3_expr)
        else:
            # 已经是Z3表达式
            self.solver.add(constraint_expr)

    def _convert_to_z3(self, expr: Expression) -> Any:
        """
        将我们的Expression转换为Z3表达式

        Args:
            expr: 表达式对象

        Returns:
            Z3表达式
        """
        if expr is None:
            return None

        from ..constraints.expressions import VariableExpr, ConstantExpr, BinaryExpr, UnaryExpr, SizeExpr

        if isinstance(expr, VariableExpr):
            if expr.name not in self.z3_vars:
                raise ValueError(f"Variable '{expr.name}' not found in Z3 variables")
            return self.z3_vars[expr.name]

        elif isinstance(expr, ConstantExpr):
            value = expr.value
            if isinstance(value, bool):
                return BoolVal(value)
            elif isinstance(value, int):
                return IntVal(value)
            else:
                return IntVal(int(value))

        elif isinstance(expr, BinaryExpr):
            left = self._convert_to_z3(expr.left)
            right = self._convert_to_z3(expr.right)

            if left is None or right is None:
                return None

            op_map = {
                BinaryOp.EQ: lambda l, r: l == r,
                BinaryOp.NE: lambda l, r: l != r,
                BinaryOp.LT: lambda l, r: l < r,
                BinaryOp.LE: lambda l, r: l <= r,
                BinaryOp.GT: lambda l, r: l > r,
                BinaryOp.GE: lambda l, r: l >= r,
                BinaryOp.AND: lambda l, r: And(l, r),
                BinaryOp.OR: lambda l, r: Or(l, r),
                BinaryOp.IMPLIES: lambda l, r: Implies(l, r),
                BinaryOp.ADD: lambda l, r: l + r,
                BinaryOp.SUB: lambda l, r: l - r,
                BinaryOp.MUL: lambda l, r: l * r,
                BinaryOp.DIV: lambda l, r: l / r,
                BinaryOp.MOD: lambda l, r: l % r,
            }

            if expr.op in op_map:
                return op_map[expr.op](left, right)
            else:
                raise ValueError(f"Unsupported operator in Z3: {expr.op}")

        elif isinstance(expr, UnaryExpr):
            inner = self._convert_to_z3(expr.expr)
            if inner is None:
                return None

            if expr.op == "!":
                return Not(inner)
            elif expr.op == "-":
                return -inner
            elif expr.op == "~":
                return ~inner
            else:
                raise ValueError(f"Unsupported unary operator: {expr.op}")

        elif isinstance(expr, SizeExpr):
            # size()表达式，需要特殊处理
            # 这里简化处理，返回常量
            return IntVal(1)

        return None

    def solve(self) -> Optional[Dict[str, Any]]:
        """
        求解约束

        Returns:
            变量名到值的字典，无解返回None
        """
        if not self.z3_vars:
            return {}

        result = self.solver.check()

        if result == sat:
            model = self.solver.model()
            solution = {}

            for name, z3_var in self.z3_vars.items():
                solution[name] = self._extract_value(model, z3_var)

            return solution
        else:
            return None

    def _extract_value(self, model: Any, z3_var: Any) -> Any:
        """
        从Z3模型中提取Python值

        Args:
            model: Z3模型
            z3_var: Z3变量

        Returns:
            Python值
        """
        try:
            val = model[z3_var]
            if hasattr(val, 'as_long'):
                return val.as_long()
            elif hasattr(val, 'as_bool'):
                return val.as_bool()
            else:
                return int(val)
        except:
            return 0

    def reset(self) -> None:
        """重置求解器"""
        self.solver = Solver()
        self.z3_vars.clear()
        self.variables.clear()

    def make_const(self, value: Any) -> Any:
        """创建常量"""
        if isinstance(value, bool):
            return BoolVal(value)
        elif isinstance(value, int):
            return IntVal(value)
        return IntVal(int(value))

    def make_binary_expr(self, left: Any, op: BinaryOp, right: Any) -> Any:
        """创建二元表达式"""
        op_map = {
            BinaryOp.EQ: lambda l, r: l == r,
            BinaryOp.NE: lambda l, r: l != r,
            BinaryOp.LT: lambda l, r: l < r,
            BinaryOp.LE: lambda l, r: l <= r,
            BinaryOp.GT: lambda l, r: l > r,
            BinaryOp.GE: lambda l, r: l >= r,
            BinaryOp.AND: lambda l, r: And(l, r),
            BinaryOp.OR: lambda l, r: Or(l, r),
            BinaryOp.IMPLIES: lambda l, r: Implies(l, r),
            BinaryOp.ADD: lambda l, r: l + r,
            BinaryOp.SUB: lambda l, r: l - r,
            BinaryOp.MUL: lambda l, r: l * r,
            BinaryOp.DIV: lambda l, r: l / r,
            BinaryOp.MOD: lambda l, r: l % r,
        }

        if op not in op_map:
            raise ValueError(f"Unsupported operator in Z3: {op}")

        return op_map[op](left, right)

    def make_unary_expr(self, op: str, expr: Any) -> Any:
        """创建一元表达式"""
        if op == "!":
            return Not(expr)
        elif op == "-":
            return -expr
        elif op == "~":
            return ~expr
        raise ValueError(f"Unsupported unary operator: {op}")

    def get_backend_name(self) -> str:
        return "Z3"

    def is_available(self) -> bool:
        return Z3_AVAILABLE
