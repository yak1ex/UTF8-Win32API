"""Converter functions"""

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
        lambda orig_type, orig_name: ("\tWSTR %s(%s);\n" % (orig_name + '_', orig_name), ''))

def ro_nolen_idx(idx):
    return lambda ctx, typespecs: reduce( \
        lambda acc, x: _ro_nolen_imp(acc, x), \
        map(lambda x: typespecs[x], idx if isinstance(idx, list) else [idx]), \
        ctx \
    )

def ro_nolen_all(ctx, typespecs):
    return reduce( \
        lambda acc, x: _ro_nolen_imp(acc, x), \
        typespecs, \
        ctx \
    )

def ro_nolen(ctx, typespecs):
    return _ro_nolen_imp(ctx, typespecs[0]) # for the first type spec


def _roarray_nolen_imp(ctx, typespec):
    target_index = ctx.desc_self.index_arg(typespec)
    orig_type, orig_name = ctx.desc_self.parameter_types[target_index]
    ctx.desc_self.parameter_types[target_index] = ('LPCSTR*', orig_name)
    ctx.desc_call.parameter_types[target_index] = (orig_type, orig_name + '_')
    before = """\
	std::vector<LPCWSTR> %s_arg;
	std::vector<WSTR> %s_hold;
	int %s_idx = 0;
	while(1) {
		%s_hold.push_back(WSTR(%s[%s_idx]));
		%s_arg.push_back(%s_hold.back());
		if(! %s_arg.back()) break;
		++%s_idx;
	}
	LPCWSTR* %s = &%s_arg[0];
""" % (orig_name, orig_name, orig_name, orig_name, orig_name, orig_name, orig_name, orig_name, orig_name, orig_name, orig_name + '_', orig_name)
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
    before = """\
	va_list %s_va;
	std::vector<LPCWSTR> %s_arg;
	std::vector<WSTR> %s_hold;
	do {
		LPSTR p = va_arg(%s_va, LPSTR);
		%s_hold.push_back(WSTR(p));
		%s_arg.push_back(%s_hold.back());
	} while(%s_arg.back());
	LPCWSTR* %s = &%s_arg[0];
""" % (orig_name, orig_name, orig_name, orig_name, orig_name, orig_name, orig_name, orig_name, orig_name + '_', orig_name)
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
    ctx.desc_call.parameter_types.append(('LPCSTR*', orig_name + '__'))
    ctx.desc_call.is_variadic = False
    ctx.desc_call.name = ctx.desc_call.name.replace('l', 'v')
    before = """\
	va_list %s_va;
	std::vector<LPCWSTR> %s_arg;
	std::vector<WSTR> %s_hold;
	do {
		LPSTR p = va_arg(%s_va, LPSTR);
		%s_hold.push_back(WSTR(p));
		%s_arg.push_back(%s_hold.back());
	} while(%s_arg.back());
	LPCWSTR* %s = &%s_arg[0];

	LPCSTR* %s_env = va_arg(%s_va, LPCSTR*);
	std::vector<LPCWSTR> %s_arg;
	std::vector<WSTR> %s_hold;
	int %s_idx = 0;
	while(1) {
		%s_hold.push_back(WSTR(%s_env[%s_idx]));
		%s_arg.push_back(%s_hold.back());
		if(! %s_arg.back()) break;
		++%s_idx;
	}
	LPCWSTR* %s = &%s_arg[0];
""" % (orig_name, orig_name, orig_name, orig_name, orig_name, orig_name, orig_name, orig_name, orig_name + '_', orig_name, \
        orig_name, orig_name, orig_name + '_', orig_name + '_', orig_name + '_', orig_name + '_', orig_name, orig_name + '_', orig_name + '_', orig_name + '_', orig_name + '_', orig_name + '_', orig_name + '__', orig_name + '_')
    return ctx._replace(code_before = ctx.code_before + before)

def rova_nolen_withenv_idx(idx):
    return lambda ctx, typespecs: _rova_nolen_withenv_imp(ctx, typespecs[idx])

def _wo_nolen_imp(ctx, typespec):
    """
    """
    return _nolen_helper('LPSTR', ctx, typespec, \
        lambda orig_type, orig_name: (\
            "\tWSTR %s(MAX_PATH);\n" % (orig_name + '_'), \
            "\t%s.get(%s, MAX_PATH);\n" % (orig_name + '_', orig_name)))

def wo_nolen_idx(idx):
    return lambda ctx, typespecs: reduce( \
        lambda acc, x: _wo_nolen_imp(acc, x), \
        map(lambda x: typespecs[x], idx if isinstance(idx, list) else [idx]), \
        ctx \
    )

def wo_nolen_all(ctx, typespecs):
    return reduce( \
        lambda acc, x: _wo_nolen_imp(acc, x), \
        typespecs, \
        ctx \
    )

def wo_nolen(ctx, typespecs):
    return _wo_nolen_imp(ctx, typespecs[0]) # for the first type spec

def _wo_nolen_ret_null_static_imp(size, ctx, typespec):
    ctx.desc_self.result_type = 'LPSTR';
    return _nolen_helper('LPSTR', ctx, typespec, lambda orig_type, orig_name: ("""\
	static char static_buf[%s * 3 + 1];
	WSTR %s(%s);
""" % (size, orig_name + '_', size), """\
	LPSTR ret_ = 0;
	if(ret) {
		ret_ = %s ? %s : static_buf;
		%s.get(ret_, %s.get_utf8_length()); // Assuming sufficient buffer
	}
""" % (orig_name, orig_name, orig_name + '_', orig_name + '_')))

def wo_nolen_ret_null_static(size, idx):
    """
    """
    return lambda ctx, typespecs: _wo_nolen_ret_null_static_imp(size if isinstance(size, str) else str(size), ctx, typespecs[idx])

def wo_rolen_ret_buffer_alloc(str_idx, len_idx):
    return lambda ctx, typespecs: _wo_rolen_ret_buffer_alloc_imp(str_idx, len_idx, ctx, typespecs)

def _wo_nolen_ret_imp(size, ctx, typespec):
    ctx.desc_self.result_type = 'LPSTR';
    return _nolen_helper('LPSTR', ctx, typespec, lambda orig_type, orig_name: ("""\
	WSTR %s(%s);
""" % (orig_name + '_', size), """\
	LPSTR ret_ = 0;
	if(ret) {
		ret_ = %s;
		%s.get(ret_, %s.get_utf8_length()); // Assuming sufficient buffer
	}
""" % (orig_name, orig_name + '_', orig_name + '_')))

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
        lambda orig_str_type, orig_str_name, orig_len_type, orig_len_name: ("""\
	WSTR %s(*%s * 3 + 1);
	boost::remove_pointer<%s>::type %s = *%s * 3 + 1;
	%s %s = &%s;
""" % (orig_str_name + '_', orig_len_name, orig_len_type, orig_len_name + '__', orig_len_name, orig_len_type, orig_len_name + '_', orig_len_name + '__'), """\
	if(%s.get_utf8_length() <= *%s) {
		*%s = %s.get(%s, *%s);
	} else {
		SetLastError(ERROR_BUFFER_OVERFLOW);
		ret = FALSE;
	}
""" % (orig_str_name + '_', orig_len_name, orig_len_name, orig_str_name + '_', orig_str_name, orig_len_name)))

def wo_rolen_ret_len(str_idx, len_idx):
    """
    """
    return lambda ctx, typespecs: _wo_len_helper(str_idx, len_idx, ctx, typespecs, \
        lambda orig_str_type, orig_str_name, orig_len_type, orig_len_name: ("""\
	WSTR %s(%s * 3 + 1);
	%s %s = %s * 3 + 1;
""" % (orig_str_name + '_', orig_len_name, orig_len_type, orig_len_name + '_', orig_len_name), """\
	if(ret) {
		if(%s.get_utf8_length() <= %s) {
			ret = %s.get(%s, %s) - 1;
		} else {
			ret = %s.get_utf8_length();
		}
	}
""" % (orig_str_name + '_', orig_len_name, orig_str_name + '_', orig_str_name, orig_len_name, orig_str_name + '_')))

def wo_rolen_ret_zero(str_idx, len_idx):
    """
    """
    return lambda ctx, typespecs: _wo_len_helper(str_idx, len_idx, ctx, typespecs, \
        lambda orig_str_type, orig_str_name, orig_len_type, orig_len_name: ("""\
	WSTR %s(%s * 3 + 1);
	%s %s = %s * 3 + 1;
""" % (orig_str_name + '_', orig_len_name, orig_len_type, orig_len_name + '_', orig_len_name), """\
	if(ret) {
		if(%s.get_utf8_length() <= %s) {
			%s.get(%s, %s);
		} else {
			SetLastError(ERROR_BUFFER_OVERFLOW);
			ret = 0;
		}
	}
""" % (orig_str_name + '_', orig_len_name, orig_str_name + '_', orig_str_name, orig_len_name)))

def _wo_rolen_ret_buffer_alloc_imp(str_idx, len_idx, ctx, typespecs):
    ctx.desc_self.result_type = 'LPSTR';
    return _wo_len_helper(str_idx, len_idx, ctx, typespecs, \
        lambda orig_str_type, orig_str_name, orig_len_type, orig_len_name: ("""\
	WSTR %s(%s * 3 + 1);
	%s %s = %s * 3 + 1;
""" % (orig_str_name + '_', orig_len_name, orig_len_type, orig_len_name + '_', orig_len_name), """\
	LPSTR ret_ = 0;
	if(ret) {
		if(%s) {
			ret_ = %s;
		} else {
			ret_ = (LPSTR)malloc(%s.get_utf8_length() < %s ? %s : %s.get_utf8_length());
			if(ret_) {
				%s = %s.get_utf8_length();
			} else {
				errno = ENOMEM;
				ret_ = 0;
			}
		}
		if(%s.get_utf8_length() <= %s) {
			%s.get(ret_, %s);
		} else {
			errno = ERANGE;
			ret_ = 0;
		}
	}
""" % (orig_str_name, orig_str_name, orig_str_name + '_', orig_len_name, orig_len_name, orig_str_name + '_', orig_len_name, orig_str_name + '_', orig_str_name + '_', orig_len_name, orig_str_name + '_', orig_len_name)))

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

def forwardA_all(ctx, typespecs):
    ctx.desc_self.parameter_types = map(lambda x: ('LPSTR', x[1]) if x[0] == 'LPWSTR' else x, ctx.desc_self.parameter_types)
    ctx.desc_call.name = ctx.desc_call.name[:-1] + 'A'
    return ctx
