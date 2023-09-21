import streamlit as st
import os
import pandas as pd
from plotly import graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import datetime
import plotly.express as px
from streamlit_extras.chart_container import chart_container

def read_scenario_file_excel(file = "scenarier.xlsx"):
    buildingtype_to_buildingcode = {
        "Hus" : "A",
        "Leilighet" : "B",
        "Kontor" : "C",
        "Butikk" : "D",
        "Hotell" : "E",
        "Barnehage" : "F",
        "Skole" : "G",
        "Universitet" : "H",
        "Kultur" : "I",
        "Sykehjem" : "J",
        "Andre" : "L"
        }
    variable_dict = {}
    xls_keys = list(pd.read_excel(file, sheet_name = None).keys())
    for key in xls_keys:
        df = pd.read_excel(file, sheet_name = key, index_col=0)
        df = df.rename(columns = buildingtype_to_buildingcode)
        df = df.T
        energy_dicts = df.to_dict()
        variable_dict[key] = energy_dicts
    #--
    energy_dicts_of_dicts = []
    for i in range(0, len(variable_dict)):
        energy_dicts_of_dicts.append(variable_dict[xls_keys[i]])
    return energy_dicts_of_dicts, xls_keys

def csv_to_df(folder_path = "data"):
    csv_file_list = []
    scenario_name_list = []
    filename_list = []
    df = pd.DataFrame({})
    for filename in os.listdir(folder_path):
        if filename.endswith("data.csv"):
            filename_list.append(filename)
            scenario_name_list.append(filename.split(sep = "_")[0])
            csv_file_list.append(filename)
    for i in range(0, len(csv_file_list)):
        df[f"{scenario_name_list[i]}"] = pd.read_csv(f"{folder_path}/{filename_list[i]}", header = None)
    return df

def select_scenario(df):
    options = df.columns
    default_options = options.to_list()

    selected_scenarios = st.multiselect("Velg scenarier", options = options, default = default_options, help = "Her kan du velge ett eller")
    if len(selected_scenarios) == 0:
        st.stop()
    return df[selected_scenarios]

def sort_columns_high_to_low(df):
    sorted_df = df.apply(lambda col: col.sort_values(ascending=False).reset_index(drop=True))
    return sorted_df

def rounding_to_int(number):
    return int(round(number, 0))

def plot_dataframe(df, color_sequence, sorting = True):
    df.sort_index(axis=1, inplace=True)
    if sorting == True:
        df = sort_columns_high_to_low(df)
        fig = px.line(df, x=df.index, y=df.columns, color_discrete_sequence=color_sequence)
        fig.update_layout(legend=dict(bgcolor="rgba(0,0,0,0)"))

        fig.update_traces(
            line=dict(
                width=1, 
            ))
        
        fig.update_xaxes(
            range=[0, 8760],
            title_text='Varighet [timer]',
            mirror=True,
            ticks="outside",
            showline=True,
            linecolor="black",
            gridcolor="lightgrey",
            )
    else:
        fig = px.area(df, x=df.index, y=df.columns)
       
        fig.update_traces(
            line=dict(
                width=0, 
                #color = color_sequence
                color = "black"
            ))
        fig.update_layout(
            legend=dict(yanchor="top", y=0.98, xanchor="left", x=0.01, bgcolor="rgba(0,0,0,0)"),
            xaxis = dict(
                tickmode = 'array',
                tickvals = [0, 24 * (31), 24 * (31 + 28), 24 * (31 + 28 + 31), 24 * (31 + 28 + 31 + 30), 24 * (31 + 28 + 31 + 30 + 31), 24 * (31 + 28 + 31 + 30 + 31 + 30), 24 * (31 + 28 + 31 + 30 + 31 + 30 + 31), 24 * (31 + 28 + 31 + 30 + 31 + 30 + 31 + 31), 24 * (31 + 28 + 31 + 30 + 31 + 30 + 31 + 31 + 30), 24 * (31 + 28 + 31 + 30 + 31 + 30 + 31 + 31 + 30 + 31), 24 * (31 + 28 + 31 + 30 + 31 + 30 + 31 + 31 + 30 + 31 + 30), 24 * (31 + 28 + 31 + 30 + 31 + 30 + 31 + 31 + 30 + 31 + 30 + 31)],
                ticktext = ["1.jan", "", "1.mar", "", "1.mai", "", "1.jul", "", "1.sep", "", "1.nov", "", "1.jan"]
                )
        )
        fig.update_xaxes(
        range=[0, 8760],
        title_text='',
        mirror=True,
        ticks="outside",
        showline=True,
        linecolor="black",
        gridcolor="lightgrey",
        )
    #-#--
    #--
    fig["data"][0]["showlegend"] = True
    fig.update_layout(
        #height = 1000,
        margin=dict(l=50,r=50,b=10,t=10,pad=0),
        legend={'title_text':''},
        barmode="stack", 
        plot_bgcolor="white", paper_bgcolor="white",
        legend_traceorder="reversed",
        )
    
 
    fig.update_yaxes(
        range=[-400, 600],
        title_text='Effekt [MW]',
        mirror=True,
        ticks="outside",
        showline=True,
        linecolor="black",
        gridcolor="lightgrey",
    )

    return fig

def plot_dataframe_moving_average(df, color_sequence = "red", window_size = 168):
    window_size = window_size
    moving_avg = df.rolling(window=window_size).mean()
    if color_sequence == "red":
        fig = px.line(moving_avg, x=moving_avg.index, y=moving_avg.columns)
        fig.update_traces(
        name = "Glidende gjennomsnitt over 1 uke",
        line=dict(
            width=1,
            #color = color_sequence
            color = "red",
        ))
    else:
        fig = px.line(moving_avg, x=moving_avg.index, y=moving_avg.columns, color_discrete_sequence=color_sequence)

    fig.update_traces(
        #name = df.co,
        line=dict(
            width=1,
            #color = color_sequence
        ))
    fig.update_layout(
        #legend=dict(yanchor="top", y=0.98, xanchor="left", x=0.01, bgcolor="rgba(0,0,0,0)"),
        xaxis = dict(
            tickmode = 'array',
            tickvals = [0, 24 * (31), 24 * (31 + 28), 24 * (31 + 28 + 31), 24 * (31 + 28 + 31 + 30), 24 * (31 + 28 + 31 + 30 + 31), 24 * (31 + 28 + 31 + 30 + 31 + 30), 24 * (31 + 28 + 31 + 30 + 31 + 30 + 31), 24 * (31 + 28 + 31 + 30 + 31 + 30 + 31 + 31), 24 * (31 + 28 + 31 + 30 + 31 + 30 + 31 + 31 + 30), 24 * (31 + 28 + 31 + 30 + 31 + 30 + 31 + 31 + 30 + 31), 24 * (31 + 28 + 31 + 30 + 31 + 30 + 31 + 31 + 30 + 31 + 30), 24 * (31 + 28 + 31 + 30 + 31 + 30 + 31 + 31 + 30 + 31 + 30 + 31)],
            ticktext = ["1.jan", "", "1.mar", "", "1.mai", "", "1.jul", "", "1.sep", "", "1.nov", "", "1.jan"]
            )
    )
    fig.update_xaxes(
    range=[0, 8760],
    title_text='',
    mirror=True,
    ticks="outside",
    showline=True,
    linecolor="black",
    gridcolor="lightgrey",
    )
    #-
    fig["data"][0]["showlegend"] = True
    fig.update_layout(
        margin=dict(l=50,r=50,b=10,t=10,pad=0),
        legend={'title_text':''},
        barmode="stack", 
        plot_bgcolor="white", paper_bgcolor="white",
        legend_traceorder="reversed",
        )


    fig.update_yaxes(
        range=[-100, 450],
        title_text='Effekt [MW]',
        mirror=True,
        ticks="outside",
        showline=True,
        linecolor="black",
        gridcolor="lightgrey",
    )

    return fig

def merge_plots(fig1, fig2):
    fig = go.Figure(data=fig1.data + fig2.data)
    fig.update_layout(
        legend=dict(yanchor="top", y=0.98, xanchor="left", x=0.01, bgcolor="rgba(0,0,0,0)"),
        xaxis = dict(
            tickmode = 'array',
            tickvals = [0, 24 * (31), 24 * (31 + 28), 24 * (31 + 28 + 31), 24 * (31 + 28 + 31 + 30), 24 * (31 + 28 + 31 + 30 + 31), 24 * (31 + 28 + 31 + 30 + 31 + 30), 24 * (31 + 28 + 31 + 30 + 31 + 30 + 31), 24 * (31 + 28 + 31 + 30 + 31 + 30 + 31 + 31), 24 * (31 + 28 + 31 + 30 + 31 + 30 + 31 + 31 + 30), 24 * (31 + 28 + 31 + 30 + 31 + 30 + 31 + 31 + 30 + 31), 24 * (31 + 28 + 31 + 30 + 31 + 30 + 31 + 31 + 30 + 31 + 30), 24 * (31 + 28 + 31 + 30 + 31 + 30 + 31 + 31 + 30 + 31 + 30 + 31)],
            ticktext = ["1.jan", "", "1.mar", "", "1.mai", "", "1.jul", "", "1.sep", "", "1.nov", "", "1.jan"]
            )
    )
    fig.update_xaxes(
    range=[0, 8760],
    title_text='',
    mirror=True,
    ticks="outside",
    showline=True,
    linecolor="black",
    gridcolor="lightgrey",
    )
    #-
    fig["data"][0]["showlegend"] = True
    fig.update_layout(
        margin=dict(l=50,r=50,b=10,t=10,pad=0),
        legend={'title_text':''},
        barmode="stack", 
        plot_bgcolor="white", paper_bgcolor="white",
        legend_traceorder="reversed",
        )


    fig.update_yaxes(
        range=[0, 600],
        title_text='Effekt [MW]',
        mirror=True,
        ticks="outside",
        showline=True,
        linecolor="black",
        gridcolor="lightgrey",
    )

    return fig

def rename_keys(dictionary, key_mapping):
    new_dictionary = {}
    for old_key, new_key in key_mapping.items():
        if old_key in dictionary:
            new_dictionary[new_key] = dictionary[old_key]
        else:
            new_dictionary[new_key] = None  # Set to None if old key not found
    return new_dictionary

def plot_energy_dict(energy_dict):
#    COLUMN_NAMES = {
#        "V" : "Luft luft varmepumpe",
#        "S" : "Solceller", 
#        "F" : "Fjernvarme",
#        "O" : "Oppgradert byggestandard",
#        "G" : "Bergvarme",
#    }
    letters = '_'
    df = pd.DataFrame(list(energy_dict.items()), columns=['Category', 'Value'])

    # Split the 'Value' column based on the provided letters
    df_splitted = df['Value'].str.split(f'[{letters}]', expand=True)
    
    for j in range(0, 10):
        new_column_names = [f'{df_splitted.iloc[j, i]}' for i in range(len(df_splitted.columns))]
        if new_column_names != None:
            break
    df_splitted.columns = new_column_names
    st.write(df_splitted)

    #for i in range(0, len(df_splitted.columns)):
    #    new_column_name = str(df_splitted.iloc[i, 0])
    #    df_splitted.columns[i] = [new_column_name]
    #    st.write(df_splitted)


    # Convert the split values to numeric (excluding None)
    #numeric_values = split_values.applymap(lambda x: float(x) if x is not None else None)

    # Create columns for each letter component
#    for i, letter in enumerate(letters):
#        df[f'Letter_{i + 1}'] = numeric_values[i]

    # Create a stacked bar chart using Plotly Express
#    fig = px.bar(df, x='Category', y=df.columns[3:], title='Percentage Breakdown',
#                 labels={'value': 'Percentage'}, barmode='stack')


def show_metrics(df, color_sequence, sorting = "energi"):

    if sorting == "energi":
        max_values = df.sum()
    else:
        max_values = df.max()
    column_max_dict = dict(max_values)
    sorted_columns = ['Referansesituasjon'] + [col for col, _ in sorted(column_max_dict.items(), key=lambda x: x[1], reverse=True) if col != 'Referansesituasjon']
    df = df[sorted_columns]
    options = df.columns
    reference_max = np.max(df["Referansesituasjon"])
    reference_sum = np.sum(df["Referansesituasjon"]) / 1000
    for i in range(0, len(options)):

        series = df[options[i]]
        max_value = rounding_to_int(np.max(series))
        sum_value = rounding_to_int(np.sum(series)/1000)
        max_value_reduction = int(((reference_max - max_value)/reference_max) * 100)
        sum_value_reduction = int(((reference_sum - sum_value)/reference_sum) * 100)
        with st.container():
            st.subheader(f"{df.columns[i]}")
            column_1, column_2 = st.columns(2)
            delta_color_1 = "inverse"
            delta_1 = f"{-max_value_reduction} %"
            delta_color_2 = "inverse"
            delta_2 = f"{-sum_value_reduction} %"
            if max_value_reduction == 0:
                delta_color_1 = "off"
                delta_1 = "Ingen reduksjon"
            if sum_value_reduction == 0:
                delta_color_2 = "off"
                delta_2 = "Ingen reduksjon"

            with column_1:
                st.metric(f"Maksimal kjøpt effekt fra nettet", value = f"{max_value:,} MW".replace(",", " "), delta = delta_1, delta_color=delta_color_1)
            with column_2:
                st.metric(f"Kjøpt energi fra nettet", value = f"{sum_value:,} GWH/år".replace(",", " "), delta = delta_2, delta_color=delta_color_2)
            #--
            #st.write(df)
            df_option = df[df.columns[i]].to_frame()
            with st.expander("Plot og data"):
                with chart_container(df_option, tabs = ["Årlig energibehov", "Se data", "Eksporter data"], export_formats=["CSV"]):
                    fig1 = plot_dataframe(df = df_option, color_sequence = color_sequence[i], sorting = False)
                    fig2 = plot_dataframe_moving_average(df = df_option, window_size = 100)
                    fig3 = merge_plots(fig1, fig2)
                    st.plotly_chart(fig3, use_container_width = True, config = {'displayModeBar': False})
                    #st.plotly_chart(fig1, use_container_width = True, config = {'displayModeBar': False})
                    #st.plotly_chart(fig2, use_container_width = True, config = {'displayModeBar': False})
            #st.markdown("---")

def main():
    st.set_page_config(
    page_title="Nedre Glomma",
    page_icon="📈",
    layout="centered")

    with open("app.css") as f:
        st.markdown("<style>{}</style>".format(f.read()), unsafe_allow_html=True)

    st.title("Varighetskurver for hele området")
    
    df = csv_to_df(folder_path = "data")
#    df = select_scenario(df)
    #color_sequence = px.colors.qualitative.Dark2
    color_sequence = [
    "#c76900", #bergvarme
    "#48a23f", #bergvarmesolfjernvarme
    "#1d3c34", #fjernvarme
    "#b7dc8f", #fremtidssituasjon
    "#2F528F", #luftluft
    "#3Bf81C", #merlokalproduksjon
    "#AfB9AB", #nåsituasjon
    "#254275", #oppgradert
    "#767171", #referansesituasjon
    "#ffc358", #solceller
]

    with chart_container(df, tabs = ["Varighetskurver", "Se data", "Eksporter data"], export_formats=["CSV"]):
        st.info("Skru av og på varighetskurvene i tegnforklaringen for å isolere ulike scenarier.")
        fig = plot_dataframe(df = df, color_sequence = color_sequence, sorting = True)
        st.plotly_chart(fig, use_container_width = True, config = {'displayModeBar': False})

    #--
    st.title("Glidende gjennomsnitt")
    selected_window_size = st.slider("Periode (uker)", min_value = 1, value = 2, max_value=3, step = 1) * 168
    with chart_container(df, tabs = ["Årlig energibehov", "Se data", "Eksporter data"], export_formats=["CSV"]):
        fig1 = plot_dataframe_moving_average(df = df, color_sequence = color_sequence, window_size = selected_window_size)
        st.plotly_chart(fig1, use_container_width = True, config = {'displayModeBar': False})
    
    #--
    st.title("Scenarier")
    #expansion_state = st.toggle("Vis plot", value = False)
    #expansion_state = True
    #if expansion_state:
        #st.experimental_rerun()
    tab1, tab2 = st.tabs(["**Effekt**sortering (høyeste til laveste)", "**Energi**sortering (høyeste til laveste)"])
    with tab1:
        show_metrics(df, color_sequence, sorting = "effekt")
    with tab2:
        show_metrics(df, color_sequence, sorting = "energi")

    st.title("Scenariobygger")
    energy_dicts_of_dicts, scenario_names = read_scenario_file_excel(file = "scenarier.xlsx")


    key_mapping = {
    'A': 'Hus',
    'B': 'Leilighet',
    'C': 'Kontor',
    'D': 'Butikk',
    'E': 'Hotell',
    'F': 'Barnehage',
    'G': 'Skole',
    'H': 'Universitet',
    'I': 'Kultur',
    'J': 'Sykehjem',
    'L': 'Andre',
    }
    area_string = "ABC"
    for i in range(0, len(energy_dicts_of_dicts)):
        scenario_name = scenario_names[i]
        energy_dicts = energy_dicts_of_dicts[i]
        for j in range(0, len(energy_dicts)):
            area = area_string[j]
            energy_dict = energy_dicts[area]
            #--
            if "Andre.1" in energy_dict:
                del energy_dict["Andre.1"]
            energy_dict = rename_keys(energy_dict, key_mapping)
            #--
            if area == "A":
                energy_area = "Fjernvarmeområde"
            elif area == "B":
                energy_area = "Tynt løsmassedekke"
            elif area == "C":
                energy_area = "Tykt løsmassedekke"
            
            st.markdown("---")
            st.write(scenario_name)
            st.write(energy_area)
            plot_energy_dict(energy_dict)



    

    

if __name__ == '__main__':
    main()