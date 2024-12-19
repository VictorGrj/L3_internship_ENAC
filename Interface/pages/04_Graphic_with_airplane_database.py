import streamlit as st
import pandas as pd
#import matplotlib as plt
import plotly.express as px

# Load data from the Excel file
def load_data(files):
    '''Read Excel files'''
    return pd.read_excel(files)

st.title("Graphics from Airplane Data Base")

# Load the Excel files
#file = "airplane_database_copieVF_test.csv"  # File with airplane details
file = "airplane_database_copieVF.xlsx"

try:
    data_airplanes = load_data(file)
except FileNotFoundError as e:
    st.error(f"File not found: {e.filename}")

# Data
prop = ["", "airplane_type",  "name", "Constructor", "icao_code", "iata_code", "n_pax", "owe",
        "mtow", "mlw", "max_fuel", "n_engine", "engine_type", "thruster_type", "powerplant", "bpr",
        "energy_type", "max_power", "max_thrust", "cruise_speed", "cruise_altitude","nominal_range"]

show = ["", "Airplane type", "Name of the airplane", "Manufacturer", "ICAO code", "IATA code",
        "Number of pax", "OWE", "MTOW", "MLW", "Max fuel", "Number of engine", "Engine type",
        "Thruster type", "Powerplant", "BPR", "Energy type", "Max power", "Max Thrust",
        "Cruise speed", "Cruise altitude", "Nominale range"]

errors = ["string", "None", "int", "m", "deg", "m2", "kg",
          "no dim", "kW", "N", "km/h", "ft", "km", "mach"]

colors = {"general": "#008000", "commuter": "#FFD700", "regional": "#FF8C00", "short_medium": "#9400D3", "long_range": "#FF0000", "business": "#0000FF"}


# Parameters selection
if st.checkbox("See all the airplane data base"):
    if not data_airplanes.empty:
        combined_data = pd.DataFrame({"Propriété": prop})

        for idx, (_, row) in enumerate(data_airplanes.iterrows(), start=1):
            column_name = f"Aircraft {idx}"
            combined_data[column_name] = [row.get(p, "None") for p in prop]
        st.dataframe(combined_data, hide_index=True)

st.write("")

## Selection of the 2 parameters
st.write("### Choose your parameters")
left_column1, right_column1 = st.columns(2)

with left_column1:
    para1 = st.selectbox("What parametre you want to see?", show)

show2 = []
for element in show:
    if element != para1:
        show2.append(element)

with right_column1:
    para2 = st.selectbox("In fonction of what other parameter " + para1, show2)


# Make the graphic
# Create the 2 list of data
if para1 != "" and para2 != "":
    st.success("You choose: "+ para1+ " and "+ para2+ " as parameters")

    for i in range(len(prop)):
        if show[i] == para1:
            par1 = prop[i]
            prop2 = prop
            del(prop2[i])
    for j in range(len(show2)):
        if show2[j] == para2:
            par2 = prop2[j]

    data1 = []
    data2 = []
    colors_list = []

    for ele1, ele2, airplane_type in zip(data_airplanes[par1], data_airplanes[par2], data_airplanes["airplane_type"]):
        if ele1 not in errors and ele2 not in errors:
            data1.append(ele1)
            data2.append(ele2)

            colors_list.append(colors.get(airplane_type, "#808080"))


    data_frame = pd.DataFrame({
        para2: data2,
        para1: data1,
        "Color": colors_list
    })


    fig = px.scatter(
        data_frame,
        x=para2,
        y=para1,
        color=data_frame["Color"],
        color_discrete_map="identity",
        title=f"{para1} in fonction of {para2}",
        labels={para1: para1, para2: para2},
    )


    # Add the AC you made at the graphic with the airplane data base data

    st.header("Choose the airplane you want to add at the graphic")

    graph_list = []
    if st.session_state.VARG1:
        data1 = st.session_state.VARG1
        for element1 in data1:
            graph_list.append(element1)
    if st.session_state.VARG2:
        data2 = st.session_state.VARG2
        for element2 in data2:
            graph_list.append(element2)

    if graph_list != []:
        name = [""]
        for ele in graph_list:
            name.append(ele[3])
        config = st.selectbox("Choose the AC design you want to add the graph.", name)
        data_graph = 0
        for ele in graph_list:
            if ele[3] == config:
                data_graph = [ele[0], ele[3]]
        slt1 = None
        slt2 = None
        if data_graph != 0:
            if par1 == "name":
                slt1 = data_graph[1]
            if par2 == "name":
                slt2 = data_graph[1]
            for slt_ele in data_graph[0]:
                if par1 == slt_ele:
                    slt1 = data_graph[0][slt_ele]
                if par2 == slt_ele:
                    slt2 = data_graph[0][slt_ele]
                if slt_ele == "mission":
                    for key1 in slt_ele:
                        if par1 == key1:
                            slt1 = data_graph[0]["mission"][key1]
                        if par2 == key1:
                            slt2 = data_graph[0]["mission"][key1]
                if slt_ele == "altitude_data":
                    for key2 in slt_ele:
                        if par1 == key2:
                            slt1 = data_graph[0]["altitude_data"][key2]
                        if par2 == key2:
                            slt2 = data_graph[0]["altitude_data"][key2]
                if slt_ele == "reserve_data":
                    for key3 in slt_ele:
                        if par1 == key3:
                            slt1 = data_graph[0]["reserve_data"][key3]
                        if par2 == key3:
                            slt2 = data_graph[0]["reserve_data"][key3]
                if slt_ele == "power_system":
                    for key4 in slt_ele:
                        if par1 == key4:
                            slt1 = data_graph[0]["power_system"][key4]
                        if par2 == key4:
                            slt2 = data_graph[0]["power_system"][key4]
            else:
                if slt1 == None:
                    st.warning("Their is no values in the design airplane for the parameter "+ para1)
                if slt2 == None:
                    st.warning("Their is no values in the design airplane for the parameter "+ para2)
            if slt1 == None or slt2 == None:
                st.plotly_chart(fig)
                st.warning("The scatter plot doesn't include the airplane you made.")
            if slt1 != None and slt2 != None:
                special_point = pd.DataFrame({para2: [slt2], para1: [slt1], "Color": ["#FFFFFF"]})
                fig.add_scatter(x=[slt2], y=[slt1], mode="markers", marker=dict(color="white", size=10, symbol="star"), name="Airplane you choose")
                st.plotly_chart(fig)
                st.success("The scatter plot include the airplane you made.")

    # How do you want your graphic
    # Sidebar for selection
    #st.sidebar.title("Graph Options")
    #option = st.sidebar.radio(
    #    "Select the library to display the graph:",
    #    ["Streamlit Native", "Matplotlib", "Plotly"]
    #)
    # If Streamlit Native is selected, add an option to choose the chart type
    #if option == "Streamlit Native":
    #    chart_type = st.sidebar.radio(
    #        "Select the type of chart:",
    #        ["Line", "Bar", "Area", "Scatter"])

    # Display graph based on the selected option
    #if option == "Streamlit Native":
    #    st.write(f"Graph using Streamlit Native - {chart_type} Chart")

    #    if chart_type == "Line":
    #        st.line_chart(data_frame)
    #    elif chart_type == "Bar":
    #        st.bar_chart(data_frame)
    #    elif chart_type == "Area":
    #        st.area_chart(data_frame)
    #    elif chart_type == "Scatter":
    #        st.scatter_chart(data_frame)

    #elif option == "Matplotlib":
    #    st.write("Graph using Matplotlib")
    #    # Create a graph using Matplotlib
    #    fig2, ax = plt.pyplot.subplots()
    #    ax.plot(data2, data1, marker='o', color='b')
    #    ax.set_title("Graph of "+para2+" in function of "+para1)
    #    ax.set_xlabel(para2)
    #    ax.set_ylabel(para1)
    #    st.pyplot(fig2)

    #elif option == "Plotly":
    #    st.write("Graph using Plotly")
    #    # Create a graph using Plotly
    #    fig1 = px.line(x=data2, y=data1,labels={'x': para2, 'y': para1},
    #                   title="Graph of "+para2+" in function of "+para1)
    #    st.plotly_chart(fig1)

else:
    st.warning("Please select 2 parameters to proceed")
