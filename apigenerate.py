#!/usr/bin/env python
""" Usage: call with <filename>
"""

import sys
import re
import clang.cindex
from descriptor import FunctionDescriptor
from dispatcher import APIDispatcher
from converter import *

dispatcher = APIDispatcher()

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

    ['', [('LPCWSTR', 'lpRootPathName'), ('LPWSTR', 'lpVolumeNameBuffer'), ('DWORD', 'nVolumeNameSize'), ('LPWSTR', 'lpFileSystemNameBuffer'), ('DWORD', 'nFileSystemNameSize')], [read_only_wo_len_idx(0), write_only_i_len_ret_zero(1,2), write_only_i_len_ret_zero(3,4)]],
    ['', [('LPCWSTR', 'lpRootPathName'), ('LPWSTR', 'lpVolumeNameBuffer'), ('DWORD', 'nVolumeNameSize'), ('LPWSTR', 'lpFileSystemNameBuffer'), ('DWORD', 'nFileSystemNameSize')], None],

    ['', [('LPCWSTR', 'lpRootPathName'), ('LPCWSTR', 'lpVolumeName')], read_only_wo_len_all],
    ['', [('LPCWSTR', 'lpRootPathName')], read_only_wo_len_all],

    ['', [('LPCWSTR', 'lpDirectoryName')], read_only_wo_len_all],
    ['', [('LPCWSTR', 'lpszVolumeMountPoint'), ('LPCWSTR', 'lpszVolueName')], read_only_wo_len_all],
    ['', [('LPCWSTR', 'lpszRootPathName'), ('LPWSTR', 'lpszVolumeMountPoint'), ('DWORD', 'cchBufferLength')], [read_only_wo_len_idx(0), write_only_i_len_ret_zero(1,2)]],
    ['', [('LPWSTR', 'lpszVolumeMountPoint'), ('DWORD', 'cchBufferLength')], write_only_i_len_ret_zero(0,1)],
    ['', [('LPCWSTR', 'lpszVolumeMountPoint'), ('LPWSTR', 'lpszVolumeName'), ('DWORD', 'cchBufferLength')], [read_only_wo_len_idx(0), write_only_i_len_ret_zero(1,2)]],
    ['', [('LPCWSTR', 'lpszVolumeMountPoint')], read_only_wo_len_all],

    ['', [('LPCWSTR', 'pszRootPath')], read_only_wo_len_all],

    ['', [('LPWCH', 'lpFilename'), ('DWORD', 'nSize')], write_only_i_len_ret_len(0,1)],

    ['', [('LPCWSTR', 'lpModuleName')], read_only_wo_len_all],

# Conversion not yet implemented:
# LONG RegEnumKeyW(HKEY hKey, DWORD dwIndex, LPWSTR lpName, DWORD cchName)
# LONG RegEnumKeyExW(HKEY hKey, DWORD dwIndex, LPWSTR lpName, LPDWORD lpcchName, LPDWORD lpReserved, LPWSTR lpClass, LPDWORD lpcchClass, PFILETIME lpftLastWriteTime)
# maybe, write_only_io_len_ret_error
    ['', [('LPWSTR', 'lpName'), ('LPDWORD', 'lpcchName'), ('LPWSTR', 'lpClass')], None],
# LONG RegQueryValueW(HKEY hKey, LPCWSTR lpSubKey, LPWSTR lpData, PLONG lpcbData)
# maybe, write_only_io_len_ret_error
    ['', [('LPCWSTR', 'lpSubKey'), ('LPWSTR', 'lpData'), ('PLONG', 'lpcbData')], None],
# LONG RegSetValueW(HKEY hKey, LPCWSTR lpSubKey, DWORD dwType, LPCWSTR lpData, DWORD cbData)
# LONG RegSetValueExW(HKEY hKey, LPCWSTR lpValueName, DWORD Reserved, DWORD dwType, BYTE const * lpData, DWORD cbData)
# dwType dependent
    ['', [('LPCWSTR', 'lpSubKey'), ('DWORD', 'dwType'), ('LPCWSTR', 'lpData'), ('DWORD', 'cbData')], None],
# LONG RegQueryValueW(HKEY hKey, LPCWSTR lpSubKey, LPWSTR lpData, PLONG lpcbData)
# LONG RegQueryMultipleValuesW(HKEY hKey, PVALENTW val_list, DWORD num_vals, LPWSTR lpValueBuf, LPDWORD ldwTotsize)
# LONG RegQueryValueExW(HKEY hKey, LPCWSTR lpValueName, LPDWORD lpReserved, LPDWORD lpType, LPBYTE lpData, LPDWORD lpcbData)
# LONG RegEnumValueW(HKEY hKey, DWORD dwIndex, LPWSTR lpValueName, LPDWORD lpcchValueName, LPDWORD lpReserved, LPDWORD lpType, LPBYTE lpData, LPDWORD lpcbData)
# lpType dependent
# LONG RegGetValueW(HKEY hkey, LPCWSTR lpSubKey, LPCWSTR lpValue, DWORD dwFlags, LPDWORD pdwType, PVOID pvData, LPDWORD pcbData)
# pdwType dependent
    ['', [('LPCWSTR', 'lpSubKey'), ('LPCWSTR', 'lpValue'), ('LPDWORD', 'pdwType'), ('PVOID', 'pvData'), ('LPDWORD', 'pcbData')], None],

    ['', [('LPCWSTR', 'lpSubKey'), ('LPWSTR', 'lpClass')], read_only_wo_len_all],
    ['', [('LPCWSTR', 'lpSubKey'), ('LPCWSTR', 'lpFile')], read_only_wo_len_all],
    ['', [('LPCWSTR', 'lpSubKey'), ('LPCWSTR', 'lpNewFile'), ('LPCWSTR', 'lpOldFile')], read_only_wo_len_all],
    ['', [('LPCWSTR', 'lpSubKey')], read_only_wo_len_all],
    ['', [('LPWSTR', 'lpClass')], read_only_wo_len_all],
    ['Reg', [('LPCWSTR', 'lpFile')], read_only_wo_len_all],
    ['Reg', [('LPCWSTR', 'lpMachineName')], read_only_wo_len_all],
    ['RegDelete', [('LPCWSTR', 'lpValueName')], read_only_wo_len_all],

    ['', [('LPCWSTR', 'lpszFormat')], read_only_wo_len_all],
])

index = clang.cindex.Index.create()
tu = index.parse(sys.argv[1])
print 'Translation unit:', tu.spelling
#dump(0, tu.cursor)
for c in tu.cursor.get_children():
    if(c.type.kind.name == "FUNCTIONPROTO" and re.search('W$', c.spelling)):
        desc = FunctionDescriptor(c)
        dispatcher.dispatch(desc)
