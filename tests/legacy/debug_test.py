"""
调试测试
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sv_randomizer import Randomizable, RandVar, RandCVar, VarType


class DebugPacket(Randomizable):
    """调试用的简单数据包"""

    def __init__(self):
        super().__init__()
        self._rand_vars['x'] = RandVar('x', VarType.INT, min_val=0, max_val=10)
        print(f"Created rand var: x in range(0, 10)")

    def pre_randomize(self):
        print("  pre_randomize called")

    def post_randomize(self):
        print(f"  post_randomize called: x={self.x}")


# 测试
print("Creating packet...")
pkt = DebugPacket()

print("\nCalling randomize()...")
success = pkt.randomize()
print(f"Result: {success}")

if success:
    print(f"x value: {pkt.x}")
else:
    print("Randomization failed!")

# 检查变量状态
print(f"\n_rand_vars: {pkt._rand_vars}")
print(f"Has 'x' attr: {hasattr(pkt, 'x')}")
