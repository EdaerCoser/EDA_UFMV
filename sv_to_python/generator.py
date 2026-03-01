# sv_to_python/generator.py
"""
Python代码生成器 - 使用Jinja2模板
"""
from datetime import datetime
from typing import List, Any
from pathlib import Path
from jinja2 import Environment, FileSystemLoader, Template

from sv_to_python.ir import (
    Operation, RegWrite, RegRead, RegSet, RegGet,
    RegReset, RegRandomize, Comment, Todo, TaskInfo
)

class PythonGenerator:
    """Python代码生成器"""

    def __init__(self, template_dir: str = None):
        """初始化生成器

        Args:
            template_dir: 模板目录路径
        """
        if template_dir is None:
            import sv_to_python
            module_dir = Path(sv_to_python.__file__).parent
            template_dir = module_dir / "templates"

        self.env = Environment(
            loader=FileSystemLoader(str(template_dir)),
            trim_blocks=True,
            lstrip_blocks=True
        )

        # 注册过滤器
        self.env.filters['generate_operation'] = self._generate_operation
        self.env.filters['generate_task'] = self.generate_task
        self.env.filters['lower'] = lambda s: s.lower() if isinstance(s, str) else s

    def _format_value(self, value: Any) -> str:
        """格式化值为Python表达式

        Args:
            value: 值（整数、字符串等）

        Returns:
            Python表达式字符串
        """
        if isinstance(value, int):
            # 转为16进制格式
            return f"0x{value:08x}"
        elif isinstance(value, str):
            return value
        return str(value)

    def _generate_operation(self, op: Operation) -> str:
        """生成单行操作代码

        Args:
            op: Operation对象

        Returns:
            Python代码字符串
        """
        if isinstance(op, RegWrite):
            return self._gen_write(op)
        elif isinstance(op, RegRead):
            return self._gen_read(op)
        elif isinstance(op, RegSet):
            return self._gen_set(op)
        elif isinstance(op, RegGet):
            return self._gen_get(op)
        elif isinstance(op, RegReset):
            return self._gen_reset(op)
        elif isinstance(op, Comment):
            return self._gen_comment(op)
        elif isinstance(op, Todo):
            return self._gen_todo(op)
        else:
            return f"# Unknown operation: {op.__class__.__name__}"

    def _gen_write(self, op: RegWrite) -> str:
        """生成write操作代码"""
        # 构建寄存器访问路径
        reg_access = ".".join(op.reg_path).lower()

        # 格式化值
        value_str = self._format_value(op.value)

        # backdoor参数
        backdoor_suffix = ", backdoor=True" if op.backdoor else ""

        return f"reg_model.{reg_access}.write({value_str}{backdoor_suffix})"

    def _gen_read(self, op: RegRead) -> str:
        """生成read操作代码"""
        reg_access = ".".join(op.reg_path).lower()
        backdoor_suffix = ", backdoor=True" if op.backdoor else ""

        return f"value = reg_model.{reg_access}.read({backdoor_suffix})"

    def _gen_set(self, op: RegSet) -> str:
        """生成set操作代码"""
        reg_access = ".".join(op.reg_path).lower()
        value_str = self._format_value(op.value)

        return f"reg_model.{reg_access}.value = {value_str}"

    def _gen_get(self, op: RegGet) -> str:
        """生成get操作代码"""
        reg_access = ".".join(op.reg_path).lower()

        return f"value = reg_model.{reg_access}.value"

    def _gen_reset(self, op: RegReset) -> str:
        """生成reset操作代码"""
        reg_access = ".".join(op.reg_path).lower()

        return f"reg_model.{reg_access}.reset()"

    def _gen_comment(self, op: Comment) -> str:
        """生成注释"""
        return f"# {op.text}"

    def _gen_todo(self, op: Todo) -> str:
        """生成TODO占位符"""
        return f"# TODO: {op.reason}\n# Original SV: {op.original_source}\nraise NotImplementedError(\"Manual conversion needed\")"

    def generate_task(self, task: TaskInfo, **context) -> str:
        """生成单个task的Python代码

        Args:
            task: TaskInfo对象
            **context: 额外的模板上下文

        Returns:
            Python代码字符串
        """
        template = self.env.get_template('task.py.j2')

        # 准备上下文
        template_context = {
            'task': task,
            **context
        }

        return template.render(**template_context)

    def generate_module(self, tasks: List[TaskInfo], **context) -> str:
        """生成完整Python模块代码

        Args:
            tasks: TaskInfo列表
            **context: 额外的模板上下文

        Returns:
            Python模块代码字符串
        """
        template = self.env.get_template('module.py.j2')

        # 默认上下文
        default_context = {
            'module_name': context.get('module_name', 'sv_tasks'),
            'generation_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'use_type_hints': context.get('use_type_hints', True),
            'source_file': context.get('source_file', 'unknown')
        }

        template_context = {**default_context, **context, 'tasks': tasks}

        return template.render(**template_context)
