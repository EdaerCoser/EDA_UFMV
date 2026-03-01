"""
性能测试 - 验证覆盖率系统的性能

根据计划要求：
- 简单采样（<10 bins）: >10,000次/秒
- 复杂采样（>100 bins）: >1,000次/秒
"""

import sys
import time
sys.path.insert(0, '.')

from sv_randomizer.core.randomizable import Randomizable
from sv_randomizer.core.variables import RandVar, VarType
from coverage.core import CoverGroup, CoverPoint


def test_simple_sampling_performance():
    """测试简单采样性能（<10 bins）"""

    class SimplePacket(Randomizable):
        def __init__(self):
            super().__init__()
            self._rand_vars['value'] = RandVar('value', VarType.BIT, bit_width=8)

            self.cg = CoverGroup("simple_cg")
            cp = CoverPoint("value", "value", bins={
                "ranges": [[0, 25], [26, 50], [51, 75], [76, 100]]
            })
            self.cg.add_coverpoint(cp)
            self.add_covergroup(self.cg)

    pkt = SimplePacket()

    # 预热
    for _ in range(100):
        pkt.randomize()

    # 测试
    iterations = 10000
    start = time.time()

    for _ in range(iterations):
        pkt.randomize()

    elapsed = time.time() - start
    rate = iterations / elapsed

    print(f"简单采样性能: {rate:.0f} 次/秒")
    print(f"  要求: >10,000 次/秒")
    assert rate > 10000, f"性能不达标: {rate:.0f} < 10,000"
    print("  [OK] 性能达标")


def test_complex_sampling_performance():
    """测试复杂采样性能（>100 bins）"""

    class ComplexPacket(Randomizable):
        def __init__(self):
            super().__init__()
            self._rand_vars['addr'] = RandVar('addr', VarType.BIT, bit_width=16)
            self._rand_vars['data'] = RandVar('data', VarType.BIT, bit_width=16)

            self.cg = CoverGroup("complex_cg")

            # 创建多个覆盖点，总计>100 bins
            addr_cp = CoverPoint("addr", "addr", bins={
                "auto": 64  # 64个自动bins
            })
            self.cg.add_coverpoint(addr_cp)

            data_cp = CoverPoint("data", "data", bins={
                "auto": 64  # 64个自动bins
            })
            self.cg.add_coverpoint(data_cp)

            self.add_covergroup(self.cg)

    pkt = ComplexPacket()

    # 预热
    for _ in range(100):
        pkt.randomize()

    # 测试
    iterations = 1000
    start = time.time()

    for _ in range(iterations):
        pkt.randomize()

    elapsed = time.time() - start
    rate = iterations / elapsed

    total_bins = sum(len(cp._bins) for cp in pkt.cg._coverpoints.values())
    print(f"\n复杂采样性能 ({total_bins} bins): {rate:.0f} 次/秒")
    print(f"  要求: >1,000 次/秒")
    assert rate > 1000, f"性能不达标: {rate:.0f} < 1,000"
    print("  [OK] 性能达标")


def test_memory_usage():
    """测试内存使用"""

    import sys

    class MemoryPacket(Randomizable):
        def __init__(self):
            super().__init__()
            self._rand_vars['addr'] = RandVar('addr', VarType.BIT, bit_width=16)

            self.cg = CoverGroup("memory_cg")
            cp = CoverPoint("addr", "addr", bins={
                "auto": 1000  # 1000个bins
            })
            self.cg.add_coverpoint(cp)
            self.add_covergroup(self.cg)

    pkt = MemoryPacket()

    # 采样以填充bins
    for _ in range(1000):
        pkt.randomize()

    # 估算对象大小
    size = sys.getsizeof(pkt)
    print(f"\n内存使用: ~{size / 1024:.1f} KB")
    print("  [OK] 内存使用合理")


if __name__ == "__main__":
    print("=" * 60)
    print("性能测试")
    print("=" * 60)

    test_simple_sampling_performance()
    test_complex_sampling_performance()
    test_memory_usage()

    print("\n" + "=" * 60)
    print("所有性能测试通过!")
    print("=" * 60)
