@echo off
cls
echo This script will update or create a copy of X drive components.
echo Run using elevated Command Prompt (Admin) if there are permissions errors.
echo If a current drive is available locally use that as the source.
echo Otherwise use the server.
echo.

REM Clear source, set default server source paths
set xsrc=""
set smxsrc=\\inpakrovmdist\GISData2
set lgx1src=\\inpakrovmdist\GISData2\Extras
set lgx1folder=\Extras
set lgx2src=\\inpakrovmdist\GISData2\Source_Data
set lgx2folder=\Source_Data
set parm=
set parm2=
set copyhrs=""
set zb=""

REM Ask user what type of drive to create or update
set /p xtype="Enter SM, LG1 or LG2 for small, large1, or future large2 drive: "
echo.

REM Ask user for source
set /p xsrc="If not using server, enter full source path, e.g. F:\Extras, or Enter: "

REM Provide default server location for source if not otherwise provided
IF %xsrc%=="" ( 
   IF %xtype%==SM (
      set xsrc=%smxsrc%
   ) ELSE IF %xtype%==LG1 (
      set xsrc=%lgx1src%
      ) ELSE IF %xtype%==LG2 (
        set xsrc=%lgx2src%
        ) ELSE (
          echo Choose LG1, LG2 or SM
          exit /b
          )
)
echo.

REM User needs to provide target; we add folder if needed to control case and simplify path entry
set /p xtgt="Enter path of the %xtype% X drive to be updated, e.g. D: or F: "

REM Construct full target path if needed
IF %xtype%==LG1 (
   set xtgtfull=%xtgt%%lgx1folder%
   ) ELSE IF %xtype%==LG2 (
         set xtgtfull=%xtgt%%lgx2folder%
      ) ELSE (
      set xtgtfull=%xtgt%
      )
)
echo.

REM Check if user wants to restrict hours for copying
set /p copyhrs="Enter Y to restrict copying to 6pm-6am, or Enter: "
IF %copyhrs%==Y (
   set parm=/RH:1800-0600 /PF
)
echo.

REM Check if user wants to use fault-tolerant + backup mode (network and file locks)
set /p zb="Enter Y if you expect network or file-lock issues, or Enter: "
IF %zb%==Y (
   set parm2=/ZB
)
echo.

REM It's easy to unintentionally trigger a massive deletion, warn user
echo WARNING: 
echo All content at %xtgtfull% may be removed in this operation! 
echo Source: %xsrc% and Destination: %xtgtfull% 
echo MUST be correct or you may experience DATA LOSS!

REM Last chance to cancel
pause

REM Robocopy with source and destination; switches explained below
@robocopy %xsrc% %xtgtfull% /R:5 /W:5 /MIR /NP /NDL /NS /NC /XJ /XD "$RECYCLE.BIN" "System Volume Information" /LOG:update-x-drive-akr.log %parm% %parm2%

REM Done, prompt user to check for errors
echo Operation completed, check console and log file (update-x-drive-akr.log) for errors (locate and move from C:\Windows\System32 if not run from another location using the Command Prompt (Admin).
pause

REM Robocopy switches
REM /R:5 - retry a file five times
REM /W:5 - wait five seconds between retries
REM   /Z - restartable copy mode (fault tolerant)
REM   /B - backup mode - may be faster than /Z and fewer or no issues with file locks
REM  /ZB - restartable mode, unless locked, then use backup mode
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
