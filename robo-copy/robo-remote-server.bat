@echo off
REM Robocopy small X drive from HQ to a remote server
REM Need to run with administrative privileges

REM This block generates a full date and time stamp for log prefixes
REM Remove %fullstamp%- from the log file names in the robocopy statement to have only the log for the most recent run for each remote server
for /f "tokens=2 delims==" %%a in ('wmic OS Get localdatetime /value') do set "dt=%%a"
set "YY=%dt:~2,2%" & set "YYYY=%dt:~0,4%" & set "MM=%dt:~4,2%" & set "DD=%dt:~6,2%"
set "HH=%dt:~8,2%" & set "Min=%dt:~10,2%" & set "Sec=%dt:~12,2%"
set "fullstamp=%YYYY%-%MM%-%DD%_%HH%-%Min%-%Sec%"

REM Usage: robo-remote-server.bat REMOTE-UNC(destination) PATH (for log file) UNIT(for log file name) PARAMETERS(robocopy)

robocopy \\inpakrovmdist\GISData2 %1 %~4 /XD "$RECYCLE.BIN" "System Volume Information" /LOG:%2\%fullstamp%-%3-update-x-drive.log > %2\%fullstamp%-%3-update-x-drive-output.log 2>&1


