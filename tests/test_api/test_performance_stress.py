"""
性能压力测试

测试内存使用、长时间运行稳定性等
"""

import pytest
import tracemalloc
import time
from sv_randomizer import Randomizable
from sv_randomizer.api import rand, constraint
from .helpers.scenario_generators import create_n_vars_object


class TestMemoryUsage:
    """内存使用测试"""

    @pytest.mark.parametrize("num_vars,iterations,expected_max_mb", [
        (10, 100, 1),
        (30, 100, 3),
        (50, 100, 5),
    ])
    def test_memory_usage(self, num_vars, iterations, expected_max_mb):
        """测试内存占用"""
        tracemalloc.start()

        cls = create_n_vars_object(num_vars)
        obj = cls()

        for _ in range(iterations):
            obj.randomize()

        current, peak = tracemalloc.get_traced_memory()
        peak_mb = peak / 1024 / 1024

        tracemalloc.stop()

        print(f"  {num_vars}变量: {peak_mb:.2f}MB")
        assert peak_mb < expected_max_mb, f"内存超限: {peak_mb:.2f}MB > {expected_max_mb}MB"


class TestLongRunStability:
    """长时间运行稳定性测试"""

    @pytest.mark.slow
    def test_long_run_stability(self):
        """测试长时间运行的稳定性"""
        cls = create_n_vars_object(20)

        # 添加一些约束使其更真实
        x_rand = rand(int)(bits=8, min=0, max=100)
        y_rand = rand(int)(bits=8, min=0, max=100)

        class ConstrainedObj(Randomizable):
            x: x_rand
            y: y_rand

            @constraint
            def sum_limit(self):
                return self.x + self.y < 150

        obj = ConstrainedObj()

        iterations = 10000
        success_count = 0

        for i in range(iterations):
            if obj.randomize():
                success_count += 1

        success_rate = success_count / iterations
        print(f"  成功率: {success_rate*100:.2f}% ({success_count}/{iterations})")
        assert success_rate >= 0.95, f"成功率过低: {success_rate*100:.2f}%"


class TestPerformanceDistribution:
    """性能分布详细测试"""

    def test_solve_time_distribution(self):
        """测试求解时间分布（识别性能瓶颈）"""
        cls = create_n_vars_object(15)

        # 添加多个约束
        v_rand = [rand(int)(bits=8, min=0, max=100) for _ in range(15)]

        class ConstrainedObj(Randomizable):
            v1: v_rand[0]
            v2: v_rand[1]
            v3: v_rand[2]
            v4: v_rand[3]
            v5: v_rand[4]

            @constraint
            def c1(self):
                return self.v1 + self.v2 < 200

            @constraint
            def c2(self):
                return self.v1 > 10 and self.v2 < 100

            @constraint
            def c3(self):
                return self.v3 < self.v4 < self.v5

        obj = ConstrainedObj()

        times = []
        for _ in range(100):
            start = time.perf_counter()
            obj.randomize()
            elapsed = time.perf_counter() - start
            times.append(elapsed)

        avg_time = sum(times) / len(times)
        max_time = max(times)
        min_time = min(times)

        print(f"  平均: {avg_time*1000:.3f}ms")
        print(f"  最小: {min_time*1000:.3f}ms")
        print(f"  最大: {max_time*1000:.3f}ms")

        # 最大时间不应该超过平均时间的5倍
        assert max_time < avg_time * 5, f"性能不稳定: max={max_time*1000:.3f}ms, avg={avg_time*1000:.3f}ms"
