"""
使用SV Randomizer求解五元一次不等式组 - 新API版本

示例问题：
求解满足以下条件的五元组 (x1, x2, x3, x4, x5)：

约束条件：
1. x1 + x2 + x3 + x4 + x5 < 100
2. x1 > 0, x2 > 0, x3 > 0, x4 > 0, x5 > 0
3. x1 >= x2 >= x3 >= x4 >= x5 (递减序列)
4. x1 + x2 > 50
5. x4 + x5 < 20
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sv_randomizer import Randomizable
from sv_randomizer.api import rand, constraint


class FiveVariableInequality(Randomizable):
    """五元一次不等式求解器 - 使用新API"""

    # 定义5个变量：x1, x2, x3, x4, x5
    x1: rand[int](min=1, max=99)
    x2: rand[int](min=1, max=99)
    x3: rand[int](min=1, max=99)
    x4: rand[int](min=1, max=99)
    x5: rand[int](min=1, max=99)

    # 定义约束 - 使用原生Python表达式

    @constraint
    def sum_less_than_100(self):
        """约束1: x1 + x2 + x3 + x4 + x5 < 100"""
        return self.x1 + self.x2 + self.x3 + self.x4 + self.x5 < 100

    @constraint
    def all_positive(self):
        """约束2: 所有变量 > 0"""
        return self.x1 > 0 and self.x2 > 0 and self.x3 > 0 and self.x4 > 0 and self.x5 > 0

    @constraint
    def decreasing_sequence(self):
        """约束3: x1 >= x2 >= x3 >= x4 >= x5 (递减序列)"""
        return self.x1 >= self.x2 >= self.x3 >= self.x4 >= self.x5

    @constraint
    def x1_x2_greater_than_50(self):
        """约束4: x1 + x2 > 50"""
        return self.x1 + self.x2 > 50

    @constraint
    def x4_x5_less_than_20(self):
        """约束5: x4 + x5 < 20"""
        return self.x4 + self.x5 < 20


def solve_and_display():
    """求解并显示结果"""
    print("=" * 70)
    print("五元一次不等式求解 (新API)")
    print("=" * 70)
    print("\n问题：求解满足以下条件的五元组 (x1, x2, x3, x4, x5)")
    print()
    print("约束条件：")
    print("  1. x1 + x2 + x3 + x4 + x5 < 100")
    print("  2. x1, x2, x3, x4, x5 > 0")
    print("  3. x1 >= x2 >= x3 >= x4 >= x5 (递减序列)")
    print("  4. x1 + x2 > 50")
    print("  5. x4 + x5 < 20")
    print()
    print("=" * 70)
    print()

    solver = FiveVariableInequality()

    print("求解中...\n")

    # 生成10个解
    solutions = []
    for i in range(50):  # 尝试50次，收集成功的解
        if solver.randomize():
            # 验证约束
            total = solver.x1 + solver.x2 + solver.x3 + solver.x4 + solver.x5
            valid = (
                total < 100 and
                solver.x1 > 0 and solver.x2 > 0 and solver.x3 > 0 and
                solver.x4 > 0 and solver.x5 > 0 and
                solver.x1 >= solver.x2 >= solver.x3 >= solver.x4 >= solver.x5 and
                solver.x1 + solver.x2 > 50 and
                solver.x4 + solver.x5 < 20
            )

            if valid:
                solution = {
                    'x1': solver.x1, 'x2': solver.x2, 'x3': solver.x3,
                    'x4': solver.x4, 'x5': solver.x5, 'sum': total
                }
                if solution not in solutions:
                    solutions.append(solution)

            if len(solutions) >= 10:
                break

    # 显示结果
    if solutions:
        print(f"找到 {len(solutions)} 个不同的解：\n")
        for i, sol in enumerate(solutions[:10], 1):
            print(f"解 {i}:")
            print(f"  (x1, x2, x3, x4, x5) = ({sol['x1']:2d}, {sol['x2']:2d}, {sol['x3']:2d}, {sol['x4']:2d}, {sol['x5']:2d})")
            print(f"  验证:")
            print(f"    总和 = {sol['sum']} < 100 [OK]")
            print(f"    递减 = {sol['x1']} >= {sol['x2']} >= {sol['x3']} >= {sol['x4']} >= {sol['x5']} [OK]")
            print(f"    x1+x2 = {sol['x1']+sol['x2']} > 50 [OK]")
            print(f"    x4+x5 = {sol['x4']+sol['x5']} < 20 [OK]")
            print()
    else:
        print("未找到满足条件的解（可能需要更多迭代或调整约束）")

    print("=" * 70)


def solve_custom_inequality():
    """自定义不等式求解示例"""
    print("\n" + "=" * 70)
    print("自定义不等式求解")
    print("=" * 70)
    print("\n示例：求 2a + 3b - c < 50，其中 a>0, b>0, c>0, a<b<c\n")

    a_rand = rand[int](min=1, max=30)
    b_rand = rand[int](min=1, max=30)
    c_rand = rand[int](min=1, max=50)

    class CustomInequality(Randomizable):
        a: a_rand
        b: b_rand
        c: c_rand

        @constraint
        def main_constraint(self):
            """2a + 3b - c < 50"""
            return 2 * self.a + 3 * self.b - self.c < 50

        @constraint
        def a_less_than_b(self):
            """a < b"""
            return self.a < self.b

        @constraint
        def b_less_than_c(self):
            """b < c"""
            return self.b < self.c

    solver = CustomInequality()

    print("找到的解：")
    for i in range(10):
        if solver.randomize():
            result = 2 * solver.a + 3 * solver.b - solver.c
            print(f"  a={solver.a:2d}, b={solver.b:2d}, c={solver.c:2d} => 2a+3b-c = {result} < 50 [OK]")

    print("=" * 70)


if __name__ == "__main__":
    solve_and_display()
    solve_custom_inequality()
