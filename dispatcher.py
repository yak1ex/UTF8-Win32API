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
            f.write("#ifndef __cplusplus\nexnter \"C\" {\n#endif\n\n")

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
                f.write("\n#ifndef __cplusplus\n};\n#endif\n\n#endif\n")

SPEC_REGEXP = 0
SPEC_TYPES = 1
SPEC_FUNC = 2

class Dispatcher(object):
    _output = _Output()
    _table = []

    def register(self, spec):
        self._table.extend(spec)

    def dispatch(self, desc):
        processed = False
        outname = os.path.basename("%s" % desc.file)
        for onespec in self._table:
            if(not re.search(onespec[SPEC_REGEXP], desc.name)):
                continue
            flag = True
            for argspec in onespec[SPEC_TYPES]:
                if desc.index_arg(argspec) == -1:
                    flag = False
                    break
            if(flag):
                processed = True
                (desc_self, desc_call, code) = onespec[SPEC_FUNC](desc, onespec[SPEC_TYPES])
                desc_self.name = desc_self.name[:-1] + 'U'
                self._output.cpp(outname, \
                    desc_self.make_func_decl() + "\n{\n" + \
                    "\t" + code + \
                    "\treturn " + desc_call.make_func_call() + ";\n}\n" \
                )
                self._output.h(outname, \
                    "extern " + desc_self.make_func_decl() + ";\n" \
                )
                break
        if not processed:
            self._output.txt(outname, \
                desc.make_func_decl() + "\n" \
            )

    def __del__(self):
        self._output.cleanup()

