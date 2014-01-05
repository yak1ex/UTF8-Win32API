#!/usr/bin/env python
""" Usage: call with <filename>
"""

from converter import *

stat_header_prologue = '''\

#ifndef UTF8_WIN32_DONT_REPLACE_MSVCRT

/* Need to include before the following macro, to avoid type conflicts */
#include <sys/stat.h>

#ifdef _USE_32BIT_TIME_T

#ifdef _stat
#undef _stat
#endif
#define _stat _ustat32

#ifdef _stati64
#undef _stati64
#endif
#define _stati64 _ustat32i64

#else

#ifdef _stat
#undef _stat
#endif
#define _stat _ustat64i32

#ifdef _stati64
#undef _stati64
#endif
#define _stati64 _ustat64

#endif

#ifdef _stat32
#undef _stat32
#endif
#define _stat32 _ustat32

#ifdef _stat32i64
#undef _stat32i64
#endif
#define _stat32i64 _ustat32i64

#ifdef _stat64i32
#undef _stat64i32
#endif
#define _stat64i32 _ustat64i32

#ifdef _stat64
#undef _stat64
#endif
#define _stat64 _ustat64

/* from _mingw_stat64.h */

#include <crtdefs.h>
#pragma pack(push, CRT_PACKING)

  struct _stat32 {
    _dev_t st_dev;
   _ino_t st_ino;
    unsigned short st_mode;
    short st_nlink;
    short st_uid;
    short st_gid;
    _dev_t st_rdev;
    _off_t st_size;
    __time32_t st_atime;
    __time32_t st_mtime;
    __time32_t st_ctime;
  };

  struct _stat32i64 {
    _dev_t st_dev;
    _ino_t st_ino;
    unsigned short st_mode;
    short st_nlink;
    short st_uid;
    short st_gid;
    _dev_t st_rdev;
    __MINGW_EXTENSION __int64 st_size;
    __time32_t st_atime;
    __time32_t st_mtime;
    __time32_t st_ctime;
  };

  struct _stat64i32 {
    _dev_t st_dev;
    _ino_t st_ino;
    unsigned short st_mode;
    short st_nlink;
    short st_uid;
    short st_gid;
    _dev_t st_rdev;
    _off_t st_size;
    __time64_t st_atime;
    __time64_t st_mtime;
    __time64_t st_ctime;
  };

  struct _stat64 {
    _dev_t st_dev;
    _ino_t st_ino;
    unsigned short st_mode;
    short st_nlink;
    short st_uid;
    short st_gid;
    _dev_t st_rdev;
    __MINGW_EXTENSION __int64 st_size;
    __time64_t st_atime;
    __time64_t st_mtime;
    __time64_t st_ctime;
  };

#pragma pack(pop)
#endif
'''

environ_header_prologue = '''\

extern char** _uenviron;
#ifndef UTF8_WIN32_DONT_REPLACE_MSVCRT
#ifdef environ
#undef environ
#endif
#define environ _uenviron
#ifdef _environ
#undef _environ
#endif
#define _environ _uenviron
#endif

'''
spec = [

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
    [('_uputenv', '_wputenv', ['_putenv'], ['_tputenv']), [('wchar_t const *', '_EnvString')], [ro_nolen, updateenv], {'header_prologue': environ_header_prologue}],

# sys/stat.h

    [('_ustat32', '_wstat32', [], ['_tstat32']), [('wchar_t const *', '_Name')], ro_nolen, {'header_prologue': stat_header_prologue}],
    [('_ustat32i64', '_wstat32i64', [], ['_tstat32i64']), [('wchar_t const *', '_Name')], ro_nolen],
    [('_ustat64i32', '_wstat64i32', [], ['_tstat64i32']), [('wchar_t const *', '_Name')], ro_nolen],
    [('_ustat64', '_wstat64', [], ['_tstat64']), [('wchar_t const *', '_Name')], ro_nolen],

# sys/utime.h

    [('_uutime', '_wutime', ['_utime'], ['_tutime']), [('wchar_t const *', '_Filename')], ro_nolen],
# Plain msvcrt may not have _utime32
#   [('_uutime32', '_wutime32', ['_utime32'], ['_tutime32']), [('wchar_t const *', '_Filename')], ro_nolen],
    [('_uutime64', '_wutime64', ['_utime64'], ['_tutime64']), [('wchar_t const *', '_Filename')], ro_nolen],

# process.h

    [('_uexecv', '_wexecv', ['_execv'], ['_texecv']), [('wchar_t const *', '_Filename'), ('wchar_t const * const *', '_ArgList')], [ro_nolen_idx(0), roarray_nolen_idx(1)], {'no_oldconv': 1}],
    [('_uexecv_', '_uexecv', ['execv'], []), [], forward, {'oldname': 1}],
    [('_uexecve', '_wexecve', ['_execve'], ['_texecve']), [('wchar_t const *', '_Filename'), ('wchar_t const * const *', '_ArgList'), ('wchar_t const * const *', '_Env')], [ro_nolen_idx(0), roarray_nolen_idx([1,2])], {'no_oldconv': 1}],
    [('_uexecve_', '_uexecve', ['execve'], []), [], forward, {'oldname': 1}],
    [('_uexecvp', '_wexecvp', ['_execvp'], ['_texecvp']), [('wchar_t const *', '_Filename'), ('wchar_t const * const *', '_ArgList')], [ro_nolen_idx(0), roarray_nolen_idx(1)], {'no_oldconv': 1}],
    [('_uexecvp_', '_uexecvp', ['execvp'], []), [], forward, {'oldname': 1}],
    [('_uexecvpe', '_wexecvpe', ['_execvpe'], ['_texecvpe']), [('wchar_t const *', '_Filename'), ('wchar_t const * const *', '_ArgList'), ('wchar_t const * const *', '_Env')], [ro_nolen_idx(0), roarray_nolen_idx([1,2])], {'no_oldconv': 1}],
    [('_uexecvpe_', '_uexecvpe', ['execvpe'], []), [], forward, {'oldname': 1}],
    [('_uexecl', '_wexecl', ['_execl'], ['_texecl']), [('wchar_t const *', '_Filename'), ('wchar_t const *', '_ArgList')], [ro_nolen_idx(0), rova_nolen_idx(1)]],
    [('_uexecle', '_wexecle', ['_execle'], ['_texecle']), [('wchar_t const *', '_Filename'), ('wchar_t const *', '_ArgList')], [ro_nolen_idx(0), rova_nolen_withenv_idx(1)]],
    [('_uexeclp', '_wexeclp', ['_execlp'], ['_texeclp']), [('wchar_t const *', '_Filename'), ('wchar_t const *', '_ArgList')], [ro_nolen_idx(0), rova_nolen_idx(1)]],
    [('_uexeclpe', '_wexeclpe', ['_execlpe'], ['_texeclpe']), [('wchar_t const *', '_Filename'), ('wchar_t const *', '_ArgList')], [ro_nolen_idx(0), rova_nolen_withenv_idx(1)]],
    [('_uspawnv', '_wspawnv', ['_spawnv'], ['_tspawnv']), [('wchar_t const *', '_Filename'), ('wchar_t const * const *', '_ArgList')], [ro_nolen_idx(0), roarray_nolen_idx(1)], {'no_oldconv': 1}],
    [('_uspawnv_', '_uspawnv', ['spawnv'], []), [], forward, {'oldname': 1}],
    [('_uspawnve', '_wspawnve', ['_spawnve'], ['_tspawnve']), [('wchar_t const *', '_Filename'), ('wchar_t const * const *', '_ArgList'), ('wchar_t const * const *', '_Env')], [ro_nolen_idx(0), roarray_nolen_idx([1,2])], {'no_oldconv': 1}],
    [('_uspawnve_', '_uspawnve', ['spawnve'], []), [], forward, {'oldname': 1}],
    [('_uspawnvp', '_wspawnvp', ['_spawnvp'], ['_tspawnvp']), [('wchar_t const *', '_Filename'), ('wchar_t const * const *', '_ArgList')], [ro_nolen_idx(0), roarray_nolen_idx(1)], {'no_oldconv': 1}],
    [('_uspawnvp_', '_uspawnvp', ['spawnvp'], []), [], forward, {'oldname': 1}],
    [('_uspawnvpe', '_wspawnvpe', ['_spawnvpe'], ['_tspawnvpe']), [('wchar_t const *', '_Filename'), ('wchar_t const * const *', '_ArgList'), ('wchar_t const * const *', '_Env')], [ro_nolen_idx(0), roarray_nolen_idx([1,2])], {'no_oldconv': 1}],
    [('_uspawnvpe_', '_uspawnvpe', ['spawnvpe'], []), [], forward, {'oldname': 1}],
    [('_uspawnl', '_wspawnl', ['_spawnl'], ['_tspawnl']), [('wchar_t const *', '_Filename'), ('wchar_t const *', '_ArgList')], [ro_nolen_idx(0), rova_nolen_idx(1)]],
    [('_uspawnle', '_wspawnle', ['_spawnle'], ['_tspawnle']), [('wchar_t const *', '_Filename'), ('wchar_t const *', '_ArgList')], [ro_nolen_idx(0), rova_nolen_withenv_idx(1)]],
    [('_uspawnlp', '_wspawnlp', ['_spawnlp'], ['_tspawnlp']), [('wchar_t const *', '_Filename'), ('wchar_t const *', '_ArgList')], [ro_nolen_idx(0), rova_nolen_idx(1)]],
    [('_uspawnlpe', '_wspawnlpe', ['_spawnlpe'], ['_tspawnlpe']), [('wchar_t const *', '_Filename'), ('wchar_t const *', '_ArgList')], [ro_nolen_idx(0), rova_nolen_withenv_idx(1)]],

]

import sys
from dispatcher import CRTDispatcher

dispatcher = CRTDispatcher(sys.argv[1].lower() != 'false')
dispatcher.register(spec)
dispatcher.run(sys.argv[3], '^_w(?!rite|to|csto)|^_u(exec|spawn)v', 'DO_NOT_MATCH_ANYTHING', ['-I', sys.argv[2]])
