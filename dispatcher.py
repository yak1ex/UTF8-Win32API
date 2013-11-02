"""Dispatcher to actual conversion routines"""

import os.path
import re

class _Output(object):
    _cpp = {}
    _h = {}

    def _cpp_name(self, outname):
        return outname.replace('.h', 'u.cpp')

    def _h_name(self, outname):
        return outname.replace('.h', 'u.h')

    def _txt_name(self, outname):
        return outname.replace('.h', 'u.txt')

    def _cpp_header(self, outname):
        actualname = self._cpp_name(outname)
        if actualname in self._cpp:
            return
        self._cpp[actualname] = 1
        with open(actualname, 'a') as f:
            # FIXME: Inappropriate tight coupling
            if outname == 'msvcrt.h':
                f.write("#define UTF8_WIN32_DONT_REPLACE_MSVCRT\n")
                f.write("#include <vector>\n")
                f.write("#include <errno.h>\n")
            f.write("#include \"" + self._h_name(outname) + "\"\n")
            f.write("#include \"win32u_helper.hpp\"\n")

    def _h_header(self, outname):
        actualname = self._h_name(outname)
        if actualname in self._h:
            return
        self._h[actualname] = 1
        guard_name = actualname.upper().replace('.', '_')
        with open(actualname, 'a') as f:
            f.write("#ifndef " + guard_name + "\n")
            f.write("#define " + guard_name + "\n\n")
            f.write("#include <windows.h>\n\n")
            # FIXME: Inappropriate tight coupling
            if outname == 'msvcrt.h':
                f.write("#include <wchar.h>\n\n")
            f.write("#ifdef __cplusplus\nextern \"C\" {\n#endif\n\n")

    def cpp(self, outname, str):
        self._cpp_header(outname)
        with open(self._cpp_name(outname), 'a') as f:
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
                f.write("\n#ifdef __cplusplus\n}\n#endif\n\n#endif\n")

from collections import namedtuple

convctx = namedtuple('ConvCtx', 'desc_self desc_call code_before code_after')

class _Spec:
# conversion spec
    REGEXP, TYPES, FUNC = range(3)
# in REGEXP for CRT
    SELF, CALL, ALIAS_OPT, ALIAS_ALL = range(4)
# macro type
    NORMAL, CRT_OPT, API_OPT = range(3)

class Dispatcher(object):
    _output = _Output()
    _table = []

    def register(self, spec):
        self._table.extend(spec)

    def dispatch(self, desc):
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

                processed = True

                ctx = convctx(desc.clone(), desc.clone(), '', '')
                ctx = self._adjust(ctx, onespec)
                funcs = onespec[_Spec.FUNC] if isinstance(onespec[_Spec.FUNC], list) else [onespec[_Spec.FUNC]]
                ctx = reduce(lambda acc, func: func(acc, onespec[_Spec.TYPES]), funcs, ctx)

                macro = self._macro(ctx, onespec)

                if ctx.desc_self.result_type == 'void' or ctx.desc_self.result_type == 'VOID':
                    call = ctx.desc_call.make_func_call() + ";\n"
                    ret = "return;\n"
                elif ctx.desc_self.result_type == ctx.desc_call.result_type:
                    call = ctx.desc_call.result_type + ' ret = ' + ctx.desc_call.make_func_call() + ";\n"
                    ret = "return ret;\n"
                else:
                    call = ctx.desc_call.result_type + ' ret = ' + ctx.desc_call.make_func_call() + ";\n"
                    ret = "return ret_;\n" # ret_ MUST be defined in conversion

                self._output.cpp(outname, \
                    ctx.desc_self.make_func_decl() + "\n{\n" + \
                    ctx.code_before + "\t" + call + ctx.code_after + "\t" + ret + "}\n" \
                )
                self._output.h(outname, \
                    "\n".join(map( \
                        lambda x: ("#ifndef UTF8_WIN32_DONT_REPLACE_MSVCRT\n" if x[0] == _Spec.CRT_OPT else "#ifndef UTF8_WIN32_DONT_REPLACE_ANSI\n" if x[0] == _Spec.API_OPT else "") + \
                            "#ifdef " + x[1] + "\n" + \
                            "#undef " + x[1] + "\n" + \
                            "#endif\n" + \
                            "#define " + x[1] + ' ' + ctx.desc_self.name + "\n" + \
                            ("#endif\n" if x[0] == _Spec.CRT_OPT or x[0] == _Spec.API_OPT else ""), macro)) + \
                    "extern " + ctx.desc_self.make_func_decl() + ";\n\n" \
                )
                break
        if not processed:
            self._output.txt(outname, \
                desc.make_func_decl() + "\n" \
            )

    def __del__(self):
        self._output.cleanup()

class APIDispatcher(Dispatcher):
    def _match(self, onespec, desc):
        return re.search(onespec[_Spec.REGEXP], desc.name)

    def _outname(self, desc):
        return os.path.basename("%s" % desc.file)

    def _adjust(self, ctx, onespec):
        ctx.desc_self.name = ctx.desc_self.name[:-1] + 'U'
        return ctx

    def _macro(self, ctx, onespec):
        return [(_Spec.NORMAL, ctx.desc_self.name[:-1]), (_Spec.API_OPT, ctx.desc_self.name[:-1] + 'A')]

    def __del__(self):
        with open('windowsu.h', 'a') as f:
            f.write("#ifndef WINDOWSU_H\n#define WINDOWSU_H\n\n")
            for actualname in self._output._h:
                f.write("#include <" + actualname + ">\n")
            f.write("\n#endif\n")
        Dispatcher.__del__(self)

class CRTDispatcher(Dispatcher):
    def _match(self, onespec, desc):
        return desc.name == onespec[_Spec.REGEXP][_Spec.CALL]

    def _outname(self, desc):
        return 'msvcrt.h'

    def _adjust(self, ctx, onespec):
        ctx.desc_self.name = onespec[_Spec.REGEXP][_Spec.SELF]
        ctx.desc_call.name = onespec[_Spec.REGEXP][_Spec.CALL]
        return ctx

    def _macro(self, ctx, onespec):
        macro = map(lambda x: (_Spec.CRT_OPT, x), onespec[_Spec.REGEXP][_Spec.ALIAS_OPT])
        macro.extend(map(lambda x: (_Spec.NORMAL, x), onespec[_Spec.REGEXP][_Spec.ALIAS_ALL]))
        return macro
