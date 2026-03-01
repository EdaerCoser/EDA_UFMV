"""
Verilog格式化器

将随机化结果输出为Verilog测试向量格式
"""

from typing import Any, Dict, List, Optional, Union

from ..core.variables import RandVar, RandCVar, VarType


class Formatter:
    """格式化器基类"""

    def format(self, obj: Any) -> str:
        """
        格式化对象

        Args:
            obj: 要格式化的对象

        Returns:
            格式化后的字符串
        """
        raise NotImplementedError


class VerilogFormatter(Formatter):
    """
    Verilog测试向量格式化器

    将Randomizable对象格式化为Verilog代码
    """

    def __init__(self, hex_threshold: int = 4):
        """
        Args:
            hex_threshold: 超过此位宽使用十六进制格式
        """
        self.hex_threshold = hex_threshold

    def format(self, obj: Any) -> str:
        """
        格式化为Verilog赋值语句

        Args:
            obj: Randomizable对象

        Returns:
            Verilog代码字符串
        """
        if not hasattr(obj, "_rand_vars") and not hasattr(obj, "_randc_vars"):
            return ""

        lines = []

        # 获取所有rand变量
        rand_vars = {**getattr(obj, "_rand_vars", {}), **getattr(obj, "_randc_vars", {})}

        for var_name, var in rand_vars.items():
            value = getattr(obj, var_name, None)
            if value is None:
                continue

            line = self._format_variable(var_name, value, var)
            lines.append(line)

        return "\n".join(lines)

    def _format_variable(self, name: str, value: Any, var: Union[RandVar, RandCVar]) -> str:
        """
        格式化单个变量

        Args:
            name: 变量名
            value: 值
            var: 变量对象

        Returns:
            Verilog赋值语句
        """
        if var.var_type == VarType.ENUM:
            # 枚举类型
            return f"  {name} = {value};"
        elif var.var_type in (VarType.BIT, VarType.LOGIC):
            # 位向量类型
            if var.bit_width and var.bit_width >= self.hex_threshold:
                # 使用十六进制格式
                hex_str = self._to_hex_format(value, var.bit_width)
                return f"  {name} = {hex_str};"
            else:
                # 使用二进制格式
                bin_str = self._to_bin_format(value, var.bit_width if var.bit_width else 8)
                return f"  {name} = {bin_str};"
        else:
            # 整数类型
            return f"  {name} = {value};"

    def _to_hex_format(self, value: int, bit_width: int) -> str:
        """
        转换为Verilog十六进制格式

        Args:
            value: 整数值
            bit_width: 位宽

        Returns:
            十六进制字符串，如 "16'h1234"
        """
        hex_digits = (bit_width + 3) // 4
        # 确保值在范围内
        max_val = (1 << bit_width) - 1
        value = value & max_val
        return f"{bit_width}'h{value:0{hex_digits}x}"

    def _to_bin_format(self, value: int, bit_width: int) -> str:
        """
        转换为Verilog二进制格式

        Args:
            value: 整数值
            bit_width: 位宽

        Returns:
            二进制字符串，如 "8'b10101010"
        """
        # 确保值在范围内
        max_val = (1 << bit_width) - 1
        value = value & max_val
        return f"{bit_width}'b{value:0{bit_width}b}"

    def format_testbench(
        self,
        obj: Any,
        test_name: str = "test",
        include_module: bool = True,
    ) -> str:
        """
        生成完整的testbench代码

        Args:
            obj: Randomizable对象
            test_name: 测试名称
            include_module: 是否包含module定义

        Returns:
            Verilog testbench代码
        """
        lines = []

        if include_module:
            lines.append(f"module {test_name}_tb;")
            lines.append("")

        # 声明信号
        rand_vars = {**getattr(obj, "_rand_vars", {}), **getattr(obj, "_randc_vars", {})}

        for var_name, var in rand_vars.items():
            decl = self._declare_signal(var_name, var)
            lines.append(f"  {decl}")

        if include_module:
            lines.append("")
            lines.append("  initial begin")

        # 测试向量
        formatted = self.format(obj)
        for line in formatted.split("\n"):
            lines.append(f"    {line}")

        if include_module:
            lines.append("  end")
            lines.append("")
            lines.append(f"endmodule // {test_name}_tb")

        return "\n".join(lines)

    def _declare_signal(self, name: str, var: Union[RandVar, RandCVar]) -> str:
        """
        生成信号声明

        Args:
            name: 信号名
            var: 变量对象

        Returns:
            Verilog声明语句
        """
        if var.var_type == VarType.ENUM:
            # 假设枚举类型已定义，使用integer
            return f"integer {name};"
        elif var.var_type == VarType.LOGIC:
            return f"logic {name};"
        elif var.var_type in (VarType.BIT,):
            bit_width = var.bit_width if var.bit_width else 1
            if bit_width == 1:
                return f"logic {name};"
            else:
                return f"logic [{bit_width-1}:0] {name};"
        else:
            return f"integer {name};"

    def format_multiple(self, objects: List[Any], header: bool = True) -> str:
        """
        格式化多个对象

        Args:
            objects: Randomizable对象列表
            header: 是否包含注释头部

        Returns:
            Verilog代码字符串
        """
        lines = []

        if header:
            lines.append("// Auto-generated test vectors")
            lines.append(f"// Total: {len(objects)} vectors")
            lines.append("")

        for i, obj in enumerate(objects):
            lines.append(f"// Vector {i + 1}")
            formatted = self.format(obj)
            for line in formatted.split("\n"):
                lines.append(f"  {line}")
            lines.append("")

        return "\n".join(lines)

    def format_as_task(self, objects: List[Any], task_name: str = "apply_vector") -> str:
        """
        格式化为Verilog task

        Args:
            objects: Randomizable对象列表
            task_name: task名称

        Returns:
            Verilog task代码
        """
        lines = []

        lines.append(f"task {task_name};")
        lines.append("  input [31:0] vector_id;")

        # 声明信号
        if objects:
            rand_vars = {**getattr(objects[0], "_rand_vars", {}), **getattr(objects[0], "_randc_vars", {})}
            for var_name, var in rand_vars.items():
                decl = self._declare_signal(var_name, var)
                lines.append(f"  output {decl}")

        lines.append("begin")
        lines.append("  case (vector_id)")

        for i, obj in enumerate(objects):
            lines.append(f"    {i}: begin")

            formatted = self.format(obj)
            for line in formatted.split("\n"):
                # 移除已有的缩进
                line = line.lstrip()
                lines.append(f"      {line}")

            lines.append("    end")

        lines.append("    default: begin")
        lines.append("      $display(\"Error: Invalid vector ID\");")
        lines.append("    end")
        lines.append("  endcase")
        lines.append("end")
        lines.append("endtask")

        return "\n".join(lines)
