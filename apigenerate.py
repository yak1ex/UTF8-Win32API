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
    ['lstrcmp', [('LPCWSTR', 'lpString1'), ('LPCWSTR', 'lpString2')], ro_nolen],
    ['GetLogicalDriveStrings', [('DWORD', 'nBufferLength'), ('LPWSTR', 'lpBuffer')], forwardA],
    ['', [('LPCWSTR', 'lpPathName'), ('LPCWSTR', 'lpPrefixString'), ('LPWSTR', 'lpTempFileName')], [ro_nolen_idx([0,1]), wo_nolen_idx(2)]],
    ['', [('LPCWSTR', 'lpPathName')], ro_nolen],
    ['', [('LPCWSTR', 'lpLibFileName')], ro_nolen],
    ['', [('LPCWSTR', 'lpExistingFileName'), ('LPCWSTR', 'lpNewFileName')], ro_nolen],

# Conversion not yet implemented:
# DWORD GetPrivateProfileStringW(LPCWSTR lpAppName, LPCWSTR lpKeyName, LPCWSTR lpDefault, LPWSTR lpReturnedString, DWORD nSize, LPCWSTR lpFileName)
    ['', [('LPCWSTR', 'lpAppName'), ('LPCWSTR', 'lpKeyName'), ('LPCWSTR', 'lpDefault'), ('LPWSTR', 'lpReturnedString'), ('DWORD', 'nSize'), ('LPCWSTR', 'lpFileName')], None],
# DWORD GetPrivateProfileSectionW(LPCWSTR lpAppName, LPWSTR lpReturnedString, DWORD nSize, LPCWSTR lpFileName)
    ['', [('LPCWSTR', 'lpAppName'), ('LPWSTR', 'lpReturnedString'), ('DWORD', 'nSize'), ('LPCWSTR', 'lpFileName')], None],
# DWORD GetPrivateProfileSectionNamesW(LPWSTR lpszReturnBuffer, DWORD nSize, LPCWSTR lpFileName)
    ['', [('LPWSTR', 'lpszReturnBuffer'), ('DWORD', 'nSize'), ('LPCWSTR', 'lpFileName')], None],

    ['', [('LPCWSTR', 'lpAppName'), ('LPCWSTR', 'lpKeyName'), ('LPCWSTR', 'lpString'), ('LPCWSTR', 'lpFileName')], ro_nolen],
    ['', [('LPCWSTR', 'lpAppName'), ('LPCWSTR', 'lpKeyName'), ('LPCWSTR', 'lpFileName')], ro_nolen],
    ['', [('LPCWSTR', 'lpAppName'), ('LPCWSTR', 'lpString'), ('LPCWSTR', 'lpFileName')], ro_nolen],
    ['', [('LPCWSTR', 'lpUNCServerName'), ('LPCWSTR', 'lpFileName')], ro_nolen],
    ['', [('LPCWSTR', 'lpFileName'), ('LPCWSTR', 'lpExistingFileName')], ro_nolen],

# Conversion not yet implemented:
# DWORD SearchPathW(LPCWSTR lpPath, LPCWSTR lpFileName, LPCWSTR lpExtension, DWORD nBufferLength, LPWSTR lpBuffer, LPWSTR * lpFilePart)
# DWORD GetFullPathNameU(LPCSTR lpFileName, DWORD nBufferLength, LPWSTR lpBuffer, LPWSTR * lpFilePart)
    ['', [('LPWSTR *', 'lpFilePart')], None],
# HANDLE FindFirstFileW(LPCWSTR lpFileName, LPWIN32_FIND_DATAW lpFindFileData)
    ['', [('LPCWSTR', 'lpFileName'), ('LPWIN32_FIND_DATAW', 'lpFindFileData')], None],
    ['', [('LPCWSTR', 'lpFileName')], ro_nolen],
# ShellMessageBoxW in shlwapi
#   ['', [('LPCWSTR', 'lpcText'), ('LPCWSTR', 'lpcTitle')], ro_nolen],
    ['', [('LPCWSTR', 'lpText'), ('LPCWSTR', 'lpCaption')], ro_nolen],
    ['', [('LPCWSTR', 'lpOutputString')], ro_nolen],
    ['GetComputerNameEx', [('LPWSTR', 'lpBuffer'), ('LPDWORD', 'nSize')], wo_rwlen_ret_bool(0,1,'ERROR_MORE_DATA')],
    ['GetComputerName', [('LPWSTR', 'lpBuffer'), ('LPDWORD', 'nSize')], wo_rwlen_ret_bool(0,1,'ERROR_BUFFER_OVERFLOW')],
    ['', [('LPWSTR', 'lpBuffer'), ('LPDWORD', 'pcbBuffer')], wo_rwlen_ret_bool(0,1,'ERROR_INSUFFICIENT_BUFFER')],

    ['', [('LPWSTR', 'lpBuffer'), ('DWORD', 'nBufferLength')], wo_rolen_ret_len(0,1)],
    ['', [('LPWSTR', 'lpBuffer'), ('UINT', 'uSize')], wo_rolen_ret_len(0,1)],

    ['', [('LPCWSTR', 'lpRootPathName'), ('LPWSTR', 'lpVolumeNameBuffer'), ('DWORD', 'nVolumeNameSize'), ('LPWSTR', 'lpFileSystemNameBuffer'), ('DWORD', 'nFileSystemNameSize')], [ro_nolen_idx(0), wo_rolen_ret_zero(1,2), wo_rolen_ret_zero(3,4)]],

    ['', [('LPCWSTR', 'lpRootPathName'), ('LPCWSTR', 'lpVolumeName')], ro_nolen],
    ['', [('LPCWSTR', 'lpRootPathName')], ro_nolen],

    ['', [('LPCWSTR', 'lpDirectoryName')], ro_nolen],
    ['', [('LPCWSTR', 'lpszVolumeMountPoint'), ('LPCWSTR', 'lpszVolueName')], ro_nolen],
    ['', [('LPCWSTR', 'lpszRootPathName'), ('LPWSTR', 'lpszVolumeMountPoint'), ('DWORD', 'cchBufferLength')], [ro_nolen_idx(0), wo_rolen_ret_zero(1,2)]],
    ['', [('LPWSTR', 'lpszVolumeMountPoint'), ('DWORD', 'cchBufferLength')], wo_rolen_ret_zero(0,1)],
    ['', [('LPCWSTR', 'lpszVolumeMountPoint'), ('LPWSTR', 'lpszVolumeName'), ('DWORD', 'cchBufferLength')], [ro_nolen_idx(0), wo_rolen_ret_zero(1,2)]],
    ['', [('LPCWSTR', 'lpszVolumeMountPoint')], ro_nolen],

    ['', [('LPCWSTR', 'pszRootPath'), ('LPSHQUERYRBINFO', 'pSHQueryRBInfo')], None],
    ['', [('LPCWSTR', 'pszRootPath')], ro_nolen],

    ['', [('LPWCH', 'lpFilename'), ('DWORD', 'nSize')], wo_rolen_ret_len(0,1)],

    ['', [('LPCWSTR', 'lpModuleName')], ro_nolen],

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

    ['', [('LPCWSTR', 'lpSubKey'), ('LPWSTR', 'lpClass')], ro_nolen],
    ['', [('LPCWSTR', 'lpSubKey'), ('LPCWSTR', 'lpFile')], ro_nolen],
    ['', [('LPCWSTR', 'lpSubKey'), ('LPCWSTR', 'lpNewFile'), ('LPCWSTR', 'lpOldFile')], ro_nolen],
    ['', [('LPCWSTR', 'lpSubKey')], ro_nolen],
    ['', [('LPWSTR', 'lpClass')], ro_nolen],
    ['Reg', [('LPCWSTR', 'lpFile')], ro_nolen],
    ['Reg', [('LPCWSTR', 'lpMachineName')], ro_nolen],
    ['RegDelete', [('LPCWSTR', 'lpValueName')], ro_nolen],

    ['', [('LPCWSTR', 'lpszFormat')], ro_nolen],

# FIXME: miniperl is compilable but fails to run
    ['MultiByteToWideChar', [('UINT', 'CodePage'), ('DWORD', 'dwFlags')], fakecp(0, 1)],
    ['WideCharToMultiByte', [('UINT', 'CodePage'), ('DWORD', 'dwFlags'), ('LPCCH', 'lpDefaultChar'), ('LPBOOL', 'lpUsedDefaultChar')], adjustdef(0, 1, 2, 3)],
])

index = clang.cindex.Index.create()
tu = index.parse(sys.argv[1])
print 'Translation unit:', tu.spelling
#dump(0, tu.cursor)
for c in tu.cursor.get_children():
    if(c.type.kind.name == "FUNCTIONPROTO" and re.search('W$|WideChar', c.spelling)):
        desc = FunctionDescriptor(c)
        dispatcher.dispatch(desc)
