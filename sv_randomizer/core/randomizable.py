"""
Randomizable基类

所有可随机化类的基类，提供randomize()方法和约束管理
"""

from typing import Any, Dict, List, Optional, get_type_hints
import random
import copy

from .variables import RandVar, RandCVar, VarType
from .seeding import create_random_instance
from ..constraints.base import Constraint
from ..solvers.solver_factory import SolverFactory
from ..utils.exceptions import ConstraintConflictError, UnsatisfiableError

# Coverage system integration (v0.2.0)
# Coverage is now an independent top-level module
from coverage.core import CoverGroup

# Type annotations support (v0.3.0)
from ..api.annotations import (
    is_rand_annotation, is_randc_annotation,
    extract_rand_metadata, extract_randc_metadata
)


class RandomizableMeta(type):
    """
    Randomizable的元类 - 自动处理类型注解

    功能：
    1. 解析类属性中的rand/randc类型注解
    2. 自动创建对应的RandVar/RandCVar对象
    3. 将变量注册到类的_rand_vars/_randc_vars字典
    """

    def __new__(cls, name: str, bases: tuple, namespace: dict, **kwargs):
        # 创建新类
        new_cls = super().__new__(cls, name, bases, namespace)

        # 为每个类创建独立的存储字典（不继承基类的）
        # 检查是否直接在类命名空间中定义了这些属性
        if '_rand_vars' not in namespace:
            new_cls._rand_vars = {}
        if '_randc_vars' not in namespace:
            new_cls._randc_vars = {}

        # 解析类型注解（跳过Randomizable基类本身）
        if name != 'Randomizable':
            try:
                hints = get_type_hints(new_cls, include_extras=True)
                _process_annotations(new_cls, hints)
            except (NameError, AttributeError):
                # 类型注解可能引用尚未定义的类型，跳过
                pass

        return new_cls


def _process_annotations(cls: type, hints: dict) -> None:
    """
    处理类型注解，创建随机变量

    Args:
        cls: 类对象
        hints: 类型注解字典 {属性名: 类型注解}
    """
    for attr_name, hint in hints.items():
        # 跳过特殊方法和私有属性
        if attr_name.startswith('_'):
            continue

        try:
            if is_rand_annotation(hint):
                metadata = extract_rand_metadata(hint)
                var = _create_rand_var(attr_name, metadata)
                cls._rand_vars[attr_name] = var

            elif is_randc_annotation(hint):
                metadata = extract_randc_metadata(hint)
                var = _create_randc_var(attr_name, metadata)
                cls._randc_vars[attr_name] = var
        except Exception as e:
            # 记录错误但继续处理其他注解
            import warnings
            warnings.warn(f"Failed to process annotation '{attr_name}': {e}")


def _create_rand_var(name: str, metadata) -> RandVar:
    """从Rand元数据创建RandVar"""
    var_type = VarType.INT

    # 确定范围
    if metadata.min is not None and metadata.max is not None:
        min_val = metadata.min
        max_val = metadata.max
    else:
        min_val = 0
        max_val = (1 << metadata.bits) - 1

    return RandVar(name, var_type, bit_width=metadata.bits,
                   min_val=min_val, max_val=max_val)


def _create_randc_var(name: str, metadata) -> RandCVar:
    """从RandC元数据创建RandCVar"""
    var_type = VarType.BIT
    return RandCVar(name, var_type, bit_width=metadata.bits)


class Randomizable(metaclass=RandomizableMeta):
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
        # v0.3.0: 保留类级别的变量（由元类创建），而不是创建新的空字典
        # 使用深拷贝避免实例间共享变量对象
        cls = self.__class__
        if hasattr(cls, '_rand_vars') and cls._rand_vars:
            self._rand_vars = {k: copy.deepcopy(v) for k, v in cls._rand_vars.items()}
        else:
            self._rand_vars = {}

        if hasattr(cls, '_randc_vars') and cls._randc_vars:
            self._randc_vars = {k: copy.deepcopy(v) for k, v in cls._randc_vars.items()}
        else:
            self._randc_vars = {}

        self._constraints: List[Constraint] = []
        self._constraint_modes: Dict[str, bool] = {}
        self._var_modes: Dict[str, bool] = {}
        self._solver_backend: Optional[str] = None

        # 种子管理
        self._seed: Optional[int] = seed
        self._random: Optional[random.Random] = None

        # Coverage system integration (v0.2.0)
        self._covergroups: Dict[str, Any] = {}  # CoverGroup instances
        self._coverage_auto_sample = True  # Auto-sample on randomize

        # v0.3.0: 解析约束方法
        self._parse_constraints()

    def pre_randomize(self) -> None:
        """
        随机化前回调

        子类可以重写此方法以在随机化前执行自定义逻辑
        例如：设置非随机变量的值、动态启用/禁用变量
        """
        pass

    def _parse_constraints(self) -> None:
        """
        解析所有约束方法，将Python表达式转换为Expression

        v0.3.0: 新增支持，自动解析@constraint装饰的方法
        """
        import ast
        import inspect
        import textwrap

        # 遍历类的所有属性
        for attr_name in dir(self.__class__):
            if attr_name.startswith('_'):
                continue

            attr = getattr(self.__class__, attr_name, None)
            if attr is None:
                continue

            # 检查是否为约束方法
            if hasattr(attr, '_is_constraint'):
                try:
                    # 获取方法的源代码
                    source = inspect.getsource(attr)
                    # 去除缩进
                    source = textwrap.dedent(source)

                    # 解析AST，提取return语句后的表达式
                    tree = ast.parse(source)
                    function_node = tree.body[0]

                    # 找到return语句
                    return_stmt = None
                    for node in ast.walk(function_node):
                        if isinstance(node, ast.Return) and node.value is not None:
                            return_stmt = node
                            break

                    if return_stmt is None:
                        continue

                    # 将Python表达式转换为Expression
                    from ..api.expression import parse_python_expression
                    expr_str = ast.unparse(return_stmt.value)
                    expr = parse_python_expression(expr_str, self)

                    # 创建约束对象
                    from ..constraints.base import ExpressionConstraint
                    constraint_obj = ExpressionConstraint(attr_name, expr)
                    self.add_constraint(constraint_obj)

                except Exception as e:
                    import warnings
                    warnings.warn(f"Failed to parse constraint '{attr_name}': {e}")

    def post_randomize(self) -> None:
        """
        随机化后回调

        子类可以重写此方法以在随机化后执行自定义逻辑
        例如：计算派生值、验证结果、生成特殊值

        扩展：自动触发覆盖率采样（v0.2.0）
        """
        # 自动采样覆盖率（如果启用）
        if self._coverage_auto_sample and self._covergroups:
            self._sample_coverage()

    def __getattr__(self, name: str) -> Any:
        """
        支持通过self.xxx访问随机变量值

        v0.3.0: 新增类型注解支持，允许直接访问注解定义的随机变量
        """
        # 防止无限递归（__getattr__不会触发__dict__查找）
        if name.startswith('_'):
            raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")

        # 检查实例的_rand_vars
        if '_rand_vars' in self.__dict__ and name in self._rand_vars:
            var = self._rand_vars[name]
            return getattr(var, 'value', None)

        # 检查实例的_randc_vars
        if '_randc_vars' in self.__dict__ and name in self._randc_vars:
            var = self._randc_vars[name]
            return getattr(var, 'value', None)

        # 检查类级别的_rand_vars（元类创建的）
        cls = self.__class__
        if hasattr(cls, '_rand_vars') and name in cls._rand_vars:
            # 从实例字典获取值，如果不存在则返回None
            if name in self.__dict__:
                return self.__dict__[name]
            var = cls._rand_vars[name]
            return getattr(var, 'value', None)

        if hasattr(cls, '_randc_vars') and name in cls._randc_vars:
            if name in self.__dict__:
                return self.__dict__[name]
            var = cls._randc_vars[name]
            return getattr(var, 'value', None)

        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")

    def __setattr__(self, name: str, value: Any) -> None:
        """
        支持设置随机变量值

        v0.3.0: 新增类型注解支持
        """
        # 在初始化期间，正常设置所有属性
        if not hasattr(self, '_rand_vars') or name in ('_rand_vars', '_randc_vars', '__dict__'):
            super().__setattr__(name, value)
            return

        # 检查是否是随机变量
        if name in self._rand_vars:
            self._rand_vars[name].value = value
            self.__dict__[name] = value
        elif name in self._randc_vars:
            self._randc_vars[name].value = value
            self.__dict__[name] = value
        # 检查类级别的变量
        elif hasattr(self.__class__, '_rand_vars') and name in self.__class__._rand_vars:
            # 确保实例有独立的_rand_vars
            if name not in self._rand_vars:
                self._rand_vars[name] = self.__class__._rand_vars[name]
            self._rand_vars[name].value = value
            self.__dict__[name] = value
        elif hasattr(self.__class__, '_randc_vars') and name in self.__class__._randc_vars:
            if name not in self._randc_vars:
                self._randc_vars[name] = self.__class__._randc_vars[name]
            self._randc_vars[name].value = value
            self.__dict__[name] = value
        else:
            super().__setattr__(name, value)

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
                # 将randc变量替换为已生成的常量值
                constraint_vars = constraint.get_variables()
                has_randc = any(v in self._randc_vars for v in constraint_vars)

                if has_randc:
                    # 涉及randc的约束：验证randc值是否满足约束
                    # 简化处理：检查约束是否被当前randc值满足
                    # TODO: 完整实现应该将randc变量作为常量添加到约束中
                    if hasattr(constraint, 'check'):
                        # 构建包含randc值的上下文进行验证
                        context = randc_values.copy()
                        if not constraint.check(context):
                            # randc值不满足约束，需要重新生成或返回失败
                            # 这里简化：返回False让用户知道约束冲突
                            raise ConstraintConflictError(
                                f"Constraint '{constraint.name}' conflicts with randc variable values: {randc_values}"
                            )
                    else:
                        # 对于表达式约束，暂时跳过（理想情况应该支持）
                        continue
                else:
                    # 不涉及randc的约束，直接添加到求解器
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

        except (ConstraintConflictError, UnsatisfiableError):
            # 预期的约束求解错误，静默返回False
            return False
        except (KeyboardInterrupt, SystemExit):
            # 不要捕获系统级异常
            raise
        except Exception as e:
            # 其他未预期的错误，记录并返回False
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
        # 首先收集装饰器定义的变量
        self._collect_decorator_vars()

        active = {}
        for name, var in {**self._rand_vars, **self._randc_vars}.items():
            if self._var_modes.get(name, True):
                active[name] = var
        return active

    def _collect_decorator_vars(self) -> None:
        """
        收集装饰器定义的随机变量

        遍历类的所有属性，找到 property 并尝试访问它们以触发变量创建
        """
        import inspect

        # 获取类的所有属性
        for name in dir(self):
            if name.startswith('_'):
                continue

            attr = getattr(self.__class__, name, None)
            if attr is None:
                continue

            # 检查是否是 property（rand/randc 装饰器创建的）
            if isinstance(attr, property):
                # 尝试访问 property 以触发变量创建
                # 使用 __dict__ 检查是否已经有值，避免重复访问
                if name not in self.__dict__:
                    try:
                        # 访问 property 会触发 getter，从而创建变量
                        _ = getattr(self, name)
                    except Exception:
                        # 忽略访问失败的情况
                        pass

    def _get_active_constraints(self) -> List[Constraint]:
        """
        获取所有启用的约束

        Returns:
            约束列表
        """
        # 首先收集装饰器定义的约束
        self._collect_decorator_constraints()

        active = []
        for constraint in self._constraints:
            if self._constraint_modes.get(constraint.name, True) and constraint.is_enabled():
                active.append(constraint)
        return active

    def _collect_decorator_constraints(self) -> None:
        """
        收集装饰器定义的约束

        遍历类的所有方法，找到带有 _is_constraint 属性的方法并调用它们
        """
        import inspect

        # 获取所有方法（包括继承的）
        for name in dir(self):
            if name.startswith('_'):
                continue

            attr = getattr(self.__class__, name, None)
            if attr is None:
                continue

            # 检查是否是约束装饰器定义的方法
            if hasattr(attr, '_is_constraint'):
                constraint_name = getattr(attr, '_constraint_name', name)

                # 检查约束是否已经添加过
                already_added = any(c.name == constraint_name for c in self._constraints)

                if not already_added:
                    try:
                        # 调用约束方法来添加约束
                        attr(self)
                    except Exception:
                        # 约束方法可能会在变量未初始化时失败，这是正常的
                        pass

    def _build_inline_constraints(self, inline: Dict[str, Any]) -> List[Constraint]:
        """
        构建内联约束

        Args:
            inline: 内联约束字典，支持两种形式：
                    - 值形式：{"addr": 1000}  → addr == 1000
                    - 函数形式：{"length": lambda x: x > 0}  → 自定义验证

        Returns:
            约束列表
        """
        from ..constraints.base import ExpressionConstraint, FunctionConstraint
        from ..constraints.expressions import VariableExpr, ConstantExpr, BinaryExpr, BinaryOp

        constraints = []

        for var_name, value in inline.items():
            if callable(value):
                # 函数形式的约束
                # 创建一个函数约束，在求解后验证
                constraint = FunctionConstraint(
                    f"_inline_func_{var_name}",
                    lambda ctx, v=value, n=var_name: v(ctx.get(n))
                )
                constraints.append(constraint)
            else:
                # 简单的值约束：变量 == 值
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

    def add_covergroup(self, covergroup) -> None:
        """
        添加覆盖率组到当前对象

        Args:
            covergroup: CoverGroup实例

        Example:
            >>> cg = PacketCoverage()
            >>> pkt.add_covergroup(cg)
        """
        self._covergroups[covergroup.name] = covergroup

    def get_covergroup(self, name: str) -> Optional[Any]:
        """
        根据名称获取覆盖率组

        Args:
            name: CoverGroup名称

        Returns:
            CoverGroup实例，不存在返回None
        """
        return self._covergroups.get(name)

    def get_coverage(self) -> Dict[str, float]:
        """
        获取所有覆盖率组的覆盖率

        Returns:
            覆盖率组名到覆盖率百分比的映射

        Example:
            >>> coverage = pkt.get_coverage()
            >>> print(coverage)
            {'packet_cg': 85.5, 'addr_cg': 92.3}
        """
        return {
            name: cg.get_coverage()
            for name, cg in self._covergroups.items()
        }

    def get_total_coverage(self) -> float:
        """
        计算总覆盖率（所有覆盖率组的加权平均）

        Returns:
            总覆盖率百分比 (0.0 - 100.0)

        Example:
            >>> total = pkt.get_total_coverage()
            >>> print(f"Total coverage: {total:.2f}%")
        """
        if not self._covergroups:
            return 0.0

        total_coverage = sum(cg.get_coverage() for cg in self._covergroups.values())
        return total_coverage / len(self._covergroups)

    def _sample_coverage(self) -> None:
        """
        采样所有覆盖率组（内部方法）

        在randomize()后自动调用
        收集当前所有变量值并触发采样
        """
        # 收集当前所有变量值
        sample_values = {}
        for var_name in self.list_rand_vars():
            if hasattr(self, var_name):
                value = getattr(self, var_name, None)
                if value is not None:
                    sample_values[var_name] = value

        # 采样所有CoverGroups
        for cg in self._covergroups.values():
            if cg.is_sampling_enabled():
                cg.sample(**sample_values)

    def enable_coverage_sampling(self) -> None:
        """启用自动覆盖率采样"""
        self._coverage_auto_sample = True

    def disable_coverage_sampling(self) -> None:
        """禁用自动覆盖率采样"""
        self._coverage_auto_sample = False
