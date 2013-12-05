#include <boost/test/auto_unit_test.hpp>

#include "windowsu.h"
#include "msvcrtu.h"

BOOST_AUTO_TEST_CASE(test_file)
{
	HANDLE hFile = CreateFile("ソソソソ開発.txt", GENERIC_WRITE, 0, NULL, CREATE_NEW, 0, NULL);
	BOOST_CHECK(hFile != INVALID_HANDLE_VALUE);
	BOOST_CHECK(CloseHandle(hFile));
	BOOST_CHECK(MoveFile("ソソソソ開発.txt", "開発.txt"));
	struct _stat st;
	BOOST_CHECK(_stat("開発.txt", &st) == 0);
	BOOST_CHECK(SetFileAttributes("開発.txt", FILE_ATTRIBUTE_HIDDEN));
	BOOST_CHECK(DeleteFile("開発.txt"));
	BOOST_CHECK(_stat("開発.txt", &st));
}

BOOST_AUTO_TEST_CASE(test_query_fs)
{
	char buf[1024];

	DWORD ret = GetTempPath(sizeof(buf), buf);
	BOOST_CHECK(ret <= sizeof(buf));
	if(ret <= sizeof(buf)) {
		BOOST_TEST_MESSAGE("GetTempPath(): " << buf);
	}
	UINT ret2 = GetWindowsDirectory(buf, sizeof(buf));
	BOOST_CHECK(ret2 <= sizeof(buf));
	if(ret2 <= sizeof(buf)) {
		BOOST_TEST_MESSAGE("GetWindowsDirectory(): " << buf);
	}
}

// GetDiskFreeSpaceEx
// SHEmptyRecycleBin
