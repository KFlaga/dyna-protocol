from . import protocol_types as types
from . import protocol_printer as printer


def tab(tabs=1):
    return " " * 4 * tabs


class CppValuePrinter(object):
    def visit_unknown(self, type, value):
        raise NotImplementedError()

    def visit_partbyte(self, type, value):
        if type.format == "hex":
            return "0x{:02x}u".format(value)
        return "{}u".format(value)

    def visit_uint8(self, type, value):
        if type.format == "hex":
            return "0x{:02x}u".format(value)
        return "{}u".format(value)

    def visit_int8(self, type, value):
        if type.format == "hex":
            return "0x{:02x}".format(value)
        return "{}".format(value)

    def visit_uint16(self, type, value):
        if type.format == "hex":
            return "0x{:04x}u".format(value)
        return "{}u".format(value)

    def visit_int16(self, type, value):
        if type.format == "hex":
            return "0x{:04x}".format(value)
        return "{}".format(value)

    def visit_uint32(self, type, value):
        if type.format == "hex":
            return "0x{:08x}u".format(value)
        return "{}u".format(value)

    def visit_int32(self, type, value):
        if type.format == "hex":
            return "0x{:08x}".format(value)
        return "{}".format(value)

    def visit_array(self, type, value):
        return "{" + ", ".join(
            [type.internal_type.visit(self, x) for x in value]
        ) + "}"


class CppTypePrinter(object):
    def __init__(self, module=""):
        self.current_module = module

    def visit_unknown(self):
        raise NotImplementedError()

    def print_value(self, value):
        return str(value) if not hasattr(value, "visit") else value.visit(self)

    def visit_line(self, line):
        return "{}".format(line.text)

    def visit_partbyte(self, type):
        return "codec::partbyte"

    def visit_uint8(self, type):
        return "std::uint8_t"

    def visit_int8(self, type):
        return "std::int8_t"

    def visit_uint16(self, type):
        return "std::uint16_t"

    def visit_int16(self, type):
        return "std::int16_t"

    def visit_uint32(self, type):
        return "std::uint32_t"

    def visit_int32(self, type):
        return "std::int32_t"

    def visit_array(self, type):
        return "std::array<{}, {}>".format(
            type.internal_type.visit(self),
            self.print_value(type.size)
        )

    def visit_pointer(self, type):
        return "{}*".format(
            type.internal_type.visit(self)
        )

    def visit_reference(self, type):
        if type.referred_module is not None and type.referred_module != self.current_module:
            return "{}::{}".format(
                type.referred_module,
                type.referred_name
            )
        else:
            return type.referred_name

    def visit_type_alias(self, type):
        return "using {} = {};\n".format(
            type.name,
            type.type.visit(self)
        )

    def visit_constant(self, type):
        return "constexpr {} {} = {};".format(
            type.type.visit(self),
            type.name,
            type.type.visit(CppValuePrinter(), type.value)
        )

    def visit_field(self, type):
        if type.value is None:
            definition = "{} {};".format(
                type.type.visit(self),
                type.name)
        else:
            definition = "{} {} = {};".format(
                type.type.visit(self),
                type.name,
                self.print_value(type.value))

        return definition + "\n"

    def get_constructor(self, type):
        def argument(field):
            return "{} {}_".format(field.type.visit(self), field.name)

        def assignment(field):
            return "{0}{{ {0}_ }}".format(field.name)

        definition =  tab() + "{}() = default;\n".format(type.name)
        non_default_fields = [x for x in type.values() if x.value is None]
        if len(non_default_fields) > 0:
            definition += tab() + "{}({}) :\n{}{}\n".format(
                type.name,
                ", ".join([argument(x) for x in non_default_fields]),
                tab(2),
                ", ".join([assignment(x) for x in non_default_fields])
            )
            definition += tab() + "{}\n"
        return definition

    def get_structure_coder(self, type):
        definition  = "inline std::uint8_t* encode(const {}& data, std::uint8_t* buffer)\n".format(type.name);
        definition += "{\n";
        for field in type.values():
            definition += tab() + "buffer = codec::encode_any(data.{}, buffer);\n".format(field.name)
        definition += tab() + "return buffer;\n";
        definition += "}\n";

        definition += "inline const std::uint8_t* decode({}& data, const std::uint8_t* buffer)\n".format(type.name);
        definition += "{\n";
        for field in type.values():
            definition += tab() + "buffer = codec::decode_any(data.{}, buffer);\n".format(field.name)
        definition += tab() + "return buffer;\n";
        definition += "}\n";

        definition += "inline std::uint8_t* encode_be(const {}& data, std::uint8_t* buffer)\n".format(type.name);
        definition += "{\n";
        for field in type.values():
            definition += tab() + "buffer = codec::encode_any_be(data.{}, buffer);\n".format(field.name)
        definition += tab() + "return buffer;\n";
        definition += "}\n";

        definition += "inline const std::uint8_t* decode_be({}& data, const std::uint8_t* buffer)\n".format(type.name);
        definition += "{\n";
        for field in type.values():
            definition += tab() + "buffer = codec::decode_any_be(data.{}, buffer);\n".format(field.name)
        definition += tab() + "return buffer;\n";
        definition += "}\n";
        return definition;

    def visit_structure(self, type):
        definition = "struct {}\n{{\n".format(type.name)
        for field in type.values():
            definition += "{}{}".format(tab(), field.visit(self))
        definition += "\n"
        definition += self.get_constructor(type)
        definition += "}} {};\n".format(" ".join([x.visit(self) for x in type.attributes]))
        definition += "\n"
        definition += self.get_structure_coder(type)
        return definition

    def visit_packed_attribute(self, attr):
        return ""

    def visit_line_comment(self, comment):
        return "// {}".format(comment.text)

    def visit_block_comment(self, comment):
        return "/* {} */".format(comment.text)

    def visit_module(self, module):
        content =  "namespace {}\n".format(module.name)
        content += "{\n"
        content += "\n".join([x.visit(CppTypePrinter(module.name)) for x in module.values()])
        content += "}\n"
        return content


class CppPrinter(printer.ProtocolPrinter):
    def __init__(self, protocol):
        super(CppPrinter, self).__init__(protocol)

    def _get_module_content(self, module):
        return self._print_header(module) + module.visit(CppTypePrinter()) + self._print_ending()

    def _get_module_file_format(self):
        return self.protocol.name + "_" + "{}.hpp"

    def _print_imports(self, imports):
        import_files = [self._get_module_file_format().format(x.name) for x in imports]
        return "\n".join(['#include "{}"'.format(x) for x in import_files])

    def _print_header(self, module):
        header =  "#pragma once\n\n"
        header += "#include <cstdint>\n"
        header += "#include <array>\n"
        header += "#include \"codec.hpp\"\n"
        header += self._print_imports(module.imports)
        header += "\n\n"
        header += "namespace {}\n".format(self.protocol.name)
        header += "{\n"
        return header

    def _print_ending(self):
        return "\n}\n"
