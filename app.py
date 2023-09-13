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

    selected_scenarios = st.multiselect("Velg scenarier", options = options, default = default_options)
    if len(selected_scenarios) == 0:
        st.stop()
    return df[selected_scenarios]

def sort_columns_high_to_low(df):
    sorted_df = df.apply(lambda col: col.sort_values(ascending=False).reset_index(drop=True))
    return sorted_df

def rounding_to_int(number):
    return int(round(number, 0))

def plot_dataframe(df, sorting = True):
    if sorting == True:
        df = sort_columns_high_to_low(df)
    fig = px.line(df, x=df.index, y=df.columns)
    fig["data"][0]["showlegend"] = True
    fig.update_layout(
        legend={'title_text':''},
        barmode="stack", margin=dict(l=20, r=20, t=20, b=20),
        plot_bgcolor="white", paper_bgcolor="white",
        legend_traceorder="reversed"
        )
    fig.update_xaxes(
        range=[0, 8760],
        title_text='Varighet [timer]',
        mirror=True,
        ticks="outside",
        showline=True,
        linecolor="black",
        gridcolor="lightgrey",
        )
    
    fig.update_yaxes(
        title_text='Effekt [MW]',
        mirror=True,
        ticks="outside",
        showline=True,
        linecolor="black",
        gridcolor="lightgrey",
    )
    # Display the plot
    st.plotly_chart(fig, use_container_width = True)

def show_metrics(df):
    options = df.columns
    for i in range(0, len(options)):
        series = df[options[i]]
        max_value = rounding_to_int(np.max(series))
        sum_value = rounding_to_int(np.sum(series)/1000)
        st.header(f"{df.columns[i]}")
        column_1, column_2 = st.columns(2)
        with column_1:
            st.metric(f"Maksimal kjøpt effekt fra nettet", value = f"{max_value} MW")
        with column_2:
            st.metric(f"Kjøpt energi fra nettet", value = f"{sum_value} GWH/år")
        st.markdown("---")

def main():
    st.set_page_config(
    page_title="Nedre Glomma",
    page_icon="📈")

    with open("app.css") as f:
        st.markdown("<style>{}</style>".format(f.read()), unsafe_allow_html=True)
    with st.expander("Se varighetskurve"):
        st.title("Resultater Nedre Glomma")
        df = csv_to_df(folder_path = "data")
        df = select_scenario(df)
        plot_dataframe(df, sorting = True)
        plot_dataframe(df, sorting = False)
        show_metrics(df)

if __name__ == '__main__':
    main()