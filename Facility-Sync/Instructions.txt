QC Checks/Post/Reconcile
Run create_new_facilities_fgdb.py in IDLE
 (or in CMD/PowerShell with C:\Python27\ArcGIS10.5\python.exe .\create_new_facilities_fgdb.py)
Copy .\akr_facility_new.gdb to X:\AKR\Statewide\cultural
Rename X:\AKR\Statewide\cultural\akr_facility.gdb to X:\AKR\Statewide\cultural\akr_facility_old.gdb (may need to kill connections first)
Rename X:\AKR\Statewide\cultural\akr_facility_new.gdb to X:\AKR\Statewide\cultural\akr_facility.gdb
Test layer files
   if ok: delete X:\AKR\Statewide\cultural\akr_facility_old.gdb; delete .\akr_facility_new.gdb
   if bad: delete akr_facility.gdb; rename akr_facility_old.gdb to akr_facility.gdb; make fixes; try again.
Update changelog


OLD Instructions:
Look at X:\AKR\Statewide\cultural\akr_facility.gdb
create a new empty FGDB in C:\tmp\facility-sync\akr_facility.gdb
select the same tables and Feature classes in SDE default and drag/drop in the new FGDB
  You do not need to select the relationship classes
  Do not select building_photo_points  (it will cause a failure)
right click on the new FGDB, and select import->Feature Class (single)...
  select building_photo_points 
Rename FACLOCID in FMSSExport to Location
Create these double fields in Catalog, and then use the GP field calculate tool with the Python Parser
PARKLOTS_py.Perim_Feet = !shape.length@feet!
PARKLOTS_py.Area_SqFt = !shape.area@SQUAREFEET!
Building_Polygon.Perim_Feet = !shape.length@feet!
Building_Polygon.Area_SqFt = !shape.area@SQUAREFEET!
ROADS_ln.Length_Feet =  !shape.length@feet!
ROADS_ln.Length_Miles =  !shape.length@miles!
TRAILS_ln.Length_Feet =  !shape.length@feet!
TRAILS_ln.Length_Miles =  !shape.length@miles!
rename X:\AKR\Statewide\cultural\akr_facility.gdb to akr_facility_oldYYYY-MM-DD.gdb
move new FGDB to \\INPAKROVMDIST\GISData\Albers\base\cultural\statewid\akr_facility.gdb
Open Layer file to check
move X:\AKR\Statewide\cultural\akr_facility_oldYYYY-MM-DD.gdb to C:\tmp\facility-sync\

