@echo off
REM Robocopy small X drive from HQ to a Park
REM Need to run with administrative privileges

REM Usage: robo-park.bat PARK-UNC(destination) PATH (for log file) UNIT(for log file name) PARAMETERS(robocopy)

robocopy \\inpakrovmdist\GISData2 %1 %~4 /XD "$RECYCLE.BIN" "System Volume Information" /LOG:%2\update-x-drive-%3.log > %2\update-x-drive-output-%3.log 2>&1

