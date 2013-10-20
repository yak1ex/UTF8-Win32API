"""Converter functions"""

def read_only_wo_len_imp(ctx, typespec):
    """
    """
    target_index = ctx.desc_self.index_arg(typespec)
    orig_type, orig_name = ctx.desc_self.parameter_types[target_index]
    ctx.desc_self.parameter_types[target_index] = ('LPCSTR', orig_name)
    ctx.desc_call.parameter_types[target_index] = (orig_type, orig_name + '_')
    code_before_ = ctx.code_before + "\tWSTR %s(%s);\n" % (orig_name + '_', orig_name)
    return ctx._replace(code_before = code_before_)

def read_only_wo_len_idx(idx):
    return lambda ctx, typespecs: reduce( \
        lambda acc, x: read_only_wo_len_imp(acc, x), \
        map(lambda x: typespecs[x], idx if isinstance(idx, list) else [idx]), \
        ctx \
    )

def read_only_wo_len_all(ctx, typespecs):
    return reduce( \
        lambda acc, x: read_only_wo_len_imp(acc, x), \
        typespecs, \
        ctx \
    )

def read_only_wo_len(ctx, typespecs):
    return read_only_wo_len_imp(ctx, typespecs[0]) # for the first type spec

def write_only_wo_len_imp(ctx, typespec):
    """
    """
    target_index = ctx.desc_self.index_arg(typespec)
    orig_type, orig_name = ctx.desc_self.parameter_types[target_index]
    ctx.desc_self.parameter_types[target_index] = ('LPSTR', orig_name)
    ctx.desc_call.parameter_types[target_index] = (orig_type, orig_name + '_')
    before = "\tWSTR %s(MAX_PATH);\n" % (orig_name + '_')
    after = "\t%s.get(%s, MAX_PATH);\n" % (orig_name + '_', orig_name)
    return ctx._replace(code_before = ctx.code_before + before, code_after = ctx.code_after + after)

def write_only_wo_len_idx(idx):
    return lambda ctx, typespecs: reduce( \
        lambda acc, x: write_only_wo_len_imp(acc, x), \
        map(lambda x: typespecs[x], idx if isinstance(idx, list) else [idx]), \
        ctx \
    )

def write_only_wo_len_all(ctx, typespecs):
    return reduce( \
        lambda acc, x: write_only_wo_len_imp(acc, x), \
        typespecs, \
        ctx \
    )

def write_only_wo_len(ctx, typespecs):
    return write_only_wo_len_imp(ctx, typespecs[0]) # for the first type spec


def _write_only_len_helper(str_idx, len_idx, ctx, typespecs, coder):
    str_index = ctx.desc_self.index_arg(typespecs[str_idx])
    len_index = ctx.desc_self.index_arg(typespecs[len_idx])
    orig_str_type, orig_str_name = ctx.desc_self.parameter_types[str_index]
    orig_len_type, orig_len_name = ctx.desc_self.parameter_types[len_index]
    ctx.desc_self.parameter_types[str_index] = ('LPSTR', orig_str_name)
    ctx.desc_call.parameter_types[str_index] = (orig_str_type, orig_str_name + '_')
    ctx.desc_call.parameter_types[len_index] = (orig_len_type, orig_len_name + '_')
    before, after = coder(orig_str_type, orig_str_name, orig_len_type, orig_len_name)
    return ctx._replace(code_before = ctx.code_before + before, code_after = ctx.code_after + after)

def write_only_io_len_ret_bool(str_idx, len_idx):
    """
    """
    return lambda ctx, typespecs: _write_only_len_helper(str_idx, len_idx, ctx, typespecs, \
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

def write_only_i_len_ret_len(str_idx, len_idx):
    """
    """
    return lambda ctx, typespecs: _write_only_len_helper(str_idx, len_idx, ctx, typespecs, \
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

def write_only_i_len_ret_zero(str_idx, len_idx):
    """
    """
    return lambda ctx, typespecs: _write_only_len_helper(str_idx, len_idx, ctx, typespecs, \
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

def write_only_i_len_ret_buffer_alloc_imp(str_idx, len_idx, ctx, typespecs):
    ctx.desc_self.result_type = 'LPSTR';
    return _write_only_len_helper(str_idx, len_idx, ctx, typespecs, \
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

def write_only_i_len_ret_buffer_alloc(str_idx, len_idx):
    return lambda ctx, typespecs: write_only_i_len_ret_buffer_alloc_imp(str_idx, len_idx, ctx, typespecs)

def write_only_wo_len_ret_null_static_imp(size, ctx, typespec):
    ctx.desc_self.result_type = 'LPSTR';
    target_index = ctx.desc_self.index_arg(typespec)
    orig_type, orig_name = ctx.desc_self.parameter_types[target_index]
    ctx.desc_self.parameter_types[target_index] = ('LPSTR', orig_name)
    ctx.desc_call.parameter_types[target_index] = (orig_type, orig_name + '_')
    before = """\
	static char static_buf[%s * 3 + 1];
	WSTR %s(%s);
""" % (size, orig_name + '_', size)
    after = """\
	LPSTR ret_ = 0;
	if(ret) {
		ret_ = %s ? %s : static_buf;
		%s.get(ret_, %s.get_utf8_length()); // Assuming sufficient buffer
	}
""" % (orig_name, orig_name, orig_name + '_', orig_name + '_')
    return ctx._replace(code_before = ctx.code_before + before, code_after = ctx.code_after + after)

def write_only_wo_len_ret_null_static(size, idx):
    """
    """
    return lambda ctx, typespecs: write_only_wo_len_ret_null_static_imp(size if isinstance(size, str) else str(size), ctx, typespecs[idx])

def write_only_i_len_ret_buffer_alloc(str_idx, len_idx):
    return lambda ctx, typespecs: write_only_i_len_ret_buffer_alloc_imp(str_idx, len_idx, ctx, typespecs)

def write_only_wo_len_ret_imp(size, ctx, typespec):
    ctx.desc_self.result_type = 'LPSTR';
    target_index = ctx.desc_self.index_arg(typespec)
    orig_type, orig_name = ctx.desc_self.parameter_types[target_index]
    ctx.desc_self.parameter_types[target_index] = ('LPSTR', orig_name)
    ctx.desc_call.parameter_types[target_index] = (orig_type, orig_name + '_')
    before = """\
	WSTR %s(%s);
""" % (orig_name + '_', size)
    after = """\
	LPSTR ret_ = 0;
	if(ret) {
		ret_ = %s;
		%s.get(ret_, %s.get_utf8_length()); // Assuming sufficient buffer
	}
""" % (orig_name, orig_name + '_', orig_name + '_')
    return ctx._replace(code_before = ctx.code_before + before, code_after = ctx.code_after + after)

def write_only_wo_len_ret(size, idx):
    """
    """
    return lambda ctx, typespecs: write_only_wo_len_ret_imp(size if isinstance(size, str) else str(size), ctx, typespecs[idx])

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
