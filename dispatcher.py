"""Dispatcher to actual conversion routines"""

import os.path
import re
from string import Template

class _Output(object):
    _cpp = {}
    _h = {}

    def __init__(self, split = False, header_dir = 'include', source_dir = 'gensrc'):
        self._header_dir = header_dir
        self._source_dir = source_dir
        self._split = split

    def configure(self, source_prologue = '', header_prologue = ''):
        self._source_prologue = source_prologue
        self._header_prologue = header_prologue

    def _cpp_name(self, outname):
        if self._split:
            return '%s/%s' % (self._source_dir, outname.replace('.h', 'u_%s.cpp' % self._cpp[outname]))
        return '%s/%s' % (self._source_dir, outname.replace('.h', 'u.cpp'))

    def _cpp2_name(self, outname):
        if self._split:
            return '%s/%s' % (self._source_dir, outname.replace('.h', 'u_%s_.cpp' % self._cpp[outname]))
        return '%s/%s' % (self._source_dir,  outname.replace('.h', 'u_.cpp'))

    def _h_name(self, outname):
        return '%s/%s' % (self._header_dir, outname.replace('.h', 'u.h'))

    def _txt_name(self, outname):
        return '%s/%s' % (self._source_dir, outname.replace('.h', 'u.txt'))

    def _cpp_header(self, outname):
        self._cpp_header_(outname, self._cpp_name(outname))

    def _cpp2_header(self, outname):
        self._cpp_header_(outname, self._cpp2_name(outname))

    def _cpp_header_(self, outname, actualname):
        if actualname in self._cpp:
            return
        self._cpp[actualname] = 1
        with open(actualname, 'a') as f:
            f.write(self._source_prologue + Template('''\
#include "win32u_apistructu.h"
#include "$header"

#include "helper/win32u_helper.hpp"
#include "helper/win32u_helperi.hpp"
#include "odstream/odstream.hpp"

''').substitute(header = self._h_name(outname).partition('/')[2]))

    def _h_header(self, outname):
        actualname = self._h_name(outname)
        if actualname in self._h:
            return
        self._h[actualname] = 1
        guard_name = actualname.partition('/')[2].upper().replace('.', '_')
        with open(actualname, 'a') as f:
            f.write(Template('''\
#ifndef $guard
#define $guard

#include <windows.h>
$header
#ifdef __cplusplus
extern "C" {
#endif

''').substitute(guard = guard_name, header = self._header_prologue))

    def cpp_renew(self, outname):
        if not outname in self._cpp:
            self._cpp[outname] = 0
        self._cpp[outname] += 1

    def cpp(self, outname, str):
        self._cpp_header(outname)
        with open(self._cpp_name(outname), 'a') as f:
            f.write(str)

    def cpp2(self, outname, str):
        self._cpp2_header(outname)
        with open(self._cpp2_name(outname), 'a') as f:
            f.write(str)

    def h(self, outname, str):
        self._h_header(outname)
        with open(self._h_name(outname), 'a') as f:
            f.write(str)

    def txt(self, outname, str):
        with open(self._txt_name(outname), 'a') as f:
            f.write(str)

    def cleanup(self):
        for actualname in self._h:
            with open(actualname, 'a') as f:
                f.write('''
#ifdef __cplusplus
}
#endif

#endif
''')

from collections import namedtuple

convctx = namedtuple('ConvCtx', 'types desc_self desc_call code_before code_after')
struct_convctx = namedtuple('StructConvCtx', 'types desc header')

class _Spec:
# conversion spec
    REGEXP, TYPES, FUNC, ATTR = range(4)
    STRUCT_FUNC = 1
# in REGEXP for CRT
    SELF, CALL, ALIAS_OPT, ALIAS_ALL = range(4)
# macro spec
    GUARD, REPLACEMENT = range(2)
    NORMAL = []
    CRT_OLD = ['UTF8_WIN32_DONT_REPLACE_MSVCRT', 'NO_OLDNAMES']
    CRT_OPT = ['UTF8_WIN32_DONT_REPLACE_MSVCRT']
    API_OPT = ['UTF8_WIN32_DONT_REPLACE_ANSI']

import clang.cindex
from descriptor import FunctionDescriptor, StructDescriptor

class Dispatcher(object):
    _table = []
    _struct_table = []
    _types = {}

    def __init__(self, split = False, header_dir = 'include', source_dir = 'gensrc'):
        self._output = _Output(split, header_dir, source_dir)

    def register(self, specs):
        for spec in specs:
            if len(spec) <= _Spec.ATTR:
                spec.append({})
        self._table.extend(specs)

    def register_struct(self, spec):
        self._struct_table.extend(spec)

    def _make_def(self, decl, name, trace, body):
        return Template('''
$decl
{
	ODS(<< "$name" << " : "$trace << std::endl);
$body
}
''').substitute(decl = decl, name = name, trace = trace, body = body)

    def run(self, input, target, target_struct, option = []):
        index = clang.cindex.Index.create()
        tu = index.parse(input, option)
        print 'Translation unit:', tu.spelling
#       dump(0, tu.cursor)
        for c in tu.cursor.get_children():
            if(FunctionDescriptor.is_target(c) and re.search(target, c.spelling)):
                self._dispatch(FunctionDescriptor(c))
            if(StructDescriptor.is_target(c) and re.search(target_struct, c.spelling)):
                self._dispatch_struct(StructDescriptor(c))

    def _process(self, desc, onespec, outname):
        ctx = convctx(self._types, desc.clone(), desc.clone(), '', '')
        ctx = self._adjust(ctx, onespec)
        funcs = onespec[_Spec.FUNC] if isinstance(onespec[_Spec.FUNC], list) else [onespec[_Spec.FUNC]]
        ctx = reduce(lambda acc, func: func(acc, onespec[_Spec.TYPES]), funcs, ctx)

        # FIXME: Fallback for variadic
        need_fallback = 'no_fallback' not in onespec[_Spec.ATTR] and not ctx.desc_self.is_variadic

        if need_fallback:
            desc_fallback, desc_fallback_call = self._fallback(ctx, onespec)
        macro = self._macro(ctx, onespec)

# No return value
        if ctx.desc_self.result_type == 'void' or ctx.desc_self.result_type == 'VOID':
            call = ctx.desc_call.make_func_call() + ';'
            ret = '''\
ODS(<< "%s : return" << std::endl);
	return;''' % ctx.desc_self.name
            if need_fallback:
                fallback_call = desc_fallback_call.make_func_call() + ';'
# A return type is converted
        elif ctx.desc_self.result_type == ctx.desc_call.result_type:
            call = '%s ret = %s;' % (ctx.desc_call.result_type, ctx.desc_call.make_func_call())
            ret = '''\
ODS(<< "%s : return " << win32u::dwrap(ret) << std::endl);
	return ret;''' % ctx.desc_self.name
            if need_fallback:
                fallback_call = 'return %s;' % desc_fallback_call.make_func_call()
# Otherwise
        else:
            call = '%s ret = %s;' % (ctx.desc_call.result_type, ctx.desc_call.make_func_call())
            ret = '''\
ODS(<< "%s : return " << win32u::dwrap(ret_) << std::endl);
	return ret_;''' % ctx.desc_self.name # ret_ MUST be defined in conversion
            if need_fallback:
                fallback_call = 'return %s;' % desc_fallback_call.make_func_call()

        self._output.cpp_renew(outname)
        self._output.cpp(outname,
            self._make_def(
                ctx.desc_self.make_func_decl(),
                ctx.desc_self.name,
                ctx.desc_self.make_trace_arg(),
                "%s\t%s\n%s\t%s" % (ctx.code_before, call, ctx.code_after, ret)))
# Check unintentional conversions, which does not specify all required parameter conversions.
        if (any([re.search('LPWSTR|LPCWSTR|W$', t) for t,n in ctx.desc_self.parameter_types]) or
            re.search('LPWSTR|LPCWSTR|W$', ctx.desc_self.result_type)):
            self._output.txt(outname, '// Warning: %s\n' % ctx.desc_self.make_func_decl())

        if need_fallback:
            self._output.cpp2(outname,
                self._make_def(
                    desc_fallback.make_func_decl(),
                    desc_fallback.name,
                    desc_fallback.make_trace_arg(),
                    "\t" + fallback_call))

        if 'header_prologue' in onespec[_Spec.ATTR]:
            self._output.h(outname, onespec[_Spec.ATTR]['header_prologue'])
        self._output.h(outname,
            "\n" + ''.join(map(
                lambda x: reduce(lambda acc, guard: Template('''\
#ifndef $guard
$body#endif
'''                 ).substitute(guard = guard, body = acc), reversed(x[_Spec.GUARD]), Template('''\
#ifdef $target
#undef $target
#endif
#define $target $name
'''                     ).substitute(target = x[_Spec.REPLACEMENT], name = ctx.desc_self.name)), macro)) +
            "extern %s;\n%s" % (ctx.desc_self.make_func_decl(),
                "extern %s;\n" % desc_fallback.make_func_decl() if need_fallback else "")
        )

    def _dispatch(self, desc):
        processed = False
        outname = self._outname(desc)
        for onespec in self._table:
            if(not self._match(onespec, desc)):
                continue

            flag = True
            for argspec in onespec[_Spec.TYPES]:
                if desc.index_arg(argspec) == -1:
                    flag = False
                    break

            if(flag):
                if onespec[_Spec.FUNC] is None:
                    break

                self._process(desc, onespec, outname)
                processed = True
                break

        if not processed:
            self._output.txt(outname,
                desc.make_func_decl() + "\n"
            )

    def _dispatch_struct(self, desc):
        processed = False
        outname = self._outname_struct(desc)
        for onespec in self._struct_table:
            if(not re.search(onespec[_Spec.REGEXP], desc.name)):
                continue

            ctx = struct_convctx(self._types, desc, '')
            funcs = onespec[_Spec.STRUCT_FUNC] if isinstance(onespec[_Spec.STRUCT_FUNC], list) else [onespec[_Spec.STRUCT_FUNC]]
            ctx = reduce(lambda acc, func: func(acc), funcs, ctx)
            self._output.h(outname, ctx.header)
            processed = True
            break

        if not processed:
            self._output.txt(outname, "struct %s;\n" % desc.name)

    def __del__(self):
        self._output.cleanup()

class APIDispatcher(Dispatcher):
    def __init__(self, split = False, header_dir = 'include', source_dir = 'gensrc'):
        Dispatcher.__init__(self, split, header_dir, source_dir)
        self._output.configure(source_prologue = '''\
#define UTF8_WIN32_DONT_REPLACE_ANSI
''')

    def _match(self, onespec, desc):
        return re.search(onespec[_Spec.REGEXP], desc.name)

    def _outname(self, desc):
        return os.path.basename("%s" % desc.file)

    def _outname_struct(self, desc):
        return 'win32u_apistruct.h'

    def _adjust(self, ctx, onespec):
        if ctx.desc_self.name[-1] == 'W':
            ctx.desc_self.name = ctx.desc_self.name[:-1] + 'U'
        else:
            ctx.desc_self.name = ctx.desc_self.name + 'U'
        return ctx

    def _fallback(self, ctx, onespec):
        fallback, fallback_call = ctx.desc_self.clone(), ctx.desc_self.clone()
        if ctx.desc_call.name[-1] == 'W':
            fallback.name = fallback.name[:-1] + 'A_'
            fallback_call.name = fallback_call.name[:-1] + 'A'
        else:
            fallback.name = fallback.name[:-1] + '_'
            fallback_call.name = fallback_call.name[:-1]
        return fallback, fallback_call

    def _macro(self, ctx, onespec):
        if ctx.desc_call.name[-1] == 'W':
            return [(_Spec.NORMAL, ctx.desc_self.name[:-1]), (_Spec.API_OPT, ctx.desc_self.name[:-1] + 'A')]
        else:
            return [(_Spec.API_OPT, ctx.desc_self.name[:-1])]

    def __del__(self):
        with open('include/windowsu.h', 'a') as f:
            f.write('''\
#ifndef WINDOWSU_H
#define WINDOWSU_H

#include "win32u_apistructu.h"
''')
            f.write(''.join(['#include "%s"\n' % x.partition('/')[2] for x in self._output._h if not re.search('/win32u_apistructu.h', x)]))
            f.write("\n#endif\n")
        Dispatcher.__del__(self)

class CRTDispatcher(Dispatcher):
    def __init__(self, split = False, header_dir = 'include', source_dir = 'gensrc'):
        Dispatcher.__init__(self, split, header_dir, source_dir)
        self._output.configure(header_prologue = '''\
#include <wchar.h>
#include <sys/utime.h>

''', source_prologue = '''\
#define UTF8_WIN32_DONT_REPLACE_MSVCRT
#include <vector>
#include <errno.h>
#include <stdio.h>
#include <direct.h>
#include <io.h>
#include <stdlib.h>
#include <sys/stat.h>
#include <sys/utime.h>
#include <process.h>
''')

    def register(self, specs):
        for spec in specs:
            if len(spec[_Spec.REGEXP][_Spec.ALIAS_OPT]) == 0:
                if len(spec) <= _Spec.ATTR:
                    spec.append({'no_fallback': 1})
                else:
                    spec[_Spec.ATTR]['no_fallback'] = 1
        Dispatcher.register(self, specs)

    def _match(self, onespec, desc):
        return desc.name == onespec[_Spec.REGEXP][_Spec.CALL]

    def _outname(self, desc):
        return 'msvcrt.h'

    def _outname_struct(self, desc):
        return 'msvcrt.h'

    def _adjust(self, ctx, onespec):
        ctx.desc_self.name = onespec[_Spec.REGEXP][_Spec.SELF]
        ctx.desc_call.name = onespec[_Spec.REGEXP][_Spec.CALL]
        return ctx

    def _fallback(self, ctx, onespec):
        fallback, fallback_call = ctx.desc_self.clone(), ctx.desc_self.clone()
        fallback.name = onespec[_Spec.REGEXP][_Spec.ALIAS_OPT][0] + '_'
        fallback_call.name = onespec[_Spec.REGEXP][_Spec.ALIAS_OPT][0]
        return fallback, fallback_call

    def _macro(self, ctx, onespec):
        macro = [(_Spec.NORMAL, x) for x in onespec[_Spec.REGEXP][_Spec.ALIAS_ALL]]
        if 'oldname' not in  onespec[_Spec.ATTR]:
            macro.extend([(_Spec.CRT_OPT, x) for x in onespec[_Spec.REGEXP][_Spec.ALIAS_OPT]])
        if 'no_oldconv' not in onespec[_Spec.ATTR]:
            macro.extend([(_Spec.CRT_OLD, x.replace('_', '')) for x in onespec[_Spec.REGEXP][_Spec.ALIAS_OPT]])
        return macro
