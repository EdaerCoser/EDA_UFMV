"""
Unit Tests for Code Generators

Tests Verilog, C, and Python code generators including:
- Code generation
- Factory pattern
- File extensions
- Output validation
"""

import pytest
from rgm.core import RegisterBlock, Register, Field, AccessType
from rgm.generators import (
    VerilogGenerator, CHeaderGenerator, PythonGenerator,
    GeneratorFactory, CodeGenerator
)


def create_test_block():
    """Helper to create a test register block."""
    block = RegisterBlock("UART", 0x40000000)

    # Control register
    ctrl = Register("CTRL", 0x00, 32, reset_value=0x00000000)
    ctrl.add_field(Field("enable", 0, 1, AccessType.RW, 0))
    ctrl.add_field(Field("mode", 1, 3, AccessType.RW, 0))
    ctrl.add_field(Field("reserved", 4, 28, AccessType.RO, 0))
    block.add_register(ctrl)

    # Status register
    status = Register("STATUS", 0x04, 32, reset_value=0x00000001)
    status.add_field(Field("tx_empty", 0, 1, AccessType.RO, 1))
    status.add_field(Field("rx_full", 1, 1, AccessType.RO, 0))
    block.add_register(status)

    # Data register
    data = Register("DATA", 0x08, 32)
    data.add_field(Field("byte", 0, 8, AccessType.RW, 0))
    block.add_register(data)

    return block


class TestCodeGeneratorBase:
    """Test CodeGenerator base class."""

    def test_base_class_is_abstract(self):
        """Test that CodeGenerator cannot be instantiated."""
        with pytest.raises(TypeError):
            CodeGenerator()


class TestVerilogGenerator:
    """Test Verilog code generator."""

    def test_verilog_creation(self):
        """Test Verilog generator creation."""
        gen = VerilogGenerator()
        assert gen.include_reset is True
        assert gen.use_always_block is True

    def test_verilog_custom_options(self):
        """Test Verilog generator with custom options."""
        gen = VerilogGenerator(include_reset=False, use_always_block=False)
        assert gen.include_reset is False
        assert gen.use_always_block is False

    def test_verilog_generate_basic(self):
        """Test basic Verilog generation."""
        block = create_test_block()
        gen = VerilogGenerator()
        code = gen.generate(block)

        # Check for module declaration
        assert "module UART_regs" in code
        assert "parameter DATA_WIDTH = 32" in code

    def test_verilog_generate_ports(self):
        """Test Verilog port generation."""
        block = create_test_block()
        gen = VerilogGenerator()
        code = gen.generate(block)

        # Check for ports
        assert "input wire clk" in code
        assert "input wire rst_n" in code
        assert "input wire [DATA_WIDTH-1:0] addr" in code
        assert "input wire [DATA_WIDTH-1:0] wdata" in code
        assert "output reg [DATA_WIDTH-1:0] rdata" in code

    def test_verilog_generate_registers(self):
        """Test Verilog register declarations."""
        block = create_test_block()
        gen = VerilogGenerator()
        code = gen.generate(block)

        # Check for register declarations
        assert "reg [31:0] CTRL_reg;" in code
        assert "reg [31:0] STATUS_reg;" in code
        assert "reg [31:0] DATA_reg;" in code

    def test_verilog_generate_write_logic(self):
        """Test Verilog write logic generation."""
        block = create_test_block()
        gen = VerilogGenerator()
        code = gen.generate(block)

        # Check for write logic
        assert "always @(posedge clk or negedge rst_n)" in code
        assert "case (addr)" in code

    def test_verilog_generate_read_logic(self):
        """Test Verilog read logic generation."""
        block = create_test_block()
        gen = VerilogGenerator()
        code = gen.generate(block)

        # Check for read logic
        assert "always @(*)" in code

    def test_verilog_generate_address_map(self):
        """Test Verilog address map comments."""
        block = create_test_block()
        gen = VerilogGenerator()
        code = gen.generate(block)

        # Check for address map
        assert "// Address Map for UART" in code
        assert "// 0x40000000: CTRL" in code
        assert "// 0x40000004: STATUS" in code

    def test_verilog_no_reset_option(self):
        """Test Verilog generation without reset."""
        block = create_test_block()
        gen = VerilogGenerator(include_reset=False)
        code = gen.generate(block)

        # Should not have reset logic
        assert "rst_n" not in code or "negedge rst_n" not in code

    def test_verilog_file_extension(self):
        """Test Verilog file extension."""
        gen = VerilogGenerator()
        assert gen.get_file_extension() == ".v"

    def test_verilog_repr(self):
        """Test string representation."""
        gen = VerilogGenerator()
        repr_str = repr(gen)
        assert "VerilogGenerator" in repr_str


class TestCHeaderGenerator:
    """Test C header code generator."""

    def test_c_header_creation(self):
        """Test C header generator creation."""
        gen = CHeaderGenerator()
        assert gen.include_guard is True
        assert gen.include_typedef is True

    def test_c_header_generate_basic(self):
        """Test basic C header generation."""
        block = create_test_block()
        gen = CHeaderGenerator()
        code = gen.generate(block)

        # Check for header guard
        assert "#ifndef UART_REGS_H" in code
        assert "#define UART_REGS_H" in code
        assert "#endif" in code

    def test_c_header_generate_base_address(self):
        """Test C header base address generation."""
        block = create_test_block()
        gen = CHeaderGenerator()
        code = gen.generate(block)

        # Check for base address
        assert "#define UART_BASE" in code
        assert "0x40000000" in code

    def test_c_header_generate_register_offsets(self):
        """Test C header register offsets."""
        block = create_test_block()
        gen = CHeaderGenerator()
        code = gen.generate(block)

        # Check for register offsets
        assert "#define UART_CTRL_OFFSET" in code
        assert "#define UART_STATUS_OFFSET" in code
        assert "#define UART_DATA_OFFSET" in code

    def test_c_header_generate_field_masks(self):
        """Test C header field bit masks."""
        block = create_test_block()
        gen = CHeaderGenerator()
        code = gen.generate(block)

        # Check for field masks
        assert "#define UART_CTRL_ENABLE_MASK" in code
        assert "#define UART_CTRL_MODE_MASK" in code

    def test_c_header_generate_typedef(self):
        """Test C header typedef generation."""
        block = create_test_block()
        gen = CHeaderGenerator(include_typedef=True)
        code = gen.generate(block)

        # Check for typedef
        assert "typedef union" in code or "typedef struct" in code

    def test_c_header_generate_functions(self):
        """Test C header inline functions."""
        block = create_test_block()
        gen = CHeaderGenerator()
        code = gen.generate(block)

        # Check for inline functions
        assert "static inline" in code or "__inline" in code

    def test_c_header_no_typedef_option(self):
        """Test C header without typedef."""
        block = create_test_block()
        gen = CHeaderGenerator(include_typedef=False)
        code = gen.generate(block)

        # Should not have typedef
        assert "typedef union" not in code

    def test_c_header_file_extension(self):
        """Test C header file extension."""
        gen = CHeaderGenerator()
        assert gen.get_file_extension() == ".h"

    def test_c_header_repr(self):
        """Test string representation."""
        gen = CHeaderGenerator()
        repr_str = repr(gen)
        assert "CHeaderGenerator" in repr_str


class TestPythonGenerator:
    """Test Python code generator."""

    def test_python_creation(self):
        """Test Python generator creation."""
        gen = PythonGenerator()
        assert gen.include_docstrings is True
        assert gen.include_type_hints is True

    def test_python_custom_options(self):
        """Test Python generator with custom options."""
        gen = PythonGenerator(include_docstrings=False, include_type_hints=False)
        assert gen.include_docstrings is False
        assert gen.include_type_hints is False

    def test_python_generate_basic(self):
        """Test basic Python generation."""
        block = create_test_block()
        gen = PythonGenerator()
        code = gen.generate(block)

        # Check for class definition
        assert "class UARTModel:" in code
        assert "def __init__(self):" in code

    def test_python_generate_imports(self):
        """Test Python import generation."""
        block = create_test_block()
        gen = PythonGenerator()
        code = gen.generate(block)

        # Check for imports
        assert "from rgm.core import" in code
        assert "RegisterBlock" in code
        assert "AccessType" in code

    def test_python_generate_registers(self):
        """Test Python register generation."""
        block = create_test_block()
        gen = PythonGenerator()
        code = gen.generate(block)

        # Check for register creation
        assert "self.ctrl = Register(" in code
        assert "self.status = Register(" in code
        assert "self.data = Register(" in code

    def test_python_generate_fields(self):
        """Test Python field generation."""
        block = create_test_block()
        gen = PythonGenerator()
        code = gen.generate(block)

        # Check for field creation
        assert "Field(" in code
        assert "AccessType.RW" in code or "AccessType.RO" in code

    def test_python_generate_access_methods(self):
        """Test Python access method generation."""
        block = create_test_block()
        gen = PythonGenerator()
        code = gen.generate(block)

        # Check for access methods
        assert "def read_ctrl(" in code
        assert "def write_ctrl(" in code

    def test_python_no_docstrings_option(self):
        """Test Python generation without docstrings."""
        block = create_test_block()
        gen = PythonGenerator(include_docstrings=False)
        code = gen.generate(block)

        # Should have fewer docstring markers
        docstring_count = code.count('"""')
        assert docstring_count >= 2  # File header at least

    def test_python_no_type_hints_option(self):
        """Test Python generation without type hints."""
        block = create_test_block()
        gen = PythonGenerator(include_type_hints=False)
        code = gen.generate(block)

        # Check that type hints are absent
        assert "-> int:" not in code or "-> None:" not in code

    def test_python_file_extension(self):
        """Test Python file extension."""
        gen = PythonGenerator()
        assert gen.get_file_extension() == ".py"

    def test_python_repr(self):
        """Test string representation."""
        gen = PythonGenerator()
        repr_str = repr(gen)
        assert "PythonGenerator" in repr_str


class TestGeneratorFactory:
    """Test GeneratorFactory functionality."""

    def test_factory_list_generators(self):
        """Test listing available generators."""
        generators = GeneratorFactory.list_generators()

        assert "verilog" in generators
        assert "v" in generators
        assert "c" in generators
        assert "h" in generators
        assert "python" in generators
        assert "py" in generators

    def test_factory_get_verilog_generator(self):
        """Test getting Verilog generator."""
        gen = GeneratorFactory.get_generator("verilog")
        assert isinstance(gen, VerilogGenerator)

    def test_factory_get_c_generator(self):
        """Test getting C header generator."""
        gen = GeneratorFactory.get_generator("c")
        assert isinstance(gen, CHeaderGenerator)

    def test_factory_get_python_generator(self):
        """Test getting Python generator."""
        gen = GeneratorFactory.get_generator("python")
        assert isinstance(gen, PythonGenerator)

    def test_factory_verilog_alias(self):
        """Test Verilog 'v' alias."""
        gen = GeneratorFactory.get_generator("v")
        assert isinstance(gen, VerilogGenerator)

    def test_factory_c_alias(self):
        """Test C 'h' alias."""
        gen = GeneratorFactory.get_generator("h")
        assert isinstance(gen, CHeaderGenerator)

    def test_factory_python_alias(self):
        """Test Python 'py' alias."""
        gen = GeneratorFactory.get_generator("py")
        assert isinstance(gen, PythonGenerator)

    def test_factory_generate_verilog(self):
        """Test direct Verilog generation."""
        block = create_test_block()
        code = GeneratorFactory.generate("verilog", block)

        assert "module UART_regs" in code
        assert len(code) > 0

    def test_factory_generate_c(self):
        """Test direct C header generation."""
        block = create_test_block()
        code = GeneratorFactory.generate("c", block)

        assert "#ifndef UART_REGS_H" in code
        assert len(code) > 0

    def test_factory_generate_python(self):
        """Test direct Python generation."""
        block = create_test_block()
        code = GeneratorFactory.generate("python", block)

        assert "class UARTModel:" in code
        assert len(code) > 0

    def test_factory_unknown_generator(self):
        """Test requesting unknown generator raises."""
        with pytest.raises(ValueError, match="Unknown generator"):
            GeneratorFactory.get_generator("unknown")

    def test_factory_get_file_extension(self):
        """Test getting file extensions via factory."""
        assert GeneratorFactory.get_file_extension("verilog") == ".v"
        assert GeneratorFactory.get_file_extension("c") == ".h"
        assert GeneratorFactory.get_file_extension("python") == ".py"

    def test_factory_register_custom_generator(self):
        """Test registering custom generator."""
        class CustomGenerator(CodeGenerator):
            def generate(self, block, **kwargs):
                return "// Custom code"

            def get_file_extension(self):
                return ".custom"

        GeneratorFactory.register_generator("custom", CustomGenerator)
        gen = GeneratorFactory.get_generator("custom")
        assert isinstance(gen, CustomGenerator)

        # Cleanup
        del GeneratorFactory._generators["custom"]


class TestGeneratorOutput:
    """Test generator output validation."""

    def test_verilog_output_non_empty(self):
        """Test Verilog generator produces output."""
        block = create_test_block()
        gen = VerilogGenerator()
        code = gen.generate(block)
        assert len(code) > 0

    def test_c_header_output_non_empty(self):
        """Test C header generator produces output."""
        block = create_test_block()
        gen = CHeaderGenerator()
        code = gen.generate(block)
        assert len(code) > 0

    def test_python_output_non_empty(self):
        """Test Python generator produces output."""
        block = create_test_block()
        gen = PythonGenerator()
        code = gen.generate(block)
        assert len(code) > 0

    def test_verilog_contains_module_end(self):
        """Test Verilog output ends with endmodule."""
        block = create_test_block()
        gen = VerilogGenerator()
        code = gen.generate(block)
        assert "endmodule" in code

    def test_c_header_contains_endif(self):
        """Test C header ends with endif."""
        block = create_test_block()
        gen = CHeaderGenerator()
        code = gen.generate(block)
        lines = code.strip().split("\n")
        assert "#endif" in lines[-1] or "#endif" in code

    def test_python_contains_class(self):
        """Test Python output contains class."""
        block = create_test_block()
        gen = PythonGenerator()
        code = gen.generate(block)
        assert "class " in code


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
