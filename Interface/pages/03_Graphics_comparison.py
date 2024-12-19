import streamlit as st
from gam_copy import GAM


def graphic():
    gam = GAM()
    graph_list = []
    name_list = []
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
        gam.payload_range_graph(graph_list, name_list)
    else:
        st.info("No configuration found")


def main():
    '''Main, display the dashboard'''
    st.set_page_config(
        page_title="Dashboard for Airplane Fuel Consumption",
        page_icon=":airplane:",
        layout="centered",
    )
    # App title
    st.title("Graph of payload in function of range")
    st.write("Every graph made before with the different method are presented here.")
    graphic()




# Run the application
if __name__ == "__main__":
    main()
