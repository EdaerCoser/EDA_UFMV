"""
JSON Coverage Report Generator

生成JSON格式的覆盖率报告，便于机器处理和CI/CD集成。
"""

import json
from typing import Any, Dict
from .base import CoverageReport


class JSONCoverageReport(CoverageReport):
    """
    JSON覆盖率报告生成器

    生成结构化的JSON报告，便于：
    - 自动化测试集成
    - 数据分析
    - 跨工具数据交换
    """

    def get_format(self) -> str:
        """获取报告格式"""
        return "json"

    def generate(self, coverage_data: Dict[str, Any]) -> str:
        """
        生成JSON报告

        Args:
            coverage_data: 覆盖率数据字典

        Returns:
            JSON格式字符串
        """
        import datetime

        # 添加元数据
        report = {
            "version": "1.0",
            "title": coverage_data.get('title', self.title),
            "timestamp": datetime.datetime.now().isoformat(),
            "generator": "EDA_UFVM Coverage System",
            "summary": self._generate_summary(coverage_data),
            "covergroups": self._process_covergroups(coverage_data)
        }

        return json.dumps(report, indent=2, ensure_ascii=False)

    def _generate_summary(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """生成摘要信息"""
        covergroups = data.get('covergroups', [])

        total_coverage = 0.0
        total_samples = 0
        total_coverpoints = 0
        total_bins = 0
        covered_bins = 0

        for cg in covergroups:
            total_coverage += cg.get('coverage', 0)
            total_samples += cg.get('sample_count', 0)
            total_coverpoints += len(cg.get('coverpoints', {}))

            for cp in cg.get('coverpoints', {}).values():
                total_bins += cp.get('total_bins', 0)
                covered_bins += cp.get('covered_bins', 0)

        if covergroups:
            total_coverage /= len(covergroups)

        return {
            "total_coverage": round(total_coverage, 2),
            "total_covergroups": len(covergroups),
            "total_coverpoints": total_coverpoints,
            "total_samples": total_samples,
            "total_bins": total_bins,
            "covered_bins": covered_bins,
            "coverage_percentage": round((covered_bins / total_bins * 100) if total_bins > 0 else 100, 2)
        }

    def _process_covergroups(self, data: Dict[str, Any]) -> list:
        """处理CoverGroups数据"""
        covergroups = []

        for cg in data.get('covergroups', []):
            cg_data = {
                "name": cg.get('name'),
                "coverage": round(cg.get('coverage', 0), 2),
                "sample_count": cg.get('sample_count', 0),
                "coverpoints": []
            }

            # 处理CoverPoints
            for cp_name, cp_data in cg.get('coverpoints', {}).items():
                cp_info = {
                    "name": cp_name,
                    "coverage": round(cp_data.get('coverage', 0), 2),
                    "weight": cp_data.get('weight', 1.0),
                    "weighted_coverage": round(cp_data.get('weighted_coverage', 0), 2),
                    "sample_count": cp_data.get('sample_count', 0),
                    "total_bins": cp_data.get('total_bins', 0),
                    "covered_bins": cp_data.get('covered_bins', 0),
                    "bins": []
                }

                # 处理Bins
                for bin_name, bin_info in cp_data.get('bins', {}).items():
                    bin_info_data = {
                        "name": bin_name,
                        "hit_count": bin_info.get('hit_count', 0),
                        "covered": bin_info.get('hit_count', 0) > 0,
                        "type": bin_info.get('type', 'Unknown')
                    }
                    cp_info["bins"].append(bin_info_data)

                cg_data["coverpoints"].append(cp_info)

            covergroups.append(cg_data)

        return covergroups
