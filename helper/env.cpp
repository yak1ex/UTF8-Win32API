#include <windows.h>
#include "helper/win32u_helper.hpp"

#include <vector>

LPSTR* CreateEnviron()
{
	std::vector<std::size_t> env_idx;
	WCHAR* env = GetEnvironmentStringsW();
	WCHAR* env_orig = env;
	std::size_t len = 0;
	while(*env != 0) {
		env_idx.push_back(len);
		len += win32u::UTF8Length(env);
		while(*++env != 0) ;
		++env;
	}
	env_idx.push_back(len);
	char* top = new char[sizeof(LPSTR) * env_idx.size() + len];
	char** result = static_cast<char**>(static_cast<void*>(top));
	char** result_temp = result;
	top += sizeof(LPSTR) * env_idx.size();
	env = env_orig;
	std::size_t i = 0;
	while(*env != 0) {
		*result_temp++ = top + env_idx[i];
		win32u::ToUTF8(top + env_idx[i], env_idx[i+1] - env_idx[i], env);
		while(*++env != 0) ;
		++env; ++i;
	}
	*result_temp = 0;
	FreeEnvironmentStringsW(env_orig);
	return result;
}

void FreeEnviron(LPSTR *p)
{
	delete[] p;
}

void ConvertEnvBlock(win32u::scoped_array<WCHAR> &result, LPVOID lpEnv)
{
	char *p = static_cast<char*>(lpEnv), *p_ = p;
	std::size_t len = 0;
	while(*p) {
		len += MultiByteToWideChar(CP_UTF8, 0, p, -1, NULL, 0);
		while(*++p != 0) ;
		++p;
	}
	win32u::scoped_array<WCHAR> dest(new WCHAR[len + 1]);
	LPWSTR p_dest = dest.get();
	p = p_;
	while(*p) {
		p_dest += MultiByteToWideChar(CP_UTF8, 0, p, -1, p_dest, len + 1 - (p_dest - dest.get()));
		while(*++p != 0) ;
		++p;
	}
	*p_dest = 0;
	dest.swap(result);
}
