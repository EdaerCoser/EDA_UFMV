# SV Randomizer

A Python implementation of SystemVerilog-style random constraint solver for hardware verification test generation.

## Features

- **rand/randc Variables**: Standard random (rand) and cyclic random (randc) variables
- **Constraint System**: Support for `inside`, `dist`, relational/logical operators, and conditional constraints
- **Pluggable Solvers**: Pure Python backend (no dependencies) and Z3 backend (industrial-grade)
- **Output Formats**: Generate test vectors in Verilog format for simulation

## Installation

```bash
# Basic installation (pure Python, no external dependencies)
pip install -e .

# With Z3 solver backend for enhanced performance
pip install -e ".[z3]"

# With statistical validation tools
pip install -e ".[stat]"

# Development installation
pip install -e ".[dev]"
```

## Quick Start

```python
from sv_randomizer import Randomizable, rand, randc, constraint, VarProxy, inside

class Packet(Randomizable):
    @rand(bit_width=16)
    def src_addr(self):
        return 0

    @rand(bit_width=16)
    def dest_addr(self):
        return 0

    @randc(bit_width=4)  # Cyclic random - ensures unique IDs
    def packet_id(self):
        return 0

    @rand(enum_values=["READ", "WRITE", "ACK", "NACK"])
    def opcode(self):
        return "READ"

    @constraint("valid_addr")
    def valid_addr_c(self):
        return VarProxy("src_addr") >= 0x1000

    @constraint("addr_not_equal")
    def addr_not_equal_c(self):
        return VarProxy("src_addr") != VarProxy("dest_addr")

# Generate random packets
pkt = Packet()
for i in range(10):
    if pkt.randomize():
        print(f"Packet {i+1}: src=0x{pkt.src_addr:04x}, dst=0x{pkt.dest_addr:04x}, "
              f"id={pkt.packet_id}, opcode={pkt.opcode}")
```

## Constraint Syntax

### Inside Constraint

```python
@constraint("length_range")
def length_range_c(self):
    return inside([(64, 64), (128, 255), (512, 1518)]) == VarProxy("length")
```

### Weighted Distribution

```python
@constraint("opcode_weighted")
def opcode_weighted_c(self):
    return dist({"READ": 50, "WRITE": 30, "ACK": 15, "NACK": 5}) == VarProxy("opcode")
```

### Implication

```python
@constraint("implication")
def implication_c(self):
    # If addr > 1000, then length < 64
    return (VarProxy("addr") > 1000).implies(VarProxy("length") < 64)
```

## Solver Backends

```python
from sv_randomizer.solvers import SolverFactory

# Use pure Python solver (default)
SolverFactory.set_default_backend("pure_python")

# Use Z3 solver (if installed)
SolverFactory.set_default_backend("z3")

# Check available backends
print(SolverFactory.list_backends())
```

## Output Formats

```python
from sv_randomizer.formatters import VerilogFormatter

pkt = Packet()
pkt.randomize()

formatter = VerilogFormatter()

# Format as Verilog assignment
verilog_code = formatter.format(pkt)
print(verilog_code)

# Generate complete testbench
testbench = formatter.format_testbench(pkt, test_name="packet_test")
print(testbench)
```

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
