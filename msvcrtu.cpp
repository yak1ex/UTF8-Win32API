#define UTF8_WIN32_DONT_REPLACE_MSVCRT
#include "msvcrtu.h"

#include "win32u_helper.hpp"

#include <wchar.h>

int uaccess(const char *path, int mode)
{
    WSTR path_(path);
    return _waccess(path_, mode);
}
