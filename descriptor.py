"""Descriptors for clang.cindex"""

def dump(level, node):
    """ 
    """
    print '%s%s %s %s %s' % (" " * level, node.spelling, node.kind.name, ("const " if node.type.is_const_qualified() else "") + node.type.kind.name, "-> " + (("const " if node.type.get_pointee().is_const_qualified() else "") + node.type.get_pointee().kind.name) if node.type.kind.name == "POINTER" else "")
    # Recurse for children of this node
    for c in node.get_children():
        dump(level + 1, c)

# TODO: Handle CONSTANTARRAY, necesary to use element_type, element_count
def dump_type(type):
    """
    """
    if type.kind.name == "TYPEDEF":
#       result = '%s=(%s)' % (type.get_declaration().spelling, dump_type(type.get_declaration().underlying_typedef_type))
        result = type.get_declaration().spelling
    else:
        if type.kind.name == "POINTER":
            result = dump_type(type.get_pointee()) + " *"
        elif type.kind.name == "UNEXPOSED":
            result = ("struct " if type.get_declaration().kind.name == "STRUCT_DECL" else "") + \
                     (type.get_declaration().spelling if type.get_declaration().spelling is not None else '__UNKNOWN__')
        elif type.kind.name == "CHAR_S":
            result = 'char'
        else:
            result = type.kind.name.lower()
    result += " const" if type.is_const_qualified() else ""
    result += " volatile" if type.is_volatile_qualified() else ""
    return result

class FunctionDescriptor(object):
    @staticmethod
    def is_target(node):
        return node.type.kind.name == "FUNCTIONPROTO"

    def __init__(self, node = None):
        """Create function descriptor from libclang node"""
        if node is None:
            return
        plist = zip( \
            [dump_type(at) for at in node.type.argument_types()], \
            [val if val != '' else 'arg' + str(idx + 1) for idx, val in enumerate([p.spelling for p in node.get_children() if p.kind.name == 'PARM_DECL'])] \
        )
        self._name = node.spelling
        self._file = node.location.file
        self._result_type = dump_type(node.type.get_result())
        self._parameter_types = plist
        self._is_variadic = node.type.is_function_variadic()

    def dump_func(self):
        """
        """
        print '%s %s(%s) at %s' % (self._result_type, self._name, ', '.join(['%s %s' % (t, n) for t, n in self._parameter_types]), self._file)

    def make_func_decl(self):
        """
        """
        return '%s %s(%s)' % (self._result_type, self._name, ', '.join(['%s %s' % (t, n) for t, n in self._parameter_types]) + (', ...' if self._is_variadic else ''))

    def make_func_call(self):
        """
        """
        assert not self._is_variadic
        return '%s(%s)' % (self._name, ', '.join([n for t, n in self._parameter_types]))

    def make_trace_arg(self):
        """
        """
        return ' << '.join(['" %s: " << win32u::dwrap(%s)' % (n, n) for t, n in self._parameter_types])

    def index_arg(self, spec):
        """search argument corresponding to the specified spec, returning its index"""
        for i,v in enumerate(self._parameter_types):
            if v[0] == spec[0] and v[1].rstrip('_') == spec[1].rstrip('_'):
                return i
            elif v[0] == spec[0] and spec[1] == None:
                return i
            elif v[1].rstrip('_') == spec[1].rstrip('_') and spec[0] == None:
                return i
        return -1

    def get_param(self, spec):
        """search argument corresponding to the specified spec, returning its type and value"""
        for v in self._parameter_types:
            if v[0] == spec[0] and v[1].rstrip('_') == spec[1].rstrip('_'):
                return v
            elif v[0] == spec[0] and spec[1] == None:
                return v
            elif v[1].rstrip('_') == spec[1].rstrip('_') and spec[0] == None:
                return v
        raise KeyError('The specified typespec is not found')

    def clone(self):
        cloned = FunctionDescriptor()
        cloned._name = self._name
        cloned._file = self._file
        cloned._result_type = self._result_type
        cloned._parameter_types = self._parameter_types[:]
        cloned._is_variadic = self._is_variadic
        return cloned

    def _get_name(self):
        return self._name
    def _set_name(self, name):
        self._name = name
    name = property(_get_name, _set_name)

    def _get_file(self):
        return self._file
    def _set_file(self, file):
        self._file = file
    file = property(_get_file, _set_file)

    def _get_result_type(self):
        return self._result_type
    def _set_result_type(self, result_type):
        self._result_type = result_type
    result_type = property(_get_result_type, _set_result_type)

    def _get_parameter_types(self):
        return self._parameter_types
    def _set_parameter_types(self, parameter_types):
        self._parameter_types = parameter_types
    parameter_types = property(_get_parameter_types, _set_parameter_types)

    def _get_is_variadic(self):
        return self._is_variadic
    def _set_is_variadic(self, is_variadic):
        self._is_variadic = is_variadic
    is_variadic = property(_get_is_variadic, _set_is_variadic)

class StructDescriptor(object):
    @staticmethod
    def is_target(node):
        return (node.kind.name == 'TYPEDEF_DECL' and
                node.underlying_typedef_type.kind.name == 'UNEXPOSED' and
                node.underlying_typedef_type.get_declaration().kind.name == 'STRUCT_DECL')

    def __init__(self, node = None):
        """Create struct descriptor from libclang node"""
        if node is None:
            return
        decl = node.underlying_typedef_type.get_declaration()
        self._name = node.spelling
        self._file = node.location.file
        self._fields = [(dump_type(p.type),p.spelling) for p in decl.get_children() if p.kind.name == 'FIELD_DECL']

    def _get_name(self):
        return self._name
    def _set_name(self, name):
        self._name = name
    name = property(_get_name, _set_name)

    def _get_file(self):
        return self._file
    def _set_file(self, file):
        self._file = file
    file = property(_get_file, _set_file)

    def _get_fields(self):
        return self._fields
    def _set_fields(self, fields):
        self._fields = fields
    fields = property(_get_fields, _set_fields)
