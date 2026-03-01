"""
随机种子控制功能演示 - 新API版本

演示如何使用随机种子控制功能来确保测试的可重复性
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sv_randomizer import Randomizable, seed
from sv_randomizer.api import rand, randc, constraint


class DataPacket(Randomizable):
    """数据包类，包含地址、长度和数据字段 - 使用新API"""

    addr: rand[int](min=0, max=65535)
    length: rand[int](min=1, max=256)
    id: randc[int](bits=4)

    @constraint
    def addr_length_sum(self):
        """约束：addr + length < 1000"""
        return self.addr + self.length < 1000


def demo_global_seed():
    """演示全局种子功能"""
    print("=" * 60)
    print("演示1: 全局种子")
    print("=" * 60)

    # 设置全局种子
    seed(42)

    print("\n使用全局种子42生成5个数据包:")
    for i in range(5):
        pkt = DataPacket()
        pkt.randomize()
        print(f"  包{i+1}: addr={pkt.addr:5d}, length={pkt.length:3d}, id={pkt.id:2d}")

    # 重置全局种子并再次生成
    from sv_randomizer import reset_global_seed
    reset_global_seed()
    seed(42)

    print("\n重置全局种子为42，再次生成5个数据包（应相同）:")
    for i in range(5):
        pkt = DataPacket()
        pkt.randomize()
        print(f"  包{i+1}: addr={pkt.addr:5d}, length={pkt.length:3d}, id={pkt.id:2d}")

    reset_global_seed()


def demo_object_seed():
    """演示对象级种子"""
    print("\n" + "=" * 60)
    print("演示2: 对象级种子")
    print("=" * 60)

    print("\n使用对象级种子123生成数据:")
    pkt = DataPacket()
    pkt.set_seed(123)

    for i in range(5):
        pkt.randomize()
        print(f"  次数{i+1}: addr={pkt.addr:5d}, length={pkt.length:3d}, id={pkt.id:2d}")

    print("\n使用相同种子123创建新对象（应重复序列）:")
    pkt2 = DataPacket()
    pkt2.set_seed(123)
    for i in range(5):
        pkt2.randomize()
        print(f"  次数{i+1}: addr={pkt2.addr:5d}, length={pkt2.length:3d}, id={pkt2.id:2d}")


def demo_temporary_seed():
    """演示临时种子"""
    print("\n" + "=" * 60)
    print("演示3: 临时种子")
    print("=" * 60)

    pkt = DataPacket()
    pkt.set_seed(42)

    print("\n正常randomize（使用对象种子42）:")
    pkt.randomize()
    print(f"  第1次: addr={pkt.addr}, length={pkt.length}, id={pkt.id}")

    pkt.randomize()
    print(f"  第2次: addr={pkt.addr}, length={pkt.length}, id={pkt.id}")

    print("\n使用临时种子999（不影响对象状态）:")
    pkt.randomize(seed=999)
    print(f"  临时种子: addr={pkt.addr}, length={pkt.length}, id={pkt.id}")

    print("\n恢复对象级种子42:")
    pkt.randomize()
    print(f"  第3次: addr={pkt.addr}, length={pkt.length}, id={pkt.id}")

    print("\n再次使用临时种子999（应产生相同值）:")
    pkt.randomize(seed=999)
    print(f"  临时种子: addr={pkt.addr}, length={pkt.length}, id={pkt.id}")


def demo_randc_cycle():
    """演示RandCVar循环"""
    print("\n" + "=" * 60)
    print("演示4: RandCVar完整循环（4位 = 16个值）")
    print("=" * 60)

    pkt = DataPacket()
    pkt.set_seed(42)

    print("\n生成16个唯一ID:")
    seen = []
    for i in range(16):
        pkt.randomize()
        seen.append(pkt.id)
        if i < 8 or i == 15:
            print(f"  ID {i+1:2d}: {pkt.id:2d}", end="  ")
            if (i + 1) % 4 == 0 or i == 15:
                print()

    unique_count = len(set(seen))
    print(f"\n唯一值数量: {unique_count}/16")

    print("\n第17次randomize（应开始重复）:")
    pkt.randomize()
    print(f"  ID 17: {pkt.id}")
    is_duplicate = pkt.id in seen
    print(f"  是否重复: {'是' if is_duplicate else '否'}")


def demo_reproducibility():
    """演示可重现性"""
    print("\n" + "=" * 60)
    print("演示5: 测试可重现性")
    print("=" * 60)

    print("\n场景：模拟测试失败，记录种子以便重现")
    import time
    failed_seed = int(time.time()) % 10000

    print(f"\n模拟测试运行，种子={failed_seed}")
    pkt = DataPacket()
    pkt.set_seed(failed_seed)
    pkt.randomize()

    # 模拟"失败"条件
    if pkt.addr > 50000 and pkt.length < 50:
        print(f"  [警告] 测试失败！addr={pkt.addr}, length={pkt.length}")
        print(f"  记录种子: {failed_seed}")

    print("\n使用记录的种子重现问题:")
    pkt2 = DataPacket()
    pkt2.set_seed(failed_seed)
    pkt2.randomize()
    print(f"  重现: addr={pkt2.addr}, length={pkt2.length}")

    if pkt.addr == pkt2.addr and pkt.length == pkt2.length:
        print("  [OK] 成功重现！")


def demo_set_seed_method():
    """演示set_seed方法"""
    print("\n" + "=" * 60)
    print("演示6: 动态设置种子")
    print("=" * 60)

    pkt = DataPacket()

    print("\n使用set_seed()方法动态改变种子:")

    for seed_val in [100, 200, 300]:
        pkt.set_seed(seed_val)
        pkt.randomize()
        print(f"  种子{seed_val}: addr={pkt.addr:5d}, length={pkt.length:3d}, id={pkt.id:2d}")

    print("\n验证：使用相同种子100:")
    pkt.set_seed(100)
    pkt.randomize()
    print(f"  种子100: addr={pkt.addr:5d}, length={pkt.length:3d}, id={pkt.id:2d}")


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("随机种子控制功能演示 (新API)")
    print("=" * 60)

    demo_global_seed()
    demo_object_seed()
    demo_temporary_seed()
    demo_randc_cycle()
    demo_reproducibility()
    demo_set_seed_method()

    print("\n" + "=" * 60)
    print("演示完成！")
    print("=" * 60)
