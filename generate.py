#!/usr/bin/env python
""" Usage: call with <filename>
"""

import sys
import re
import clang.cindex
from descriptor import FunctionDescriptor
from dispatcher import Dispatcher

# TODO: Avoid magic values

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

# TODO: Need to complete parameter names

dispatcher = Dispatcher()

dispatcher.register([\
   [[('LPCWSTR', 'lpApplicationName')], read_only_wo_len]
])

index = clang.cindex.Index.create()
tu = index.parse(sys.argv[1])
print 'Translation unit:', tu.spelling
#dump(0, tu.cursor)
for c in tu.cursor.get_children():
    if(c.type.kind.name == "FUNCTIONPROTO" and re.search('W$', c.spelling)):
        desc = FunctionDescriptor(c)
        dispatcher.dispatch(desc)
