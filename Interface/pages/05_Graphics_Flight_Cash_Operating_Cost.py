import numpy as np
import streamlit as st
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import matplotlib.patches as mpatches

#from gam_utils.physical_data import PhysicalData
#from gam_utils import unit
#from gam_copy import GAM

from draw_domains import find_index#, draw_domains
from doc_vs_techno_commuter_modify import init_commuter
from doc_vs_techno_regional_modify import init_regional
from doc_vs_techno_long_range_modify import init_long
from doc_vs_techno_short_medium_modify import init_short


def pritting_fuel():
    max_fuel_factor = 1.25
    stdm_factor = 1.0
    lod_factor = 1.0

    def plot_domain(ax, init_function, title):
        gam, design_mission, power_system, dist_window, npax_window, criterion = init_function(
            max_fuel_factor, stdm_factor, lod_factor,
            battery_density, fuel_cell_power_density, lh2_tank_index,
            emotor_price, fuel_cell_price, lh2_tank_price, battery_capacity_price,
            battery_price, lh2_price, lch4_price, e_fuel_price
        )
        color_ind, npax_list, dist_list = find_index(
            gam, design_mission, power_system, dist_window, npax_window, criterion
        )

        #im = ax.imshow(color_ind, cmap=cmapa, vmin=0, vmax=len(labels) - 1)
        ax.set_xticks(
            np.linspace(0, len(color_ind), 6).astype(int)
        )
        ax.set_xticklabels(
            np.linspace(dist_list[0], dist_list[-1], num=6).astype(int)
        )
        ax.set_yticks(
            np.linspace(0, len(color_ind[0]), 7).astype(int)
        )
        ax.set_yticklabels(
            np.linspace(npax_list[0], npax_list[-1], num=7).astype(int)[::-1]
        )
        ax.set_title(title, fontsize=12)
        return criterion


    st.sidebar.write("### Select the type of aircraft you want to show:")
    airplane_type = st.sidebar.radio("", ["Commuter", "Regional", "Short Medium", "Long Range", "All type combined"])


    if airplane_type == "Commuter":
        st.header("Graphic for commuter airplane")
        left1, right1 = st.columns(2)

        with left1:
            st.header("Parameters for commuter airplane")

            left12, right12 = st.columns(2)

            with left12:
                # Sliders for Techno Parameters
                battery_density1 = st.slider("Battery Energy Density (Wh/kg)", 500, 1000, 750, 5)
                fuel_cell_power1_density = st.slider("Fuel Cell Power Density (W/kg)", 0.1, 3.0, 1.0, 0.1)
                lh2_tank_index1 = st.slider("LH2 Tank Gravimetric Index", 0.1, 1.0, 0.4, 0.05)

                # Sliders for Techno Cost Parameters
                emotor_price1 = st.slider("eMotor Price (/kW)", 50, 200, 104, 2)
                fuel_cell_price1 = st.slider("Fuel Cell Price (/kW)", 20, 100, 44, 2)
                lh2_tank_price1 = st.slider("LH2 Tank Price (/kg)", 100, 500, 270, 2)
                battery_capacity_price1 = st.slider("Battery Capacity Price (/Wh)", 100, 500, 330, 2)

                # Sliders for Energy Cost Parameters
                battery_price1 = st.slider("Battery Energy Price (/MWh)", 50, 200, 110, 2)
                lh2_price1 = st.slider("LH2 Energy Price (/MWh)", 50, 200, 140, 2)
                lch4_price1 = st.slider("LCH4 Energy Price (/MWh)", 50, 200, 120, 2)
                e_fuel_price1 = st.slider("eFuel Energy Price (/MWh)", 50, 200, 125, 2)

            with right12:
                # Text input for Techno Parameters
                battery_density = float(st.text_input("Battery Energy Density (Wh/kg)", battery_density1))
                st.write("")
                fuel_cell_power_density = float(st.text_input("Fuel Cell Power Density (W/kg)", fuel_cell_power1_density))
                st.write("")
                lh2_tank_index = float(st.text_input("LH2 Tank Gravimetric Index", lh2_tank_index1))

                # Text input for Techno Cost Parameters
                st.write("")
                emotor_price = float(st.text_input("eMotor Price (/kW)", emotor_price1))
                st.write("")
                fuel_cell_price = float(st.text_input("Fuel Cell Price (/kW)", fuel_cell_price1))
                st.write("")
                lh2_tank_price = float(st.text_input("LH2 Tank Price (/kg)", lh2_tank_price1))
                st.write("")
                battery_capacity_price = float(st.text_input("Battery Capacity Price (/Wh)", battery_capacity_price1))

                # Text input for Energy Cost Parameters
                st.write("")
                battery_price = float(st.text_input("Battery Energy Price (/MWh)", battery_price1))
                st.write("")
                lh2_price = float(st.text_input("LH2 Energy Price (/MWh)", lh2_price1))
                st.write("")
                lch4_price = float(st.text_input("LCH4 Energy Price (/MWh)", lch4_price1))
                st.write("")
                e_fuel_price = float(st.text_input("eFuel Energy Price (/MWh)", e_fuel_price1))

        with right1:
            st.header("Domain Visualization")
            figa, ax = plt.subplots(1, 1, figsize=(8, 8))

            colors = ["green", "cyan", "blue", "orange", "brown"]
            cmapa = LinearSegmentedColormap.from_list("mycmap", colors)


            gam, design_mission, power_system, dist_window, npax_window, criterionCum = init_commuter(
                max_fuel_factor, stdm_factor, lod_factor,
                    battery_density, fuel_cell_power_density, lh2_tank_index,
                    emotor_price, fuel_cell_price, lh2_tank_price, battery_capacity_price,
                    battery_price, lh2_price, lch4_price, e_fuel_price
            )
            labels = [
                power_system[key]["engine_type"] + " " + power_system[key]["energy_type"]
                for key in power_system.keys()
            ]
            labels[1] += "+fc"

            plot_domain(ax, init_commuter, "Commuter")

            # Colors
            pcolors = cmapa(np.linspace(0.0, 1.0, len(labels)))
            labels = [label.replace("turboprop", "turboprop/fan") for label in labels]
            patches = [
                mpatches.Patch(color=pcolor, label=label) for pcolor, label in zip(pcolors, labels)
            ]

            figa.supxlabel("Range (km)", fontsize=12, y=0.09)
            figa.supylabel("Capacity (seat)", fontsize=12, x=0.04)
            plt.suptitle("Best domains for: " + criterionCum, fontsize=14)
            plt.figlegend(
                handles=patches, loc=8, bbox_to_anchor=(0.5, 0.01), borderaxespad=0.0, ncol=3
            )
            plt.tight_layout()
            plt.subplots_adjust(bottom=0.2)

            # Plot of the graphics
            st.pyplot(figa)


    if airplane_type == "Regional":
        st.header("Graphic for regional airplane")
        left2, right2 = st.columns(2)

        with left2:
            st.header("Parameters for commuter airplane")

            left22, right22 = st.columns(2)

            with left22:
                # Sliders for Techno Parameters
                battery_density1 = st.slider("Battery Energy Density (Wh/kg)", 500, 1000, 750, 5)
                fuel_cell_power1_density = st.slider("Fuel Cell Power Density (W/kg)", 0.1, 3.0, 2.0, 0.1)
                lh2_tank_index1 = st.slider("LH2 Tank Gravimetric Index", 0.1, 1.0, 0.45, 0.05)

                # Sliders for Techno Cost Parameters
                emotor_price1 = st.slider("eMotor Price (/kW)", 50, 200, 104, 2)
                fuel_cell_price1 = st.slider("Fuel Cell Price (/kW)", 20, 100, 44, 2)
                lh2_tank_price1 = st.slider("LH2 Tank Price (/kg)", 100, 500, 270, 2)
                battery_capacity_price1 = st.slider("Battery Capacity Price (/Wh)", 100, 500, 330, 2)

                # Sliders for Energy Cost Parameters
                battery_price1 = st.slider("Battery Energy Price (/MWh)", 50, 200, 110, 2)
                lh2_price1 = st.slider("LH2 Energy Price (/MWh)", 50, 200, 140, 2)
                lch4_price1 = st.slider("LCH4 Energy Price (/MWh)", 50, 200, 120, 2)
                e_fuel_price1 = st.slider("eFuel Energy Price (/MWh)", 50, 200, 135, 2)

            with right22:
                # Text input for Techno Parameters
                battery_density = float(st.text_input("Battery Energy Density (Wh/kg)", battery_density1))
                st.write("")
                fuel_cell_power_density = float(st.text_input("Fuel Cell Power Density (W/kg)", fuel_cell_power1_density))
                st.write("")
                lh2_tank_index = float(st.text_input("LH2 Tank Gravimetric Index", lh2_tank_index1))

                # Text input for Techno Cost Parameters
                st.write("")
                emotor_price = float(st.text_input("eMotor Price (/kW)", emotor_price1))
                st.write("")
                fuel_cell_price = float(st.text_input("Fuel Cell Price (/kW)", fuel_cell_price1))
                st.write("")
                lh2_tank_price = float(st.text_input("LH2 Tank Price (/kg)", lh2_tank_price1))
                st.write("")
                battery_capacity_price = float(st.text_input("Battery Capacity Price (/Wh)", battery_capacity_price1))

                # Text input for Energy Cost Parameters
                st.write("")
                battery_price = float(st.text_input("Battery Energy Price (/MWh)", battery_price1))
                st.write("")
                lh2_price = float(st.text_input("LH2 Energy Price (/MWh)", lh2_price1))
                st.write("")
                lch4_price = float(st.text_input("LCH4 Energy Price (/MWh)", lch4_price1))
                st.write("")
                e_fuel_price = float(st.text_input("eFuel Energy Price (/MWh)", e_fuel_price1))

        with right2:
            st.header("Domain Visualization")
            figa, ax = plt.subplots(1, 1, figsize=(8, 8))

            colors = ["green", "cyan", "blue", "orange", "brown"]
            cmapa = LinearSegmentedColormap.from_list("mycmap", colors)

            gam, design_mission, power_system, dist_window, npax_window, criterionCum = init_commuter(
                max_fuel_factor, stdm_factor, lod_factor,
                    battery_density, fuel_cell_power_density, lh2_tank_index,
                    emotor_price, fuel_cell_price, lh2_tank_price, battery_capacity_price,
                    battery_price, lh2_price, lch4_price, e_fuel_price
            )
            labels = [
                power_system[key]["engine_type"] + " " + power_system[key]["energy_type"]
                for key in power_system.keys()
            ]
            labels[1] += "+fc"

            plot_domain(ax, init_regional, "Regional")

            # Colors
            pcolors = cmapa(np.linspace(0.0, 1.0, len(labels)))
            labels = [label.replace("turboprop", "turboprop/fan") for label in labels]
            patches = [
                mpatches.Patch(color=pcolor, label=label) for pcolor, label in zip(pcolors, labels)
            ]

            figa.supxlabel("Range (km)", fontsize=12, y=0.09)
            figa.supylabel("Capacity (seat)", fontsize=12, x=0.04)
            plt.suptitle("Best domains for: " + criterionCum, fontsize=14)
            plt.figlegend(
                handles=patches, loc=8, bbox_to_anchor=(0.5, 0.01), borderaxespad=0.0, ncol=3
            )
            plt.tight_layout()
            plt.subplots_adjust(bottom=0.2)

            # Plot of the graphics
            st.pyplot(figa)


    if airplane_type == "Short Medium":
        st.header("Graphic for short medium airplane")
        left3, right3 = st.columns(2)

        with left3:
            st.header("Parameters for commuter airplane")

            left32, right32 = st.columns(2)

            with left32:
                # Sliders for Techno Parameters
                battery_density1 = st.slider("Battery Energy Density (Wh/kg)", 500, 1000, 750, 5)
                fuel_cell_power1_density = st.slider("Fuel Cell Power Density (W/kg)", 0.1, 3.0, 2.0, 0.1)
                lh2_tank_index1 = st.slider("LH2 Tank Gravimetric Index", 0.1, 1.0, 0.76, 0.05)

                # Sliders for Techno Cost Parameters
                emotor_price1 = st.slider("eMotor Price (/kW)", 50, 200, 104, 2)
                fuel_cell_price1 = st.slider("Fuel Cell Price (/kW)", 20, 100, 44, 2)
                lh2_tank_price1 = st.slider("LH2 Tank Price (/kg)", 100, 500, 270, 2)
                battery_capacity_price1 = st.slider("Battery Capacity Price (/Wh)", 100, 500, 330, 2)

                # Sliders for Energy Cost Parameters
                battery_price1 = st.slider("Battery Energy Price (/MWh)", 50, 200, 110, 2)
                lh2_price1 = st.slider("LH2 Energy Price (/MWh)", 50, 200, 140, 2)
                lch4_price1 = st.slider("LCH4 Energy Price (/MWh)", 50, 200, 120, 2)
                e_fuel_price1 = st.slider("eFuel Energy Price (/MWh)", 50, 200, 145, 2)

            with right32:
                # Text input for Techno Parameters
                battery_density = float(st.text_input("Battery Energy Density (Wh/kg)", battery_density1))
                st.write("")
                fuel_cell_power_density = float(st.text_input("Fuel Cell Power Density (W/kg)", fuel_cell_power1_density))
                st.write("")
                lh2_tank_index = float(st.text_input("LH2 Tank Gravimetric Index", lh2_tank_index1))

                # Text input for Techno Cost Parameters
                st.write("")
                emotor_price = float(st.text_input("eMotor Price (/kW)", emotor_price1))
                st.write("")
                fuel_cell_price = float(st.text_input("Fuel Cell Price (/kW)", fuel_cell_price1))
                st.write("")
                lh2_tank_price = float(st.text_input("LH2 Tank Price (/kg)", lh2_tank_price1))
                st.write("")
                battery_capacity_price = float(st.text_input("Battery Capacity Price (/Wh)", battery_capacity_price1))

                # Text input for Energy Cost Parameters
                st.write("")
                battery_price = float(st.text_input("Battery Energy Price (/MWh)", battery_price1))
                st.write("")
                lh2_price = float(st.text_input("LH2 Energy Price (/MWh)", lh2_price1))
                st.write("")
                lch4_price = float(st.text_input("LCH4 Energy Price (/MWh)", lch4_price1))
                st.write("")
                e_fuel_price = float(st.text_input("eFuel Energy Price (/MWh)", e_fuel_price1))

        with right3:
            st.header("Domain Visualization")
            figa, ax = plt.subplots(1, 1, figsize=(8, 8))

            colors = ["green", "cyan", "blue", "orange", "brown"]
            cmapa = LinearSegmentedColormap.from_list("mycmap", colors)

            gam, design_mission, power_system, dist_window, npax_window, criterionCum = init_commuter(
                max_fuel_factor, stdm_factor, lod_factor,
                    battery_density, fuel_cell_power_density, lh2_tank_index,
                    emotor_price, fuel_cell_price, lh2_tank_price, battery_capacity_price,
                    battery_price, lh2_price, lch4_price, e_fuel_price
            )
            labels = [
                power_system[key]["engine_type"] + " " + power_system[key]["energy_type"]
                for key in power_system.keys()
            ]
            labels[1] += "+fc"

            plot_domain(ax, init_short, "Short-medium")

            # Colors
            pcolors = cmapa(np.linspace(0.0, 1.0, len(labels)))
            labels = [label.replace("turboprop", "turboprop/fan") for label in labels]
            patches = [
                mpatches.Patch(color=pcolor, label=label) for pcolor, label in zip(pcolors, labels)
            ]

            figa.supxlabel("Range (km)", fontsize=12, y=0.09)
            figa.supylabel("Capacity (seat)", fontsize=12, x=0.04)
            plt.suptitle("Best domains for: " + criterionCum, fontsize=14)
            plt.figlegend(
                handles=patches, loc=8, bbox_to_anchor=(0.5, 0.01), borderaxespad=0.0, ncol=3
            )
            plt.tight_layout()
            plt.subplots_adjust(bottom=0.2)

            # Plot of the graphics
            st.pyplot(figa)


    if airplane_type == "Long Range":
        st.header("Graphic for long range airplane")
        left4, right4= st.columns(2)

        with left4:
            st.header("Parameters for commuter airplane")

            left42, right42 = st.columns(2)

            with left42:
                # Sliders for Techno Parameters
                battery_density1 = st.slider("Battery Energy Density (Wh/kg)", 500, 1000, 750, 5)
                fuel_cell_power1_density = st.slider("Fuel Cell Power Density (W/kg)", 0.1, 3.0, 2.0, 0.1)
                lh2_tank_index1 = st.slider("LH2 Tank Gravimetric Index", 0.1, 1.0, 0.73, 0.05)

                # Sliders for Techno Cost Parameters
                emotor_price1 = st.slider("eMotor Price (/kW)", 50, 200, 104, 2)
                fuel_cell_price1 = st.slider("Fuel Cell Price (/kW)", 20, 100, 44, 2)
                lh2_tank_price1 = st.slider("LH2 Tank Price (/kg)", 100, 500, 270, 2)
                battery_capacity_price1 = st.slider("Battery Capacity Price (/Wh)", 100, 500, 330, 2)

                # Sliders for Energy Cost Parameters
                battery_price1 = st.slider("Battery Energy Price (/MWh)", 50, 200, 110, 2)
                lh2_price1 = st.slider("LH2 Energy Price (/MWh)", 50, 200, 140, 2)
                lch4_price1 = st.slider("LCH4 Energy Price (/MWh)", 50, 200, 120, 2)
                e_fuel_price1 = st.slider("eFuel Energy Price (/MWh)", 50, 200, 155, 2)

            with right42:
                # Text input for Techno Parameters
                battery_density = float(st.text_input("Battery Energy Density (Wh/kg)", battery_density1))
                st.write("")
                fuel_cell_power_density = float(st.text_input("Fuel Cell Power Density (W/kg)", fuel_cell_power1_density))
                st.write("")
                lh2_tank_index = float(st.text_input("LH2 Tank Gravimetric Index", lh2_tank_index1))

                # Text input for Techno Cost Parameters
                st.write("")
                emotor_price = float(st.text_input("eMotor Price (/kW)", emotor_price1))
                st.write("")
                fuel_cell_price = float(st.text_input("Fuel Cell Price (/kW)", fuel_cell_price1))
                st.write("")
                lh2_tank_price = float(st.text_input("LH2 Tank Price (/kg)", lh2_tank_price1))
                st.write("")
                battery_capacity_price = float(st.text_input("Battery Capacity Price (/Wh)", battery_capacity_price1))

                # Text input for Energy Cost Parameters
                st.write("")
                battery_price = float(st.text_input("Battery Energy Price (/MWh)", battery_price1))
                st.write("")
                lh2_price = float(st.text_input("LH2 Energy Price (/MWh)", lh2_price1))
                st.write("")
                lch4_price = float(st.text_input("LCH4 Energy Price (/MWh)", lch4_price1))
                st.write("")
                e_fuel_price = float(st.text_input("eFuel Energy Price (/MWh)", e_fuel_price1))

        with right4:
            st.header("Domain Visualization")
            figa, ax = plt.subplots(1, 1, figsize=(8, 8))

            colors = ["green", "cyan", "blue", "orange", "brown"]
            cmapa = LinearSegmentedColormap.from_list("mycmap", colors)

            gam, design_mission, power_system, dist_window, npax_window, criterionCum = init_commuter(
                max_fuel_factor, stdm_factor, lod_factor,
                    battery_density, fuel_cell_power_density, lh2_tank_index,
                    emotor_price, fuel_cell_price, lh2_tank_price, battery_capacity_price,
                    battery_price, lh2_price, lch4_price, e_fuel_price
            )
            labels = [
                power_system[key]["engine_type"] + " " + power_system[key]["energy_type"]
                for key in power_system.keys()
            ]
            labels[1] += "+fc"

            plot_domain(ax, init_long, "Long range")

            # Colors
            pcolors = cmapa(np.linspace(0.0, 1.0, len(labels)))
            labels = [label.replace("turboprop", "turboprop/fan") for label in labels]
            patches = [
                mpatches.Patch(color=pcolor, label=label) for pcolor, label in zip(pcolors, labels)
            ]

            figa.supxlabel("Range (km)", fontsize=12, y=0.09)
            figa.supylabel("Capacity (seat)", fontsize=12, x=0.04)
            plt.suptitle("Best domains for: " + criterionCum, fontsize=14)
            plt.figlegend(
                handles=patches, loc=8, bbox_to_anchor=(0.5, 0.01), borderaxespad=0.0, ncol=3
            )
            plt.tight_layout()
            plt.subplots_adjust(bottom=0.2)

            # Plot of the graphics
            st.pyplot(figa)


    if airplane_type == "All type combined":
        st.header("Graphic for all type of airplane")
        aleft1, aright1 = st.columns(2)

        with aleft1:
            st.header("Parameters for all type of airplane")
            
            aleft2, aright2 = st.columns(2)

            with aleft2:
                # Sliders for Techno Parameters
                battery_density1 = st.slider("Battery Energy Density (Wh/kg)", 500, 1000, 750, 5)
                fuel_cell_power1_density = st.slider("Fuel Cell Power Density (W/kg)", 0.1, 3.0, 1.0, 0.1)
                lh2_tank_index1 = st.slider("LH2 Tank Gravimetric Index", 0.1, 1.0, 0.4, 0.05)

                # Sliders for Techno Cost Parameters
                emotor_price1 = st.slider("eMotor Price (/kW)", 50, 200, 104, 2)
                fuel_cell_price1 = st.slider("Fuel Cell Price (/kW)", 20, 100, 44, 2)
                lh2_tank_price1 = st.slider("LH2 Tank Price (/kg)", 100, 500, 270, 2)
                battery_capacity_price1 = st.slider("Battery Capacity Price (/Wh)", 100, 500, 330, 2)

                # Sliders for Energy Cost Parameters
                battery_price1 = st.slider("Battery Energy Price (/MWh)", 50, 200, 110, 2)
                lh2_price1 = st.slider("LH2 Energy Price (/MWh)", 50, 200, 140, 2)
                lch4_price1 = st.slider("LCH4 Energy Price (/MWh)", 50, 200, 120, 2)
                e_fuel_price1 = st.slider("eFuel Energy Price (/MWh)", 50, 200, 125, 2)

            with aright2:
                # Text input for Techno Parameters
                battery_density = float(st.text_input("Battery Energy Density (Wh/kg)", battery_density1))
                st.write("")
                fuel_cell_power_density = float(st.text_input("Fuel Cell Power Density (W/kg)", fuel_cell_power1_density))
                st.write("")
                lh2_tank_index = float(st.text_input("LH2 Tank Gravimetric Index", lh2_tank_index1))

                # Text input for Techno Cost Parameters
                st.write("")
                emotor_price = float(st.text_input("eMotor Price (/kW)", emotor_price1))
                st.write("")
                fuel_cell_price = float(st.text_input("Fuel Cell Price (/kW)", fuel_cell_price1))
                st.write("")
                lh2_tank_price = float(st.text_input("LH2 Tank Price (/kg)", lh2_tank_price1))
                st.write("")
                battery_capacity_price = float(st.text_input("Battery Capacity Price (/Wh)", battery_capacity_price1))

                # Text input for Energy Cost Parameters
                st.write("")
                battery_price = float(st.text_input("Battery Energy Price (/MWh)", battery_price1))
                st.write("")
                lh2_price = float(st.text_input("LH2 Energy Price (/MWh)", lh2_price1))
                st.write("")
                lch4_price = float(st.text_input("LCH4 Energy Price (/MWh)", lch4_price1))
                st.write("")
                e_fuel_price = float(st.text_input("eFuel Energy Price (/MWh)", e_fuel_price1))

        with aright1:
            st.header("Domain Visualization")
            figa, ax = plt.subplots(2, 2, figsize=(8, 8))

            colors = ["green", "cyan", "blue", "orange", "brown"]
            cmapa = LinearSegmentedColormap.from_list("mycmap", colors)

            gam, design_mission, power_system, dist_window, npax_window, criterionCum = init_commuter(
                max_fuel_factor, stdm_factor, lod_factor,
                    battery_density, fuel_cell_power_density, lh2_tank_index,
                    emotor_price, fuel_cell_price, lh2_tank_price, battery_capacity_price,
                    battery_price, lh2_price, lch4_price, e_fuel_price
            )
            labels = [
                power_system[key]["engine_type"] + " " + power_system[key]["energy_type"]
                for key in power_system.keys()
            ]
            labels[1] += "+fc"

            titles = ["Commuter", "Regional", "Short-medium", "Long range"]
            init_functions = [init_commuter, init_regional, init_short, init_long]
            criteria = []

            for i, (init_func, title) in enumerate(zip(init_functions, titles)):
                criteria.append(plot_domain(ax[i // 2, i % 2], init_func, title))

            # Colors
            pcolors = cmapa(np.linspace(0.0, 1.0, len(labels)))
            labels = [label.replace("turboprop", "turboprop/fan") for label in labels]
            patches = [
                mpatches.Patch(color=pcolor, label=label) for pcolor, label in zip(pcolors, labels)
            ]

            figa.supxlabel("Range (km)", fontsize=12, y=0.09)
            figa.supylabel("Capacity (seat)", fontsize=12, x=0.04)
            plt.suptitle("Best domains for: " + criteria[-1], fontsize=14)
            plt.figlegend(
                handles=patches, loc=8, bbox_to_anchor=(0.5, 0.01), borderaxespad=0.0, ncol=3
            )
            plt.tight_layout()
            plt.subplots_adjust(bottom=0.2)

            # Plot of the graphics
            st.pyplot(figa)



def main_graph():
    '''Main, display the dashboard'''
    st.set_page_config(
        page_title="Dashboard for Airplane Fuel Consumption",
        page_icon=":airplane:",
        layout="wide",
    )
    # App title
    st.title("Visualization of Best Domains")
    pritting_fuel()


# Run the application
if __name__ == "__main__":
    main_graph()
