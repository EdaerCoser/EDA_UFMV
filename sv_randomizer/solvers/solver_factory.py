"""
求解器工厂

提供可插拔的求解器后端管理
"""

from typing import Dict, Optional, Type

from .backend_interface import SolverBackend
from .pure_python import PurePythonBackend
from .z3_backend import Z3Backend, Z3_AVAILABLE


class SolverFactory:
    """
    求解器工厂类

    支持可插拔的求解器后端架构
    """

    # 注册的求解器后端
    _backends: Dict[str, Type[SolverBackend]] = {
        "pure_python": PurePythonBackend,
    }

    # 如果Z3可用，注册它
    if Z3_AVAILABLE:
        _backends["z3"] = Z3Backend

    # 默认后端
    _default_backend = "pure_python"

    @classmethod
    def register_backend(cls, name: str, backend_class: Type[SolverBackend]) -> None:
        """
        注册新的求解器后端

        Args:
            name: 后端名称
            backend_class: 后端类（必须继承SolverBackend）
        """
        if not issubclass(backend_class, SolverBackend):
            raise ValueError(f"Backend class must inherit from SolverBackend")

        cls._backends[name] = backend_class

    @classmethod
    def unregister_backend(cls, name: str) -> None:
        """
        注销求解器后端

        Args:
            name: 后端名称
        """
        if name in cls._backends:
            del cls._backends[name]

    @classmethod
    def set_default_backend(cls, backend_name: str) -> None:
        """
        设置默认后端

        Args:
            backend_name: 后端名称
        """
        if backend_name not in cls._backends:
            available = list(cls._backends.keys())
            raise ValueError(
                f"Unknown backend: '{backend_name}'. "
                f"Available backends: {available}"
            )

        # 检查后端是否可用
        temp_backend = cls._backends[backend_name]()
        if not temp_backend.is_available():
            raise RuntimeError(
                f"Backend '{backend_name}' is not available. "
                f"Make sure required dependencies are installed."
            )

        cls._default_backend = backend_name

    @classmethod
    def get_solver(cls, backend: Optional[str] = None, **kwargs) -> SolverBackend:
        """
        获取求解器实例

        Args:
            backend: 后端名称，None则使用默认
            **kwargs: 传递给后端构造函数的参数

        Returns:
            求解器实例
        """
        if backend is None:
            backend = cls._default_backend

        if backend not in cls._backends:
            available = list(cls._backends.keys())
            raise ValueError(
                f"Unknown backend: '{backend}'. "
                f"Available backends: {available}"
            )

        backend_class = cls._backends[backend]
        solver = backend_class(**kwargs)

        if not solver.is_available():
            raise RuntimeError(
                f"Backend '{backend}' is not available. "
                f"Install required dependencies."
            )

        return solver

    @classmethod
    def list_backends(cls) -> list[str]:
        """
        列出所有已注册的后端

        Returns:
            后端名称列表
        """
        return list(cls._backends.keys())

    @classmethod
    def get_default_backend(cls) -> str:
        """
        获取默认后端名称

        Returns:
            默认后端名称
        """
        return cls._default_backend

    @classmethod
    def is_backend_available(cls, backend_name: str) -> bool:
        """
        检查后端是否可用

        Args:
            backend_name: 后端名称

        Returns:
            是否可用
        """
        if backend_name not in cls._backends:
            return False

        backend = cls._backends[backend_name]()
        return backend.is_available()

    @classmethod
    def get_backend_info(cls, backend_name: str) -> dict:
        """
        获取后端信息

        Args:
            backend_name: 后端名称

        Returns:
            包含后端信息的字典
        """
        if backend_name not in cls._backends:
            return {}

        backend = cls._backends[backend_name]()

        return {
            "name": backend_name,
            "class": backend.__class__.__name__,
            "available": backend.is_available(),
            "is_default": backend_name == cls._default_backend,
        }

    @classmethod
    def auto_select_backend(cls, num_vars: int = 0, num_constraints: int = 0) -> str:
        """
        根据问题规模自动选择后端

        Args:
            num_vars: 变量数量
            num_constraints: 约束数量

        Returns:
            推荐的后端名称
        """
        # 如果Z3可用且问题较复杂，使用Z3
        if cls.is_backend_available("z3"):
            complexity_score = num_vars * 10 + num_constraints * 5
            if complexity_score > 100:
                return "z3"

        # 默认使用PurePython
        return "pure_python"
