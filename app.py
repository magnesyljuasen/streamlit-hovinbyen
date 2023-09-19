import streamlit as st
import os
import pandas as pd
from plotly import graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import datetime
import plotly.express as px

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
    if sorting == True:
        df = sort_columns_high_to_low(df)
        fig = px.line(df, x=df.index, y=df.columns, color_discrete_sequence=color_sequence)
        fig.update_layout(legend=dict(bgcolor="rgba(0,0,0,0)"))
        
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
                color = color_sequence
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
    fig["data"][0]["showlegend"] = True
    fig.update_layout(
        legend={'title_text':''},
        barmode="stack", margin=dict(l=20, r=20, t=20, b=20),
        plot_bgcolor="white", paper_bgcolor="white",
        legend_traceorder="reversed",
        )
    
    
    fig.update_yaxes(
        range=[0, 70],
        title_text='Effekt [MW]',
        mirror=True,
        ticks="outside",
        showline=True,
        linecolor="black",
        gridcolor="lightgrey",
    )
    # Display the plot
    st.plotly_chart(fig, use_container_width = True, config = {'displayModeBar': False})

def show_metrics(df, color_sequence):
    c1, c2 = st.columns(2)
    options = df.columns
    reference_max = np.max(df["Referansesituasjon"])
    reference_sum = np.sum(df["Referansesituasjon"]) / 1000
    for i in range(0, len(options)):
        if (i % 2):
            col = c1
        else:
            col = c2
        with col:
            series = df[options[i]]
            max_value = rounding_to_int(np.max(series))
            sum_value = rounding_to_int(np.sum(series)/1000)
            max_value_reduction = int(((reference_max - max_value)/reference_max) * 100)
            sum_value_reduction = int(((reference_sum - sum_value)/reference_sum) * 100)
            with st.container():
                st.header(f"{df.columns[i]}")
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
                    st.metric(f"Maksimal kjøpt effekt fra nettet", value = f"{max_value} MW", delta = delta_1, delta_color=delta_color_1)
                with column_2:
                    st.metric(f"Kjøpt energi fra nettet", value = f"{sum_value} GWH/år", delta = delta_2, delta_color=delta_color_2)
                #--
                #st.write(df)
                df_option = df[df.columns[i]].to_frame()
                plot_dataframe(df = df_option, color_sequence = color_sequence[i], sorting = False)
                with st.expander("Se data"):
                    st.write(df_option)
                st.markdown("---")

def main():
    st.set_page_config(
    page_title="Nedre Glomma",
    page_icon="📈",
    layout="wide")

    with open("app.css") as f:
        st.markdown("<style>{}</style>".format(f.read()), unsafe_allow_html=True)
    st.title("Overordnede resultater")
    df = csv_to_df(folder_path = "data")
    df = select_scenario(df)
    #color_sequence = px.colors.qualitative.Dark2
    color_sequence = [
    "#1d3c34",
    "#48a23f",
    "#FFC358",
    "#ff5733",
    "#33FF57",
    "#5733FF",
    "#FF33E6",
    "#33E6FF",
    "#FF5733",
    "#FF33E6",
    "#5733FF",
    "#33E6FF",
]


    plot_dataframe(df = df, color_sequence = color_sequence, sorting = True)
    with st.expander("Se data"):
        st.write(df)
    #--
    show_metrics(df, color_sequence)

if __name__ == '__main__':
    main()