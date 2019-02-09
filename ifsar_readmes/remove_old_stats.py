import os
for line in open('old_style_stats.txt','r'):
   filename = os.path.join('X:\Extras\AKR\Statewide\DEM\SDMI_IFSAR',line.strip())
   os.remove(filename)
