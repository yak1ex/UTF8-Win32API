#!/usr/bin/env python
""" Usage: call with <filename>
"""

import sys
import re
import clang.cindex
from descriptor import FunctionDescriptor
from dispatcher import Dispatcher
from converter import *

# TODO: Need to complete parameter names

dispatcher = Dispatcher()

dispatcher.register([\
    ['BinaryType', [('LPCWSTR', 'lpApplicationName')], read_only_wo_len],
    ['lstrcmp', [('LPCWSTR', 'lpString1'), ('LPCWSTR', 'lpString2')], read_only_wo_len_all],
    ['GetLogicalDriveStrings', [('DWORD', 'nBufferLength'), ('LPWSTR', 'lpBuffer')], forwardA_all],
    ['', [('LPCWSTR', 'lpPathName'), ('LPCWSTR', 'lpPrefixString'), ('LPWSTR', 'lpTempFileName')], [read_only_wo_len_idx([0,1]), write_only_wo_len_idx(2)]],

    ['', [('LPCWSTR', 'lpPathName')], read_only_wo_len_all],
    ['', [('LPCWSTR', 'lpLibFileName')], read_only_wo_len_all],
    ['', [('LPCWSTR', 'lpExistingFileName'), ('LPCWSTR', 'lpNewFileName')], read_only_wo_len_all],
])

index = clang.cindex.Index.create()
tu = index.parse(sys.argv[1])
print 'Translation unit:', tu.spelling
#dump(0, tu.cursor)
for c in tu.cursor.get_children():
    if(c.type.kind.name == "FUNCTIONPROTO" and re.search('W$', c.spelling)):
        desc = FunctionDescriptor(c)
        dispatcher.dispatch(desc)
