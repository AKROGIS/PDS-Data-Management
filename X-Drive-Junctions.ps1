# Script to create junction(s) on park server to create composite X drive using local paths
# v0.1 2017-11-20
# References: the internet

"Note the location of the internal X drive and the external X drive before proceeding"
"This step is critical to a complete X drive"

# Suggest internal drive letters, can be removed if not helpful; may also be tailored per park
"Internal drive letters may include:"
GET-WMIOBJECT –query "SELECT * from win32_logicaldisk where DriveType = '3'" | %{$_.deviceid}
$smX = Read-Host -Prompt 'Enter the path of the internal X drive'

# Suggest external drive letters, can be removed if not helpful; may also be tailored per park
"External drive letters may include:"
gwmi win32_diskdrive | ?{$_.interfacetype -eq "USB"} | %{gwmi -Query "ASSOCIATORS OF {Win32_DiskDrive.DeviceID=`"$($_.DeviceID.replace('\','\\'))`"} WHERE AssocClass = Win32_DiskDriveToDiskPartition"} |  %{gwmi -Query "ASSOCIATORS OF {Win32_DiskPartition.DeviceID=`"$($_.DeviceID)`"} WHERE AssocClass = Win32_LogicalDiskToPartition"} | %{$_.deviceid}
$lgX = Read-Host -Prompt 'Enter the path of the external X drive'

# Check neither user-provided paths are null
IF($smX -And $lgX)
{
   # Construct complete junction command (*** NEED TO CORRECT PATHS *** others should be possible from same two inputs)
   $mklink = "mklink /j "+  $smX + "\Extras " + $lgX + "\Extras"
}
ELSE
{
   # Error and exit
   "Enter both locations"
   exit
}

# Diagnostic: Write-Host $mklink

# Execute the command to create the junction (can add others, as needed)
cmd /c $mklink