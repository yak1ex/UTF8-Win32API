#ifndef MSVCRTU_H
#define MSVCRTU_H

#ifndef __cplusplus
exnter "C" {
#endif

#ifndef UTF8_WIN32_DONT_REPLACE_MSVCRT
#define _access uaccess
#endif
int uaccess(const char* path, int mode);

#ifndef __cplusplus
};
#endif

#endif
