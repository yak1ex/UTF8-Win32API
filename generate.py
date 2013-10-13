#!/usr/bin/env python
""" Usage: call with <filename>
"""

import sys
import re
import clang.cindex
from descriptor import FunctionDescriptor
from dispatcher import Dispatcher
from converter import *

# TODO: Need to complete parameter names

dispatcher = Dispatcher()

dispatcher.register([\
    ['BinaryType', [('LPCWSTR', 'lpApplicationName')], read_only_wo_len],
    ['lstrcmp', [('LPCWSTR', 'lpString1'), ('LPCWSTR', 'lpString2')], read_only_wo_len_all],
    ['GetLogicalDriveStrings', [('DWORD', 'nBufferLength'), ('LPWSTR', 'lpBuffer')], forwardA_all],
    ['', [('LPCWSTR', 'lpPathName'), ('LPCWSTR', 'lpPrefixString'), ('LPWSTR', 'lpTempFileName')], [read_only_wo_len_idx([0,1]), write_only_wo_len_idx(2)]],
    ['', [('LPCWSTR', 'lpPathName')], read_only_wo_len_all],
    ['', [('LPCWSTR', 'lpLibFileName')], read_only_wo_len_all],
    ['', [('LPCWSTR', 'lpExistingFileName'), ('LPCWSTR', 'lpNewFileName')], read_only_wo_len_all],

# Conversion not yet implemented:
# DWORD GetPrivateProfileStringW(LPCWSTR lpAppName, LPCWSTR lpKeyName, LPCWSTR lpDefault, LPWSTR lpReturnedString, DWORD nSize, LPCWSTR lpFileName)
    ['', [('LPCWSTR', 'lpAppName'), ('LPCWSTR', 'lpKeyName'), ('LPCWSTR', 'lpDefault'), ('LPWSTR', 'lpReturnedString'), ('DWORD', 'nSize'), ('LPCWSTR', 'lpFileName')], None],
# DWORD GetPrivateProfileSectionW(LPCWSTR lpAppName, LPWSTR lpReturnedString, DWORD nSize, LPCWSTR lpFileName)
    ['', [('LPCWSTR', 'lpAppName'), ('LPWSTR', 'lpReturnedString'), ('DWORD', 'nSize'), ('LPCWSTR', 'lpFileName')], None],
# DWORD GetPrivateProfileSectionNamesW(LPWSTR lpszReturnBuffer, DWORD nSize, LPCWSTR lpFileName)
    ['', [('LPWSTR', 'lpszReturnBuffer'), ('DWORD', 'nSize'), ('LPCWSTR', 'lpFileName')], None],

    ['', [('LPCWSTR', 'lpAppName'), ('LPCWSTR', 'lpKeyName'), ('LPCWSTR', 'lpString'), ('LPCWSTR', 'lpFileName')], read_only_wo_len_all],
    ['', [('LPCWSTR', 'lpAppName'), ('LPCWSTR', 'lpKeyName'), ('LPCWSTR', 'lpFileName')], read_only_wo_len_all],
    ['', [('LPCWSTR', 'lpAppName'), ('LPCWSTR', 'lpString'), ('LPCWSTR', 'lpFileName')], read_only_wo_len_all],
    ['', [('LPCWSTR', 'lpUNCServerName'), ('LPCWSTR', 'lpFileName')], read_only_wo_len_all],
    ['', [('LPCWSTR', 'lpFileName'), ('LPCWSTR', 'lpExistingFileName')], read_only_wo_len_all],

# Conversion not yet implemented:
# DWORD SearchPathW(LPCWSTR lpPath, LPCWSTR lpFileName, LPCWSTR lpExtension, DWORD nBufferLength, LPWSTR lpBuffer, LPWSTR * lpFilePart)
# DWORD GetFullPathNameU(LPCSTR lpFileName, DWORD nBufferLength, LPWSTR lpBuffer, LPWSTR * lpFilePart)
    ['', [('LPWSTR *', 'lpFilePart')], None],

    ['', [('LPCWSTR', 'lpFileName')], read_only_wo_len_all],
    ['', [('LPCWSTR', 'lpcText'), ('LPCWSTR', 'lpcTitle')], read_only_wo_len_all],
    ['', [('LPCWSTR', 'lpText'), ('LPCWSTR', 'lpCaption')], read_only_wo_len_all],
    ['', [('LPCWSTR', 'lpOutputString')], read_only_wo_len_all],
    ['', [('LPWSTR', 'lpBuffer'), ('LPDWORD', 'nSize')], write_only_io_len_ret_bool(0,1)],

    ['', [('LPWSTR', 'lpBuffer'), ('DWORD', 'nBufferLength')], write_only_i_len_ret_len(0,1)],
    ['', [('LPWSTR', 'lpBuffer'), ('UINT', 'uSize')], write_only_i_len_ret_len(0,1)],

# Conversion not yet implemented:
# WINBOOL GetVolumeInformationW(LPCWSTR lpRootPathName, LPWSTR lpVolumeNameBuffer, DWORD nVolumeNameSize, LPDWORD lpVolumeSerialNumber, LPDWORD lpMaximumComponentLength, LPDWORD lpFileSystemFlags, LPWSTR lpFileSystemNameBuffer, DWORD nFileSystemNameSize)
    ['', [('LPCWSTR', 'lpRootPathName'), ('LPWSTR', 'lpVolumeNameBuffer'), ('DWORD', 'nVolumeNameSize'), ('LPWSTR', 'lpFileSystemNameBuffer'), ('DWORD', 'nFileSystemNameSize')], None],

    ['', [('LPCWSTR', 'lpRootPathName'), ('LPCWSTR', 'lpVolumeName')], read_only_wo_len_all],
    ['', [('LPCWSTR', 'lpRootPathName')], read_only_wo_len_all],

    ['', [('LPCWSTR', 'lpDirectoryName')], read_only_wo_len_all],

# Conversion not yet implemented:
# HANDLE FindFirstVolumeMountPointW(LPCWSTR lpszRootPathName, LPWSTR lpszVolumeMountPoint, DWORD cchBufferLength)
#    ['', [('LPCWSTR', 'pszRootPath'), ('LPWSTR', 'lpszVolumeMountPoint')], [read_only_wo_len_idx(0), ]],
    ['', [('LPCWSTR', 'pszRootPath'), ('LPWSTR', 'lpszVolumeMountPoint')], None],
    ['', [('LPCWSTR', 'pszRootPath')], read_only_wo_len_all],
])

index = clang.cindex.Index.create()
tu = index.parse(sys.argv[1])
print 'Translation unit:', tu.spelling
#dump(0, tu.cursor)
for c in tu.cursor.get_children():
    if(c.type.kind.name == "FUNCTIONPROTO" and re.search('W$', c.spelling)):
        desc = FunctionDescriptor(c)
        dispatcher.dispatch(desc)
