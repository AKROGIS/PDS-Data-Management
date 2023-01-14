@echo off
REM Creates symbolic links to remote servers for the robo copy process
REM Needs to be run with administrative privileges
REM This file is typically installed in E:\XDrive\RemoteServers
REM   on the server running the robo copy process.
REM If a Park file server or share name changes, then:
REM   1) Make the changes in this file and commit to the repo
REM   2) Copy the new file to the robo copy server
REM   3) Open up an administrative PowerShell or DOS CMD prompt
REM   4) Delete the old junction e.g. rmdir E:\XDrive\RemoteServers\XDrive-LACL
REM   5) Run this script e.g. E:\XDrive\RemoteServers\make-remote-server-links.bat
REM
mklink /D XDrive-KEFJ \\inpkefjvfs\GISData
mklink /D XDrive-YUGA \\inpyugavmgis\GISData
mklink /D XDrive-DENA \\inpdenagis\GIS_Data
mklink /D XDrive-WRST \\INPWRSTvFS01\GIS_Data
mklink /D XDrive-LACL \\INPLACLvFS\GIS
mklink /D XDrive-SEAN \\INPGLBAFS03\GISData
mklink /D XDrive-KATM \\inpkatmvfs01\GIS
mklink /D XDrive-SITK \\INPSITKvFS\SITK\GISData
mklink /D XDrive-NOME \\INPBELAvFS\GIS
mklink /D XDrive-KOTZ \\INPWEARvFS\GIS
mklink /D XDrive-GLBA \\INPGLBAFSPri\GIS
mklink /D XDrive-KENN \\inpwrstkenn\gis_data
mklink /D XDrive-KLGO \\INPKLGOVMGIS01\akro_gis
