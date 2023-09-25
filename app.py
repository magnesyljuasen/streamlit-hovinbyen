import streamlit as st
import os
import pandas as pd
from plotly import graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import datetime
import plotly.express as px
from streamlit_extras.chart_container import chart_container
from PIL import Image

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
        fig.update_layout(
            legend=dict(bgcolor="rgba(0,0,0,0)"),
            )

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

def string_to_number(x):
    if x == None:
        return 0
    elif x == "00":
        return 0
    elif len(x) == 2 and x != None:
        return int(x[1:2])
    elif len(x) == 3 and x != None:
        return int(x[1:3])
    elif len(x) == 4 and x != None: # 100
        return int(x[1:4])
    
def explanation_text_scenario(scenario_name):
    if scenario_name == "Referansesituasjon":
        st.write(""" Referansesituasjonen definerer nullsituasjonen for området og er den de andre scenariene sammenlignes med. """)
        st.write(""" Her er det simulert energiflyt for: """)
        st.write(" 1) Alle bygg som er koblet på fjernvarme i dag (untatt industri).")
        st.write(" 2) Alle bygg er som har energibrønn på tomten (sjekket mot nasjonal grunnvannsdatabase GRANADA).")
    if scenario_name == "LuftLuftVarmepumper":
        st.write(""" Dette scenariet definerer en situasjon der alle bygg som ikke hadde bergvarme/fjernvarme i referansesituasjonen får luft luft varmepumper.""")
        st.write(""" Her er det simulert energiflyt for: """)
        st.write(" 1) Alle bygg som er koblet på fjernvarme i dag (untatt industri).")
        st.write(" 2) Alle bygg er som har energibrønn på tomten (sjekket mot nasjonal grunnvannsdatabase GRANADA).")
        st.write(" 3) Resten av byggene har luft luft varmepumpe")
    if scenario_name == "Nåsituasjon":
        st.write(""" Nåsituasjonen er et forsøk på å definere området slik det er i dag.""")
        st.write(""" Her er det simulert energiflyt for: """)
        st.write(" 1) Alle bygg som er koblet på fjernvarme i dag (untatt industri).")
        st.write(" 2) Alle bygg er som har energibrønn på tomten (sjekket mot nasjonal grunnvannsdatabase GRANADA).")
        st.write(" 3) 60% av byggene har luft luft varmepumpe og 10% av byggene har solceller.")
    if scenario_name == "Solceller":
        st.write(""" Dette scenariet definerer en situasjon der alle bygg som ikke hadde bergvarme/fjernvarme i referansesituasjonen får solceller.""")
        st.write(""" Her er det simulert energiflyt for: """)
        st.write(" 1) Alle bygg som er koblet på fjernvarme i dag (untatt industri).")
        st.write(" 2) Alle bygg er som har energibrønn på tomten (sjekket mot nasjonal grunnvannsdatabase GRANADA).")
        st.write(" 3) Resten av byggene har solceller.")
    if scenario_name == "Fjernvarme":
        st.write(""" Dette scenariet definerer en situasjon der alle bygg som **ligger innenfor konsensjonsområdene for fjernvarme og som ikke er eneboliger** får fjernvarme.""")
        st.write(""" Her er det simulert energiflyt for: """)
        st.write(" 1) Alle bygg som er koblet på fjernvarme i dag (untatt industri).")
        st.write(" 2) Alle bygg er som har energibrønn på tomten (sjekket mot nasjonal grunnvannsdatabase GRANADA).")
        st.write(" 3) Alle byggene i fjernvarmeområdene som ikke er eneboliger får fjernvarme.")
    if scenario_name == "Fremtidssituasjon2030":
        st.write(""" Scenariet definerer en antatt situasjon for år 2030 med en **moderat økning** når det gjelder bergvarme, fjernvarme, solceller og oppgradering av bygningsmassen.""")
        st.write(""" Her er det simulert energiflyt for: """)
        st.write(" 1) Alle bygg som er koblet på fjernvarme i dag (untatt industri).")
        st.write(" 2) Alle bygg er som har energibrønn på tomten (sjekket mot nasjonal grunnvannsdatabase GRANADA).")
        st.write(" 3) 30% av bygg får solceller, fjernvarme, bergvarme og 30% av byggene untatt eneboligene oppgraderes.")
        st.write(" 4) 10% av eneboliger oppgraderes.")
        st.write(" 5) Mer fjernvarme gjelder kun i fjernvarmeområdet for bygninger som ikke er eneboliger, og det er mindre bergvarme i områdene med tykt løsmassedekke.""")
        
    if scenario_name == "MerLokalproduksjon":
        st.write(""" Scenariet definerer en situasjon med en **større økning** når det gjelder bergvarme, fjernvarme og solceller""")
        st.write(""" Her er det simulert energiflyt for: """)
        st.write(" 1) Alle bygg som er koblet på fjernvarme i dag (untatt industri).")
        st.write(" 2) Alle bygg er som har energibrønn på tomten (sjekket mot nasjonal grunnvannsdatabase GRANADA).")
        st.write(" 3) 50% av bygg får solceller, fjernvarme og bergvarme. ")
        st.write("4) Mer fjernvarme gjelder kun i fjernvarmeområdet for bygninger som ikke er eneboliger, og det er mindre bergvarme i områdene med tykt løsmassedekke.")
    if scenario_name == "OppgradertBygningsmasse":
        st.write(""" Dette scenariet definerer en situasjon der alle bygg som har laveste byggestandard (eldre bygg) blir oppgradert til TEK10/TEK17-standard.""")
        st.write(""" Her er det simulert energiflyt for: """)
        st.write(" 1) Alle bygg som er koblet på fjernvarme i dag (untatt industri).")
        st.write(" 2) Alle bygg er som har energibrønn på tomten (sjekket mot nasjonal grunnvannsdatabase GRANADA).")
        st.write(" 3) Alle eldre bygg oppgraderes til TEK10/TEK17-standard.")
    if scenario_name == "Bergvarme":
        st.write(""" Dette scenariet definerer en situasjon der alle bygg som ikke hadde bergvarme/fjernvarme i referansesituasjonen får bergvarme.""")
        st.write(""" Her er det simulert energiflyt for: """)
        st.write(" 1) Alle bygg som er koblet på fjernvarme i dag (untatt industri).")
        st.write(" 2) Alle bygg er som har energibrønn på tomten (sjekket mot nasjonal grunnvannsdatabase GRANADA).")
        st.write(" 3) Alle bygg som ligger i områder med tynt løsmassedekke og 50% av byggene i områder med tykt løsmassedekke får bergvarme. ")
        st.write(" 4) Alle eneboligene som ligger i konsesjonsområdene for fjernvarme for også bergvarme.")
    if scenario_name == "BergvarmeSolFjernvarme":
        st.write(""" Dette scenariet definerer en situasjon med en **veldig stor økning** når det gjelder bergvarme og solceller""")
        st.write(""" Her er det simulert energiflyt for: """)
        st.write(" 1) Alle bygg som er koblet på fjernvarme i dag (untatt industri).")
        st.write(" 2) Alle bygg er som har energibrønn på tomten (sjekket mot nasjonal grunnvannsdatabase GRANADA).")
        st.write(" 3) Alle bygg som ligger i områder med tynt løsmassedekke og 50% av byggene i områder med tykt løsmassedekke får bergvarme. ")
        st.write(" 4) Alle eneboligene som ligger i konsesjonsområdene for fjernvarme får også bergvarme. """)
        st.write(" 5) Alle bygg får solceller.""")




def plot_energy_dict(energy_dict):
    key_mapping = {
    'Hus',
    'Leilighet',
    'Kontor',
    'Butikk',
    'Hotell',
    'Barnehage',
    'Skole',
    'Universitet',
    'Kultur',
    'Sykehjem',
    'Andre',
    }
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
    df_splitted = df_splitted.applymap(string_to_number)
    df_splitted.index = key_mapping
    st.bar_chart(df_splitted)

def show_building_statistics():
    df2 = pd.read_csv("data/Referansesituasjon_filtered.csv")
    grouped_df = df2.groupby('BYGNINGSTYPE_NAVN').size().reset_index(name='COUNT')
    fig = px.bar(grouped_df, x='BYGNINGSTYPE_NAVN', y='COUNT')
    fig.update_layout(
    autosize=True,
    margin=dict(l=0,r=0,b=10,t=10,pad=0),
    yaxis_title="Antall bygg",
    xaxis_title="Bygningstyper",
    plot_bgcolor="white",
    legend=dict(yanchor="top", y=0.98, xanchor="left", x=0.01, bgcolor="rgba(0,0,0,0)"),
    )
    fig.update_xaxes(
        ticks="outside",
        linecolor="black",
        gridcolor="lightgrey",
    )
    fig.update_yaxes(
        range=[0, 30000],
        tickformat=",",
        ticks="outside",
        linecolor="black",
        gridcolor="lightgrey",
    )
    fig.update_layout(separators="* .*")
    st.plotly_chart(fig, use_container_width = True, config = {'displayModeBar': False})
    st.markdown("---")
    #-- pie
    pie_fig = px.pie(data_frame=grouped_df, names = 'BYGNINGSTYPE_NAVN', values = 'COUNT')
    # Customize the layout for the pie chart
    pie_fig.update_layout(
        autosize=True,
        margin=dict(l=0, r=0, b=10, t=10, pad=0),
        plot_bgcolor="white",
        #legend=dict(yanchor="top", y=0.98, xanchor="left", x=0.01, bgcolor="rgba(0,0,0,0)"),
    )
    pie_fig.update_traces(hoverinfo='label+percent+name', textinfo='none')
    #pie_fig.update(layout_title_text='Van Gogh: 5 Most Prominent Colors Shown Proportionally', layout_showlegend=False)

    # Assuming you are using Streamlit to display the chart
    st.plotly_chart(pie_fig, use_container_width=True, config={'displayModeBar': False})

def typewrite(text:str):
    with open("assets/codepen.css") as f:
        # The CSS from the codepen was stored in codepen.css
        css = f.read()

    with open("assets/codepen.js") as f:
        # The JS from the codepen was stored in codepen.js
        js = f.read()

    html = f"""
    <!DOCTYPE html>
    <head>
    <style>
        {css}
    </style>
    </head>
    <body>
        <p id="typewrite" data-content="">{text.upper()}</p>
        <script>
            {js}
        </script>
    </body>
    </html>
    """
    return html

def front_page():
    text = """Hvor mye, når og hvordan kan energieffektivisering og lokal energiproduksjon dempe presset på nettet for å bidra til raskere elektrifisering i området?"""
    typewrited = typewrite(text)
    with st.container():
        st.components.v1.html(typewrited, height=500, scrolling=False)
    c1, c2 = st.columns(2)
    with c1:
        image = Image.open('assets/AsplanViak_Logo_Sekund├ªrlogo_Skogsgr├©nn_RGB.png')
        st.image(image)
    with c2:
        image = Image.open('assets/Zero.png')
        st.image(image)

def show_temperature_series():
    df = pd.read_excel("assets/ns3031.xlsx")
    with chart_container(df, tabs = ["Graf", "Se data", "Eksporter data"], export_formats=["CSV"]):
        fig = px.line(df, x=df.index, y=df.columns)
        
        fig.update_traces(
            line=dict(
                width=0.5, 
                #color = color_sequence
                color = "blue"
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
            #range=[-400, 600],
            title_text='Utetemperatur [°C]',
            mirror=True,
            ticks="outside",
            showline=True,
            linecolor="black",
            gridcolor="lightgrey",
        )
        st.plotly_chart(fig, use_container_width = True, config = {'displayModeBar': False})


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
            name = df.columns[i]
            if name == "LuftLuftVarmepumper":
                name = "Luft-luft-varmepumper"
            elif name == "Fremtidssituasjon2030":
                name = "Mulig fremtidssituasjon 2030"
            elif name == "MerLokalproduksjon":
                name = "Mer lokalproduksjon"
            elif name == "OppgradertBygningsmasse":
                name = "Oppgradert bygningsmasse"
            elif name == "BergvarmeSolFjernvarme":
                name = "Bergvarme og sol"
            st.subheader(name)
            explanation_text_scenario(df.columns[i])
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
                st.metric(f"""1. Maksimalt behov for tilført el-effekt fra el-nettet""", value = f"{max_value:,} MW".replace(",", " "), delta = delta_1, delta_color=delta_color_1)
            with column_2:
                st.metric(f"""1. Behov for tilført el-energi fra el-nettet""", value = f"{sum_value:,} GWH/år".replace(",", " "), delta = delta_2, delta_color=delta_color_2)
            #--
            df1 = pd.read_csv(f"data/{df.columns[i]}_filtered.csv", low_memory = False)
            bergvarme_count = len(df1[df1['grunnvarme'] == True])
            fjernvarme_count = len(df1[df1['fjernvarme'] == True])
            luftluft_count = len(df1[df1['luft_luft_varmepumpe'] == True])
            solceller_count = len(df1[df1['solceller'] == True])
            oppgraderes_count = len(df1[df1['oppgraderes'] == True])
            totalt_count = len(df1)
            #--
            with st.expander("Antall bygg", expanded = False):
                df_bar = {
                'Type tiltak': [
                    'bergvarme',
                    'Fjernvarme',
                    'Luft-luft-varmepumpe',
                    'Solceller',
                    'Oppgradert bygningsmasse'
                ],
                'Antall bygg': [bergvarme_count, fjernvarme_count, luftluft_count, solceller_count, oppgraderes_count]
                }

                fig = px.bar(df_bar, x='Type tiltak', y='Antall bygg')
                fig.update_layout(
                autosize=True,
                margin=dict(l=0,r=0,b=10,t=10,pad=0),
                yaxis_title="Antall bygg med tiltak",
                plot_bgcolor="white",
                legend=dict(yanchor="top", y=0.98, xanchor="left", x=0.01, bgcolor="rgba(0,0,0,0)"),
                    )
                fig.update_xaxes(
                    ticks="outside",
                    linecolor="black",
                    gridcolor="lightgrey",
                )
                fig.update_yaxes(
                    range=[0, 52834],
                    tickformat=",",
                    ticks="outside",
                    linecolor="black",
                    gridcolor="lightgrey",
                )
                fig.update_layout(separators="* .*")
                st.plotly_chart(fig, use_container_width = True, config = {'displayModeBar': False})
            #--
            #st.write(df)
            df_option = df[df.columns[i]].to_frame()
            with st.expander("Plot og data", expanded = False):
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

    st.markdown("<h1 style='text-align: center;'>Systemsmart <br>Nedre Glomma 2.0</h1>", unsafe_allow_html=True)
    tab0_site, tab1_site, tab2_site, tab3_site = st.tabs(["Oppdraget", "Energiscenarier", "Bygningsstatistikk", "Varighetskurver og glidende gjennomsnitt"])
    with tab0_site:
        front_page()
    with tab3_site:
        st.info("Resultatene som vises her gjelder for alle bygg i området.", icon="ℹ️")
        st.write("**Varighetskurver for hele området**")
        df = csv_to_df(folder_path = "data")
    #   df = select_scenario(df)
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

        #with chart_container(df, tabs = ["Varighetskurver", "Se data", "Eksporter data"], export_formats=["CSV"]):
        fig = plot_dataframe(df = df, color_sequence = color_sequence, sorting = True)
        st.plotly_chart(fig, use_container_width = True, config = {'displayModeBar': False})
        with st.expander("Se data"):
            st.write(df)

        #--
        st.write("**Glidende gjennomsnitt**")
        #selected_window_size = st.slider("Periode (uker)", min_value = 1, value = 2, max_value=3, step = 1) * 168
        #with chart_container(df, tabs = ["Årlig energibehov", "Se data", "Eksporter data"], export_formats=["CSV"]):
        fig1 = plot_dataframe_moving_average(df = df, color_sequence = color_sequence, window_size = 168)
        st.plotly_chart(fig1, use_container_width = True, config = {'displayModeBar': False})
        with st.expander("Se data"):
            st.write(df)
        st.warning("Tips! Skru av og på kurvene i tegnforklaringen for å isolere ulike scenarier.", icon="ℹ️")
        
        #--
    with tab2_site:
        st.header("Bygningsstatistikk")
        st.write("""Det er totalt **52 834 bygg** i området som er tilgjengelige for energitiltak. 
                Garasjer, industri og andre bygningskategorier uten energibehov er filtrert bort.""")
        
        with st.expander("Vis bygningsstatistikk", expanded = True):
            show_building_statistics()
    
    with tab1_site:
        st.header("Energiscenarier")
        st.write("""Det er simulert 10 ulike scenarier som vises nedenfor. 
                Disse er preprossesert, **men fullt mulig å konfigurere og definere som man vil**. 
                Inndata til simuleringene er et excel-ark der man kan velge prosentsatser for ulike tiltak i ulike energiområder. """)
        
        st.write("Eksempler:")
        st.write(" - • At 50% av alle kontorbygninger innenfor fjernvarmeområdet skal få fjernvarme")
        st.write(" - • At 70% av alle eneboliger med tynt løsmassedekke skal ha bergvarme.")
        st.write(" - • At 30% av alle eneboliger skal ha solceller, 50% av de som er innenfor området med tynt løsmassedekke skal ha bergvarme og 20% av eneboligene får oppgradert byggestandard.")
        
        st.write("Det er altså mulig å velge enkelttiltak samt kombinasjoner for ulike bygg i ulike energiområder.")
        with st.expander("Forutsetninger for beregningene"):
            st.write("**Utetemperatur**")
            st.write("Utetemperatur som ligger til grunn er hentet fra NS3031, og vist i figuren under. ")
            show_temperature_series()
            st.write("**Industribygg**")
            st.write("""Industribygg er ikke tatt med i beregningene. Det er 281 + 119 = 400 adresser som er påkoblet fjernvarme. 
                     138 av disse er "industribygg", og fjernes fra simuleringen, derav 262 som blir simulert.""")
        st.info("Vi ønsker innspill på hvilke scenarier som er lure å simulere.", icon="ℹ️")
        #expansion_state = st.toggle("Vis plot", value = False)
        #expansion_state = True
        #if expansion_state:
            #st.experimental_rerun()
        
        tab1, tab2 = st.tabs(["**Effekt**sortering (høyeste til laveste)", "**Energi**sortering (høyeste til laveste)"])
        with tab1:
            show_metrics(df, color_sequence, sorting = "effekt")
        with tab2:
            show_metrics(df, color_sequence, sorting = "energi")

   
if __name__ == '__main__':
    main()