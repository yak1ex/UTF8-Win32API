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

def make_func_desc(node):
    """
    """
    plist = zip([dump_type(at) for at in node.type.argument_types()], [p.spelling for p in node.get_children() if p.kind.name == 'PARM_DECL'])
    return (node.spelling, node.location.file, dump_type(node.type.get_result()), plist)

def dump_func(desc):
    """
    """
    print '%s %s(%s) at %s' % (desc[2], desc[0], ', '.join([t + ' ' + n for t, n in desc[3]]), desc[1])

def make_func_decl(desc):
    """
    """
    return '%s %s(%s)' % (desc[2], desc[0], ', '.join([t + ' ' + n for t, n in desc[3]]))

def make_func_call(desc):
    """
    """
    return '%s(%s)' % (desc[0], ', '.join([n for t, n in desc[3]]))

def index_arg(desc, spec):
    """
    """
    for i,v in enumerate(desc[3]):
        if v == spec:
            return i
        elif v[0] == spec[0] and spec[1] == None:
            return i
        elif v[1] == spec[1] and spec[0] == None:
            return i
    return -1

def read_only_wo_len(desc, spec):
    """
    """
    target_index = index_arg(desc, spec[0])
    orig = desc[3][target_index][1]
    desc_self = (desc[0], desc[1], desc[2], desc[3][:])
    desc_self[3][target_index] = ('LPCSTR', orig)
    desc_call = (desc[0], desc[1], desc[2], desc[3][:])
    desc_call[3][target_index] = (desc[3][target_index][0], orig + '_')
    code = "WSTR %s(%s);\n" % (orig + '_', orig)
    return (desc_self, desc_call, code)

spec = [
           [[('LPCWSTR', 'lpApplicationName')], read_only_wo_len]
       ]

# TODO: Need to complete parameter names

cpp_status = {}
h_status = {}

def cpp_header(outname):
    actualname = outname + '.cpp'
    if actualname in cpp_status:
        return
    cpp_status[actualname] = 1
    with open(actualname, 'a') as f:
        f.write("#include \"" + outname + ".h\"\n")
        f.write("#include \"win32u.hpp\"\n")

def h_header(outname):
    actualname = outname + '.h'
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
        desc = make_func_desc(c)
        processed = False
        for onespec in spec:
            flag = True
            for argspec in onespec[0]:
                if index_arg(desc, argspec) == -1:
                    flag = False
                    break
            if(flag):
                processed = True
                outname = os.path.basename("%s" % desc[1])
                (desc_self, desc_call, code) = onespec[1](desc, onespec[0])
                desc_self = (desc_self[0][:-1] + 'U', desc_self[1], desc_self[2], desc_self[3])
                cpp_header(outname)
                with open(outname + '.cpp', 'a') as f:
                    f.write(make_func_decl(desc_self) + "\n{\n")
                    f.write("\t" + code)
                    f.write("\treturn " + make_func_call(desc_call) + ";\n}\n")
                h_header(outname)
                with open(outname + '.h', 'a') as f:
                    f.write("extern " + make_func_decl(desc_self) + ";\n")
                break
        if not processed:
            outname = os.path.basename("%s" % desc[1])
            with open(outname + '.txt', 'a') as f:
                f.write(make_func_decl(desc) + "\n")

for actualname in h_status:
    with open(actualname, 'a') as f:
        f.write("\n#ifndef __cplusplus\n};\n#endif\n\n#endif\n")
