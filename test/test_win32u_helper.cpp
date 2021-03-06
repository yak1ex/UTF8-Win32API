#include <boost/test/auto_unit_test.hpp>
#include <boost/type_traits/is_same.hpp>

#include "helper/win32u_helper.hpp"
#include <iostream>

//const char pszDevJ[] = "\xe9\x96\x8b\xe7\x99\xba";
//const char pszSoftJ[] = "\xe3\x82\xbd\xe3\x83\x95\xe3\x83\x88";
//const char pszTxt[] = "\x23\x74\x78\x74";

const char pszDevJ[] = "\xe9\x96\x8b\xe7\x99\xba";
const char pszJp[] = "\xe9\x96\x8b\xe7\x99\xba\xe3\x82\xbd\xe3\x83\x95\xe3\x83\x88\x2e\x74\x78\x74";
const wchar_t pszDevJW[] = L"x958b\x767a";
const wchar_t pszJpW[] = L"\x958b\x767a\x30bd\x30d5\x30c8\x2e\x74\x78\x74";

using win32u::WSTR;

void test_WSTR_null_(WSTR &ws)
{
	char buf[1024];

	BOOST_CHECK(static_cast<LPWSTR>(ws) == 0); // null pointer comparison
	BOOST_CHECK(static_cast<LPCWSTR>(ws) == 0); // null pointer comparison
	BOOST_CHECK_EQUAL(ws.size(), 0);
	BOOST_CHECK_EQUAL(ws.get_utf8_length(), 0);
	buf[0] = '\xFF';
	BOOST_CHECK_EQUAL(ws.get(NULL, 1024), 0);
	BOOST_CHECK_EQUAL(buf[0], '\xFF');
	BOOST_CHECK_EQUAL(ws.get(buf, sizeof(buf)), 0);
	BOOST_CHECK_EQUAL(buf[0], '\xFF'); // unchanged
	buf[0] = '\xFF';
	BOOST_CHECK_EQUAL(ws.get_truncated(buf, sizeof(buf)), 0);
	BOOST_CHECK_EQUAL(buf[0], '\xFF'); // unchanged
}

BOOST_AUTO_TEST_CASE(test_WSTR_null)
{
	LPCSTR psz = 0;
	WSTR ws(psz); // Just to pass 0 leads ambiguous error
	test_WSTR_null_(ws);
}

BOOST_AUTO_TEST_CASE(test_WSTR_null_with_size)
{
	WSTR ws(0, 1024); // To specify size explicitly should not affect
	test_WSTR_null_(ws);
}

BOOST_AUTO_TEST_CASE(atest_WSTR_zero_as_null)
{
	DWORD dw = 0;
	WSTR ws(dw); // Just to pass 0 leads ambiguous error
	test_WSTR_null_(ws);
}

BOOST_AUTO_TEST_CASE(test_WSTR_null_swap)
{
	char buf[1024];

	LPCSTR psz = 0;
	WSTR ws(psz); // Just to pass 0 leads ambiguous error
	WSTR ws2("Test");

	ws2.swap(ws);

	BOOST_CHECK_EQUAL(lstrcmpW(ws, L"Test"), 0);
	BOOST_CHECK(static_cast<LPWSTR>(ws2) == 0); // null pointer comparison
	BOOST_CHECK(static_cast<LPCWSTR>(ws2) == 0); // null pointer comparison
	BOOST_CHECK_EQUAL(ws2.size(), 0);
	BOOST_CHECK_EQUAL(ws2.get_utf8_length(), 0);
	buf[0] = '\xFF';
	BOOST_CHECK_EQUAL(ws2.get(buf, sizeof(buf)), 0);
	BOOST_CHECK_EQUAL(buf[0], '\xFF'); // unchanged
	buf[0] = '\xFF';
	BOOST_CHECK_EQUAL(ws2.get_truncated(buf, sizeof(buf)), 0);
	BOOST_CHECK_EQUAL(buf[0], '\xFF'); // unchanged

}

void test_WSTR_ascii_(WSTR& ws)
{
	char buf[1024];

	BOOST_CHECK_EQUAL(lstrcmpW(ws, L"Test1"), 0);
	BOOST_CHECK_EQUAL(ws.size(), 6);
	BOOST_CHECK_EQUAL(ws.get_utf8_length(), 6);
	BOOST_CHECK_EQUAL(ws.get(NULL, 1024), 0);
	BOOST_CHECK_EQUAL(ws.get(buf, 4), 0); // ERROR_INSUFFICIENT_BUFFER
	BOOST_CHECK_EQUAL(ws.get(buf, 6), 6); // including terminator
	BOOST_CHECK_EQUAL(lstrcmpA(buf, "Test1"), 0);
	buf[0] = '\0';
	BOOST_CHECK_EQUAL(ws.get(buf, 1024), 6); // including terminator
	BOOST_CHECK_EQUAL(lstrcmpA(buf, "Test1"), 0);
	BOOST_CHECK_EQUAL(ws.get_truncated(buf, 3), 3);
	BOOST_CHECK_EQUAL(lstrcmpA(buf, "Te"), 0);
	int spec[] = { 0, 1, 2, 3, 4, 5, 6, 6, 6 };
	for(std::size_t idx = 0; idx != sizeof(spec) / sizeof(spec[0]); ++idx) {
		BOOST_CHECK_EQUAL(ws.get_truncated(buf, idx), spec[idx]);
	}
}

BOOST_AUTO_TEST_CASE(test_WSTR_ascii)
{
	WSTR ws("Test1");
	test_WSTR_ascii_(ws);
}

BOOST_AUTO_TEST_CASE(test_WSTR_ascii_with_size)
{
	WSTR ws("Test123456", 5);
	test_WSTR_ascii_(ws);
}

BOOST_AUTO_TEST_CASE(test_WSTR_ascii_copy)
{
	WSTR ws("Test1");
	WSTR ws2(ws);

// Deep copy
	BOOST_CHECK_NE(ws, ws2);
	BOOST_CHECK_EQUAL(ws.size(), ws2.size());
	BOOST_CHECK_EQUAL(lstrcmpW(ws, ws2), 0);
}

BOOST_AUTO_TEST_CASE(test_WSTR_ascii_swap)
{
	WSTR ws("Test1");
	WSTR ws2("Test2");

	ws.swap(ws2);

	BOOST_CHECK_EQUAL(lstrcmpW(ws, L"Test2"), 0);
	BOOST_CHECK_EQUAL(lstrcmpW(ws2, L"Test1"), 0);
}

BOOST_AUTO_TEST_CASE(test_WSTR_jp)
{
	char buf[1024];
	WSTR ws(pszJp);

	BOOST_CHECK_EQUAL(lstrcmpW(ws, pszJpW), 0);
	BOOST_CHECK_EQUAL(ws.size(), 10);
	BOOST_CHECK_EQUAL(ws.get_utf8_length(), 20);
	BOOST_CHECK_EQUAL(ws.get(NULL, 1024), 0);
	BOOST_CHECK_EQUAL(ws.get(buf, 19), 0); // ERROR_INSUFFICIENT_BUFFER
	BOOST_CHECK_EQUAL(ws.get(buf, 20), 20); // including terminator
	BOOST_CHECK_EQUAL(lstrcmpA(buf, pszJp), 0);
	buf[0] = '\0';
	BOOST_CHECK_EQUAL(ws.get(buf, 1024), 20); // including terminator
	BOOST_CHECK_EQUAL(lstrcmpA(buf, pszJp), 0);
	BOOST_CHECK_EQUAL(ws.get_truncated(buf, 8), 7);
	BOOST_CHECK_EQUAL(lstrcmpA(buf, pszDevJ), 0);
	int spec[] = { 0, 1, 1, 1, 4, 4, 4, 7, 7, 7, 10, 10, 10, 13, 13, 13, 16, 17, 18, 19, 20, 20, 20 };
	for(std::size_t idx = 0; idx != sizeof(spec) / sizeof(spec[0]); ++idx) {
		BOOST_CHECK_EQUAL(ws.get_truncated(buf, idx), spec[idx]);
	}
}

BOOST_AUTO_TEST_CASE(test_WSTR_extend)
{
	LPSTR psz = NULL;
	WSTR ws(psz);

	BOOST_CHECK_EQUAL(ws.extend(0), 0);
	BOOST_CHECK_GT(ws.extend(1),0);
	DWORD dw = ws.size();
	BOOST_CHECK_EQUAL(ws.extend(1), dw * 2);
	BOOST_CHECK_EQUAL(ws.extend_to(dw), dw * 2);
	BOOST_CHECK_EQUAL(ws.extend_to(dw * 3), dw * 3);

	WSTR ws2(1024);
	BOOST_CHECK_EQUAL(ws2.size(), 1024);
	BOOST_CHECK_EQUAL(ws2.extend(1), 2048);
}

BOOST_AUTO_TEST_CASE(test_remove_pointer)
{
	using boost::is_same;
	using win32u::remove_pointer;

	BOOST_CHECK((is_same<remove_pointer<int>::type, int>::value));
	BOOST_CHECK((is_same<remove_pointer<const int>::type, const int>::value));
	BOOST_CHECK((is_same<remove_pointer<volatile int>::type, volatile int>::value));
	BOOST_CHECK((is_same<remove_pointer<const volatile int>::type, const volatile int>::value));

	BOOST_CHECK((is_same<remove_pointer<int*>::type, int>::value));
	BOOST_CHECK((is_same<remove_pointer<const int*>::type, const int>::value));
	BOOST_CHECK((is_same<remove_pointer<volatile int*>::type, volatile int>::value));
	BOOST_CHECK((is_same<remove_pointer<const volatile int*>::type, const volatile int>::value));

	BOOST_CHECK((is_same<remove_pointer<int&>::type, int&>::value));
	BOOST_CHECK((is_same<remove_pointer<const int&>::type, const int&>::value));
	BOOST_CHECK((is_same<remove_pointer<volatile int&>::type, volatile int&>::value));
	BOOST_CHECK((is_same<remove_pointer<const volatile int&>::type, const volatile int&>::value));

	BOOST_CHECK((is_same<remove_pointer<int*&>::type, int*&>::value));
	BOOST_CHECK((is_same<remove_pointer<const int*&>::type, const int*&>::value));
	BOOST_CHECK((is_same<remove_pointer<volatile int*&>::type, volatile int*&>::value));
	BOOST_CHECK((is_same<remove_pointer<const volatile int*&>::type, const volatile int*&>::value));
}

BOOST_AUTO_TEST_CASE(test_scoped_array)
{
	using win32u::scoped_array;
	scoped_array<char> p;
	BOOST_CHECK(p.get() == 0); // null pointer comparison
	//p.swap(scoped_array<char>(new char[10]()));
	scoped_array<char>(new char[10]()).swap(p);
	BOOST_CHECK(p.get() != 0); // null pointer comparison
	p[0] = 5;
	BOOST_CHECK_EQUAL(p[0], 5);
	{
		const scoped_array<char> & cp = p;
		BOOST_CHECK_EQUAL(cp[0], 5);
	}
}

BOOST_AUTO_TEST_CASE(test_adjust_filepart)
{
	using win32u::AdjustFilePart;
	LPCWSTR pw1 = L"c:\\\xd869\xddf1\xd869\xde1a\\test.txt";
	LPSTR pa1 = "c:\\\xf0\xaa\x97\xb1\xf0\xaa\x98\x9a\\test.txt";
	LPSTR par1 = AdjustFilePart(pw1, pw1 + 8, pa1);
	BOOST_CHECK_EQUAL(*par1, 't');
	BOOST_CHECK_EQUAL(par1 - pa1, 12);
	LPCWSTR pw2 = L"c:\\\x9f5f\x9f6c\\test.txt";
	LPSTR pa2 = "c:\\\xe9\xbd\x9f\xe9\xbd\xac\\test.txt";
	LPSTR par2 = AdjustFilePart(pw2, pw2 + 6, pa2);
	BOOST_CHECK_EQUAL(*par2, 't');
	BOOST_CHECK_EQUAL(par2 - pa2, 10);
}
