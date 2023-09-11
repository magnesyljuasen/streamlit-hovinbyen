import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d
import time
import streamlit as st
import os
import pandas as pd
from plotly import graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import datetime
import plotly.express as px

def plot_dataframe(df):
    fig = px.line(df, x=df.index, y=df.columns)
    fig["data"][0]["showlegend"] = True
    fig.update_layout(
        legend={'title_text':''},
        barmode="stack", margin=dict(l=20, r=20, t=20, b=20),
        plot_bgcolor="white", paper_bgcolor="white",
        legend_traceorder="reversed"
        )
    fig.update_xaxes(
        #range=[0, 8760],
        title_text='Utetemperatur [grader]',
        mirror=True,
        ticks="outside",
        showline=True,
        linecolor="black",
        gridcolor="lightgrey",
        )
    
    fig.update_yaxes(
        title_text='Effekt [kW]',
        mirror=True,
        ticks="outside",
        showline=True,
        linecolor="black",
        gridcolor="lightgrey",
    )
    # Display the plot
    st.plotly_chart(fig, use_container_width = True)


class HeatPumpSize:
    def __init__(self):
        pass

    def __preprocess_air_source_heat_pump(self):
        # Load data from Excel file
        data = pd.read_excel('utetemperatur.xlsx')
        self.TEMPERATURE_ARRAY = np.array(data["temp"])

        P_NOMINAL = 5  # Nominell effekt på VP
        COP_NOMINAL = 5  # Nominell COP

        # SN- NSPEK 3031:2023 - tabell K.13
        temperature_datapoints = [-15, 2, 7]

        P_3031 = np.array([
            [0.46, 0.72, 1],
            [0.23, 0.36, 0.5],
            [0.09, 0.14, 0.2]
            ])

        COP_3031 = np.array([plot_dataframe
            [0.44, 0.53, 0.64],
            [0.61, 0.82, 0.9],
            [0.55, 0.68, 0.82]
            ])

        P_3031_list = []
        COP_3031_list = []
        for i in range(0, len(temperature_datapoints)):
            P_3031_list.append(np.polyfit(x = temperature_datapoints, y = P_3031[i], deg = 1))
            COP_3031_list.append(np.polyfit(x = temperature_datapoints, y = COP_3031[i], deg = 1))

        self.P_HP_DICT = []
        self.COP_HP_DICT = []
        self.INTERPOLATE_HP_DICT = []
        for index, outdoor_temperature in enumerate(self.TEMPERATURE_ARRAY):
            p_hp_list = np.array([np.polyval(P_3031_list[0], outdoor_temperature), np.polyval(P_3031_list[1], outdoor_temperature), np.polyval(P_3031_list[2], outdoor_temperature)]) * P_NOMINAL
            cop_hp_list = np.array([np.polyval(COP_3031_list[0], outdoor_temperature), np.polyval(COP_3031_list[1], outdoor_temperature), np.polyval(COP_3031_list[2], outdoor_temperature)]) * COP_NOMINAL
            interpolate_hp_list = np.polyfit(x = p_hp_list, y = cop_hp_list, deg = 0)[0]
            #--
            self.P_HP_DICT.append(p_hp_list)
            self.COP_HP_DICT.append(cop_hp_list)
            self.INTERPOLATE_HP_DICT.append(interpolate_hp_list)

    def __air_source_heat_pump_calculation(self):
        varmebehov = row[self.THERMAL_DEMAND]
        varmepumpe = []
        cop = []
        for i in range(0, len(self.TEMPERATURE_ARRAY)):
            effekt = varmebehov[i]
            outdoor_temperature = self.TEMPERATURE_ARRAY[i]
            if outdoor_temperature < -15:
                cop.append(1)
                varmepumpe.append(0)
            else:
                p_hp_list = self.P_HP_DICT[i]
                cop_hp_list = self.COP_HP_DICT[i]
                if effekt >= p_hp_list[0]:
                    varmepumpe.append(p_hp_list[0])
                    cop.append(cop_hp_list[0])
                elif effekt <= p_hp_list[2]:
                    varmepumpe.append(effekt)
                    cop.append(cop_hp_list[2])
                else:
                    varmepumpe.append(effekt)
                    cop.append(self.INTERPOLATE_HP_DICT[i])

        varmebehov = np.array(varmebehov)
        cop = np.array(cop)
        varmepumpe = np.array(varmepumpe)
        air_list = varmepumpe - varmepumpe / cop
        compressor_list = varmepumpe - air_list
        peak_list = demand_list - varmepumpe

        reference_array = np.array(outdoor_temperature_list)
        sorted_indices = np.argsort(reference_array)


df = pd.DataFrame({
    #"Utetemperatur" : outdoor_temperature_list[sorted_indices],
    "Behov" : demand_list[sorted_indices],
    "Levert fra luft" : air_list[sorted_indices],
    #"Kompressor" : compressor_list[sorted_indices]
})
#df = df.set_index("Utetemperatur")
st.write(df)

plot_dataframe(df)

