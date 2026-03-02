"""
代码生成器示例

展示如何使用RGM的代码生成器从寄存器模型生成各种格式的代码。
"""

import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from rgm.core import Field, Register, RegisterBlock, AccessType
from rgm.generators import GeneratorFactory


def create_uart_model():
    """创建UART寄存器模型"""
    print("创建UART寄存器模型...")

    # 创建寄存器块
    uart_block = RegisterBlock("UART", base_address=0x4000_0000)

    # 创建控制寄存器
    ctrl = Register("CTRL", 0x00, 32, 0x00000000, "UART控制寄存器")
    ctrl.add_field(Field("enable", 0, 1, AccessType.RW, 0, "使能位"))
    ctrl.add_field(Field("mode", 1, 3, AccessType.RW, 0, "工作模式"))
    ctrl.add_field(Field("parity_en", 4, 1, AccessType.RW, 0, "校验使能"))
    ctrl.add_field(Field("reserved", 5, 27, AccessType.RO, 0, "保留位"))

    # 创建状态寄存器
    status = Register("STATUS", 0x04, 32, 0x00000000, "UART状态寄存器")
    status.add_field(Field("tx_empty", 0, 1, AccessType.RO, 1, "发送缓冲区空"))
    status.add_field(Field("rx_full", 1, 1, AccessType.RO, 0, "接收缓冲区满"))
    status.add_field(Field("tx_busy", 2, 1, AccessType.RO, 0, "发送忙"))
    status.add_field(Field("error", 3, 1, AccessType.W1C, 0, "错误标志"))

    # 创建数据寄存器
    data = Register("DATA", 0x08, 32, 0x00000000, "UART数据寄存器")
    data.add_field(Field("tx_data", 0, 8, AccessType.WO, 0, "发送数据"))
    data.add_field(Field("rx_data", 8, 8, AccessType.RO, 0, "接收数据"))
    data.add_field(Field("reserved", 16, 16, AccessType.RO, 0, "保留位"))

    # 添加寄存器到块
    uart_block.add_register(ctrl)
    uart_block.add_register(status)
    uart_block.add_register(data)

    return uart_block


def main():
    """主函数：演示代码生成器"""
    print("=" * 60)
    print("EDA_UFVM RGM代码生成器示例")
    print("=" * 60)

    # 创建寄存器模型
    uart_block = create_uart_model()

    print(f"\n寄存器块: {uart_block}")
    print(f"包含寄存器: {', '.join(r.name for r in uart_block.get_registers())}")

    # ========== 1. 生成Verilog RTL ==========
    print("\n1. 生成Verilog RTL代码")
    print("-" * 40)

    verilog_code = GeneratorFactory.generate("verilog", uart_block)
    print(verilog_code[:500] + "..." if len(verilog_code) > 500 else verilog_code)

    # ========== 2. 生成C头文件 ==========
    print("\n2. 生成C头文件")
    print("-" * 40)

    c_header = GeneratorFactory.generate("c", uart_block)
    print(c_header[:500] + "..." if len(c_header) > 500 else c_header)

    # ========== 3. 生成Python模型 ==========
    print("\n3. 生成Python模型代码")
    print("-" * 40)

    python_code = GeneratorFactory.generate("python", uart_block)
    print(python_code[:500] + "..." if len(python_code) > 500 else python_code)

    # ========== 4. 保存到文件 ==========
    print("\n4. 保存到文件")
    print("-" * 40)

    output_dir = "examples/rgm/generated"
    os.makedirs(output_dir, exist_ok=True)

    # Verilog
    verilog_file = f"{output_dir}/uart_regs.v"
    with open(verilog_file, "w", encoding="utf-8") as f:
        f.write(verilog_code)
    print(f"   Verilog: {verilog_file}")

    # C头文件
    c_file = f"{output_dir}/uart_regs.h"
    with open(c_file, "w", encoding="utf-8") as f:
        f.write(c_header)
    print(f"   C Header: {c_file}")

    # Python模型
    py_file = f"{output_dir}/uart_model.py"
    with open(py_file, "w", encoding="utf-8") as f:
        f.write(python_code)
    print(f"   Python: {py_file}")

    # ========== 5. 生成器信息 ==========
    print("\n5. 可用的生成器")
    print("-" * 40)
    for gen_name in GeneratorFactory.list_generators():
        ext = GeneratorFactory.get_file_extension(gen_name)
        print(f"   {gen_name:12s} -> {ext}")

    print("\n" + "=" * 60)
    print("代码生成完成！")
    print("=" * 60)


if __name__ == "__main__":
    main()
