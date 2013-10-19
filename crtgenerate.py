#!/usr/bin/env python
""" Usage: call with <filename>
"""

import sys
import re
import clang.cindex
from descriptor import dump, FunctionDescriptor
from dispatcher import CRTDispatcher
from converter import *

# NOTE: wchar_t is treated as int for libclang

spec = { \
    'io.h': [ \
        [('_uaccess', '_waccess', ['_access'], []), [('int const *', '_Filename')], read_only_wo_len],
    ],
}

for file, filespec in spec.iteritems():

    dispatcher = CRTDispatcher()
    dispatcher.register(filespec)

    index = clang.cindex.Index.create()
    tu = index.parse(sys.argv[1] + '/' + file)
    print 'Translation unit:', tu.spelling
    for c in tu.cursor.get_children():
        #dump(0, c)
        if(c.type.kind.name == "FUNCTIONPROTO" and re.search('_w', c.spelling)):
            desc = FunctionDescriptor(c)
            dispatcher.dispatch(desc)
