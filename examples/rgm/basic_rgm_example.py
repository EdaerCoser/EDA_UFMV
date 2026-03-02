"""
RGM基础示例 - 寄存器模型系统核心功能

展示EDA_UFVM寄存器模型系统的基本用法，包括：
- Field、Register、RegisterBlock的定义
- UVM风格接口（set/get/update/mirror/poke/peek）
- 字段读写操作
"""

import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from rgm.core import Field, Register, RegisterBlock, AccessType


def main():
    """主函数：演示RGM基础功能"""
    print("=" * 60)
    print("EDA_UFVM RGM基础示例")
    print("=" * 60)

    # ========== 1. 创建寄存器块 ==========
    print("\n1. 创建UART寄存器块")
    uart_block = RegisterBlock("UART", base_address=0x4000_0000)
    print(f"   创建寄存器块: {uart_block}")

    # ========== 2. 创建控制寄存器 ==========
    print("\n2. 创建控制寄存器 (CTRL @ 0x00)")
    ctrl_reg = Register(
        name="CTRL",
        offset=0x00,
        width=32,
        reset_value=0x00000000,
        description="UART控制寄存器"
    )

    # 添加字段
    ctrl_reg.add_field(Field("enable", 0, 1, AccessType.RW, 0, description="使能位"))
    ctrl_reg.add_field(Field("mode", 1, 3, AccessType.RW, 0, description="工作模式"))
    ctrl_reg.add_field(Field("parity_en", 4, 1, AccessType.RW, 0, description="校验使能"))
    ctrl_reg.add_field(Field("reserved", 5, 27, AccessType.RO, 0, description="保留位"))

    print(f"   字段: {', '.join(f.name for f in ctrl_reg.get_fields())}")

    # ========== 3. 创建状态寄存器 ==========
    print("\n3. 创建状态寄存器 (STATUS @ 0x04)")
    status_reg = Register(
        name="STATUS",
        offset=0x04,
        width=32,
        reset_value=0x00000000,
        description="UART状态寄存器"
    )

    status_reg.add_field(Field("tx_empty", 0, 1, AccessType.RO, 1, description="发送缓冲区空"))
    status_reg.add_field(Field("rx_full", 1, 1, AccessType.RO, 0, description="接收缓冲区满"))
    status_reg.add_field(Field("tx_busy", 2, 1, AccessType.RO, 0, description="发送忙"))
    status_reg.add_field(Field("error", 3, 1, AccessType.W1C, 0, description="错误标志（写1清除）"))

    print(f"   字段: {', '.join(f.name for f in status_reg.get_fields())}")

    # ========== 4. 添加寄存器到块 ==========
    print("\n4. 添加寄存器到块")
    uart_block.add_register(ctrl_reg)
    uart_block.add_register(status_reg)
    print(f"   寄存器块: {uart_block}")

    # ========== 5. 基本读写操作 ==========
    print("\n5. 基本读写操作")
    print(f"   CTRL复位值: 0x{ctrl_reg.read():08X}")
    ctrl_reg.write(0x0000000F)  # enable=1, mode=7, parity_en=1
    print(f"   CTRL写入值: 0x{ctrl_reg.read():08X}")
    print(f"   enable字段: {ctrl_reg.read_field('enable')}")
    print(f"   mode字段: {ctrl_reg.read_field('mode')}")

    # ========== 6. 字段写入 ==========
    print("\n6. 字段写入操作")
    ctrl_reg.write_field("mode", 5)
    print(f"   写入mode=5后: 0x{ctrl_reg.read():08X}")
    ctrl_reg.write_field("enable", 0)
    print(f"   写入enable=0后: 0x{ctrl_reg.read():08X}")

    # ========== 7. UVM风格接口演示 ==========
    print("\n7. UVM风格接口演示")
    ctrl_reg.reset()
    print(f"   复位后: 0x{ctrl_reg.get():08X}")

    # set() - 设置期望值
    ctrl_reg.set(0xABCD1234)
    print(f"   set(0xABCD1234): 0x{ctrl_reg.get():08X}")

    # update() - 批量写入
    ctrl_reg.update()
    print(f"   update()后: 0x{ctrl_reg.read():08X}")

    # ========== 8. W1C字段行为演示 ==========
    print("\n8. W1C字段行为演示")
    status_reg.write(0xFFFFFFFF)  # 设置所有位
    print(f"   STATUS初始值: 0x{status_reg.read():08X}")
    print(f"   error位初始: {status_reg.read_field('error')}")

    # W1C字段写入1会清除
    status_reg.write_field("error", 1)
    print(f"   写入error=1后: {status_reg.read_field('error')}")

    # ========== 9. 层次化路径访问 ==========
    print("\n9. 层次化路径访问")
    uart_block.write_field("CTRL", "enable", 1)
    uart_block.write_field("CTRL", "mode", 3)
    print(f"   UART.CTRL.enable: {uart_block.read_field('CTRL', 'enable')}")
    print(f"   UART.CTRL.mode: {uart_block.read_field('CTRL', 'mode')}")

    # ========== 10. 通过偏移访问 ==========
    print("\n10. 通过偏移访问")
    reg = uart_block.get_reg_by_offset(0x00)
    if reg:
        print(f"   偏移0x00的寄存器: {reg.name}")

    reg = uart_block.get_reg_by_offset(0x04)
    if reg:
        print(f"   偏移0x04的寄存器: {reg.name}")

    # ========== 11. 复位操作 ==========
    print("\n11. 复位操作")
    uart_block.reset(kind="SOFT")
    print(f"   软复位后CTRL: 0x{ctrl_reg.get():08X}")

    # ========== 12. 寄存器块摘要 ==========
    print("\n12. 寄存器块摘要")
    summary = uart_block.get_summary()
    print(f"   名称: {summary['name']}")
    print(f"   基地址: {summary['base_address']}")
    print(f"   寄存器数量: {summary['register_count']}")
    print(f"   寄存器列表: {', '.join(summary['registers'])}")

    print("\n" + "=" * 60)
    print("示例完成！")
    print("=" * 60)


if __name__ == "__main__":
    main()
