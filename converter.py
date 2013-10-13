"""Converter functions"""

def read_only_wo_len_imp(args, typespec):
    """
    """
    suffix, desc_self, desc_call, code_before, code_after = args
    target_index = desc_self.index_arg(typespec)
    orig_type, orig_name = desc_self.parameter_types[target_index]
    desc_self.parameter_types[target_index] = ('LPCSTR', orig_name)
    desc_call.parameter_types[target_index] = (orig_type, orig_name + '_')
    code_before += "\tWSTR %s(%s);\n" % (orig_name + '_', orig_name)
    return (suffix, desc_self, desc_call, code_before, code_after)

def read_only_wo_len_idx(idx):
    return lambda args, typespecs: reduce( \
        lambda acc, x: read_only_wo_len_imp(acc, x), \
        map(lambda x: typespecs[x], idx if isinstance(idx, list) else [idx]), \
        args \
    )

def read_only_wo_len_all(args, typespecs):
    return reduce( \
        lambda acc, x: read_only_wo_len_imp(acc, x), \
        typespecs, \
        args \
    )

def read_only_wo_len(args, typespecs):
    return read_only_wo_len_imp(args, typespecs[0]) # for the first type spec

def write_only_wo_len_imp(args, typespec):
    """
    """
    suffix, desc_self, desc_call, code_before, code_after = args
    target_index = desc_self.index_arg(typespec)
    orig_type, orig_name = desc_self.parameter_types[target_index]
    desc_self.parameter_types[target_index] = ('LPSTR', orig_name)
    desc_call.parameter_types[target_index] = (orig_type, orig_name + '_')
    code_before += "\tWSTR %s(MAX_PATH);\n" % (orig_name + '_')
    code_after += "\t%s.get(%s, MAX_PATH);\n" % (orig_name + '_', orig_name)
    return (suffix, desc_self, desc_call, code_before, code_after)

def write_only_wo_len_idx(idx):
    return lambda args, typespecs: reduce( \
        lambda acc, x: write_only_wo_len_imp(acc, x), \
        map(lambda x: typespecs[x], idx if isinstance(idx, list) else [idx]), \
        args \
    )

def write_only_wo_len_all(args, typespecs):
    return reduce( \
        lambda acc, x: write_only_wo_len_imp(acc, x), \
        typespecs, \
        args \
    )

def write_only_wo_len(args, typespecs):
    return write_only_wo_len_imp(args, typespecs[0]) # for the first type spec

def _write_only_len_helper(str_idx, len_idx, args, typespecs, coder):
    suffix, desc_self, desc_call, code_before, code_after = args
    str_index = desc_self.index_arg(typespecs[str_idx])
    len_index = desc_self.index_arg(typespecs[len_idx])
    orig_str_type, orig_str_name = desc_self.parameter_types[str_index]
    orig_len_type, orig_len_name = desc_self.parameter_types[len_index]
    desc_self.parameter_types[str_index] = ('LPSTR', orig_str_name)
    desc_call.parameter_types[str_index] = (orig_str_type, orig_str_name + '_')
    desc_call.parameter_types[len_index] = (orig_len_type, orig_len_name + '_')
    before, after = coder(orig_str_type, orig_str_name, orig_len_type, orig_len_name)
    return (suffix, desc_self, desc_call, code_before + before, code_after + after)

def write_only_io_len_ret_bool_imp(str_idx, len_idx, args, typespecs):
    """
    """
    return _write_only_len_helper(str_idx, len_idx, args, typespecs, \
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

def write_only_io_len_ret_bool(str_idx, len_idx):
    return lambda args, typespecs: write_only_io_len_ret_bool_imp(str_idx, len_idx, args, typespecs)

def write_only_i_len_ret_len_imp(str_idx, len_idx, args, typespecs):
    """
    """
    return _write_only_len_helper(str_idx, len_idx, args, typespecs, \
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

def write_only_i_len_ret_len(str_idx, len_idx):
    return lambda args, typespecs: write_only_i_len_ret_len_imp(str_idx, len_idx, args, typespecs)

def forwardA_all(args, typespecs):
    desc_self = args[1]
    desc_self.parameter_types = map(lambda x: ('LPSTR', x[1]) if x[0] == 'LPWSTR' else x, desc_self.parameter_types)
    return ('A', desc_self, args[2], '', '')
