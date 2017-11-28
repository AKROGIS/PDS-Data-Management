@echo off
REM This script is to set up the new X drive on a park server. Currently it will:
REM 1) Create the Extras junction point
REM 2) Create the GISData2 share for Domain Users
REM 3) Prompt the user to check file permissions
REM Run as admin

REM clear/set variables
set smXloc=""
set lgX1loc=""

REM Uncomment next line to manually set small X drive location if known (w/ trailing slash, e.g. D:\)
REM set smXloc="D:\"

REM If not set ask user
IF %smXloc%=="" (
    set /p smXloc="Enter small X drive location with trailing slash (e.g. D:\):"
)

REM Check defined or user-provided path exists, or exit
IF NOT EXIST "%smXloc%" (
    ECHO %smXloc% not found
    EXIT /B 1
)

REM Uncomment next line to manually set large X drive location if known (w/ trailing slash, e.g. G:\)
REM set lgX1loc="G:\"

REM If not set ask user
IF %lgX1loc%=="" (
    set /p lgX1loc="Enter large X drive location with trailing slash (e.g. G:\):"
)

REM Check defined or user-provided path exists, or exit
IF NOT EXIST "%lgX1loc%" (
    ECHO %lgX1loc% not found
    EXIT /B 1
)

REM Create junction(s) for composite X drive - currently 1) Extras
mklink /j %smXloc%Extras %lgX1loc%Extras

REM Create new share for new X drive (local users will re-map X: to this, and HQ will update to this share)
net share GISData2=%smXloc% /grant:"nps\Domain Users",READ /REMARK:"AKRO GIS X Drive"

REM can add permissions with icacls command, potentially, but good to prompt user to check for other groups; could potentially overwrite all permissions, but that may cause larger issues
Echo Check and set file system permissions on BOTH X drive locations!