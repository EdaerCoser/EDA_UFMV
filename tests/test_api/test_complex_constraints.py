"""
复杂约束测试 - 数学/逻辑约束场景

测试高维方程组、资源分配等抽象数学约束场景
"""

import pytest
from sv_randomizer import Randomizable
from sv_randomizer.api import rand, constraint


class TestWeightedConstraints5Vars:
    """5变量加权约束测试"""

    def test_5var_weighted_sum(self):
        """测试5变量加权和约束"""
        v1 = rand(int)(bits=6, min=0, max=50)
        v2 = rand(int)(bits=6, min=0, max=50)
        v3 = rand(int)(bits=6, min=0, max=50)
        v4 = rand(int)(bits=6, min=0, max=50)
        v5 = rand(int)(bits=6, min=0, max=50)

        class WeightedSum5Vars(Randomizable):
            val1: v1
            val2: v2
            val3: v3
            val4: v4
            val5: v5

            @constraint
            def weighted_total(self):
                return (2*self.val1 + 3*self.val2 + self.val3 +
                        4*self.val4 + 2*self.val5) == 100

        obj = WeightedSum5Vars()
        success_count = 0
        for _ in range(100):
            if obj.randomize():
                success_count += 1
                total = (2*obj.val1 + 3*obj.val2 + obj.val3 +
                        4*obj.val4 + 2*obj.val5)
                assert total == 100
                if success_count >= 10:
                    break

        # This is a moderate constraint, should find solutions
        assert success_count >= 5, f"Expected at least 5 successful randomizations, got {success_count}"

    def test_5var_weighted_sum_with_bounds(self):
        """测试5变量加权和+边界约束"""
        v1 = rand(int)(bits=6, min=0, max=50)
        v2 = rand(int)(bits=6, min=0, max=50)
        v3 = rand(int)(bits=6, min=0, max=50)
        v4 = rand(int)(bits=6, min=0, max=50)
        v5 = rand(int)(bits=6, min=0, max=50)

        class WeightedSumWithBounds(Randomizable):
            val1: v1
            val2: v2
            val3: v3
            val4: v4
            val5: v5

            @constraint
            def weighted_total(self):
                return (2*self.val1 + 3*self.val2 + self.val3 +
                        4*self.val4 + 2*self.val5) == 100

            @constraint
            def min_values(self):
                return (self.val1 >= 5 and self.val2 >= 5 and self.val3 >= 5)

        obj = WeightedSumWithBounds()
        success_count = 0
        for _ in range(100):
            if obj.randomize():
                success_count += 1
                total = (2*obj.val1 + 3*obj.val2 + obj.val3 +
                        4*obj.val4 + 2*obj.val5)
                assert total == 100
                assert obj.val1 >= 5 and obj.val2 >= 5 and obj.val3 >= 5
                if success_count >= 5:
                    break

        # More constrained with minimum values
        assert success_count >= 2, f"Expected at least 2 successful randomizations, got {success_count}"


class TestResourceAllocation6Vars:
    """6变量资源分配测试"""

    def test_6var_total_allocation(self):
        """测试6变量资源总和约束"""
        vars = [rand(int)(bits=7, min=0, max=100) for _ in range(6)]

        class ResourceAllocation6Vars(Randomizable):
            r1: vars[0]
            r2: vars[1]
            r3: vars[2]
            r4: vars[3]
            r5: vars[4]
            r6: vars[5]

            @constraint
            def total_100_percent(self):
                return self.r1 + self.r2 + self.r3 + self.r4 + self.r5 + self.r6 == 100

        obj = ResourceAllocation6Vars()
        success_count = 0
        for _ in range(50):
            if obj.randomize():
                success_count += 1
                total = obj.r1 + obj.r2 + obj.r3 + obj.r4 + obj.r5 + obj.r6
                assert total == 100
                if success_count >= 10:
                    break

        # This is a moderately constrained problem
        assert success_count >= 5, f"Expected at least 5 successful randomizations, got {success_count}"

    def test_6var_min_allocation(self):
        """测试每个资源池最小分配"""
        vars = [rand(int)(bits=7, min=0, max=100) for _ in range(6)]

        class ResourceAllocation6Vars(Randomizable):
            r1: vars[0]
            r2: vars[1]
            r3: vars[2]
            r4: vars[3]
            r5: vars[4]
            r6: vars[5]

            @constraint
            def total_100_percent(self):
                return self.r1 + self.r2 + self.r3 + self.r4 + self.r5 + self.r6 == 100

            @constraint
            def min_each_pool(self):
                return (self.r1 >= 5 and self.r2 >= 5 and self.r3 >= 5 and
                        self.r4 >= 5 and self.r5 >= 5 and self.r6 >= 5)

        obj = ResourceAllocation6Vars()
        success_count = 0
        for _ in range(100):
            if obj.randomize():
                success_count += 1
                assert obj.r1 >= 5 and obj.r2 >= 5 and obj.r3 >= 5
                assert obj.r4 >= 5 and obj.r5 >= 5 and obj.r6 >= 5
                if success_count >= 5:
                    break

        # 6*5=30 minimum, leaving 70 to distribute - should be doable
        assert success_count >= 3, f"Expected at least 3 successful randomizations, got {success_count}"


class TestLogicalConstraints8Vars:
    """8变量逻辑约束测试"""

    def test_8var_inequality_system(self):
        """测试8变量不等式系统"""
        vars = [rand(int)(bits=6, min=0, max=100) for _ in range(8)]

        class InequalitySystem8Vars(Randomizable):
            v1: vars[0]
            v2: vars[1]
            v3: vars[2]
            v4: vars[3]
            v5: vars[4]
            v6: vars[5]
            v7: vars[6]
            v8: vars[7]

            @constraint
            def increasing_sequence(self):
                return (self.v1 <= self.v2 and self.v2 <= self.v3 and
                        self.v3 <= self.v4 and self.v4 <= self.v5 and
                        self.v5 <= self.v6 and self.v6 <= self.v7 and
                        self.v7 <= self.v8)

            @constraint
            def range_constraint(self):
                return (self.v8 - self.v1 >= 20)

        obj = InequalitySystem8Vars()
        success_count = 0
        for _ in range(100):
            if obj.randomize():
                success_count += 1
                assert obj.v1 <= obj.v2 <= obj.v3 <= obj.v4 <= obj.v5 <= obj.v6 <= obj.v7 <= obj.v8
                assert obj.v8 - obj.v1 >= 20
                if success_count >= 10:
                    break

        # Monotonic sequence constraint is reasonable
        assert success_count >= 5, f"Expected at least 5 successful randomizations, got {success_count}"

    def test_8var_sum_bounds(self):
        """测试8变量总和边界约束"""
        vars = [rand(int)(bits=6, min=0, max=50) for _ in range(8)]

        class SumBounds8Vars(Randomizable):
            a1: vars[0]
            a2: vars[1]
            a3: vars[2]
            a4: vars[3]
            b1: vars[4]
            b2: vars[5]
            b3: vars[6]
            b4: vars[7]

            @constraint
            def sum_range(self):
                # Both groups must sum to at least 80
                return ((self.a1 + self.a2 + self.a3 + self.a4) >= 80 and
                        (self.b1 + self.b2 + self.b3 + self.b4) >= 80)

        obj = SumBounds8Vars()
        success_count = 0
        for _ in range(50):
            if obj.randomize():
                success_count += 1
                sum_a = obj.a1 + obj.a2 + obj.a3 + obj.a4
                sum_b = obj.b1 + obj.b2 + obj.b3 + obj.b4
                assert sum_a >= 80
                assert sum_b >= 80
                if success_count >= 10:
                    break

        # Lower bound constraints are reasonable
        assert success_count >= 5, f"Expected at least 5 successful randomizations, got {success_count}"


class TestConditionalConstraints7Vars:
    """7变量条件约束测试"""

    def test_7var_conditional_ranges(self):
        """测试7变量条件范围约束"""
        vars = [rand(int)(bits=6, min=0, max=100) for _ in range(7)]

        class ConditionalRanges7Vars(Randomizable):
            x1: vars[0]
            x2: vars[1]
            x3: vars[2]
            x4: vars[3]
            x5: vars[4]
            x6: vars[5]
            x7: vars[6]

            @constraint
            def conditional_high(self):
                # If x1 > 50, then x2 must be > 30
                return (self.x1 <= 50) or (self.x2 > 30)

            @constraint
            def conditional_low(self):
                # If x7 < 20, then x6 must be < 40
                return (self.x7 >= 20) or (self.x6 < 40)

            @constraint
            def mutual_exclusion(self):
                # x3 and x4 cannot both be high
                return (self.x3 <= 60) or (self.x4 <= 60)

        obj = ConditionalRanges7Vars()
        success_count = 0
        for _ in range(50):
            if obj.randomize():
                success_count += 1
                # Verify conditional constraints
                assert (obj.x1 <= 50) or (obj.x2 > 30)
                assert (obj.x7 >= 20) or (obj.x6 < 40)
                assert (obj.x3 <= 60) or (obj.x4 <= 60)
                if success_count >= 10:
                    break

        # Conditional constraints should be easy
        assert success_count >= 8, f"Expected at least 8 successful randomizations, got {success_count}"
