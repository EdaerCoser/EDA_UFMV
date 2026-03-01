"""
Randomizable基类

所有可随机化类的基类，提供randomize()方法和约束管理
"""

from typing import Any, Dict, List, Optional
import random

from .variables import RandVar, RandCVar
from .seeding import create_random_instance
from ..constraints.base import Constraint
from ..solvers.solver_factory import SolverFactory
from ..utils.exceptions import ConstraintConflictError, UnsatisfiableError


class Randomizable:
    """
    可随机化类的基类

    类似SystemVerilog中的类，所有包含rand/randc变量的类都应继承此类

    示例:
        class Packet(Randomizable):
            def __init__(self):
                super().__init__()
                self._rand_vars['addr'] = RandVar('addr', VarType.BIT, bit_width=16)
                self._randc_vars['id'] = RandCVar('id', VarType.BIT, bit_width=8)

            def pre_randomize(self):
                print("Before randomization")

            def post_randomize(self):
                print(f"After: addr={self.addr}, id={self.id}")

        pkt = Packet()
        pkt.randomize()
    """

    def __init__(self, seed: Optional[int] = None):
        """
        初始化Randomizable对象

        Args:
            seed: 随机种子，None则使用全局种子
        """
        self._rand_vars: Dict[str, RandVar] = {}
        self._randc_vars: Dict[str, RandCVar] = {}
        self._constraints: List[Constraint] = []
        self._constraint_modes: Dict[str, bool] = {}
        self._var_modes: Dict[str, bool] = {}
        self._solver_backend: Optional[str] = None

        # 种子管理
        self._seed: Optional[int] = seed
        self._random: Optional[random.Random] = None

    def pre_randomize(self) -> None:
        """
        随机化前回调

        子类可以重写此方法以在随机化前执行自定义逻辑
        例如：设置非随机变量的值、动态启用/禁用变量
        """
        pass

    def post_randomize(self) -> None:
        """
        随机化后回调

        子类可以重写此方法以在随机化后执行自定义逻辑
        例如：计算派生值、验证结果、生成特殊值
        """
        pass

    def set_seed(self, seed: Optional[int]) -> None:
        """
        设置或重置此对象的随机种子

        Args:
            seed: 随机种子，None则使用全局种子

        Example:
            >>> obj = MyPacket()
            >>> obj.set_seed(42)
            >>> obj.randomize()  # 使用种子42
        """
        self._seed = seed
        self._random = None  # 重置Random实例（延迟创建）

    def get_seed(self) -> Optional[int]:
        """
        获取当前种子设置

        Returns:
            当前种子，None表示未设置（使用全局种子）

        Example:
            >>> seed = obj.get_seed()
            >>> print(f"Object seed: {seed}")
        """
        return self._seed

    def get_random(self) -> random.Random:
        """
        获取此对象的Random实例（延迟创建）

        优先级: 对象级种子 > 全局种子 > 系统熵

        Returns:
            Random实例

        Example:
            >>> rand = obj.get_random()
            >>> value = rand.randint(0, 100)
        """
        if self._random is None:
            self._random = create_random_instance(self._seed)
        return self._random

    def randomize(self, with_constraints: Optional[Dict[str, Any]] = None, seed: Optional[int] = None) -> bool:
        """
        执行随机化

        这是核心方法，执行以下步骤：
        1. 调用pre_randomize()
        2. 收集活跃的变量和约束
        3. 应用内联约束（如果有）
        4. 调用求解器求解
        5. 将解应用到变量
        6. 调用post_randomize()

        Args:
            with_constraints: 内联约束字典，格式: {变量名: 值或约束}
                             例如: {"addr": 1000} 或 {"length": lambda x: x > 0}
            seed: 可选的临时种子，覆盖对象种子

        Returns:
            True表示成功，False表示约束冲突无解
        """
        # 1. 调用pre_randomize
        self.pre_randomize()

        # 2. 确定使用的Random实例
        if seed is not None:
            # 临时种子：创建临时Random实例
            rand = random.Random(seed)
        else:
            # 使用对象级Random实例
            rand = self.get_random()

        # 3. 收集活跃的变量和约束
        active_vars = self._get_active_vars()
        active_constraints = self._get_active_constraints()

        if not active_vars and not active_constraints:
            # 没有随机变量，直接返回
            self.post_randomize()
            return True

        # 4. 应用内联约束（如果有）
        if with_constraints:
            inline_constraints = self._build_inline_constraints(with_constraints)
            active_constraints.extend(inline_constraints)

        # 5. 调用求解器

        # 首先处理randc变量 - 直接从值池取值
        randc_values = {}
        for var_name, var in self._randc_vars.items():
            if var_name in active_vars:
                # 设置Random实例
                var.set_random(rand)
                # randc变量直接从值池获取下一个值
                value = var.get_next()
                randc_values[var_name] = value
                setattr(self, var_name, value)

        try:
            solver = SolverFactory.get_solver(self._solver_backend, random_instance=rand)

            # 创建求解器变量（只处理rand变量）
            rand_vars = {k: v for k, v in active_vars.items() if k not in self._randc_vars}

            for var_name, var in rand_vars.items():
                var_type = "int"
                kwargs = {
                    "min_val": var.min_val,
                    "max_val": var.max_val,
                    "bit_width": var.bit_width,
                    "enum_values": var.enum_values,
                }

                if var.var_type.value in ("bool", "logic"):
                    var_type = "bool"
                elif var.var_type.value == "bit":
                    var_type = "bit"
                elif var.var_type.value == "enum":
                    var_type = "enum"

                solver.create_variable(var_name, var_type, **kwargs)

            # 添加约束
            for constraint in active_constraints:
                # 如果约束涉及randc变量，需要特殊处理
                # 这里简化：跳过涉及randc的约束
                constraint_vars = constraint.get_variables()
                has_randc = any(v in self._randc_vars for v in constraint_vars)
                if not has_randc:
                    solver.add_constraint(constraint)

            # 求解
            solution = solver.solve()

            if solution is None:
                return False

            # 6. 将解应用到变量
            for var_name, value in solution.items():
                if var_name in self._rand_vars:
                    self._rand_vars[var_name].current_value = value
                setattr(self, var_name, value)

            # 7. 调用post_randomize
            self.post_randomize()
            return True

        except Exception as e:
            # 捕获求解错误
            import traceback
            traceback.print_exc()
            return False

    def constraint_mode(self, constraint_name: str, mode: Optional[bool] = None) -> bool:
        """
        启用/禁用约束，类似SystemVerilog的constraint_mode()

        Args:
            constraint_name: 约束名称
            mode: True启用，False禁用，None则只查询当前状态

        Returns:
            约束的当前模式（True=启用，False=禁用）
        """
        if mode is not None:
            self._constraint_modes[constraint_name] = mode
            # 更新约束对象的enabled状态
            for constraint in self._constraints:
                if constraint.name == constraint_name:
                    constraint.enabled = mode

        return self._constraint_modes.get(constraint_name, True)

    def rand_mode(self, var_name: str, mode: Optional[bool] = None) -> bool:
        """
        启用/禁用随机变量，类似SystemVerilog的rand_mode()

        Args:
            var_name: 变量名
            mode: True启用，False禁用，None则只查询当前状态

        Returns:
            变量的当前模式（True=启用，False=禁用）
        """
        if mode is not None:
            self._var_modes[var_name] = mode

        return self._var_modes.get(var_name, True)

    def set_solver_backend(self, backend: str) -> None:
        """
        设置求解器后端

        Args:
            backend: 后端名称 ("pure_python" 或 "z3")
        """
        self._solver_backend = backend

    def _get_active_vars(self) -> Dict[str, RandVar]:
        """
        获取所有启用的随机变量

        Returns:
            变量名到RandVar/RandCVar的字典
        """
        active = {}
        for name, var in {**self._rand_vars, **self._randc_vars}.items():
            if self._var_modes.get(name, True):
                active[name] = var
        return active

    def _get_active_constraints(self) -> List[Constraint]:
        """
        获取所有启用的约束

        Returns:
            约束列表
        """
        active = []
        for constraint in self._constraints:
            if self._constraint_modes.get(constraint.name, True) and constraint.is_enabled():
                active.append(constraint)
        return active

    def _build_inline_constraints(self, inline: Dict[str, Any]) -> List[Constraint]:
        """
        构建内联约束

        Args:
            inline: 内联约束字典

        Returns:
            约束列表
        """
        from ..constraints.base import ExpressionConstraint
        from ..constraints.expressions import VariableExpr, ConstantExpr, BinaryExpr, BinaryOp

        constraints = []

        for var_name, value in inline.items():
            if callable(value):
                # 函数形式的约束
                # 这里简化处理，实际应该更复杂
                pass
            else:
                # 简单的值约束
                expr = BinaryExpr(
                    VariableExpr(var_name),
                    BinaryOp.EQ,
                    ConstantExpr(value)
                )
                constraint = ExpressionConstraint(f"_inline_{var_name}", expr)
                constraints.append(constraint)

        return constraints

    def add_constraint(self, constraint: Constraint) -> None:
        """
        添加约束

        Args:
            constraint: 约束对象
        """
        self._constraints.append(constraint)
        # 初始模式为启用
        self._constraint_modes[constraint.name] = True

    def get_constraint(self, name: str) -> Optional[Constraint]:
        """
        根据名称获取约束

        Args:
            name: 约束名称

        Returns:
            约束对象，不存在返回None
        """
        for constraint in self._constraints:
            if constraint.name == name:
                return constraint
        return None

    def list_constraints(self) -> List[str]:
        """
        列出所有约束名称

        Returns:
            约束名称列表
        """
        return [c.name for c in self._constraints]

    def list_rand_vars(self) -> List[str]:
        """
        列出所有随机变量名称

        Returns:
            变量名列表
        """
        return list(self._rand_vars.keys()) + list(self._randc_vars.keys())
