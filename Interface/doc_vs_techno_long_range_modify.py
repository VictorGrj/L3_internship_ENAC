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
from gam_copy import GAM

from draw_domains import find_index, draw_domains
import matplotlib.pyplot as plt

def init_long(max_fuel_factor, stdm_factor, lod_factor,
                  battery_density, fuel_cell_power_density, lh2_tank_index,
                  emotor_price, fuel_cell_price, lh2_tank_price, battery_capacity_price,
                  battery_price, lh2_price, lch4_price, e_fuel_price):
    gam = GAM()

    # Explore long_range category
    #-----------------------------------------------------------------------------------------------------------------------
    design_mission = {"category": "short_medium",
                    "npax": 350,
                    "range": unit.convert_from("km", 8000),
                    "speed": 0.85,
                    "altitude": unit.convert_from("ft", 35000)}

    # Long_range settings
    bpr = 12
    npax_window = [250, 550]
    dist_window = [8000, 15000]

    criterion = "flight_cash_operating_cost"

    gam.max_fuel_factor = max_fuel_factor    # Design on max fuel mission
    gam.stdm_factor = stdm_factor            # Assuming 10% weight improvement for all aircraft
    gam.lod_factor = lod_factor              # Assuming 5% L/D improvement for all aircraft

    # Techno parameters
    gam.battery_enrg_density = unit.convert_from("Wh", battery_density)
    gam.power_density["fuel_cell"] = unit.W_kW(fuel_cell_power_density)
    gam.lh2_tank_gravimetric_index = lh2_tank_index
    

    # Techno cost parameters
    gam.tech_data["emotor_power_price"] = emotor_price / unit.convert_from("kW", 1)      # $/kW
    gam.tech_data["fuel_cell_power_price"] = fuel_cell_price / unit.convert_from("kW", 1)    # $/kW
    gam.tech_data["lh2_tank_mass_price"] = lh2_tank_price                                  # $/kg
    gam.tech_data["battery_capacity_price"] = battery_capacity_price / unit.convert_from("Wh", 1)  # $/Wh

    # Energy cost parameters
    gam.energy_price["battery"] = battery_price / unit.convert_from("MWh", 1)   # ref :  110
    gam.energy_price["lh2"] = lh2_price / unit.convert_from("MWh", 1)       # ref :  140
    gam.energy_price["lch4"] = lch4_price / unit.convert_from("MWh", 1)      # ref :  120
    gam.energy_price["e_fuel"] = e_fuel_price / unit.convert_from("MWh", 1)    # ref :  125

    power_system = {}

    # Electric with batteries
    #-----------------------------------------------------------------------------------------------------------------------
    power_system["battery"] = {"energy_type": "battery",
                            "engine_count": 2,
                            "engine_type": "emotor",
                            "thruster_type": "fan",
                            "bpr": None}

    # Electric with hydrogen fuel cell
    #-----------------------------------------------------------------------------------------------------------------------
    power_system["lh2_fc"] = {"energy_type": "liquid_h2",
                            "engine_count": 2,
                            "engine_type": "emotor",
                            "thruster_type": "fan",
                            "bpr": None}

    # Turboshaft burning hydrogen
    #-----------------------------------------------------------------------------------------------------------------------
    power_system["lh2_th"] = {"energy_type": "liquid_h2",
                            "engine_count": 2,
                            "engine_type": "turbofan",
                            "thruster_type": "fan",
                            "bpr": bpr}

    # Turboshaft burning methane
    #-----------------------------------------------------------------------------------------------------------------------
    power_system["ch4_th"] = {"energy_type": "liquid_ch4",
                            "engine_count": 2,
                            "engine_type": "turbofan",
                            "thruster_type": "fan",
                            "bpr": bpr}

    # Turboshaft burning petrol
    #-----------------------------------------------------------------------------------------------------------------------
    power_system["e_fuel"] = {"energy_type": "e_fuel",
                            "engine_count": 2,
                            "engine_type": "turbofan",
                            "thruster_type": "fan",
                            "bpr": bpr}
    return gam, design_mission, power_system, dist_window, npax_window, criterion


