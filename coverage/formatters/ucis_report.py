"""
UCIS Coverage Report Generator

生成UCIS（Unified Coverage Interoperability Standard）格式的覆盖率报告。

UCIS是IEEE 1687标准，用于EDA工具间的覆盖率数据交换。
"""

import json
from typing import Any, Dict
from .base import CoverageReport


class UCISCoverageReport(CoverageReport):
    """
    UCIS覆盖率报告生成器

    生成符合IEEE 1687标准的UCIS格式报告（简化版）。

    注意：这是UCIS的简化实现，主要用于演示。
    完整的UCIS实现需要支持更复杂的结构和元数据。
    """

    UCIS_VERSION = "1.0"
    UCIS_NAMESPACE = "http://www.accellera.org/XMLSchema/UCIS/1.0"

    def get_format(self) -> str:
        """获取报告格式"""
        return "ucis"

    def generate(self, coverage_data: Dict[str, Any]) -> str:
        """
        生成UCIS格式报告

        Args:
            coverage_data: 覆盖率数据字典

        Returns:
            UCIS XML格式字符串
        """
        import datetime

        # UCIS使用XML格式
        xml_parts = [
            '<?xml version="1.0" encoding="UTF-8"?>',
            f'<ucis xmlns="{self.UCIS_NAMESPACE}" version="{self.UCIS_VERSION}">',
            self._generate_header(),
            self._generate_covergroups(coverage_data),
            self._generate_footer(),
            '</ucis>'
        ]

        return "\n".join(xml_parts)

    def _generate_header(self) -> str:
        """生成UCIS头部信息"""
        import datetime

        timestamp = datetime.datetime.now().isoformat()

        return f"""    <info>
        <generator>EDA_UFVM Coverage System</generator>
        <timestamp>{timestamp}</timestamp>
        <version>v0.2.0</version>
    </info>
"""

    def _generate_covergroups(self, data: Dict[str, Any]) -> str:
        """生成CoverGroups部分"""
        xml_parts = []

        for cg in data.get('covergroups', []):
            cg_name = cg.get('name', 'Unknown')
            cg_coverage = cg.get('coverage', 0.0)

            xml_parts.append(f"""    <covergroup name="{cg_name}" coverage="{cg_coverage:.2f}">""")

            # 生成CoverPoints
            for cp_name, cp_data in cg.get('coverpoints', {}).items():
                cp_coverage = cp_data.get('coverage', 0.0)
                cp_total_bins = cp_data.get('total_bins', 0)
                cp_covered_bins = cp_data.get('covered_bins', 0)

                xml_parts.append(f"""        <coverpoint name="{cp_name}" coverage="{cp_coverage:.2f}">""")
                xml_parts.append(f"            <bins total=\"{cp_total_bins}\" covered=\"{cp_covered_bins}\" >")

                # 生成Bins
                for bin_name, bin_info in cp_data.get('bins', {}).items():
                    hit_count = bin_info.get('hit_count', 0)
                    covered = "true" if hit_count > 0 else "false"

                    xml_parts.append(f"""                <bin name="{bin_name}" hits="{hit_count}" covered="{covered}" />""")

                xml_parts.append("            </bins>")
                xml_parts.append("        </coverpoint>")

            xml_parts.append("    </covergroup>")

        return "\n".join(xml_parts)

    def _generate_footer(self) -> str:
        """生成UCIS尾部信息"""
        return """    <statistics>
        <!-- UCIS统计信息 -->
    </statistics>
"""


class UCISJSONReport(CoverageReport):
    """
    UCIS JSON格式报告

    使用JSON表示UCIS数据结构，便于处理和交换。
    """

    def get_format(self) -> str:
        """获取报告格式"""
        return "ucis_json"

    def generate(self, coverage_data: Dict[str, Any]) -> str:
        """
        生成UCIS JSON格式报告

        Args:
            coverage_data: 覆盖率数据字典

        Returns:
            UCIS JSON格式字符串
        """
        import datetime

        ucis_data = {
            "ucis_version": UCISCoverageReport.UCIS_VERSION,
            "namespace": UCISCoverageReport.UCIS_NAMESPACE,
            "generator": "EDA_UFVM Coverage System",
            "timestamp": datetime.datetime.now().isoformat(),
            "covergroups": self._convert_to_ucis_format(coverage_data)
        }

        return json.dumps(ucis_data, indent=2, ensure_ascii=False)

    def _convert_to_ucis_format(self, data: Dict[str, Any]) -> list:
        """转换为UCIS格式"""
        ucis_covergroups = []

        for cg in data.get('covergroups', []):
            ucis_cg = {
                "name": cg.get('name'),
                "coverage": round(cg.get('coverage', 0), 2),
                "type": "covergroup",
                "coverpoints": []
            }

            for cp_name, cp_data in cg.get('coverpoints', {}).items():
                ucis_cp = {
                    "name": cp_name,
                    "coverage": round(cp_data.get('coverage', 0), 2),
                    "type": "coverpoint",
                    "bins": []
                }

                for bin_name, bin_info in cp_data.get('bins', {}).items():
                    ucis_bin = {
                        "name": bin_name,
                        "hits": bin_info.get('hit_count', 0),
                        "covered": bin_info.get('hit_count', 0) > 0,
                        "type": bin_info.get('type', 'Unknown')
                    }
                    ucis_cp["bins"].append(ucis_bin)

                ucis_cg["coverpoints"].append(ucis_cp)

            ucis_covergroups.append(ucis_cg)

        return ucis_covergroups
