#include "win32u_helper.hpp"
#include "winnls.h"
#include <algorithm> // for std::swap()

namespace win32u {

WSTR::WSTR(LPCSTR str, int len) :
	m_size(str ? MultiByteToWideChar(CP_UTF8, 0, str, len, NULL, 0)
	               + ((len > 0 && str[len - 1] != 0) ? 1 : 0)
	           : 0),
	m_wstr(str ? new WCHAR[m_size] : 0)
{
	if(str) {
		MultiByteToWideChar(CP_UTF8, 0, str, len, m_wstr.get(), m_size);
		m_wstr[m_size - 1] = 0; // force to null-terminate
	}
}

WSTR::WSTR(const WSTR& r) : m_size(r.m_size), m_wstr(r.m_wstr.get() ? new WCHAR[r.m_size] : 0)
{
	if(m_size)
		CopyMemory(m_wstr.get(), r, m_size * sizeof(WCHAR));
}

WSTR::WSTR(DWORD size) : m_size(size), m_wstr(size ? new WCHAR[size] : 0)
{
}

void WSTR::swap(WSTR& r)
{
	std::swap(m_size, r.m_size);
	m_wstr.swap(r.m_wstr);
}

DWORD WSTR::get(LPSTR buffer, DWORD length) const
{
	if(!buffer) return 0;
	if(!m_size) return 0;
	// m_size may not represent correct string length after buffer is written
	// therefore, we use -1 for detecting null terminator
	return WideCharToMultiByte(CP_UTF8, 0, m_wstr.get(), -1, buffer, length, NULL, NULL);
}

DWORD WSTR::get_truncated(LPSTR buffer, DWORD length) const
{
	if(!buffer) return 0;
	if(!m_size) return 0;
	DWORD dwLen = get_utf8_length();
	if(dwLen <= length) return get(buffer, length);

	scoped_array<unsigned char> temp(new unsigned char[dwLen]);
	get(static_cast<LPSTR>(static_cast<void*>(temp.get())), dwLen);

	unsigned char *source = temp.get(), *dest = static_cast<unsigned char*>(static_cast<void*>(buffer)), *terminator = NULL;
	while(length > 0) {
		if((*source & 0xC0) != 0x80) { // first byte
			terminator = dest;
		}
		*dest++ = *source++;
		--length;
	}
	if(terminator) {
		*terminator++ = '\0';
		return static_cast<LPSTR>(static_cast<void*>(terminator)) - buffer;
	} else {
		return 0;
	}
}

DWORD WSTR::get_utf8_length() const
{
	if(!m_size) return 0;
	// m_size may not represent correct string length after buffer is written
	// therefore, we use -1 for detecting null terminator
	return WideCharToMultiByte(CP_UTF8, 0, m_wstr.get(), -1, NULL, 0, NULL, NULL);
}

DWORD WSTR::extend(DWORD times)
{
	if(times == 0) return m_size;
	DWORD new_size = (m_size ? m_size : MAX_PATH) << times; // MAX_PATH is arbitrary selection.
	return extend_to(new_size);
}

DWORD WSTR::extend_to(DWORD new_size)
{
	if(new_size > m_size) {
		WSTR ws(new_size);
		swap(ws);
	}
	return m_size;
}

// NOTE: Sanity check is NOT done
static std::size_t GetOffset(LPCWSTR lpBaseW, LPCWSTR lpFilePartW)
{
	std::size_t result = 0;
	while(lpBaseW != lpFilePartW) {
		if(*lpBaseW < 0xD800U || *lpBaseW > 0xDBFFU) ++result;
		++lpBaseW;
	}
	return result;
}

// NOTE: Sanity check is NOT done
static LPSTR Advance(LPSTR lpBase, std::size_t diff)
{
	while(diff-- != 0) {
		if(*lpBase == 0) break;
		switch(static_cast<unsigned char>(*lpBase) & 0xC0) {
		case 0x00: // ASCII
		case 0x40: // ASCII
			++lpBase;
			break;
		case 0xC0:
			++lpBase;
			// fall through
		case 0x80:
			while((static_cast<unsigned char>(*lpBase) & 0xC0) == 0x80) ++lpBase;
			break;
		}
	}
	return lpBase;
}

LPSTR AdjustFilePart(LPCWSTR lpBaseW, LPCWSTR lpFilePartW, LPSTR lpBase)
{
	return Advance(lpBase, GetOffset(lpBaseW, lpFilePartW));
}

}
