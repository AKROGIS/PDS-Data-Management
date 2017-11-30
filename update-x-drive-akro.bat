@echo off
echo This script will update or create a copy of the X drive components for backup or deployment.
echo Run this with administrative privileges.
echo If an updated drive is available locally use that as the source. Otherwise use the server.

REM Clear source, set default server source paths
set xsrc=""
set smxsrc=\\inpakrovmdist\GISData2
set lgx1src=\\inpakrovmdist\GISData2\Extras
set lgx1folder=\Extras
set lgx2src=\\inpakrovmdist\GISData2\Source_Data
set lgx2folder=\Source_Data


REM Ask user what type of drive to create or update
set /p xtype="Enter SM, LG1 or LG2 depending on the type of X drive you are working with: "

REM Ask user for source
set /p xsrc="Enter the source (with folder, if %lgx1folder% or %lgx2folder%) for the %xtype% X drive (no trailing slash), or default server location will be used: "

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

REM User needs to provide target; we add folder if needed to control case and simplify path entry
set /p xtgt="Enter the target (destination) for the %xtype% X drive to be updated (no trailing slash): "

REM Construct full target path if needed
IF %xtype%==LG1 (
   set xtgtfull=%xtgt%%lgx1folder%
   ) ELSE IF %xtype%==LG2 (
         set xtgtfull=%xtgt%%lgx2folder%
      ) ELSE (
      set xtgtfull=%xtgt%
      )
)

REM It's easy to unintentionally trigger a massive deletion, warn user
echo WARNING: 
echo All content at %xtgtfull% may be removed in this operation! 
echo Verify source: %xsrc%
echo If %xsrc% and %xtgtfull% are not exactly correct you may experience near-immediate and total DATA LOSS!

REM Last chance to cancel
pause

REM Robocopy with source and destination; switches explained below
@robocopy %xsrc% %xtgtfull% /R:5 /W:5 /Z /MIR /TEE /NP /NFL /NS /NC /XJ /COPY:DATSO /XD "$RECYCLE.BIN" "System Volume Information" /LOG:update-x-drive-akro.log

REM Done, prompt user to check for errors
echo Operation completed, check console and log file (update-x-drive-akro.log) for errors
pause

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
REM Reference: https://ss64.com/nt/robocopy.html
