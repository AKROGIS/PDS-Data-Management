@echo off
REM This script will map the X drive to the test environment on INPAKRO38816
REM Run as local administrator
echo If there are open connections this will not work/refresh; in that case disconnect manually in Windows Explorer, then re-run this to establish test connection.
echo Confirm your X drive source before proceeding with testing or work!!
pause
net use x: /delete /y
net use x: \\INPAKRO38816\GISData2 /persistent:yes
explorer.exe x:\
pause