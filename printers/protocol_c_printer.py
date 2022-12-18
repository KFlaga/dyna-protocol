from . import protocol_types as types
from . import protocol_printer as printer


def tab(tabs=1):
    return " " * 4 * tabs


class CValuePrinter(object):
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
        return "{" + ", ".join([type.internal_type.visit(self, x) for x in value]) + "}"


class CTypePrinter(object):
    def __init__(self, module=""):
        self.current_module = module

    def add_module(self, name):
        return "{}_{}".format(self.current_module, name)

    def visit_unknown(self):
        raise NotImplementedError()

    def print_value(self, size):
        return size if not hasattr(size, "visit") else size.visit(self)

    def visit_line(self, line):
        return "{}".format(line.text)

    def visit_partbyte(self, type):
        return "uint8_t"

    def visit_uint8(self, type):
        return "uint8_t"

    def visit_int8(self, type):
        return "int8_t"

    def visit_uint16(self, type):
        return "uint16_t"

    def visit_int16(self, type):
        return "int16_t"

    def visit_uint32(self, type):
        return "uint32_t"

    def visit_int32(self, type):
        return "int32_t"

    def visit_array(self, type):
        return "{}[{}]".format(
            type.internal_type.visit(self),
            self.print_value(type.size)
        )

    def visit_pointer(self, type):
        return "{}*".format(
            type.internal_type.visit(self)
        )

    def visit_reference(self, type):
        if type.referred_module is not None:
            return "{}_{}".format(
                type.referred_module,
                type.referred_name
            )
        else:
            return type.referred_name

    def visit_type_alias(self, type):
        if isinstance(type.type, types.Array):
            array = type.type
            return "typedef {} {}[{}];\n".format(
                array.internal_type.visit(self),
                self.add_module(type.name),
                self.print_value(array.size)
            )
        else:
            return "typedef {} {};\n".format(
                type.type.visit(self),
                self.add_module(type.name)
            )

    def visit_constant(self, type):
        if type.type is types.Array:
            return "#define {} {}".format(
                self.add_module(type.name),
                type.type.visit(CValuePrinter(), type.value)
            )
        else:
            return "#define {} ({}){}".format(
                self.add_module(type.name),
                type.type.visit(self),
                type.type.visit(CValuePrinter(), type.value)
            )

    def visit_field(self, type):
        definition = "{} {};".format(type.type.visit(self), type.name)
        if type.value is not None:
            definition += types.LineComment(
                "Must be: {}".format(self.print_value(type.value))
            ).visit(self)

        return definition + "\n"

    def visit_structure(self, type):
        definition = "typedef struct {}\n{{\n".format(
            " ".join([x.visit(self) for x in type.attributes]))
        for field in type.values():
            definition += "{}{}".format(tab(), field.visit(self))

        definition += "}} {};\n".format(self.add_module(type.name))
        return definition

    def visit_packed_attribute(self, attr):
        return "PACKED"

    def visit_line_comment(self, comment):
        return "// {}".format(comment.text)

    def visit_block_comment(self, comment):
        return "/* {} */".format(comment.text)

    def visit_module(self, module):
        return "\n".join([x.visit(CTypePrinter(module.name)) for x in module.values()])


class CPrinter(printer.ProtocolPrinter):
    def __init__(self, protocol):
        super(CPrinter, self).__init__(protocol)

    def _get_module_content(self, module):
        return self._print_header(module) + module.visit(CTypePrinter())

    def _get_module_file_format(self):
        return self.protocol.name + "_" + "{}.h"

    def _print_imports(self, imports):
        import_files = [self._get_module_file_format().format(x.name) for x in imports]
        return "\n".join(['#include "{}"'.format(x) for x in import_files])

    def _print_header(self, module):
        header =  "#pragma once\n\n"
        header += "#include <stdint.h>\n"
        header += "#include <stddef.h>\n"
        header += self._print_imports(module.imports)
        header += "\n"
        header += "#ifndef PACKED\n"
        header += "#define PACKED __attribute__ ((__packed__))\n"
        header += "#endif\n\n"
        return header
