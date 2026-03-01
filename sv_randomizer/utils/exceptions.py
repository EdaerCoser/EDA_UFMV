"""
自定义异常类

定义SV Randomizer中使用的所有异常类型
"""


class RandomizerError(Exception):
    """随机化器基础异常"""

    pass


class ConstraintConflictError(RandomizerError):
    """约束冲突异常

    当检测到约束之间存在数学上的冲突时抛出
    """

    def __init__(self, message: str, conflicting_constraints: list = None):
        self.conflicting_constraints = conflicting_constraints or []
        super().__init__(message)


class UnsatisfiableError(RandomizerError):
    """约束不可满足异常

    当约束集在数学上无解时抛出
    """

    def __init__(self, message: str, constraints: list = None):
        self.constraints = constraints or []
        super().__init__(message)


class VariableNotFoundError(RandomizerError):
    """变量未找到异常

    当引用的变量不存在时抛出
    """

    def __init__(self, var_name: str):
        self.var_name = var_name
        super().__init__(f"Variable '{var_name}' not found")


class SolverBackendError(RandomizerError):
    """求解器后端异常

    当求解器后端发生错误时抛出
    """

    def __init__(self, message: str, backend_name: str = None):
        self.backend_name = backend_name
        super().__init__(message)


class InvalidConstraintError(RandomizerError):
    """无效约束异常

    当约束定义不合法时抛出
    """

    def __init__(self, message: str, constraint_name: str = None):
        self.constraint_name = constraint_name
        super().__init__(message)
