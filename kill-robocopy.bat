@echo off

REM Batch file to kill robocopy processes
REM Run with administrative privileges or taskkill will fail
REM Absolute path for log file recommended, otherwise may be written to C:\Windows\System32 depending upon how batch file is executed
REM Suggested application: schedule to run in the morning

taskkill /f /im Robocopy.exe > kill-robocopy.log 2>&1