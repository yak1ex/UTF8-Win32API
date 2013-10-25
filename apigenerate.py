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
    ['BinaryType', [('LPCWSTR', 'lpApplicationName')], ro_nolen],
    ['lstrcmp', [('LPCWSTR', 'lpString1'), ('LPCWSTR', 'lpString2')], ro_nolen_all],
    ['GetLogicalDriveStrings', [('DWORD', 'nBufferLength'), ('LPWSTR', 'lpBuffer')], forwardA_all],
    ['', [('LPCWSTR', 'lpPathName'), ('LPCWSTR', 'lpPrefixString'), ('LPWSTR', 'lpTempFileName')], [ro_nolen_idx([0,1]), wo_nolen_idx(2)]],
    ['', [('LPCWSTR', 'lpPathName')], ro_nolen_all],
    ['', [('LPCWSTR', 'lpLibFileName')], ro_nolen_all],
    ['', [('LPCWSTR', 'lpExistingFileName'), ('LPCWSTR', 'lpNewFileName')], ro_nolen_all],

# Conversion not yet implemented:
# DWORD GetPrivateProfileStringW(LPCWSTR lpAppName, LPCWSTR lpKeyName, LPCWSTR lpDefault, LPWSTR lpReturnedString, DWORD nSize, LPCWSTR lpFileName)
    ['', [('LPCWSTR', 'lpAppName'), ('LPCWSTR', 'lpKeyName'), ('LPCWSTR', 'lpDefault'), ('LPWSTR', 'lpReturnedString'), ('DWORD', 'nSize'), ('LPCWSTR', 'lpFileName')], None],
# DWORD GetPrivateProfileSectionW(LPCWSTR lpAppName, LPWSTR lpReturnedString, DWORD nSize, LPCWSTR lpFileName)
    ['', [('LPCWSTR', 'lpAppName'), ('LPWSTR', 'lpReturnedString'), ('DWORD', 'nSize'), ('LPCWSTR', 'lpFileName')], None],
# DWORD GetPrivateProfileSectionNamesW(LPWSTR lpszReturnBuffer, DWORD nSize, LPCWSTR lpFileName)
    ['', [('LPWSTR', 'lpszReturnBuffer'), ('DWORD', 'nSize'), ('LPCWSTR', 'lpFileName')], None],

    ['', [('LPCWSTR', 'lpAppName'), ('LPCWSTR', 'lpKeyName'), ('LPCWSTR', 'lpString'), ('LPCWSTR', 'lpFileName')], ro_nolen_all],
    ['', [('LPCWSTR', 'lpAppName'), ('LPCWSTR', 'lpKeyName'), ('LPCWSTR', 'lpFileName')], ro_nolen_all],
    ['', [('LPCWSTR', 'lpAppName'), ('LPCWSTR', 'lpString'), ('LPCWSTR', 'lpFileName')], ro_nolen_all],
    ['', [('LPCWSTR', 'lpUNCServerName'), ('LPCWSTR', 'lpFileName')], ro_nolen_all],
    ['', [('LPCWSTR', 'lpFileName'), ('LPCWSTR', 'lpExistingFileName')], ro_nolen_all],

# Conversion not yet implemented:
# DWORD SearchPathW(LPCWSTR lpPath, LPCWSTR lpFileName, LPCWSTR lpExtension, DWORD nBufferLength, LPWSTR lpBuffer, LPWSTR * lpFilePart)
# DWORD GetFullPathNameU(LPCSTR lpFileName, DWORD nBufferLength, LPWSTR lpBuffer, LPWSTR * lpFilePart)
    ['', [('LPWSTR *', 'lpFilePart')], None],

    ['', [('LPCWSTR', 'lpFileName')], ro_nolen_all],
# ShellMessageBoxW in shlwapi
#   ['', [('LPCWSTR', 'lpcText'), ('LPCWSTR', 'lpcTitle')], ro_nolen_all],
    ['', [('LPCWSTR', 'lpText'), ('LPCWSTR', 'lpCaption')], ro_nolen_all],
    ['', [('LPCWSTR', 'lpOutputString')], ro_nolen_all],
    ['', [('LPWSTR', 'lpBuffer'), ('LPDWORD', 'nSize')], wo_rwlen_ret_bool(0,1)],

    ['', [('LPWSTR', 'lpBuffer'), ('DWORD', 'nBufferLength')], wo_rolen_ret_len(0,1)],
    ['', [('LPWSTR', 'lpBuffer'), ('UINT', 'uSize')], wo_rolen_ret_len(0,1)],

    ['', [('LPCWSTR', 'lpRootPathName'), ('LPWSTR', 'lpVolumeNameBuffer'), ('DWORD', 'nVolumeNameSize'), ('LPWSTR', 'lpFileSystemNameBuffer'), ('DWORD', 'nFileSystemNameSize')], [ro_nolen_idx(0), wo_rolen_ret_zero(1,2), wo_rolen_ret_zero(3,4)]],
    ['', [('LPCWSTR', 'lpRootPathName'), ('LPWSTR', 'lpVolumeNameBuffer'), ('DWORD', 'nVolumeNameSize'), ('LPWSTR', 'lpFileSystemNameBuffer'), ('DWORD', 'nFileSystemNameSize')], None],

    ['', [('LPCWSTR', 'lpRootPathName'), ('LPCWSTR', 'lpVolumeName')], ro_nolen_all],
    ['', [('LPCWSTR', 'lpRootPathName')], ro_nolen_all],

    ['', [('LPCWSTR', 'lpDirectoryName')], ro_nolen_all],
    ['', [('LPCWSTR', 'lpszVolumeMountPoint'), ('LPCWSTR', 'lpszVolueName')], ro_nolen_all],
    ['', [('LPCWSTR', 'lpszRootPathName'), ('LPWSTR', 'lpszVolumeMountPoint'), ('DWORD', 'cchBufferLength')], [ro_nolen_idx(0), wo_rolen_ret_zero(1,2)]],
    ['', [('LPWSTR', 'lpszVolumeMountPoint'), ('DWORD', 'cchBufferLength')], wo_rolen_ret_zero(0,1)],
    ['', [('LPCWSTR', 'lpszVolumeMountPoint'), ('LPWSTR', 'lpszVolumeName'), ('DWORD', 'cchBufferLength')], [ro_nolen_idx(0), wo_rolen_ret_zero(1,2)]],
    ['', [('LPCWSTR', 'lpszVolumeMountPoint')], ro_nolen_all],

    ['', [('LPCWSTR', 'pszRootPath')], ro_nolen_all],

    ['', [('LPWCH', 'lpFilename'), ('DWORD', 'nSize')], wo_rolen_ret_len(0,1)],

    ['', [('LPCWSTR', 'lpModuleName')], ro_nolen_all],

# Conversion not yet implemented:
# LONG RegEnumKeyW(HKEY hKey, DWORD dwIndex, LPWSTR lpName, DWORD cchName)
# LONG RegEnumKeyExW(HKEY hKey, DWORD dwIndex, LPWSTR lpName, LPDWORD lpcchName, LPDWORD lpReserved, LPWSTR lpClass, LPDWORD lpcchClass, PFILETIME lpftLastWriteTime)
# maybe, wo_rwlen_ret_error
    ['', [('LPWSTR', 'lpName'), ('LPDWORD', 'lpcchName'), ('LPWSTR', 'lpClass')], None],
# LONG RegQueryValueW(HKEY hKey, LPCWSTR lpSubKey, LPWSTR lpData, PLONG lpcbData)
# maybe, wo_rwlen_ret_error
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

    ['', [('LPCWSTR', 'lpSubKey'), ('LPWSTR', 'lpClass')], ro_nolen_all],
    ['', [('LPCWSTR', 'lpSubKey'), ('LPCWSTR', 'lpFile')], ro_nolen_all],
    ['', [('LPCWSTR', 'lpSubKey'), ('LPCWSTR', 'lpNewFile'), ('LPCWSTR', 'lpOldFile')], ro_nolen_all],
    ['', [('LPCWSTR', 'lpSubKey')], ro_nolen_all],
    ['', [('LPWSTR', 'lpClass')], ro_nolen_all],
    ['Reg', [('LPCWSTR', 'lpFile')], ro_nolen_all],
    ['Reg', [('LPCWSTR', 'lpMachineName')], ro_nolen_all],
    ['RegDelete', [('LPCWSTR', 'lpValueName')], ro_nolen_all],

    ['', [('LPCWSTR', 'lpszFormat')], ro_nolen_all],
])

index = clang.cindex.Index.create()
tu = index.parse(sys.argv[1])
print 'Translation unit:', tu.spelling
#dump(0, tu.cursor)
for c in tu.cursor.get_children():
    if(c.type.kind.name == "FUNCTIONPROTO" and re.search('W$', c.spelling)):
        desc = FunctionDescriptor(c)
        dispatcher.dispatch(desc)
