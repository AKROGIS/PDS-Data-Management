@echo off
REM Batch file to kill robocopy processes
REM Run with administrative privileges or taskkill will fail
REM Suggested application: schedule to run in the morning

REM This block generates a full date and time stamp for log prefixes
REM Remove %fullstamp%- from the log file names in the robocopy statement to have only the log for the most recent run for each remote server
for /f "tokens=2 delims==" %%a in ('wmic OS Get localdatetime /value') do set "dt=%%a"
set "YY=%dt:~2,2%" & set "YYYY=%dt:~0,4%" & set "MM=%dt:~4,2%" & set "DD=%dt:~6,2%"
set "HH=%dt:~8,2%" & set "Min=%dt:~10,2%" & set "Sec=%dt:~12,2%"
set "fullstamp=%YYYY%-%MM%-%DD%_%HH%-%Min%-%Sec%"

taskkill /f /im Robocopy.exe > E:\Xdrive\Logs\%fullstamp%-robo-morning-kill.log 2>&1