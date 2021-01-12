# Facilities SDE to FGDB

Exports the current data in the `DEFAULT` version of the facilities SDE
into a new file geodatabase for publication to the PDS.  Most users will not
be viewing the SDE data directly, so changes in SDE will not be available
until this process is completed.

1) Edits are made to the facilities SDE, then reviewed, corrected and posted
   to `Default`.
2) Edit a copy of [`create_new_facilities_fgdb.py`](./reate_new_facilities_fgdb.py)
   to correct the path to the `working_folder` at the top of the script.
3) Run `create_new_facilities_fgdb.py` in IDLE or with CMD/powershell with a
   command similar to `C:\path\to\python.exe \path\to\create_new_facilities_fgdb.py`
4) Copy `.\akr_facility_new.gdb` to `X:\AKR\Statewide\cultural`.
   (Assuming the current directory is the `working_folder` from step 2.)
5) Rename `X:\AKR\Statewide\cultural\akr_facility.gdb` to 
   `X:\AKR\Statewide\cultural\akr_facility_old.gdb`. You may need to log in to
   the `INPAKROVMDIST` as an administrator and kill all connections to this
   file before windows will let you rename the old version.
6) Rename `X:\AKR\Statewide\cultural\akr_facility_new.gdb` to
   `X:\AKR\Statewide\cultural\akr_facility.gdb`
7) Test layer files
   - if ok:
     - delete `X:\AKR\Statewide\cultural\akr_facility_old.gdb`
     - delete `.\akr_facility_new.gdb`
   - if bad:
     - delete `X:\AKR\Statewide\cultural\akr_facility.gdb`
     - rename `X:\AKR\Statewide\cultural\akr_facility_old.gdb` to 
       `X:\AKR\Statewide\cultural\akr_facility.gdb`
     - make fixes to facilities database, layer files, or the script as
       appropriate.
     - try again
8) Update the PDS Change Log (same as any PDS update)
