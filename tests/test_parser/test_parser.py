"""
语法分析器单元测试

测试Verilog语法分析器的各种功能
"""

import pytest

from parser.core.lexer import VerilogLexer
from parser.core.parser import VerilogParser
from parser.core.ast_nodes import (
    ModuleDecl,
    RegisterDecl,
    ConstraintBlock,
    BinaryExpr,
    VariableExpr,
    ConstantExpr,
)


class TestModuleParsing:
    """测试模块解析"""

    def test_simple_module(self):
        """测试简单模块解析"""
        code = """
        module SimpleDUT;
            logic [15:0] addr;
        endmodule
        """
        lexer = VerilogLexer(code)
        tokens = lexer.tokenize()
        parser = VerilogParser(tokens)
        modules = parser.parse()

        assert len(modules) == 1
        assert modules[0].name == "SimpleDUT"

    def test_module_with_parameters(self):
        """测试带参数的模块"""
        code = """
        module ParamDUT #(
            parameter WIDTH = 8,
            parameter DEPTH = 1024
        );
            logic [WIDTH-1:0] data;
        endmodule
        """
        lexer = VerilogLexer(code)
        tokens = lexer.tokenize()
        parser = VerilogParser(tokens)
        modules = parser.parse()

        assert len(modules) == 1
        assert len(modules[0].parameters) == 2
        assert modules[0].parameters[0].name == "WIDTH"
        assert modules[0].parameters[1].name == "DEPTH"

    def test_module_with_ports(self):
        """测试带端口的模块"""
        code = """
        module PortDUT (
            input logic clk,
            output logic [7:0] data
        );
            logic [15:0] addr;
        endmodule
        """
        lexer = VerilogLexer(code)
        tokens = lexer.tokenize()
        parser = VerilogParser(tokens)
        modules = parser.parse()

        assert len(modules) == 1
        assert len(modules[0].ports) == 2
        assert modules[0].ports[0].name == "clk"
        assert modules[0].ports[1].name == "data"


class TestRegisterParsing:
    """测试寄存器声明解析"""

    def test_simple_register(self):
        """测试简单寄存器声明"""
        code = """
        module Test;
            logic [15:0] addr;
        endmodule
        """
        lexer = VerilogLexer(code)
        tokens = lexer.tokenize()
        parser = VerilogParser(tokens)
        modules = parser.parse()

        registers = [item for item in modules[0].items if isinstance(item, RegisterDecl)]
        assert len(registers) == 1
        assert registers[0].name == "addr"
        assert registers[0].data_type == "logic"
        assert registers[0].bit_width == (15, 0)

    def test_rand_register(self):
        """测试rand寄存器声明"""
        code = """
        module Test;
            rand logic [15:0] addr;
        endmodule
        """
        lexer = VerilogLexer(code)
        tokens = lexer.tokenize()
        parser = VerilogParser(tokens)
        modules = parser.parse()

        registers = [item for item in modules[0].items if isinstance(item, RegisterDecl)]
        assert len(registers) == 1
        assert registers[0].is_rand == True
        assert registers[0].is_randc == False

    def test_randc_register(self):
        """测试randc寄存器声明"""
        code = """
        module Test;
            randc logic [3:0] id;
        endmodule
        """
        lexer = VerilogLexer(code)
        tokens = lexer.tokenize()
        parser = VerilogParser(tokens)
        modules = parser.parse()

        registers = [item for item in modules[0].items if isinstance(item, RegisterDecl)]
        assert len(registers) == 1
        assert registers[0].is_randc == True
        assert registers[0].bit_width == (3, 0)

    def test_multiple_registers(self):
        """测试多个寄存器声明"""
        code = """
        module Test;
            rand logic [15:0] addr;
            randc logic [3:0] id;
            logic [7:0] data;
        endmodule
        """
        lexer = VerilogLexer(code)
        tokens = lexer.tokenize()
        parser = VerilogParser(tokens)
        modules = parser.parse()

        registers = [item for item in modules[0].items if isinstance(item, RegisterDecl)]
        assert len(registers) == 3
        assert registers[0].name == "addr"
        assert registers[1].name == "id"
        assert registers[2].name == "data"


class TestConstraintParsing:
    """测试约束块解析"""

    def test_simple_constraint(self):
        """测试简单约束块"""
        code = """
        module Test;
            rand logic [15:0] addr;

            constraint valid_addr {
                addr > 16'h1000;
            }
        endmodule
        """
        lexer = VerilogLexer(code)
        tokens = lexer.tokenize()
        parser = VerilogParser(tokens)
        modules = parser.parse()

        constraints = [item for item in modules[0].items if isinstance(item, ConstraintBlock)]
        assert len(constraints) == 1
        assert constraints[0].name == "valid_addr"
        assert len(constraints[0].expressions) > 0

    def test_constraint_with_binary_expr(self):
        """测试包含二元表达式的约束"""
        code = """
        module Test;
            rand logic [15:0] addr;

            constraint valid_range {
                addr >= 16'h1000 && addr <= 16'hFFFF;
            }
        endmodule
        """
        lexer = VerilogLexer(code)
        tokens = lexer.tokenize()
        parser = VerilogParser(tokens)
        modules = parser.parse()

        constraints = [item for item in modules[0].items if isinstance(item, ConstraintBlock)]
        assert len(constraints) == 1


class TestExpressionParsing:
    """测试表达式解析"""

    def test_binary_expression(self):
        """测试二元表达式解析"""
        code = """
        module Test;
            rand logic a;
            constraint c { a > 0; }
        endmodule
        """
        lexer = VerilogLexer(code)
        tokens = lexer.tokenize()
        parser = VerilogParser(tokens)
        modules = parser.parse()

        constraints = [item for item in modules[0].items if isinstance(item, ConstraintBlock)]
        assert len(constraints) == 1
        assert len(constraints[0].expressions) > 0

    def test_variable_expression(self):
        """测试变量表达式"""
        code = """
        module Test;
            rand logic my_var;
        endmodule
        """
        lexer = VerilogLexer(code)
        tokens = lexer.tokenize()
        parser = VerilogParser(tokens)
        modules = parser.parse()

        registers = [item for item in modules[0].items if isinstance(item, RegisterDecl)]
        assert len(registers) == 1
        assert registers[0].name == "my_var"


class TestComplexVerilogCode:
    """测试复杂Verilog代码解析"""

    def test_complete_dut_model(self):
        """测试完整的DUT模型"""
        code = """
        module SimpleDUT;
            rand logic [15:0] addr;
            randc logic [3:0] id;
            rand logic [7:0] data;

            constraint valid_addr {
                addr >= 16'h1000;
                addr <= 16'hFFFF;
            }

            constraint valid_data {
                data > 0;
                data < 255;
            }
        endmodule
        """
        lexer = VerilogLexer(code)
        tokens = lexer.tokenize()
        parser = VerilogParser(tokens)
        modules = parser.parse()

        assert len(modules) == 1
        assert modules[0].name == "SimpleDUT"

        registers = [item for item in modules[0].items if isinstance(item, RegisterDecl)]
        assert len(registers) == 3

        constraints = [item for item in modules[0].items if isinstance(item, ConstraintBlock)]
        assert len(constraints) == 2
        assert constraints[0].name == "valid_addr"
        assert constraints[1].name == "valid_data"

    def test_module_with_params_and_ports(self):
        """测试带参数和端口的完整模块"""
        code = """
        module CompleteDUT #(
            parameter WIDTH = 8
        ) (
            input logic clk,
            output logic [WIDTH-1:0] data
        );
            rand logic [15:0] addr;
            rand logic [7:0] value;

            constraint valid {
                addr > 0;
                value < 256;
            }
        endmodule
        """
        lexer = VerilogLexer(code)
        tokens = lexer.tokenize()
        parser = VerilogParser(tokens)
        modules = parser.parse()

        assert len(modules) == 1
        assert len(modules[0].parameters) == 1
        assert len(modules[0].ports) == 2


class TestEdgeCases:
    """测试边界情况"""

    def test_empty_module(self):
        """测试空模块"""
        code = """
        module EmptyDUT;
        endmodule
        """
        lexer = VerilogLexer(code)
        tokens = lexer.tokenize()
        parser = VerilogParser(tokens)
        modules = parser.parse()

        assert len(modules) == 1
        assert len(modules[0].items) == 0

    def test_module_with_comments(self):
        """测试带注释的模块"""
        code = """
        // This is a comment
        module CommentDUT;
            /* This is a block comment */
            rand logic [15:0] addr; // Line comment
        endmodule
        """
        lexer = VerilogLexer(code)
        tokens = lexer.tokenize()
        parser = VerilogParser(tokens)
        modules = parser.parse()

        assert len(modules) == 1
        registers = [item for item in modules[0].items if isinstance(item, RegisterDecl)]
        assert len(registers) == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
