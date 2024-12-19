from pandas._libs.lib import is_integer
from pandas._libs.lib import is_float
import streamlit as st
import pandas as pd
from gam_copy import GAM
from gam_utils import unit



# Load data from the Excel file
def load_data(file):
    '''Read Excel files'''
    return pd.read_excel(file)


def setup3():
    if "VARG2" not in st.session_state:
        st.session_state.VARG2 = []


    # Load the Excel files
    #file = "airplane_database_copieVF_test.csv"  # File with airplane details
    file = "airplane_database_copieVF.xlsx"

    try:
        data_airplanes= load_data(file)
    except FileNotFoundError as e:
        st.error(f"File not found: {e.filename}")
        return

    prop = ["airplane_type",  "name", "Constructor", "icao_code", "iata_code", "n_pax", "owe",
            "mtow", "mlw", "max_fuel", "n_engine", "engine_type", "thruster_type", "powerplant",
            "bpr", "energy_type", "max_power", "max_thrust", "cruise_speed", "cruise_altitude","nominal_range"]


    st.header("How would you like to search the name of your airplane?")
    # Choice: Use aircraft type or skip directly to ICAO
    search_option = st.radio(
        "",
        ("By Aircraft manufactor and ICAO Code", "By Aircraft Type and ICAO Code", "By ICAO Code Only")
    )


    if search_option == "By Aircraft manufactor and ICAO Code":
        # List of the name of the aircraft construstor
        constructor = [" "]
        errors = ["string", "mach", "None", "unknown", "int", "m", "deg", "m2", "kg", "no_dim", "kW", "N", "km/h", "ft", "km"]
        for element in data_airplanes["Constructor"]:
            if element not in errors:
                if element not in constructor:
                    constructor.append(element)

        # Chose of the constructor
        constructor1 = st.selectbox('From which constructor your plane come?',
                                constructor)

        if constructor1 != " ":
            st.success(f"You selected: {constructor1}")
            data_airplanes_cons = data_airplanes[data_airplanes["Constructor"] == constructor1]
            if not data_airplanes_cons.empty:
                combined_data = pd.DataFrame({"Property": prop})
                for idx, (_, row) in enumerate(data_airplanes_cons.iterrows(), start=1):
                    column_name = f"{idx}"
                    combined_data[column_name] = [row.get(p, "N/A") for p in prop]
                st.dataframe(combined_data, hide_index=True)


            # User input for ICAO code
            icao_code = st.text_input("Enter an ICAO code:")

            if icao_code:
                # Find the IATA code from the ICAO code
                filtered_icao = data_airplanes[data_airplanes["icao_code"] == icao_code]

                if not filtered_icao.empty:
                    iata_code = filtered_icao["iata_code"].iloc[0]
                    st.success(f"IATA code found: {iata_code}")

                    # Filter airplane details by IATA code and selected construtor
                    airplane_info = data_airplanes[
                        (data_airplanes["iata_code"] == iata_code) &
                        (data_airplanes["Constructor"] == constructor1)
                    ]

                    if not airplane_info.empty:
                        st.success(f"Airplane details for IATA code '{iata_code}' and constructor '{constructor1}':")
                        combined_data = pd.DataFrame({"Property": prop})

                        for idx, (_, row) in enumerate(airplane_info.iterrows(), start=1):
                            column_name = f"{idx}"
                            combined_data[column_name] = [row.get(p, "N/A") for p in prop]

                        st.dataframe(combined_data, hide_index=True)

                    else:
                        st.warning(f"No airplane details found for IATA code '{iata_code}' and constructor '{constructor1}'.")
                else:
                    st.warning(f"No IATA code found for ICAO code '{icao_code}'.")
        else:
            st.warning("Please select an aircraft constructor to proceed.")

    elif search_option == "By Aircraft Type and ICAO Code":
        # Dropdown for aircraft type
        atp = [" ", "General", "Commuter", "Regional",
                "Short Medium", "Long Range"]
        corres = ["", "general", "commuter", "regional",
                    "short_medium", "long_range"]

        selected_type1 = st.selectbox("Which type of aircraft do you have?", atp)
        selected_type = ""
        for i in range(len(atp)):
            if atp[i] == selected_type1:
                selected_type = corres[i]

        if selected_type1 != " ":
            st.success(f"You selected: {selected_type1}")
            data_airplanes_type = data_airplanes[data_airplanes["airplane_type"] == selected_type]
            if not data_airplanes_type.empty:
                combined_data = pd.DataFrame({"Property": prop})

                for idx, (_, row) in enumerate(data_airplanes_type.iterrows(), start=1):
                    column_name = f"{idx}"
                    combined_data[column_name] = [row.get(p, "N/A") for p in prop]
                st.dataframe(combined_data, hide_index=True)

            # User input for ICAO code
            icao_code = st.text_input("Enter an ICAO code:")

            if icao_code:
                # Find the IATA code from the ICAO code
                filtered_icao = data_airplanes[data_airplanes["icao_code"] == icao_code]

                if not filtered_icao.empty:
                    iata_code = filtered_icao["iata_code"].iloc[0]
                    st.success(f"IATA code found: {iata_code}")

                    # Filter airplane details by IATA code and selected type
                    airplane_info = data_airplanes[
                        (data_airplanes["iata_code"] == iata_code) &
                        (data_airplanes["airplane_type"] == selected_type)
                    ]

                    if not airplane_info.empty:
                        st.success(f"Airplane details for IATA code '{iata_code}' and type '{selected_type1}':")
                        combined_data = pd.DataFrame({"Property": prop})

                        for idx, (_, row) in enumerate(airplane_info.iterrows(), start=1):
                            column_name = f"{idx}"
                            combined_data[column_name] = [row.get(p, "N/A") for p in prop]

                        st.dataframe(combined_data, hide_index=True)

                    else:
                        st.warning(f"No airplane details found for IATA code '{iata_code}' and type '{selected_type1}'.")
                else:
                    st.warning(f"No IATA code found for ICAO code '{icao_code}'.")
        else:
            st.warning("Please select an aircraft type to proceed.")

    elif search_option == "By ICAO Code Only":
        # User input for ICAO code without selecting type
        icao_code = st.text_input("Enter an ICAO code:")

        if icao_code:
            # Find the IATA code from the ICAO code
            filtered_icao = data_airplanes[data_airplanes["icao_code"] == icao_code]

            if not filtered_icao.empty:
                iata_code = filtered_icao["iata_code"].iloc[0]
                st.success(f"IATA code found: {iata_code}")

                # Retrieve all airplane details for the matched IATA code
                airplane_info = data_airplanes[data_airplanes["iata_code"] == iata_code]

                if not airplane_info.empty:
                    st.success(f"Airplane details for IATA code '{iata_code}':")
                    combined_data = pd.DataFrame({"Property": prop})

                    for idx, (_, row) in enumerate(airplane_info.iterrows(), start=1):
                        column_name = f"{idx}"
                        combined_data[column_name] = [row.get(p, "N/A") for p in prop]

                    st.dataframe(combined_data, hide_index=True)
                else:
                    st.warning(f"No airplane details found for IATA code '{iata_code}'.")
            else:
                st.warning(f"No IATA code found for ICAO code '{icao_code}'.")
        else:
            st.warning("Please select an ICAO code to proceed.")


    # User input for airplane name
    airplane = st.text_input("Enter the name of your aircraft (you can use the search tool just above): ")
    final_data = []
    if data_airplanes[data_airplanes["name"] == airplane].empty:
        st.warning(f"No airplane found for the name '{airplane}'.")
    if airplane != "" and not data_airplanes[data_airplanes["name"] == airplane].empty and data_airplanes[data_airplanes["name"] == airplane][data_airplanes["airplane_type"] == "business"].empty:
        st.success(f"Airplane found: {airplane}")

        # Data of the plane the user search
        final_data = data_airplanes[data_airplanes["name"] == airplane]
        final = pd.DataFrame({"Property": prop})

        for idx, (_, row) in enumerate(final_data.iterrows(), start=1):
            column_name = f"{idx}"
            final[column_name] = [row.get(p, "N/A") for p in prop]

        st.dataframe(final, hide_index=True)


        st.write("")

        st.header("Make a configuration for your " + airplane)
        st.write("### Design an " + airplane + " like airplane")


        # Initialization of gam entries
        design_mission = {"category": "",
                          "npax": "",
                          "speed": "",
                          "range": "",
                          "altitude": "",
                          "mtow": "",
                          "owe": "",
                          "payload": "",
                          "payload_max": "",}
        gam = GAM()


        # Complete the power systeme
        st.write("#### Choose your parameters for the power system.")

        errors = ["string", "mach", "None", "unknown", "int", "m", "deg", "m2", "kg", "no_dim", "kW", "N", "km/h", "ft", "km"]
        power_data = ["", "", "", "", ""]

        energy_type = ["", "petrol", "kerosene", "gasoline", "compressed_h2", "liquid_h2", "liquid_ch4", "liquid_nh3", "battery"]
        energy = st.selectbox("Choose the energy type you want", energy_type)
        power_data[0] = energy

        nbengine = st.text_input("Choose the number of engine you want.")
        if nbengine != "":
            if int(nbengine) <= 12 and is_integer(int(nbengine)):
                power_data[1] = int(nbengine)

        engine_type = ["", "turbofan", "turboprop", "piston", "emotor"]
        etype = st.selectbox("Choose the engine type you want", engine_type)
        power_data[2] = etype

        if power_data[2] == "turbofan":
            power_data[3] = "fan"
        elif power_data[2] == "turboprop":
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


        # Complete design mission
        st.write("### Tune the design mission of the "+ airplane)

        # Complete category
        category = ["general", "commuter", "regional", "short_medium", "long_range"]
        for elec in category:
            test_cat = final_data[final_data["airplane_type"] == elec]
            if not test_cat.empty:
                design_mission["category"] = elec


        # Complete npax
        pax = st.text_input("Choose the number of PAX in the airplane.")
        if pax != "":
            if is_integer(int(pax)) == False:
                st.warning("Please select a number for the number of PAX")
            else:
                design_mission["npax"] = int(pax)

        # Complete speed
        cruise_speed = st.text_input("Choose the cruise speed of your airplane in km/h or in Mach number.")
        if cruise_speed != "":
            if is_float(float(cruise_speed)) and float(cruise_speed) > 1:
                design_mission["speed"] = unit.convert_from("km/h", int(cruise_speed))
            elif is_float(float(cruise_speed)) and float(cruise_speed) < 1:
                design_mission["speed"] = float(cruise_speed)
            else:
                st.warning("Please select a number for the number of cruise speed")

        # Complete range
        dis = {"general": 500, "commuter": 1500, "regional": 4500,
               "short_medium": 8000, "long_range": 15000}
        for key in dis:
            test = final_data[final_data["airplane_type"] == key]
            if not test.empty:
                if dis[key] - 1500 >= 0:
                    range_slider = st.slider("Range of the aircraft (in km):", dis[key] - 1500, dis[key] + 1500, dis[key], 10)
                    range_slider = int(st.text_input("Select the precise design range you require ", range_slider))
                    st.write(f"### Selected range: {range_slider} km")
                else:
                    range_slider = st.slider("Range of the aircraft (in km):", 0, dis[key] + 1500, dis[key], 10)
                    range_slider = int(st.text_input("Select the precise design range you require ", range_slider))
                    st.write(f"### Selected range: {range_slider} km")

        design_mission["range"] = unit.convert_from("km", range_slider)

        # Complete altitude
        cruise_altitude = st.text_input("Choose the cruise altitude of your airplane (in feet).")
        if cruise_altitude != "":
            if is_integer(int(cruise_altitude)) == False:
                st.warning("Please select a number for the number of cruise altitude (in m).")
            else:
                design_mission["altitude"] = int(cruise_altitude)*0.3048

        # Complete MTOW
        for e in data_airplanes["mtow"]:
            if e not in errors:
                test_mtow = final_data[final_data["mtow"] == e]
                if not test_mtow.empty:
                    design_mission["mtow"] = e

        # Complete OWE
        for e in data_airplanes["owe"]:
            if e not in errors:
                test_owe = final_data[final_data["owe"] == e]
                if not test_owe.empty:
                    design_mission["owe"] = e

        # Complete payload
        for key in dis:
            test = final_data[final_data["airplane_type"] == key]
            if not test.empty:
                if design_mission["npax"] != "":
                    payload = design_mission["npax"]*gam.mpax_dict[key]
                    design_mission["payload"] = payload

        #payload = st.text_input("Choose the payload of your airplane (in KG).")
        #if payload != "":
        #    if is_integer(int(payload)) == False:
        #        st.warning("Please select a number for the number of payload.")
        #    else:
        #        design_mission["payload"] = int(payload)

        # Complete max_payload
        if design_mission["payload"] != "":
            max_payload = design_mission["payload"]*gam.max_payload_factor
            design_mission["payload_max"] = float(max_payload)

        #max_payload = st.text_input("Choose the max payload of your airplane (in KG).")
        #if max_payload != "":
        #    if is_integer(int(max_payload)) == False:
        #        st.warning("Please select a number for the number of max payload.")
        #   else:
        #       design_mission["payload_max"] = int(max_payload)



        st.write("")
        c = 0
        this_dict = {}
        for key in design_mission:
            if design_mission[key] != "":
                c +=1
        if c == 9:
            table_rows = []
            this_dict = gam.tune_design(power_system, design_mission)
            st.write("What property of the airplane do you want to see:")

            Name = st.checkbox("Name")
            if Name:
                table_rows.append({
                        "Property" : "Name",
                        "Value" : airplane
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
        else:
            st.warning("Please select all the parameters for the design missoin.")


        st.write("")
        st.write("Compute and build the Payload-Range of the airplane")
        if this_dict != {}:
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

                duplicate_name = any(ele[3] == name and ele[3] != "" for ele in st.session_state.VARG2)
                if duplicate_name:
                    st.warning("Please select a new name for this AC.")
                else:
                    if st.button("Yes, save the AC", key="save_new_ac"):
                        tup = (this_dict, two_dict, table, name)
                        st.session_state.VARG2.append(tup)
                        if name:
                            tup = (this_dict, two_dict, table, name)
                            st.session_state.VARG2.append(tup)
                            st.success(f"{name} saved!")
                        else:
                            tup = (this_dict, two_dict, table, f"AC {len(st.session_state.VARG1)}")
                            st.session_state.VARG2.append(tup)
                            st.success(f"AC {len(st.session_state.VARG2)} saved!")

            st.write("")
            st.write("### Saved AC")
            if st.session_state.VARG2:
                for idx, config in enumerate(st.session_state.VARG2, start=1):

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
                del st.session_state.VARG2[st.session_state.deleted_index]
                del st.session_state.deleted_index
                st.rerun()



#            with right_column3:
#                st.write("##")
#                st.button("No, delete this configuration")

            st.write("")
            st.header("Show the result for the generic aiplane eand with your configuration")

            if 'info_all' not in st.session_state:
                st.session_state.info_all = False

            left_column6, right_column6 = st.columns(2)

            with left_column6:
                if st.button("Show all of the informations about the configurations"):
                    st.session_state.info_all = True
            with right_column6:
                if st.button("Hide all the informations about the configurations"):
                    st.session_state.info_all = False

            if st.session_state.info_all:
                if st.session_state.VARG2:
                    consolidated_data = {}
                    for idx, config in enumerate(st.session_state.VARG2, start=1):
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
            if st.session_state.VARG2:
                for idx, config in enumerate(st.session_state.VARG2, start=1):
                    config_list.append(config[0])
                    name_list.append(config[3])
                gam.payload_range_graph(config_list, name_list)



            st.write("")
            st.header("Tweak the" + airplane + " airplane design")
            if st.session_state.VARG2:
                configs = []
                for element in st.session_state.VARG2:
                    configs.append(element)
                na = [""]
                for ele in configs:
                    na.append(ele[3])
                config = st.selectbox("Choose the AC design you want to teawk.", na)
                selec_conf = 0
                for ele in configs:
                    if ele[3] == config:
                        selec_conf = ele
                if selec_conf != 0:
                    st.write("### Tweak the data from the "+ config + " " + airplane + " airplane.")
                    t_power = selec_conf[0]["power_system"]
                    t_mission = {}
                    t_mission["category"] = selec_conf[0]["mission"]["category"]

                    power_data2 = ["", "", "", "", ""]

                    energy_type2 = ["", "petrol", "kerosene", "gasoline", "compressed_h2", "liquid_h2", "liquid_ch4", "liquid_nh3", "battery"]
                    energy2 = st.selectbox("Choose the new energy type", energy_type2)
                    if energy2 != "":
                        power_data2[0] = energy2
                    else:
                        power_data2[0] = t_power["energy_type"]

                    engine_count2 =  ["", 1, 2, 4]
                    nbengine2 = st.selectbox("Choose the new engine count", engine_count2)
                    if nbengine2 != "":
                        power_data2[1] = nbengine2
                    else:
                        power_data2[1] = t_power["engine_count"]

                    engine_type2 = ["", "turbofan", "turboprop", "piston", "emotor"]
                    etype2 = st.selectbox("Choose the new engine type", engine_type2)
                    if etype2 == "":
                        power_data2[2] = t_power["engine_type"]
                    else:
                        power_data2[2] = etype2

                    if power_data2[2] == "turbofan":
                        power_data2[3] = "fan"
                    elif power_data2[2] == "turboprop":
                        power_data2[3] = "propeller"
                    else:
                        power_data2[3] = "None"

                    if power_data2[2] == "turbofan":
                        bpr2 = st.slider("New BPR of the aircraft engine:", 5, 15, 10, 1)
                        bpr12 = bpr2
                        bpr12 = st.text_input("Select the precise new BPR of the aircraft engine ", bpr12)
                        if bpr12 != bpr2:
                            bpr2 = bpr12
                        if bpr12 != "":
                            if is_float(float(bpr12)):
                                power_data2[4] = float(bpr12)
                            else:
                                st.warning("Please choose an bpr to proceed.")
                        else:
                            power_data2[4] = t_power["bpr"]
                    else:
                        power_data2[4] = "None"

                    st.write("")
                    st.write("Do you want to see the power settings you choose?")

                    left2, right2 = st.columns(2)
                    t_power = {"energy_type" : power_data2[0], "engine_count" : power_data2[1],
                                "engine_type" : power_data2[2], "thruster_type" : power_data2[3], "bpr" : power_data2[4]}
                    st.session_state.t_power_system = False
                    if 't_power_system' not in st.session_state:
                        st.session_state.t_power_system = False

                    with left2:
                        if st.button("Show the tweaked power system"):
                            st.session_state.t_power_system = True
                    with right2:
                        if st.button("Hide the tweaked power system"):
                            st.session_state.t_power_system = False

                    if st.session_state.t_power_system:
                        dataframes_tp = []
                        compt = 0
                        for key in t_power:
                            if t_power[key] != "":
                                tup = (key, t_power[key])
                                dataframes_tp.append(tup)
                                compt +=1
                            else:
                                st.warning("Choose a parameter for the "+ key+ " to proceed.")
                        if compt == 5:
                            st.dataframe(dataframes_tp, hide_index=True)


                    # Tweak Mission
                    npax_slider = st.slider("Number of PAX of the aircraft:", int(selec_conf[0]["mission"]["npax"]*0.9), int(selec_conf[0]["mission"]["npax"]*1.1), selec_conf[0]["mission"]["npax"], 1)
                    npax_slider = int(st.text_input("Select the precise number of PAX ", npax_slider))
                    t_mission["npax"] = npax_slider

                    speed = selec_conf[0]["mission"]["speed"]
                    if speed < 1:
                        if speed*0.9 < 0.5:
                            if speed*1.1 > 0.95:
                                speed_slider = st.slider("Speed of the aircraft (in Mach Number):", 0.5, 0.95, speed, 0.01)
                                speed_slider = float(st.text_input("Select the precise speed you require ", speed_slider))
                                t_mission["speed"] = speed_slider
                            else:
                                speed_slider = st.slider("Speed of the aircraft (in Mach Number):", 0.5, speed*1.1, speed, 0.01)
                                speed_slider = float(st.text_input("Select the precise speed you require ", speed_slider))
                                t_mission["speed"] = speed_slider
                        else:
                            if speed*1.1 > 0.95:
                                speed_slider = st.slider("Speed of the aircraft (in Mach Number):", speed*0.9, 0.95, speed, 0.01)
                                speed_slider = float(st.text_input("Select the precise speed you require ", speed_slider))
                                t_mission["speed"] = speed_slider
                            else:
                                speed_slider = st.slider("Speed of the aircraft (in Mach Number):", speed*0.9, speed*1.1, speed, 0.01)
                                speed_slider = float(st.text_input("Select the precise speed you require ", speed_slider))
                                t_mission["speed"] = speed_slider
                    if speed > 1:
                        speed_slider = st.slider("Speed of the aircraft (in km/h):", int(speed*3.6*0.9), int(speed*3.6*1.1), int(speed*3.6), 1)
                        speed_slider = float(st.text_input("Select the precise speed you require ", speed_slider))
                        t_mission["speed"] = speed_slider

                    dis = selec_conf[0]["mission"]["range"]
                    dis = int(dis/1000)
                    dis_slider = st.slider("Range of the aircraft (in km):", int(dis*0.9), int(dis*1.1), dis, 1)
                    dis_slider = int(st.text_input("Select the precise range of the aircaft (in km) :", dis_slider))
                    t_mission["range"] = dis_slider*1000

                    alt = int(selec_conf[0]["mission"]["altitude"]*3.28084)
                    alt_slider = st.slider("Cruise altitude of the aircraft (in feet):", int(alt*0.9), int(alt*1.1), alt, 1)
                    alt_slider = int(st.text_input("Select the precise cruise altitude of the aircaft (in feet) :", alt_slider))
                    t_mission["altitude"] = alt_slider*0.3048

                    t_mtow = float(selec_conf[0]["mission"]["mtow"])
                    t_mtow_slider = st.slider("MTOW of the aircraft (in kg):", t_mtow*0.9, t_mtow*1.1, t_mtow, 1.0)
                    t_mtow_slider = float(st.text_input("Select the precise  MTOW of the aircaft (in kg) :", t_mtow_slider))
                    t_mission["mtow"] = t_mtow_slider

                    t_owe = float(selec_conf[0]["mission"]["owe"])
                    t_owe_slider = st.slider("OWE of the aircraft (in kg):", t_owe*0.9, t_owe*1.1, t_owe, 1.0)
                    t_owe_slider = float(st.text_input("Select the precise OWE of the aircaft (in kg) :", t_owe_slider))
                    t_mission["owe"] = t_owe_slider

                    t_payload = float(selec_conf[0]["mission"]["payload"])
                    t_payload_slider = st.slider("Choose the payload of the aircraft (in kg):", t_payload*0.9, t_payload*1.1, t_payload, 1.0)
                    t_payload_slider = float(st.text_input("Select the precise payload of the aircaft (in kg) :", t_payload_slider))
                    t_mission["payload"] = t_payload_slider

                    t_maxpayload = float(selec_conf[0]["mission"]["payload_max"])
                    t_maxpayload_slider = st.slider("Choose the max payload of the aircraft (in kg):", t_maxpayload*0.9, t_maxpayload*1.1, t_maxpayload, 1.0)
                    t_maxpayload_slider = float(st.text_input("Select the precise max payload of the aircaft (in kg) :", t_maxpayload_slider))
                    t_mission["payload_max"] = t_maxpayload_slider

                    st.write("")
                    st.write("Do you want to see the tweaked design mission you choose?")

                    left3, right3 = st.columns(2)
                    st.session_state.tweakmission = False
                    if 'tweakmission' not in st.session_state:
                        st.session_state.tweakmission = False

                    with left3:
                        if st.button("Show tweaked design mission"):
                            st.session_state.tweakmission = True
                    with right3:
                        if st.button("Hide tweaked design mission"):
                            st.session_state.tweakmission = False

                    if st.session_state.tweakmission:
                        dataframes = []
                        compt = 0
                        for key in design_mission:
                            if design_mission[key] != "":
                                tup = (key, t_mission[key])
                                dataframes.append(tup)
                                compt +=1
                            else:
                                st.warning("Choose a parameter for the "+ key+ " to proceed.")
                        if compt == 9:
                            st.dataframe(dataframes, hide_index=True)
                        else:
                            st.warning("Please select all the parameters for the design missoin.")


                    gam2 = GAM()
                    table_rows_2 = []
                    this_dict2 = gam2.tune_design(t_power, t_mission)
                    st.write("What property of the airplane do you want to see:")

                    Name = st.checkbox("Name", key = "Name_tweak")
                    if Name:
                        table_rows_2.append({
                                "Property" : "Name",
                                "Value" : "Tweked "+airplane
                            })
                    propulsion = st.checkbox("Propulsion system definition", key = "t_prop")
                    if propulsion:
                        table_rows_2.append({
                            "Property": "Engine type",
                            "Value": this_dict2["power_system"]["engine_type"]
                        })
                        table_rows_2.append({
                            "Property": "Energy source",
                            "Value": this_dict2["power_system"]["energy_type"]
                        })
                        table_rows_2.append({
                            "Property": "Thruster type",
                            "Value": this_dict2["power_system"]["thruster_type"]
                        })
                        table_rows_2.append({
                            "Property" : " Number of engine ",
                            "Value" : "%.0f" % this_dict2["n_engine"]
                        })
                        table_rows_2.append({
                            "Property": "By Pass Ratio",
                            "Value": this_dict2["by_pass_ratio"]
                        })
                    mission = st.checkbox("Design mission definition", key = "t_mission")
                    if mission:
                        table_rows_2.append({
                            "Property" : " Airplane type",
                            "Value" : this_dict2["airplane_type"]
                        })
                        table_rows_2.append({
                            "Property" : " Number of passenger ",
                            "Value" : "%.0f" % this_dict2["npax"]
                        })
                        table_rows_2.append({
                            "Property" : " Design range ",
                            "Value" : "%.0f km" % unit.convert_to("km", this_dict2["nominal_range"])
                        })
                        if this_dict2["cruise_speed"] > 1:
                            table_rows_2.append({
                                "Property" : " Cruise speed ",
                                "Value" : "%.1f km/h" % unit.convert_to("km/h", this_dict2["cruise_speed"]) 
                            })
                        if this_dict2["cruise_speed"] <= 1:
                            table_rows_2.append({
                                "Property" : " Cruise Mach ",
                                "Value" : "%.2f" % this_dict2["cruise_speed"]
                            })
                        table_rows_2.append({
                            "Property" : " Cruise altitude ",
                            "Value" : "%.1f ft" % unit.convert_to("ft", this_dict2["altitude_data"]["mission"]),
                        })
                    breakdown = st.checkbox("Mass breakdown", key = "t_braekdown")
                    if breakdown:
                        table_rows_2.append({
                            "Property": "MTOW",
                            "Value": "%.0f kg" % this_dict2["mtow"]
                        })
                        table_rows_2.append({
                            "Property": "MZFW",
                            "Value": "%.0f kg" % this_dict2["mzfw"]
                        })
                        table_rows_2.append({
                            "Property": "Payload max",
                            "Value": "%.0f kg" % this_dict2["payload_max"]
                        })
                        table_rows_2.append({
                            "Property": "Maximum payload factor",
                            "Value": "%.3f" % this_dict2["max_payload_factor"]
                        })
                        table_rows_2.append({
                            "Property": "OWE",
                            "Value": "%.0f kg" % this_dict2["owe"]
                        })
                        table_rows_2.append({
                            "Property": "Operator items",
                            "Value": "%.0f kg" % this_dict2["op_item"]
                        })
                        table_rows_2.append({
                            "Property": "MWE",
                            "Value": "%.0f kg" % this_dict2["mwe"]
                        })
                        table_rows_2.append({
                            "Property": "Furnishing",
                            "Value": "%.0f kg" % this_dict2["furnishing"]
                        })
                        table_rows_2.append({
                            "Property": "Standard MWE",
                            "Value": "%.0f kg" % this_dict2["std_mwe"]
                        })
                        table_rows_2.append({
                            "Property": "Propulsion mass",
                            "Value": "%.0f kg" % this_dict2["propulsion_mass"]
                        })
                        table_rows_2.append({
                            "Property": "Energy storage mass",
                            "Value": "%.0f kg" % this_dict2["energy_storage_mass"]
                        })
                        table_rows_2.append({
                            "Property": "Fuel cell system mass",
                            "Value": "%.0f kg" % this_dict2["fuel_cell_system_mass"]
                        })
                        table_rows_2.append({
                            "Property": "Basic MWE",
                            "Value": "%.0f kg" % this_dict2["basic_mwe"]
                        })
                        table_rows_2.append({
                            "Property": "MWE shift",
                            "Value": "%.0f kg" % this_dict2["stdm_shift"]
                        })
                    output = st.checkbox("Design mission output", key = "t_output")
                    if output:
                        table_rows_2.append({
                            "Property": "Nominal pax mass allowance",
                            "Value": "%.1f kg" % this_dict2["mpax"]
                        })
                        table_rows_2.append({
                            "Property": "Nominal payload delta",
                            "Value": "%.0f kg" % this_dict2["delta_payload"]
                        })
                        table_rows_2.append({
                            "Property": "Nominal payload",
                            "Value": "%.0f kg" % this_dict2["payload"]
                        })
                        table_rows_2.append({
                            "Property": "Nominal mission time",
                            "Value": "%.1f h" % unit.h_s(this_dict2["nominal_time"])
                        })

                        table_rows_2.append({
                            "Property": "Mission fuel",
                            "Value": "%.0f kg" % this_dict2["mission_fuel"]
                        })
                        table_rows_2.append({
                            "Property": "Reserve fuel",
                            "Value": "%.0f kg" % this_dict2["reserve_fuel"]
                        })
                        table_rows_2.append({
                            "Property": "Total fuel",
                            "Value": "%.0f kg" % this_dict2["total_fuel"]
                        })
                        table_rows_2.append({
                            "Property": "Fuel consumption",
                            "Value": "%.2f L/pax/100km" % unit.convert_to("L", this_dict2["fuel_consumption"] * unit.m_km(100))
                        })
                        table_rows_2.append({
                            "Property": "Mission energy",
                            "Value": "%.0f kWh" % unit.kWh_J(this_dict2["mission_enrg"])
                        })
                        table_rows_2.append({
                            "Property": "Reserve energy",
                            "Value": "%.0f kWh" % unit.kWh_J(this_dict2["reserve_enrg"])
                        })
                        table_rows_2.append({
                            "Property": "Total energy",
                            "Value": "%.0f kWh" % unit.kWh_J(this_dict2["total_energy"])
                        })
                        table_rows_2.append({
                            "Property": "Energy consumption",
                            "Value": "%.2f kWh/pax/100km" % unit.kWh_J(this_dict2["enrg_consumption"] * unit.m_km(100))
                        })
                        table_rows_2.append({
                            "Property": "Wake Turbulence Category",
                            "Value": this_dict2["wake_turbulence_class"]
                        })
                    factor = st.checkbox("Factors & Efficiencies", key = "t_factor")
                    if factor:
                        table_rows_2.append({
                            "Property": "Max power",
                            "Value": "%.0f kW" % unit.kW_W(this_dict2["max_power"])
                        })
                        table_rows_2.append({
                            "Property": "Standard mass factor",
                            "Value": "%.4f" % this_dict2["stdm_factor"]
                        })
                        table_rows_2.append({
                            "Property": "Aerodynamic efficiency factor",
                            "Value": "%.4f" % this_dict2["aero_eff_factor"]
                        })
                        table_rows_2.append({
                            "Property": "Aerodynamic efficiency (L/D)",
                            "Value": "%.2f" % this_dict2["aerodynamic_efficiency"]
                        })
                        table_rows_2.append({
                            "Property": "Propulsion system efficiency",
                            "Value": "%.3f" % this_dict2["propulsion_system_efficiency"]
                        })
                        table_rows_2.append({
                            "Property": "Storage energy density",
                            "Value": "%.0f Wh/kg" % unit.Wh_J(this_dict2["storage_energy_density"])
                        })
                        table_rows_2.append({
                            "Property": "Propulsion power density",
                            "Value": "%.2f kW/kg" % unit.kW_W(this_dict2["propulsion_power_density"])
                        })
                        table_rows_2.append({
                            "Property": "Structural factor (OWE/MTOW)",
                            "Value": "%.2f" % this_dict2["structural_factor"]
                        })
                        table_rows_2.append({
                            "Property": "Energy efficiency factor, P.K/E",
                            "Value": "%.2f pax.km/kWh" % unit.convert_to("km/kWh", this_dict2["pk_o_enrg"])
                        })
                        table_rows_2.append({
                            "Property": "Mass efficiency factor, P.K/M",
                            "Value": "%.2f pax.km/kg" % unit.convert_to("km/kg", this_dict2["pk_o_mass"])
                        })

                    st.write("")
                    table2 = pd.DataFrame(table_rows_2)
                    st.dataframe(table2, width=600, column_config={"Property": {"width": 300}, "Value": {"width": 300},}, hide_index=True)


                    st.write("")
                    st.write("Compute and build the Payload-Range of the airplane")
                    if this_dict2 != {}:
                        two_dict2 = gam2.build_payload_range(this_dict2)    # Compute payload-range data and add them in ac_dict
                        left4 , right4 = st.columns(2)

                        if 'payload_info2' not in st.session_state:
                            st.session_state.payload_info2 = False

                        with left4:
                            if st.button("Show Tweaked payload-range information"):
                                st.session_state.payload_info2 = True
                        with right4:
                            if st.button("Hide treaked payload-range information"):
                                st.session_state.payload_info2 = False

                        if st.session_state.payload_info2 :
                            gam2.print_payload_range(this_dict2)    # Print payload-range data


                        st.write("")
                        st.write("Do you want to save this AC?")
                        left_3, right_3 = st.columns(2)

                        with left_3:
                            name2 = st.text_input("Choose the name of this Tweaked AC if you want.")

                            duplicate_name2 = any(ele[3] == name2 and ele[3] != "" for ele in st.session_state.VARG2)
                            if duplicate_name2:
                                st.warning("Please select a new name for this AC.")
                            else:
                                if st.button("Yes, save the AC", key="save_tweak_ac"):
                                    tup = (this_dict2, two_dict2, table2, name2)
                                    st.session_state.VARG2.append(tup)
                                    if name2:
                                        st.success(f"{name2} saved!")
                                    else:
                                        st.success(f"AC {len(st.session_state.VARG2)} saved!")

                        st.write("")
                        st.write("### Saved AC")
                        if st.session_state.VARG2:
                            for idx, config in enumerate(st.session_state.VARG2, start=1):

                                if config[3]:
                                    st.write(config[3])
                                else:
                                    st.write(f"**AC {idx}:**")

                                left5, right5 = st.columns(2)
                                if "AC" not in st.session_state:
                                    st.session_state.AC = False
                                with left5:
                                    if st.button(f"Show {config[3] or f'AC {idx}'}", key=f"show_tweak_{idx}"):
                                        st.session_state.AC = True
                                with right5:
                                    if st.button(f"Hide {config[3] or f'AC {idx}'}", key=f"hide_tweak_{idx}"):
                                        st.session_state.AC = False
                                if st.session_state.AC:
                                    st.dataframe(config[2], width=600, hide_index=True)


                                if st.button(f"Delete {config[3] or f'AC {idx}'}", key=f"delete_tweak_{idx}"):
                                    st.session_state.deleted_index = idx - 1

                        else:
                            st.info("No configurations saved yet.")


                        if "deleted_index" in st.session_state:
                            del st.session_state.VARG2[st.session_state.deleted_index]
                            del st.session_state.deleted_index
                            st.rerun()



                        with right_3:
                            st.write("##")
                            st.button("No, delete this tweaked AC")

                        st.write("")
                        st.header("Show the result for the " + airplane + " and with your configuration")

                        if 'info_all' not in st.session_state:
                            st.session_state.info_all = False

                        left6, right6 = st.columns(2)

                        with left6:
                            if st.button("Show all of the informations about the AC"):
                                st.session_state.info_all = True
                        
                        with right6:
                            if st.button("Hide all the informations about the AC"):
                                st.session_state.info_all = False

                        if st.session_state.info_all:
                            if st.session_state.VARG2:
                                consolidated_data2 = {}
                                for idx, config in enumerate(st.session_state.VARG2, start=1):
                                    config_table2 = config[2]
                                    for _, row in config_table2.iterrows():
                                        property_name = row["Property"]
                                        value = row["Value"]
                                        if property_name not in consolidated_data2:
                                            consolidated_data2[property_name] = {}
                                        consolidated_data2[property_name][f"Value{idx}"] = value

                                consolidated_table2 = pd.DataFrame.from_dict(consolidated_data2, orient="index")
                                consolidated_table2.reset_index(inplace=True)
                                consolidated_table2.rename(columns={"index": "Property"}, inplace=True)

                                st.dataframe(consolidated_table2, width=1000, hide_index=True)

                            else:
                                st.info("No configurations to display.")


                        config_list2 = []
                        name_list2 = []
                        if st.session_state.VARG2:
                            for idx, config in enumerate(st.session_state.VARG2, start=1):
                                config_list2.append(config[0])
                                name_list2.append(config[3])
                            gam2.payload_range_graph(config_list2, name_list2)
                else:
                    st.warning("Please select an AC to proceed.")
            else:
                st.info("No configurations to display.")
        else:
            st.warning("Please finish to choose the different parameters to proceed.")   
    else:
        st.warning("Please select the airplane to proceed.")




def main3():
    '''Main, display the dashboard'''
    st.set_page_config(
        page_title="Dashboard for Airplane Fuel Consumption",
        page_icon=":airplane:",
        layout="centered",
    )
    # App title
    st.title("Dashboard for Airplane Fuel Consumption with a tune existing airplane")
    setup3()





# Run the application
if __name__ == "__main__":
    main3()
