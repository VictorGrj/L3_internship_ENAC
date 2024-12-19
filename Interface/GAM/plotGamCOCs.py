#!/usr/bin/env python3
"""
Created on Thu Jan 20 20:20:20 2020

:author: Conceptual Airplane Design & Operations (CADO team)
         Nicolas PETEILH, Pascal ROCHES, Nicolas MONROLIN, Dajung KIM, Thierry DRUOT
         Aircraft & Systems, Air Transport Department, ENAC
"""

import numpy as np

from gam_utils.physical_data import PhysicalData
from gam_utils import unit
from gam_v2 import GAM

from draw_domains import draw_domains, find_index
from matplotlib.colors import LinearSegmentedColormap
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
from doc_vs_techno_commuter import init_commuter
from doc_vs_techno_regional_modify import init_regional
from doc_vs_techno_long_range_modify import init_long
from doc_vs_techno_short_medium import init_short

fig, ax   = plt.subplots(2,2,figsize=(8,8) )
max_fuel_factor = 1.25
stdm_factor = 1.0
lod_factor = 1.0


gam, design_mission, power_system, dist_window, npax_window, criterionCum = init_commuter(max_fuel_factor, stdm_factor, lod_factor)
color_indCum, npaxCum_list, distCum_list = find_index(gam, design_mission, power_system, dist_window, npax_window, criterionCum)

labels = [power_system[key]["engine_type"] + " " + power_system[key]["energy_type"] for key in power_system.keys() ]
labels[1] += "+fc"
colors = ["green", "cyan", "blue", "orange", 'brown']
cmap1  = LinearSegmentedColormap.from_list("mycmap", colors)
im     = ax[0,0].imshow(color_indCum, cmap=cmap1, vmin=0, vmax=len(labels)-1)
ax[0,0].set_xticks(np.linspace(0, len(color_indCum), 6).astype(int), np.linspace(distCum_list[0],distCum_list[-1],num=6).astype(int))
ax[0,0].set_yticks(np.linspace(0, len(color_indCum[0]), 7).astype(int), np.linspace(npaxCum_list[0],npaxCum_list[-1],num=7).astype(int)[::-1])
ax[0,0].set_title("Commuter", fontsize=12)
# ax[0,0].set_xlabel('Range (km)', fontsize=12)
# ax[0,0].set_ylabel('Capacity (seat)', fontsize=12)


gam, design_mission, power_system, dist_window, npax_window, criterionReg = init_regional(max_fuel_factor, stdm_factor, lod_factor)
color_indReg, npaxReg_list, distReg_list = find_index(gam, design_mission, power_system, dist_window, npax_window, criterionReg)
im     = ax[0,1].imshow(color_indReg, cmap=cmap1, vmin=0, vmax=len(labels)-1)
ax[0,1].set_xticks(np.linspace(0, len(color_indReg), 6).astype(int), np.linspace(distReg_list[0],distReg_list[-1],num=6).astype(int))
ax[0,1].set_yticks(np.linspace(0, len(color_indReg[0]), 7).astype(int), np.linspace(npaxReg_list[0],npaxReg_list[-1],num=7).astype(int)[::-1])
ax[0,1].set_title("Regional", fontsize=12)
# ax[0,1].set_xlabel('Range (km)', fontsize=12)
# ax[0,1].set_ylabel('Capacity (seat)', fontsize=12)


gam, design_mission, power_system, dist_window, npax_window, criterionShort = init_short(max_fuel_factor, stdm_factor, lod_factor)
color_indShort, npaxShortlist, distShort_list = find_index(gam, design_mission, power_system, dist_window, npax_window, criterionShort)
im     = ax[1,0].imshow(color_indShort, cmap=cmap1, vmin=0, vmax=len(labels)-1)
ax[1,0].set_xticks(np.linspace(0, len(color_indShort), 6).astype(int), np.linspace(distShort_list[0],distShort_list[-1],num=6).astype(int))
ax[1,0].set_yticks(np.linspace(0, len(color_indShort[0]), 7).astype(int), np.linspace(npaxShortlist[0],npaxShortlist[-1],num=7).astype(int)[::-1])
ax[1,0].set_title("Short-medium", fontsize=12)
# ax[1,0].set_xlabel('Range (km)', fontsize=12)
# ax[1,0].set_ylabel('Capacity (seat)', fontsize=12)

gam, design_mission, power_system, dist_window, npax_window, criterionLong = init_long(max_fuel_factor, stdm_factor, lod_factor)
color_indLong, npaxLonglist, distLong_list = find_index(gam, design_mission, power_system, dist_window, npax_window, criterionLong)
im     = ax[1,1].imshow(color_indLong, cmap=cmap1, vmin=0, vmax=len(labels)-1)
ax[1,1].set_xticks(np.linspace(0, len(color_indLong), 6).astype(int), np.linspace(distLong_list[0],distLong_list[-1],num=6).astype(int))
ax[1,1].set_yticks(np.linspace(0, len(color_indLong[0]), 7).astype(int), np.linspace(npaxLonglist[0],npaxLonglist[-1],num=7).astype(int)[::-1])
ax[1,1].set_title("Long range", fontsize=12)
# ax[1,1].set_xlabel('Range (km)', fontsize=12)
# ax[1,1].set_ylabel('Capacity (seat)', fontsize=12)

fig.supxlabel('Range (km)', fontsize=12, y=0.09)
fig.supylabel('Capacity (seat)', fontsize=12, x=0.04)

# ax[1,1].set_ylabel('Capacity (seat)', fontsize=12)
pcolors = cmap1(np.linspace(0.0, 1.0, len(labels)))
for i in range(len(labels)):
    labels[i] = labels[i].replace("turboprop","turboprop/fan")  


patches =[mpatches.Patch(color=n,label=labels[i]) for i, n in enumerate(pcolors)]
# put those patched as legend-handles into the legend
plt.suptitle("Best domains for : "+criterionLong, fontsize=14)
plt.figlegend(handles=patches, loc=8, bbox_to_anchor=(0.5, 0.01), borderaxespad=0., ncol=3 ) #   
plt.tight_layout()
plt.subplots_adjust(bottom=0.152)
plt.show()
