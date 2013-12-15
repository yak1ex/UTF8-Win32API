#include <windows.h>
#include "win32u_helper.hpp"

#include <iostream>
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

// LPSTR CreateEnvBlock(char cDelim);
// void FreeEnvBlock(LPCSTR);

int main(void)
{
	int argc;
	LPWSTR* argv = CommandLineToArgvW(GetCommandLineW(), &argc);
	std::vector<std::size_t> uargv_idx;
	std::vector<char> uargv_body;
	int nLen = 0;
	for(int i = 0; i < argc; ++i) {
		uargv_idx.push_back(nLen);
		nLen += UTF8Length(argv[i]);
	}
	uargv_idx.push_back(nLen);
	uargv_body.reserve(nLen);
	for(int i = 0; i < argc; ++i) {
		uargv_body.resize(uargv_idx[i+1]);
		ToUTF8(&uargv_body[0] + uargv_idx[i], uargv_idx[i+1] - uargv_idx[i], argv[i]);
	}
	std::vector<char*> uargv;
	for(int i = 0; i < argc; ++i) {
		uargv.push_back(&uargv_body[0] + uargv_idx[i]);
	}
	uargv.push_back(0);
	// TODO: env

	if(static_cast<int(*)(...)>(_umain) != reinterpret_cast<int(*)(...)>(_umain_stub)) {
		std::cout << "\"C\" _umain()" << std::endl;
		return static_cast<int(*)(...)>(_umain)();
	}
	if(static_cast<int(*)()>(_umain) != reinterpret_cast<int(*)()>(_umain_stub)) {
		std::cout << "_umain()" << std::endl;
		return static_cast<int(*)()>(_umain)();
	}
	if(static_cast<int(*)(int)>(_umain) != reinterpret_cast<int(*)(int)>(_umain_stub)) {
		std::cout << "_umain(int)" << std::endl;
		return static_cast<int(*)(int)>(_umain)(argc);
	}
	if(static_cast<int(*)(int,char**)>(_umain) != reinterpret_cast<int(*)(int,char**)>(_umain_stub)) {
		std::cout << "_umain(int, char**)" << std::endl;
		return static_cast<int(*)(int,char**)>(_umain)(argc, &uargv[0]);
	}
	if(static_cast<int(*)(int,char**,char**)>(_umain) != reinterpret_cast<int(*)(int,char**,char**)>(_umain_stub)) {
		std::cout << "_umain(int, char**,char**)" << std::endl;
		return static_cast<int(*)(int,char**,char**)>(_umain)(argc, &uargv[0], 0);
	}
	std::cout << "_umain not defined" << std::endl;
	return -1; // Not reached
}
