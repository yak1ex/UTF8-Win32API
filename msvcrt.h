#define intptr_t int
#include <wchar.h>
intptr_t _uexecv(char const *_Filename,char *const _ArgList[]);
intptr_t _uexecve(const char *_Filename,char *const _ArgList[],char *const _Env[]);
intptr_t _uexecvp(const char *_Filename,char *const _ArgList[]);
intptr_t _uexecvpe(const char *_Filename,char *const _ArgList[],char *const _Env[]);
intptr_t _uspawnv(int,const char *_Filename,char *const _ArgList[]);
intptr_t _uspawnve(int,const char *_Filename,char *const _ArgList[],char *const _Env[]);
intptr_t _uspawnvp(int,const char *_Filename,char *const _ArgList[]);
intptr_t _uspawnvpe(int,const char *_Filename,char *const _ArgList[],char *const _Env[]);
