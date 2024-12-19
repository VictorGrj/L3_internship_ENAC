
import matplotlib.pyplot as plt
from doc_vs_techno_commuter import init_commuter
from doc_vs_techno_regional import init_regional
from doc_vs_techno_long_range import init_long
from doc_vs_techno_short_medium import init_short
from draw_domains import draw_domains, find_index

max_fuel_factor = 1.0
stdm_factor = 1.0
lod_factor = 1.0

# Cummuter
#-----------------------------------------------------------------------------------------------------------------------
gam, design_mission, power_system, dist_window, npax_window, criterion = init_commuter(max_fuel_factor, stdm_factor, lod_factor)
color_ind, npax_list, dist_list = find_index(gam, design_mission, power_system, dist_window, npax_window, criterion)
fig, ax   = plt.subplots()
patches = draw_domains(color_ind, npax_list, dist_list, power_system, criterion, ax)
plt.legend(handles=patches, bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0. )
plt.tight_layout()
plt.subplots_adjust(left=0.11, right=0.60)
plt.show()

max_fuel_factor = 1.25
# Regional
#-----------------------------------------------------------------------------------------------------------------------
gam, design_mission, power_system, dist_window, npax_window, criterion = init_regional(max_fuel_factor, stdm_factor, lod_factor)
color_ind, npax_list, dist_list = find_index(gam, design_mission, power_system, dist_window, npax_window, criterion)
fig, ax   = plt.subplots()
patches = draw_domains(color_ind, npax_list, dist_list, power_system, criterion, ax)
plt.legend(handles=patches, bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0. )
plt.tight_layout()
plt.subplots_adjust(left=0.11, right=0.60)
plt.show()


# Short medium
#-----------------------------------------------------------------------------------------------------------------------
gam, design_mission, power_system, dist_window, npax_window, criterion = init_short(max_fuel_factor, stdm_factor, lod_factor)
color_ind, npax_list, dist_list = find_index(gam, design_mission, power_system, dist_window, npax_window, criterion)
fig, ax   = plt.subplots()
patches = draw_domains(color_ind, npax_list, dist_list, power_system, criterion, ax)
plt.legend(handles=patches, bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0. )
plt.tight_layout()
plt.subplots_adjust(left=0.11, right=0.60)
plt.show()

# Long 
#-----------------------------------------------------------------------------------------------------------------------
gam, design_mission, power_system, dist_window, npax_window, criterion = init_long(max_fuel_factor, stdm_factor, lod_factor)
color_ind, npax_list, dist_list = find_index(gam, design_mission, power_system, dist_window, npax_window, criterion)
fig, ax   = plt.subplots()
patches = draw_domains(color_ind, npax_list, dist_list, power_system, criterion, ax)
plt.legend(handles=patches, bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0. )
plt.tight_layout()
plt.subplots_adjust(left=0.11, right=0.60)
plt.show()
