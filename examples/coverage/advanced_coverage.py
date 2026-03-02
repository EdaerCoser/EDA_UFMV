"""
Advanced Coverage Example - 功能覆盖率高级示例

这个示例展示了EDA_UFVM覆盖率系统的高级功能：
- 使用装饰器定义覆盖率（SystemVerilog语法兼容）
- 自动分箱（auto bins）
- 通配符bins（wildcard bins）
- 非法bins（illegal bins）
- 多个覆盖率组
- 权重分配

对应SystemVerilog的高级覆盖率特性。
"""

import sys
sys.path.insert(0, '../..')

from sv_randomizer.core.randomizable import Randomizable
from sv_randomizer.core.variables import RandVar, RandCVar, VarType
from coverage.core import CoverGroup, CoverPoint
from coverage.api import covergroup, coverpoint, sample_coverage


class Transaction(Randomizable):
    """
    事务类 - 演示高级覆盖率功能

    对应SystemVerilog：
        class Transaction;
            rand bit [15:0] addr;
            rand bit [7:0]  opcode;
            rand bit [31:0] data;
            rand bit [3:0]  tag;
        endclass
    """

    def __init__(self):
        super().__init__()

        # 定义随机变量
        self._rand_vars['addr'] = RandVar('addr', VarType.BIT, bit_width=16)
        self._rand_vars['opcode'] = RandVar('opcode', VarType.BIT, bit_width=8)
        self._rand_vars['data'] = RandVar('data', VarType.BIT, bit_width=32)
        self._rand_vars['tag'] = RandVar('tag', VarType.BIT, bit_width=4)

        # 使用装饰器风格定义覆盖率（SystemVerilog语法兼容）
        self._setup_decorator_coverage()

        # 使用传统API定义覆盖率
        self._setup_advanced_coverage()

    def _setup_decorator_coverage(self):
        """
        使用装饰器定义覆盖率 - SystemVerilog语法风格

        对应SystemVerilog：
            covergroup addr_cg;
                coverpoint addr;
                    bins low[] = {[0:127]};
                    bins mid[] = {[128:255]};
                    bins high[] = {[256:511]};
                    ignore_bins reserved = {0};
                endgroup
        """

        # 创建CoverGroup（对应 covergroup addr_cg;）
        self.addr_cg = CoverGroup("addr_cg")

        # 添加地址覆盖率点（对应 coverpoint addr;）
        addr_cp = CoverPoint(
            name="addr",
            sample_expr="addr",
            bins={
                # 范围bins（对应 bins low[] = {[0:127]};）
                "low": [[0, 0x7F]],
                "mid": [[0x80, 0xFF]],
                "high": [[0x100, 0x1FF]],
                # 忽略特定值（对应 ignore_bins reserved = {0};）
                "ignore": [0],
            }
        )
        self.addr_cg.add_coverpoint(addr_cp)

        # 添加操作码覆盖率点
        opcode_cp = CoverPoint(
            name="opcode",
            sample_expr="opcode",
            bins={
                # 自动分箱（对应 auto_bin_max = 16）
                "auto": 16,  # 将0-255范围自动分成16个bin
            },
            weight=2.0  # 权重更高
        )
        self.addr_cg.add_coverpoint(opcode_cp)

        self.add_covergroup(self.addr_cg)

    def _setup_advanced_coverage(self):
        """
        高级覆盖率功能演示
        """

        # 创建通配符覆盖率组
        self.wildcard_cg = CoverGroup("wildcard_cg")

        # 通配符bin示例（对应 wildcard bins）
        # 用于匹配特定模式，如"8????"匹配0x8000-0x8FFF
        wildcard_cp = CoverPoint(
            name="addr_pattern",
            sample_expr="addr",
            bins={
                "wildcards": ["8???", "9???", "A???", "B???"],
            }
        )
        self.wildcard_cg.add_coverpoint(wildcard_cp)

        # 非法bin示例（对应 illegal_bins）
        # 命中非法bin会抛出异常
        illegal_cp = CoverPoint(
            name="illegal_addr",
            sample_expr="addr",
            bins={
                "values": [0x0000, 0xFFFF],  # 正常值
                "illegal": [0xDEAD, 0xBEEF],  # 非法地址
            }
        )
        self.wildcard_cg.add_coverpoint(illegal_cp)

        # Tag覆盖率（演示小范围值）
        tag_cp = CoverPoint(
            name="tag_values",
            sample_expr="tag",
            bins={
                "values": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15],
            }
        )
        self.wildcard_cg.add_coverpoint(tag_cp)

        self.add_covergroup(self.wildcard_cg)


def print_separator(title=""):
    """打印分隔线"""
    if title:
        print(f"\n{'=' * 20} {title} {'=' * 20}")
    else:
        print("=" * 60)


def main():
    """主测试函数"""

    print_separator("EDA_UFVM 功能覆盖率 - 高级示例")

    # 创建事务对象
    txn = Transaction()

    # 测试1: 生成随机事务并收集覆盖率
    print_separator("测试1: 随机事务生成")
    print("生成200个随机事务...")

    for i in range(200):
        txn.randomize()

        # 每50次打印一次
        if (i + 1) % 50 == 0:
            coverage = txn.get_total_coverage()
            print(f"  已生成 {i+1} 个事务, 总覆盖率: {coverage:.2f}%")

    # 测试2: 打印覆盖率报告
    print_separator("测试2: 覆盖率报告")

    print(f"\n总覆盖率: {txn.get_total_coverage():.2f}%")

    for cg_name, cg in txn._covergroups.items():
        cov = cg.get_coverage()
        print(f"  {cg_name}: {cov:.2f}%")

    # 测试3: 详细覆盖率分析
    print_separator("测试3: 详细覆盖率分析")

    # 地址覆盖率详情
    print("\n[地址覆盖率组]")
    addr_details = txn.addr_cg.get_coverage_details()
    print(f"  覆盖率: {addr_details['coverage']:.2f}%")
    print(f"  采样次数: {addr_details['sample_count']}")

    for cp_name, cp_details in addr_details['coverpoints'].items():
        print(f"\n  CoverPoint: {cp_name}")
        print(f"    权重: {cp_details['weight']}")
        print(f"    覆盖率: {cp_details['coverage']:.2f}%")
        print(f"    已覆盖: {cp_details['covered_bins']}/{cp_details['total_bins']} bins")

    # 通配符覆盖率详情
    print("\n[通配符覆盖率组]")
    wild_details = txn.wildcard_cg.get_coverage_details()
    print(f"  覆盖率: {wild_details['coverage']:.2f}%")

    for cp_name, cp_details in wild_details['coverpoints'].items():
        print(f"\n  CoverPoint: {cp_name}")
        print(f"    覆盖率: {cp_details['coverage']:.2f}%")
        print(f"    已覆盖: {cp_details['covered_bins']}/{cp_details['total_bins']} bins")

        # 显示每个bin的状态
        print(f"    Bin状态:")
        for bin_name, bin_info in list(cp_details['bins'].items())[:5]:  # 只显示前5个
            hit = bin_info['hit_count']
            status = "X" if hit > 0 else " "
            print(f"      [{status}] {bin_name}: {hit} 次")

    # 测试4: 演示手动采样
    print_separator("测试4: 手动采样")

    # 禁用自动采样
    txn.disable_coverage_sampling()
    print("\n已禁用自动采样，现在手动采样...")

    # 手动触发采样
    sample_coverage(txn)

    # 重新启用自动采样
    txn.enable_coverage_sampling()
    print("已重新启用自动采样")

    # 测试5: 演示CoverGroup的采样控制
    print_separator("测试5: 采样控制")

    # 禁用特定CoverGroup
    txn.addr_cg.disable_sampling()
    print("\n已禁用 addr_cg 采样")

    txn.randomize()
    print("randomize() 后 - addr_cg未被采样")

    # 重新启用
    txn.addr_cg.enable_sampling()
    print("已重新启用 addr_cg 采样")

    txn.randomize()
    print("randomize() 后 - addr_cg正常采样")

    # 测试6: 演示CoverPoint的启用/禁用
    print_separator("测试6: CoverPoint控制")

    addr_cp = txn.addr_cg.get_coverpoint("addr")
    if addr_cp:
        addr_cp.disable()
        print("\n已禁用 addr coverpoint")

        txn.randomize()
        print("randomize() 后 - addr coverpoint未被采样")

        addr_cp.enable()
        print("已重新启用 addr coverpoint")

    # 最终覆盖率报告
    print_separator("最终覆盖率报告")

    print(f"\n总覆盖率: {txn.get_total_coverage():.2f}%")

    print("\n各CoverGroup覆盖率:")
    for cg_name, cg in txn._covergroups.items():
        print(f"  {cg_name}: {cg.get_coverage():.2f}%")

    print("\n所有随机变量:")
    for var_name in txn.list_rand_vars():
        print(f"  {var_name}")

    print_separator("完成")


if __name__ == "__main__":
    main()
