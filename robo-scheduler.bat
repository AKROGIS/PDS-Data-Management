@echo off
REM Schedules robocopy small X drive from HQ to parks
REM Need to run with administrative privileges
REM Update log path according to available drive/folder
set logpath=c:\logs
REM Usage: robo-park.bat PARK-UNC(destination) PATH (for log file) UNIT(for log file name) PARAMETERS(robocopy)
REM Standard example: robo-park.bat c:\test c:\logs TEST "/R:5 /W:5 /Z /MIR /NP /NFL /NDL /NS /NC /XJ /RH:1800-0600 /PF"

REM For increased logging/output remove some or all of /NDL /NFL /NS /NC /NP 
REM To remove hours restriction remove /RH:1800-0600 /PF

REM Starts all processes without /wait switch concurrently - can use /wait to sequence portions of the robocopy calls, e.g. include a /wait switch after each fifth start command
start /min robo-park.bat c:\test %logpath% TEST "/R:5 /W:5 /Z /MIR /NP /NFL /NDL /NS /NC /XJ /RH:1800-0600 /PF"
start /min robo-park.bat c:\test %logpath% TEST2 "/R:5 /W:5 /Z /MIR /NP /NFL /NDL /NS /NC /XJ /RH:1800-0600 /PF"

REM Robocopy switches
REM /R:5 - retry a file five times
REM /W:5 - wait five seconds between retries
REM   /Z - restartable copy mode (fault tolerant)
REM /MIR - mirror (copy and delete in destination)
REM /TEE - output progress to console and to log
REM  /NP - no progress (overwhelms output)
REM /NFL - no file listing (too much output; may be useful in some cases)
REM /NDL - no directory listing (if running silently at server will reduce log size)
REM /ETA - provides ETA for each file; limited use
REM  /NS - don't log size
REM  /NC - don't log file class
REM  /XJ - don't copy through junctions
REM /COPY:DATSO - copy data, attributes, timestamps, security, owner info (excludes audit info, which causes issues; otherwise same as /COPYALL)
REM /LOG:file - writes log to file
REM /RH:HHMM-HHMM - sets run hours
REM  /PF - check run hours per file
REM Reference: https://ss64.com/nt/robocopy.html