#include "windowsu.h"

/* TODO: establish test framework */

int main(void)
{
	HANDLE hFile;
	char buf[1024];
	DWORD len;

	DeleteFile("開発.txt");
	OutputDebugString("ユニコードで出力される？");
	MessageBox(NULL, "ユニコードで出力される？", "テスト", MB_OK);

	hFile = CreateFile("ソソソソ開発.txt", GENERIC_WRITE, 0, NULL, CREATE_NEW, 0, NULL);
	CloseHandle(hFile);
	MoveFile("ソソソソ開発.txt", "開発.txt");
	SetFileAttributes("開発.txt", FILE_ATTRIBUTE_HIDDEN);
	len = sizeof(buf);
	if(GetComputerName(buf, &len)) {
		MessageBox(NULL, buf, "GetComputerName", MB_OK);
	}
	if(GetTempPath(sizeof(buf), buf)) {
		MessageBox(NULL, buf, "GetTempPath", MB_OK);
	}
	if(GetWindowsDirectory(buf, sizeof(buf))) {
		MessageBox(NULL, buf, "GetWindowsDirectory", MB_OK);
	}
	{
		ULARGE_INTEGER ui;
		if(GetDiskFreeSpaceEx("C:\\Documents and Settings\\atarashi\\デスクトップ\\files", &ui, NULL, NULL)) {
			wsprintf(buf, "%04X%04X", ui.HighPart, ui.LowPart);
			MessageBox(NULL, buf, "GetDiskFreeSpaceEx", MB_OK);
		}
	}
	{
		MONITORINFOEX mi = { sizeof(MONITORINFOEX) };
		POINT pt = { 0, 0 };
		HMONITOR hMonitor = MonitorFromPoint(pt, MONITOR_DEFAULTTOPRIMARY);
		if(GetMonitorInfo(hMonitor, (MONITORINFO*)&mi)) {
			wsprintf(buf, "%s %d %d %d %d\n", mi.szDevice, mi.rcMonitor.left, mi.rcMonitor.top, mi.rcMonitor.right, mi.rcMonitor.bottom);
			MessageBox(NULL, buf, "GetMonitorInfo", MB_OK);
		}
	}
	SHEmptyRecycleBin(NULL, "C:\\cygwin\\home\\atarashi\\work\\win32u\\ソフト", 0);
	return 0;
}
