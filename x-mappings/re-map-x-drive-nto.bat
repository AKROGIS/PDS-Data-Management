@echo off
cls
REM This script will map to the various X drive sources
echo This will switch your X drive; close any open X:\ files before continuing.
echo Confirm the switch was successful after the script completes. 
echo.
set /p xtype="Enter (N)ew, (T1)est, (T2)est, or (O)ld (N, T1, T2, or O): "
IF %xtype%==N (
  echo Removing X Drive connection
  net use x: /delete /y
  echo Mapping New X Drive
  net use x: \\INPAKROVMDIST\GISData2 /persistent:yes
  explorer.exe x:\
) ELSE IF %xtype%==T1 (
  echo Removing X Drive connection
  net use x: /delete /y
  echo Mapping Test1 X drive
  net use x: \\INPAKRO42491\GISData /persistent:yes
  explorer.exe x:\
) ELSE IF %xtype%==T2 (
  echo Removing X Drive connection
  net use x: /delete /y
  echo Mapping Test2 X drive
  net use x: \\INPAKRO38816\GISData2 /persistent:yes
  explorer.exe x:\
) ELSE IF %xtype%==O (
  echo Removing X Drive connection
  net use x: /delete /y
  echo Mapping Old X Drive
  net use x: \\INPAKROVMDIST\GISData /persistent:yes
  explorer.exe x:\
) ELSE (
  echo Run again and select N, T1, T2, or O
)
pause