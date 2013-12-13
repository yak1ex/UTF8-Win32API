#include <windows.h>
#include "win32u_helper.hpp"

#include <vector>

extern int _umain(...);

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
	return _umain(argc, &uargv[0]);
}
