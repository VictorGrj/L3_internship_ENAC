from pandas._libs.lib import is_float, is_integer
import streamlit as st
import pandas as pd
from gam_copy import GAM
from gam_utils import unit


# Load data from the Excel file
#def load_data(file):
#    return pd.read_excel(file)


def setup2():
    if "VARG1" not in st.session_state:
        st.session_state.VARG1 = []

    # Load the Excel files
    #file = "airplane_database_copieVF_test.csv"  # File with airplane details
    #file = "airplane_database_copieVF.xlsx"

    #try:
    #    data_airplanes= load_data(file)
    #except FileNotFoundError as e:
    #    st.error(f"File not found: {e.filename}")
    #    return


    st.header("Choose your parameters for the power system.")

    #errors = ["string", "mach", "None", "unknown", "int", "m", "deg", "m2", "kg", "no_dim", "kW", "N", "km/h", "ft", "km"]
    power_data = ["", "", "", "", ""]

    energy_type = ["", "petrol", "kerosene", "gasoline", "compressed_h2", "liquid_h2", "liquid_ch4", "liquid_nh3", "battery"]
    energy = st.selectbox("Choose the energy type you want", energy_type)
    power_data[0] = energy

    engine_count=  ["", 1, 2, 4]
    nbengine = st.selectbox("Choose the engine count you want", engine_count)
    power_data[1] = nbengine

    engine_type = ["", "turbofan", "turboprop", "piston", "emotor"]
    etype = st.selectbox("Choose the engine type you want", engine_type)
    power_data[2] = etype

    if power_data[2] == "turbofan":
        power_data[3] = "fan"
    elif power_data[2] == "turboprop" or power_data[2] == "piston" or power_data[2] == "emotor":
        power_data[3] = "propeller"
    else:
        power_data[3] = "None"

    if power_data[2] == "turbofan":
        bpr = st.slider("BPR of the aircraft engine:", 5, 15, 10, 1)
        bpr1 = bpr
        bpr1 = st.text_input("Select the precise BPR of the aircraft engine ", bpr1)
        if bpr1 != bpr:
            bpr = bpr1
        if bpr1 != "":
            if is_float(float(bpr1)):
                power_data[4] = float(bpr1)
            else:
                st.warning("Please choose an bpr to proceed.")
        else:
            st.warning("Please choose an bpr to proceed.")
    else:
        power_data[4] = "None"

    st.write("")
    st.write("Do you want to see the power settings you choose?")

    left1, right1 = st.columns(2)
    power_system = {"energy_type" : power_data[0], "engine_count" : power_data[1],
                "engine_type" : power_data[2], "thruster_type" : power_data[3], "bpr" : power_data[4]}
    st.session_state.power_systeme = False
    if 'power_systeme' not in st.session_state:
        st.session_state.power_systeme = False

    with left1:
        if st.button("Show power system"):
            st.session_state.power_systeme = True
    with right1:
        if st.button("Hide power system"):
            st.session_state.power_systeme = False

    if st.session_state.power_systeme:
        dataframes = []
        compt = 0
        for key in power_system:
            if power_system[key] != "":
                tup = (key, power_system[key])
                dataframes.append(tup)
                compt +=1
            else:
                st.warning("Choose a parameter for the "+ key+ " to proceed.")
        if compt == 5:
            st.dataframe(dataframes, hide_index=True)


######################################################################################################


    st.write("")
    st.header("Choose the design mission of the generic airplane:")

    design_mission = {"category": "", "npax": "", "speed": "", "range": "", "altitude": ""}

    corres_cat  = ["", "General", "Commuter", "Regional", "Short/medium range", "Long range"]
    cat = ["", "general", "commuter", "regional", "short_medium", "long_range"]

    airplane_type = st.selectbox("Choose the airplane category:", corres_cat)
    if airplane_type != "":
        for i in range(len(corres_cat)):
            if corres_cat[i] == airplane_type:
                design_mission["category"] = cat[i]
                st.write("You choose the "+airplane_type+" for the airplane type.")

        dis = {"general": 500, "commuter": 1500, "regional": 4500,
                "short_medium": 8000, "long_range": 15000}
        for key in dis:
            if key == design_mission["category"]:
                if dis[key] - 5000 >= 0:
                    range_slider = st.slider("Range of the aircraft (in km):", dis[key] - 5000, dis[key], dis[key] - 2500, 10)
                    range_slider1 = range_slider
                    range_slider1 = int(st.text_input("Select the precise design range you require ", range_slider1))
                    design_mission["range"] = unit.m_km(range_slider1)
                    if range_slider1 != range_slider:
                        range_slider = range_slider1
                    st.write(f"### Selected range: {range_slider1} km")
                else:
                    range_slider = st.slider("Range of the aircraft (in km):", 0, int(dis[key]), int(dis[key]/2), 10)
                    range_slider1 = range_slider
                    range_slider1 = int(st.text_input("Select the precise design range you require ", range_slider1))
                    design_mission["range"] = unit.m_km(range_slider1)
                    if range_slider1 != range_slider:
                        range_slider = range_slider1
                    st.write(f"### Selected range: {range_slider1} km")


        cap = {"general": 6, "commuter": 19, "regional": 80,
                "short_medium": 250, "long_range": 550}
        pax = st.text_input("Choose the number of PAX in the airplane")
        if pax != "":
            if is_integer(int(pax)) == False:
                st.warning("Please select a number for the number of PAX")
            if int(pax) <= cap[design_mission["category"]]:
                design_mission["npax"] = int(pax)
            else:
                st.warning("Please select an number of PAX, under " + str(cap[design_mission["category"]]))
        else:
            st.warning("Choose the number of pax to proceed.")

        st.write("Please select just one of this choice cruise speed in km/h or in Mach Number.")
        cspeed = [""]
        s = 200
        for i in range(10):
            cspeed.append(s)
            s += 25
        cruisespeed = st.selectbox("Choose the cruise speed of the airplane in km/h.", cspeed)
        maspeed = st.text_input("Choose the cruise speed in Mach Number between 0.5 and 0.9")
        if cruisespeed != "" and maspeed == "":
            design_mission["speed"] = cruisespeed*(10/36)
        elif cruisespeed == "" and maspeed != "":
            if is_float(float(maspeed)) and 0.5 < float(maspeed) < 0.9:
                design_mission["speed"] = float(maspeed)
            else:
                st.warning("Please write en number between 0.5 and 0.9")
        elif cruisespeed != "" and maspeed != "":
            st.warning("Choose just one type of cruise speed and no both to proceed.")
        else:
            st.warning("Please select the speed of the airplane to proceed.")


        alt = ["", 1500, 3000, 5000, 6000, 10000, 20000, 25000, 30000, 35000]
        altitude = st.selectbox("Choose the altitude of your airplane in ft.", alt)
        if altitude != "":
            design_mission["altitude"] = altitude*0.3048
        else:
            st.warning("Please choose the cruise altitude of your airplane to proceed.")
    else:
        st.warning("Choose the design mission of the airplane to proceed")


    st.write("")
    st.write("Do you want to see the design mission you choose?")

    left2, right2 = st.columns(2)
    st.session_state.designmission = False
    if 'designmission' not in st.session_state:
        st.session_state.designmission = False

    with left2:
        if st.button("Show design mission"):
            st.session_state.designmission = True
    with right2:
        if st.button("Hide design mission"):
            st.session_state.designmission = False

    if st.session_state.designmission:
        dataframes = []
        compt = 0
        for key in design_mission:
            if design_mission[key] != "":
                tup = (key, design_mission[key])
                dataframes.append(tup)
                compt +=1
            else:
                st.warning("Choose a parameter for the "+ key+ " to proceed.")
        if compt == 5:
            st.dataframe(dataframes, hide_index=True)


    st.header("Make the configuration of the generic airplane")

    c = 0
    for key in power_system:
        if power_system[key] != "":
            c += 1
    c1 = 0
    for key in design_mission:
        if design_mission[key] != "":
            c1 += 1
    if c1 == 5 and  c == 5:
        gam = GAM()
        st.write("")
        table_rows = []
        this_dict = gam.design_airplane(power_system, design_mission)
        st.write("What property of the airplane do you want to see:")

        Name = st.checkbox("Name")
        if Name:
            table_rows.append({
                    "Property" : "Name",
                    "Value" : "Generic Airplane"
                })
        propulsion = st.checkbox("Propulsion system definition")
        if propulsion:
            table_rows.append({
                "Property": "Engine type",
                "Value": this_dict["power_system"]["engine_type"]
            })
            table_rows.append({
                "Property": "Energy source",
                "Value": this_dict["power_system"]["energy_type"]
            })
            table_rows.append({
                "Property": "Thruster type",
                "Value": this_dict["power_system"]["thruster_type"]
            })
            table_rows.append({
                "Property" : " Number of engine ",
                "Value" : "%.0f" % this_dict["n_engine"]
            })
            table_rows.append({
                "Property": "By Pass Ratio",
                "Value": this_dict["by_pass_ratio"]
            })
        mission = st.checkbox("Design mission definition")
        if mission:
            table_rows.append({
                "Property" : " Airplane type",
                "Value" : this_dict["airplane_type"]
            })
            table_rows.append({
                "Property" : " Number of passenger ",
                "Value" : "%.0f" % this_dict["npax"]
            })
            table_rows.append({
                "Property" : " Design range ",
                "Value" : "%.0f km" % unit.convert_to("km", this_dict["nominal_range"])
            })
            if this_dict["cruise_speed"] > 1:
                table_rows.append({
                    "Property" : " Cruise speed ",
                    "Value" : "%.1f km/h" % unit.convert_to("km/h", this_dict["cruise_speed"]) 
                })
            if this_dict["cruise_speed"] <= 1:
                table_rows.append({
                    "Property" : " Cruise Mach ",
                    "Value" : "%.2f" % this_dict["cruise_speed"]
                })
            table_rows.append({
                "Property" : " Cruise altitude ",
                "Value" : "%.1f ft" % unit.convert_to("ft", this_dict["altitude_data"]["mission"]),
            })
        breakdown = st.checkbox("Mass breakdown")
        if breakdown:
            table_rows.append({
                "Property": "MTOW",
                "Value": "%.0f kg" % this_dict["mtow"]
            })
            table_rows.append({
                "Property": "MZFW",
                "Value": "%.0f kg" % this_dict["mzfw"]
            })
            table_rows.append({
                "Property": "Payload max",
                "Value": "%.0f kg" % this_dict["payload_max"]
            })
            table_rows.append({
                "Property": "Maximum payload factor",
                "Value": "%.3f" % this_dict["max_payload_factor"]
            })
            table_rows.append({
                "Property": "OWE",
                "Value": "%.0f kg" % this_dict["owe"]
            })
            table_rows.append({
                "Property": "Operator items",
                "Value": "%.0f kg" % this_dict["op_item"]
            })
            table_rows.append({
                "Property": "MWE",
                "Value": "%.0f kg" % this_dict["mwe"]
            })
            table_rows.append({
                "Property": "Furnishing",
                "Value": "%.0f kg" % this_dict["furnishing"]
            })
            table_rows.append({
                "Property": "Standard MWE",
                "Value": "%.0f kg" % this_dict["std_mwe"]
            })
            table_rows.append({
                "Property": "Propulsion mass",
                "Value": "%.0f kg" % this_dict["propulsion_mass"]
            })
            table_rows.append({
                "Property": "Energy storage mass",
                "Value": "%.0f kg" % this_dict["energy_storage_mass"]
            })
            table_rows.append({
                "Property": "Fuel cell system mass",
                "Value": "%.0f kg" % this_dict["fuel_cell_system_mass"]
            })
            table_rows.append({
                "Property": "Basic MWE",
                "Value": "%.0f kg" % this_dict["basic_mwe"]
            })
            table_rows.append({
                "Property": "MWE shift",
                "Value": "%.0f kg" % this_dict["stdm_shift"]
            })
        output = st.checkbox("Design mission output")
        if output:
            table_rows.append({
                "Property": "Nominal pax mass allowance",
                "Value": "%.1f kg" % this_dict["mpax"]
            })
            table_rows.append({
                "Property": "Nominal payload delta",
                "Value": "%.0f kg" % this_dict["delta_payload"]
            })
            table_rows.append({
                "Property": "Nominal payload",
                "Value": "%.0f kg" % this_dict["payload"]
            })
            table_rows.append({
                "Property": "Nominal mission time",
                "Value": "%.1f h" % unit.h_s(this_dict["nominal_time"])
            })

            table_rows.append({
                "Property": "Mission fuel",
                "Value": "%.0f kg" % this_dict["mission_fuel"]
            })
            table_rows.append({
                "Property": "Reserve fuel",
                "Value": "%.0f kg" % this_dict["reserve_fuel"]
            })
            table_rows.append({
                "Property": "Total fuel",
                "Value": "%.0f kg" % this_dict["total_fuel"]
            })
            table_rows.append({
                "Property": "Fuel consumption",
                "Value": "%.2f L/pax/100km" % unit.convert_to("L", this_dict["fuel_consumption"] * unit.m_km(100))
            })
            table_rows.append({
                "Property": "Mission energy",
                "Value": "%.0f kWh" % unit.kWh_J(this_dict["mission_enrg"])
            })
            table_rows.append({
                "Property": "Reserve energy",
                "Value": "%.0f kWh" % unit.kWh_J(this_dict["reserve_enrg"])
            })
            table_rows.append({
                "Property": "Total energy",
                "Value": "%.0f kWh" % unit.kWh_J(this_dict["total_energy"])
            })
            table_rows.append({
                "Property": "Energy consumption",
                "Value": "%.2f kWh/pax/100km" % unit.kWh_J(this_dict["enrg_consumption"] * unit.m_km(100))
            })
            table_rows.append({
                "Property": "Wake Turbulence Category",
                "Value": this_dict["wake_turbulence_class"]
            })
        factor = st.checkbox("Factors & Efficiencies")
        if factor:
            table_rows.append({
                "Property": "Max power",
                "Value": "%.0f kW" % unit.kW_W(this_dict["max_power"])
            })
            table_rows.append({
                "Property": "Standard mass factor",
                "Value": "%.4f" % this_dict["stdm_factor"]
            })
            table_rows.append({
                "Property": "Aerodynamic efficiency factor",
                "Value": "%.4f" % this_dict["aero_eff_factor"]
            })
            table_rows.append({
                "Property": "Aerodynamic efficiency (L/D)",
                "Value": "%.2f" % this_dict["aerodynamic_efficiency"]
            })
            table_rows.append({
                "Property": "Propulsion system efficiency",
                "Value": "%.3f" % this_dict["propulsion_system_efficiency"]
            })
            table_rows.append({
                "Property": "Storage energy density",
                "Value": "%.0f Wh/kg" % unit.Wh_J(this_dict["storage_energy_density"])
            })
            table_rows.append({
                "Property": "Propulsion power density",
                "Value": "%.2f kW/kg" % unit.kW_W(this_dict["propulsion_power_density"])
            })
            table_rows.append({
                "Property": "Structural factor (OWE/MTOW)",
                "Value": "%.2f" % this_dict["structural_factor"]
            })
            table_rows.append({
                "Property": "Energy efficiency factor, P.K/E",
                "Value": "%.2f pax.km/kWh" % unit.convert_to("km/kWh", this_dict["pk_o_enrg"])
            })
            table_rows.append({
                "Property": "Mass efficiency factor, P.K/M",
                "Value": "%.2f pax.km/kg" % unit.convert_to("km/kg", this_dict["pk_o_mass"])
            })
        
        st.write("")
        table = pd.DataFrame(table_rows)
        st.dataframe(table, width=600, column_config={"Property": {"width": 300}, "Value": {"width": 300},}, hide_index=True)

        st.write("")
        st.write("Compute and build the Payload-Range of the airplane")
        two_dict = gam.build_payload_range(this_dict)    # Compute payload-range data and add them in ac_dict
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
            gam.print_payload_range(this_dict)    # Print payload-range data



        st.write("")
        st.write("Do you want to save this AC?")
        left_column3, right_column3 = st.columns(2)

        with left_column3:
            name = st.text_input("Choose the name of this AC if you want.")

            duplicate_name = any(ele[3] == name and ele[3] != "" for ele in st.session_state.VARG1)
            if duplicate_name:
                st.warning("Please select a new name for this AC.")
            else:
                if st.button("Yes, save the AC", key="save_new_ac"):
                    if name:
                        tup = (this_dict, two_dict, table, name)
                        st.session_state.VARG1.append(tup)
                        st.success(f"{name} saved!")
                    else:
                        tup = (this_dict, two_dict, table, f"AC {len(st.session_state.VARG1)}")
                        st.session_state.VARG1.append(tup)
                        st.success(f"AC {len(st.session_state.VARG1)} saved!")

        st.write("")
        st.write("### Saved AC")
        if st.session_state.VARG1:
            for idx, config in enumerate(st.session_state.VARG1, start=1):

                if config[3]:
                    st.write(config[3])
                else:
                    st.write(f"**AC {idx}:**")

                left_column5, right_column5 = st.columns(2)
                if "AC" not in st.session_state:
                    st.session_state.AC = False
                with left_column5:
                    if st.button(f"Show {config[3] or f'AC {idx}'}", key=f"show_{idx}"):
                        st.session_state.AC = True
                with right_column5:
                    if st.button(f"Hide {config[3] or f'AC {idx}'}", key=f"hide_{idx}"):
                        st.session_state.AC = False
                if st.session_state.AC:
                    st.dataframe(config[2], width=600, hide_index=True)


                if st.button(f"Delete {config[3] or f'AC {idx}'}", key=f"delete_{idx}"):
                    st.session_state.deleted_index = idx - 1

        else:
            st.info("No configurations saved yet.")


        if "deleted_index" in st.session_state:
            del st.session_state.VARG1[st.session_state.deleted_index]
            del st.session_state.deleted_index
            st.rerun()



#        with right_column3:
#            st.write("#")
#            st.button("No, delete this AC")

        st.write("")
        st.header("Show the result for the generic airplane and with your AC")

        if 'info_all' not in st.session_state:
            st.session_state.info_all = False

        left_column6, right_column6 = st.columns(2)

        with left_column6:
            if st.button("Show all of the informations about the AC"):
                st.session_state.info_all = True

        with right_column6:
            if st.button("Hide all the informations about the AC"):
                st.session_state.info_all = False

        if st.session_state.info_all:
            if st.session_state.VARG1:
                consolidated_data = {}
                for idx, config in enumerate(st.session_state.VARG1, start=1):
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
        if st.session_state.VARG1:
            for idx, config in enumerate(st.session_state.VARG1, start=1):
                config_list.append(config[0])
                name_list.append(config[3])
            gam.payload_range_graph(config_list, name_list)
        else:
            st.info("No configurations to display.")

    else:
        st.warning("Please finish to choose the different parameters to proceed")



def main2():
    '''Main, display the dashboard'''
    st.set_page_config(
        page_title="Dashboard for Airplane Fuel Consumption",
        page_icon=":airplane:",
        layout="centered",
    )
    # App title
    st.title("Dashboard for Airplane Fuel Consumption with an generic airplane")

    setup2()





# Run the application
if __name__ == "__main__":
    main2()
