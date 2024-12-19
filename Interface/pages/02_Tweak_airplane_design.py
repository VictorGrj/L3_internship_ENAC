from pandas._libs.lib import is_integer, is_float
import streamlit as st
import pandas as pd
from gam_copy import GAM
from gam_utils import unit


def tweak_graphic():
    if "VARG3" not in st.session_state:
        st.session_state.VARG3 = []
    gam = GAM()

    dis = {"general": 95, "commuter": 105, "regional": 110,
        "short_medium": 115, "long_range": 120}

    graph_list = [""]
    name_list = [""]
    if st.session_state.VARG1:
        data1 = st.session_state.VARG1
        for element1 in data1:
            graph_list.append(element1[0])
            name_list.append(element1[3])
    if st.session_state.VARG2:
        data2 = st.session_state.VARG2
        for element2 in data2:
            graph_list.append(element2[0])
            name_list.append(element2[3])
    if graph_list != [] and name_list != []:
        st.header("Choose the airplane ou want to tweak")
        final_name = st.selectbox("Choose the airplane you want to tweak in the list : ", name_list)
        if final_name != "":
            final_data = [graph_list[name_list.index(final_name)], final_name]
            st.header("Choose the parameters yo want to tweak.")
            left1, right1 = st.columns(2)

            with left1:
                st.write("#### Type 1 of parameter")
                # prop_system_eff
                prop_sys_eff = st.text_input("Propulsion system efficiency (defaut value is 1).")
                if prop_sys_eff != "":
                    if is_float(float(prop_sys_eff)) == False:
                        st.warning("Please select a number for the propulsion system efficiency.")
                    else:
                        gam.prop_system_eff = float(prop_sys_eff)
                elif prop_sys_eff == "":
                    gam.prop_system_eff = 1
                # lod_factor
                lod = st.text_input("LOD factor (defaut value is 1).")
                if lod != "":
                    if is_float(float(lod)) == False:
                        st.warning("Please select a number for the LOD factor.")
                    else:
                        gam.lod_factor = float(lod)
                elif lod == "":
                    gam.lod_factor = 1
                # stdm_factor
                stdm = st.text_input("STDM factor (defaut value is 1).")
                if stdm != "":
                    if is_float(float(stdm)) == False:
                        st.warning("Please select a number for the STDM factor.")
                    else:
                        gam.stdm_factor = float(stdm)
                elif stdm == "":
                    gam.stdm_factor = 1

            with right1:
                st.write("#### Type 2 of parameter")
                # mpax
                mpax = st.text_input("Masse of one PAX.")
                if mpax != "":
                    if is_float(float(mpax)) == False:
                        st.warning("Please select a number for the masse of one PAX.")
                    else:
                        for key in dis:
                            data = final_data[0]
                            if data["airplane_type"] == key:
                                gam.mpax_dict[key] = float(mpax)
                if mpax == "":
                    for key in dis:
                        data = final_data[0]
                        if data["airplane_type"] == key:
                            gam.mpax_dict[key] = dis[key]
                # max_payload_factor
                max_payload = st.text_input("Max payload factor (defaut value is 1.15).")
                if max_payload != "":
                    if is_float(float(max_payload)) == False:
                        st.warning("Please select a number for the max payload factor.")
                    else:
                        gam.max_payload_factor = float(max_payload)
                elif max_payload == "":
                    gam.max_payload_factor = 1.15
                # max_fuel_factor
                mff = st.text_input("Max fuel factor (defaut value is 1.25).")
                if mff != "":
                    if is_float(float(mff)) == False:
                        st.warning("Please select a number for the max fuel factor.")
                    else:
                        gam.max_fuel_factor = float(mff)
                elif mff == "":
                    gam.max_fuel_factor = 1.25

            ## Make the power system and the design mession for tweak
            st.header("Show payload-range of the tweak airplane")
            fpower_system = {}
            fdesign_mission = {}
            for elements in final_data[0]:
                if elements == "power_system":
                    fpower_system = final_data[0]["power_system"]
                if elements == "mission":
                    fdesign_mission = final_data[0]["mission"]
                if elements == "mtow":
                    fdesign_mission["mtow"] = final_data[0]["mtow"]
                if elements == "owe":
                    fdesign_mission["owe"] = final_data[0]["owe"]
            for key in dis:
                if final_data[0]["airplane_type"] == key:
                    if fdesign_mission["npax"] != "":
                        payload = fdesign_mission["npax"]*gam.mpax_dict[key]
                        fdesign_mission["payload"] = payload
            if fdesign_mission["payload"] != "":
                max_payload = fdesign_mission["payload"]*gam.max_payload_factor
                fdesign_mission["payload_max"] = float(max_payload)



            # Run the GAM with the design_airplane
            if fpower_system != {} and fdesign_mission != {}:
                tweak_dict = gam.tune_design(fpower_system, fdesign_mission)
                table_rows = []

                st.write("What property of the airplane do you want to see:")

                table_rows.append({
                        "Property" : "Name",
                        "Value" : final_name
                    })
                table_rows.append({
                    "Property": "Engine type",
                    "Value": tweak_dict["power_system"]["engine_type"]
                })
                table_rows.append({
                    "Property": "Energy source",
                    "Value": tweak_dict["power_system"]["energy_type"]
                })
                table_rows.append({
                    "Property": "Thruster type",
                    "Value": tweak_dict["power_system"]["thruster_type"]
                })
                table_rows.append({
                    "Property" : " Number of engine ",
                    "Value" : "%.0f" % tweak_dict["n_engine"]
                })
                table_rows.append({
                    "Property": "By Pass Ratio",
                    "Value": tweak_dict["by_pass_ratio"]
                })
                table_rows.append({
                    "Property" : " Airplane type",
                    "Value" : tweak_dict["airplane_type"]
                })
                table_rows.append({
                    "Property" : " Number of passenger ",
                    "Value" : "%.0f" % tweak_dict["npax"]
                })
                table_rows.append({
                    "Property" : " Design range ",
                    "Value" : "%.0f km" % unit.convert_to("km", tweak_dict["nominal_range"])
                })
                if tweak_dict["cruise_speed"] > 1:
                    table_rows.append({
                        "Property" : " Cruise speed ",
                        "Value" : "%.1f km/h" % unit.convert_to("km/h", tweak_dict["cruise_speed"]) 
                    })
                if tweak_dict["cruise_speed"] <= 1:
                    table_rows.append({
                        "Property" : " Cruise Mach ",
                        "Value" : "%.2f" % tweak_dict["cruise_speed"]
                    })
                table_rows.append({
                    "Property" : " Cruise altitude ",
                    "Value" : "%.1f ft" % unit.convert_to("ft", tweak_dict["altitude_data"]["mission"]),
                })
                table_rows.append({
                    "Property": "MTOW",
                    "Value": "%.0f kg" % tweak_dict["mtow"]
                })
                table_rows.append({
                    "Property": "MZFW",
                    "Value": "%.0f kg" % tweak_dict["mzfw"]
                })
                table_rows.append({
                    "Property": "Payload max",
                    "Value": "%.0f kg" % tweak_dict["payload_max"]
                })
                table_rows.append({
                    "Property": "Maximum payload factor",
                    "Value": "%.3f" % tweak_dict["max_payload_factor"]
                })
                table_rows.append({
                    "Property": "OWE",
                    "Value": "%.0f kg" % tweak_dict["owe"]
                })
                table_rows.append({
                    "Property": "Operator items",
                    "Value": "%.0f kg" % tweak_dict["op_item"]
                })
                table_rows.append({
                    "Property": "MWE",
                    "Value": "%.0f kg" % tweak_dict["mwe"]
                })
                table_rows.append({
                    "Property": "Furnishing",
                    "Value": "%.0f kg" % tweak_dict["furnishing"]
                })
                table_rows.append({
                    "Property": "Standard MWE",
                    "Value": "%.0f kg" % tweak_dict["std_mwe"]
                })
                table_rows.append({
                    "Property": "Propulsion mass",
                    "Value": "%.0f kg" % tweak_dict["propulsion_mass"]
                })
                table_rows.append({
                    "Property": "Energy storage mass",
                    "Value": "%.0f kg" % tweak_dict["energy_storage_mass"]
                })
                table_rows.append({
                    "Property": "Fuel cell system mass",
                    "Value": "%.0f kg" % tweak_dict["fuel_cell_system_mass"]
                })
                table_rows.append({
                    "Property": "Basic MWE",
                    "Value": "%.0f kg" % tweak_dict["basic_mwe"]
                })
                table_rows.append({
                    "Property": "MWE shift",
                    "Value": "%.0f kg" % tweak_dict["stdm_shift"]
                })
                table_rows.append({
                    "Property": "Nominal pax mass allowance",
                    "Value": "%.1f kg" % tweak_dict["mpax"]
                })
                table_rows.append({
                    "Property": "Nominal payload delta",
                    "Value": "%.0f kg" % tweak_dict["delta_payload"]
                })
                table_rows.append({
                    "Property": "Nominal payload",
                    "Value": "%.0f kg" % tweak_dict["payload"]
                })
                table_rows.append({
                    "Property": "Nominal mission time",
                    "Value": "%.1f h" % unit.h_s(tweak_dict["nominal_time"])
                })

                table_rows.append({
                    "Property": "Mission fuel",
                    "Value": "%.0f kg" % tweak_dict["mission_fuel"]
                })
                table_rows.append({
                    "Property": "Reserve fuel",
                    "Value": "%.0f kg" % tweak_dict["reserve_fuel"]
                })
                table_rows.append({
                    "Property": "Total fuel",
                    "Value": "%.0f kg" % tweak_dict["total_fuel"]
                })
                table_rows.append({
                    "Property": "Fuel consumption",
                    "Value": "%.2f L/pax/100km" % unit.convert_to("L", tweak_dict["fuel_consumption"] * unit.m_km(100))
                })
                table_rows.append({
                    "Property": "Mission energy",
                    "Value": "%.0f kWh" % unit.kWh_J(tweak_dict["mission_enrg"])
                })
                table_rows.append({
                    "Property": "Reserve energy",
                    "Value": "%.0f kWh" % unit.kWh_J(tweak_dict["reserve_enrg"])
                })
                table_rows.append({
                    "Property": "Total energy",
                    "Value": "%.0f kWh" % unit.kWh_J(tweak_dict["total_energy"])
                })
                table_rows.append({
                    "Property": "Energy consumption",
                    "Value": "%.2f kWh/pax/100km" % unit.kWh_J(tweak_dict["enrg_consumption"] * unit.m_km(100))
                })
                table_rows.append({
                    "Property": "Wake Turbulence Category",
                    "Value": tweak_dict["wake_turbulence_class"]
                })
                table_rows.append({
                    "Property": "Max power",
                    "Value": "%.0f kW" % unit.kW_W(tweak_dict["max_power"])
                })
                table_rows.append({
                    "Property": "Standard mass factor",
                    "Value": "%.4f" % tweak_dict["stdm_factor"]
                })
                table_rows.append({
                    "Property": "Aerodynamic efficiency factor",
                    "Value": "%.4f" % tweak_dict["aero_eff_factor"]
                })
                table_rows.append({
                    "Property": "Aerodynamic efficiency (L/D)",
                    "Value": "%.2f" % tweak_dict["aerodynamic_efficiency"]
                })
                table_rows.append({
                    "Property": "Propulsion system efficiency",
                    "Value": "%.3f" % tweak_dict["propulsion_system_efficiency"]
                })
                table_rows.append({
                    "Property": "Storage energy density",
                    "Value": "%.0f Wh/kg" % unit.Wh_J(tweak_dict["storage_energy_density"])
                })
                table_rows.append({
                    "Property": "Propulsion power density",
                    "Value": "%.2f kW/kg" % unit.kW_W(tweak_dict["propulsion_power_density"])
                })
                table_rows.append({
                    "Property": "Structural factor (OWE/MTOW)",
                    "Value": "%.2f" % tweak_dict["structural_factor"]
                })
                table_rows.append({
                    "Property": "Energy efficiency factor, P.K/E",
                    "Value": "%.2f pax.km/kWh" % unit.convert_to("km/kWh", tweak_dict["pk_o_enrg"])
                })
                table_rows.append({
                    "Property": "Mass efficiency factor, P.K/M",
                    "Value": "%.2f pax.km/kg" % unit.convert_to("km/kg", tweak_dict["pk_o_mass"])
                })
                st.write("")
                table = pd.DataFrame(table_rows)
                st.dataframe(table, width=600, column_config={"Property": {"width": 300}, "Value": {"width": 300},}, hide_index=True)



            else:
                st.warning("The program can't compute the data.")

            st.write("")
            st.write("Compute and build the Payload-Range of the airplane")
            if tweak_dict != {}:
                two_dict2 = gam.build_payload_range(tweak_dict)    # Compute payload-range data and add them in ac_dict
                left_column4 , right_column4 = st.columns(2)

                if 'payload_info' not in st.session_state:
                    st.session_state.payload_info = False

                with left_column4:
                    if st.button("Show payload-range information"):
                        st.session_state.payload_info = True
                with right_column4:
                    if st.button("Hide payload-range information"):
                        st.session_state.payload_info = False

                if st.session_state.payload_info :
                    gam.print_payload_range(tweak_dict)    # Print payload-range data


                st.write("")
                st.write("## Do you want to save this tweak AC?")
                left_column3, right_column3 = st.columns(2)

                with left_column3:
                    name = st.text_input("Choose the name of this tweak AC if you want.")

                    duplicate_name = any(ele[3] == name and ele[3] != "" for ele in st.session_state.VARG3)
                    if duplicate_name:
                        st.warning("Please select a new name for this tweak AC.")
                    else:
                        if st.button("Yes, save the tweak AC", key="save_new_ac"):
                            if name:
                                tup = (tweak_dict, two_dict2, table, name)
                                st.session_state.VARG3.append(tup)
                                st.success(f"{name} saved!")
                            else:
                                tup = (tweak_dict, two_dict2, table, f"Tweak AC {len(st.session_state.VARG3)}")
                                st.session_state.VARG3.append(tup)
                                st.success(f"Tweak AC {len(st.session_state.VARG3)} saved!")

                st.write("")
                st.write("### Saved tweak AC")
                if st.session_state.VARG3:
                    for idx, config in enumerate(st.session_state.VARG3, start=1):

                        if config[3]:
                            st.write(config[3])
                        else:
                            st.write(f"**Tweak AC {idx}:**")

                        left_column5, right_column5 = st.columns(2)
                        if "AC" not in st.session_state:
                            st.session_state.AC = False
                        with left_column5:
                            if st.button(f"Show {config[3] or f'Tweak AC {idx}'}", key=f"show_{idx}"):
                                st.session_state.AC = True
                        with right_column5:
                            if st.button(f"Hide {config[3] or f'Tweak AC {idx}'}", key=f"hide_{idx}"):
                                st.session_state.AC = False
                        if st.session_state.AC:
                            st.dataframe(config[2], width=600, hide_index=True)


                        if st.button(f"Delete {config[3] or f'Tweak AC {idx}'}", key=f"delete_{idx}"):
                            st.session_state.deleted_index = idx - 1

                else:
                    st.info("No configurations saved yet.")


                if "deleted_index" in st.session_state:
                    del st.session_state.VARG3[st.session_state.deleted_index]
                    del st.session_state.deleted_index
                    st.rerun()



        #        with right_column3:
        #            st.write("#")
        #            st.button("No, delete this AC")

                st.write("")
                st.header("Show the result for the tweak AC")

                if 'info_all' not in st.session_state:
                    st.session_state.info_all = False

                left_column6, right_column6 = st.columns(2)

                with left_column6:
                    if st.button("Show all of the informations about the Tweak AC"):
                        st.session_state.info_all = True

                with right_column6:
                    if st.button("Hide all the informations about the Tweak AC"):
                        st.session_state.info_all = False

                if st.session_state.info_all:
                    if st.session_state.VARG3:
                        consolidated_data = {}
                        for idx, config in enumerate(st.session_state.VARG3, start=1):
                            config_table = config[2]
                            for _, row in config_table.iterrows():
                                property_name = row["Property"]
                                value = row["Value"]
                                if property_name not in consolidated_data:
                                    consolidated_data[property_name] = {}
                                consolidated_data[property_name][f"Value{idx}"] = value

                        consolidated_table = pd.DataFrame.from_dict(consolidated_data, orient="index")
                        consolidated_table.reset_index(inplace=True)
                        consolidated_table.rename(columns={"index": "Property"}, inplace=True)

                        st.dataframe(consolidated_table, width=1000, hide_index=True)

                    else:
                        st.info("No configurations to display.")


                config_list = []
                name_list = []
                if st.session_state.VARG3:
                    for idx, config in enumerate(st.session_state.VARG3, start=1):
                        config_list.append(config[0])
                        name_list.append(config[3])
                    gam.payload_range_graph(config_list, name_list)
                else:
                    st.info("No configurations to display.")
            else:
                st.warning("The data can't be computed.")



def main_tweak():
    '''Main, display the dashboard'''
    st.set_page_config(
        page_title="Dashboard for Airplane Fuel Consumption",
        page_icon=":airplane:",
        layout="centered",
    )
    # App title
    st.title("Tweak one of the airplane you have made")
    tweak_graphic()




# Run the application
if __name__ == "__main__":
    main_tweak()
