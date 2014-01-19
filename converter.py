"""Converter functions

This file defines converter functions.

Actual converters' parameter:
ctx: A conversion context (a named tuple consisting of types, desc_self,desc_call, code_before and code_after).
  types: A hash consisting of { StructName: StructDescriptor, ... }.
  desc_self: A FunctionDescriptor for the function.
  desc_call: A FunctionDescriptor for the delegated function.
  code_before: A code fragment before the call of the delegated function.
  code_after: A code fragment after the call of the delegated function.
typespec: A list consisting of REGEXP, TYPES, FUNC and ATTR.
  REGEXP(0): A regexp or a tuple of consisting of SELF, CALL, ALIAS_OPT and ALIAS_ALL.
    SELF(0): A target function name.
    CALL(1): A delegated function name.
    ALIAS_OPT(2): A list of optional alias names.
    ALIAS_ALL(3): A list of alias names always effective.
  TYPES(1): A list of tuples consisting of a type name and a parameter name.
  FUNC(2): Converter functions. It can be scalar if only a converter function is used. Ohterwise, a list.
  ATTR(3): A hash of conversion attributes. The current available attributes are as follows:
    'no_fallback':  Do not produce an ANSI fallback function.
    'oldname': Treat an alias for optional function name as for an old function name.
    'no_oldconv': Do not produce an alias for old function name.
    'header_prologue': Add header contents before the function declaration.

Actual converters' return value:
A conversion context (a named tuple consisting of types, desc_self,desc_call, code_before and code_after)

"""

from string import Template

def _nolen_helper(ctx, typespec, coder):
    index = ctx.desc_self.index_arg(typespec)
    ctx.desc_self.transform_param(index, lambda t,n: (
        "LPSTR" if t == "LPWSTR" or t == "wchar_t *" else "LPCSTR", n))
    ctx.desc_call.transform_param(index, lambda t,n: (t, n + '_'))
    before, after = coder(*ctx.desc_self.get_param(index))
    return ctx._replace(code_before = ctx.code_before + before, code_after = ctx.code_after + after)

def _ro_nolen_imp(ctx, typespec):
    return _nolen_helper(ctx, typespec, \
        lambda t, n: (Template("""\
	win32u::WSTR ${name}_($name);
""").substitute(name = n), ''))

def ro_nolen_idx(idx):
    """A converter for read only strings without the corresponding length variables. Indices are specified."""
    return lambda ctx, typespecs: reduce( \
        lambda acc, x: _ro_nolen_imp(acc, x), \
        map(lambda x: typespecs[x], idx if isinstance(idx, list) else [idx]), \
        ctx \
    )

def ro_nolen(ctx, typespecs):
    """A converter for read only strings without the corresponding length variables. All specs are processed."""
    return reduce( \
        lambda acc, x: _ro_nolen_imp(acc, x), \
        typespecs, \
        ctx \
    )

def _roarray_nolen_imp(ctx, typespec):
    index = ctx.desc_self.index_arg(typespec)
    ctx.desc_self.transform_param(index, lambda t,n: ('LPCSTR const *', n))
    ctx.desc_call.transform_param(index, lambda t,n: (t, n + '_'))
    before = Template("""\
	std::vector<win32u::WSTR> ${name}_hold;
	int ${name}_idx = 0;
	while(1) {
		${name}_hold.push_back(win32u::WSTR(${name}[${name}_idx]));
		if(! ${name}_hold.back()) break;
		++${name}_idx;
	}
	std::vector<LPCWSTR> ${name}_arg;
	for(std::size_t ${name}_hold_idx = 0; ${name}_hold_idx != ${name}_hold.size(); ++${name}_hold_idx) {
		${name}_arg.push_back(${name}_hold[${name}_hold_idx]);
	}
	LPCWSTR* ${name}_ = &${name}_arg[0];
""").substitute(name = ctx.desc_self.get_pname(index))
    return ctx._replace(code_before = ctx.code_before + before)

def roarray_nolen_idx(idx):
    """A converter for an array of read only strings without the corresponding length variables. Indices are specified."""
    return lambda ctx, typespecs: reduce( \
        lambda acc, x: _roarray_nolen_imp(acc, x), \
        map(lambda x: typespecs[x], idx if isinstance(idx, list) else [idx]), \
        ctx \
    )

def _rova_nolen_imp(ctx, typespec):
    index = ctx.desc_self.index_arg(typespec)
    ctx.desc_self.transform_param(index, lambda t,n: ('LPCSTR', n))
    ctx.desc_call.transform_param(index, lambda t,n: (t, n + '_'))
    ctx.desc_call.is_variadic = False
    ctx.desc_call.name = ctx.desc_call.name.replace('l', 'v')
    before = Template("""\
	va_list ${name}_va;
	va_start(${name}_va, $name);
	std::vector<win32u::WSTR> ${name}_hold;
	${name}_hold.push_back(win32u::WSTR($name));
	do {
		LPSTR p = va_arg(${name}_va, LPSTR);
		${name}_hold.push_back(win32u::WSTR(p));
	} while(${name}_hold.back());
	std::vector<LPCWSTR> ${name}_arg;
	for(std::size_t ${name}_hold_idx = 0; ${name}_hold_idx != ${name}_hold.size(); ++${name}_hold_idx) {
		${name}_arg.push_back(${name}_hold[${name}_hold_idx]);
	}
	LPCWSTR* ${name}_ = &${name}_arg[0];
""").substitute(name = ctx.desc_self.get_pname(index))
    return ctx._replace(code_before = ctx.code_before + before)

def rova_nolen_idx(idx):
    """A converter for variadic read only strings without the corresponding length variables. The index prior to the variadic arguments is specified."""
    return lambda ctx, typespecs: reduce( \
        lambda acc, x: _rova_nolen_imp(acc, x), \
        map(lambda x: typespecs[x], idx if isinstance(idx, list) else [idx]), \
        ctx \
    )

def _rova_nolen_withenv_imp(ctx, typespec):
    index = ctx.desc_self.index_arg(typespec)
    ctx.desc_self.transform_param(index, lambda t,n: ('LPCSTR', n))
    ctx.desc_call.transform_param(index, lambda t,n: (t, n + '_'))
    ctx.desc_call.parameter_types.append(('LPCSTR*', ctx.desc_self.get_pname(index) + '_env_'))
    ctx.desc_call.is_variadic = False
    ctx.desc_call.name = ctx.desc_call.name.replace('l', 'v')
    before = Template("""\
	va_list ${name}_va;
	va_start(${name}_va, $name);
	std::vector<win32u::WSTR> ${name}_hold;
	${name}_hold.push_back(win32u::WSTR($name));
	do {
		LPSTR p = va_arg(${name}_va, LPSTR);
		${name}_hold.push_back(win32u::WSTR(p));
	} while(${name}_hold.back());
	std::vector<LPCWSTR> ${name}_arg;
	for(std::size_t ${name}_hold_idx = 0; ${name}_hold_idx != ${name}_hold.size(); ++${name}_hold_idx) {
		${name}_arg.push_back(${name}_hold[${name}_hold_idx]);
	}
	LPCWSTR* ${name}_ = &${name}_arg[0];

	LPCSTR* ${name}_env = va_arg(${name}_va, LPCSTR*);
	std::vector<win32u::WSTR> ${name}_env_hold;
	int ${name}_env_idx = 0;
	while(1) {
		${name}_env_hold.push_back(win32u::WSTR(${name}_env[${name}_env_idx]));
		if(! ${name}_env_hold.back()) break;
		++${name}_env_idx;
	}
	std::vector<LPCWSTR> ${name}_env_arg;
	for(std::size_t ${name}_env_hold_idx = 0; ${name}_env_hold_idx != ${name}_env_hold.size(); ++${name}_env_hold_idx) {
		${name}_env_arg.push_back(${name}_env_hold[${name}_env_hold_idx]);
	}
	LPCWSTR* ${name}_env_ = &${name}_env_arg[0];
""").substitute(name = ctx.desc_self.get_pname(index))
    return ctx._replace(code_before = ctx.code_before + before)

def rova_nolen_withenv_idx(idx):
    """A converter for variadic read only strings for arguments and environment variables without the corresponding length variables.

    The index prior to the variadic arguments is specified.
    """
    return lambda ctx, typespecs: _rova_nolen_withenv_imp(ctx, typespecs[idx])

def _wo_nolen_imp(ctx, typespec):
    return _nolen_helper(ctx, typespec, \
        lambda type, name: (\
            Template("""\
	win32u::WSTR ${name}_($name ? MAX_PATH : 0);
""").substitute(name = name), \
            Template("""\
	${name}_.get($name, MAX_PATH);
""").substitute(name = name)))

def wo_nolen_idx(idx):
    """A converter for write only strings without the corresponding length variables. Indices are specified."""
    return lambda ctx, typespecs: reduce( \
        lambda acc, x: _wo_nolen_imp(acc, x), \
        map(lambda x: typespecs[x], idx if isinstance(idx, list) else [idx]), \
        ctx \
    )

def wo_nolen(ctx, typespecs):
    """A converter for write only strings without the corresponding length variables. All specs are processed."""
    return reduce( \
        lambda acc, x: _wo_nolen_imp(acc, x), \
        typespecs, \
        ctx \
    )

def _wo_nolen_ret_null_static_imp(size, ctx, typespec):
    ctx.desc_self.result_type = 'LPSTR';
    return _nolen_helper(ctx, typespec, lambda type, name: (Template("""\
	static char static_buf[$size * 3];
	win32u::WSTR ${name}_($name);
""").substitute(size = size, name = name), Template("""\
	LPSTR ret_ = 0;
	if(ret) {
		ret_ = $name ? $name : static_buf;
		${name}_.get(ret_, ${name}_.get_utf8_length()); // Assuming sufficient buffer
	}
""").substitute(name = name)))

def wo_nolen_ret_null_static(size, idx):
    """A converter for write only strings returned as the result without the corresponding length variables, returning the static buffer if NULL pointer is specified."""
    return lambda ctx, typespecs: _wo_nolen_ret_null_static_imp(size if isinstance(size, str) else str(size), ctx, typespecs[idx])

def wo_rolen_ret_buffer_alloc(str_idx, len_idx):
    return lambda ctx, typespecs: _wo_rolen_ret_buffer_alloc_imp(str_idx, len_idx, ctx, typespecs)

def _wo_nolen_ret_imp(size, ctx, typespec):
    ctx.desc_self.result_type = 'LPSTR';
    return _nolen_helper(ctx, typespec, lambda type, name: (Template("""\
	win32u::WSTR ${name}_($size);
""").substitute(size = size, name = name), Template("""\
	LPSTR ret_ = 0;
	if(ret) {
		ret_ = ${name};
		${name}_.get(ret_, ${name}_.get_utf8_length()); // Assuming sufficient buffer
	}
""").substitute(name = name)))

def wo_nolen_ret(size, idx):
    """A converter for write only strings returned as the result without the corresponding length variables."""
    return lambda ctx, typespecs: _wo_nolen_ret_imp(size if isinstance(size, str) else str(size), ctx, typespecs[idx])

def _wo_len_helper(str_idx, len_idx, ctx, typespecs, coder):
    str_index = ctx.desc_self.index_arg(typespecs[str_idx])
    len_index = ctx.desc_self.index_arg(typespecs[len_idx])
    ctx.desc_self.transform_param(str_index, lambda t,n: ('LPSTR', n))
    ctx.desc_call.transform_param(str_index, lambda t,n: (t, n + '_'))
    ctx.desc_call.transform_param(len_index, lambda t,n: (t, n + '_'))
    before, after = coder(ctx.desc_self.get_ptype(str_index), ctx.desc_self.get_pname(str_index), *ctx.desc_self.get_param(len_index))
    return ctx._replace(code_before = ctx.code_before + before, code_after = ctx.code_after + after)

# TODO: Not sure len_name can be NULL or not
def wo_rwlen_ret_bool(str_idx, len_idx, error):
    """A converter for a write only string with a read/write length variable, returning a boolean flag."""
    return lambda ctx, typespecs: _wo_len_helper(str_idx, len_idx, ctx, typespecs, \
        lambda str_type, str_name, len_type, len_name: (Template("""\
	win32u::WSTR ${str_name}_(*${len_name});
	win32u::remove_pointer<$len_type>::type ${len_name}__ = *$len_name;
	$len_type ${len_name}_ = &${len_name}__;
""").substitute(str_name = str_name, len_name = len_name, len_type = len_type), Template("""\
	if(${str_name}_.get_utf8_length() <= *$len_name) {
		*$len_name = ${str_name}_.get($str_name, *$len_name);
	} else {
		SetLastError($error_code);
		ret = FALSE;
	}
""").substitute(str_name = str_name, len_name = len_name, error_code = error)))

# TODO: currently, returns length more than required
def wo_rolen_ret_len(str_idx, len_idx):
    """A converter for a write only string with a read only length variable, returning the required length for error conditions."""
    return lambda ctx, typespecs: _wo_len_helper(str_idx, len_idx, ctx, typespecs, \
        lambda str_type, str_name, len_type, len_name: (Template("""\
	$len_type ${len_name}_ = $len_name;
	win32u::WSTR ${str_name}_(${len_name}_);
""").substitute(str_name = str_name, len_name = len_name, len_type = len_type), Template("""\
	if(ret) {
		if(! $str_name) {
			ret = ret * 3;
		} else if(${str_name}_.get_utf8_length() <= $len_name) {
			ret = ${str_name}_.get($str_name, $len_name) - 1;
		} else {
			ret = ${str_name}_.get_utf8_length();
		}
	}
""").substitute(str_name = str_name, len_name = len_name)))

def wo_rolen_ret_zero(str_idx, len_idx):
    """A converter for a write only string with a read only length variable, returning 0 for error conditions."""
    return lambda ctx, typespecs: _wo_len_helper(str_idx, len_idx, ctx, typespecs, \
        lambda str_type, str_name, len_type, len_name: (Template("""\
	$len_type ${len_name}_ = $len_name;
	win32u::WSTR ${str_name}_(${len_name}_);
""").substitute(str_name = str_name, len_name = len_name, len_type = len_type), Template("""\
	if(ret) {
		if(${str_name}_.get_utf8_length() <= $len_name) {
			${str_name}_.get($str_name, $len_name);
		} else {
			SetLastError(ERROR_BUFFER_OVERFLOW);
			ret = 0;
		}
	}
""").substitute(str_name = str_name, len_name = len_name)))

def _wo_rolen_ret_buffer_alloc_imp(str_idx, len_idx, ctx, typespecs):
    ctx.desc_self.result_type = 'LPSTR';
    return _wo_len_helper(str_idx, len_idx, ctx, typespecs, \
        lambda str_type, str_name, len_type, len_name: (Template("""\
	$len_type ${len_name}_ = $len_name;
	win32u::WSTR ${str_name}_(${len_name}_);
""").substitute(str_name = str_name, len_name = len_name, len_type = len_type), Template("""\
	LPSTR ret_ = 0;
	if(ret) {
		if($str_name) {
			ret_ = $str_name;
		} else {
			ret_ = (LPSTR)malloc(${str_name}_.get_utf8_length() < $len_name ? $len_name : ${str_name}_.get_utf8_length());
			if(ret_) {
				$len_name = ${str_name}_.get_utf8_length();
			} else {
				errno = ENOMEM;
				ret_ = 0;
			}
		}
		if(${str_name}_.get_utf8_length() <= $len_name) {
			${str_name}_.get(ret_, $len_name);
		} else {
			errno = ERANGE;
			ret_ = 0;
		}
	}
""").substitute(str_name = str_name, len_name = len_name)))

def wo_rolen_ret_buffer_alloc(str_idx, len_idx):
    """A converter for a write only string returned as a result, with a read only length variable.

    If a NULL pointer is specified, the buffer is newly allocated.
    """
    return lambda ctx, typespecs: _wo_rolen_ret_buffer_alloc_imp(str_idx, len_idx, ctx, typespecs)

# FIXME: Free the old buffer.
def ret_alloc(ctx, typespecs):
    """A converter to a function returning a string in a newly allocated buffer."""
    ctx.desc_self.result_type = 'LPSTR';
    return ctx._replace(code_after = ctx.code_after + """\
	DWORD alloc_size = win32u::UTF8Length(ret);
	LPSTR ret_ = (LPSTR)malloc(alloc_size);
	win32u::ToUTF8(ret_, alloc_size, ret);
""")

def forwardA(ctx, typespecs):
    """A converter to forward to SomeFuncA function.

    Type adjustment from LPWSTR to LPSTR is processed.
    """
    ctx.desc_self.parameter_types = map(lambda x: ('LPSTR', x[1]) if x[0] == 'LPWSTR' else x, ctx.desc_self.parameter_types)
    ctx.desc_call.name = ctx.desc_call.name[:-1] + 'A'
    return ctx

def forward(ctx, typespecs):
    """A converter just forwarding. All parameters are kept as they are."""
    return ctx

def _optional_imp(ctx, typespec, args):
    ctx.desc_call.parameter_types.extend(map(lambda x: (x[1], 'optional_' + str(x[0])), enumerate(args)))
    ctx.desc_call.is_variadic = False
    return ctx._replace(code_before = ctx.code_before + Template("""\
	va_list optional_va;
	va_start(optional_va, $name);
""").substitute(name = ctx.desc_self.get_pname(typespec)) + "\n".join(map(lambda x: Template("""\
	$type optional_$idx = va_arg(optional_va, $type);
""").substitute(idx = x[0], type = x[1]), enumerate(args))) + "\n")

def optional(idx, *args):
    """A converter for functions having optional arguments.

    The index to the last non-optional parameter is specified and a list of types for optional arguments follows.
    """
    return lambda ctx, typespecs: _optional_imp(ctx, typespecs[idx], args)

def _fakecp_imp(ctx, typespec_cp, typespec_flag):
    return ctx._replace(code_before = ctx.code_before + Template("""\
	if($cpname == CP_ACP) {
		$cpname = CP_UTF8;
//		$flagname &= WC_ERR_INVALID_CHARS; // Applicable only for Windows Vista and later
		$flagname = 0;
	}
""").substitute(cpname = ctx.desc_self.get_pname(typespec_cp), flagname = ctx.desc_self.get_pname(typespec_flag)))

def fakecp(idx_cp, idx_flag):
    """A converter for MultiByteToWideChar.

    CP_ACP for UINT CodePage is converted to CP_UTF8.
    """
    return lambda ctx, typespecs: _fakecp_imp(ctx, typespecs[idx_cp], typespecs[idx_flag])

def _adjustdef_imp(ctx, typespec_cp, typespec_flag, typespec_def, typespec_used):
    return ctx._replace(code_before = ctx.code_before + Template("""\
	if($cpname == CP_ACP) {
		$cpname = CP_UTF8;
		$flagname &= MB_ERR_INVALID_CHARS;
		if($usedname) {
			*$usedname = FALSE;
			$usedname = 0;
		}
		$defname = 0;
	}
""").substitute(
        cpname = ctx.desc_self.get_pname(typespec_cp),
        flagname = ctx.desc_self.get_pname(typespec_flag),
        defname = ctx.desc_self.get_pname(typespec_def),
        usedname = ctx.desc_self.get_pname(typespec_used)
    ))

def adjustdef(idx_cp, idx_flag, idx_def, idx_used):
    """A converter for WideCharToMulitiByte.

    CP_ACP for UINT CodePage is converted to CP_UTF8.
    In this case, MB_ERR_INVALID_CHARS is dropped and lpDefaultChar and lpUsedDefaultChar are set as 0.
    """
    return lambda ctx, typespecs: _adjustdef_imp(ctx, typespecs[idx_cp], typespecs[idx_flag], typespecs[idx_def], typespecs[idx_used])

def _adjustfilepart_imp(ctx, typespec_buf, typespec_fp):
    index_fp = ctx.desc_self.index_arg(typespec_fp)
    ctx.desc_self.transform_param(index_fp, lambda t,n: ('LPSTR *', n))
    ctx.desc_call.transform_param(index_fp, lambda t,n: (t, n + '_'))
    return ctx._replace(code_before = ctx.code_before + Template("""\
	LPWSTR ${name_fp}__;
	LPWSTR* ${name_fp}_ = &${name_fp}__;
""").substitute(name_fp = ctx.desc_self.get_pname(index_fp)), code_after = ctx.code_after + Template("""\
	if($name_fp) {
		*$name_fp = AdjustFilePart(${name_buf}_, *${name_fp}_, $name_buf);
	}
""").substitute(name_fp = ctx.desc_self.get_pname(index_fp), name_buf = ctx.desc_call.get_pname(typespec_buf).rstrip('_')))
# FIXME: desc_call.get_pname is required

def adjustfilepart(idx_fn, idx_fp):
    """A converter for GetFullPathName"""
    return lambda ctx, typespecs: _adjustfilepart_imp(ctx, typespecs[idx_fn], typespecs[idx_fp])

def _convertenv_imp(ctx, typespec_flag, typespec_env):
    index_env = ctx.desc_self.index_arg(typespec_env)
    ctx.desc_call.transform_param(index_env, lambda t,n: (t, n + '_'))
    return ctx._replace(code_before = ctx.code_before + Template("""\
	extern void ConvertEnvBlock(win32u::scoped_array<WCHAR> &result, LPVOID lpEnv);
	LPVOID ${name_env}_;
	win32u::scoped_array<WCHAR> ${name_env}__;
	if($name_flag & CREATE_UNICODE_ENVIRONMENT) { // already unicode
		${name_env}_ = $name_env;
	} else {
		if($name_env) {
			ConvertEnvBlock(${name_env}__, $name_env);
			${name_env}_ = ${name_env}__.get();
		} else {
			${name_env}_ = 0;
		}
		$name_flag |= CREATE_UNICODE_ENVIRONMENT;
	}
""").substitute(name_flag = ctx.desc_self.get_pname(typespec_env), name_env = ctx.desc_self.get_pname(index_env)))

def convertenv(idx_flag, idx_env):
    """A converter for CreateProcess env block"""
    return lambda ctx, typespecs: _convertenv_imp(ctx, typespecs[idx_flag], typespecs[idx_env])

def updateenv(ctx, typespecs):
    return ctx._replace(code_after = ctx.code_after + '''\
	extern void UpdateEnviron();
	UpdateEnviron();
''')

def _w2u_imp(ctx, typespec):
    index = ctx.desc_self.index_arg(typespec)
    orig_type, orig_name = ctx.desc_self.get_param(index)
    ctx.desc_self.transform_param(index, lambda t,n: (t[:-1] + 'U', n))
    ctx.desc_call.transform_param(index, lambda t,n: (t, n + '_'))
    if orig_type[3:] in ctx.types:
        fields = ctx.types[orig_type[3:]]
    if orig_type[2:] in ctx.types:
        fields = ctx.types[orig_type[2:]]
    if orig_type in ctx.types:
        fields = ctx.types[orig_type]
    fields = [(t,v) for t,v in fields.fields if t == 'LPWSTR' or t == 'LPCWSTR']
    return ctx._replace(code_before = ctx.code_before + Template("""\
	win32u::remove_pointer<$orig_type>::type ${orig_name}__;
	$orig_type ${orig_name}_ = & ${orig_name}__;
	CopyMemory(${orig_name}_, $orig_name, sizeof(${orig_name}__));
$mapper""").substitute(orig_name = orig_name, orig_type = orig_type, mapper = ''.join([Template("""\
	win32u::WSTR ${orig_name}_$field($orig_name -> $field);
	${orig_name}_ -> $field = ${orig_name}_$field;
""").substitute(orig_name = orig_name, field = v) for t,v in fields])))

def w2u(idx):
    """A converter to replace (LPC?)?.*W types with .*U.

    Fields having LPWSTR or LPCWSTR types are set by the pointers to converted WCHAR strings.
    """
    return lambda ctx, typespecs: reduce( \
        lambda acc, x: _w2u_imp(acc, x), \
        map(lambda x: typespecs[x], idx if isinstance(idx, list) else [idx]), \
        ctx \
    )

# Converters for struct

def struct_u2a(ctx):
    """A struct converter to create an alias of struct SomethingA as SomethingU."""
    ctx.types[ctx.desc.name] = ctx.desc
    uname = ctx.desc.name[:-1] + 'U'
    aname = ctx.desc.name[:-1] + 'A'
    return ctx._replace(header = ctx.header + Template('''\
#ifndef $uname
#define $uname $aname
#define LP$uname LP$aname
#define LPC$uname LPC$aname
#endif
''').substitute(uname = uname, aname = aname))
