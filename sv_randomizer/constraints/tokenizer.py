"""
约束表达式词法分析器

将约束字符串分解为 token 流，支持 SystemVerilog 风格的运算符和关键字
"""

import re
from dataclasses import dataclass
from enum import Enum
from typing import Any, List, NamedTuple


class TokenType(Enum):
    """Token 类型枚举"""

    # 运算符
    ARITHMETIC_OP = "ARITHMETIC_OP"  # +, -, *, /, %
    RELATIONAL_OP = "RELATIONAL_OP"  # ==, !=, <, >, <=, >=
    LOGICAL_OP = "LOGICAL_OP"  # &&, ||, !
    BITWISE_OP = "BITWISE_OP"  # &, |, ^, ~, <<, >>
    IMPLIES_OP = "IMPLIES_OP"  # ->

    # 关键字
    INSIDE = "INSIDE"  # inside
    DIST = "DIST"  # dist

    # 字面量
    NUMBER = "NUMBER"  # 123, 0x1FF, 0b1010
    IDENTIFIER = "IDENTIFIER"  # 变量名
    STRING = "STRING"  # 字符串字面量

    # 分隔符
    LPAREN = "LPAREN"  # (
    RPAREN = "RPAREN"  # )
    LBRACE = "LBRACE"  # {
    RBRACE = "RBRACE"  # }
    LBRACKET = "LBRACKET"  # [
    RBRACKET = "RBRACKET"  # ]
    COMMA = "COMMA"  # ,
    COLON = "COLON"  # :

    # 其他
    WHITESPACE = "WHITESPACE"
    UNKNOWN = "UNKNOWN"


@dataclass
class Token:
    """词法 token"""

    type: TokenType
    value: Any
    position: int  # 在原始字符串中的位置

    def __repr__(self) -> str:
        return f"Token({self.type.value}, {repr(self.value)}, pos={self.position})"

    def __eq__(self, other) -> bool:
        if not isinstance(other, Token):
            return False
        return self.type == other.type and self.value == other.value


class TokenizeError(Exception):
    """词法分析错误"""

    def __init__(self, message: str, position: int, expression: str):
        self.message = message
        self.position = position
        self.expression = expression
        super().__init__(f"{message} at position {position}")


# Token 匹配模式 (按优先级排序)
TOKEN_PATTERNS = [
    # 多字符运算符 (必须先匹配)
    (r"<<", TokenType.BITWISE_OP),
    (r">>", TokenType.BITWISE_OP),
    (r"==", TokenType.RELATIONAL_OP),
    (r"!=", TokenType.RELATIONAL_OP),
    (r"<=", TokenType.RELATIONAL_OP),
    (r">=", TokenType.RELATIONAL_OP),
    (r"&&", TokenType.LOGICAL_OP),
    (r"\|\|", TokenType.LOGICAL_OP),
    (r"->", TokenType.IMPLIES_OP),
    (r":=", TokenType.COLON),  # dist 权重语法
    (r":/", TokenType.COLON),  # dist 权重语法

    # 单字符运算符和分隔符
    (r"\+", TokenType.ARITHMETIC_OP),
    (r"-", TokenType.ARITHMETIC_OP),
    (r"\*", TokenType.ARITHMETIC_OP),
    (r"/", TokenType.ARITHMETIC_OP),
    (r"%", TokenType.ARITHMETIC_OP),
    (r"<", TokenType.RELATIONAL_OP),
    (r">", TokenType.RELATIONAL_OP),
    (r"=", TokenType.ARITHMETIC_OP),  # 赋值 (如果支持)
    (r"&", TokenType.BITWISE_OP),
    (r"\|", TokenType.BITWISE_OP),
    (r"\^", TokenType.BITWISE_OP),
    (r"~", TokenType.BITWISE_OP),
    (r"!", TokenType.LOGICAL_OP),

    # 分隔符
    (r"\(", TokenType.LPAREN),
    (r"\)", TokenType.RPAREN),
    (r"\{", TokenType.LBRACE),
    (r"\}", TokenType.RBRACE),
    (r"\[", TokenType.LBRACKET),
    (r"\]", TokenType.RBRACKET),
    (r",", TokenType.COMMA),
    (r":", TokenType.COLON),

    # 数字字面量
    (
        r"0[xX][0-9a-fA-F]+",
        TokenType.NUMBER,
    ),  # 十六进制
    (r"0[bB][01]+", TokenType.NUMBER),  # 二进制
    (r"\d+", TokenType.NUMBER),  # 十进制

    # 关键字和标识符
    (r"inside", TokenType.INSIDE),
    (r"dist", TokenType.DIST),
    (r"[a-zA-Z_][a-zA-Z0-9_]*", TokenType.IDENTIFIER),

    # 空白 (跳过但不记录)
    (r"\s+", TokenType.WHITESPACE),
]


def tokenize(expression: str) -> List[Token]:
    """
    将约束字符串分解为 token 流

    Args:
        expression: 约束表达式字符串

    Returns:
        Token 列表 (不包含 WHITESPACE)

    Raises:
        TokenizeError: 如果遇到无法识别的字符
    """
    tokens = []
    pos = 0
    expr_len = len(expression)

    while pos < expr_len:
        match = None

        # 尝试匹配所有模式
        for pattern, token_type in TOKEN_PATTERNS:
            regex = re.compile(pattern)
            match = regex.match(expression, pos)
            if match:
                value = match.group(0)
                token = Token(token_type, value, pos)

                # 跳过空白
                if token_type != TokenType.WHITESPACE:
                    # 处理数字字面量
                    if token_type == TokenType.NUMBER:
                        token.value = _parse_number(value)

                    tokens.append(token)

                pos = match.end()
                break

        if not match:
            # 无法识别的字符
            raise TokenizeError(
                f"Unexpected character '{expression[pos]}'",
                pos,
                expression,
            )

    return tokens


def _parse_number(value: str) -> int:
    """
    解析数字字面量

    Args:
        value: 数字字符串

    Returns:
        整数值
    """
    value = value.strip()

    # 十六进制
    if value.startswith(("0x", "0X")):
        return int(value, 16)

    # 二进制
    if value.startswith(("0b", "0B")):
        return int(value, 2)

    # 十进制
    return int(value)


def format_error_position(expression: str, position: int) -> str:
    """
    格式化错误位置，便于显示

    Args:
        expression: 原始表达式
        position: 错误位置

    Returns:
        格式化的错误字符串
    """
    line_start = expression.rfind("\n", 0, position) + 1
    line_end = expression.find("\n", position)
    if line_end == -1:
        line_end = len(expression)

    line = expression[line_start:line_end]
    column = position - line_start

    # 构建指针
    pointer = " " * column + "^"

    return f"{line}\n{pointer}"


# 便捷函数


def print_tokens(expression: str) -> None:
    """打印 token 流 (用于调试)"""
    try:
        tokens = tokenize(expression)
        print(f"Expression: {expression}")
        print("Tokens:")
        for token in tokens:
            print(f"  {token}")
        print()
    except TokenizeError as e:
        print(f"Error: {e}")
        print(format_error_position(e.expression, e.position))
