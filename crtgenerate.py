#!/usr/bin/env python
""" Usage: call with <filename>
"""

import sys
import re
import clang.cindex
from descriptor import dump, FunctionDescriptor
from dispatcher import CRTDispatcher
from converter import *

spec = [ \

# stdio.h
    [('_ufsopen', '_wfsopen', ['_fsopen'], ['_tfsopen']), [('wchar_t const *', '_Filename'), ('wchar_t const *', '_Mode')], read_only_wo_len],
        [('_ufopen', '_wfopen', ['fopen'], ['_tfopen']), [('wchar_t const *', '_Filename'), ('wchar_t const *', '_Mode')], read_only_wo_len],
    [('_ufreopen', '_wfreopen', ['freopen'], ['_tfreopen']), [('wchar_t const *', '_Filename'), ('wchar_t const *', '_Mode')], read_only_wo_len],
    [('_upopen', '_wpopen', ['_popen'], ['_tpopen']), [('wchar_t const *', '_Command'), ('wchar_t const *', '_Mode')], read_only_wo_len],
    [('_uremove', '_wremove', ['remove'], ['_tremove']), [('wchar_t const *', '_Filename')], read_only_wo_len],
    [('_utmpnam', '_wtmpnam', ['tmpnam'], ['_ttmpnam']), [('wchar_t *', '_Buffer')], write_only_wo_len_ret_null_static('MAX_PATH', 0)],
    [('_utempnam', '_wtempnam', ['_tempnam'], ['_ttempnam']), [('wchar_t const *', '_Directory'), ('wchar_t const *', '_FilePrefix')], [read_only_wo_len_all, ret_alloc]],

# direct.h
    [('_uchdir', '_wchdir', ['_chdir'], ['_tchdir']), [('wchar_t const *', '_Path')], read_only_wo_len],
    [('_umkdir', '_wmkdir', ['_mkdir'], ['_tmkdir']), [('wchar_t const *', '_Path')], read_only_wo_len],
    [('_urmdir', '_wrmdir', ['_rmdir'], ['_trmdir']), [('wchar_t const *', '_Path')], read_only_wo_len],
    [('_ugetcwd', '_wgetcwd', ['_getcwd'], ['_tgetcwd']), [('wchar_t *', '_DstBuf'), ('int', '_SizeInWords')], write_only_i_len_ret_buffer_alloc(0, 1)],
    [('_ugetdcwd', '_wgetdcwd', ['_getdcwd'], ['_tgetdcwd']), [('wchar_t *', '_DstBuf'), ('int', '_SizeInWords')], write_only_i_len_ret_buffer_alloc(0, 1)],

# io.h
    [('_uaccess', '_waccess', ['_access'], ['_taccess']), [('wchar_t const *', '_Filename')], read_only_wo_len],
    [('_uchmod', '_wchmod', ['_chmod'], ['_tchmod']), [('wchar_t const *', '_Filename')], read_only_wo_len],
    [('_ucreat', '_wcreat', ['_creat'], ['_tcreat']), [('wchar_t const *', '_Filename')], read_only_wo_len],
    [('_uunlink', '_wunlink', ['_unlink'], ['_tunlink']), [('wchar_t const *', '_Filename')], read_only_wo_len],
    [('_urename', '_wrename', ['rename'], ['_trename']), [('wchar_t const *', '_OldFilename'), ('wchar_t const *', '_NewFilename')], read_only_wo_len],
    [('_uopen', '_wopen', ['_open'], ['_topen']), [('wchar_t const *', '_Filename')], read_only_wo_len],
    [('_usopen', '_wsopen', ['_sopen'], ['_tsopen']), [('wchar_t const *', '_Filename')], read_only_wo_len],
    [('_umktemp', '_wmktemp', ['_mktemp'], ['_tmktemp']), [('wchar_t *', '_TemplateName')], write_only_wo_len_ret("MAX_PATH", 0)],

# stdlib.h

    [('_usystem', '_wsystem', ['system'], ['_tsystem']), [('wchar_t const *', '_Command')], read_only_wo_len],
    [('_uputenv', '_wputenv', ['_putenv'], ['_tputenv']), [('wchar_t const *', '_EnvString')], read_only_wo_len],

# sys/stat.h

    [('_ustat', '_wstat', ['_stat'], ['_tstat']), [('wchar_t const *', '_Name')], read_only_wo_len],
    [('_ustat32', '_wstat32', ['_stat32'], ['_tstat32']), [('wchar_t const *', '_Name')], read_only_wo_len],
    [('_ustat32i64', '_wstat32i64', ['_stat32i64'], ['_tstat32i64']), [('wchar_t const *', '_Name')], read_only_wo_len],
    [('_ustat64i32', '_wstat64i32', ['_stat64i32'], ['_tstat64i32']), [('wchar_t const *', '_Name')], read_only_wo_len],
    [('_ustat64', '_wstat64', ['_stat64'], ['_tstat64']), [('wchar_t const *', '_Name')], read_only_wo_len],

# sys/utime.h

    [('_uutime', '_wutime', ['_utime'], ['_tutime']), [('wchar_t const *', '_Filename')], read_only_wo_len],
    [('_uutime32', '_wutime32', ['_utime32'], ['_tutime32']), [('wchar_t const *', '_Filename')], read_only_wo_len],
    [('_uutime64', '_wutime64', ['_utime64'], ['_tutime64']), [('wchar_t const *', '_Filename')], read_only_wo_len],

]

dispatcher = CRTDispatcher()

dispatcher.register(spec)

index = clang.cindex.Index.create()
tu = index.parse(sys.argv[2], ['-I', sys.argv[1]])
print 'Translation unit:', tu.spelling
for c in tu.cursor.get_children():
    #dump(0, c)
    if(c.type.kind.name == "FUNCTIONPROTO" and re.search('^_w(?!rite|to|csto)', c.spelling)):
        desc = FunctionDescriptor(c)
        dispatcher.dispatch(desc)
