"""
词法分析器单元测试

测试Verilog词法分析器的各种功能
"""

import pytest

from parser.core.lexer import VerilogLexer
from parser.core.token import TokenType, ParseError


class TestKeywordRecognition:
    """测试关键字识别"""

    def test_module_keyword(self):
        """测试module关键字"""
        lexer = VerilogLexer("module")
        tokens = lexer.tokenize()
        assert tokens[0].type == TokenType.MODULE
        assert tokens[0].value == "MODULE"

    def test_endmodule_keyword(self):
        """测试endmodule关键字"""
        lexer = VerilogLexer("endmodule")
        tokens = lexer.tokenize()
        assert tokens[0].type == TokenType.ENDMODULE

    def test_rand_keyword(self):
        """测试rand关键字"""
        lexer = VerilogLexer("rand")
        tokens = lexer.tokenize()
        assert tokens[0].type == TokenType.RAND

    def test_randc_keyword(self):
        """测试randc关键字"""
        lexer = VerilogLexer("randc")
        tokens = lexer.tokenize()
        assert tokens[0].type == TokenType.RANDC

    def test_constraint_keyword(self):
        """测试constraint关键字"""
        lexer = VerilogLexer("constraint")
        tokens = lexer.tokenize()
        assert tokens[0].type == TokenType.CONSTRAINT

    def test_logic_keyword(self):
        """测试logic关键字"""
        lexer = VerilogLexer("logic")
        tokens = lexer.tokenize()
        assert tokens[0].type == TokenType.LOGIC

    def test_input_output_keywords(self):
        """测试input/output关键字"""
        lexer = VerilogLexer("input output inout")
        tokens = lexer.tokenize()
        assert tokens[0].type == TokenType.INPUT
        assert tokens[1].type == TokenType.OUTPUT
        assert tokens[2].type == TokenType.INOUT


class TestNumberRecognition:
    """测试数字识别"""

    def test_decimal_number(self):
        """测试十进制数字"""
        lexer = VerilogLexer("123")
        tokens = lexer.tokenize()
        assert tokens[0].type == TokenType.NUMBER
        assert tokens[0].value == "123"

    def test_hex_number(self):
        """测试十六进制数字"""
        lexer = VerilogLexer("8'hFF")
        tokens = lexer.tokenize()
        assert tokens[0].type == TokenType.NUMBER
        assert tokens[0].value == "8'hFF"

    def test_binary_number(self):
        """测试二进制数字"""
        lexer = VerilogLexer("4'b1010")
        tokens = lexer.tokenize()
        assert tokens[0].type == TokenType.NUMBER
        assert tokens[0].value == "4'b1010"

    def test_octal_number(self):
        """测试八进制数字"""
        lexer = VerilogLexer("6'o77")
        tokens = lexer.tokenize()
        assert tokens[0].type == TokenType.NUMBER
        assert tokens[0].value == "6'o77"

    def test_number_with_underscores(self):
        """测试带下划线的数字"""
        lexer = VerilogLexer("16'b1010_0101_1010_0101")
        tokens = lexer.tokenize()
        assert tokens[0].type == TokenType.NUMBER


class TestIdentifierRecognition:
    """测试标识符识别"""

    def test_simple_identifier(self):
        """测试简单标识符"""
        lexer = VerilogLexer("mySignal")
        tokens = lexer.tokenize()
        assert tokens[0].type == TokenType.IDENTIFIER
        assert tokens[0].value == "mySignal"

    def test_identifier_with_underscore(self):
        """测试带下划线的标识符"""
        lexer = VerilogLexer("my_signal_123")
        tokens = lexer.tokenize()
        assert tokens[0].type == TokenType.IDENTIFIER

    def test_identifier_with_dollar(self):
        """测试带美元符号的标识符"""
        lexer = VerilogLexer("$display")
        tokens = lexer.tokenize()
        assert tokens[0].type == TokenType.IDENTIFIER
        assert tokens[0].value == "$display"


class TestOperatorRecognition:
    """测试运算符识别"""

    def test_arithmetic_operators(self):
        """测试算术运算符"""
        lexer = VerilogLexer("+ - * / %")
        tokens = lexer.tokenize()
        assert tokens[0].type == TokenType.PLUS
        assert tokens[1].type == TokenType.MINUS
        assert tokens[2].type == TokenType.STAR
        assert tokens[3].type == TokenType.SLASH
        assert tokens[4].type == TokenType.PERCENT

    def test_relational_operators(self):
        """测试关系运算符"""
        lexer = VerilogLexer("== != < > <= >=")
        tokens = lexer.tokenize()
        assert tokens[0].type == TokenType.EQ
        assert tokens[1].type == TokenType.NE
        assert tokens[2].type == TokenType.LT
        assert tokens[3].type == TokenType.GT
        assert tokens[4].type == TokenType.LE
        assert tokens[5].type == TokenType.GE

    def test_logical_operators(self):
        """测试逻辑运算符"""
        lexer = VerilogLexer("&& || !")
        tokens = lexer.tokenize()
        assert tokens[0].type == TokenType.AND
        assert tokens[1].type == TokenType.OR
        assert tokens[2].type == TokenType.NOT

    def test_bitwise_operators(self):
        """测试位运算符"""
        lexer = VerilogLexer("& | ^ ~ << >>")
        tokens = lexer.tokenize()
        assert tokens[0].type == TokenType.BIT_AND
        assert tokens[1].type == TokenType.BIT_OR
        assert tokens[2].type == TokenType.BIT_XOR
        assert tokens[3].type == TokenType.BIT_NOT
        assert tokens[4].type == TokenType.LSHIFT
        assert tokens[5].type == TokenType.RSHIFT


class TestCommentHandling:
    """测试注释处理"""

    def test_single_line_comment(self):
        """测试单行注释"""
        lexer = VerilogLexer("// This is a comment\nmodule")
        tokens = lexer.tokenize(include_comments=True)
        assert tokens[0].type == TokenType.COMMENT
        assert "This is a comment" in tokens[0].value

    def test_block_comment(self):
        """测试块注释"""
        lexer = VerilogLexer("/* This is a\nblock comment */")
        tokens = lexer.tokenize(include_comments=True)
        assert tokens[0].type == TokenType.COMMENT

    def test_comment_excluded_by_default(self):
        """测试默认情况下注释被排除"""
        lexer = VerilogLexer("// Comment\nmodule")
        tokens = lexer.tokenize()
        # 默认情况下注释应该被排除
        comment_tokens = [t for t in tokens if t.type == TokenType.COMMENT]
        assert len(comment_tokens) == 0


class TestComplexVerilogCode:
    """测试复杂Verilog代码的词法分析"""

    def test_simple_module_declaration(self):
        """测试简单模块声明"""
        code = """
        module SimpleDUT;
            rand logic [15:0] addr;
            randc logic [3:0] id;
        endmodule
        """
        lexer = VerilogLexer(code)
        tokens = lexer.tokenize()

        # 检查关键字
        token_types = [t.type for t in tokens if t.type != TokenType.NEWLINE and t.type != TokenType.EOF]
        assert TokenType.MODULE in token_types
        assert TokenType.ENDMODULE in token_types
        assert TokenType.RAND in token_types
        assert TokenType.RANDC in token_types
        assert TokenType.LOGIC in token_types

    def test_constraint_block_tokens(self):
        """测试约束块的token"""
        code = "constraint valid_addr { addr inside {[0x1000:0xFFFF]}; }"
        lexer = VerilogLexer(code)
        tokens = lexer.tokenize()

        token_types = [t.type for t in tokens if t.type != TokenType.EOF]
        assert TokenType.CONSTRAINT in token_types
        assert TokenType.IDENTIFIER in token_types
        assert TokenType.LBRACE in token_types
        assert TokenType.RBRACE in token_types


class TestErrorHandling:
    """测试错误处理"""

    def test_unknown_character(self):
        """测试无法识别的字符"""
        lexer = VerilogLexer("©")  # 版权符号
        with pytest.raises(ParseError) as exc_info:
            lexer.tokenize()
        assert "Unexpected character" in str(exc_info.value)

    def test_unterminated_string(self):
        """测试未终止的字符串"""
        lexer = VerilogLexer('"unterminated string\nmodule')
        with pytest.raises(ParseError) as exc_info:
            lexer.tokenize()
        assert "Unterminated string" in str(exc_info.value)


class TestPositionTracking:
    """测试位置跟踪"""

    def test_line_column_tracking(self):
        """测试行列位置跟踪"""
        code = "module\n  logic"
        lexer = VerilogLexer(code)
        tokens = lexer.tokenize()

        # module在第1行第1列
        module_token = [t for t in tokens if t.type == TokenType.MODULE][0]
        assert module_token.line == 1
        assert module_token.column == 1

        # logic在第2行
        logic_token = [t for t in tokens if t.type == TokenType.LOGIC][0]
        assert logic_token.line == 2

    def test_newline_token(self):
        """测试换行符token"""
        lexer = VerilogLexer("line1\nline2")
        tokens = lexer.tokenize()

        newline_tokens = [t for t in tokens if t.type == TokenType.NEWLINE]
        assert len(newline_tokens) == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
