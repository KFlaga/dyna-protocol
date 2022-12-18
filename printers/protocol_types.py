from collections import OrderedDict


def visitable(type_name):
    visit_func_name = "visit_{}".format(type_name)
    def visit_func(self, visitor, *args, **kwargs):
        if hasattr(visitor, visit_func_name):
            return getattr(visitor, visit_func_name)(self, *args, **kwargs)
        else:
            return None

    def impl(cls):
        cls.visit = visit_func
        return cls
    return impl


@visitable("unknown")
class Type(object):
    is_type = True


@visitable("unknown")
class Object(object):
    is_object = True


@visitable("unknown")
class Attribute(object):
    is_attribute = True


@visitable("packed_attribute")
class PackedAttribute(Attribute):
    pass


@visitable("partbyte")
class partbyte(Type):
    def __init__(self, format="dec"):
        self.format = format


@visitable("uint8")
class uint8(Type):
    def __init__(self, format="dec"):
        self.format = format


@visitable("int8")
class int8(Type):
    def __init__(self, format="dec"):
        self.format = format


@visitable("uint16")
class uint16(Type):
    def __init__(self, format="dec"):
        self.format = format


@visitable("int16")
class int16(Type):
    def __init__(self, format="dec"):
        self.format = format


@visitable("uint32")
class uint32(Type):
    def __init__(self, format="dec"):
        self.format = format


@visitable("int32")
class int32(Type):
    def __init__(self, format="dec"):
        self.format = format


@visitable("array")
class Array(Type):
    def __init__(self, internal_type, size, format="no-indent"):
        self.internal_type = internal_type
        self.size = size
        self.format = format


@visitable("pointer")
class Pointer(Type):
    def __init__(self, internal_type):
        self.internal_type = internal_type


@visitable("reference")
class Reference(Object, Type):
    def __init__(self, referred_name, referred_module=None):
        self.referred_name = referred_name
        if referred_module is None:
            self.referred_module = None
        else:
            self.referred_module = referred_module.name


class Parameterized(Type):
    def __init__(self, initializer):
        self.initializer = initializer

    def __call__(self, **kwargs):
        return self.initializer(kwargs)


@visitable("type_alias")
class TypeAlias(Object):
    def __init__(self, type):
        self.type = type
        self.name = ""


@visitable("field")
class Field(Type):
    is_field = True

    def __init__(self, name, type, fixed_value = None):
        self.name = name
        self.type = type
        self.value = fixed_value


@visitable("structure")
class Structure(Object, OrderedDict):
    def __init__(self, fields=None, attributes=None):
        super(Structure, self).__init__()
        self.attributes = []
        if attributes is not None:
            for x in attributes:
                assert hasattr(x, "is_attribute")
                self.attributes.append(x)

        if fields is not None:
            for x in fields:
                assert hasattr(x, "is_field")
                self.__setitem__(x.name, x)

    def __setitem__(self, key, value):
        assert hasattr(value, "is_type")
        assert isinstance(key, str)

        if not hasattr(value, "is_field"):
            value = Field(key, value)
        value.name = key
        OrderedDict.__setitem__(self, key, value)


@visitable("constant")
class Constant(Object):
    def __init__(self, value, type):
        self.value = value
        self.type = type
        self.name = ""


@visitable("line_comment")
class LineComment(Object):
    def __init__(self, text):
        self.text = text


@visitable("block_comment")
class BlockComment(Object):
    def __init__(self, text):
        self.text = text


@visitable("line")
class Line(Object):
    def __init__(self, text=""):
        self.text = text


@visitable("module")
class Module(OrderedDict):
    def __init__(self, name):
        super(Module, self).__init__()
        self.name = name
        self.imports = []
        self.__unique_counter = 0

    def __internal_name(self):
        self.__unique_counter += 1
        return "__internal__" + str(self.__unique_counter)

    def __setitem__(self, key, value):
        assert value.is_object is True
        assert isinstance(key, str)

        if key == "":
            key = self.__internal_name()

        value.name = key
        OrderedDict.__setitem__(self, key, value)

    def add(self, element, name=""):
        if name == "":
            name = self.__internal_name()
        self.__setitem__(name, element)

    def add_import(self, module):
        assert isinstance(module, Module)
        self.imports.append(module)


class Protocol(object):
    def __init__(self, name, modules = None):
        self.name = name
        self.modules = modules if modules is not None else []

    def add_module(self, module):
        assert isinstance(module, Module)
        self.modules.append(module)
