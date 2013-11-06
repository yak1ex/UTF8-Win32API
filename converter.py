"""Converter functions"""

from string import Template

def _nolen_helper(target_type, ctx, typespec, coder):
    target_index = ctx.desc_self.index_arg(typespec)
    orig_type, orig_name = ctx.desc_self.parameter_types[target_index]
    ctx.desc_self.parameter_types[target_index] = (target_type, orig_name)
    ctx.desc_call.parameter_types[target_index] = (orig_type, orig_name + '_')
    before, after = coder(orig_type, orig_name)
    return ctx._replace(code_before = ctx.code_before + before, code_after = ctx.code_after + after)

def _ro_nolen_imp(ctx, typespec):
    """
    """
    return _nolen_helper('LPCSTR', ctx, typespec, \
        lambda orig_type, orig_name: (Template("""\
	WSTR ${name}_($name);
""").substitute(name = orig_name), ''))

def ro_nolen_idx(idx):
    return lambda ctx, typespecs: reduce( \
        lambda acc, x: _ro_nolen_imp(acc, x), \
        map(lambda x: typespecs[x], idx if isinstance(idx, list) else [idx]), \
        ctx \
    )

def ro_nolen(ctx, typespecs):
    return reduce( \
        lambda acc, x: _ro_nolen_imp(acc, x), \
        typespecs, \
        ctx \
    )

def _roarray_nolen_imp(ctx, typespec):
    target_index = ctx.desc_self.index_arg(typespec)
    orig_type, orig_name = ctx.desc_self.parameter_types[target_index]
    ctx.desc_self.parameter_types[target_index] = ('LPCSTR const *', orig_name)
    ctx.desc_call.parameter_types[target_index] = (orig_type, orig_name + '_')
    before = Template("""\
	std::vector<LPCWSTR> ${name}_arg;
	std::vector<WSTR> ${name}_hold;
	int ${name}_idx = 0;
	while(1) {
		${name}_hold.push_back(WSTR(${name}[${name}_idx]));
		${name}_arg.push_back(${name}_hold.back());
		if(! ${name}_arg.back()) break;
		++${name}_idx;
	}
	LPCWSTR* ${name}_ = &${name}_arg[0];
""").substitute(name = orig_name)
    return ctx._replace(code_before = ctx.code_before + before)

def roarray_nolen_idx(idx):
    return lambda ctx, typespecs: reduce( \
        lambda acc, x: _roarray_nolen_imp(acc, x), \
        map(lambda x: typespecs[x], idx if isinstance(idx, list) else [idx]), \
        ctx \
    )

def _rova_nolen_imp(ctx, typespec):
    target_index = ctx.desc_self.index_arg(typespec)
    orig_type, orig_name = ctx.desc_self.parameter_types[target_index]
    ctx.desc_self.parameter_types[target_index] = ('LPCSTR', orig_name)
    ctx.desc_call.parameter_types[target_index] = (orig_type, orig_name + '_')
    ctx.desc_call.is_variadic = False
    ctx.desc_call.name = ctx.desc_call.name.replace('l', 'v')
    before = Template("""\
	va_list ${name}_va;
	va_start(${name}_va, $name);
	std::vector<LPCWSTR> ${name}_arg;
	std::vector<WSTR> ${name}_hold;
	do {
		LPSTR p = va_arg(${name}_va, LPSTR);
		${name}_hold.push_back(WSTR(p));
		${name}_arg.push_back(${name}_hold.back());
	} while(${name}_arg.back());
	LPCWSTR* ${name}_ = &${name}_arg[0];
""").substitute(name = orig_name)
    return ctx._replace(code_before = ctx.code_before + before)

def rova_nolen_idx(idx):
    return lambda ctx, typespecs: reduce( \
        lambda acc, x: _rova_nolen_imp(acc, x), \
        map(lambda x: typespecs[x], idx if isinstance(idx, list) else [idx]), \
        ctx \
    )

def _rova_nolen_withenv_imp(ctx, typespec):
    target_index = ctx.desc_self.index_arg(typespec)
    orig_type, orig_name = ctx.desc_self.parameter_types[target_index]
    ctx.desc_self.parameter_types[target_index] = ('LPCSTR', orig_name)
    ctx.desc_call.parameter_types[target_index] = (orig_type, orig_name + '_')
    ctx.desc_call.parameter_types.append(('LPCSTR*', orig_name + '_env_'))
    ctx.desc_call.is_variadic = False
    ctx.desc_call.name = ctx.desc_call.name.replace('l', 'v')
    before = Template("""\
	va_list ${name}_va;
	va_start(${name}_va, $name);
	std::vector<LPCWSTR> ${name}_arg;
	std::vector<WSTR> ${name}_hold;
	do {
		LPSTR p = va_arg(${name}_va, LPSTR);
		${name}_hold.push_back(WSTR(p));
		${name}_arg.push_back(${name}_hold.back());
	} while(${name}_arg.back());
	LPCWSTR* ${name}_ = &${name}_arg[0];

	LPCSTR* ${name}_env = va_arg(${name}_va, LPCSTR*);
	std::vector<LPCWSTR> ${name}_env_arg;
	std::vector<WSTR> ${name}_env_hold;
	int ${name}_env_idx = 0;
	while(1) {
		${name}_env_hold.push_back(WSTR(${name}_env[${name}_env_idx]));
		${name}_env_arg.push_back(${name}_env_hold.back());
		if(! ${name}_env_arg.back()) break;
		++${name}_env_idx;
	}
	LPCWSTR* ${name}_env_ = &${name}_env_arg[0];
""").substitute(name = orig_name)
    return ctx._replace(code_before = ctx.code_before + before)

def rova_nolen_withenv_idx(idx):
    return lambda ctx, typespecs: _rova_nolen_withenv_imp(ctx, typespecs[idx])

def _wo_nolen_imp(ctx, typespec):
    """
    """
    return _nolen_helper('LPSTR', ctx, typespec, \
        lambda orig_type, orig_name: (\
            Template("""\
	WSTR ${name}_(MAX_PATH);
""").substitute(name = orig_name), \
            Template("""\
	${name}_.get($name, MAX_PATH);
""").substitute(name = orig_name)))

def wo_nolen_idx(idx):
    return lambda ctx, typespecs: reduce( \
        lambda acc, x: _wo_nolen_imp(acc, x), \
        map(lambda x: typespecs[x], idx if isinstance(idx, list) else [idx]), \
        ctx \
    )

def wo_nolen(ctx, typespecs):
    return reduce( \
        lambda acc, x: _wo_nolen_imp(acc, x), \
        typespecs, \
        ctx \
    )

def _wo_nolen_ret_null_static_imp(size, ctx, typespec):
    ctx.desc_self.result_type = 'LPSTR';
    return _nolen_helper('LPSTR', ctx, typespec, lambda orig_type, orig_name: (Template("""\
	static char static_buf[$size * 3 + 1];
	WSTR ${name}_($name);
""").substitute(size = size, name = orig_name), Template("""\
	LPSTR ret_ = 0;
	if(ret) {
		ret_ = $name ? $name : static_buf;
		${name}_.get(ret_, ${name}_.get_utf8_length()); // Assuming sufficient buffer
	}
""").substitute(name = orig_name)))

def wo_nolen_ret_null_static(size, idx):
    """
    """
    return lambda ctx, typespecs: _wo_nolen_ret_null_static_imp(size if isinstance(size, str) else str(size), ctx, typespecs[idx])

def wo_rolen_ret_buffer_alloc(str_idx, len_idx):
    return lambda ctx, typespecs: _wo_rolen_ret_buffer_alloc_imp(str_idx, len_idx, ctx, typespecs)

def _wo_nolen_ret_imp(size, ctx, typespec):
    ctx.desc_self.result_type = 'LPSTR';
    return _nolen_helper('LPSTR', ctx, typespec, lambda orig_type, orig_name: (Template("""\
	WSTR ${name}_($size);
""").substitute(size = size, name = orig_name), Template("""\
	LPSTR ret_ = 0;
	if(ret) {
		ret_ = ${name};
		${name}_.get(ret_, ${name}_.get_utf8_length()); // Assuming sufficient buffer
	}
""").substitute(name = orig_name)))

def wo_nolen_ret(size, idx):
    """
    """
    return lambda ctx, typespecs: _wo_nolen_ret_imp(size if isinstance(size, str) else str(size), ctx, typespecs[idx])

def _wo_len_helper(str_idx, len_idx, ctx, typespecs, coder):
    str_index = ctx.desc_self.index_arg(typespecs[str_idx])
    len_index = ctx.desc_self.index_arg(typespecs[len_idx])
    orig_str_type, orig_str_name = ctx.desc_self.parameter_types[str_index]
    orig_len_type, orig_len_name = ctx.desc_self.parameter_types[len_index]
    ctx.desc_self.parameter_types[str_index] = ('LPSTR', orig_str_name)
    ctx.desc_call.parameter_types[str_index] = (orig_str_type, orig_str_name + '_')
    ctx.desc_call.parameter_types[len_index] = (orig_len_type, orig_len_name + '_')
    before, after = coder(orig_str_type, orig_str_name, orig_len_type, orig_len_name)
    return ctx._replace(code_before = ctx.code_before + before, code_after = ctx.code_after + after)

def wo_rwlen_ret_bool(str_idx, len_idx):
    """
    """
    return lambda ctx, typespecs: _wo_len_helper(str_idx, len_idx, ctx, typespecs, \
        lambda orig_str_type, orig_str_name, orig_len_type, orig_len_name: (Template("""\
	WSTR ${str_name}_(*${len_name} * 3 + 1);
	my_remove_pointer<$len_type>::type ${len_name}__ = *$len_name * 3 + 1;
	$len_type ${len_name}_ = &${len_name}__;
""").substitute(str_name = orig_str_name, len_name = orig_len_name, len_type = orig_len_type), Template("""\
	if(${str_name}_.get_utf8_length() <= *$len_name) {
		*$len_name = ${str_name}_.get($str_name, *$len_name);
	} else {
		SetLastError(ERROR_BUFFER_OVERFLOW);
		ret = FALSE;
	}
""").substitute(str_name = orig_str_name, len_name = orig_len_name)))

def wo_rolen_ret_len(str_idx, len_idx):
    """
    """
    return lambda ctx, typespecs: _wo_len_helper(str_idx, len_idx, ctx, typespecs, \
        lambda orig_str_type, orig_str_name, orig_len_type, orig_len_name: (Template("""\
	WSTR ${str_name}_($len_name * 3 + 1);
	$len_type ${len_name}_ = $len_name * 3 + 1;
""").substitute(str_name = orig_str_name, len_name = orig_len_name, len_type = orig_len_type), Template("""\
	if(ret) {
		if(${str_name}_.get_utf8_length() <= $len_name) {
			ret = ${str_name}_.get($str_name, $len_name) - 1;
		} else {
			ret = ${str_name}_.get_utf8_length();
		}
	}
""").substitute(str_name = orig_str_name, len_name = orig_len_name)))

def wo_rolen_ret_zero(str_idx, len_idx):
    """
    """
    return lambda ctx, typespecs: _wo_len_helper(str_idx, len_idx, ctx, typespecs, \
        lambda orig_str_type, orig_str_name, orig_len_type, orig_len_name: (Template("""\
	WSTR ${str_name}_($len_name * 3 + 1);
	$len_type ${len_name}_ = $len_name * 3 + 1;
""").substitute(str_name = orig_str_name, len_name = orig_len_name, len_type = orig_len_type), Template("""\
	if(ret) {
		if(${str_name}_.get_utf8_length() <= $len_name) {
			${str_name}_.get($str_name, $len_name);
		} else {
			SetLastError(ERROR_BUFFER_OVERFLOW);
			ret = 0;
		}
	}
""").substitute(str_name = orig_str_name, len_name = orig_len_name)))

def _wo_rolen_ret_buffer_alloc_imp(str_idx, len_idx, ctx, typespecs):
    ctx.desc_self.result_type = 'LPSTR';
    return _wo_len_helper(str_idx, len_idx, ctx, typespecs, \
        lambda orig_str_type, orig_str_name, orig_len_type, orig_len_name: (Template("""\
	WSTR ${str_name}_($len_name * 3 + 1);
	$len_type ${len_name}_ = $len_name * 3 + 1;
""").substitute(str_name = orig_str_name, len_name = orig_len_name, len_type = orig_len_type), Template("""\
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
""").substitute(str_name = orig_str_name, len_name = orig_len_name)))

def wo_rolen_ret_buffer_alloc(str_idx, len_idx):
    return lambda ctx, typespecs: _wo_rolen_ret_buffer_alloc_imp(str_idx, len_idx, ctx, typespecs)

def ret_alloc(ctx, typespecs):
    """
    """
    ctx.desc_self.result_type = 'LPSTR';
    return ctx._replace(code_after = ctx.code_after + """\
	DWORD alloc_size = UTF8Length(ret);
	LPSTR ret_ = (LPSTR)malloc(alloc_size);
	ToUTF8(ret_, alloc_size, ret);
""")

def forwardA(ctx, typespecs):
    ctx.desc_self.parameter_types = map(lambda x: ('LPSTR', x[1]) if x[0] == 'LPWSTR' else x, ctx.desc_self.parameter_types)
    ctx.desc_call.name = ctx.desc_call.name[:-1] + 'A'
    return ctx

def forward(ctx, typespecs):
    return ctx

def _optional_imp(ctx, typespec, args):
    target_index = ctx.desc_self.index_arg(typespec)
    orig_type, orig_name = ctx.desc_self.parameter_types[target_index]
    ctx.desc_call.parameter_types.extend(map(lambda x: (x[1], 'optional_' + str(x[0])), enumerate(args)))
    ctx.desc_call.is_variadic = False
    return ctx._replace(code_before = ctx.code_before + Template("""\
	va_list optional_va;
	va_start(optional_va, $name);
""").substitute(name = orig_name) + "\n".join(map(lambda x: Template("""\
	$type optional_$idx = va_arg(optional_va, $type);
""").substitute(idx = x[0], type = x[1]), enumerate(args))) + "\n")

def optional(idx, *args):
    return lambda ctx, typespecs: _optional_imp(ctx, typespecs[idx], args)

def _fakecp_imp(ctx, typespec_cp, typespec_flag):
    target_index_cp = ctx.desc_self.index_arg(typespec_cp)
    orig_type_cp, orig_name_cp = ctx.desc_self.parameter_types[target_index_cp]
    target_index_flag = ctx.desc_self.index_arg(typespec_flag)
    orig_type_flag, orig_name_flag = ctx.desc_self.parameter_types[target_index_flag]
    return ctx._replace(code_before = ctx.code_before + Template("""\
	if($cpname == CP_ACP) {
		$cpname = CP_UTF8;
//		$flagname &= WC_ERR_INVALID_CHARS; // Applicable only for Windows Vista and later
		$flagname = 0;
	}
""").substitute(cpname = orig_name_cp, flagname = orig_name_flag))

def fakecp(idx_cp, idx_flag):
    return lambda ctx, typespecs: _fakecp_imp(ctx, typespecs[idx_cp], typespecs[idx_flag])

def _adjustdef_imp(ctx, typespec_cp, typespec_flag, typespec_def, typespec_used):
    target_index_cp = ctx.desc_self.index_arg(typespec_cp)
    orig_type_cp, orig_name_cp = ctx.desc_self.parameter_types[target_index_cp]
    target_index_flag = ctx.desc_self.index_arg(typespec_flag)
    orig_type_flag, orig_name_flag = ctx.desc_self.parameter_types[target_index_flag]
    target_index_def = ctx.desc_self.index_arg(typespec_def)
    orig_type_def, orig_name_def = ctx.desc_self.parameter_types[target_index_def]
    target_index_used = ctx.desc_self.index_arg(typespec_used)
    orig_type_used, orig_name_used = ctx.desc_self.parameter_types[target_index_used]
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
""").substitute(cpname = orig_name_cp, flagname = orig_name_flag, defname = orig_name_def, usedname = orig_name_used))

def adjustdef(idx_cp, idx_flag, idx_def, idx_used):
    return lambda ctx, typespecs: _adjustdef_imp(ctx, typespecs[idx_cp], typespecs[idx_flag], typespecs[idx_def], typespecs[idx_used])
