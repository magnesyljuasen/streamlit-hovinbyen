st.title("Resultater - Nedre Glomma")
    df1 = read_csv("data/Bergvarme_filtered.csv")
    df2 = read_csv("data/Fjernvarme_filtered.csv")
    df3 = read_csv("data/Referanse_filtered.csv")

    df1_energy, df1_effect = get_columns(df1)
    df2_energy, df2_effect = get_columns(df2)
    df3_energy, df3_effect = get_columns(df3)
    
    tab1, tab2, tab3 = st.tabs(["Scenario 1", "Scenario 2", "Scenario 3"])
    with tab1:
        st.header("Scenario 1")
        c1, c2 = st.columns(2)
        with c1:
            st.metric("Maksimal effekt (kW)", value = f"{int(np.sum(df1_effect))} MW")
            df = df1.groupby('Byggtype_profet')['_nettutveksling_vintereffekt'].sum()
            df = df.reset_index()
            plotly_plot_effect(df)
        with c2:
            st.metric("Energi (kWh/år)", value = f"{int(np.sum(df1_energy))} GWh")
            df = df3.groupby('Byggtype_profet')['_nettutveksling_energi'].sum()
            df = df.reset_index()
            plotly_plot_energy(df)
    with tab2:
        st.header("Scenario 2")
        c1, c2 = st.columns(2)
        with c1:
            start = int(np.sum(df1_effect))
            final = int(np.sum(df2_effect))
            st.metric("Maksimal effekt (kW)", value = f"{np.sum(df2_effect)} MW", delta=f"-{round(((start - final)/start),2) * 100} %", delta_color="inverse")
            df = df2.groupby('Byggtype_profet')['_nettutveksling_vintereffekt'].sum()
            df = df.reset_index()
            plotly_plot_effect(df)

        with c2:
            start = int(np.sum(df1_energy))
            final = int(np.sum(df3_energy))
            st.metric("Energi (kWh/år)", value = f"{int(np.sum(df2_energy))} GWh", delta=f"-{round(((start - final)/start),2) * 100} %", delta_color = "inverse")
            df = df2.groupby('Byggtype_profet')['_nettutveksling_energi'].sum()
            df = df.reset_index()
            plotly_plot_energy(df)
    with tab3:
        st.header("Scenario 3")
        c1, c2 = st.columns(2)
        with c1:
            start = int(np.sum(df1_effect))
            final = int(np.sum(df3_effect))
            st.metric("Maksimal effekt (kW)", value = f"{int(np.sum(df3_effect))} MW", delta=f"-{round(((start - final)/start),2) * 100} %", delta_color = "inverse")
            df = df3.groupby('Byggtype_profet')['_nettutveksling_vintereffekt'].sum()
            df = df.reset_index()
            plotly_plot_effect(df)
        with c2:
            start = int(np.sum(df1_energy))
            final = int(np.sum(df3_energy))
            st.metric("Energi (kWh/år)", value = f"{int(np.sum(df3_energy))} GWh", delta=f"-{round(((start - final)/start),2) * 100} %", delta_color = "inverse")
            df = df3.groupby('Byggtype_profet')['_nettutveksling_energi'].sum()
            df = df.reset_index()
            plotly_plot_energy(df)