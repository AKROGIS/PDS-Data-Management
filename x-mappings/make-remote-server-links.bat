@echo off
REM Creates symbolic links for remote servers
REM Need to run with administrative privileges
mklink /D XDrive-AKRTestServer1 \\inpakro42491\GISData
mklink /D XDrive-AKRTestServer2 \\inpakro38816\GISData2
mklink /D XDrive-KEFJ \\inpkefjvfs\GISData
mklink /D XDrive-YUGA \\inpyugavmgis\GISData