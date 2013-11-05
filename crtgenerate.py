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
    [('_ufsopen', '_wfsopen', ['_fsopen'], ['_tfsopen']), [('wchar_t const *', '_Filename'), ('wchar_t const *', '_Mode')], ro_nolen],
    [('_ufopen', '_wfopen', ['fopen'], ['_tfopen']), [('wchar_t const *', '_Filename'), ('wchar_t const *', '_Mode')], ro_nolen],
    [('_ufreopen', '_wfreopen', ['freopen'], ['_tfreopen']), [('wchar_t const *', '_Filename'), ('wchar_t const *', '_Mode')], ro_nolen],
    [('_upopen', '_wpopen', ['_popen'], ['_tpopen']), [('wchar_t const *', '_Command'), ('wchar_t const *', '_Mode')], ro_nolen],
    [('_uremove', '_wremove', ['remove'], ['_tremove']), [('wchar_t const *', '_Filename')], ro_nolen],
    [('_utmpnam', '_wtmpnam', ['tmpnam'], ['_ttmpnam']), [('wchar_t *', '_Buffer')], wo_nolen_ret_null_static('MAX_PATH', 0)],
    [('_utempnam', '_wtempnam', ['_tempnam'], ['_ttempnam']), [('wchar_t const *', '_Directory'), ('wchar_t const *', '_FilePrefix')], [ro_nolen, ret_alloc]],

# direct.h
    [('_uchdir', '_wchdir', ['_chdir'], ['_tchdir']), [('wchar_t const *', '_Path')], ro_nolen],
    [('_umkdir', '_wmkdir', ['_mkdir'], ['_tmkdir']), [('wchar_t const *', '_Path')], ro_nolen],
    [('_urmdir', '_wrmdir', ['_rmdir'], ['_trmdir']), [('wchar_t const *', '_Path')], ro_nolen],
    [('_ugetcwd', '_wgetcwd', ['_getcwd'], ['_tgetcwd']), [('wchar_t *', '_DstBuf'), ('int', '_SizeInWords')], wo_rolen_ret_buffer_alloc(0, 1)],
    [('_ugetdcwd', '_wgetdcwd', ['_getdcwd'], ['_tgetdcwd']), [('wchar_t *', '_DstBuf'), ('int', '_SizeInWords')], wo_rolen_ret_buffer_alloc(0, 1)],

# io.h
    [('_uaccess', '_waccess', ['_access'], ['_taccess']), [('wchar_t const *', '_Filename')], ro_nolen],
    [('_uchmod', '_wchmod', ['_chmod'], ['_tchmod']), [('wchar_t const *', '_Filename')], ro_nolen],
    [('_ucreat', '_wcreat', ['_creat'], ['_tcreat']), [('wchar_t const *', '_Filename')], ro_nolen],
    [('_uunlink', '_wunlink', ['_unlink'], ['_tunlink']), [('wchar_t const *', '_Filename')], ro_nolen],
    [('_urename', '_wrename', ['rename'], ['_trename']), [('wchar_t const *', '_OldFilename'), ('wchar_t const *', '_NewFilename')], ro_nolen],
    [('_uopen', '_wopen', ['_open'], ['_topen']), [('wchar_t const *', '_Filename'), ('int', '_OpenFlag')], [ro_nolen_idx(0), optional(1, 'int')]],
    [('_usopen', '_wsopen', ['_sopen'], ['_tsopen']), [('wchar_t const *', '_Filename'), ('int', '_ShareFlag')], [ro_nolen_idx(0), optional(1, 'int')]],
    [('_umktemp', '_wmktemp', ['_mktemp'], ['_tmktemp']), [('wchar_t *', '_TemplateName')], wo_nolen_ret("MAX_PATH", 0)],

# stdlib.h

    [('_usystem', '_wsystem', ['system'], ['_tsystem']), [('wchar_t const *', '_Command')], ro_nolen],
    [('_uputenv', '_wputenv', ['_putenv'], ['_tputenv']), [('wchar_t const *', '_EnvString')], ro_nolen],

# sys/stat.h

    [('_ustat32', '_wstat32', [], ['_tstat32']), [('wchar_t const *', '_Name')], ro_nolen],
    [('_ustat32i64', '_wstat32i64', [], ['_tstat32i64']), [('wchar_t const *', '_Name')], ro_nolen],
    [('_ustat64i32', '_wstat64i32', [], ['_tstat64i32']), [('wchar_t const *', '_Name')], ro_nolen],
    [('_ustat64', '_wstat64', [], ['_tstat64']), [('wchar_t const *', '_Name')], ro_nolen],

# sys/utime.h

    [('_uutime', '_wutime', ['_utime'], ['_tutime']), [('wchar_t const *', '_Filename')], ro_nolen],
    [('_uutime32', '_wutime32', ['_utime32'], ['_tutime32']), [('wchar_t const *', '_Filename')], ro_nolen],
    [('_uutime64', '_wutime64', ['_utime64'], ['_tutime64']), [('wchar_t const *', '_Filename')], ro_nolen],

# process.h

    [('_uexecv', '_wexecv', ['_execv'], ['_texecv']), [('wchar_t const *', '_Filename'), ('wchar_t const * const *', '_ArgList')], [ro_nolen_idx(0), roarray_nolen_idx(1)]],
    [('_uexecv_', '_uexecv', ['execv'], []), [], forward],
    [('_uexecve', '_wexecve', ['_execve'], ['_texecve']), [('wchar_t const *', '_Filename'), ('wchar_t const * const *', '_ArgList'), ('wchar_t const * const *', '_Env')], [ro_nolen_idx(0), roarray_nolen_idx([1,2])]],
    [('_uexecve_', '_uexecve', ['execve'], []), [], forward],
    [('_uexecvp', '_wexecvp', ['_execvp'], ['_texecvp']), [('wchar_t const *', '_Filename'), ('wchar_t const * const *', '_ArgList')], [ro_nolen_idx(0), roarray_nolen_idx(1)]],
    [('_uexecvp_', '_uexecvp', ['execvp'], []), [], forward],
    [('_uexecvpe', '_wexecvpe', ['_execvpe'], ['_texecvpe']), [('wchar_t const *', '_Filename'), ('wchar_t const * const *', '_ArgList'), ('wchar_t const * const *', '_Env')], [ro_nolen_idx(0), roarray_nolen_idx([1,2])]],
    [('_uexecvpe_', '_uexecvpe', ['execvpe'], []), [], forward],
    [('_uexecl', '_wexecl', ['_execl'], ['_texecl']), [('wchar_t const *', '_Filename'), ('wchar_t const *', '_ArgList')], [ro_nolen_idx(0), rova_nolen_idx(1)]],
    [('_uexecle', '_wexecle', ['_execle'], ['_texecle']), [('wchar_t const *', '_Filename'), ('wchar_t const *', '_ArgList')], [ro_nolen_idx(0), rova_nolen_withenv_idx(1)]],
    [('_uexeclp', '_wexeclp', ['_execlp'], ['_texeclp']), [('wchar_t const *', '_Filename'), ('wchar_t const *', '_ArgList')], [ro_nolen_idx(0), rova_nolen_idx(1)]],
    [('_uexeclpe', '_wexeclpe', ['_execlpe'], ['_texeclpe']), [('wchar_t const *', '_Filename'), ('wchar_t const *', '_ArgList')], [ro_nolen_idx(0), rova_nolen_withenv_idx(1)]],
    [('_uspawnv', '_wspawnv', ['_spawnv'], ['_tspawnv']), [('wchar_t const *', '_Filename'), ('wchar_t const * const *', '_ArgList')], [ro_nolen_idx(0), roarray_nolen_idx(1)]],
    [('_uspawnv_', '_uspawnv', ['spawnv'], []), [], forward],
    [('_uspawnve', '_wspawnve', ['_spawnve'], ['_tspawnve']), [('wchar_t const *', '_Filename'), ('wchar_t const * const *', '_ArgList'), ('wchar_t const * const *', '_Env')], [ro_nolen_idx(0), roarray_nolen_idx([1,2])]],
    [('_uspawnve_', '_uspawnve', ['spawnve'], []), [], forward],
    [('_uspawnvp', '_wspawnvp', ['_spawnvp'], ['_tspawnvp']), [('wchar_t const *', '_Filename'), ('wchar_t const * const *', '_ArgList')], [ro_nolen_idx(0), roarray_nolen_idx(1)]],
    [('_uspawnvp_', '_uspawnvp', ['spawnvp'], []), [], forward],
    [('_uspawnvpe', '_wspawnvpe', ['_spawnvpe'], ['_tspawnvpe']), [('wchar_t const *', '_Filename'), ('wchar_t const * const *', '_ArgList'), ('wchar_t const * const *', '_Env')], [ro_nolen_idx(0), roarray_nolen_idx([1,2])]],
    [('_uspawnvpe_', '_uspawnvpe', ['spawnvpe'], []), [], forward],
    [('_uspawnl', '_wspawnl', ['_spawnl'], ['_tspawnl']), [('wchar_t const *', '_Filename'), ('wchar_t const *', '_ArgList')], [ro_nolen_idx(0), rova_nolen_idx(1)]],
    [('_uspawnle', '_wspawnle', ['_spawnle'], ['_tspawnle']), [('wchar_t const *', '_Filename'), ('wchar_t const *', '_ArgList')], [ro_nolen_idx(0), rova_nolen_withenv_idx(1)]],
    [('_uspawnlp', '_wspawnlp', ['_spawnlp'], ['_tspawnlp']), [('wchar_t const *', '_Filename'), ('wchar_t const *', '_ArgList')], [ro_nolen_idx(0), rova_nolen_idx(1)]],
    [('_uspawnlpe', '_wspawnlpe', ['_spawnlpe'], ['_tspawnlpe']), [('wchar_t const *', '_Filename'), ('wchar_t const *', '_ArgList')], [ro_nolen_idx(0), rova_nolen_withenv_idx(1)]],

]

dispatcher = CRTDispatcher()

dispatcher.register(spec)

index = clang.cindex.Index.create()
tu = index.parse(sys.argv[2], ['-I', sys.argv[1]])
print 'Translation unit:', tu.spelling
for c in tu.cursor.get_children():
    #dump(0, c)
    if(c.type.kind.name == "FUNCTIONPROTO" and re.search('^_w(?!rite|to|csto)|^_u(exec|spawn)v', c.spelling)):
        desc = FunctionDescriptor(c)
        dispatcher.dispatch(desc)
