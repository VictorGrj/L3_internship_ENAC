#!/usr/bin/env python3
"""
Created on Thu Jan 20 20:20:20 2020

:author: Conceptual Airplane Design & Operations (CADO team)
         Nicolas PETEILH, Pascal ROCHES, Nicolas MONROLIN, Dajung KIM, Thierry DRUOT
         Aircraft & Systems, Air Transport Department, ENAC
"""

import numpy as np

import pandas as pd
from tabulate import tabulate

from scipy.interpolate import RegularGridInterpolator
from matplotlib.colors import LinearSegmentedColormap
from gam_utils import unit
from gam_utils.physical_data import PhysicalData
import matplotlib.patches as mpatches


# Domain map
#-----------------------------------------------------------------------------------------------------------------------

def find_index(gam, design_mission, power_system, dist_window, npax_window, criterion):
    """Draw the domain map
    """
    npax_list = np.linspace(npax_window[0], npax_window[1], 5)
    dist_list = np.linspace(dist_window[0], dist_window[1], 5)

    npax_list_2 = np.linspace(npax_window[0], npax_window[1], 64)
    dist_list_2 = np.linspace(dist_window[0], dist_window[1], 64)

    crit = {}
    surf = {}

    for techno in power_system.keys():
        crit[techno] = []

        for dist in dist_list:
            design_mission["range"] = unit.convert_from("km", dist)
            crit[techno].append([])

            for npax in npax_list:
                design_mission["npax"] = npax

                try:
                    ac_dict = gam.design_airplane(power_system[techno], design_mission)
                    cost_dict = gam.operating_cost(ac_dict, traffic_zone="west_bound")
                    all_in_one = {**ac_dict, **cost_dict}
                    crit[techno][-1].append(all_in_one[criterion])
                except:
                    crit[techno][-1].append(np.inf)

        crit_mat = np.array(crit[techno])
        surf[techno] = RegularGridInterpolator((dist_list, npax_list), crit_mat, bounds_error=False, fill_value=None)

    crit_2 = {}
    dist_mat, npax_mat = np.meshgrid(dist_list_2, npax_list_2)

    for techno in power_system.keys():
        crit_2[techno] = surf[techno]((dist_mat.T, npax_mat.T))

    best_tech = []
    color_ind = []
    for jd, dist in enumerate(dist_list_2):
        best_tech.append([])
        color_ind.append([])
        for jn, npax in enumerate(npax_list_2):
            best_tech[-1].append(np.inf)
            color_ind[-1].append([])
            for ind, tech in enumerate(power_system.keys()):
                if crit_2[tech][jd][jn] < best_tech[-1][-1]:
                    best_tech[-1][-1] = crit_2[tech][jd][jn]
                    color_ind[-1][-1] = ind
                    
    arr         = np.array(color_ind).T
    flipped_arr = arr[::-1]
    npax_list = np.linspace(npax_window[0], npax_window[1], 5)
    dist_list = np.linspace(dist_window[0], dist_window[1], 5)
    
    return flipped_arr, npax_list, dist_list

def draw_domains(color_ind, npax_list, dist_list, power_system, criterion, ax):
    
    # print(flipped_arr)
    labels = [power_system[key]["engine_type"] + " " + power_system[key]["energy_type"] for key in power_system.keys() ]
    labels[1] += "+fc"
    colors = ["green", "cyan", "blue", "orange", 'brown']
    cmap1  = LinearSegmentedColormap.from_list("mycmap", colors)
    im     = ax.imshow(color_ind, cmap=cmap1, vmin=0, vmax=len(labels)-1)
    ax.set_xticks(np.linspace(0, len(color_ind), 6).astype(int), np.linspace(dist_list[0],dist_list[-1],num=6).astype(int))
    ax.set_yticks(np.linspace(0, len(color_ind[0]), 7).astype(int), np.linspace(npax_list[0],npax_list[-1],num=7).astype(int)[::-1])
    ax.set_title("Best domains for : "+criterion, fontsize=14)
    ax.set_xlabel('Range (km)', fontsize=12)
    ax.set_ylabel('Capacity (seat)', fontsize=12)
    pcolors = cmap1(np.linspace(0.0, 1.0, len(labels)))
    patches =[mpatches.Patch(color=n,label=labels[i]) for i, n in enumerate(pcolors)]
    # put those patched as legend-handles into the legend
    return patches