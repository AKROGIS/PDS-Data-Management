@echo off
REM Creates symbolic links for remote servers
REM Need to run with administrative privileges
mklink /D XDrive-KEFJ \\inpkefjvfs\GISData
mklink /D XDrive-YUGA \\inpyugavmgis\GISData
mklink /D XDrive-DENA \\inpdenagis\GIS_Data
mklink /D XDrive-WRST \\INPWRSTvFS01\GIS_Data
mklink /D XDrive-LACL \\INPLACLPAVFS\GIS
mklink /D XDrive-SEAN \\INPGLBAFS03\GISData
mklink /D XDrive-KATM \\inpkatmvfs\GIS
mklink /D XDrive-SITK \\INPSITKvFS\SITK\GISData
mklink /D XDrive-NOME \\INPWEARNOMEvFS\GIS
mklink /D XDrive-KOTZ \\INPWEARKOTZvFS\GIS
mklink /D XDrive-GLBA \\INPGLBAFSPri\GIS
mklink /D XDrive-KENN \\inpwrstkennms\gis_data
mklink /D XDrive-KLGO \\inpklgogis01\akro_gis