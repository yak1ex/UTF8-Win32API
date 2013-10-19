"""Descriptors for clang.cindex"""

def dump(level, node):
    """ 
    """
    print '%s%s %s %s %s' % (" " * level, node.spelling, node.kind.name, ("const " if node.type.is_const_qualified() else "") + node.type.kind.name, "-> " + (("const " if node.type.get_pointee().is_const_qualified() else "") + node.type.get_pointee().kind.name) if node.type.kind.name == "POINTER" else "")
    # Recurse for children of this node
    for c in node.get_children():
        dump(level + 1, c)

def dump_type(type):
    """
    """
    if type.kind.name == "TYPEDEF":
#       result = type.get_declaration().spelling + '=(' + dump_type(type.get_declaration().underlying_typedef_type) + ')'
        result = type.get_declaration().spelling
    else:
        if type.kind.name == "POINTER":
            result = dump_type(type.get_pointee()) + " *"
        else:
            result = type.kind.name.lower()
    result += " const" if type.is_const_qualified() else ""
    result += " volatile" if type.is_volatile_qualified() else ""
    return result

class FunctionDescriptor(object):
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

    def dump_func(self):
        """
        """
        print '%s %s(%s) at %s' % (self._result_type, self._name, ', '.join([t + ' ' + n for t, n in self._parameter_types]), self._file)

    def make_func_decl(self):
        """
        """
        return '%s %s(%s)' % (self._result_type, self._name, ', '.join([t + ' ' + n for t, n in self._parameter_types]))

    def make_func_call(self):
        """
        """
        return '%s(%s)' % (self._name, ', '.join([n for t, n in self._parameter_types]))

    def index_arg(self, spec):
        """search argument corresponding to the specified spec"""
        for i,v in enumerate(self._parameter_types):
            if v == spec:
                return i
            elif v[0] == spec[0] and spec[1] == None:
                return i
            elif v[1] == spec[1] and spec[0] == None:
                return i
        return -1

    def clone(self):
        cloned = FunctionDescriptor()
        cloned._name = self._name
        cloned._file = self._file
        cloned._result_type = self._result_type
        cloned._parameter_types = self._parameter_types[:]
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

