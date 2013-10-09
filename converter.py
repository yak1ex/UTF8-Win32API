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

def forwardA_all(args, typespecs):
    desc_self = args[1]
    desc_self.parameter_types = map(lambda x: ('LPSTR', x[1]) if x[0] == 'LPWSTR' else x, desc_self.parameter_types)
    return ('A', desc_self, args[2], '', '')
