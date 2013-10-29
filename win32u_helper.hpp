#ifndef WIN32U_H
#define WIN32U_H

#include <algorithm>
#include <windows.h>

template<typename T>
struct my_remove_pointer
{
	typedef T type;
};

template<typename T>
struct my_remove_pointer<T*>
{
	typedef T type;
};

template<typename T>
class my_scoped_array
{
	T *m;
	my_scoped_array(const my_scoped_array&);
	my_scoped_array& operator=(const my_scoped_array&);
public:
	my_scoped_array(T *p = 0) : m(p) {}
	~my_scoped_array() { delete[] m; }
	T* get() { return m; }
	const T* get() const { return m; }
	T& operator[](std::size_t idx) { return m[idx]; }
	const T& operator[](std::size_t idx) const { return m[idx]; }
	void swap(my_scoped_array& other) { std::swap(m, other.m); }
};

class WSTR
{
	DWORD m_size;
	my_scoped_array<WCHAR> m_wstr;
public:
	explicit WSTR(LPCSTR str, int len = -1);
	WSTR(const WSTR& r);
	explicit WSTR(DWORD size = MAX_PATH);
	WSTR& operator=(WSTR r) { swap(r); return *this; }
//	~WSTR();
	operator LPWSTR() { return m_wstr.get(); }
	operator LPCWSTR() const { return m_wstr.get(); }
	void swap(WSTR& r);
	DWORD get(LPSTR, DWORD) const;
	DWORD get_truncated(LPSTR, DWORD) const;
	DWORD get_utf8_length() const;
	DWORD size() const { return m_size; }
	DWORD extend(DWORD times = 1);
	DWORD extend_to(DWORD new_size);
};

inline DWORD ToUTF8(LPSTR buffer, DWORD length, LPWSTR ws)
{
	return WideCharToMultiByte(CP_UTF8, 0, ws, -1, buffer, length, NULL, NULL);
}

inline DWORD UTF8Length(LPWSTR ws)
{
	return WideCharToMultiByte(CP_UTF8, 0, ws, -1, NULL, 0, NULL, NULL);
}


#endif
