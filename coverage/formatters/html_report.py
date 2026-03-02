"""
HTML Coverage Report Generator

生成HTML格式的覆盖率报告，提供可视化界面。
"""

from typing import Any, Dict
from .base import CoverageReport


class HTMLCoverageReport(CoverageReport):
    """
    HTML覆盖率报告生成器

    生成包含以下内容的HTML报告：
    - 总体覆盖率摘要
    - 各CoverGroup详情
    - 各CoverPoint详情
    - Bin命中情况
    - 可视化进度条
    - 交互式折叠面板
    """

    def get_format(self) -> str:
        """获取报告格式"""
        return "html"

    def generate(self, coverage_data: Dict[str, Any]) -> str:
        """
        生成HTML报告

        Args:
            coverage_data: 覆盖率数据字典，格式：
                {
                    'title': '报告标题',
                    'covergroups': [
                        {
                            'name': 'cg_name',
                            'coverage': 85.5,
                            'sample_count': 1000,
                            'coverpoints': {...}
                        },
                        ...
                    ]
                }

        Returns:
            HTML报告内容
        """
        self._data = coverage_data
        title = coverage_data.get('title', self.title)

        # 计算总覆盖率
        total_coverage = self._calculate_total_coverage(coverage_data)

        html_parts = [
            self._generate_header(title),
            self._generate_summary(coverage_data, total_coverage),
            self._generate_covergroups(coverage_data),
            self._generate_footer()
        ]

        return "\n".join(html_parts)

    def _calculate_total_coverage(self, data: Dict[str, Any]) -> float:
        """计算总覆盖率"""
        covergroups = data.get('covergroups', [])
        if not covergroups:
            return 0.0

        total = sum(cg.get('coverage', 0) for cg in covergroups)
        return total / len(covergroups)

    def _generate_header(self, title: str) -> str:
        """生成HTML头部"""
        return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            background: #f5f5f5;
            padding: 20px;
            line-height: 1.6;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }}
        .header h1 {{
            font-size: 2em;
            margin-bottom: 10px;
        }}
        .summary {{
            padding: 30px;
            background: #f8f9fa;
            border-bottom: 1px solid #dee2e6;
        }}
        .summary-item {{
            display: inline-block;
            margin: 10px 20px;
            text-align: center;
        }}
        .summary-value {{
            font-size: 2em;
            font-weight: bold;
            color: #667eea;
        }}
        .summary-label {{
            color: #6c757d;
            font-size: 0.9em;
        }}
        .covergroup {{
            border-bottom: 1px solid #dee2e6;
        }}
        .covergroup-header {{
            padding: 20px 30px;
            background: #fff;
            cursor: pointer;
            display: flex;
            justify-content: space-between;
            align-items: center;
            transition: background 0.2s;
        }}
        .covergroup-header:hover {{
            background: #f8f9fa;
        }}
        .covergroup-name {{
            font-size: 1.2em;
            font-weight: 600;
        }}
        .coverage-badge {{
            padding: 8px 16px;
            border-radius: 20px;
            font-weight: bold;
            color: white;
        }}
        .coverpoint {{
            padding: 20px 30px 20px 50px;
            background: #f8f9fa;
            border-bottom: 1px solid #dee2e6;
        }}
        .coverpoint:last-child {{
            border-bottom: none;
        }}
        .coverpoint-name {{
            font-weight: 600;
            margin-bottom: 10px;
        }}
        .progress-bar {{
            width: 100%;
            height: 30px;
            background: #e9ecef;
            border-radius: 15px;
            overflow: hidden;
            margin: 10px 0;
        }}
        .progress-fill {{
            height: 100%;
            transition: width 0.3s ease;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: bold;
            font-size: 0.9em;
        }}
        .bins-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
            gap: 10px;
            margin-top: 15px;
        }}
        .bin-item {{
            padding: 10px;
            border-radius: 4px;
            text-align: center;
            font-size: 0.9em;
        }}
        .bin-covered {{
            background: #d4edda;
            color: #155724;
        }}
        .bin-uncovered {{
            background: #f8d7da;
            color: #721c24;
        }}
        .footer {{
            padding: 20px 30px;
            background: #f8f9fa;
            text-align: center;
            color: #6c757d;
            font-size: 0.9em;
        }}
        .collapsible-content {{
            max-height: 0;
            overflow: hidden;
            transition: max-height 0.3s ease;
        }}
        .collapsible-content.open {{
            max-height: 5000px;
        }}
        .toggle-icon {{
            transition: transform 0.3s;
        }}
        .toggle-icon.open {{
            transform: rotate(180deg);
        }}
    </style>
    <script>
        function toggleCovergroup(button) {{
            const content = button.nextElementSibling;
            const icon = button.querySelector('.toggle-icon');

            content.classList.toggle('open');
            icon.classList.toggle('open');
        }}
    </script>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{title}</h1>
            <p>Coverage Report</p>
        </div>
"""

    def _generate_summary(self, data: Dict[str, Any], total_coverage: float) -> str:
        """生成摘要部分"""
        covergroups = data.get('covergroups', [])
        total_samples = sum(cg.get('sample_count', 0) for cg in covergroups)
        total_cps = sum(len(cg.get('coverpoints', {})) for cg in covergroups)

        coverage_color = self._get_coverage_color(total_coverage)

        return f"""        <div class="summary">
            <div class="summary-item">
                <div class="summary-value" style="color: {coverage_color};">
                    {self._format_percentage(total_coverage)}
                </div>
                <div class="summary-label">总覆盖率</div>
            </div>
            <div class="summary-item">
                <div class="summary-value">{len(covergroups)}</div>
                <div class="summary-label">CoverGroups</div>
            </div>
            <div class="summary-item">
                <div class="summary-value">{total_cps}</div>
                <div class="summary-label">CoverPoints</div>
            </div>
            <div class="summary-item">
                <div class="summary-value">{total_samples}</div>
                <div class="summary-label">采样次数</div>
            </div>
        </div>
"""

    def _generate_covergroups(self, data: Dict[str, Any]) -> str:
        """生成CoverGroups部分"""
        covergroups = data.get('covergroups', [])
        html_parts = []

        for cg in covergroups:
            cg_name = cg.get('name', 'Unknown')
            cg_coverage = cg.get('coverage', 0.0)
            cg_samples = cg.get('sample_count', 0)
            coverpoints = cg.get('coverpoints', {})

            coverage_color = self._get_coverage_color(cg_coverage)

            # CoverGroup头部
            html_parts.append(f"""        <div class="covergroup">
            <div class="covergroup-header" onclick="toggleCovergroup(this)">
                <div class="covergroup-name">{cg_name}</div>
                <div style="display: flex; align-items: center; gap: 15px;">
                    <span>采样: {cg_samples}</span>
                    <span class="coverage-badge" style="background: {coverage_color};">
                        {self._format_percentage(cg_coverage)}
                    </span>
                    <span class="toggle-icon">&#9662;</span>
                </div>
            </div>
""")

            # CoverPoints内容
            html_parts.append(f"""            <div class="collapsible-content open">
""")

            for cp_name, cp_data in coverpoints.items():
                cp_coverage = cp_data.get('coverage', 0.0)
                cp_samples = cp_data.get('sample_count', 0)
                cp_total_bins = cp_data.get('total_bins', 0)
                cp_covered_bins = cp_data.get('covered_bins', 0)
                bins = cp_data.get('bins', {})

                coverage_color = self._get_coverage_color(cp_coverage)

                html_parts.append(f"""                <div class="coverpoint">
                    <div class="coverpoint-name">{cp_name}</div>
                    <div style="display: flex; justify-content: space-between; margin: 10px 0;">
                        <span>采样: {cp_samples}</span>
                        <span>Bins: {cp_covered_bins}/{cp_total_bins}</span>
                    </div>
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: {cp_coverage}%; background: {coverage_color};">
                            {self._format_percentage(cp_coverage)}
                        </div>
                    </div>
                    <div class="bins-grid">
""")

                # Bins网格（最多显示20个）
                for i, (bin_name, bin_info) in enumerate(list(bins.items())[:20]):
                    hit_count = bin_info.get('hit_count', 0)
                    bin_class = "bin-covered" if hit_count > 0 else "bin-uncovered"
                    html_parts.append(f"""                        <div class="bin-item {bin_class}">
                            <div>{bin_name[:20]}</div>
                            <div>{hit_count} 次</div>
                        </div>
""")

                html_parts.append("""                    </div>
                </div>
""")

            html_parts.append("""            </div>
        </div>
""")

        return "\n".join(html_parts)

    def _generate_footer(self) -> str:
        """生成HTML尾部"""
        import datetime
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        return f"""        <div class="footer">
            <p>Generated by EDA_UFVM Coverage System</p>
            <p>{timestamp}</p>
        </div>
    </div>
</body>
</html>
"""
