#ifndef WIN32U_H
#define WIN32U_H

#include <windows.h>
#include <boost/scoped_array.hpp>

class WSTR
{
	DWORD m_size;
	boost::scoped_array<WCHAR> m_wstr;
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
