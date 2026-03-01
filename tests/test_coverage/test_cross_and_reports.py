"""
Unit tests for Cross Coverage and Report Generators

测试Cross覆盖功能和报告生成器。
"""

import pytest
import tempfile
import os
from pathlib import Path

from sv_randomizer.coverage.core import Cross, CrossBuilder, create_cross, CoverGroup, CoverPoint
from sv_randomizer.coverage.formatters import (
    HTMLCoverageReport,
    JSONCoverageReport,
    UCISCoverageReport,
    ReportFactory,
    create_report,
    generate_report
)


class TestCross:
    """测试Cross覆盖"""

    def test_init(self):
        """测试Cross初始化"""
        cross = Cross("test_cross", ["cp1", "cp2"])
        assert cross.name == "test_cross"
        assert cross._coverpoint_names == ["cp1", "cp2"]
        assert cross.is_enabled() is True

    def test_with_filter(self):
        """测试带过滤函数的Cross"""
        filter_func = lambda bins: bins[0] != "illegal"
        cross = Cross("filtered_cross", ["cp1", "cp2"], cross_filter=filter_func)
        assert cross._cross_filter == filter_func

    def test_enable_disable(self):
        """测试启用/禁用Cross"""
        cross = Cross("test_cross", ["cp1", "cp2"])

        cross.disable()
        assert cross.is_enabled() is False

        cross.enable()
        assert cross.is_enabled() is True


class TestCrossBuilder:
    """测试Cross构建器"""

    def test_builder_basic(self):
        """测试基本构建"""
        cross = (CrossBuilder("test_cross")
                 .add_coverpoints("cp1", "cp2")
                 .build())

        assert cross.name == "test_cross"
        assert cross._coverpoint_names == ["cp1", "cp2"]

    def test_builder_with_filter(self):
        """测试带过滤的构建"""
        filter_func = lambda bins: True
        cross = (CrossBuilder("test_cross")
                 .add_coverpoint("cp1")
                 .add_coverpoint("cp2")
                 .with_filter(filter_func)
                 .build())

        assert cross._cross_filter == filter_func

    def test_builder_empty_raises_error(self):
        """测试空Cross抛出异常"""
        builder = CrossBuilder("empty_cross")

        with pytest.raises(ValueError):
            builder.build()


class TestCreateCross:
    """测试便捷函数"""

    def test_create_cross(self):
        """测试create_cross函数"""
        builder = create_cross("test_cross", "cp1", "cp2")
        assert isinstance(builder, CrossBuilder)

        cross = builder.build()
        assert cross.name == "test_cross"


class TestCrossIntegration:
    """测试Cross与CoverGroup集成"""

    def test_cross_in_covergroup(self):
        """测试Cross在CoverGroup中"""
        cg = CoverGroup("test_cg")

        # 添加CoverPoints
        cp1 = CoverPoint("cp1", "val1", bins={"values": [1, 2]})
        cp2 = CoverPoint("cp2", "val2", bins={"values": [3, 4]})
        cg.add_coverpoint(cp1)
        cg.add_coverpoint(cp2)

        # 添加Cross
        cross = Cross("cross", ["cp1", "cp2"])
        cg.add_cross(cross)

        # 验证父关系
        assert cross._parent == cg

    def test_cross_sampling(self):
        """测试Cross采样"""
        cg = CoverGroup("test_cg")

        cp1 = CoverPoint("cp1", "val1", bins={"values": [1, 2]})
        cp2 = CoverPoint("cp2", "val2", bins={"values": [3, 4]})
        cg.add_coverpoint(cp1)
        cg.add_coverpoint(cp2)

        cross = Cross("cross", ["cp1", "cp2"])
        cg.add_cross(cross)

        # 采样
        cg.sample(val1=1, val2=3)

        # 验证Cross计数
        assert cross._sample_count == 1


class TestHTMLReport:
    """测试HTML报告生成器"""

    def test_get_format(self):
        """测试获取格式"""
        reporter = HTMLCoverageReport()
        assert reporter.get_format() == "html"

    def test_generate_basic(self):
        """测试生成基本HTML报告"""
        reporter = HTMLCoverageReport("Test Report")

        data = {
            "title": "Test Coverage",
            "covergroups": [
                {
                    "name": "cg1",
                    "coverage": 85.5,
                    "sample_count": 100,
                    "coverpoints": {
                        "cp1": {
                            "coverage": 80.0,
                            "sample_count": 50,
                            "total_bins": 5,
                            "covered_bins": 4,
                            "weight": 1.0,
                            "weighted_coverage": 80.0,
                            "bins": {
                                "bin1": {"hit_count": 10, "type": "ValueBin"},
                                "bin2": {"hit_count": 0, "type": "ValueBin"}
                            }
                        }
                    }
                }
            ]
        }

        html = reporter.generate(data)

        assert "<!DOCTYPE html>" in html
        assert "Test Coverage" in html
        assert "85.50%" in html
        assert "cg1" in html

    def test_save_report(self):
        """测试保存报告"""
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = os.path.join(tmpdir, "test_report.html")
            reporter = HTMLCoverageReport()

            data = {
                "title": "Test",
                "covergroups": []
            }

            content = reporter.generate(data)
            saved_path = reporter.save(content, filepath)

            assert os.path.exists(saved_path)
            assert saved_path == filepath


class TestJSONReport:
    """测试JSON报告生成器"""

    def test_get_format(self):
        """测试获取格式"""
        reporter = JSONCoverageReport()
        assert reporter.get_format() == "json"

    def test_generate_basic(self):
        """测试生成JSON报告"""
        reporter = JSONCoverageReport("Test Report")

        data = {
            "title": "Test Coverage",
            "covergroups": [
                {
                    "name": "cg1",
                    "coverage": 85.5,
                    "sample_count": 100,
                    "coverpoints": {}
                }
            ]
        }

        json_str = reporter.generate(data)

        import json
        parsed = json.loads(json_str)

        assert parsed["title"] == "Test Coverage"
        assert parsed["summary"]["total_coverage"] == 85.5
        assert len(parsed["covergroups"]) == 1


class TestUCISReport:
    """测试UCIS报告生成器"""

    def test_get_format(self):
        """测试获取格式"""
        reporter = UCISCoverageReport()
        assert reporter.get_format() == "ucis"

    def test_generate_basic(self):
        """测试生成UCIS报告"""
        reporter = UCISCoverageReport("Test Report")

        data = {
            "title": "Test Coverage",
            "covergroups": [
                {
                    "name": "cg1",
                    "coverage": 85.5,
                    "sample_count": 100,
                    "coverpoints": {
                        "cp1": {
                            "coverage": 80.0,
                            "total_bins": 5,
                            "covered_bins": 4,
                            "sample_count": 50,
                            "weight": 1.0,
                            "weighted_coverage": 80.0,
                            "bins": {
                                "bin1": {"hit_count": 10, "type": "ValueBin"}
                            }
                        }
                    }
                }
            ]
        }

        ucis = reporter.generate(data)

        assert '<?xml version="1.0"' in ucis
        assert '<ucis' in ucis
        assert 'cg1' in ucis
        assert '85.5' in ucis


class TestReportFactory:
    """测试报告工厂"""

    def test_get_html_reporter(self):
        """测试获取HTML报告器"""
        reporter = ReportFactory.get_reporter("html")
        assert isinstance(reporter, HTMLCoverageReport)

    def test_get_json_reporter(self):
        """测试获取JSON报告器"""
        reporter = ReportFactory.get_reporter("json")
        assert isinstance(reporter, JSONCoverageReport)

    def test_get_ucis_reporter(self):
        """测试获取UCIS报告器"""
        reporter = ReportFactory.get_reporter("ucis")
        assert isinstance(reporter, UCISCoverageReport)

    def test_invalid_format_raises_error(self):
        """测试无效格式抛出异常"""
        with pytest.raises(ValueError):
            ReportFactory.get_reporter("invalid_format")

    def test_create_html_report(self):
        """测试便捷方法创建HTML报告"""
        reporter = ReportFactory.create_html_report()
        assert isinstance(reporter, HTMLCoverageReport)

    def test_get_available_formats(self):
        """测试获取可用格式"""
        formats = ReportFactory.get_available_formats()
        assert "html" in formats
        assert "json" in formats
        assert "ucis" in formats


class TestConvenienceFunctions:
    """测试便捷函数"""

    def test_create_report(self):
        """测试create_report函数"""
        from sv_randomizer.coverage.formatters import create_report

        reporter = create_report("html")
        assert isinstance(reporter, HTMLCoverageReport)

    def test_generate_report(self):
        """测试generate_report函数"""
        from sv_randomizer.coverage.formatters import generate_report

        data = {
            "title": "Test",
            "covergroups": []
        }

        # 不保存文件
        content = generate_report(data, "html")
        assert "<!DOCTYPE html>" in content

        # 保存到文件
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = os.path.join(tmpdir, "test.html")
            content = generate_report(data, "html", filepath)
            assert os.path.exists(filepath)


class TestCrossCoverageCalculation:
    """测试Cross覆盖率计算"""

    def test_two_way_cross(self):
        """测试两变量Cross"""
        cg = CoverGroup("test_cg")

        cp1 = CoverPoint("cp1", "val1", bins={"values": [1, 2]})
        cp2 = CoverPoint("cp2", "val2", bins={"values": [3, 4]})

        cg.add_coverpoint(cp1)
        cg.add_coverpoint(cp2)

        cross = Cross("cross", ["cp1", "cp2"])
        cg.add_cross(cross)

        # 采样一些组合
        cg.sample(val1=1, val2=3)
        cg.sample(val1=2, val2=4)

        # 验证覆盖率
        coverage = cross.get_coverage()
        assert coverage == 50.0  # 2/4 = 50%

    def test_cross_with_filter(self):
        """测试带过滤的Cross"""
        filter_func = lambda bins: bins[0] != 2
        cross = Cross("filtered_cross", ["cp1", "cp2"], cross_filter=filter_func)

        # 模拟添加到CoverGroup（手动设置bins）
        cross._bins = {
            (1, 3): 1,
            (2, 4): 1
        }
        cross._total_bins = 2
        cross._bins_loaded = True

        coverage = cross.get_coverage()
        # 只有一个组合通过过滤（1, 3），且被采样
        assert coverage > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
