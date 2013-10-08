#!/usr/bin/env python
""" Usage: call with <filename>
"""

import sys
import re
import clang.cindex
from descriptor import FunctionDescriptor
from dispatcher import Dispatcher

def read_only_wo_len_imp(suffix, desc_self, desc_call, code, typespec):
    """
    """
    target_index = desc.index_arg(typespec)
    orig_type, orig_name = desc.parameter_types[target_index]
    desc_self.parameter_types[target_index] = ('LPCSTR', orig_name)
    desc_call.parameter_types[target_index] = (orig_type, orig_name + '_')
    code += "\tWSTR %s(%s);\n" % (orig_name + '_', orig_name)
    return (suffix, desc_self, desc_call, code)

def read_only_wo_len_idx(idx):
    return lambda desc, typespecs: reduce( \
        lambda acc, x: read_only_wo_len_imp(acc[0], acc[1], acc[2], acc[3], x), \
        map(lambda x: typespecs[x], idx), \
        ('W', desc.clone(), desc.clone(), '') \
    )

def read_only_wo_len_all(desc, typespecs):
    return reduce( \
        lambda acc, x: read_only_wo_len_imp(acc[0], acc[1], acc[2], acc[3], x), \
        typespecs, \
        ('W', desc.clone(), desc.clone(), '') \
    )

def read_only_wo_len(desc, typespecs):
    return read_only_wo_len_imp('W', desc.clone(), desc.clone(), '', typespecs[0]) # for the first type spec

def forwardA_all(desc, typespecs):
    desc_self = desc.clone()
    desc_self.parameter_types = map(lambda x: ('LPSTR', x[1]) if x[0] == 'LPWSTR' else x, desc_self.parameter_types)
    return ('A', desc_self, desc.clone(), '')

# TODO: Need to complete parameter names

dispatcher = Dispatcher()

dispatcher.register([\
    ['BinaryType', [('LPCWSTR', 'lpApplicationName')], read_only_wo_len],
    ['lstrcmp', [('LPCWSTR', 'lpString1'), ('LPCWSTR', 'lpString2')], read_only_wo_len_all],
    ['GetLogicalDriveStrings', [('DWORD', 'nBufferLength'), ('LPWSTR', 'lpBuffer')], forwardA_all],

    ['', [('LPCWSTR', 'lpPathName')], read_only_wo_len_all],
    ['', [('LPCWSTR', 'lpLibFileName')], read_only_wo_len_all],
])

index = clang.cindex.Index.create()
tu = index.parse(sys.argv[1])
print 'Translation unit:', tu.spelling
#dump(0, tu.cursor)
for c in tu.cursor.get_children():
    if(c.type.kind.name == "FUNCTIONPROTO" and re.search('W$', c.spelling)):
        desc = FunctionDescriptor(c)
        dispatcher.dispatch(desc)
