#include <windows.h>
#include "win32u_helper.hpp"

#include <iostream>
#include <vector>
#include <map>

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

template<typename T>
static inline unsigned long get_offset(T t)
{
	return reinterpret_cast<unsigned long>(_umain_stub) - reinterpret_cast<unsigned long>(t);
}

template<typename T>
static inline void add_offset(T& t, unsigned long offset)
{
	t = reinterpret_cast<T>(reinterpret_cast<unsigned long>(t) + offset);
}

// GCC in StrawberryPerl 5.18.1.1 32bit seems to have a bug to set wrong addresses for function pointers.
void fix_fptr()
{
	std::map<unsigned long, int> counter;
	++counter[get_offset(ptr_umain)];
	++counter[get_offset(ptr_umain0)];
	++counter[get_offset(ptr_umain1)];
	++counter[get_offset(ptr_umain2)];
	++counter[get_offset(ptr_umain3)];
//	assert(counter.size() == 2);
	unsigned long offset = counter.begin()->second > (++(counter.begin()))->second ? counter.begin()->first : (++(counter.begin()))->first;
	add_offset(ptr_umain, offset);
	add_offset(ptr_umain0, offset);
	add_offset(ptr_umain1, offset);
	add_offset(ptr_umain2, offset);
	add_offset(ptr_umain3, offset);
}

// LPSTR CreateEnvBlock(char cDelim);
// void FreeEnvBlock(LPCSTR);

template<typename T>
static inline bool is_target(T t)
{
	return t != reinterpret_cast<T>(_umain_stub);
}

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

	fix_fptr();
	if(is_target(ptr_umain)) {
		std::cout << "\"C\" _umain()" << std::endl;
		return ptr_umain();
	}
	if(is_target(ptr_umain0)) {
		std::cout << "_umain()" << std::endl;
		return ptr_umain0();
	}
	if(is_target(ptr_umain1)) {
		std::cout << "_umain(int)" << std::endl;
		return ptr_umain1(argc);
	}
	if(is_target(ptr_umain2)) {
		std::cout << "_umain(int, char**)" << std::endl;
		return ptr_umain2(argc, &uargv[0]);
	}
	if(is_target(ptr_umain3)) {
		std::cout << "_umain(int, char**, char**)" << std::endl;
		return ptr_umain3(argc, &uargv[0], 0);
	}
	std::cout << "_umain not defined" << std::endl;
	return -1; // Not reached
}
