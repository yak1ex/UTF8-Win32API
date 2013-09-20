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

def dump_func(node):
    """
    """
    print '%s at %s' % (node.spelling, node.location.file)

index = clang.cindex.Index.create()
tu = index.parse(sys.argv[1])
print 'Translation unit:', tu.spelling
#dump(0, tu.cursor)
for c in tu.cursor.get_children():
    if(c.type.kind.name == "FUNCTIONPROTO" and re.search('[AW]$', c.spelling)):
        dump_func(c)
