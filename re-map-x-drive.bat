@echo off
REM This script will map the various X drive sources
echo You may or may not need to disconnect the X drive manually in Windows Explorer and re-run this - check which X you are mapped to and confirm your X drive source before proceeding with testing or work!!
set /p xtype="Enter (N)ew, (T)est, or (O)ld (N,T,or O): "
net use x: /delete /y
IF %xtype%==N (
  echo Mapping New X Drive
  net use x: \\INPAKROVMDIST\GISData2 /persistent:yes
) ELSE IF %xtype%==T (
  echo Mapping Test X drive
  net use x: \\INPAKRO38816\GISData2 /persistent:yes
) ELSE IF %xtype%==O (
  echo Mapping Old X Drive
  net use x: \\INPAKROVMDIST\GISData /persistent:yes
) ELSE (
  echo Run again and select N, T, or O
)
explorer.exe x:\
pause