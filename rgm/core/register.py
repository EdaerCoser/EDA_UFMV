"""
Register - 寄存器类

对应硬件寄存器和UVM的uvm_reg。
包含多个字段，支持完整的UVM风格接口（set/get/update/mirror/poke/peek）。
"""

from typing import Dict, Optional, List, TYPE_CHECKING

if TYPE_CHECKING:
    from .field import Field
    from .register_block import RegisterBlock

from .field import AccessType


class Register:
    """
    寄存器类

    对应SystemVerilog的寄存器定义和UVM的uvm_reg。

    SystemVerilog示例:
        logic [31:0] control_reg;  // @0x0000

    Args:
        name: 寄存器名称
        offset: 相对于RegisterBlock的偏移地址
        width: 寄存器位宽（默认32）
        reset_value: 复位值（默认0）
        description: 寄存器描述

    Example:
        >>> reg = Register(
        ...     name="control",
        ...     offset=0x0000,
        ...     width=32,
        ...     description="Control register"
        ... )
        >>> from rgm.core import Field, AccessType
        >>> reg.add_field(Field("enable", 0, 1, AccessType.RW, 0))
        >>> reg.add_field(Field("mode", 1, 3, AccessType.RW, 0))
        >>> reg.write(0x0F)
        >>> value = reg.read()
    """

    def __init__(
        self,
        name: str,
        offset: int,
        width: int = 32,
        reset_value: int = 0,
        description: str = "",
    ):
        self.name = name
        self.offset = offset  # 相对于RegisterBlock的偏移
        self.width = width
        self.reset_value = reset_value
        self.description = description

        # 字段管理
        self._fields: Dict[str, "Field"] = {}

        # 运行时状态
        self._current_value = reset_value
        self._parent_block: Optional["RegisterBlock"] = None

        # 访问接口（策略模式）
        self._access_interface = None

        # UVM风格：镜像值、实际值、期望值分离
        self._mirrored_value = reset_value  # 镜像值（期望值）
        self._actual_value = reset_value  # 实际硬件值
        self._desired_value = reset_value  # 期望写入值

    def add_field(self, field: "Field") -> None:
        """
        添加字段

        Args:
            field: Field实例

        Raises:
            ValueError: 字段超出寄存器宽度或与现有字段重叠
        """
        # 验证字段范围
        if field.bit_offset + field.bit_width > self.width:
            raise ValueError(
                f"Field '{field.name}' exceeds register width "
                f"(offset={field.bit_offset}, width={field.bit_width}, "
                f"reg_width={self.width})"
            )

        # 检查重叠
        for existing_field in self._fields.values():
            if self._fields_overlap(field, existing_field):
                raise ValueError(
                    f"Field '{field.name}' overlaps with "
                    f"'{existing_field.name}'"
                )

        self._fields[field.name] = field
        field._parent_register = self

        # Update register's current value with field's reset value
        field_mask = field.get_mask()
        self._current_value = (self._current_value & ~field_mask) | (field.reset_value << field.bit_offset)

        # Also update mirrored and actual values
        self._mirrored_value = (self._mirrored_value & ~field_mask) | (field.reset_value << field.bit_offset)
        self._actual_value = (self._actual_value & ~field_mask) | (field.reset_value << field.bit_offset)

    def _fields_overlap(self, field1: "Field", field2: "Field") -> bool:
        """
        检查两个字段是否重叠

        Args:
            field1: 第一个字段
            field2: 第二个字段

        Returns:
            True if overlapping, False otherwise
        """
        f1_start = field1.bit_offset
        f1_end = field1.bit_offset + field1.bit_width - 1
        f2_start = field2.bit_offset
        f2_end = field2.bit_offset + field2.bit_width - 1

        return not (f1_end < f2_start or f2_end < f1_start)

    def get_field(self, name: str) -> Optional["Field"]:
        """
        获取字段

        Args:
            name: 字段名称

        Returns:
            Field实例或None
        """
        return self._fields.get(name)

    def get_fields(self) -> List["Field"]:
        """
        获取所有字段

        Returns:
            字段列表
        """
        return list(self._fields.values())

    def read(self) -> int:
        """
        读取寄存器值（使用访问接口）

        Returns:
            当前寄存器值
        """
        # 如果有访问接口，使用FrontDoor或BackDoor
        if self._access_interface and self._parent_block:
            abs_addr = self.get_address()
            value = self._access_interface.read(abs_addr)
            self._current_value = value
            self._actual_value = value
            return value

        self._actual_value = self._current_value
        return self._current_value

    def write(self, value: int) -> None:
        """
        写入寄存器值（使用访问接口）

        Args:
            value: 要写入的值
        """
        masked_value = value & ((1 << self.width) - 1)

        # 如果有访问接口，使用FrontDoor或BackDoor
        if self._access_interface and self._parent_block:
            abs_addr = self.get_address()
            self._access_interface.write(abs_addr, masked_value)

        # 更新本地值
        self._current_value = masked_value
        self._mirrored_value = masked_value
        self._actual_value = masked_value

    def read_field(self, field_name: str) -> int:
        """
        读取字段值（读-改-写）

        Args:
            field_name: 字段名称

        Returns:
            字段值

        Raises:
            ValueError: 字段不存在
        """
        field = self.get_field(field_name)
        if not field:
            raise ValueError(f"Field '{field_name}' not found")

        # 先读取整个寄存器
        reg_value = self.read()
        field._current_value = reg_value
        field._mirrored_value = reg_value
        return field.read()

    def write_field(self, field_name: str, value: int) -> None:
        """
        写入字段值（读-改-写）

        Args:
            field_name: 字段名称
            value: 要写入的值

        Raises:
            ValueError: 字段不存在或为只读
        """
        field = self.get_field(field_name)
        if not field:
            raise ValueError(f"Field '{field_name}' not found")

        if field.access == AccessType.RO:
            raise ValueError(f"Cannot write to RO field '{field_name}'")

        # 读-改-写
        current = self.read()
        field._current_value = current
        field.write(value)

        # 更新寄存器值
        new_value = current & ~field.get_mask()
        new_value |= (field._current_value << field.bit_offset) & field.get_mask()
        self.write(new_value)

    def reset(self) -> None:
        """重置寄存器"""
        self._current_value = self.reset_value
        self._mirrored_value = self.reset_value
        self._actual_value = self.reset_value
        for field in self._fields.values():
            field.reset()

    def get_address(self) -> int:
        """
        获取绝对地址

        Returns:
            绝对地址（如果有父块）
        """
        if self._parent_block:
            return self._parent_block.base_address + self.offset
        return self.offset

    # ========== UVM风格接口 ==========

    def set(self, value: int) -> None:
        """
        设置期望值（UVM风格）- 不立即写入硬件

        Args:
            value: 期望值
        """
        self._desired_value = value & ((1 << self.width) - 1)

    def get(self) -> int:
        """
        获取镜像值（UVM风格）

        Returns:
            镜像值
        """
        return self._mirrored_value & ((1 << self.width) - 1)

    def update(self, field: str = None) -> None:
        """
        批量写入（UVM风格）- 将期望值写入硬件

        Args:
            field: 可选，指定字段名称
        """
        if field:
            self.write_field(field, self._desired_value)
        else:
            self.write(self._desired_value)

    def mirror(self, check: bool = True) -> int:
        """
        同步硬件值到镜像（UVM风格）

        Args:
            check: 是否检查值匹配

        Returns:
            实际硬件值

        Raises:
            ValueError: 如果check=True且值不匹配
        """
        self._actual_value = self.read()
        if check:
            if self._actual_value != self._mirrored_value:
                raise ValueError(
                    f"Register {self.name} mismatch: "
                    f"mirrored=0x{self._mirrored_value:X}, "
                    f"actual=0x{self._actual_value:X}"
                )
        self._mirrored_value = self._actual_value
        return self._actual_value

    def poke(self, value: int) -> None:
        """
        后门写入（UVM风格）- 强制写入，忽略访问权限

        Args:
            value: 要写入的值
        """
        masked_value = value & ((1 << self.width) - 1)

        # 使用BackDoor访问（如果可用）
        if self._parent_block and hasattr(self._parent_block, "_backdoor"):
            backdoor = self._parent_block._backdoor
            if backdoor:
                addr = self.get_address()
                backdoor.write(addr, masked_value)

        self._mirrored_value = masked_value
        self._current_value = masked_value

    def peek(self) -> int:
        """
        后门读取（UVM风格）- 直接读取硬件

        Returns:
            寄存器值
        """
        # 使用BackDoor访问（如果可用）
        if self._parent_block and hasattr(self._parent_block, "_backdoor"):
            backdoor = self._parent_block._backdoor
            if backdoor:
                addr = self.get_address()
                return backdoor.read(addr)

        return self._mirrored_value

    def __repr__(self) -> str:
        return (
            f"Register(name='{self.name}', offset=0x{self.offset:X}, "
            f"width={self.width}, value=0x{self._current_value:X}, "
            f"fields={len(self._fields)})"
        )
