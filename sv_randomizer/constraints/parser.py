"""
约束表达式解析器

使用递归下降解析法将字符串表达式转换为 AST
支持 SystemVerilog 风格的约束语法
"""

from typing import List, Optional, Union

from .tokenizer import Token, TokenType, tokenize, TokenizeError
from .expressions import (
    BinaryExpr,
    BinaryOp,
    ConstantExpr,
    Expression,
    UnaryExpr,
    VariableExpr,
)


class ParseError(Exception):
    """语法分析错误"""

    def __init__(self, message: str, token: Token, tokens: List[Token]):
        self.message = message
        self.token = token
        self.tokens = tokens
        super().__init__(f"{message} at position {token.position}")


class ConstraintParser:
    """
    SystemVerilog 风格约束表达式解析器

    语法 (优先级从低到高):
    expression      ::= logical_or_expr
    logical_or      ::= logical_and ('||' logical_and)*
    logical_and     ::= implication ('&&' implication)*
    implication     ::= equality ('->' equality)?
    equality        ::= relational (('==' | '!=') relational)*
    relational      ::= shift (('<' | '>' | '<=' | '>=') shift)*
    shift           ::= additive (('<<' | '>>') additive)*
    additive        ::= multiplicative (('+' | '-') multiplicative)*
    multiplicative ::= unary (('*' | '/' | '%') unary)*
    unary           ::= ('!' | '-' | '~') unary | primary
    primary         ::= NUMBER | IDENTIFIER | '(' expression ')'
    """

    def __init__(self, expression: str):
        """
        初始化解析器

        Args:
            expression: 约束表达式字符串
        """
        self.expression = expression
        self.tokens = tokenize(expression)
        self.pos = 0

    def parse(self) -> Expression:
        """
        解析表达式并返回 AST

        Returns:
            Expression AST

        Raises:
            ParseError: 语法错误
            TokenizeError: 词法错误
        """
        if not self.tokens:
            raise ParseError("Empty expression", Token(TokenType.UNKNOWN, "", 0), [])

        expr = self._parse_logical_or()

        # 确保所有 token 都被消耗
        if not self._is_at_end():
            unexpected = self._peek()
            raise ParseError(
                f"Unexpected token '{unexpected.value}'",
                unexpected,
                self.tokens,
            )

        return expr

    # === 私有解析方法 ===

    def _parse_logical_or(self) -> Expression:
        """解析逻辑或表达式 (||)"""
        left = self._parse_logical_and()

        while self._match_operator("||", TokenType.LOGICAL_OP):
            op_token = self._previous()
            right = self._parse_logical_and()
            left = BinaryExpr(left, BinaryOp.OR, right)

        return left

    def _parse_logical_and(self) -> Expression:
        """解析逻辑与表达式 (&&)"""
        left = self._parse_implication()

        while self._match_operator("&&", TokenType.LOGICAL_OP):
            op_token = self._previous()
            right = self._parse_implication()
            left = BinaryExpr(left, BinaryOp.AND, right)

        return left

    def _parse_implication(self) -> Expression:
        """解析蕴含表达式 (->)"""
        left = self._parse_equality()

        if self._match_operator("->", TokenType.IMPLIES_OP):
            op_token = self._previous()
            right = self._parse_equality()
            return BinaryExpr(left, BinaryOp.IMPLIES, right)

        return left

    def _parse_equality(self) -> Expression:
        """解析相等性表达式 (==, !=)"""
        left = self._parse_relational()

        while True:
            if self._match_operator("==", TokenType.RELATIONAL_OP):
                op = BinaryOp.EQ
            elif self._match_operator("!=", TokenType.RELATIONAL_OP):
                op = BinaryOp.NE
            else:
                break

            op_token = self._previous()
            right = self._parse_relational()
            left = BinaryExpr(left, op, right)

        return left

    def _parse_relational(self) -> Expression:
        """解析关系表达式 (<, >, <=, >=)"""
        left = self._parse_shift()

        while True:
            if self._match_operator("<", TokenType.RELATIONAL_OP):
                op = BinaryOp.LT
            elif self._match_operator("<=", TokenType.RELATIONAL_OP):
                op = BinaryOp.LE
            elif self._match_operator(">", TokenType.RELATIONAL_OP):
                op = BinaryOp.GT
            elif self._match_operator(">=", TokenType.RELATIONAL_OP):
                op = BinaryOp.GE
            else:
                break

            op_token = self._previous()
            right = self._parse_shift()
            left = BinaryExpr(left, op, right)

        return left

    def _parse_shift(self) -> Expression:
        """解析移位表达式 (<<, >>)"""
        left = self._parse_additive()

        while True:
            if self._match_operator("<<", TokenType.BITWISE_OP):
                op = BinaryOp.SHIFT_LEFT
            elif self._match_operator(">>", TokenType.BITWISE_OP):
                op = BinaryOp.SHIFT_RIGHT
            else:
                break

            op_token = self._previous()
            right = self._parse_additive()
            left = BinaryExpr(left, op, right)

        return left

    def _parse_additive(self) -> Expression:
        """解析加法表达式 (+, -)"""
        left = self._parse_multiplicative()

        while True:
            if self._match_operator("+", TokenType.ARITHMETIC_OP):
                op = BinaryOp.ADD
            elif self._match_operator("-", TokenType.ARITHMETIC_OP):
                op = BinaryOp.SUB
            else:
                break

            op_token = self._previous()
            right = self._parse_multiplicative()
            left = BinaryExpr(left, op, right)

        return left

    def _parse_multiplicative(self) -> Expression:
        """解析乘法表达式 (*, /, %)"""
        left = self._parse_unary()

        while True:
            if self._match_operator("*", TokenType.ARITHMETIC_OP):
                op = BinaryOp.MUL
            elif self._match_operator("/", TokenType.ARITHMETIC_OP):
                op = BinaryOp.DIV
            elif self._match_operator("%", TokenType.ARITHMETIC_OP):
                op = BinaryOp.MOD
            else:
                break

            op_token = self._previous()
            right = self._parse_unary()
            left = BinaryExpr(left, op, right)

        return left

    def _parse_unary(self) -> Expression:
        """解析一元表达式 (!, -, ~)"""
        if self._match_operator("!", TokenType.LOGICAL_OP):
            op_token = self._previous()
            expr = self._parse_unary()
            return UnaryExpr("!", expr)

        if self._match_operator("-", TokenType.ARITHMETIC_OP):
            op_token = self._previous()
            expr = self._parse_unary()
            return UnaryExpr("-", expr)

        if self._match_operator("~", TokenType.BITWISE_OP):
            op_token = self._previous()
            expr = self._parse_unary()
            return UnaryExpr("~", expr)

        return self._parse_primary()

    def _parse_primary(self) -> Expression:
        """解析基本表达式"""
        # 左括号 - 分组表达式
        if self._match(TokenType.LPAREN):
            expr = self._parse_logical_or()
            self._consume(TokenType.RPAREN, "Expect ')' after expression")
            return expr

        # 数字字面量
        if self._match(TokenType.NUMBER):
            token = self._previous()
            return ConstantExpr(token.value)

        # 标识符 (变量名)
        if self._match(TokenType.IDENTIFIER):
            token = self._previous()
            return VariableExpr(token.value)

        # 无法识别的 token
        raise ParseError(
            f"Unexpected token '{self._peek().value}', expected expression",
            self._peek(),
            self.tokens,
        )

    # === Token 辅助方法 ===

    def _match(self, token_type: TokenType) -> bool:
        """如果当前 token 是指定类型，则消耗它"""
        if self._check(token_type):
            self._advance()
            return True
        return False

    def _match_operator(self, value: str, token_type: TokenType) -> bool:
        """如果当前 token 是指定运算符，则消耗它"""
        if self._check(token_type) and self._peek().value == value:
            self._advance()
            return True
        return False

    def _check(self, token_type: TokenType) -> bool:
        """检查当前 token 是否是指定类型"""
        if self._is_at_end():
            return False
        return self._peek().type == token_type

    def _advance(self) -> Token:
        """消耗并返回当前 token"""
        if not self._is_at_end():
            self.pos += 1
        return self._previous()

    def _peek(self) -> Token:
        """查看当前 token 但不消耗"""
        if self._is_at_end():
            return Token(TokenType.UNKNOWN, "", len(self.expression))
        return self.tokens[self.pos]

    def _previous(self) -> Token:
        """返回上一个 token"""
        if self.pos > 0:
            return self.tokens[self.pos - 1]
        return Token(TokenType.UNKNOWN, "", 0)

    def _is_at_end(self) -> bool:
        """检查是否到达 token 流末尾"""
        return self.pos >= len(self.tokens)

    def _consume(self, token_type: TokenType, message: str) -> Token:
        """消耗指定类型的 token，否则抛出错误"""
        if self._check(token_type):
            return self._advance()

        raise ParseError(message, self._peek(), self.tokens)


# === 便捷函数 ===


def parse_expression(expression: str) -> Expression:
    """
    解析约束表达式字符串

    Args:
        expression: 约束表达式字符串

    Returns:
        Expression AST

    Raises:
        ParseError: 语法错误
        TokenizeError: 词法错误

    示例:
        >>> expr = parse_expression("x > 10 && y < 20")
        >>> isinstance(expr, BinaryExpr)
        True
    """
    parser = ConstraintParser(expression)
    return parser.parse()


# === 用于测试和调试 ===


def print_ast(expr: Expression, indent: int = 0) -> None:
    """打印 AST 结构 (用于调试)"""
    prefix = "  " * indent
    print(f"{prefix}{expr}")

    if isinstance(expr, BinaryExpr):
        print(f"{prefix}  left:")
        print_ast(expr.left, indent + 2)
        print(f"{prefix}  op: {expr.op.value}")
        print(f"{prefix}  right:")
        print_ast(expr.right, indent + 2)
    elif isinstance(expr, UnaryExpr):
        print(f"{prefix}  op: {expr.op}")
        print(f"{prefix}  expr:")
        print_ast(expr.expr, indent + 1)


if __name__ == "__main__":
    # 测试解析器
    test_expressions = [
        "x > 10",
        "x + y < 100",
        "x > 10 && y < 20",
        "x == 5 || y != 10",
        "!(x == 0)",
        "x + y * z > 100",
        "(x + y) * z > 100",
    ]

    for expr_str in test_expressions:
        print(f"\n解析: {expr_str}")
        try:
            expr = parse_expression(expr_str)
            print(f"成功: {expr}")
        except (ParseError, TokenizeError) as e:
            print(f"错误: {e}")
