#!/usr/bin/env python
""" Usage: call with <filename>
"""

import sys
import re
import clang.cindex
import os.path

# TODO: Avoid magic values


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
            result = type.kind.name
    result += " const" if type.is_const_qualified() else ""
    result += " volatile" if type.is_volatile_qualified() else ""
    return result

class FunctionDescriptor(object):
    def __init__(self, node = None):
        """Create function descriptor from libclang node"""
        if node is None:
            return
        plist = zip([dump_type(at) for at in node.type.argument_types()], [p.spelling for p in node.get_children() if p.kind.name == 'PARM_DECL'])
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

def read_only_wo_len(desc, spec):
    """
    """
    target_index = desc.index_arg(spec[0])
    orig_type, orig_name = desc.parameter_types[target_index]
    desc_self = desc.clone()
    desc_self.parameter_types[target_index] = ('LPCSTR', orig_name)
    desc_call = desc.clone()
    desc_call.parameter_types[target_index] = (orig_type, orig_name + '_')
    code = "WSTR %s(%s);\n" % (orig_name + '_', orig_name)
    return (desc_self, desc_call, code)

spec = [
           [[('LPCWSTR', 'lpApplicationName')], read_only_wo_len]
       ]

# TODO: Need to complete parameter names

def cpp_name(outname):
    return outname.replace('.h', 'u.cpp')

def h_name(outname):
    return outname.replace('.h', 'u.h')

def txt_name(outname):
    return outname.replace('.h', 'u.txt')

cpp_status = {}
h_status = {}

def cpp_header(outname):
    actualname = cpp_name(outname)
    if actualname in cpp_status:
        return
    cpp_status[actualname] = 1
    with open(actualname, 'a') as f:
        f.write("#include \"" + h_name(outname) + "\"\n")
        f.write("#include \"win32u_helper.hpp\"\n")

def h_header(outname):
    actualname = h_name(outname)
    if actualname in h_status:
        return
    h_status[actualname] = 1
    guard_name = actualname.upper().replace('.', '_')
    with open(actualname, 'a') as f:
        f.write("#ifndef " + guard_name + "\n")
        f.write("#define " + guard_name + "\n\n")
        f.write("#include <windows.h>\n\n")
        f.write("#ifndef __cplusplus\nexnter \"C\" {\n#endif\n\n")

index = clang.cindex.Index.create()
tu = index.parse(sys.argv[1])
print 'Translation unit:', tu.spelling
#dump(0, tu.cursor)
for c in tu.cursor.get_children():
    if(c.type.kind.name == "FUNCTIONPROTO" and re.search('W$', c.spelling)):
        desc = FunctionDescriptor(c)
        processed = False
        for onespec in spec:
            flag = True
            for argspec in onespec[0]:
                if desc.index_arg(argspec) == -1:
                    flag = False
                    break
            if(flag):
                processed = True
                outname = os.path.basename("%s" % desc.file)
                (desc_self, desc_call, code) = onespec[1](desc, onespec[0])
                desc_self.name = desc_self.name[:-1] + 'U'
                cpp_header(outname)
                with open(cpp_name(outname), 'a') as f:
                    f.write(desc_self.make_func_decl() + "\n{\n")
                    f.write("\t" + code)
                    f.write("\treturn " + desc_call.make_func_call() + ";\n}\n")
                h_header(outname)
                with open(h_name(outname), 'a') as f:
                    f.write("extern " + desc_self.make_func_decl() + ";\n")
                break
        if not processed:
            outname = os.path.basename("%s" % desc.file)
            with open(txt_name(outname), 'a') as f:
                f.write(desc.make_func_decl() + "\n")

for actualname in h_status:
    with open(actualname, 'a') as f:
        f.write("\n#ifndef __cplusplus\n};\n#endif\n\n#endif\n")
