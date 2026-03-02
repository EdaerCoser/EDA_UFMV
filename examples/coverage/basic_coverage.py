"""
Basic Coverage Example - 功能覆盖率基础示例

这个示例展示了如何使用EDA_UFVM的覆盖率系统来验证随机化测试的覆盖范围。

对应SystemVerilog的covergroup和coverpoint概念。
"""

import sys
sys.path.insert(0, '../..')

from sv_randomizer.core.randomizable import Randomizable
from sv_randomizer.core.variables import RandVar, RandCVar, VarType
from coverage.core import CoverGroup, CoverPoint


class Packet(Randomizable):
    """
    数据包类 - 包含随机变量和覆盖率定义

    类似SystemVerilog的：
        class Packet;
            rand bit [15:0] addr;
            rand bit [7:0]  opcode;
            rand bit [31:0] data;
        endclass
    """

    def __init__(self):
        super().__init__()

        # 定义随机变量（对应SystemVerilog的rand变量）
        self._rand_vars['addr'] = RandVar('addr', VarType.BIT, bit_width=16)
        self._rand_vars['opcode'] = RandVar('opcode', VarType.BIT, bit_width=8)
        self._rand_vars['data'] = RandVar('data', VarType.BIT, bit_width=32)

        # 创建覆盖率组
        self._setup_coverage()

    def _setup_coverage(self):
        """设置覆盖率组"""

        # 创建CoverGroup（对应SystemVerilog的covergroup）
        self.addr_cg = CoverGroup("addr_coverage")

        # 创建CoverPoint for addr（对应coverpoint addr）
        addr_cp = CoverPoint(
            name="addr_cp",
            sample_expr="addr",  # 采样变量名
            bins={
                # 定义范围bins（对应 bins ranges[] = {[0:255], [256:511], ...}）
                "ranges": [[0, 0xFF], [0x100, 0x1FF], [0x200, 0x2FF]],
                # 忽略的值（对应 ignore_bins）
                "ignore": [0],
            },
            weight=1.0
        )
        self.addr_cg.add_coverpoint(addr_cp)

        # 创建CoverPoint for opcode
        opcode_cp = CoverPoint(
            name="opcode_cp",
            sample_expr="opcode",
            bins={
                # 值bins（对应 bins values[] = {0, 1, 2, 3}）
                "values": [0, 1, 2, 3],
            }
        )
        self.addr_cg.add_coverpoint(opcode_cp)

        # 将CoverGroup添加到Randomizable对象
        # 这样randomize()时会自动采样覆盖率
        self.add_covergroup(self.addr_cg)

    def post_randomize(self):
        """随机化后回调 - 打印数据包信息"""
        super().post_randomize()
        print(f"Packet: addr=0x{self.addr:04X}, opcode={self.opcode}, data=0x{self.data:08X}")


def main():
    """主测试函数"""

    print("=" * 60)
    print("EDA_UFVM 功能覆盖率系统 - 基础示例")
    print("=" * 60)

    # 创建数据包对象
    pkt = Packet()

    # 生成100个随机数据包并自动采样覆盖率
    print("\n生成100个随机数据包...")
    for i in range(100):
        pkt.randomize()

    print("\n" + "=" * 60)
    print("覆盖率报告")
    print("=" * 60)

    # 获取总覆盖率
    total_coverage = pkt.get_total_coverage()
    print(f"\n总覆盖率: {total_coverage:.2f}%")

    # 获取各个CoverGroup的覆盖率
    print("\n详细覆盖率:")
    for cg_name, coverage in pkt.get_coverage().items():
        print(f"  {cg_name}: {coverage:.2f}%")

    # 获取覆盖率详细信息
    print("\n覆盖率详细信息:")
    details = pkt.addr_cg.get_coverage_details()

    print(f"  CoverGroup: {details['name']}")
    print(f"  总覆盖率: {details['coverage']:.2f}%")
    print(f"  采样次数: {details['sample_count']}")

    # 每个CoverPoint的详情
    for cp_name, cp_details in details['coverpoints'].items():
        print(f"\n  CoverPoint: {cp_name}")
        print(f"    覆盖率: {cp_details['coverage']:.2f}%")
        print(f"    总bin数: {cp_details['total_bins']}")
        print(f"    已覆盖bin数: {cp_details['covered_bins']}")
        print(f"    采样次数: {cp_details['sample_count']}")

    # 显示每个bin的命中情况
    print("\n  Bin命中详情:")
    for bin_name, bin_info in cp_details['bins'].items():
        status = "X" if bin_info['hit_count'] > 0 else " "
        print(f"    [{status}] {bin_name}: {bin_info['hit_count']} 次 - {bin_info['definition']}")

    print("\n" + "=" * 60)
    print("完成！")
    print("=" * 60)


if __name__ == "__main__":
    main()
