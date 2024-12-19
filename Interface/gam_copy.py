#!/usr/bin/env python3
"""
Created on Thu Jan 20 20:20:20 2020

:author: Conceptual Airplane Design & Operations (CADO team)
         Nicolas PETEILH, Pascal ROCHES, Nicolas MONROLIN, Thierry DRUOT
         Aircraft & Systems, Air Transport Department, ENAC
"""
import streamlit as st
import numpy as np
import pandas as pd
from scipy.optimize import fsolve
from scipy.interpolate import interp1d

from copy import deepcopy

import matplotlib.pyplot as plt
import matplotlib.colors as colors

from gam_utils import data_analysis as uda
from gam_utils import math as umath
from gam_utils import unit

from gam_utils.physical_data import PhysicalData

phd = PhysicalData()


# --------------------------------------------------------------------------------------------------
#
#  Main class
#
# --------------------------------------------------------------------------------------------------

class GAM(object):
    """
    The Generic Airplane Model is a very simple way to size and fly airplanes of different
    categories and propulsive technologies
    The user can define freely the capacity, range and propulsive technology among available ones
    and fly the resulting aircraft over give routes
    """

    def __init__(self):

        # ----------------------------------------------------------------------------------
        """Key definitions
        """
        # Categories
        self.general = "general"
        self.commuter = "commuter"
        self.regional = "regional"
        self.business = "business"
        self.short_medium = "short_medium"  # Single aisle
        self.long_range = "long_range"  # Twin aisle

        # Thrusters
        self.propeller = "propeller"
        self.fan = "fan"

        # Engines
        self.turbofan = "turbofan"
        self.turboprop = "turboprop"
        self.piston = "piston"
        self.emotor = "emotor"

        self.power_elec = "power_elec"
        self.fuel_cell = "fuel_cell"

        # Energy storage
        self.petrol = "petrol"
        self.kerosene = "kerosene"
        self.e_fuel = "e_fuel"
        self.gasoline = "gasoline"
        self.gh2 = "compressed_h2"
        self.lh2 = "liquid_h2"
        self.lch4 = "liquid_ch4"
        self.lnh3 = "liquid_nh3"
        self.battery = "battery"

        # Colors in graphs
        self.colors = {self.general: "green",
                       self.commuter: "gold",
                       self.regional: "darkorange",
                       self.short_medium: "darkviolet",
                       self.long_range: "red",
                       self.business: "blue"}

        # Propulsion dictionary structures (not used in this version)
        self.main_power_system = {"energy_type": None, "engine_count": None,"engine_type": None, "thruster_type": None, "bpr": None, "hybrid": None}
        self.scnd_power_system = {"energy_type": None, "engine_count": None, "engine_type": None, "thruster_type": None, "hybrid_ratio": None}

        # ----------------------------------------------------------------------
        """Category data
        """
        # Maximum capacity and range per category, with most frequent speed, engine data
        self.category = {self.general: {"capacity": 6, "distance": unit.m_km(500), "speed": unit.convert_from("km/h", 300),
                                        "engine_type": self.turboprop, "thruster_type": self.propeller, "bpr": None},
                         self.commuter: {"capacity": 19, "distance": unit.m_km(1500), "speed": unit.convert_from("km/h", 400),
                                         "engine_type": self.turboprop, "thruster_type": self.propeller, "bpr": None},
                         self.regional: {"capacity": 80, "distance": unit.m_km(4500), "speed": 0.5,
                                         "engine_type": self.turbofan, "thruster_type": self.fan, "bpr": 12},
                         self.short_medium: {"capacity": 250, "distance": unit.m_km(8000), "speed": 0.78,
                                             "engine_type": self.turbofan, "thruster_type": self.fan, "bpr": 12},
                         self.long_range: {"capacity": 550, "distance": unit.m_km(15000), "speed": 0.85,
                                           "engine_type": self.turbofan, "thruster_type": self.fan, "bpr": 12}}

        # Flight altitudes versus airplane categories, [cruise altitude, diversion altitude, holding altitude]
        self.flight_altitudes = {self.general: unit.convert_from("ft", [5000, 3000, 1500]),
                                 self.commuter: unit.convert_from("ft", [10000, 6000, 1500]),
                                 self.regional: unit.convert_from("ft", [20000, 10000, 1500]),
                                 self.short_medium: unit.convert_from("ft", [35000, 25000, 1500]),
                                 self.long_range: unit.convert_from("ft", [35000, 25000, 1500]),
                                 self.business: unit.convert_from("ft", [35000, 25000, 1500])
                                 }

        # Parameter for reserve computation, [flight fuel factor, diversion distance, holding time]
        self.reserve_parameters = {self.general: [0., 0., unit.s_min(30)],
                                   self.commuter: [0., 0., unit.s_min(30)],
                                   self.regional: [0., 0., unit.s_min(45)],
                                   self.short_medium: [0.05, unit.m_NM(200), unit.s_min(30)],
                                   self.long_range: [0.03, unit.m_NM(200), unit.s_min(30)],
                                   self.business: [0.05, unit.m_NM(200), unit.s_min(30)]
                                   }

        # Furnishing mass allowance per passenger (kg/pax) depends on airplane category
        self.furnishing_dict = {self.general: 18,
                                self.commuter: 18,
                                self.regional: 22,
                                self.short_medium: 22,
                                self.long_range: 30,
                                self.business: 40
                                }

        # Operator items index factor (kg/passenger/distance)
        self.operator_item_index = 5.e-6  # kg/pax/m

        # Passenger mass allowance (kg/pax) depends on airplane category
        self.mpax_dict = {self.general: 95,
                          self.commuter: 105,
                          self.regional: 110,
                          self.short_medium: 115,
                          self.long_range: 120,
                          self.business: 120
                          }
        self.mpax = "model"

        # Yearly utilization versus mean range
        self.util_dist_list = unit.convert_from("NM",[100., 500., 1000., 1500., 2000., 2500., 3000., 3500., 4000.])
        self.util_list = [2300., 2300., 1500., 1200., 900., 800., 700., 600., 600.]

        # Wake turbulence categorization
        # Source :
        # @inproceedings{inproceedings,
        # author = {Durmus, Seyhun},
        # year = {2021},
        # month = {11},
        # pages = {},
        # title = {INTERNATIONAL CONFERENCE OF AERONAUTICS AND ASTRONAUTICS (ICAA'2021) EXAMINATION OF AIRCRAFT ACCORDING TO WAKE TURBULENCE RECATEGORIZATION CATEGORIES CONSIDERING THE MASS, WINGSPAN, AND ENGINE TYPES}
        # }
        self.wtc_mtow_list = [15000, 60000, 100000, 270000, 560000]
        self.wt_class_list = ["F", "E", "D", "C", "B", "A"]

        # -------------------------------------------------------------------------------------------------------------------
        """Mission performance model data
        """
        # Mass factors
        self.max_payload_factor = 1.15  # max_payload = nominal_paylod * max_payload_factor
        self.max_fuel_factor = 1.25     # max_fuel = nominal_fuel * max_fuel_factor
        self.mlw_factor = 1.07          # MLW = MZFW * mlw_factor

        self.delta_payload = 0. # Reference payload tuning

        self.disa = 0.
        self.take_off_time = unit.s_min(1)  # 30s take off + 30s initial climb
        self.full_power_time = unit.s_min(15)  # for hybrid thermal-electrical only, allow to compute the onboard energy storage

        # -------------------------------------------------------------------------------------------------------------------
        """Propulsion model data
        """
        # Reference power regression function, from general to wide bodies, Constant c adjusted for very small aircraft
        # ref_power = a * mtow**2 + b*mtow + c, represents the total power installed on the airplane
        self.ref_power_factors = [8.31693845e-05, 2.03027049e+02, -1.05e5]  # [a, b, c], ref_power = a * mtow**2 + b * mtow + c
        self.delta_power = 0.   # Reference power tuning

        # Efficiencies
        self.prop_eff = 0.80            # Propeller efficiency
        self.fan_eff = 0.82             # Propeller like fan efficiency
        self.emotor_eff = 0.90          # Electrical motor efficiency (source MAGNIX)
        self.fuel_cell_eff = 0.50       # Fuel Cell efficiency at system level (source Horizon Fuel Cell)
        self.fuel_energy_ratio = 2.28   # eta_fan / (eta_prop * eta_thermal), 0.8 / (0.7 * 0.5), FHV * SFC / SEC
        
        self.prop_system_eff = 1.       # Propulsion system efficiency factor

        # PSFC of reciprocating engines (Lycoming IO-720)
        self.psfc_piston = unit.convert_from("kg/kW/h", 0.25)
        self.fhv_piston = phd.fuel_heat(self.gasoline)

        # PSFC is linked to the max power of the turboshaft
        self.psfc_turboshaft_coef = [0.2, 10, 0.65]  # kg/kW/h = a + b / (kW)**c
        self.fhv_turboshaft = phd.fuel_heat(self.kerosene)

        # The thermal efficiency used to compute TSFC is fixed (Mean value from several common engines)
        self.eff_th_turbofan = 0.474    # 0.474
        self.fuel_mixture = 0.02        # Fuel to air ratio

        # Propulsion component power densities in kW/kg
        self.power_density = {self.turbofan: unit.W_kW(4.3),
                              self.turboprop: unit.W_kW(4.3),
                              self.piston: unit.W_kW(1.1),      # Lycoming IO-720
                              self.emotor: unit.W_kW(4.5),      # source Magnix
                              self.power_elec: unit.W_kW(10),   # source Magnix
                              self.fuel_cell: unit.W_kW(1),     # source HorizonFuelCell : 770 W/kg
                              self.propeller: unit.W_kW(10),
                              self.fan: unit.W_kW(15)
                              }

        # Other densities
        self.battery_enrg_density = unit.J_Wh(250)  # Wh/kg
        self.battery_vol_density = 2800.  # kg/m3

        self.tank_efficiency_factor = unit.convert_from("bar", 661e-3)  # 1000 bar.L/kg, Source AFHYPAC, Fiche 4.2 from CEA document

        self.initial_gh2_pressure = unit.convert_from("bar", 700)
        self.gh2_density = phd.fuel_density(self.gh2, press=self.initial_gh2_pressure)
        # kg_H2 / (kg_H2 + kg_Tank)
        self.gh2_tank_gravimetric_index = 1 / (1 + self.initial_gh2_pressure / (self.tank_efficiency_factor * self.gh2_density))
        self.gh2_tank_volumetric_index = 6.62   # kg_GH2 / m3_Tank, Source AFHYPAC, Fiche 4.2 from CEA document, Not used in this version

        self.lh2_density = phd.fuel_density(self.lh2)  # 20.39 K
        self.lh2_tank_gravimetric_index = 0.40  # kg_LH2 / (kg_LH2 + kg_Tank), Source Hypoint 2022 : 0.5
        self.lh2_tank_volumetric_index = 6.62   # kg_LH2 / m3_Tank, Source AFHYPAC, Fiche 4.2 from CEA document, Not used in this version

        self.lch4_density = phd.fuel_density(self.lch4)  # at 111.63 K
        ih2 = self.lh2_tank_gravimetric_index
        ich4 = 1 / (1 + (self.lh2_density / self.lch4_density) * (1 / ih2 - 1))
        self.lch4_tank_gravimetric_index = ich4  # kg_LCH4 / (kg_LCH4 + kg_Tank), Extrapolation from liquid H2 tanks
        self.lch4_tank_volumetric_index = self.lh2_tank_volumetric_index * (self.lch4_density / self.lh2_density)  # kg_CH4 / m3_Tank

        self.initial_lnh3_pressure = unit.convert_from("bar", 30)  # Liquid here because NH3 is liquid up to 50°C at less than 20 bars
        self.lnh3_density = phd.fuel_density(self.lnh3, press=self.initial_lnh3_pressure)
        # kg_LNH3 / (kg_NH3 + kg_Tank)  liquid here because NH3 is liquid up to 50°C at les than 20 bars
        self.lnh3_tank_gravimetric_index = 1 / (1 + self.initial_lnh3_pressure / (self.tank_efficiency_factor * self.lnh3_density))
        self.lnh3_tank_volumetric_index = 80  # kg_LNH3 / m3_Tank, Not used in this version

        # -------------------------------------------------------------------------------------------------------------------
        """Mass model data
        """
        # Standard mass regression function, from general to wide bodies, Constant c adjusted for very small aircraft
        # Standard airframe MWE = OWE - propulsion_system_mass - furnishing_mass - operator_item_mass
        # standard_af_mwe = a * mtow**2 + b*mtow + c
        self.standard_af_mwe_factors = [-3.18952359e-07, 4.22840552e-01, -30]  # [a, b, c]   # With new total_power

        # Mass tuning parameters
        self.stdm_shift = 0.    # Mass delta on standard MWE
        self.stdm_factor = 1.   # Mass factor on standard MWE

        # -------------------------------------------------------------------------------------------------------------------
        """Aero model data
        """
        # Correlation factor to estimate L/D (Raymer's mod"el)
        self.lod_coef = {self.general: 11,
                         self.commuter: 11,
                         self.regional: 12.5,
                         self.short_medium: 15.5,
                         self.long_range: 17
                         }
        # For existing commercial passenger airplanes, L/D is linked to the size of the aircraft through the MTOW
        self.lod_mtow_list = [200., 40000., 200000., 500000., 1.e6]
        self.lod_list = [13., 16, 19, 20., 20.]

        # Aero tuning parameters
        self.lod = "model"      # Allows to force a value for L/D
        self.lod_factor = 1.    # Tuning of aerodynamic efficiency

        # -------------------------------------------------------------------------------------------------------------------
        """Cost model data
           Model for classical thermal aircraft from Thorbeck
        """
        euro_dollar = 1.2

        self.energy_price = {self.petrol : 50.0 / unit.convert_from("MWh", 1),    # $/MWh 0.50 euros/kg
                             self.gasoline : 50.0 / unit.convert_from("MWh", 1),  # $/MWh
                             self.kerosene : 50.0 / unit.convert_from("MWh", 1),  # $/MWh
                             self.e_fuel : 125.0 / unit.convert_from("MWh", 1),   # $/MWh
                             self.gh2 : 160.0 / unit.convert_from("MWh", 1),      # $/MWh
                             self.lh2 : 140.0 / unit.convert_from("MWh", 1),      # $/MWh (2035)
                             self.lch4 : 120.0 / unit.convert_from("MWh", 1),     # $/MWh
                             self.lnh3 : 54.0 / unit.convert_from("MWh", 1),      # $/MWh based on green hydrogen
                             self.battery : 110.0 / unit.convert_from("MWh", 1)}  # $/MWh, 0.11 euros/kWh

        # self.energy_price = {self.petrol : 0.50 * euro_dollar / unit.convert_from("MJ", 43.1),      # 0.50 euros/kg
        #                      self.gasoline : 0.50 * euro_dollar / unit.convert_from("MJ", 43.1),    # 0.50 euros/kg
        #                      self.kerosene : 0.50 * euro_dollar / unit.convert_from("MJ", 43.1),    # 0.50 euros/kg
        #                      self.e_fuel : 2.66 * euro_dollar / unit.convert_from("MJ", 43.1),      # 2.66 euros/kg
        #                      self.gh2 : 3.90 * euro_dollar / unit.convert_from("MJ", 121),          # 3.90 euros/kg (2035)
        #                      self.lh2 : 3.90 * euro_dollar / unit.convert_from("MJ", 121),          # 3.90 euros/kg (2035)
        #                      self.lch4 : 100 * euro_dollar / unit.convert_from("MWh", 1),           # 100 euros/MWh
        #                      self.lnh3 : ((3.90 * 1.1) / 17) / unit.convert_from("MJ", 16.89),      # based on green hydrogen
        #                      self.battery : 0.11/unit.convert_from("kWh", 1)}                       # 0.11 euros/kWh
        #
        # print("*****************************************************************")
        # for k in self.energy_price.keys():
        #     print(k, self.energy_price[k] * 1.e6 / 0.277777 * 1000)
        # print("*****************************************************************")

        self.cost_range = {self.general: unit.m_km(200),
                           self.commuter: unit.m_km(400),
                           self.regional: unit.m_km(1000),
                           self.short_medium: unit.m_km(3000),
                           self.long_range: unit.m_km(6000)}

        self.cost_data = {"airframe_mass_price": 1150 * euro_dollar,
                          "thermal_engine_mass_price": 2500 * euro_dollar,

                          "depreciation_period": 14,     # Years
                          "interest_rate": 0.05,
                          "residual_value_factor": 0.1,
                          "insurance_rate": 0.005,

                          "flight_attd_salary": 60000 * euro_dollar,    # $/year/flight_attendent
                          "flight_crew_salary": 300000 * euro_dollar,   # $/year/2pilots
                          "crew_complement": 5,                         # Number of crew per airplane

                          "handling_fees": 0.1 * euro_dollar,   # Cost per kg of payload
                          "landing_fees": 0.01 * euro_dollar,   # Cost per kg of MTOW
                          "labor_cost": 50 * euro_dollar,       # Cost per hour
                          "burden_factor": 2}

        self.tech_data = {# ref M.Marksel et A.Prapotnik Brdnik, « Comparative Analysis  of
                          # Direct Operating  Costs: Conventional vs.Hydrogen  Fuel  Cell 19 - Seat Aircraft », Sustainability
                          "emotor_power_price": 94,     # euro/kW
                          "fuel_cell_power_price": 40,  # euro/kW
                          "fuel_cell_maintenance_factor": 1.277e-4,
                          # ref K.O.Ploetner, « Operating Cost Estimation for Electric - Powered Transport Aircraft »,
                          "emotor_maintenance_factor": 0.75,
                          # ref BER, “Fast-Forwarding to a Future of On-Demand Urban Air Transportation,” 2016.
                          # ref chäfer, A. W., Barrett, S. R. H., and Doyme1, K., “Technological, economic and environmental prospects of all-electric
                          # aircraft,” Nature Energy, 2018.
                          "battery_capacity_price": 300 / unit.J_Wh(1),  # 300 euro/Wh
                          # ref A First-Order Analysis of Direct Operating Costs of Battery Electric Aircraft of Zayat Kinan Al
                          # ref [1] « The Commonwealth Scientific and Industrial Research Organisation », Current, propose 4000 for battery lifetime cycle
                          "battery_lifetime_cycle": 5000,   # cycles
                          # ref https://ec.europa.eu/info/funding-tenders/opportunities/portal/screen/opportunities/topic-details/horizon-jti-cleanh2-2023-07-01
                          "gh2_tank_mass_price": 300,       # euro/kg
                          "lh2_tank_mass_price": 245}       # euro/kg

        self.traffic_zone_factor = {"domestic_europe": 1.0,
                                    "west_bound": 0.7,
                                    "east_bound": 0.6}

        # -------------------------------------------------------------------------------------------------------------------
        """Dictionary definitions
        """
        self.flight_altitude_out = {"airplane_type": None, "mission": None, "diversion": None, "holding": None}
        self.reserve_data_out = {"airplane_type": None, "fuel_factor": None, "diversion_leg": None, "holding_time": None}



    def print_model_data(self):
        print("Category data")
        print("=======================================================================================================")
        print("Category framing, max capacity and range and most frequent speed and propulsion system type")
        for cat in self.category.keys():
            print("     gam.category[gam."+cat+"]['capacity'] = ", self.category[cat]["capacity"], " pax")
            print("     gam.category[gam."+cat+"]['distance'] = ", "%.0f" % unit.convert_to("km", self.category[cat]["distance"]), " km")
            if 1 < self.category[cat]["speed"]:
                print("        gam.category[gam."+cat+"]['speed'] = ", "%.1f" % unit.convert_to("km/h", self.category[cat]["speed"]), " km/h")
            else:
                print("        gam.category[gam."+cat+"]['speed'] = ", "%.2f" % self.category[cat]["speed"], " mach")
            print("  gam.category[gam."+cat+"]['engine_type'] = ", self.category[cat]["engine_type"])
            print("gam.category[gam."+cat+"]['thruster_type'] = ", self.category[cat]["thruster_type"])
            print("")
        print("Flight altitudes, [cruise altitude, diversion altitude, holding altitude]")
        for cat in self.flight_altitudes.keys():
            print("  gam.flight_altitudes[gam."+cat+"] = ", unit.convert_to("ft", self.flight_altitudes[cat]), " ft")
        print("")
        print("Parameter for reserve computation, [flight fuel factor, diversion distance, holding time]")
        for cat in self.reserve_parameters.keys():
            print("  gam.reserve_parameters[gam."+cat+"] = ", [self.reserve_parameters[cat][0],
                                                               unit.NM_m(self.reserve_parameters[cat][1]),
                                                               unit.min_s(self.reserve_parameters[cat][2])], " [no_dim, NM, min]")
        print("")
        print("Furnishing allowance depends on airplane category")
        for cat in self.furnishing_dict.keys():
            print(" gam.furnishing_dict[gam."+cat+"] = ", self.furnishing_dict[cat], " kg")
        print("")
        print("Furnishing are computed thanks to a fixed index")
        print("  gam.operator_item_index = ", "%.1f" % (self.operator_item_index * 1e6), " kg/pax/1000km")
        print("")
        print("Passenger mass allowance depends on airplane category")
        for cat in self.furnishing_dict.keys():
            print("  gam.mpax_dict[gam."+cat+"] = ", self.mpax_dict[cat], " kg")
        print("")
        print("Yearly utilization for commercial passenger airplanes versus mean operational range")
        print("  gam.util_dist_list = ", unit.convert_to("NM", self.util_dist_list), " NM, list of mean range")
        print("       gam.util_list = ", self.util_list, " 1/year, list of mission per year")
        print("")
        print("Wake turbulence class is estimate according to MTOW only")
        print(" gam.wtc_mtow_list = ", self.wtc_mtow_list, " kg, list of mtow")
        print(" gam.wt_class_list = ", self.wt_class_list)
        print("")
        print("Propulsion model")
        print("-------------------------------------------------------------------------------------------------------")
        print("Reference power regression function, from general to wide bodies, Constant c adjusted for very small aircraft")
        print("  gam.ref_power_factors = ", self.ref_power_factors, " a,b,c : ref_power = a * mtow**2 + b * mtow + c, total installed power")
        print("")
        print("Various efficiencies and performance indices used by models")
        print("          gam.prop_eff = ", "%.3f" % self.prop_eff, " Propeller efficiency")
        print("           gam.fan_eff = ", "%.3f" % self.fan_eff, " Fan propeller like efficiency")
        print("        gam.emotor_eff = ", "%.3f" % self.emotor_eff, " Electric motor efficiency")
        print("     gam.fuel_cell_eff = ", "%.3f" % self.fuel_cell_eff, " Fuel cell efficiency")
        print(" gam.fuel_energy_ratio = ", "%.3f" % self.fuel_energy_ratio, " Fuel over energy ratio, FHV * SFC / SEC")
        print("")
        print("   gam.prop_system_eff = ", "%.3f" % self.prop_system_eff, " Propulsion system efficiency factor")
        print("")
        print("PSFC for reciprocating engines is constant and corresponds to the given fhv")
        print("  gam.psfc_piston = ", unit.convert_to("kg/kW/h", self.psfc_piston), " kg/kW/h")
        print("   gam.fhv_piston = ", "%.3f" % unit.convert_to("kWh/kg", self.fhv_piston), " kWh/kg")
        print("")
        print("PSFC is linked to the max power of the turboshaft and corresponds to the given fhv")
        print("  gam.psfc_turboshaft_coef = ", self.psfc_turboshaft_coef, " a,b,c : psfc = a + b / (kW)**c, retrieved in kg/kW/h")
        print("        gam.fhv_turboshaft = ", "%.3f" % unit.convert_to("kWh/kg", self.fhv_turboshaft), " kWh/kg")
        print("")
        print("TSFC is computed thanks to a fixed value for thermal efficiency")
        print("  gam.eff_th_turbofan = ", self.eff_th_turbofan)
        print("")
        print("The fuel mixture used to compute TSFC is fixed")
        print("     gam.fuel_mixture = ", self.fuel_mixture)
        print("")
        print("   gam.power_density[gam.turbofan] = ", "%.2f" % unit.kW_W(self.power_density[self.turbofan]), " kW/kg")
        print("  gam.power_density[gam.turboprop] = ", "%.2f" % unit.kW_W(self.power_density[self.turboprop]), " kW/kg")
        print("     gam.power_density[gam.piston] = ", "%.2f" % unit.kW_W(self.power_density[self.piston]), " kW/kg")
        print("     gam.power_density[gam.emotor] = ", "%.2f" % unit.kW_W(self.power_density[self.emotor]), " kW/kg")
        print(" gam.power_density[gam.power_elec] = ", "%.2f" % unit.kW_W(self.power_density[self.power_elec]), " kW/kg")
        print("  gam.power_density[gam.fuel_cell] = ", "%.2f" % unit.kW_W(self.power_density[self.fuel_cell]), " kW/kg")
        print("  gam.power_density[gam.propeller] = ", "%.2f" % unit.kW_W(self.power_density[self.propeller]), " kW/kg")
        print("        gam.power_density[gam.fan] = ", "%.2f" % unit.kW_W(self.power_density[self.fan]), " kW/kg")
        print("")
        print(" gam.battery_enrg_density = ", "%.0f" % unit.Wh_J(self.battery_enrg_density), " Wh/kg")
        print("  gam.battery_vol_density = ", "%.0f" % self.battery_vol_density, " kg/m3")
        print("")
        print("      gam.tank_efficiency_factor = ", "%.0f" % unit.convert_to("bar", self.tank_efficiency_factor * 1e3), " bar.liter/kg")
        print("")
        print("        gam.initial_gh2_pressure = ", "%.0f" % unit.convert_to("bar", self.initial_gh2_pressure), " bar")
        print("                 gam.gh2_density = ", "%.2f" % self.gh2_density, " kg/m3")
        print("  gam.gh2_tank_gravimetric_index = ", "%.3f" % self.gh2_tank_gravimetric_index, " kg_GH2 / (kg_GH2 + kg_Tank")
        print("   gam.gh2_tank_volumetric_index = ", "%.1f" % self.gh2_tank_volumetric_index, " kg_GH2 / (m3_Tank_+_GH2)")
        print("")
        print("                 gam.lh2_density = ", "%.2f" % self.lh2_density, " kg/m3")
        print("  gam.lh2_tank_gravimetric_index = ", "%.3f" % self.lh2_tank_gravimetric_index, " kg_LH2 / (kg_LH2 + kg_Tank")
        print("   gam.lh2_tank_volumetric_index = ", "%.1f" % self.lh2_tank_volumetric_index, " kg_LH2 / (m3_Tank_+_LH2)")
        print("")
        print("                gam.lch4_density = ", "%.2f" % self.lch4_density, " kg/m3")
        print(" gam.lch4_tank_gravimetric_index = ", "%.3f" % self.lch4_tank_gravimetric_index, " kg_LCH4 / (kg_LCH4 + kg_Tank")
        print("  gam.lch4_tank_volumetric_index = ", "%.1f" % self.lch4_tank_volumetric_index, " kg_LCH4 / (m3_Tank_+_LCH4)")
        print("")
        print("       gam.initial_lnh3_pressure = ", unit.convert_to("bar", self.initial_lnh3_pressure), " bar")
        print("                gam.lnh3_density = ", "%.2f" % self.lnh3_density, " kg/m3")
        print(" gam.lnh3_tank_gravimetric_index = ", "%.3f" % self.lnh3_tank_gravimetric_index, " kg_LNH3 / (kg_LNH3 + kg_Tank")
        print("  gam.lnh3_tank_volumetric_index = ", "%.1f" % self.lnh3_tank_volumetric_index, " kg_LNH3 / (m3_Tank_+_LNH3)")
        print("")
        print("Aerodynamic model")
        print("-------------------------------------------------------------------------------------------------------")
        print("For commercial passenger airplanes, L/D is linked to the size of the aircraft through the MTOW")
        print("  gam.lod_mtow_list = ", self.lod_mtow_list, " kg, list of MTOW")
        print("       gam.lod_list = ", self.lod_list, " L/D, list of aerodynamic efficiencies")
        print("")
        print("     gam.lod_factor = ", self.lod_factor, " L/D model tuning")
        print("            gam.lod = ", self.lod, " Can be 'model' or a user value to force the L/D")
        print("")
        print("Mass estimation model")
        print("-------------------------------------------------------------------------------------------------------")
        print("Standard airframe mass regression function, from general to wide bodies, Constant c adjusted for very small aircraft")
        print("  gam.standard_af_mwe_factors = ", self.standard_af_mwe_factors, " a,b,c : standard_af_mwe = a * mtow**2 + b*mtow + c")
        print("")
        print("               gam.stdm_shift = ", self.stdm_shift, " kg, Mass delta on standard MWE")
        print("              gam.stdm_factor = ", self.stdm_factor, " nodim, Mass factor on standard MWE")
        print("")
        print("Some data for mission performance estimation")
        print("-------------------------------------------------------------------------------------------------------")
        print("      gam.max_payload_factor = ", "%.3f" % self.max_payload_factor, " max_payload = nominal_paylod * max_payload_factor")
        print("         gam.max_fuel_factor = ", "%.3f" % self.max_fuel_factor, " max_fuel = nominal_fuel * max_fuel_factor")
        print("              gam.mlw_factor = ", "%.3f" % self.mlw_factor, " MLW = MZFW * mlw_factor")
        print("")
        print("           gam.delta_payload = ", "%.3f" % self.delta_payload, " Reference payload tuning")
        print("")
        print("                    gam.disa = ", "%.1f" % self.disa, " K, Temperature shift for all computations")
        print("           gam.take_off_time = ", "%.0f" % self.take_off_time, " s, 30s take off + initial climb")
        print("         gam.full_power_time = ", "%.0f" % self.full_power_time, " s, 15s take off + initial climb, for hybrid only")

    #-------------------------------------------------------------------------------------------------------------------
    """Low level sub-models
    """
    def flight_attd_count(self, n_pax):
        if n_pax < 20:
            return 0
        else:
            return np.ceil(n_pax / 50)

    def wake_turbulence_class(self, mtow):
        """Estimate Wake Turbulence Class according to MTOW only
        """
        cat = self.wt_class_list[np.searchsorted(self.wtc_mtow_list, mtow, side="right")]
        return cat

    def yearly_utilization(self, block_time):
        """Compute the yearly utilization from the average block time
           Source : A simplified DOC method, TU Berlin by Thorbeck
        """
        # nr = np.interp(mean_range, self.util_dist_list, self.util_list)
        nr = 6011.2 / ((block_time / 3600) + 1.83)
        return nr

    def flight_altitude(self, airplane_type, cruise_altp=None):
        """return [cruise altitude, diversion altitude, holding altitude]
        """
        mz, dz, hz = self.flight_altitudes[airplane_type]
        if cruise_altp is not None:
            mz = cruise_altp
        self.flight_altitude_out["airplane_type"] = airplane_type
        self.flight_altitude_out["mission"] = mz
        self.flight_altitude_out["diversion"] = dz
        self.flight_altitude_out["holding"] = hz
        return self.flight_altitude_out

    def reserve_data(self, airplane_type):
        """return [mission fuel factor, diversion leg, holding time]
        """
        ff, dl, ht = self.reserve_parameters[airplane_type]
        self.reserve_data_out["airplane_type"] = airplane_type
        self.reserve_data_out["fuel_factor"] = ff
        self.reserve_data_out["diversion_leg"] = dl
        self.reserve_data_out["holding_time"] = ht
        return self.reserve_data_out

    def get_lod(self, mtow, force_model=False):
        """Return L/D estimation or user input
        """
        if force_model or self.lod == "model":
            lod_ref = np.interp(mtow, self.lod_mtow_list, self.lod_list)
            lod = lod_ref * self.lod_factor
        else:
            lod = self.lod
        return lod

    def get_lod_2(self, category, mtow, ar, force_model=False):
        """Return L/D estimation or user input
        """
        if force_model or self.lod == "model":
            volume = 0.00484679 * mtow
            s_wet = 0.50449901 * volume + 16.24162662 * volume**0.6
            s_ref = 1.01525863e-03 * mtow + 1.98722257e-01 * np.sqrt(mtow) + 5.01760301e+00
            lod_max = self.lod_coef[category] * np.sqrt(ar * s_ref / s_wet)
            lod = 0.866 * lod_max
        else:
            lod = self.lod
        return lod

    def get_piston_eff(self):
        """Return reciprocating engine overall efficiency, including propeller
        """
        eff = (self.prop_eff * self.prop_system_eff) / (self.fhv_piston * self.psfc_piston)
        return eff

    def get_piston_sfc(self, energy_type):
        """Return reciprocating engine PSFC  (kg/s/W)
        """
        eff = self.get_piston_eff()
        fhv = phd.fuel_heat(energy_type)
        sfc = self.prop_eff / (fhv * eff)
        return sfc, fhv

    def get_turboprop_eff(self, max_power):
        """Return turboprop engine overall efficiency, including propeller
        """
        a, b, c = self.psfc_turboshaft_coef
        psfc_ref = unit.convert_from("kg/kW/h", a + b / unit.kW_W(max_power)**c)
        eff = (self.prop_eff * self.prop_system_eff) / (self.fhv_turboshaft * psfc_ref)
        return eff

    def get_turboprop_sfc(self, max_power, energy_type):
        """Return turboprop engine PSFC  (kg/s/W)
        """
        eff = self.get_turboprop_eff(max_power)
        fhv = phd.fuel_heat(energy_type)
        sfc = self.prop_eff / (fhv * eff)
        return sfc, fhv

    def get_turbofan_eff(self, tas, bpr, energy_type):
        """Return turbofan engine overall efficiency, including fan
        """
        fhv = phd.fuel_heat(energy_type)
        eff_th = self.eff_th_turbofan
        alpha = self.fuel_mixture
        eff_pr = 1 / (0.5 + np.sqrt(0.25 + ((alpha * eff_th * fhv) / (2 * (1 + bpr) * tas ** 2))))
        eff = eff_th * eff_pr * self.prop_system_eff
        return eff

    def get_turbofan_sfc(self, tas, bpr, energy_type):
        """Return turbofan engine TSFC (kg/s/N)
        """
        eff = self.get_turbofan_eff(tas, bpr, energy_type)
        fhv = phd.fuel_heat(energy_type)
        sfc = tas / (eff * fhv)
        return sfc, fhv

    def get_emotor_eff(self, energy_type, thruster_type):
        """Return electric motor overall efficiency, including propeller and eventually fuel cell
        """
        if thruster_type==self.propeller:
            thruster_eff = self.prop_eff
        elif thruster_type==self.fan:
            thruster_eff = self.fan_eff
        else:
            raise Exception("thruster type is unknown")
        if energy_type==self.battery:
            eff = thruster_eff * self.emotor_eff * self.prop_system_eff
        elif energy_type in [self.gh2, self.lh2]:
            eff = thruster_eff * self.emotor_eff * self.fuel_cell_eff * self.prop_system_eff
        else:
            raise Exception("energy type is unknown")
        return eff

    def ref_power(self, mtow):
        """Required total generic power for an airplane with a given MTOW
        This sub-model is a key element of the method
        """
        a, b, c = self.ref_power_factors
        power = (a * mtow + b) * mtow + c + self.delta_power
        return power

    def take_off_energy(self, total_power):
        """Return the energy required for take off
        """
        take_off_enrg = total_power * self.take_off_time  # Take off
        return take_off_enrg

    def climb_energy(self, mass, alt):
        """Return the energy required to climb to the cruise altitude
        """
        climb_enrg = mass * alt * phd.gravity()  # Altitude elevation
        return climb_enrg

    def standard_mass(self, mtow):
        """Averaged Standard standard MWE for an airplane with a given MTOW (std_mass = MWE - furnishing - operator items)
        This sub-model is a key element of the method
        """
        a, b, c = self.standard_af_mwe_factors
        std_mass = (a * mtow + b) * mtow + c
        return std_mass

    def furnishing(self, npax, category):
        """Semi empirical furnishing mass
        """
        index = self.furnishing_dict[category]
        return index * npax

    def op_item(self, npax, distance):
        """Semi empirical mass for operator items
        """
        kp = self.operator_item_index
        return kp * npax * distance

    def get_pax_allowance(self, category):
        """Compute passenger mass allowance
        WARNING : continuous function to avoid convergence problem within solvings
        """
        if self.mpax == "model":
            m_pax = self.mpax_dict[category]
        else:
            m_pax = self.mpax
        return m_pax


    #-------------------------------------------------------------------------------------------------------------------
    """Model components for mass estimation
    """
    def propulsion_mass(self, power_system, total_power):
        """Estimates the mass of the propulsion system according to the selected architecture
        """
        energy_type = power_system["energy_type"]
        engine_type = power_system["engine_type"]
        thruster_type = power_system["thruster_type"]

        fuel_cell_system_mass = 0
        if engine_type == self.piston:
            propulsion_mass = total_power / self.power_density[engine_type]
            propulsion_mass += total_power / self.power_density[self.propeller]
        elif engine_type == self.turboprop:
            propulsion_mass = total_power / self.power_density[engine_type]
            propulsion_mass += total_power / self.power_density[self.propeller]
        elif engine_type == self.turbofan:
            propulsion_mass = total_power / self.power_density[engine_type]
        elif engine_type == self.emotor:
            propulsion_mass = total_power / self.power_density[engine_type]
            propulsion_mass += total_power / self.power_density[self.power_elec]
            if thruster_type == self.fan:
                propulsion_mass += total_power / self.power_density[self.fan]
            elif thruster_type == self.propeller:
                propulsion_mass += total_power / self.power_density[self.propeller]
            else:
                raise Exception("target power system - thruster type is unknown")

            if energy_type in [self.gh2, self.lh2]:
                fuel_cell_system_mass = (total_power / self.emotor_eff) / self.power_density[self.fuel_cell]
            elif energy_type == self.battery:
                pass
            else:
                raise Exception("target power system - energy_type is unknown")
        else:
            raise Exception("engine type is unknown")

        return propulsion_mass, fuel_cell_system_mass

    def energy_storage_mass(self, power_system, max_fuel, max_enrg):
        """Compute fuel and or energy storage mass
        """
        energy_storage_mass = 0.
        if power_system["energy_type"] in [self.kerosene, self.e_fuel, self.gasoline, self.petrol]:
            fuel_density = phd.fuel_density(power_system["energy_type"])
        elif power_system["energy_type"] == self.gh2:
            fuel_density = phd.fuel_density(self.gh2, press=self.initial_gh2_pressure)
            self.gh2_tank_gravimetric_index = 1 / (
                    1 + self.initial_gh2_pressure / (self.tank_efficiency_factor * fuel_density))
            energy_storage_mass += max_fuel * (1. / self.gh2_tank_gravimetric_index - 1.)
        elif power_system["energy_type"] == self.lh2:
            fuel_density = phd.fuel_density(self.lh2)
            energy_storage_mass += max_fuel * (1. / self.lh2_tank_gravimetric_index - 1.)
        elif power_system["energy_type"] == self.lch4:
            fuel_density = phd.fuel_density(self.lch4)
            energy_storage_mass += max_fuel * (1. / self.lch4_tank_gravimetric_index - 1.)
        elif power_system["energy_type"] == self.lnh3:
            fuel_density = phd.fuel_density(self.lnh3)
            self.lnh3_tank_gravimetric_index = 1 / (
                    1 + self.initial_lnh3_pressure / (self.tank_efficiency_factor * fuel_density))
            energy_storage_mass += max_fuel * (1. / self.lnh3_tank_gravimetric_index - 1.)
        elif power_system["energy_type"] == self.battery:
            fuel_density = phd.fuel_density(self.battery)
            energy_storage_mass += max_enrg / self.battery_enrg_density
        else:
            raise Exception("energy_type is unknown")

        return energy_storage_mass, fuel_density

    def owe_structure(self, category, npax, mtow, distance, total_power, max_fuel, max_enrg, power_system):
        """Compute OWE from the point of view of structures
        """
        furnishing = self.furnishing(npax, category)
        operator_items = self.op_item(npax, distance)
        standard_mass = self.standard_mass(mtow)  # Standard MWE is MWE without furnishing
        propulsion_mass, fuel_cell_system_mass = self.propulsion_mass(power_system, total_power)
        energy_storage_mass, fuel_density = self.energy_storage_mass(power_system, max_fuel, max_enrg)

        basic_mwe = standard_mass * self.stdm_factor + self.stdm_shift
        std_mwe = basic_mwe + propulsion_mass + energy_storage_mass + fuel_cell_system_mass
        mwe = std_mwe + furnishing
        owe = mwe + operator_items

        return {"owe": owe,
                "op_item": operator_items,
                "mwe": mwe,
                "furnishing": furnishing,
                "std_mwe": std_mwe,
                "propulsion_mass": propulsion_mass,
                "fuel_cell_system_mass": fuel_cell_system_mass,
                "energy_storage_mass": energy_storage_mass,
                "fuel_density": fuel_density,
                "basic_mwe": basic_mwe,
                "stdm_factor": self.stdm_factor,
                "stdm_shift": self.stdm_shift}

    #-------------------------------------------------------------------------------------------------------------------
    """Model components for mission fuel estimation
    """
    def get_tas(self, tamb, speed, speed_type):
        vsnd = phd.sound_speed(tamb)
        if speed_type == "mach":
            tas = speed * vsnd
            return tas, speed
        elif speed_type == "tas":
            mach = speed / vsnd
            return speed, mach

    def leg_fuel(self, start_mass, distance, altp, speed, speed_type, mtow, max_power, power_system):
        """Compute fuel and or energy over a given distance
        """
        pamb, tamb, g = phd.atmosphere_g(altp, self.disa)
        tas, mach = self.get_tas(tamb, speed, speed_type)

        time = distance / tas
        lod = self.get_lod(mtow)

        if power_system["engine_type"] == self.piston:
            eff = self.get_piston_eff()
        elif power_system["engine_type"] == self.turboprop:
            eff = self.get_turboprop_eff(max_power)
        elif power_system["engine_type"] == self.turbofan:
            eff = self.get_turbofan_eff(tas, power_system["bpr"], power_system["energy_type"])
        elif power_system["engine_type"] == self.emotor:
            eff = self.get_emotor_eff(power_system["energy_type"], power_system["thruster_type"])
        else:
            raise Exception("power system, engine type is unknown")

        if power_system["energy_type"] == self.battery:
            fuel = 0.
            enrg = start_mass * g * distance / (eff * lod)      # Airplane mass is constant
        else:
            fhv = phd.fuel_heat(power_system["energy_type"])
            fuel = start_mass * (1. - np.exp(-(g * distance) / (eff * fhv * lod)))
            enrg = fuel * fhv

        return fuel, enrg, lod, eff, time

    def holding_fuel(self, start_mass, time, altp, speed, speed_type, mtow, max_power, power_system):
        """Compute the fuel for a given holding time
        WARNING : when fuel is used, returned value is fuel mass (kg)
                  when battery is used, returned value is energy (J)
        """
        pamb, tamb, g = phd.atmosphere_g(altp, self.disa)
        tas,mach = self.get_tas(tamb, speed, speed_type)

        lod = self.get_lod(mtow)

        if power_system["engine_type"] == self.piston:
            eff = self.get_piston_eff()
        elif power_system["engine_type"] == self.turboprop:
            eff = self.get_turboprop_eff(max_power)
        elif power_system["engine_type"] == self.turbofan:
            eff = self.get_turbofan_eff(tas, power_system["bpr"], power_system["energy_type"])
        elif power_system["engine_type"] == self.emotor:
            eff = self.get_emotor_eff(power_system["energy_type"], power_system["thruster_type"])
        else:
            raise Exception("power system, engine type is unknown")

        if power_system["energy_type"] == self.battery:
            fuel = 0.
            enrg = start_mass * g * tas * time / (eff * lod)      # Airplane mass is constant
        else:
            fhv = phd.fuel_heat(power_system["energy_type"])
            fuel = start_mass * (1. - np.exp(-(g * tas * time) / (eff * fhv * lod)))
            enrg = fuel * fhv

        return fuel, enrg, lod

    def total_fuel(self, tow, distance, cruise_speed, mtow, total_power, power_system, altitude_data, reserve_data):
        """Compute the total fuel required for a mission
        WARNING : when fuel is used, returned value is fuel mass (kg)
                  when battery is used, returned value is energy (J)
        """
        if cruise_speed > 1:
            speed_type = "tas"
        else:
            speed_type = "mach"

        max_power = total_power / power_system["engine_count"]
        cruise_altp = altitude_data["mission"]

        mission_fuel = 0
        mission_enrg = 0

        mission_enrg += self.take_off_energy(total_power)
        mission_enrg += self.climb_energy(tow, cruise_altp)
        if power_system["energy_type"] != self.battery:
            mission_fuel += mission_enrg * (self.fuel_energy_ratio / phd.fuel_heat(power_system["energy_type"]))

        fuel, enrg, mission_lod, global_eff, mission_time = self.leg_fuel(tow, distance, cruise_altp, cruise_speed, speed_type, mtow, max_power, power_system)
        mission_fuel += fuel
        mission_enrg += enrg

        if power_system["energy_type"] != self.battery:
            ldw = tow - mission_fuel
        else:
            ldw = tow

        reserve_fuel = 0.
        reserve_enrg = 0.

        if reserve_data["fuel_factor"] > 0:
            reserve_fuel += reserve_data["fuel_factor"] * mission_fuel
            reserve_enrg += reserve_data["fuel_factor"] * mission_enrg
        if reserve_data["diversion_leg"] > 0:
            leg = reserve_data["diversion_leg"]
            diversion_altp = altitude_data["diversion"]
            lf, le, lod, eff, time = self.leg_fuel(ldw, leg, diversion_altp, cruise_speed, speed_type, mtow, max_power, power_system)
            reserve_fuel += lf
            reserve_enrg += le
        if reserve_data["holding_time"] > 0:
            time = reserve_data["holding_time"]
            holding_altp = altitude_data["holding"]
            speed = 1. * cruise_speed
            hf, he, lod = self.holding_fuel(ldw, time, holding_altp, speed, speed_type, mtow, max_power, power_system)
            reserve_fuel += hf
            reserve_enrg += he

        return {"tow": tow,
                "distance": distance,
                "total_fuel": mission_fuel + reserve_fuel,
                "mission_fuel": mission_fuel,
                "reserve_fuel": reserve_fuel,
                "total_enrg": mission_enrg + reserve_enrg,
                "mission_enrg": mission_enrg,
                "reserve_enrg": reserve_enrg,
                "mission_lod": mission_lod,
                "global_eff": global_eff,
                "mission_time": mission_time}

    def owe_performance(self, payload, mtow, range, cruise_speed, total_power, power_system, altitude_data, reserve_data):
        """Compute OWE from the point of view of mission
        energy_storage_mass contains the battery weight or tank weight for GH2 or LH2 storage
        """
        this_dict = self.total_fuel(mtow, range, cruise_speed, mtow, total_power, power_system, altitude_data, reserve_data)

        owe = mtow - payload - this_dict["total_fuel"]

        max_fuel = this_dict["total_fuel"] * self.max_fuel_factor  # Tanks are sized for max fuel
        max_enrg = this_dict["total_enrg"] * self.max_fuel_factor  # Battery is sized for max fuel

        return {"owe": owe,
                "total_energy": this_dict["total_enrg"],
                "total_fuel": this_dict["total_fuel"],
                "mission_fuel": this_dict["mission_fuel"],
                "reserve_fuel": this_dict["reserve_fuel"],
                "max_fuel": max_fuel,
                "mission_enrg": this_dict["mission_enrg"],
                "reserve_enrg": this_dict["reserve_enrg"],
                "max_energy": max_enrg,
                "payload": payload,
                "aerodynamic_efficiency": this_dict["mission_lod"],
                "propulsion_system_efficiency": this_dict["global_eff"]}

    #-------------------------------------------------------------------------------------------------------------------
    """Model components for airplane sizing, e.g. defining characteristics masses OWE, MZFW, MLW, MTOW
    """
    def get_category_data(self, mission):
        """Retrieves payload characteristics from mission dictionary data
        """
        design_range = mission["range"]
        guessed_category = None

        if "npax" in mission.keys() and "range" in mission.keys():
            for cat in self.category.keys():
                if mission["npax"] <= self.category[cat]["capacity"] and mission["range"] <= self.category[cat]["distance"]:
                    guessed_category = cat
                    break
            if "category" not in mission.keys():
                raise Exception("Could not find category for npax = ",mission["npax"], " and range = ", mission["range"])
        else:
            guessed_category = None

        if "category" in mission.keys():
            category = mission["category"]
        else:
            if guessed_category is None:
                raise Exception("Keys 'npax' AND 'range' must be valued in category guess mode")
            else:
                category = guessed_category

        if "speed" in mission.keys():
            cruise_speed = mission["speed"]
        else:
            if guessed_category is None:
                raise Exception("Keys 'npax' AND 'range' must be valued in speed guess mode")
            else:
                cruise_speed = self.category[category]["speed"]

        if "altitude" in mission.keys():
            cruise_altp = mission["altitude"]
        else:
            if guessed_category is None:
                raise Exception("Keys 'npax' AND 'range' must be valued in altitude guess mode")
            else:
                cruise_altp = self.flight_altitudes[category][0]

        if "npax" in mission.keys() and "payload" not in mission.keys():
            npax = mission["npax"]
            mpax = self.get_pax_allowance(category)
            payload = npax * mpax + self.delta_payload
        elif "npax" in mission.keys() and "payload" in mission.keys():
            npax = mission["npax"]
            payload = mission["payload"]
            mpax = payload / npax
            self.mpax = mpax
        elif "npax" not in mission.keys() and "payload" in mission.keys():
            npax = 0
            mpax = self.get_pax_allowance(category)
            payload = mission["payload"]
        else:
            raise Exception("Key 'npax' or/and key 'payload' must be present in mission input dictionary")
        return design_range, npax, mpax, payload, category, cruise_speed, cruise_altp

    def design_airplane(self, power_system, mission):
        """Perform the design of the aircraft with a target on Range

        power_system = {"energy_type": can be : "petrol", "kerosene", "gasoline", "compressed_h2", "liquid_h2", "liquid_ch4", "liquid_nh3", "battery"
                        "engine_count": integer, the number of engines
                        "engine_type": can be : "turbofan", "turboprop", "piston", "emotor"
                        "thruster_type": can be : "propeller", "fan"
                        "bpr": by pass ratio, for turbofan only}

        design_mission = {"category": can be : "general", "commuter", "regional", "business", "short_medium", "long_range"
                          "npax": integer, nominal number of passengers (used for design mission)
                          "speed": design cruise speed, can be speed in m/s or Mach number
                          "range": m, design range
                          "altitude": m, nominal cruise altitude}

        The method retrieves a dictionary with all airplane data

        WARNINGS:
            Any data to be given to methods MUST be delivered in standard units. Use the conversion library (or any other)
            The key "npax" in the design_mission dictionnary can be replace by "payload" associated to a mass value
            The combination "emotor" AND "liquid_h2" or "compressed_h2" implies the use of fuel cells
            The category is used to select the mode for fuel (energy) mission reserve computation
            The effect of cruise altitude will only impact the amount of fuel (energy) during mission climb
        """
        if "bpr" not in power_system.keys():
            power_system["bpr"] = None

        design_range, npax, mpax, payload, category, cruise_speed, cruise_altp = self.get_category_data(mission)

        altitude_data = self.flight_altitude(category, cruise_altp)
        reserve_data = self.reserve_data(category)

        def mass_mission_balance(mtow):
            total_power = self.ref_power(mtow)
            dict_p = self.owe_performance(payload, mtow, design_range, cruise_speed, total_power, power_system, altitude_data, reserve_data)
            dict_s = self.owe_structure(category, npax, mtow, design_range, total_power, dict_p["max_fuel"], dict_p["max_energy"], power_system)
            mtow_out = dict_s["owe"] + payload + dict_p["total_fuel"]
            return dict_p["owe"] - dict_s["owe"]

        mtow_ini = 0.9e-3 * (payload / mpax) * design_range
        output_dict = fsolve(mass_mission_balance, x0=mtow_ini, args=(), full_output=True)
        if (output_dict[2] != 1) or output_dict[0][0] < 0:
            raise Exception("Convergence problem")

        mtow = output_dict[0][0]
        total_power = self.ref_power(mtow)
        max_power = total_power / power_system["engine_count"]
        dict_p = self.owe_performance(payload, mtow, design_range, cruise_speed, total_power, power_system, altitude_data, reserve_data)
        dict_s = self.owe_structure(category, npax, mtow, design_range, total_power, dict_p["max_fuel"], dict_p["max_energy"], power_system)

        this_dict = self.total_fuel(mtow, 0., cruise_speed, mtow, total_power, power_system, altitude_data, reserve_data)

        payload_max = min(mtow - dict_s["owe"] - this_dict["total_fuel"], dict_p["payload"] * self.max_payload_factor)
        this_dict["max_payload_factor"] = self.max_payload_factor
        mzfw = dict_s["owe"] + payload_max
        mlw = mzfw * self.mlw_factor

        storage_energy_density = dict_p["total_energy"] / (dict_s["energy_storage_mass"] + dict_p["total_fuel"])

        propulsion_power_density = total_power / (dict_s["propulsion_mass"] + dict_s["fuel_cell_system_mass"])

        wtc = self.wake_turbulence_class(mtow)

        return self.design_dict(npax, mpax, design_range, cruise_speed, category, max_power, total_power, mtow, mzfw, mlw, payload_max,
                            power_system, mission, altitude_data, reserve_data, dict_p, dict_s,
                            storage_energy_density, propulsion_power_density, wtc)

    def best_design(self, power_system, mission, crit="pk_o_mass"):
        """Compute the optimal range for a given capacity according to the criterion PK/OWE or PK/E
        """
        def fct(range):
            mission["range"] = range
            this_dict = self.design_airplane(power_system, mission)
            return this_dict[crit]

        range_ini = unit.m_km(400)
        dr = unit.m_km(50)
        range_opt, pk_o_owe_max, rc = umath.maximize_1d(range_ini, dr, [fct])
        return range_opt, pk_o_owe_max, rc

    def design_from_mtow(self, power_system, mission):
        """Perform the design with a target on MTOW instead of a target on Range
        Targetted MTOW must be provided in the mission dictionary under the keys "mtow"

        power_system = {"energy_type": can be : "petrol", "kerosene", "gasoline", "compressed_h2", "liquid_h2", "liquid_ch4", "liquid_nh3", "battery"
                        "engine_count": integer, the number of engines
                        "engine_type": can be : "turbofan", "turboprop", "piston", "emotor"
                        "thruster_type": can be : "propeller", "fan"
                        "bpr": by pass ratio, for turbofan only}

        design_mission = {"category": can be : "general", "commuter", "regional", "business", "short_medium", "long_range"
                          "npax": integer, nominal number of passengers (used for design mission)
                          "speed": design cruise speed, can be speed in m/s or Mach number
                          "mtow": kg, design mtow (range will be an output)
                          "altitude": m, nominal cruise altitude}

        The method retrieves a dictionary with all airplane data

        WARNINGS:
            Any data to be given to methods MUST be delivered in standard units. Use the conversion library (or any other)
            The key "npax" in the design_mission dictionnary can be replace by "payload" associated to a mass value
            The combination "emotor" AND "liquid_h2" or "compressed_h2" implies the use of fuel cells
            The category is used to select the mode for fuel (energy) mission reserve computation
            The effect of cruise altitude will only impact the amount of fuel (energy) during mission climb
        """
        if "bpr" not in power_system.keys():
            power_system["bpr"] = None

        design_range, npax, mpax, payload, category, cruise_speed, cruise_altp = self.get_category_data(mission)

        mtow = mission["mtow"]

        altitude_data = self.flight_altitude(category, cruise_altp)
        reserve_data = self.reserve_data(category)

        total_power = self.ref_power(mtow)
        max_power = total_power / power_system["engine_count"]

        def mass_mission_balance(distance):
            dict_p = self.owe_performance(payload, mtow, distance, cruise_speed, total_power, power_system, altitude_data, reserve_data)
            dict_s = self.owe_structure(category, npax, mtow, distance, total_power, dict_p["max_fuel"], dict_p["max_energy"], power_system)
            return dict_p["owe"] - dict_s["owe"]

        distance_ini = 40 * mtow
        output_dict = fsolve(mass_mission_balance, x0=distance_ini, args=(), full_output=True)
        if (output_dict[2] != 1): raise Exception("Convergence problem")

        distance = output_dict[0][0]

        dict_p = self.owe_performance(payload, mtow, distance, cruise_speed, total_power, power_system, altitude_data, reserve_data)
        dict_s = self.owe_structure(category, npax, mtow, distance, total_power, dict_p["max_fuel"], dict_p["max_energy"], power_system)

        this_dict = self.total_fuel(mtow, 0., cruise_speed, mtow, total_power, power_system, altitude_data, reserve_data)

        payload_max = min(mtow - dict_s["owe"] - this_dict["total_fuel"], dict_p["payload"] * self.max_payload_factor)
        mzfw = dict_s["owe"] + payload_max
        mlw = mzfw * self.mlw_factor

        storage_energy_density = dict_p["total_energy"] / (dict_s["energy_storage_mass"] + dict_p["total_fuel"])

        propulsion_power_density = total_power / (dict_s["propulsion_mass"] + dict_s["fuel_cell_system_mass"])

        wtc = self.wake_turbulence_class(mtow)

        return self.design_dict(npax, mpax, design_range, cruise_speed, category, max_power, total_power, mtow, mzfw, mlw, payload_max,
                            power_system, mission, altitude_data, reserve_data, dict_p, dict_s,
                            storage_energy_density, propulsion_power_density, wtc)

    def tune_design(self, power_system, mission):
        """Computes the following model parameters :
            self.lod_factor
            self.stdm_factor
            self.mpax
            self.max_payload_factor
        so that the results of the design process exactly matches with the characteristics of a given aircraft
        in terms of Design Range, Passenger Capacity, MTOW, OWE, MZFW and Payload
        Required input data must be provided in the mission dictionary :

        power_system = {"energy_type": can be : "petrol", "kerosene", "gasoline", "compressed_h2", "liquid_h2", "liquid_ch4", "liquid_nh3", "battery"
                        "engine_count": integer, the number of engines
                        "engine_type": can be : "turbofan", "turboprop", "piston", "emotor"
                        "thruster_type": can be : "propeller", "fan"
                        "bpr": by pass ratio, for turbofan only}

        design_mission = {"category": can be : "general", "commuter", "regional", "business", "short_medium", "long_range"
                          "npax": integer, nominal number of passengers (used for design mission)
                          "speed": design cruise speed, can be speed in m/s or Mach number
                          "range": m, design range
                          "altitude": m, nominal cruise altitude
                          "mtow": kg, maximum take off mass (must be provided for calibration purpose)
                          "owe": kg, operational empty mass (must be provided for calibration purpose)
                          "payload": kg, nominal payload (must be provided for calibration purpose)
                          "payload_max": kg, maximum payload (must be provided for calibration purpose)}

        The method retrieves a dictionary with all airplane data

        WARNINGS:
            Any data to be given to methods MUST be delivered in standard units. Use the conversion library (or any other)
            The key "npax" in the design_mission dictionnary can be replace by "payload" associated to a mass value
            The combination "emotor" AND "liquid_h2" or "compressed_h2" implies the use of fuel cells
            The category is used to select the mode for fuel (energy) mission reserve computation
            The effect of cruise altitude will only impact the amount of fuel (energy) during mission climb

            If only one key among "npax" and "payload" is present, self.mpax will keep the value given by the model
            Il "payload_max" is not present, self.max_payload_factor will keep the value given by the model
            "category", "range" and "speed" are compulsory
            The parameter : self.stdm_factor can be estimated from these data only for FUEL airplanes.
            For battery airplanes, it must be given by the user
        """
        if "bpr" not in power_system.keys():
            power_system["bpr"] = None

        design_range, npax, mpax, payload, category, cruise_speed, cruise_altp = self.get_category_data(mission)

        self.mpax = mpax

        mtow_target = mission["mtow"]
        owe_target = mission["owe"]

        if "payload_max" in mission.keys():
            payload_max = mission["payload_max"]
            self.max_payload_factor = payload_max / payload

        altitude_data = self.flight_altitude(category, cruise_altp)
        reserve_data = self.reserve_data(category)

        def fct1(x):
            self.lod_factor = x[0]
            self.stdm_factor = x[1]
            total_power = self.ref_power(mtow_target)
            dict_p = self.owe_performance(payload, mtow_target, design_range, cruise_speed, total_power, power_system, altitude_data, reserve_data)
            dict_s = self.owe_structure(category, npax, mtow_target, design_range, total_power, dict_p["max_fuel"], dict_p["max_energy"], power_system)
            return [owe_target - dict_p["owe"], owe_target - dict_s["owe"]]

        def fct2(x):
            self.lod_factor = x
            total_power = self.ref_power(mtow_target)
            dict_p = self.owe_performance(payload, mtow_target, design_range, cruise_speed, total_power, power_system, altitude_data, reserve_data)
            dict_s = self.owe_structure(category, npax, mtow_target, design_range, total_power, dict_p["max_fuel"], dict_p["max_energy"], power_system)
            return owe_target - dict_s["owe"]

        ac = self.design_from_mtow(power_system, mission)

        if power_system["energy_type"] != self.battery:
            x_ini = [ac["aero_eff_factor"], ac["stdm_factor"]]
            output_dict = fsolve(fct1, x0=x_ini, args=(), full_output=True)
            if (output_dict[2] != 1): raise Exception("Convergence problem")
            self.lod_factor = output_dict[0][0]
            self.stdm_factor = output_dict[0][1]
        else:
            x_ini = ac["aero_eff_factor"]
            output_dict = fsolve(fct2, x0=x_ini, args=(), full_output=True)
            if (output_dict[2] != 1): raise Exception("Convergence problem")
            self.lod_factor = output_dict[0][0]

        total_power = self.ref_power(mtow_target)
        max_power = total_power / power_system["engine_count"]
        dict_p = self.owe_performance(payload, mtow_target, design_range, cruise_speed, total_power, power_system, altitude_data, reserve_data)
        dict_s = self.owe_structure(category, npax, mtow_target, design_range, total_power, dict_p["max_fuel"], dict_p["max_energy"], power_system)

        this_dict = self.total_fuel(mtow_target, 0., cruise_speed, mtow_target, total_power, power_system, altitude_data, reserve_data)

        payload_max = min(mtow_target - dict_s["owe"] - this_dict["total_fuel"], dict_p["payload"] * self.max_payload_factor)
        mzfw = dict_s["owe"] + payload_max
        mlw = mzfw * self.mlw_factor

        storage_energy_density = dict_p["total_energy"] / (dict_s["energy_storage_mass"] + dict_p["total_fuel"])

        propulsion_power_density = total_power / (dict_s["propulsion_mass"] + dict_s["fuel_cell_system_mass"])

        wtc = self.wake_turbulence_class(mtow_target)

        return self.design_dict(npax, mpax, design_range, cruise_speed, category, max_power, total_power, mtow_target, mzfw, mlw, payload_max,
                            power_system, mission, altitude_data, reserve_data, dict_p, dict_s,
                            storage_energy_density, propulsion_power_density, wtc)

    def design_dict(self, npax, mpax, nominal_range, cruise_speed, category, max_power, total_power, mtow, mzfw, mlw, payload_max,
                    power_system, mission, altitude_data, reserve_data, dict_p, dict_s,
                    storage_energy_density, propulsion_power_density, wtc):
        """Centralize all airplane characteristics into a dictionary
        """
        if cruise_speed > 1: speed_type = "tas"
        else: speed_type = "mach"
        altp = altitude_data["mission"]
        pamb, tamb, g = phd.atmosphere_g(altp, self.disa)
        tas, mach = self.get_tas(tamb, cruise_speed, speed_type)

        return {"airplane_type": category,
                "npax": npax,
                "mpax": mpax,
                "delta_payload": self.delta_payload,
                "payload": dict_p["payload"],
                "mission": mission,
                "max_payload_factor" : self.max_payload_factor,

                "nominal_range": nominal_range,
                "cruise_speed": cruise_speed,
                "cruise_tas": tas,
                "nominal_time": nominal_range / tas,
                "altitude_data": altitude_data,
                "reserve_data": reserve_data,
                "mission_fuel": dict_p["mission_fuel"],
                "reserve_fuel": dict_p["reserve_fuel"],
                "total_fuel": dict_p["total_fuel"],
                "fuel_consumption": (dict_p["mission_fuel"] / dict_s["fuel_density"]) / npax / nominal_range,
                "mission_enrg": dict_p["mission_enrg"],
                "reserve_enrg": dict_p["reserve_enrg"],
                "total_energy": dict_p["total_energy"],
                "enrg_consumption": dict_p["mission_enrg"] / npax / nominal_range,

                "n_engine": power_system["engine_count"],
                "by_pass_ratio": power_system["bpr"],
                "max_power": max_power,
                "total_power": total_power,
                "power_system": power_system,

                "mtow": mtow,
                "mlw": mlw,
                "mzfw": mzfw,
                "payload_max": payload_max,
                "owe": dict_s["owe"],
                "op_item": dict_s["op_item"],
                "mwe": dict_s["mwe"],
                "furnishing": dict_s["furnishing"],
                "std_mwe": dict_s["std_mwe"],
                "propulsion_mass": dict_s["propulsion_mass"],
                "energy_storage_mass": dict_s["energy_storage_mass"],
                "fuel_cell_system_mass": dict_s["fuel_cell_system_mass"],
                "basic_mwe": dict_s["basic_mwe"],
                "stdm_factor": dict_s["stdm_factor"],
                "stdm_shift": dict_s["stdm_shift"],

                "storage_energy_density": storage_energy_density,
                "propulsion_power_density": propulsion_power_density,
                "aero_eff_factor": self.lod_factor,
                "aerodynamic_efficiency": dict_p["aerodynamic_efficiency"],
                "propulsion_system_efficiency": dict_p["propulsion_system_efficiency"],
                "structural_factor": dict_s["owe"] / mtow,

                "wake_turbulence_class": wtc,

                "pk_o_mass": npax * nominal_range / dict_s["owe"],
                "pk_o_enrg": npax * nominal_range / dict_p["total_energy"]}

    def operating_cost(self, ac_dict, traffic_zone="west_bound"):
        """Estimate operating costs (coc & doc, from Thorbeck methodology)
        """
        cd = self.cost_data
        td = self.tech_data

        engine_type = ac_dict["power_system"]["engine_type"]
        energy_type = ac_dict["power_system"]["energy_type"]

        n_pax = ac_dict["npax"]
        m_pax = self.get_pax_allowance(ac_dict["airplane_type"])

        # Fly cost mission
        cost_range = self.cost_range[ac_dict["airplane_type"]]
        this_dict = self.fly_distance(ac_dict, cost_range, n_pax, mode="pax")
        mission_enrg = this_dict["mission_enrg"]
        mission_time = this_dict["mission_time"]

        mtow = ac_dict["mtow"]
        owe = ac_dict["owe"]

        n_engine = ac_dict["n_engine"]
        max_power = ac_dict["max_power"]
        cruise_tas = ac_dict["cruise_tas"]

        flight_cycle_count = self.yearly_utilization(mission_time)

        m_airframe = ac_dict["basic_mwe"] + ac_dict["furnishing"] + ac_dict["op_item"]
        airframe_price = cd["airframe_mass_price"] * m_airframe

        battery_yearly_capital_cost = 0
        fuel_cell_price = 0
        tank_price = 0

        if engine_type == self.emotor:
            engine_price = td["emotor_power_price"] * ac_dict["max_power"] * n_engine
            if energy_type in [self.gh2, self.lh2]:
                fuel_cell_price = td["fuel_cell_power_price"] * self.power_density[self.fuel_cell] * ac_dict["fuel_cell_system_mass"]
        else:
            engine_price = cd["thermal_engine_mass_price"] * ac_dict["propulsion_mass"]

        if energy_type in [self.lh2, self.lch4, self.lnh3]:
            tank_price = ac_dict["energy_storage_mass"] * td["lh2_tank_mass_price"]
        elif energy_type == self.gh2:
            tank_price = ac_dict["energy_storage_mass"] * td["gh2_tank_mass_price"]
        elif energy_type == self.battery:
            battery_price = ac_dict["energy_storage_mass"] * self.battery_enrg_density * td["battery_capacity_price"]
            battery_depreciation_period = td["battery_lifetime_cycle"] / flight_cycle_count
            fac = (1 / (1 + cd["interest_rate"])) ** battery_depreciation_period
            battery_annuity_factor = cd["interest_rate"] * (1 - cd["residual_value_factor"] * fac) / (1 - fac)
            battery_yearly_capital_cost = battery_price * (battery_annuity_factor + cd["insurance_rate"])

        slst = max_power / (0.1 * cruise_tas)   # Assuming 10% of cruise speed is representative of a low speed reference

        fac = (1 / (1 + cd["interest_rate"])) ** cd["depreciation_period"]
        annuity_factor = cd["interest_rate"] * (1 - cd["residual_value_factor"] * fac) / (1 - fac)
        yearly_capital_cost =  (airframe_price + engine_price + fuel_cell_price + tank_price) * (annuity_factor + cd["insurance_rate"]) \
                              + battery_yearly_capital_cost

        yearly_crew_cost = cd["crew_complement"] * (cd["flight_attd_salary"] * self.flight_attd_count(n_pax) + cd["flight_crew_salary"])

        block_time_hour = mission_time / 3600
        airframe_material_cost = (owe / 1000) * (0.21 * block_time_hour + 13.7) + 57.5
        airframe_labor_cost = cd["labor_cost"] * (1 + cd["burden_factor"]) * ((0.655 + 0.01 * (owe / 1000)) * block_time_hour + 0.254 + 0.01 * (owe / 1000))
        engine_maintenance_cost = n_engine * (1.5 * unit.convert_to("kgf", slst) / 1000 + 30.5 * block_time_hour + 10.6)

        if engine_type == self.emotor:
            engine_maintenance_cost = engine_maintenance_cost * td["emotor_maintenance_factor"]

        flight_maintenance_cost = airframe_material_cost + airframe_labor_cost + engine_maintenance_cost

        yearly_flight_cost = (mission_enrg * self.energy_price[energy_type] +
                             m_pax * n_pax * cd["handling_fees"] +
                             mtow * cd["landing_fees"] +
                             self.traffic_zone_factor[traffic_zone] * (cost_range / 1000) * np.sqrt(mtow / 50000) +
                             flight_maintenance_cost) * flight_cycle_count

        yearly_cash_operating_cost = yearly_crew_cost + yearly_flight_cost
        yearly_direct_operating_cost = yearly_cash_operating_cost + yearly_capital_cost

        flight_cash_operating_cost = yearly_cash_operating_cost / flight_cycle_count
        flight_direct_operating_cost = yearly_direct_operating_cost / flight_cycle_count

        cost_breakdown = {"annuity_factor": annuity_factor,
                          "flight_cycle_count": np.floor(flight_cycle_count),
                          "airframe_price": airframe_price,
                          "engine_price": engine_price,
                          "fuel_cell_price": fuel_cell_price,
                          "tank_price": tank_price,
                          "battery_yearly_capital_cost": battery_yearly_capital_cost,
                          "yearly_capital_cost": yearly_capital_cost,
                          "yearly_crew_cost": yearly_crew_cost,
                          "airframe_material_cost": airframe_material_cost,
                          "airframe_labor_cost": airframe_labor_cost,
                          "engine_maintenance_cost": engine_maintenance_cost,
                          "yearly_flight_cost": yearly_flight_cost,
                          "yearly_cash_operating_cost": yearly_cash_operating_cost,
                          "yearly_direct_operating_cost": yearly_direct_operating_cost,
                          "flight_cash_operating_cost": flight_cash_operating_cost,
                          "flight_direct_operating_cost": flight_direct_operating_cost}
        return cost_breakdown

    def print_operating_cost(self, this_dict):
        print("Operating cost")
        print("=======================================================================================================")
        print("    Annuity factor = ", "%.5f" % this_dict["annuity_factor"])
        print("Flight cycle count = ", "%.0f" % this_dict["flight_cycle_count"])
        print("    Airframe price = ", "%.3f" % (this_dict["airframe_price"]*1.e-6), " M$")
        print("      Engine price = ", "%.3f" % (this_dict["engine_price"]*1.e-6), " M$")
        print("   Fuel cell price = ", "%.3f" % (this_dict["fuel_cell_price"]*1.e-3), " k$")
        print("        Tank price = ", "%.3f" % (this_dict["tank_price"]*1.e-3), " k$")
        print("")
        print("Battery yearly capital cost = ", "%.3f" % (this_dict["battery_yearly_capital_cost"]*1.e-3), " k$")
        print("  Total yearly capital cost = ", "%.3f" % (this_dict["yearly_capital_cost"]*1.e-6), " M$")
        print("     Total yearly crew cost = ", "%.3f" % (this_dict["yearly_crew_cost"]*1.e-6), " M$")
        print("")
        print(" Airframe material cost (one flight) = ", "%.1f" % this_dict["airframe_material_cost"], " $")
        print("    Airframe labor cost (one flight) = ", "%.1f" % this_dict["airframe_labor_cost"], " $")
        print("Engine maintenance cost (one flight) = ", "%.1f" % this_dict["engine_maintenance_cost"], " $")
        print("            Total yearly flight cost = ", "%.3f" % (this_dict["yearly_flight_cost"]*1.e-6), " M$")
        print("")
        print("  Yearly Cash Operating Cost = ", "%.3f" % (this_dict["yearly_cash_operating_cost"]*1.e-6), " M$")
        print("Yearly Direct Operating Cost = ", "%.3f" % (this_dict["yearly_direct_operating_cost"]*1.e-6), " M$")
        print("")
        print("  Flight Cash Operating Cost = ", "%.0f" % this_dict["flight_cash_operating_cost"], " $")
        print("Flight Direct Operating Cost = ", "%.0f" % this_dict["flight_direct_operating_cost"], " $")

    def print_design(self, this_dict, name=None):
        """Print the characteristics of a given airplane
        """
        st.write("")
        if name != None:
            st.write(name)
        st.write("=============================================================================")
        st.write("Propulsion system definition")
        st.write("  Energy type = ", this_dict["power_system"]["energy_type"])
        st.write("  Engine type = ", this_dict["power_system"]["engine_type"])
        st.write("  Thruster type = ", this_dict["power_system"]["thruster_type"])
        st.write("  Engine count = ", "%.0f" % this_dict["n_engine"])
        st.write("  By Pass Ratio = ", this_dict["by_pass_ratio"])
        st.write("")
        st.write("Design mission definition")
        st.write("  Category = ", this_dict["airplane_type"])
        st.write("  Number of passenger = ", "%.0f" % this_dict["npax"])
        st.write("  Design range = ", "%.0f" % unit.convert_to("km", this_dict["nominal_range"]), " km")
        if this_dict["cruise_speed"] > 1:
            st.write("  Cruise speed = ", "%.1f" % unit.convert_to("km/h", this_dict["cruise_speed"]), " km/h")
        else:
            st.write("  Cruise Mach = ", "%.2f" % this_dict["cruise_speed"])
        st.write("  Cruise altitude = ", "%.1f" % unit.convert_to("m", this_dict["altitude_data"]["mission"]), " m")
        st.write("-----------------------------------------------------------------------------")
        st.write("Mass breakdown")
        st.write("  MTOW = ", "%.0f" % this_dict["mtow"], " kg")
        st.write("")
        st.write("  MZFW = ", "%.0f" % this_dict["mzfw"], " kg")
        st.write("  Maximum payload = ", "%.0f" % this_dict["payload_max"], " kg")
        st.write("  Maximum payload factor = ", "%.3f" % this_dict["max_payload_factor"])
        st.write("")
        st.write("  OWE = ", "%.0f" % this_dict["owe"], " kg")
        st.write("  Operator items = ", "%.0f" % this_dict["op_item"], " kg")
        st.write("")
        st.write("  MWE = ", "%.0f" % this_dict["mwe"], " kg")
        st.write("  Furnishing = ", "%.0f" % this_dict["furnishing"], " kg")
        st.write("  Standard MWE = ", "%.0f" % this_dict["std_mwe"], " kg")
        st.write("  Propulsion mass = ", "%.0f" % this_dict["propulsion_mass"])
        st.write("  Energy storage mass = ", "%.0f" % this_dict["energy_storage_mass"])
        st.write("  Fuel cell system mass = ", "%.0f" % this_dict["fuel_cell_system_mass"])
        st.write("  Basic MWE = ", "%.0f" % this_dict["basic_mwe"], " kg")
        st.write("  MWE factor = ", "%.3f" % this_dict["stdm_factor"])
        st.write("  MWE sfift = ", "%.0f" % this_dict["stdm_shift"], " kg")
        st.write("-----------------------------------------------------------------------------")
        st.write("Design mission output")
        st.write("  Nominal pax mass allowance = ", "%.1f" % this_dict["mpax"], " kg")
        st.write("  Nominal payload delta = ", "%.0f" % this_dict["delta_payload"], " kg")
        st.write("  Nominal payload = ", "%.0f" % this_dict["payload"], " kg")
        st.write("  Nominal mission time = ", "%.1f" % unit.h_s(this_dict["nominal_time"]), " h")
        st.write("")
        st.write("  Mission fuel = ", "%.0f" % this_dict["mission_fuel"], " kg")
        st.write("  Reserve fuel = ", "%.0f" % this_dict["reserve_fuel"], " kg")
        st.write("  Total fuel = ", "%.0f" % this_dict["total_fuel"], " kg")
        st.write("  Fuel consumption = ", "%.2f" % unit.convert_to("L", this_dict["fuel_consumption"] * unit.m_km(100)), " L/pax/100km")
        st.write("")
        st.write("  Mission energy = ", "%.3f" % unit.MWh_J(this_dict["mission_enrg"]), " MWh")
        st.write("  Reserve energy = ", "%.3f" % unit.MWh_J(this_dict["reserve_enrg"]), " MWh")
        st.write("  Total energy = ", "%.3f" % unit.MWh_J(this_dict["total_energy"]), " MWh")
        st.write("  Energy consumption = ", "%.2f" % unit.kWh_J(this_dict["enrg_consumption"] * unit.m_km(100)), " kWh/pax/100km")
        st.write("")
        st.write("  Wake Turbulence Category = ", this_dict["wake_turbulence_class"])
        st.write("-----------------------------------------------------------------------------")
        st.write("Factors & Efficiencies")
        st.write("  Max power = ", "%.3f" % unit.kW_W(this_dict["max_power"]), " MW")
        st.write("")
        st.write("  Standard mass factor", "%.4f" % this_dict["stdm_factor"])
        st.write("  Aerodynamic efficiency factor", "%.4f" % this_dict["aero_eff_factor"])
        st.write("")
        st.write("  Aerodynamic efficiency (L/D)", "%.2f" % this_dict["aerodynamic_efficiency"])
        st.write("  Propulsion system efficiency", "%.3f" % this_dict["propulsion_system_efficiency"])
        st.write("  Storage energy density = ", "%.0f" % unit.Wh_J(this_dict["storage_energy_density"]), " Wh/kg")
        st.write("  Propulsion power density = ", "%.2f" % unit.kW_W(this_dict["propulsion_power_density"]), " kW/kg")
        st.write("")
        st.write("  Structural factor (OWE/MTOW) = ", "%.2f" % this_dict["structural_factor"])
        st.write("  Energy efficiency factor, P.K/E = ", "%.2f" % unit.convert_to("km/kWh", this_dict["pk_o_enrg"]), " pax.km/kWh")
        st.write("  Mass efficiency factor, P.K/M = ", "%.2f" % unit.convert_to("km/kg", this_dict["pk_o_mass"]), " pax.km/kg")

        # st.write(" Maximum mass efficiency factor, P.K/M max = ", "%.2f" % unit.convert_to("km/kg", this_dict["pk_o_mass_max"]), " pax.km/kg")
        # st.write(" Minimum mass efficiency factor, P.K/M min = ", "%.2f" % unit.convert_to("km/kg", this_dict["pk_o_mass_min"]), " pax.km/kg")

    #-------------------------------------------------------------------------------------------------------------------
    """Methods to fly the airplane on given situations
    """
    def fly_tow_n_distance(self, ac_dict, tow, distance):
        """Compute a mission from tow & distance
        """
        altitude_data = ac_dict["altitude_data"]
        cruise_speed = ac_dict["cruise_speed"]

        mtow = ac_dict["mtow"]
        owe = ac_dict["owe"]
        total_power = ac_dict["total_power"]
        power_system = ac_dict["power_system"]
        reserve_data = ac_dict["reserve_data"]

        this_dict = self.total_fuel(tow, distance, cruise_speed, mtow, total_power, power_system, altitude_data, reserve_data)
        payload = tow - owe - this_dict["total_fuel"]
        this_dict["payload"] = payload
        this_dict["pk_o_mass"] = (payload / ac_dict["mpax"]) * distance / owe
        this_dict["pk_o_enrg"] = (payload / ac_dict["mpax"]) * distance / this_dict["total_enrg"]
        return this_dict

    def fly_tow(self, ac_dict, tow, input, mode="pax"):
        """Compute a mission from tow & payload
        """
        if mode == "pax":
            payload = input * ac_dict["mpax"]
            npax = input
        elif mode == "kg":
            payload = input
            npax = payload / ac_dict["mpax"]
        else:
            raise Exception("input_type is unknown")

        altitude_data = ac_dict["altitude_data"]
        cruise_speed = ac_dict["cruise_speed"]

        mtow = ac_dict["mtow"]
        owe = ac_dict["owe"]
        total_power = ac_dict["total_power"]
        power_system = ac_dict["power_system"]
        reserve_data = ac_dict["reserve_data"]

        def fct(distance):
            this_dict = self.total_fuel(tow, distance, cruise_speed, mtow, total_power, power_system, altitude_data, reserve_data)
            if power_system["energy_type"] != self.battery:
                y = tow - (owe + payload + this_dict["total_fuel"])
            else:
                y = ac_dict["total_energy"] - this_dict["total_enrg"]
            return y

        dist_ini = 0.75 * ac_dict["nominal_range"]
        output_dict = fsolve(fct, x0=dist_ini, args=(), full_output=True)
        if (output_dict[2] != 1): raise Exception("Convergence problem")

        distance = output_dict[0][0]

        this_dict = self.total_fuel(tow, distance, cruise_speed, mtow, total_power, power_system, altitude_data, reserve_data)
        this_dict["payload"] = payload
        this_dict["pk_o_mass"] = npax * distance / owe
        this_dict["pk_o_enrg"] = npax * distance / this_dict["total_enrg"]
        return this_dict

    def fly_distance(self, ac_dict, distance, input, mode="pax"):
        """Compute a mission from distance & payload
        """
        if mode == "pax":
            payload = input * ac_dict["mpax"]
            npax = input
        elif mode == "kg":
            payload = input
            npax = payload / ac_dict["mpax"]
        else:
            raise Exception("input_type is unknown")

        altitude_data = ac_dict["altitude_data"]
        cruise_speed = ac_dict["cruise_speed"]

        mtow = ac_dict["mtow"]
        owe = ac_dict["owe"]
        total_power = ac_dict["total_power"]
        power_system = ac_dict["power_system"]
        reserve_data = ac_dict["reserve_data"]

        def fct(tow):
            this_dict = self.total_fuel(tow, distance, cruise_speed, mtow, total_power, power_system, altitude_data, reserve_data)
            return tow - (owe + payload + this_dict["total_fuel"])

        if power_system["energy_type"] != self.battery:
            tow_ini = 0.75 * mtow
            output_dict = fsolve(fct, x0=tow_ini, args=(), full_output=True)
            if (output_dict[2] != 1): raise Exception("Convergence problem")
            tow = output_dict[0][0]
        else:
            tow = owe + payload

        this_dict = self.total_fuel(tow, distance, cruise_speed, mtow, total_power, power_system, altitude_data, reserve_data)
        this_dict["payload"] = payload
        this_dict["pk_o_mass"] = npax * distance / owe
        this_dict["pk_o_enrg"] = npax * distance / this_dict["total_enrg"]
        return this_dict

    def print_mission(self, this_dict, title=""):
        """Print the output of a mission calculation
        """
        print("")
        print(title)
        print("=============================================================================")
        print("        Distance = ", "%.0f" % unit.convert_to("km", this_dict["distance"]), " km")
        print("")
        print(" Take Off Weight = ", "%.0f" % this_dict["tow"], " kg")
        print("         Payload = ", "%.0f" % this_dict["payload"], " kg")
        print("")
        print("      Total fuel = ", "%.0f" % (this_dict["mission_fuel"] + this_dict["reserve_fuel"]), " kg")
        print("    Mission fuel = ", "%.0f" % this_dict["mission_fuel"], " kg")
        print("    Reserve fuel = ", "%.0f" % this_dict["reserve_fuel"], " kg")
        print("")
        print("    Total energy = ", "%.0f" % unit.kWh_J(this_dict["mission_enrg"] + this_dict["reserve_enrg"]), " kWh")
        print("  Mission energy = ", "%.0f" % unit.kWh_J(this_dict["mission_enrg"]), " kWh")
        print("  Reserve energy = ", "%.0f" % unit.kWh_J(this_dict["reserve_enrg"]), " kWh")

    #-------------------------------------------------------------------------------------------------------------------
    """Methods to build and manage the Payload-Range diagram
    """
    def build_payload_range(self, ac_dict, mode="kg"):
        """Compute payload - range characteristics and add them to ac_dict
        mode = "mass" : payload will be retrieved in kg
        mode = "pax : payload will be retrieved in pax
        """
        plr = {}
        mtow = ac_dict["mtow"]

        this_dict = self.fly_tow(ac_dict, mtow, ac_dict["payload_max"], mode="kg")
        ac_dict["range_pl_max"] = this_dict["distance"]  # Range for maximum payload mission
        plr["max_payload_mission"] = {"payload": ac_dict["payload_max"], "range": ac_dict["range_pl_max"]}

        payload_fuel_max = ac_dict["payload"] + ac_dict["total_fuel"] * (1 - self.max_fuel_factor)
        this_dict = self.fly_tow(ac_dict, mtow, payload_fuel_max, mode="kg")
        ac_dict["payload_fuel_max"] = payload_fuel_max  # Payload for max fuel mission
        ac_dict["range_fuel_max"] = this_dict["distance"]  # Range for max fuel mission
        plr["max_fuel_mission"] = {"payload": ac_dict["payload_fuel_max"], "range": ac_dict["range_fuel_max"]}

        tow_zero_payload = mtow - payload_fuel_max
        this_dict = self.fly_tow(ac_dict, tow_zero_payload, 0., mode="kg")
        ac_dict["range_no_pl"] = this_dict["distance"]  # Range for zero payload mission
        plr["zero_payload_mission"] = {"payload": 0, "range": ac_dict["range_no_pl"]}

        if mode == "pax":
            plr["max_payload_mission"]["payload"] = round( plr["max_payload_mission"]["payload"] / self.mpax_dict[ac_dict["airplane_type"]])
            plr["max_fuel_mission"]["payload"] = round( plr["max_fuel_mission"]["payload"] / self.mpax_dict[ac_dict["airplane_type"]])
            plr["zero_payload_mission"]["payload"] = round( plr["zero_payload_mission"]["payload"] / self.mpax_dict[ac_dict["airplane_type"]])
        elif mode == "kg":
            pass
        else:
            raise Exception["mode value is unknown"]

        return plr

    def print_payload_range(self, this_dict):
        st.write("")
        st.write("      Maximum payload = ", "%.0f" % this_dict["payload_max"], " kg")
        st.write(" Range of max payload = ", "%.0f" % unit.convert_to("km", this_dict["range_pl_max"]), " km")
        st.write("")
        st.write("      Nominal payload = ", "%.0f" % this_dict["payload"], " kg")
        st.write("        Nominal range = ", "%.0f" % unit.convert_to("km", this_dict["nominal_range"]), " km")
        st.write("")
        st.write("     Max fuel payload = ", "%.0f" % this_dict["payload_fuel_max"], " kg")
        st.write("       Max fuel range = ", "%.0f" % unit.convert_to("km", this_dict["range_fuel_max"]), " km")
        st.write("")
        st.write("   Zero payload range = ", "%.0f" % unit.convert_to("km", this_dict["range_no_pl"]), " km")
        st.write("")

    def draw_payload_range(self, ac_dict, color=None, label=None, index=None, mode="kg"):
        """Print a single payload - range diagram
        """
        if label is None:
            plot_title = "Phantom Design"
            window_title = "Payload - Range"
            fig, axes = plt.subplots(1, 1)
            fig.canvas.manager.set_window_title(plot_title)
            fig.suptitle(window_title, fontsize=16)

        if mode == "pax":
            payload = [round(ac_dict["payload_max"] / ac_dict["mpax"]),
                       round(ac_dict["payload_max"] / ac_dict["mpax"]),
                       round(ac_dict["payload_fuel_max"] / ac_dict["mpax"]),
                       0.]
            nominal = [round(ac_dict["payload"] / ac_dict["mpax"]),
                       unit.km_m(ac_dict["nominal_range"])]
        elif mode == "kg":
            payload = [ac_dict["payload_max"],
                       ac_dict["payload_max"],
                       ac_dict["payload_fuel_max"],
                       0.]
            nominal = [ac_dict["payload"],
                       unit.km_m(ac_dict["nominal_range"])]
        else:
            raise Exception["mode value is unknown"]

        range = [0.,
                 unit.km_m(ac_dict["range_pl_max"]),
                 unit.km_m(ac_dict["range_fuel_max"]),
                 unit.km_m(ac_dict["range_no_pl"])]

        if color is not None:
            plt.plot(range, payload, linewidth=2, label=label, color=color)
        else:
            plt.plot(range, payload, linewidth=2, label=label)
        plt.scatter(range[1:], payload[1:], marker="+", c="orange", s=100)
        plt.scatter(nominal[1], nominal[0], marker="o", c="green", s=50)
        if index is not None:
            plt.annotate(index, (nominal[1], nominal[0]), color="color", fontsize=10)

        if label is None:
            plt.ylabel('Payload (kg)', fontsize=14)
            plt.xlabel('Range (km)', fontsize=14)
            plt.grid(True)
            st.pyplot(fig)


    def payload_range_graph(self, graph_list, acname, color=None, label=None, index=None, mode="kg"):
        plot_title = "Payload - Range"
        window_title = "Payload - Range"
        fig, ax = plt.subplots(figsize=(8, 5))
        fig.canvas.manager.set_window_title(window_title)
        fig.suptitle(plot_title, fontsize=16)


        for i in range(len(graph_list)):
            ac_dict = graph_list[i]
            color = graph_list[i].get("color", None)
            label = graph_list[i].get("label", None)

            if mode == "pax":
                payload = [
                    round(ac_dict["payload_max"] / ac_dict["mpax"]),
                    round(ac_dict["payload_max"] / ac_dict["mpax"]),
                    round(ac_dict["payload_fuel_max"] / ac_dict["mpax"]),
                    0.]
                nominal = [
                    round(ac_dict["payload"] / ac_dict["mpax"]),
                    unit.km_m(ac_dict["nominal_range"])]
            elif mode == "kg":
                payload = [
                    ac_dict["payload_max"],
                    ac_dict["payload_max"],
                    ac_dict["payload_fuel_max"],
                    0.]
                nominal = [
                    ac_dict["payload"],
                    unit.km_m(ac_dict["nominal_range"])]
            else:
                raise ValueError("Unknown mode value. Use 'kg' or 'pax'.")

            range_vals = [0.,
                unit.km_m(ac_dict["range_pl_max"]),
                unit.km_m(ac_dict["range_fuel_max"]),
                unit.km_m(ac_dict["range_no_pl"])]

            if color is not None:
                ax.plot(range_vals, payload, linewidth=2, label=acname[i], color=color)
            else:
                ax.plot(range_vals, payload, linewidth=2, label=acname[i])
            ax.scatter(range_vals[1:], payload[1:], marker="+", c="orange", s=100)
            ax.scatter(nominal[1], nominal[0], marker="o", c="green", s=50)

        ax.set_ylabel('Payload (kg)' if mode == "kg" else 'Payload (pax)', fontsize=14)
        ax.set_xlabel('Range (km)', fontsize=14)
        ax.grid(True)
        ax.legend()
        plt.show()
        return st.pyplot(fig)


    def set_multi_payload_range(self, mode="kg"):
        """Open a graph for multiple payload - range diagrams
        And let the user to draw other things into it
        """
        plot_title = "GAM Design"
        window_title = "Payload - Range"
        fig, axes = plt.subplots(1, 1)
        fig.canvas.manager.set_window_title(plot_title)
        fig.suptitle(window_title, fontsize=16)

    def show_multi_payload_range(self, mode="kg"):
        """Display a graph for multiple payload - range diagrams
        """
        if mode == "pax":
            plt.ylabel('Payload (pax)', fontsize=14)
        elif mode == "kg":
            plt.ylabel('Payload (kg)', fontsize=14)
        else:
            raise Exception["mode value is unknown"]

        plt.xlabel('Range (km)', fontsize=14)
        plt.grid(True)
        plt.legend(fontsize=10, bbox_to_anchor=(1, 1), loc="upper left")
        plt.tight_layout()
        plt.show()

    def is_in_plr(self, ac_dict, distance, input, mode="pax"):
        """Detects if a mission is possible
        """
        if mode == "pax":
            payload = input * ac_dict["mpax"]
        elif mode == "kg":
            payload = input
        else:
            raise Exception("input_type is unknown")

        out_dict = {"capa": True, "dist": True}

        c1 = ac_dict["payload_max"] - payload  # Max payload limit
        c2 = (payload - ac_dict["payload_fuel_max"]) * (ac_dict["range_pl_max"] - ac_dict["range_fuel_max"]) \
             - (ac_dict["payload_max"] - ac_dict["payload_fuel_max"]) * (distance - ac_dict["range_fuel_max"])  # Max Take off weight limit
        c3 = payload * (ac_dict["range_fuel_max"] - ac_dict["range_no_pl"]) \
             - ac_dict["payload_max"] * (distance - ac_dict["range_no_pl"])  # Max fuel limit
        c4 = ac_dict["range_no_pl"] - distance  # Max range limit

        if ((c1 < 0. or c2 < 0. or c3 < 0.) and c4 >= 0.):  # Out of PLR because of capacity
            out_dict["capa"] = False
        elif (c1 >= 0. and c4 < 0.):  # Out of PLR because of range
            out_dict["dist"] = False
        elif (c1 < 0. and c4 < 0.):  # Out of PLR because of range and capacity
            out_dict["capa"] = False
            out_dict["dist"] = False
        return out_dict

    def max_capacity(self, ac_dict, distance, mode="pax"):
        """Retrieve the maximum capacity for a given range

        :param ac_dict: Airplane dictionary
        :param distance: Distance to fly
        :return:  capacity
        """
        if distance <= ac_dict["range_pl_max"]:
            payload = ac_dict["payload_max"]
            capacity = np.floor(ac_dict["payload_max"] / ac_dict["mpax"])
        elif ac_dict["range_pl_max"] < distance and distance <= ac_dict["range_fuel_max"]:
            payload = ac_dict["payload_fuel_max"] \
                      + (ac_dict["payload_max"] - ac_dict["payload_fuel_max"]) * (distance - ac_dict["range_fuel_max"]) \
                                                                               / (ac_dict["range_pl_max"] - ac_dict["range_fuel_max"])
            capacity = np.floor(payload / ac_dict["mpax"])
        elif ac_dict["range_fuel_max"] < distance and distance <= ac_dict["range_no_pl"]:
            payload = ac_dict["payload_fuel_max"] * (distance - ac_dict["range_no_pl"]) \
                                                  / (ac_dict["range_fuel_max"] - ac_dict["range_no_pl"])
            capacity = np.floor(payload / ac_dict["mpax"])
        else:
            capacity = 0.
        if mode == "pax":
            return capacity
        elif mode == "kg":
            return payload
        else:
            raise Exception["mode value is unknown"]

    def max_distance(self, ac_dict, input, mode="pax"):
        """Retrieve the maximum range for a given number of passenger or payload mass

        :param ac_dict: Airplane dictionary
        :param npax: Number of passenger
        :return:  distance
        """
        if mode == "pax":
            payload = input * ac_dict["mpax"]
        elif mode == "kg":
            payload = input
        else:
            raise Exception("input_type is unknown")

        if ac_dict["payload_max"] < payload:
            distance = 0.
        elif ac_dict["payload_fuel_max"] < payload and payload <= ac_dict["payload_max"]:
            distance = ac_dict["range_fuel_max"] + (payload - ac_dict["payload_fuel_max"]) * (
                    ac_dict["range_pl_max"] - ac_dict["range_fuel_max"]) / (
                               ac_dict["payload_max"] - ac_dict["payload_fuel_max"])
        else:
            distance = ac_dict["range_no_pl"] + payload * (ac_dict["range_fuel_max"] - ac_dict["range_no_pl"]) / \
                       ac_dict["payload_fuel_max"]
        return distance

    #-------------------------------------------------------------------------------------------------------------------
    """Methods to manipulate the airplane data base
    """
    def read_db(file):
        """Read data base and convert to standard units
        WARNING: special treatment for cruise_speed and max_speed which can be Mach number
        """
        raw_data = pd.read_excel(file)  # Load data base as a Pandas data frame
        un = raw_data.iloc[0:2, 0:]  # Take unit structure only
        df = raw_data.iloc[2:, 0:].reset_index(drop=True)  # Remove unit rows and reset index

        for name in df.columns:
            if un.loc[0, name] not in ["string", "int"] and un.loc[1, name] != "mach":
                df[name] = unit.convert_from(un.loc[0, name], list(df[name]))
            if un.loc[0, name] == "string":
                df[name] = [str(s) for s in list(df[name])]
            if un.loc[1, name] == "mach":
                for j in df.index:
                    if df.loc[j, name] > 1.:
                        df.loc[j, name] = float(unit.convert_from(un.loc[0, name], df.loc[j, name]))
        return df, un

    def clean_airplane_database(self, data_file):
        """Remove duplications from the Airplane Database
        """
        df_in, un_in = self.read_db(data_file)
        df = df_in[df_in['airplane_type'] != 'business'].reset_index(drop=True).copy()
        code_list = list(set(df["iata_code"]))
        index_list = [df[df['iata_code'] == c]['mtow'].idxmax() for c in code_list]
        df_out = df.iloc[index_list]

        return df_out

    def get_design_data(self, df, airplane, index="name"):
        """Get design data from data base given as dataframe df
        Can treat multiple request, lists are retrieved
        """
        power_system = []
        design_mission = []
        for ap in airplane:
            df1 = df[df[index] == ap].reset_index(drop=True).copy()
            if df1.shape[0] == 0:
                raise Exception("Unknown index : ", index)

            power_system.append({"energy_type": df1["energy_type"].iloc[0],
                                 "engine_count": df1["n_engine"].iloc[0],
                                 "engine_type": df1["engine_type"].iloc[0],
                                 "thruster_type": df1["thruster_type"].iloc[0],
                                 "bpr": df1["bpr"].iloc[0]})

            design_mission.append({"category": df1["airplane_type"].iloc[0],
                                   "npax": df1["n_pax"].iloc[0],
                                   "speed": df1["cruise_speed"].iloc[0],
                                   "range": df1["nominal_range"].iloc[0],
                                   "altitude": df1["cruise_altitude"].iloc[0]})

        return power_system, design_mission



class GamNtwkPlugIn(object):
    """GAM plugin dealing with route network operations
    """
    # OAG basic fields
    # -----------------------
    # Operating Carrier
    # Published Carrier
    # Flight Number
    # Origin
    # Origin_country_id         added
    # Destination
    # Destination_country_id    added
    # Departure Time
    # Arrival Time
    # Op Days
    # Elapsed Time
    # Distance (KM)
    # Distance          added (m)
    # Stops
    # Equipment
    # Frequency
    # Seats
    # Loading           added (available seat per flight)
    # Time series
    def __init__(self, gam_ac, airplane_code_file=None, airport_database_file=None, oag_file=None, capa_step=20, dist_step=unit.m_km(200)):

        self.gam_ac = gam_ac

        if airplane_code_file is not None and airport_database_file is not None and oag_file is not None:

            self.airplane_code = self.get_data_base(airplane_code_file)

            self.airport_data = self.get_data_base(airport_database_file)

            self.airport_data['latitude'] = self.airport_data['latitude'].multiply(np.pi/180)       # Convert degrees into radians
            self.airport_data['longitude'] = self.airport_data['longitude'].multiply(np.pi/180)     # Convert degrees into radians

            self.oag_df_raw = pd.read_csv(oag_file)

            oag_df_in = self.oag_df_raw.copy()
            oag_df_in['Distance'] = oag_df_in['Distance (KM)'].multiply(1000)
            oag_df_in['Loading'] = oag_df_in['Seats']/oag_df_in['Frequency']
            apt_data = self.airport_data.copy()
            known_apt = set(apt_data["iata_code"])
            apt_data_orig = apt_data.rename(columns={'iata_code': 'Origin', 'country_id': 'Origin_country_id'})
            apt_data_dest = apt_data.rename(columns={'iata_code': 'Destination', 'country_id': 'Destination_country_id'})
            apt_data_orig = apt_data_orig[['Origin', 'Origin_country_id']]
            apt_data_dest = apt_data_dest[['Destination', 'Destination_country_id']]

            oag_df_orig = pd.merge(oag_df_in, apt_data_orig, on=['Origin'])

            self.oag_df = pd.merge(oag_df_orig, apt_data_dest, on=['Destination'])

            apt_fr_o = set(self.oag_df['Origin'])
            apt_fr_d = set(self.oag_df['Destination'])
            apt_fr = apt_fr_o.union(apt_fr_d)

            self.info_dict = {}

            self.info_dict["airport"] = list(apt_fr)
            self.info_dict["unknown_airport"] = list(apt_fr - known_apt)

            ac_data = self.airplane_code.copy()
            ap_code = ac_data[["iata_code", "model"]].drop_duplicates(subset=["iata_code"])
            ap_code.set_index("iata_code", inplace=True)
            flying_set = set(self.oag_df["Equipment"])
            known_set = set(ap_code.index)

            self.info_dict["aircraft"] = list(flying_set)
            self.info_dict["unknown_aircraft"] = list(flying_set - known_set)

            self.info_dict["capa_step"] = capa_step
            self.info_dict["dist_step"] = dist_step
            seats_list = np.arange(0, max(self.oag_df['Loading'])+1.01*capa_step, capa_step)
            range_list = np.arange(0, max(self.oag_df['Distance'])+1.01*dist_step, dist_step)
            bins_list = [seats_list, range_list]
            data_flights = plt.hist2d(self.oag_df['Loading'], self.oag_df['Distance'],
                                      weights = self.oag_df['Frequency'],
                                      bins = bins_list)
            # data_flights[0] : list of nc list of nr values
            # data_flights[1] : list of capacities, nc values from 0 to max capacity
            # data_flights[2] : list of ranges, nr values from 0 to max range
            self.info_dict["flights"] = data_flights
            plt.close()

    def get_data_base(self, file_name):
        df, un = uda.read_db(file_name)
        return df

    def draw_grid(self, file_name, title):
        """Draw the figure of the flight grid and store it in a file

        :param file_name: file to store the figure
        :return:
        """

        fig, ax = plt.subplots()

        table = np.array(self.info_dict["flights"][0])
        capa_list = np.array(self.info_dict["flights"][1])
        range_list = np.array(self.info_dict["flights"][2]) * 1.e-3

        max_val = table.max()
        min_val = table.min() + 0.1

        im = ax.pcolormesh(table,
                           edgecolors='b',
                           linewidth=0.01,
                           cmap=plt.cm.get_cmap("rainbow",10),
                           norm=colors.LogNorm(vmin=min_val, vmax=max_val))

        # im = ax.pcolormesh(table,
        #                    edgecolors='b',
        #                    linewidth=0.01,
        #                    cmap=plt.cm.get_cmap("rainbow",10),
        #                    norm=colors.Normalize(vmin=min_val, vmax=max_val))
        ax = plt.gca()
        ax.set_aspect('equal')
        ax.set_xlabel('Ranges (km)', fontsize=14)
        ax.set_ylabel('Seat capacity', fontsize=14)
        ax.xaxis.set_ticks(range(len(range_list)))
        ax.xaxis.set_ticklabels(range_list, fontsize=8, rotation='vertical')
        ax.yaxis.set_ticks(range(len(capa_list)))
        ax.yaxis.set_ticklabels(capa_list, fontsize=8)
        plt.title(title, fontsize=16)
        plt.grid(True)
        cbar = fig.colorbar(im, ax=ax, orientation='vertical', aspect=40.)
        plt.tight_layout()
        plt.savefig(file_name, dpi=500, bbox_inches='tight')
        plt.show()

    def which_airport(self, airport_df, airport_code, code_type="iata_code"):
        """Return airport names from IATA or ICAO codes
        """
        name_list = []
        for code in airport_code:
            df = airport_df[airport_df[code_type] == code].reset_index(drop=True).copy()
            name_list.append(df["name"].iloc[0])
        return name_list

    #-------------------------------------------------------------------------------------------------------------------
    """Methods to create a default aircraft catalog according to categorization
    """
    def get_default_catalog(self, catalog_count, show_graph=False):
        """Generate a default catalog of airplane according to category data
        The user must specify the number of aircraft in each category (general, commuter, ...) using a dictionary
        Exemple : catalog_count = {"general":1, "commuter":1, "regional":2, "short_medium":2, "long_range":2}
        """
        cat_data = deepcopy(self.gam_ac.category)
        cat_data["origin"] = {"capacity": 0, "distance": 0}
        cat_list = ["origin", self.gam_ac.general, self.gam_ac.commuter, self.gam_ac.regional, self.gam_ac.short_medium, self.gam_ac.long_range]

        catalog = {}
        for i, cat in enumerate(self.gam_ac.category.keys()):
            na = catalog_count[cat]
            for j in range(na):
                dcap = cat_data[cat_list[1 + i]]["capacity"] - cat_data[cat_list[i]]["capacity"]
                capa = cat_data[cat_list[i]]["capacity"] + (dcap / na) * (1 + j)

                ddis = cat_data[cat_list[1 + i]]["distance"] - cat_data[cat_list[i]]["distance"]
                dist = cat_data[cat_list[i]]["distance"] + (ddis / na) * (1 + j)

                power_system = {"energy_type": "kerosene",
                                "engine_count": 2,
                                "engine_type": self.gam_ac.category[cat]["engine_type"],
                                "thruster_type": self.gam_ac.category[cat]["thruster_type"],
                                "bpr": self.gam_ac.category[cat]["bpr"]}

                design_mission = {"category": cat,
                                  "npax": capa,
                                  "speed": self.gam_ac.category[cat]["speed"],
                                  "range": dist,
                                  "altitude": self.gam_ac.flight_altitudes[cat][0]}

                ap_dict = self.gam_ac.design_airplane(power_system, design_mission)
                self.gam_ac.build_payload_range(ap_dict)  # Compute Payload - Range missions and store them into catalog[key]
                catalog[cat + "_" + str(1 + j)] = ap_dict

        if show_graph:
            self.gam_ac.show_catalog_plr(catalog)

        return catalog

    def show_catalog_plr(self, catalog):
        """Display payload range diagrams of all airplane in the catalog
        """
        self.gam_ac.set_multi_payload_range()
        # Draw Payload-Range
        for ap in catalog.keys():
            color = str(self.gam_ac.colors[catalog[ap]["airplane_type"]])
            self.gam_ac.draw_payload_range(catalog[ap], color=color, label=ap, index=ap)  # Display diagram

        # Draw category frames
        currentAxis = plt.gca()
        cat_list = list(self.gam_ac.category.keys())
        cat_list.reverse()
        for j, cat in enumerate(cat_list):
            color = str(self.gam_ac.colors[cat])
            dist = self.gam_ac.category[cat]["distance"]
            mpax = self.gam_ac.get_pax_allowance(cat)
            payload = self.gam_ac.category[cat]["capacity"] * mpax
            plt.plot([0, unit.km_m(dist), unit.km_m(dist)], [payload, payload, 0], linewidth=1, color=color)
            # currentAxis.add_patch(Rectangle((0, 0), dist, payload, edgecolor=color, fill=False,  zorder=j/10))

        self.gam_ac.show_multi_payload_range()

    #-------------------------------------------------------------------------------------------------------------------
    """Methods to allocate airplane from a catalog on existing sets of routes
    """
    def fly_catalog(self, catalog):
        airport = {}
        fleet = {}
        fuel = {}
        n_count = [0,0]
        for r in range(len(self.oag_df.index)):  # Loop on routes
            n_pax = self.oag_df.at[r, "Loading"]
            distance = self.oag_df.at[r, "Distance"]
            n_flight = self.oag_df.at[r, "Frequency"]
            fly_able = False
            for ac in catalog.keys():  # Loop on airplanes

                out_dict = self.gam_ac.is_in_plr(catalog[ac], distance, n_pax, mode="pax")

                if out_dict["capa"] and out_dict["dist"]:
                    this_dict = self.gam_ac.fly_distance(catalog[ac], distance, n_pax)  # Compute consumption

                    if catalog[ac]["power_system"]["energy_type"] in fuel.keys():
                        if catalog[ac]["power_system"]["energy_type"] == "battery":
                            fuel["battery"] += this_dict["mission_enrg"] * n_flight
                        else:
                            fuel[catalog[ac]["power_system"]["energy_type"]] += this_dict["mission_fuel"] * n_flight
                    else:
                        if catalog[ac]["power_system"]["energy_type"] == "battery":
                            fuel["battery"] = this_dict["mission_enrg"] * n_flight
                        else:
                            fuel[catalog[ac]["power_system"]["energy_type"]] = this_dict["mission_fuel"] * n_flight

                    fly_able = True
                    self.oag_df.at[r, "Equipment_GAM"] = ac

                    if ac in fleet.keys():
                        fleet[ac]["mean_dist"] = (fleet[ac]["mean_dist"] * fleet[ac]["n_flight"] + distance * n_flight) / (fleet[ac]["n_flight"] + n_flight)
                        fleet[ac]["pk"] += n_flight * n_pax * unit.km_m(distance)
                        fleet[ac]["n_flight"] += n_flight
                    else:
                        if 1 < catalog[ac]["cruise_speed"]:
                            speed = catalog[ac]["cruise_speed"]
                        else:
                            speed = phd.vtas_from_mach(catalog[ac]["altitude_data"]["mission"], 0, catalog[ac]["cruise_speed"])
                        fleet[ac] = {"n_aircraft": 0,
                                     "n_flight": n_flight,
                                     "pk": n_flight * n_pax * unit.km_m(distance),
                                     "mean_dist": distance,
                                     "speed": speed}
                    break

            if not fly_able:
                print("Route n° ", r, " cannot be flown, n_pax = ", n_pax, "  dist = ", "%.0f" % unit.km_m(distance), " km")

            orig = self.oag_df.at[r, "Origin"]
            if orig in airport.keys():
                if "Departure" in airport[orig]:
                    if ac in airport[orig]["Departure"].keys():
                        airport[orig]["Departure"][ac] += n_flight
                    else:
                        airport[orig]["Departure"][ac] = n_flight
                else:
                    airport[orig]["Departure"] = {ac: n_flight}
            else:
                airport[orig] = {"Departure": {ac: n_flight}}

            dest = self.oag_df.at[r, "Destination"]
            if dest in airport.keys():
                if "Arrival" in airport[dest]:
                    if ac in airport[dest]["Arrival"].keys():
                        airport[dest]["Arrival"][ac] += n_flight
                    else:
                        airport[dest]["Arrival"][ac] = n_flight
                else:
                    airport[dest] = {"Arrival": {ac: n_flight}}
            else:
                airport[dest] = {"Arrival": {ac: n_flight}}

            n_count[0] += 1
            n_count[1] += 1
            if 100000 <= n_count[0]:
                print("")
                print(n_count[1])
                n_count[0] = 0

        print("")
        print(n_count[1])

        for ac in fleet.keys():
            block_time = fleet[ac]["mean_dist"] / fleet[ac]["speed"]
            yearly_flights = self.gam_ac.yearly_utilization(block_time)
            fleet[ac]["n_aircraft"] = fleet[ac]["n_flight"] / yearly_flights

        return airport, fleet, fuel




if __name__ == '__main__':

    gam = GAM()

    gam.print_model_data()  # Print model parameters


    print("Design an A320neo like airplane")
    print("===========================================================================================================")

    power_system = {"energy_type": "kerosene", "engine_count": 2, "engine_type": "turbofan", "thruster_type": "fan", "bpr": 12}
    design_mission = {"category": "regional", "npax": 180, "speed": 0.78, "range": unit.convert_from("km", 5500), "altitude": unit.convert_from("ft", 35000)}

    ac_dict = gam.design_airplane(power_system, design_mission)     # Design the airplane
    gam.print_design(ac_dict, name="This plane")                    # Print airplane characteristics


    print("Compute and build the Payload-Range of the airplane")
    print("===========================================================================================================")

    gam.build_payload_range(ac_dict)    # Compute payload-range data and add them in ac_dict
    gam.print_payload_range(ac_dict)    # Print payload-range data
    gam.draw_payload_range(ac_dict)     # Draw the payload-range diagram

    distance = unit.convert_from("km", 850)
    input = 10000
    input_type = "kg"


    print("Estimate operating costs")
    print("===========================================================================================================")

    cost_dict = gam.operating_cost(ac_dict)
    gam.print_operating_cost(cost_dict)

    print("")


    print("Test if a combination of capacity and distance is inside the Payload-Range capability")
    print("===========================================================================================================")

    print("distance = ", unit.convert_to("km", distance), " km")
    print("input = ", input, " ", input_type)
    print("")

    print("is in Payload-Range = ", gam.is_in_plr(ac_dict, distance, input, mode=input_type))     # Check if given distance and payload is feasible

    max_dist = gam.max_distance(ac_dict, input, mode=input_type)
    print("max distance for ", input, " ", input_type, " = ", unit.convert_to("km", "%.0f" % unit.convert_to("km", max_dist)), " km")   # Get the maximum fly-abledistance for a given payload

    max_capa = gam.max_capacity(ac_dict, distance, mode="kg")
    print("max capacity for ", unit.convert_to("km", distance), " km", " = ", max_capa, " kg")     # Get the maximum capacity (in passenger) for a given distance

    print("")


    print("Fly a specific route with a given loading")
    print("===========================================================================================================")

    distance = unit.convert_from("km", 850)
    input = 150
    input_type = "pax"

    print("")
    print("Input for This mission :")
    print("distance = ", unit.convert_to("km", distance), " km")
    print("input = ", input, " ", input_type)

    out_dict = gam.fly_distance(ac_dict, distance, input, mode=input_type)
    gam.print_mission(out_dict, title="This mission")

    print("")


    print("Calibrate the GAM model to match with given aircraft performance")
    print("===========================================================================================================")

    design_mission = {"category": "regional",
                      "npax": 180,
                      "speed": 0.78,
                      "range": unit.convert_from("km", 5500),
                      "altitude": unit.convert_from("ft", 35000),
                      "mtow": 81000,          # maximum take off mass (must be provided for calibration)
                      "owe": 45000,           # operational empty mass(must be provided for calibration)
                      "payload": 19000,       # operational empty mass(must be provided for calibration)
                      "payload_max": 22000,   # operational empty mass(must be provided for calibration)
                      }

    ac_dict = gam.tune_design(power_system, design_mission)

    print("")
    print("Calibrated aero efficiency factor = ", gam.lod_factor)
    print("Calibrated standard mass factor = ", gam.stdm_factor)
    print("Calibrated max payload factor = ", gam.max_payload_factor)
    print("Calibrated pax mass allowance = ", gam.mpax)

    print("")


    print("Check in direct mode")
    print("===========================================================================================================")

    power_system = {"energy_type": "kerosene", "engine_count": 2, "engine_type": "turbofan", "thruster_type": "fan", "bpr": 12}
    design_mission = {"category": "regional", "npax": 180, "speed": 0.78, "range": unit.convert_from("km", 5500), "altitude": unit.convert_from("ft", 35000)}

    ac_dict = gam.design_airplane(power_system, design_mission)     # Design the airplane
    gam.print_design(ac_dict, name="This plane")                    # Print airplane characteristics

    print("")


    print("Create a generic fleet of kerosene aircraft")
    print("===========================================================================================================")
    ntwk = GamNtwkPlugIn(gam)

    catalog_split = {"general": 1, "commuter": 1, "regional": 2, "short_medium": 3, "long_range": 3}

    catalog = ntwk.get_default_catalog(catalog_split)

    # print("-----------------------------------------------------------------------------")
    # for ac in fleet.keys():
    #     gam.print_design(fleet[ac], name=ac)

    ntwk.show_catalog_plr(catalog)