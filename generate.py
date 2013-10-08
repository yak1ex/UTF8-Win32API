#!/usr/bin/env python
""" Usage: call with <filename>
"""

import sys
import re
import clang.cindex
from descriptor import FunctionDescriptor
from dispatcher import Dispatcher

def read_only_wo_len_imp(desc_self, desc_call, code, spec):
    """
    """
    target_index = desc.index_arg(spec[0]) # The first entry
    orig_type, orig_name = desc.parameter_types[target_index]
    desc_self.parameter_types[target_index] = ('LPCSTR', orig_name)
    desc_call.parameter_types[target_index] = (orig_type, orig_name + '_')
    code += "WSTR %s(%s);\n" % (orig_name + '_', orig_name)
    return (desc_self, desc_call, code)

def read_only_wo_len(desc, spec):
    return read_only_wo_len_imp(desc.clone(), desc.clone(), '', spec)

# TODO: Need to complete parameter names

dispatcher = Dispatcher()

dispatcher.register([\
   ['BinaryType', [('LPCWSTR', 'lpApplicationName')], read_only_wo_len]
])

index = clang.cindex.Index.create()
tu = index.parse(sys.argv[1])
print 'Translation unit:', tu.spelling
#dump(0, tu.cursor)
for c in tu.cursor.get_children():
    if(c.type.kind.name == "FUNCTIONPROTO" and re.search('W$', c.spelling)):
        desc = FunctionDescriptor(c)
        dispatcher.dispatch(desc)
