#ifndef WIN32U_HELPERI_H
#define WIN32U_HELPERI_H

#ifdef DEBUG

namespace win32u {

template<typename T>
inline const T& dwrap(const T& t) { return t; }

inline const char* dwrap(const char* t) { return t ? t : "(NULL)"; }

inline const char* dwrap(char* t) { return t ? "(maybe OUT)" : "(NULL)"; }

}

#endif

#endif

