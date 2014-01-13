#include <atltime.h>
#include <cstringt.h>
#include <atlimage.h>
#include <atlcomtime.h>
#include <atltypes.h>
#include <atlsimpstr.h>
#include <atlstr.h>
#include <atltime.h>

#include <stdio.h>

int 
main(int argc, char* argv[])
{
	/* string */
	CStringT< char, StrTraitATL< char, ChTraitsCRT< char > > > str;
	str = "hi";
	str += ",independent MFC!\n";
	printf(str);


	/* point size rect */
	CPoint pt;
	CRect rc;
	CSize sz;
	rc.left = rc.top = 0;
	rc.right = rc.bottom = 100;
	sz = rc.Size();
	pt.x = 10;
	pt.y = 10;
	printf("rect(%d, %d, %d, %d):(%d,%d) move (%d, %d)\n",
		rc.left, rc.top, rc.right, rc.bottom, sz.cx, sz.cy, pt.x, pt.y);

	/* time */
	CTime tms;
	CTime tm;
	str.Format("%04d-%02d-%02d %02d:%02d:%02d\n",
		tms.GetYear(), tms.GetMonth(), tms.GetDay(), tm.GetHour(), tm.GetMinute(), tm.GetSecond());
	printf(str);

	CFileTime ft;
	CFileTimeSpan fts;
	COleDateTime dt;
	COleDateTimeSpan dts;

	str.Format("%lld\n", ft.GetTime());
	printf(str);

	/* image */
	CImage image;
	image.Load(L"image.png");
	str.Format("width:%d height%d\n", image.GetWidth(), image.GetHeight());
	printf(str);

	system("pause");
	return 0;
}
