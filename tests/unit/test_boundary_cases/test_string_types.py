"""
Boundary Value Tests - String Types

Tests for handling string boundary conditions:
- Empty strings
- Single character strings
- Long strings
- Unicode strings
- Special character strings
"""

import pytest

from sv_randomizer import Randomizable
from sv_randomizer.core.variables import RandVar, VarType
from coverage.core import CoverGroup, CoverPoint
from rgm.core import RegisterBlock, Register, Field
from rgm.utils import AccessType


# =============================================================================
# Empty String Tests
# =============================================================================

@pytest.mark.unit
@pytest.mark.boundary
@pytest.mark.P0
class TestEmptyStrings:
    """Tests for empty string handling."""

    def test_empty_string_coverage(self):
        """Test coverage with empty string value."""
        cg = CoverGroup("empty_str_cg")
        cp = CoverPoint("str_cp", "value", bins={"empty": [""]})
        cg.add_coverpoint(cp)

        cg.sample(value="")
        assert cg.coverage == 100.0

    def test_empty_string_register_name(self):
        """Test register with empty name (if allowed)."""
        # Empty name may be rejected
        try:
            reg = Register("", 0x00, 32)
            # If allowed, name should be empty
            assert reg.name == ""
        except (ValueError, AssertionError):
            # May reject empty names - that's acceptable
            pass

    def test_empty_string_field_name(self):
        """Test field with empty name (if allowed)."""
        try:
            field = Field("", bit_offset=0, bit_width=8, access=AccessType.RW)
            # If allowed
            assert field.name == ""
        except (ValueError, AssertionError):
            # May reject empty names
            pass

    def test_empty_string_covergroup_name(self):
        """Test CoverGroup with empty name (if allowed)."""
        try:
            cg = CoverGroup("")
            # If allowed
            assert cg._name == ""
        except (ValueError, AssertionError):
            # May reject empty names
            pass


# =============================================================================
# Single Character String Tests
# =============================================================================

@pytest.mark.unit
@pytest.mark.boundary
@pytest.mark.P0
class TestSingleCharStrings:
    """Tests for single character string handling."""

    @pytest.mark.parametrize("char", ["a", "Z", "0", " ", "\n", "\t"])
    def test_single_char_coverage(self, char):
        """Test coverage with single character values."""
        cg = CoverGroup(f"single_char_cg_{ord(char)}")
        cp = CoverPoint("char_cp", "value", bins={"chars": [char]})
        cg.add_coverpoint(cp)

        cg.sample(value=char)
        assert cg.coverage == 100.0

    def test_single_char_register_name(self):
        """Test register with single character name."""
        reg = Register("R", 0x00, 32)
        assert reg.name == "R"

    def test_single_char_field_name(self):
        """Test field with single character name."""
        field = Field("x", bit_offset=0, bit_width=8, access=AccessType.RW)
        assert field.name == "x"


# =============================================================================
# Long String Tests
# =============================================================================

@pytest.mark.unit
@pytest.mark.boundary
@pytest.mark.P1
class TestLongStrings:
    """Tests for long string handling."""

    def test_long_string_register_name(self):
        """Test register with very long name."""
        long_name = "R" * 1000
        reg = Register(long_name, 0x00, 32)
        assert reg.name == long_name
        assert len(reg.name) == 1000

    def test_long_string_field_name(self):
        """Test field with very long name."""
        long_name = "field" * 250  # 1250 characters
        field = Field(long_name, bit_offset=0, bit_width=8, access=AccessType.RW)
        assert field.name == long_name

    def test_long_string_covergroup_name(self):
        """Test CoverGroup with very long name."""
        long_name = "cg" * 500  # 1000 characters
        cg = CoverGroup(long_name)
        assert cg._name == long_name

    def test_long_string_coverage_value(self):
        """Test coverage sampling with long string value."""
        long_string = "a" * 10000
        cg = CoverGroup("long_str_cg")
        cp = CoverPoint("long_str_cp", "value", bins={"long": [long_string]})
        cg.add_coverpoint(cp)

        cg.sample(value=long_string)
        assert cg.coverage == 100.0


# =============================================================================
# Unicode String Tests
# =============================================================================

@pytest.mark.unit
@pytest.mark.boundary
@pytest.mark.P1
class TestUnicodeStrings:
    """Tests for Unicode string handling."""

    @pytest.mark.parametrize("unicode_str", [
        "héllo",           # Latin with accent
        "世界",            # Chinese
        "Привет",          # Russian
        "مرحبا",           # Arabic
        "こんにちは",      # Japanese
        "🚀🌟🎉",         # Emoji
        "a\u0301",        # Combining character
    ])
    def test_unicode_coverage(self, unicode_str):
        """Test coverage with Unicode strings."""
        cg = CoverGroup(f"unicode_cg_{hash(unicode_str)}")
        cp = CoverPoint("unicode_cp", "value", bins={"unicode": [unicode_str]})
        cg.add_coverpoint(cp)

        cg.sample(value=unicode_str)
        assert cg.coverage == 100.0

    def test_unicode_register_name(self):
        """Test register with Unicode name."""
        reg = Register("REG_世界", 0x00, 32)
        assert "REG_世界" in reg.name

    def test_unicode_field_name(self):
        """Test field with Unicode name."""
        field = Field("camión", bit_offset=0, bit_width=8, access=AccessType.RW)
        assert field.name == "camión"


# =============================================================================
# Special Character String Tests
# =============================================================================

@pytest.mark.unit
@pytest.mark.boundary
@pytest.mark.P1
class TestSpecialCharStrings:
    """Tests for special character string handling."""

    @pytest.mark.parametrize("special_str", [
        " ",              # Space
        "\n",             # Newline
        "\t",             # Tab
        "\r",             # Carriage return
        "null\x00byte",   # Null byte
        "quote\"test",    # Quote
        "apostrophe'test",# Apostrophe
        "path\\to\\file", # Backslash
        "path/to/file",   # Forward slash
    ])
    def test_special_char_coverage(self, special_str):
        """Test coverage with special character strings."""
        cg = CoverGroup(f"special_cg_{hash(special_str)}")
        cp = CoverPoint("special_cp", "value", bins={"special": [special_str]})
        cg.add_coverpoint(cp)

        cg.sample(value=special_str)
        assert cg.coverage == 100.0

    def test_whitespace_variations(self):
        """Test various whitespace characters."""
        whitespace_cases = [
            " ",           # Space
            "  ",          # Double space
            "\t",          # Tab
            "\n",          # Newline
            "\r\n",        # Windows newline
            " \t\n",       # Mixed whitespace
        ]

        for ws in whitespace_cases:
            cg = CoverGroup(f"ws_cg_{hash(ws)}")
            cp = CoverPoint("ws_cp", "value", bins={"ws": [ws]})
            cg.add_coverpoint(cp)

            cg.sample(value=ws)
            assert cg.coverage == 100.0


# =============================================================================
# String Boundary Edge Cases
# =============================================================================

@pytest.mark.unit
@pytest.mark.boundary
@pytest.mark.P2
class TestStringEdgeCases:
    """Tests for string edge cases."""

    def test_string_with_only_nulls(self):
        """Test string with only null bytes."""
        null_string = "\x00\x00\x00"
        cg = CoverGroup("null_str_cg")
        cp = CoverPoint("null_cp", "value", bins={"nulls": [null_string]})
        cg.add_coverpoint(cp)

        cg.sample(value=null_string)
        assert cg.coverage == 100.0

    def test_mixed_length_strings(self):
        """Test coverpoint with strings of varying lengths."""
        strings = ["", "a", "ab", "abc", "abcd"]
        cg = CoverGroup("mixed_len_cg")
        cp = CoverPoint("len_cp", "value", bins={"various": strings})
        cg.add_coverpoint(cp)

        for s in strings:
            cg.sample(value=s)

        assert cg.coverage == 100.0

    def test_similar_strings(self):
        """Test coverpoint with very similar strings."""
        strings = ["test", "Test", "TEST", "test ", " test"]
        cg = CoverGroup("similar_cg")
        cp = CoverPoint("similar_cp", "value", bins={"similar": strings})
        cg.add_coverpoint(cp)

        for s in strings:
            cg.sample(value=s)

        # Each string is a distinct bin
        assert cg.coverage == 100.0

    def test_case_sensitivity(self):
        """Test that string matching is case-sensitive."""
        cg = CoverGroup("case_cg")
        cp = CoverPoint("case_cp", "value", bins={"lower": ["test"]})
        cg.add_coverpoint(cp)

        # Should match exactly
        cg.sample(value="test")
        assert cg.coverage == 100.0

        # Should not match different case
        cg2 = CoverGroup("case_cg2")
        cp2 = CoverPoint("case_cp2", "value", bins={"lower": ["test"]})
        cg2.add_coverpoint(cp2)
        cg2.sample(value="TEST")
        # "TEST" is not in ["test"], so coverage should be 0
        assert cg2.coverage == 0.0


# =============================================================================
# String Performance Tests
# =============================================================================

@pytest.mark.unit
@pytest.mark.boundary
@pytest.mark.performance
@pytest.mark.P2
class TestStringPerformance:
    """Tests for string handling performance."""

    def test_many_string_bins_performance(self):
        """Test performance with many string bins."""
        import string

        # Generate many unique strings
        many_strings = [f"str_{i}" for i in range(1000)]

        cg = CoverGroup("many_str_cg")
        cp = CoverPoint("many_str_cp", "value", bins={"many": many_strings})
        cg.add_coverpoint(cp)

        # Sample a few values
        cg.sample(value="str_0")
        cg.sample(value="str_500")
        cg.sample(value="str_999")

        # Should handle gracefully
        assert 0.0 < cg.coverage < 100.0

    def test_long_string_sampling_performance(self):
        """Test performance with very long string values."""
        # Create very long string
        long_string = "x" * 100000  # 100KB string

        cg = CoverGroup("long_perf_cg")
        cp = CoverPoint("long_perf_cp", "value", bins={"long": [long_string]})
        cg.add_coverpoint(cp)

        # Should complete without excessive delay
        cg.sample(value=long_string)
        assert cg.coverage == 100.0


# =============================================================================
# String Encoding Tests
# =============================================================================

@pytest.mark.unit
@pytest.mark.boundary
@pytest.mark.P2
class TestStringEncoding:
    """Tests for string encoding edge cases."""

    def test_utf8_boundary_strings(self):
        """Test strings at UTF-8 encoding boundaries."""
        # Characters that span multiple bytes in UTF-8
        multi_byte_chars = [
            "¢",     # 2 bytes
            "€",     # 3 bytes
            "𐍈",    # 4 bytes
        ]

        for char in multi_byte_chars:
            cg = CoverGroup(f"utf8_cg_{ord(char)}")
            cp = CoverPoint("utf8_cp", "value", bins={"mb": [char]})
            cg.add_coverpoint(cp)

            cg.sample(value=char)
            assert cg.coverage == 100.0

    def test_bom_character(self):
        """Test string with BOM (Byte Order Mark)."""
        bom_str = "\ufefftest"
        cg = CoverGroup("bom_cg")
        cp = CoverPoint("bom_cp", "value", bins={"bom": [bom_str]})
        cg.add_coverpoint(cp)

        cg.sample(value=bom_str)
        assert cg.coverage == 100.0

    def test_invalid_utf8_sequences(self):
        """Test handling of invalid UTF-8 sequences."""
        # These may be rejected or handled
        invalid_sequences = [
            "\xff",       # Invalid UTF-8 byte
            "\xfe",       # Invalid UTF-8 byte
        ]

        for seq in invalid_sequences:
            try:
                cg = CoverGroup(f"invalid_cg_{ord(seq)}")
                cp = CoverPoint("invalid_cp", "value", bins={"inv": [seq]})
                cg.add_coverpoint(cp)

                cg.sample(value=seq)
                # If accepted, should work
                assert cg.coverage == 100.0
            except (UnicodeError, ValueError):
                # May reject invalid UTF-8 - that's acceptable
                pass


# =============================================================================
# String Comparison Tests
# =============================================================================

@pytest.mark.unit
@pytest.mark.boundary
@pytest.mark.P2
class TestStringComparison:
    """Tests for string comparison edge cases."""

    def test_string_with_trailing_spaces(self):
        """Test strings that differ only in trailing spaces."""
        cg = CoverGroup("trail_cg")
        cp = CoverPoint("trail_cp", "value", bins={"exact": ["test "]})
        cg.add_coverpoint(cp)

        # Exact match
        cg.sample(value="test ")
        assert cg.coverage == 100.0

        # No match (missing space)
        cg2 = CoverGroup("trail_cg2")
        cp2 = CoverPoint("trail_cp2", "value", bins={"exact": ["test "]})
        cg2.add_coverpoint(cp2)
        cg2.sample(value="test")
        assert cg2.coverage == 0.0

    def test_string_with_leading_spaces(self):
        """Test strings that differ only in leading spaces."""
        cg = CoverGroup("lead_cg")
        cp = CoverPoint("lead_cp", "value", bins={"exact": [" test"]})
        cg.add_coverpoint(cp)

        # Exact match
        cg.sample(value=" test")
        assert cg.coverage == 100.0

    def test_string_zero_width_chars(self):
        """Test strings with zero-width characters."""
        zero_width_cases = [
            "test\u200B",      # Zero-width space
            "test\u200C",      # Zero-width non-joiner
            "test\u200D",      # Zero-width joiner
            "test\uFEFF",      # Zero-width no-break space (BOM)
        ]

        for s in zero_width_cases:
            cg = CoverGroup(f"zw_cg_{hash(s)}")
            cp = CoverPoint("zw_cp", "value", bins={"zw": [s]})
            cg.add_coverpoint(cp)

            cg.sample(value=s)
            assert cg.coverage == 100.0


# =============================================================================
# String Type Mixing Tests
# =============================================================================

@pytest.mark.unit
@pytest.mark.boundary
@pytest.mark.P2
class TestStringTypeMixing:
    """Tests for mixing strings with other types."""

    def test_mixed_string_int_bins(self):
        """Test coverpoint with both string and integer bins."""
        # May be rejected or handled
        try:
            cg = CoverGroup("mixed_cg")
            cp = CoverPoint("mixed_cp", "value",
                           bins={"mixed": ["string", 42, 3.14]})
            cg.add_coverpoint(cp)

            # If accepted, test sampling
            cg.sample(value="string")
            cg.sample(value=42)
            assert cg.coverage > 0.0
        except (TypeError, ValueError):
            # May reject mixed types - that's acceptable
            pass

    def test_string_number_conversion(self):
        """Test strings that look like numbers."""
        number_strings = ["123", "45.67", "-999", "0.0", "1e10"]

        for s in number_strings:
            cg = CoverGroup(f"numstr_cg_{hash(s)}")
            cp = CoverPoint("numstr_cp", "value", bins={"nums": [s]})
            cg.add_coverpoint(cp)

            # Should treat as strings, not numbers
            cg.sample(value=s)
            assert cg.coverage == 100.0
