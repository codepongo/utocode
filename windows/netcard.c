/**
 @file		netcard.c
 @brief		start or stop network adapter(net card) in windows
 @details	
			> cl /D "_UNICODE" /D "UNICODE" /D"INITGUID" netcard.c
			thanks hmm
 @author	zuohaitao
 @date		2013-04-23
 warning	
 bug		
**/


#include <windows.h>
#include <tchar.h>
#include <locale.h>
#include <Devpkey.h>
#include <Setupapi.h>
#include <Devpropdef.h>
#include <Devguid.h>
#include <assert.h>
#include <Cfgmgr32.h>

#pragma comment(lib, "Setupapi.lib")
//#pragma comment(lib, "Cfgmgr32.lib")

VOID PrintDeviceName(HDEVINFO hDevices, PSP_DEVINFO_DATA pDevice);
BOOL GetDeviceStatus(HDEVINFO hDevices, PSP_DEVINFO_DATA pDevice);
VOID SetDeviceStatus(HDEVINFO hDevices, PSP_DEVINFO_DATA pDevice, BOOL bStatus);

int _tmain(int argc, _TCHAR* argv[])
{
	HDEVINFO hDevices = NULL;

	_tsetlocale(LC_ALL, TEXT("chs_china.936"));

	do 
	{
		LONG i = -1;
		BOOL bStatus;

		hDevices = SetupDiGetClassDevs(&GUID_DEVCLASS_NET, NULL, NULL, DIGCF_PRESENT);
		if (INVALID_HANDLE_VALUE == hDevices)
		{
			break;
		}
		
		while (TRUE)
		{
			BOOL bResult = FALSE;

			SP_DEVINFO_DATA device = {0};

			device.cbSize = sizeof(SP_DEVINFO_DATA);

			bResult = SetupDiEnumDeviceInfo(hDevices, ++i, &device);
			if (!bResult)
			{
				break;
			}

			PrintDeviceName(hDevices, &device);
  
			bStatus = GetDeviceStatus(hDevices, &device);
			if (bStatus)
			{
				printf(" is enabble\n");
			}
			else
			{
				printf(" is disable\n");
			}
			SetDeviceStatus(hDevices, &device, !bStatus); 
		}
	}
	while (FALSE);

	if (NULL != hDevices)
	{
		SetupDiDestroyDeviceInfoList(hDevices);
		hDevices = NULL;
	}

	return 0;
}

VOID PrintDeviceName(HDEVINFO hDevices, PSP_DEVINFO_DATA pDevice)
{
	PWCHAR pszName = NULL;

	if (NULL == hDevices || NULL == pDevice)
	{
		return;
	}

	do 
	{
		DWORD dwBytes = 0;

		BOOL bStatus = FALSE;

		DEVPROPTYPE nType = 0;

		bStatus = SetupDiGetDeviceProperty(
			hDevices, pDevice, 
			&DEVPKEY_NAME, &nType, 
			NULL, 0, 
			&dwBytes, 0);

		if (!bStatus && ERROR_INSUFFICIENT_BUFFER != GetLastError())
		{
			DWORD dwError = GetLastError();
			break;
		}

		pszName = (PWCHAR)HeapAlloc(GetProcessHeap(), HEAP_ZERO_MEMORY, dwBytes + sizeof(WCHAR));
		if (NULL == pszName)
		{
			break;
		}

		bStatus = SetupDiGetDeviceProperty(
			hDevices, pDevice, 
			&DEVPKEY_NAME, &nType, 
			(PBYTE)pszName, dwBytes, 
			&dwBytes, 0);

		if (!bStatus)
		{
			break;
		}

		wprintf(L"%s", pszName);
	}
	while (FALSE);

	if (NULL != pszName)
	{
		HeapFree(GetProcessHeap(), 0, pszName);
		pszName = NULL;
	}
}

BOOL GetDeviceStatus(HDEVINFO hDevices, PSP_DEVINFO_DATA pDevice)
{
	SP_DEVINFO_DATA DevInfoData = {sizeof(SP_DEVINFO_DATA)};
	DWORD dwDevStatus,dwProblem;
	CONFIGRET bResult;	
	bResult = CM_Get_DevNode_Status(&dwDevStatus,&dwProblem,pDevice->DevInst,0);
	assert(bResult == CR_SUCCESS);  
	return (dwProblem != CM_PROB_HARDWARE_DISABLED) && (dwProblem != CM_PROB_DISABLED);  
}

VOID SetDeviceStatus(HDEVINFO hDevices, PSP_DEVINFO_DATA pDevice, BOOL bStatus)
{
	if (NULL == hDevices || NULL == pDevice)
	{
		return;
	}

	do 
	{
		SP_PROPCHANGE_PARAMS parameters = {0};
		PSP_CLASSINSTALL_HEADER pHeader = &parameters.ClassInstallHeader;

		pHeader->cbSize = sizeof(SP_CLASSINSTALL_HEADER);
		pHeader->InstallFunction = DIF_PROPERTYCHANGE;

		parameters.Scope = DICS_FLAG_GLOBAL;
		parameters.StateChange = (bStatus ? DICS_ENABLE : DICS_DISABLE);

		bStatus = SetupDiSetClassInstallParams(hDevices, pDevice, (PSP_CLASSINSTALL_HEADER)&parameters, sizeof(SP_PROPCHANGE_PARAMS));
		if (!bStatus)
		{
			wprintf(L"SetupDiSetClassInstallParams Failure, Error = %d\n", GetLastError());
		}

		bStatus = SetupDiCallClassInstaller(DIF_PROPERTYCHANGE, hDevices, pDevice);
		if (!bStatus)
		{
			wprintf(L"SetupDiCallClassInstaller Failure, Error = %d\n", GetLastError());
		}
	}
	while (FALSE);
}
