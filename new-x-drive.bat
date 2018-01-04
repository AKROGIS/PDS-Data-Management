@echo off
cls
REM This script will map the new X drive
echo This will switch your X drive; close any open X:\ files before continuing.
echo Confirm the switch was successful after the script completes. 
echo.
set /p xtype="Enter (Y)es to update: "
IF %xtype%==Y (
  echo Removing X Drive connection
  net use x: /delete /y
  echo Mapping New X Drive
  net use x: \\INPAKROVMDIST\GISData2 /persistent:yes
  explorer.exe x:\
) ELSE IF %xtype%==y (
  echo Removing X Drive connection
  net use x: /delete /y
  echo Mapping New X Drive
  net use x: \\INPAKROVMDIST\GISData2 /persistent:yes
  explorer.exe x:\
) ELSE IF %xtype%==Yes (
  echo Removing X Drive connection
  net use x: /delete /y
  echo Mapping New X Drive
  net use x: \\INPAKROVMDIST\GISData2 /persistent:yes
  explorer.exe x:\
) ELSE IF %xtype%==YES (
  echo Removing X Drive connection
  net use x: /delete /y
  echo Mapping New X Drive
  net use x: \\INPAKROVMDIST\GISData2 /persistent:yes
  explorer.exe x:\
) ELSE (
  echo No change was made.
)
pause