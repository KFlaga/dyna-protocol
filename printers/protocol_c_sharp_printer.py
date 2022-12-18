from . import protocol_types as types
from . import protocol_printer as printer


def tab(tabs=1):
    return " " * 4 * tabs


class CSharpValuePrinter(object):
    def visit_unknown(self, type, value, indent):
        raise NotImplementedError()

    def visit_partbyte(self, type, value, indent):
        if type.format == "hex":
            return "(byte)0x{:02x}u".format(value)
        return "(byte){}u".format(value)

    def visit_uint8(self, type, value, indent):
        if type.format == "hex":
            return "(byte)0x{:02x}u".format(value)
        return "(byte){}u".format(value)

    def visit_int8(self, type, value, indent):
        if type.format == "hex":
            return "(sbyte)0x{:02x}".format(value)
        return "(sbyte){}".format(value)

    def visit_uint16(self, type, value, indent):
        if type.format == "hex":
            return "(ushort)0x{:04x}u".format(value)
        return "(ushort){}u".format(value)

    def visit_int16(self, type, value, indent):
        if type.format == "hex":
            return "(short)0x{:04x}".format(value)
        return "(short){}".format(value)

    def visit_uint32(self, type, value, indent):
        if type.format == "hex":
            return "(uint)0x{:08x}u".format(value)
        return "(uint){}u".format(value)

    def visit_int32(self, type, value, indent):
        if type.format == "hex":
            return "(int)0x{:08x}".format(value)
        return "(int){}".format(value)

    def visit_array(self, type, value, indent):
        type_print = type.visit(CSharpTypePrinter())
        # for now we don't need pretty-print in C# from values
        # if type.format == "indent":
            # values_print = ",".join(["\n" + tab(indent + 1) + type.internal_type.visit(self, x, indent + 1) for x in value])
            # return "new " + type_print + " {" + values_print + "\n" + tab(indent) + "}"
        # else:
            # values_print = ", ".join([type.internal_type.visit(self, x, indent + 1) for x in value])
            # return "new " + type_print + " {" + values_print + "}"
        values_print = ", ".join([type.internal_type.visit(self, x, indent + 1) for x in value])
        return "new " + type_print + " {" + values_print + "}"


class CSharpMarshalAsPrinter(object):
    def __init__(self, type_printer):
        self.type_printer = type_printer

    def visit_array(self, type, indent):
        return "{}[MarshalAs(UnmanagedType.ByValArray, SizeConst={})]\n".format(
                tab(indent),
                self.type_printer.print_value(type.size)
            )


class CSharpTypePrinter(object):
    def __init__(self, module="", indent=0):
        self.current_module = module
        self.indent = 0

    def visit_unknown(self):
        raise NotImplementedError()

    def print_value(self, value):
        return str(value) if not hasattr(value, "visit") else value.visit(self)

    def visit_line(self, line):
        return "{}".format(line.text)

    def visit_partbyte(self, type):
        return "byte"

    def visit_uint8(self, type):
        return "byte"

    def visit_int8(self, type):
        return "sbyte"

    def visit_uint16(self, type):
        return "ushort"

    def visit_int16(self, type):
        return "short"

    def visit_uint32(self, type):
        return "uint"

    def visit_int32(self, type):
        return "int"

    def visit_array(self, type):
        return "{}[]".format(type.internal_type.visit(self))

    def visit_pointer(self, type):
        return "{}[]".format(type.internal_type.visit(self))

    def visit_reference(self, type):
        if type.referred_module is not None and type.referred_module != self.current_module:
            return "{}.{}".format(
                type.referred_module,
                type.referred_name
            )
        else:
            return type.referred_name

    def visit_type_alias(self, type):
        internal_name = type.type.visit(self)

        definition =  "{}public struct {}\n".format(tab(self.indent), type.name)
        definition += "{\n"
        marshal_as = type.type.visit(CSharpMarshalAsPrinter(self), self.indent)
        if marshal_as is not None:
            definition += tab(self.indent + 1) + marshal_as
        definition += tab(self.indent + 1) + "public {} Value;\n".format(internal_name)
        definition += tab(self.indent + 1) + "public static implicit operator {0}({1} v) => new {0}() {{ Value = v }};\n" \
            .format(type.name, internal_name)
        definition += "}\n"
        
        return definition

    def visit_constant(self, type):
        is_array = hasattr(type.type, "size")
        modifier = "static readonly" if is_array else "const"
        return "{}public {} {} {} = {};".format(
            tab(self.indent),
            modifier,
            type.type.visit(self),
            type.name,
            type.type.visit(CSharpValuePrinter(), type.value, self.indent)
        )

    def visit_typedef(self, type):
        # C# type aliases are only visible in file-scope, so typedef is not very useful.
        # If typedef is used Reference, full type will be printed
        return ""

    class PrintFieldsStorage():
        def __init__(self, parent):
            self.parent = parent
    
        def visit_field(self, field, indent):
            definition = "{}public {} {};\n".format(
                tab(indent),
                field.type.visit(self.parent),
                field.name
            )
            marshal_as = field.type.visit(CSharpMarshalAsPrinter(self.parent), indent)
            if marshal_as is not None:
                definition = marshal_as + definition
            return definition

    class PrintFieldArgument():
        def __init__(self, parent):
            self.parent = parent
    
        def visit_field(self, field, indent):
            return "{} {}_".format(field.type.visit(self.parent), field.name)

    class PrintFieldValue():
        def __init__(self, parent):
            self.parent = parent
    
        def visit_field(self, field):
            if field.value is None:
                return "this.{0} = {0}_;".format(field.name)
            else:
                return "this.{0} = {1};".format(field.name, self.parent.print_value(field.value))

    def visit_structure(self, type):
        # attributes
        definition =  "".join([x.visit(self) + "\n" for x in type.attributes])
        definition += "public struct {}\n".format(type.name)
        definition += "{\n"
        # fields
        for field in type.values():
            definition += field.visit(CSharpTypePrinter.PrintFieldsStorage(self), self.indent + 1)
        definition += "\n"
        # ctor
        definition += "{}public {}({})\n".format(tab(), type.name, ", ".join( \
            [x.visit(CSharpTypePrinter.PrintFieldArgument(self), self.indent + 1) for x in type.values() if x.value is None])) # ctor arguments -> all without explicit value
        definition += tab() + "{\n"
        definition += "".join(["{}{}\n".format(tab(self.indent + 2), x.visit(CSharpTypePrinter.PrintFieldValue(self))) for x in type.values()]) # ctor body -> assign all fields
        definition += tab() + "}\n"
        definition += "}\n"
        return definition

    def visit_packed_attribute(self, attr):
        return tab(self.indent) + "[StructLayout(LayoutKind.Sequential, Pack=1)]"

    def visit_line_comment(self, comment):
        return tab(self.indent) +  "// {}".format(comment.text)

    def visit_block_comment(self, comment):
        return tab(self.indent) +  "/* {} */".format(comment.text)

    def visit_module(self, module):
        content =  "internal static class {}\n".format(module.name)
        content += "{"
        content += "\n".join([x.visit(CSharpTypePrinter(module.name, 0)) for x in module.values()])
        content += "\n}"
        return content


class CSharpPrinter(printer.ProtocolPrinter):
    def __init__(self, protocol):
        super(CSharpPrinter, self).__init__(protocol)

    def _get_module_content(self, module):
        return self._print_header() + module.visit(CSharpTypePrinter()) + self._print_ending()

    def _get_module_file_format(self):
        return self.protocol.name + "_" + "{}.cs"

    def _print_header(self):
        header =  "using System;\n"
        header += "using System.Runtime.InteropServices;\n"
        header += "\n\n"
        header += "namespace {}\n".format(self.protocol.name)
        header += "{\n"
        return header

    def _print_ending(self):
        return "\n}\n"
