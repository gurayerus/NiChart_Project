import os

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st
import utils.utils_st as utilst


def calc_subject_centiles(df_subj: pd.DataFrame, df_cent: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate subject specific centile values
    """

    # Filter centiles to subject's age
    tmp_ind = (df_cent.Age - df_subj.Age[0]).abs().idxmin()
    sel_age = df_cent.loc[tmp_ind, "Age"]
    df_cent_sel = df_cent[df_cent.Age == sel_age]

    # Find ROIs in subj data that are included in the centiles file
    sel_vars = df_subj.columns[df_subj.columns.isin(df_cent_sel.ROI.unique())].tolist()
    df_cent_sel = df_cent_sel[df_cent_sel.ROI.isin(sel_vars)].drop(
        ["ROI", "Age"], axis=1
    )

    cent = df_cent_sel.columns.str.replace("centile_", "").astype(int).values
    vals_cent = df_cent_sel.values
    vals_subj = df_subj.loc[0, sel_vars]

    cent_subj = np.zeros(vals_subj.shape[0])
    for i, sval in enumerate(vals_subj):
        # Find nearest x values
        ind1 = np.where(vals_subj[i] < vals_cent[i, :])[0][0] - 1
        ind2 = ind1 + 1

        print(ind1)

        # Calculate slope
        slope = (cent[ind2] - cent[ind1]) / (vals_cent[i, ind2] - vals_cent[i, ind1])

        # Estimate subj centile
        cent_subj[i] = cent[ind1] + slope * (vals_subj[i] - vals_cent[i, ind1])

    df_out = pd.DataFrame(dict(ROI=sel_vars, Centiles=cent_subj))
    return df_out


def display_plot(df: pd.DataFrame, sel_mrid: str) -> None:
    """
    Displays the plot with the given mrid
    """

    # Data columns
    dtmp = ["TotalBrain", "GM", "WM", "Ventricles"]
    vtmp = df[df.MRID == sel_mrid][dtmp].iloc[0].values.tolist()

    # Main container for the plot
    plot_container = st.container(border=True)
    with plot_container:
        # fig = px.bar(df, x='Fruit', y='Quantity', title='Fruit Consumption')
        fig = px.bar(x=dtmp, y=vtmp, title="Data Values")
        st.plotly_chart(fig)


# Panel for output (dataset name + out_dir)
utilst.util_panel_workingdir(st.session_state.app_type)

# Panel for selecting input data
with st.expander(":material/upload: Select or upload input data", expanded=False):

    # Set default path for the plot csv
    if os.path.exists(st.session_state.paths["csv_mlscores"]):
        st.session_state.paths["csv_plot"] = st.session_state.paths["csv_mlscores"]
    elif os.path.exists(st.session_state.paths["csv_dlmuse"]):
        st.session_state.paths["csv_plot"] = st.session_state.paths["csv_dlmuse"]

    # Input csv
    helpmsg = "Input csv file with DLMUSE ROI volumes.\n\nChoose the file by typing it into the text field or using the file browser to browse and select it"
    csv_plot, csv_path = utilst.user_input_filename(
        "Select file",
        "btn_input_seg",
        "DLMUSE ROI file",
        st.session_state.paths["last_in_dir"],
        st.session_state.paths["csv_plot"],
        helpmsg,
    )
    if os.path.exists(csv_plot):
        st.session_state.paths["csv_plot"] = csv_plot
        st.session_state.paths["last_in_dir"] = csv_path

        df = pd.read_csv(st.session_state.paths["csv_plot"])
        list_mrid = df.MRID.tolist()

        sel_mrid = st.selectbox("MRID", list_mrid, key="selbox_mrid", index=None)

        if sel_mrid is not None:
            display_plot(df, sel_mrid)
