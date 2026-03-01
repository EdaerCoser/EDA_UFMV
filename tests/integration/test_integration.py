"""
集成测试 - 验证覆盖率系统与Randomizable的完整集成
"""

import sys
sys.path.insert(0, '.')

from sv_randomizer.core.randomizable import Randomizable
from sv_randomizer.core.variables import RandVar, VarType
from coverage.core import CoverGroup, CoverPoint


def test_full_integration():
    """测试完整的覆盖率系统集成"""

    # 创建测试类
    class TestPacket(Randomizable):
        def __init__(self):
            super().__init__()

            # 定义随机变量
            self._rand_vars['addr'] = RandVar('addr', VarType.BIT, bit_width=16)
            self._rand_vars['data'] = RandVar('data', VarType.BIT, bit_width=8)

            # 创建覆盖率组
            self.cg = CoverGroup("test_cg")

            # 添加覆盖点
            addr_cp = CoverPoint("addr", "addr", bins={
                "ranges": [[0, 5000], [5001, 10000], [10001, 20000], [20001, 30000], [30001, 65535]]
            })
            self.cg.add_coverpoint(addr_cp)

            data_cp = CoverPoint("data", "data", bins={
                "values": [0, 1, 2, 3, 4]
            })
            self.cg.add_coverpoint(data_cp)

            # 添加到Randomizable
            self.add_covergroup(self.cg)

    # 测试1: 基本功能
    print("测试1: 基本功能")
    pkt = TestPacket()
    # 未采样时覆盖率应该是0%（除非没有bins）
    assert pkt.get_total_coverage() == 0.0, "未采样时覆盖率应该是0%"

    # 测试2: 自动采样
    print("测试2: 自动采样")
    for _ in range(50):
        pkt.randomize()

    coverage = pkt.get_total_coverage()
    print(f"  覆盖率: {coverage:.2f}%")
    assert coverage > 0, "应该有部分覆盖率"

    # 测试3: 覆盖率详情
    print("测试3: 覆盖率详情")
    details = pkt.cg.get_coverage_details()
    assert 'coverpoints' in details
    assert len(details['coverpoints']) == 2

    # 测试4: 启用/禁用
    print("测试4: 启用/禁用")
    pkt.disable_coverage_sampling()
    old_coverage = coverage

    for _ in range(10):
        pkt.randomize()

    new_coverage = pkt.get_total_coverage()
    assert old_coverage == new_coverage, "禁用后覆盖率不应变化"

    pkt.enable_coverage_sampling()

    # 测试5: CoverPoint级别控制
    print("测试5: CoverPoint级别控制")
    addr_cp = pkt.cg.get_coverpoint("addr")
    addr_cp.disable()

    for _ in range(10):
        pkt.randomize()

    # 测试6: 数据完整性
    print("测试6: 数据完整性")
    assert hasattr(pkt, 'addr')
    assert hasattr(pkt, 'data')
    assert pkt.cg._instance_count > 0

    print("\n所有集成测试通过!")
    return True


if __name__ == "__main__":
    test_full_integration()
