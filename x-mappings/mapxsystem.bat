@echo off
REM Use in conjunction with a scheduled task to map the X drive for the local System account
net use x: \\inpakrovmdist\gisdata2 /persistent:yes