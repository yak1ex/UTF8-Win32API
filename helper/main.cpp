#include <windows.h>
#include "helper/win32u_helper.hpp"

#include <vector>

int _umain_stub()
{
    return 0;
}

extern "C" int _umain(...) __attribute__((weak, alias("_Z11_umain_stubv")));
extern int _umain() __attribute__((weak, alias("_Z11_umain_stubv")));
extern int _umain(int argc) __attribute__((weak, alias("_Z11_umain_stubv")));
extern int _umain(int argc, char ** argv) __attribute__((weak, alias("_Z11_umain_stubv")));
extern int _umain(int argc, char ** argv, char **envp) __attribute__((weak, alias("_Z11_umain_stubv")));

static int(*ptr_umain)(...)                   = static_cast<int(*)(...)>(_umain);
static int(*ptr_umain0)()                     = static_cast<int(*)()>(_umain);
static int(*ptr_umain1)(int)                  = static_cast<int(*)(int)>(_umain);
static int(*ptr_umain2)(int, char**)          = static_cast<int(*)(int, char**)>(_umain);
static int(*ptr_umain3)(int, char**, char**)  = static_cast<int(*)(int, char**, char**)>(_umain);

extern LPSTR* _uenviron;
extern void UpdateEnviron();

template<typename T>
static inline bool is_target(T t)
{
	return t != reinterpret_cast<T>(_umain_stub);
}

int main(void)
{
// NOTE: A static initializer calls CreateEnviron(), thus the below line is not required.
//	UpdateEnviron();

// No arguments
	if(is_target(ptr_umain0)) {
		return ptr_umain0();
	}

// 1 argument
	int argc;
	LPWSTR* argv = CommandLineToArgvW(GetCommandLineW(), &argc);
	if(is_target(ptr_umain1)) {
		return ptr_umain1(argc);
	}

// 2 arguments
	std::vector<std::size_t> uargv_idx;
	std::vector<char> uargv_body;
	int nLen = 0;
	for(int i = 0; i < argc; ++i) {
		uargv_idx.push_back(nLen);
		nLen += win32u::UTF8Length(argv[i]);
	}
	uargv_idx.push_back(nLen);
	uargv_body.reserve(nLen);
	for(int i = 0; i < argc; ++i) {
		uargv_body.resize(uargv_idx[i+1]);
		win32u::ToUTF8(&uargv_body[0] + uargv_idx[i], uargv_idx[i+1] - uargv_idx[i], argv[i]);
	}
	std::vector<char*> uargv;
	for(int i = 0; i < argc; ++i) {
		uargv.push_back(&uargv_body[0] + uargv_idx[i]);
	}
	uargv.push_back(0);
	if(is_target(ptr_umain2)) {
		return ptr_umain2(argc, &uargv[0]);
	}

// 3 arguments
	if(is_target(ptr_umain3)) {
		return ptr_umain3(argc, &uargv[0], _uenviron);
	}
	if(is_target(ptr_umain)) {
		return ptr_umain(argc, &uargv[0], _uenviron);
	}

	return -1; // Not reached
}
