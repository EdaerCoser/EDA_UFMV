# sv_to_python/cli.py
"""
CLI工具 - sv2python命令
"""
import sys
import click
from pathlib import Path
from typing import Optional

from sv_to_python.parser import SVParser
from sv_to_python.extractor import UVMOperationExtractor
from sv_to_python.generator import PythonGenerator
from sv_to_python.ir import TaskInfo
from sv_to_python.errors import ConversionError

@click.group()
@click.version_option(version="0.1.0")
def cli():
    """SV to Python - SystemVerilog任务转换工具"""
    pass

@cli.command()
@click.argument('input_file', type=click.Path(exists=True, path_type=Path))
@click.option('-o', '--output', type=click.Path(path_type=Path),
              help='输出文件路径')
@click.option('--reg-model', default='reg_model',
              help='RGM模型名称（默认: reg_model）')
@click.option('--task', help='只转换指定的task')
@click.option('--verbose', '-v', is_flag=True, help='详细输出')
@click.option('--dry-run', is_flag=True, help='只分析不生成文件')
def convert(input_file: Path, output: Optional[Path],
            reg_model: str, task: Optional[str],
            verbose: bool, dry_run: bool):
    """转换SV文件到Python"""
    try:
        if verbose:
            click.echo(f"Parsing: {input_file}")

        # 解析SV文件
        parser = SVParser(input_file)
        tasks_dict = parser.get_tasks()

        if verbose:
            click.echo(f"Found {len(tasks_dict)} tasks")

        # 提取操作
        extractor = UVMOperationExtractor()
        tasks = []

        for task_name, task_def in tasks_dict.items():
            if task and task != task_name:
                continue

            operations = extractor.extract(task_def, parser.source_text)
            task_info = TaskInfo(
                name=task_name,
                parameters=task_def.parameters,
                operations=operations,
                line_no=task_def.line_no
            )
            tasks.append(task_info)

            if verbose:
                click.echo(f"  {task_name}: {len(operations)} operations")

        # 生成Python代码
        generator = PythonGenerator()
        code = generator.generate_module(
            tasks,
            module_name=input_file.stem,
            source_file=str(input_file)
        )

        if dry_run:
            click.echo("\n" + "=" * 60)
            click.echo("DRY RUN - Generated code:")
            click.echo("=" * 60)
            click.echo(code)
            return

        # 输出到文件或stdout
        if output:
            output.write_text(code, encoding='utf-8')
            click.echo(f"[OK] Generated: {output}")
        else:
            click.echo(code)

    except ConversionError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"Unexpected error: {e}", err=True)
        if verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)

@cli.command()
@click.argument('input_file', type=click.Path(exists=True, path_type=Path))
@click.option('--json', 'output_json', is_flag=True,
              help='输出JSON格式')
@click.option('--detail', is_flag=True,
              help='显示详细信息')
def list(input_file: Path, output_json: bool, detail: bool):
    """列出SV文件中的tasks"""
    try:
        parser = SVParser(input_file)
        tasks = parser.get_tasks()

        if output_json:
            import json
            tasks_info = {}
            for name, task_def in tasks.items():
                tasks_info[name] = {
                    'parameters': task_def.parameters,
                    'line_no': task_def.line_no
                }
            click.echo(json.dumps(tasks_info, indent=2))
        else:
            click.echo(f"Tasks in {input_file.name}:")
            for i, (name, task_def) in enumerate(tasks.items(), 1):
                params_str = ", ".join([p[1] for p in task_def.parameters])
                click.echo(f"  {i}. {name}({params_str})")
                if detail:
                    click.echo(f"     Line: {task_def.line_no}")
                    click.echo(f"     Parameters: {len(task_def.parameters)}")

    except ConversionError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)

@cli.command()
@click.argument('input_file', type=click.Path(exists=True, path_type=Path))
@click.option('--sv-source', type=click.Path(exists=True, path_type=Path),
              help='原始SV文件（用于对比）')
@click.option('--check-syntax', is_flag=True,
              help='检查Python语法')
@click.option('--import-check', is_flag=True,
              help='检查导入是否可用')
def validate(input_file: Path, sv_source: Optional[Path],
             check_syntax: bool, import_check: bool):
    """验证转换结果"""
    try:
        code = input_file.read_text(encoding='utf-8')

        issues = []

        # 检查语法
        if check_syntax:
            import ast
            try:
                ast.parse(code)
                click.echo("[OK] Syntax check passed")
            except SyntaxError as e:
                issues.append(f"Syntax error: {e}")

        # 检查TODO标记
        todo_count = code.count("# TODO:")
        if todo_count > 0:
            issues.append(f"Found {todo_count} TODO items requiring manual implementation")

        if issues:
            click.echo("Issues found:", err=True)
            for issue in issues:
                click.echo(f"  - {issue}", err=True)
            sys.exit(1)
        else:
            click.echo("[OK] Validation passed")

    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)

if __name__ == '__main__':
    cli()
