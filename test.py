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

index = clang.cindex.Index.create()
tu = index.parse(sys.argv[1])
print 'Translation unit:', tu.spelling
#dump(0, tu.cursor)
for c in tu.cursor.get_children():
    if(c.type.kind.name == "FUNCTIONPROTO" and re.search('W$', c.spelling)):
        desc = make_func_desc(c)
        dump_func(desc)
