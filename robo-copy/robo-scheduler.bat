@echo off
REM Schedules robocopy small X drive from HQ to remote servers
REM Need to run with administrative privileges
REM Update log path according to available drive/folder
set logpath=E:\XDrive\Logs
REM Usage: E:\XDrive\UpdateTools\robo-remote-server.bat REMOTE-UNC(destination) PATH (for log file) UNIT(for log file name) PARAMETERS(robocopy)
REM Standard example: E:\XDrive\UpdateTools\robo-remote-server.bat c:\test c:\logs TEST "/R:5 /W:5 /Z /MIR /NDL /NP /NS /NC /XJ /RH:1800-0600 /PF"

REM For increased logging/output remove /NDL and/or /NFL; add in to reduce log size
REM Robo process kicks off at 6pm (18:00), and is killed (if still running) at 6:59
REM To remove hours restriction remove /RH:1800-0600 /PF

REM Starts all processes without /wait switch concurrently - can use /wait to sequence portions of the robocopy calls, e.g. include a /wait switch after each fifth start command
REM start /min CMD /c E:\XDrive\UpdateTools\robo-remote-server.bat E:\Xdrive\RemoteServers\XDrive-AKRTestServer1 %logpath% AKRTest1 "/R:5 /W:5 /Z /MIR /NDL /NP /NS /NC /XJ /XD Local"
REM start /min CMD /c E:\XDrive\UpdateTools\robo-remote-server.bat E:\Xdrive\RemoteServers\XDrive-AKRTestServer2 %logpath% AKRTest2 "/R:5 /W:5 /Z /MIR /NDL /NP /NS /NC /XJ"
start /min CMD /c E:\XDrive\UpdateTools\robo-remote-server.bat E:\XDrive\RemoteServers\XDrive-KEFJ %logpath% KEFJ "/R:5 /W:5 /Z /MIR /NDL /NP /NS /NC /XJ /RH:2200-0600 /PF"
start /min CMD /c E:\XDrive\UpdateTools\robo-remote-server.bat E:\XDrive\RemoteServers\XDrive-YUGA %logpath% YUGA "/R:5 /W:5 /Z /MIR /NDL /NP /NS /NC /XJ /RH:2200-0600 /PF"
start /min CMD /c E:\XDrive\UpdateTools\robo-remote-server.bat E:\XDrive\RemoteServers\XDrive-WRST %logpath% WRST "/R:5 /W:5 /Z /MIR /NDL /NP /NS /NC /XJ /RH:2000-0600 /PF /XD GIS_WRST"
REM /min CMD /c E:\XDrive\UpdateTools\robo-remote-server.bat E:\XDrive\RemoteServers\XDrive-KENN %logpath% KENN "/R:5 /W:5 /Z /MIR /NDL /NP /NS /NC /XJ /RH:1800-0600 /PF /XD GIS_WRST"
start /min CMD /c E:\XDrive\UpdateTools\robo-remote-server.bat E:\XDrive\RemoteServers\XDrive-DENA %logpath% DENA "/R:5 /W:5 /Z /MIR /NDL /NP /NS /NC /XJ /RH:2200-0600 /PF /XD Local Research_Files"
start /min CMD /c E:\XDrive\UpdateTools\robo-remote-server.bat E:\XDrive\RemoteServers\XDrive-LACL %logpath% LACL "/R:5 /W:5 /Z /MIR /NDL /NP /NS /NC /XJ /RH:1800-0600 /PF"
start /min CMD /c E:\XDrive\UpdateTools\robo-remote-server.bat E:\XDrive\RemoteServers\XDrive-KATM %logpath% KATM "/R:5 /W:5 /Z /MIR /NDL /NP /NS /NC /XJ /RH:1800-0600 /PF"
start /min CMD /c E:\XDrive\UpdateTools\robo-remote-server.bat E:\XDrive\RemoteServers\XDrive-SEAN %logpath% SEAN "/R:5 /W:5 /Z /MIR /NDL /NP /NS /NC /XJ /RH:2200-0600 /PF"
start /min CMD /c E:\XDrive\UpdateTools\robo-remote-server.bat E:\XDrive\RemoteServers\XDrive-SITK %logpath% SITK "/R:5 /W:5 /Z /MIR /NDL /NP /NS /NC /XJ /RH:2200-0600 /PF"
start /min CMD /c E:\XDrive\UpdateTools\robo-remote-server.bat E:\XDrive\RemoteServers\XDrive-NOME %logpath% NOME "/R:5 /W:5 /Z /MIR /NDL /NP /NS /NC /XJ /RH:2000-0600 /PF"
start /min CMD /c E:\XDrive\UpdateTools\robo-remote-server.bat E:\XDrive\RemoteServers\XDrive-KOTZ %logpath% KOTZ "/R:5 /W:5 /Z /MIR /NDL /NP /NS /NC /XJ /RH:2000-0600 /PF"
start /min CMD /c E:\XDrive\UpdateTools\robo-remote-server.bat E:\XDrive\RemoteServers\XDrive-KLGO %logpath% KLGO "/R:5 /W:5 /Z /MIR /NDL /NP /NS /NC /XJ /RH:2200-0600 /PF /XD"
start /min CMD /c E:\XDrive\UpdateTools\robo-remote-server.bat E:\XDrive\RemoteServers\XDrive-GLBA %logpath% GLBA "/R:5 /W:5 /Z /MIR /NDL /NP /NS /NC /XJ /RH:2000-0600 /PF /XD GLBA_Local __DFSR_DIAGNOSTICS_TEST_FOLDER__ DfsrPrivate"

REM Robocopy switches
REM /R:5 - retry a file five times
REM /W:5 - wait five seconds between retries
REM   /Z - restartable copy mode (fault tolerant)
REM   /B - backup mode - may be faster than /Z and fewer or no issues with file locks, but requires higher privileges to run
REM  /ZB - restartable mode, unless locked, then use backup mode, but requires higher privileges to run
REM /MIR - mirror (copy and delete in destination)
REM /TEE - output progress to console and to log - hit to up-front performance, overwhelms output, not recommended
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
