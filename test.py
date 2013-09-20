#!/usr/bin/env python
""" Usage: call with <filename>
"""

import sys
import re
import clang.cindex

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
    result = "const " if type.is_const_qualified() else ""
    if type.kind.name == "TYPEDEF":
        result += type.get_declaration().spelling + '=(' + dump_type(type.get_declaration().underlying_typedef_type) + ')'
    else:
        result += type.kind.name
        if type.kind.name == "POINTER":
            result += " -> " + dump_type(type.get_pointee())
    return result

def dump_func(node):
    """
    """
    print '%s at %s' % (node.spelling, node.location.file)
    print dump_type(node.type.get_result())
    for at in node.type.argument_types():
        print dump_type(at)
    for p in node.get_children():
        if p.kind.name == 'PARM_DECL':
            print p.spelling

index = clang.cindex.Index.create()
tu = index.parse(sys.argv[1])
print 'Translation unit:', tu.spelling
#dump(0, tu.cursor)
for c in tu.cursor.get_children():
    if(c.type.kind.name == "FUNCTIONPROTO" and re.search('[AW]$', c.spelling)):
        dump_func(c)
