"""
BackDoor Access - 后门访问（直接内存访问）

用于仿真环境中的直接访问，绕过总线协议。
"""

from typing import Optional, Dict, Callable


class BackDoorAccess:
    """
    后门访问 - 直接内存访问

    对应UVM的uvm_reg_backdoor访问机制。

    用途：
    - 仿真环境中的快速访问
    - 避免总线协议开销
    - 直接操作DUT内部状态
    - 调试和性能分析

    Args:
        memory_map: 可选的内存映射字典 {address: value}
        read_func: 自定义读取函数
        write_func: 自定义写入函数

    Example:
        >>> # 仿真环境
        >>> back_door = BackDoorAccess(memory_map={0x4000: 0x1234})
        >>> value = back_door.read(0x4000)

        >>> # 生产环境（FPGA）
        >>> back_door = BackDoorAccess(
        ...     read_func=lambda addr: read_physical_memory(addr),
        ...     write_func=lambda addr, val: write_physical_memory(addr, val)
        ... )
    """

    def __init__(
        self,
        memory_map: Optional[Dict[int, int]] = None,
        read_func: Optional[Callable[[int], int]] = None,
        write_func: Optional[Callable[[int, int], None]] = None,
    ):
        """
        初始化BackDoor访问

        Args:
            memory_map: 可选的内存映射字典
            read_func: 自定义读取函数
            write_func: 自定义写入函数
        """
        self._memory_map = memory_map or {}
        self._read_func = read_func
        self._write_func = write_func

    def read(self, address: int) -> int:
        """
        直接读取内存

        Args:
            address: 绝对地址

        Returns:
            读取到的值
        """
        if self._read_func:
            return self._read_func(address)
        return self._memory_map.get(address, 0)

    def write(self, address: int, value: int) -> None:
        """
        直接写入内存

        Args:
            address: 绝对地址
            value: 要写入的值
        """
        if self._write_func:
            self._write_func(address, value)
        else:
            self._memory_map[address] = value

    def is_available(self) -> bool:
        """
        检查后门访问是否可用

        Returns:
            True（后门访问在仿真中总是可用）
        """
        return True

    def update_memory_map(self, address: int, value: int) -> None:
        """
        更新内存映射

        Args:
            address: 地址
            value: 值
        """
        self._memory_map[address] = value

    def set_memory_map(self, memory_map: Dict[int, int]) -> None:
        """
        设置完整的内存映射

        Args:
            memory_map: 新的内存映射字典
        """
        self._memory_map = dict(memory_map)

    def get_memory_map(self) -> Dict[int, int]:
        """
        获取内存映射

        Returns:
            内存映射字典
        """
        return self._memory_map.copy()

    def __repr__(self) -> str:
        return f"BackDoorAccess(entries={len(self._memory_map)}, has_custom_funcs={self._read_func is not None})"
