import os
import sys

import pandas as pd
import streamlit as st
import utils.utils_cloud as utilcloud
import utils.utils_io as utilio
import utils.utils_pages as utilpg
import utils.utils_panels as utilpn
import utils.utils_st as utilst

run_dir = os.path.join(st.session_state.paths["root"], "src", "workflows", "w_sMRI")
sys.path.append(run_dir)
import w_mlscores as w_mlscores

# Page config should be called for each page
utilpg.config_page()
utilpg.show_menu()


def panel_indata() -> None:
    panel_inrois()
    panel_indemog()


def panel_inrois() -> None:
    """
    Panel for uploading input rois
    """
    with st.container(border=True):
        if st.session_state.app_type == "cloud":
            utilst.util_upload_file(
                st.session_state.paths["dlmuse_csv"],
                "DLMUSE csv",
                "uploaded_dlmuse_file",
                False,
                "visible",
            )

        else:  # st.session_state.app_type == 'desktop'
            utilst.util_select_file(
                "selected_dlmuse_file",
                "DLMUSE csv",
                st.session_state.paths["dlmuse_csv"],
                st.session_state.paths["file_search_dir"],
            )

        if os.path.exists(st.session_state.paths["dlmuse_csv"]):
            p_dlmuse = st.session_state.paths["dlmuse_csv"]
            st.session_state.flags["dlmuse_csv"] = True
            st.success(f"Data is ready ({p_dlmuse})", icon=":material/thumb_up:")

            df_rois = pd.read_csv(st.session_state.paths["dlmuse_csv"])
            with st.expander("Show ROIs", expanded=False):
                st.dataframe(df_rois)

        # Check the input data
        @st.dialog("Input data requirements")  # type:ignore
        def help_inrois_data():
            df_muse = pd.DataFrame(
                columns=["MRID", "702", "701", "600", "601", "..."],
                data=[
                    ["Subj1", "...", "...", "...", "...", "..."],
                    ["Subj2", "...", "...", "...", "...", "..."],
                    ["Subj3", "...", "...", "...", "...", "..."],
                    ["...", "...", "...", "...", "...", "..."],
                ],
            )
            st.markdown(
                """
                ### DLMUSE File:
                The DLMUSE CSV file contains volumes of ROIs (Regions of Interest) segmented by the DLMUSE algorithm. This file is generated as output when DLMUSE is applied to a set of images.
                """
            )
            st.write("Example MUSE data file:")
            st.dataframe(df_muse)

        col1, col2 = st.columns([0.5, 0.1])
        with col2:
            if st.button(
                "Get help 🤔", key="key_btn_help_mlinrois", use_container_width=True
            ):
                help_inrois_data()


def panel_indemog() -> None:
    """
    Panel for uploading demographics
    """
    with st.container(border=True):
        flag_manual = st.checkbox("Enter data manually", False)
        if flag_manual:
            st.info("Please enter values for your sample")
            df_rois = pd.read_csv(st.session_state.paths["dlmuse_csv"])
            df_tmp = pd.DataFrame({"MRID": df_rois["MRID"], "Age": None, "Sex": None})
            df_user = st.data_editor(df_tmp)

            if st.button("Save data"):
                if not os.path.exists(
                    os.path.dirname(st.session_state.paths["demog_csv"])
                ):
                    os.makedirs(os.path.dirname(st.session_state.paths["demog_csv"]))

                df_user.to_csv(st.session_state.paths["demog_csv"], index=False)
                st.success(f"Data saved to {st.session_state.paths['demog_csv']}")

        else:
            if st.session_state.app_type == "cloud":
                utilst.util_upload_file(
                    st.session_state.paths["demog_csv"],
                    "Demographics csv",
                    "uploaded_demog_file",
                    False,
                    "visible",
                )

            else:  # st.session_state.app_type == 'desktop'
                utilst.util_select_file(
                    "selected_demog_file",
                    "Demographics csv",
                    st.session_state.paths["demog_csv"],
                    st.session_state.paths["file_search_dir"],
                )

        if os.path.exists(st.session_state.paths["demog_csv"]):
            p_demog = st.session_state.paths["demog_csv"]
            st.session_state.flags["demog_csv"] = True
            st.success(f"Data is ready ({p_demog})", icon=":material/thumb_up:")

            df_demog = pd.read_csv(st.session_state.paths["demog_csv"])
            with st.expander("Show demographics data", expanded=False):
                st.dataframe(df_demog)

        # Check the input data
        if os.path.exists(st.session_state.paths["demog_csv"]):
            if st.button("Verify input data"):
                [f_check, m_check] = w_mlscores.check_input(
                    st.session_state.paths["dlmuse_csv"],
                    st.session_state.paths["demog_csv"],
                )
                if f_check == 0:
                    st.session_state.flags["dlmuse_csv+demog"] = True
                    st.success(m_check, icon=":material/thumb_up:")
                    st.session_state.flags["csv_mlscores"] = True
                else:
                    st.session_state.flags["dlmuse_csv+demog"] = False
                    st.error(m_check, icon=":material/thumb_down:")
                    st.session_state.flags["csv_mlscores"] = False

        # Help
        @st.dialog("Input data requirements")  # type:ignore
        def help_indemog_data():
            df_demog = pd.DataFrame(
                columns=["MRID", "Age", "Sex"],
                data=[
                    ["Subj1", "57", "F"],
                    ["Subj2", "65", "M"],
                    ["Subj3", "44", "F"],
                    ["...", "...", "..."],
                ],
            )
            st.markdown(
                """
                ### Demographics File:
                The DEMOGRAPHICS CSV file contains demographic information for each subject in the study.
                - **Required Columns:**
                    - **MRID:** Unique subject identifier.
                    - **Age:** Age of the subject.
                    - **Sex:** Sex of the subject (e.g., M, F).
                - **Matching MRIDs:** Ensure the MRID values in this file match the corresponding MRIDs in the DLMUSE file for merging the data files.
                """
            )
            st.write("Example demographic data file:")
            st.dataframe(df_demog)

        col1, col2 = st.columns([0.5, 0.1])
        with col2:
            if st.button(
                "Get help 🤔", key="key_btn_help_mlindemog", use_container_width=True
            ):
                help_indemog_data()


def panel_run() -> None:
    """
    Panel for running ml score calculation
    """
    with st.container(border=True):

        btn_mlscore = st.button("Run MLScore", disabled=False)
        if btn_mlscore:

            if not os.path.exists(st.session_state.paths["mlscores"]):
                os.makedirs(st.session_state.paths["mlscores"])

            # Check flag for harmonization
            flag_harmonize = True
            df_tmp = pd.read_csv(st.session_state.paths["demog_csv"])
            if df_tmp.shape[0] < st.session_state.harm_min_samples:
                flag_harmonize = False
                st.warning("Sample size is small. The data will not be harmonized!")

            if "SITE" not in df_tmp.columns:
                st.warning(
                    "SITE column missing, assuming all samples are from the same site!"
                )
                df_tmp["SITE"] = "SITE1"

            with st.spinner("Wait for it..."):
                st.info("Running: mlscores_workflow ", icon=":material/manufacturing:")
                fcount = df_tmp.shape[0]
                if st.session_state.has_cloud_session:
                    utilcloud.update_stats_db(
                        st.session_state.cloud_user_id, "MLScores", fcount
                    )

                try:
                    if flag_harmonize:
                        w_mlscores.run_workflow(
                            st.session_state.experiment,
                            st.session_state.paths["root"],
                            st.session_state.paths["dlmuse_csv"],
                            st.session_state.paths["demog_csv"],
                            st.session_state.paths["mlscores"],
                        )
                    else:
                        w_mlscores.run_workflow_noharmonization(
                            st.session_state.experiment,
                            st.session_state.paths["root"],
                            st.session_state.paths["dlmuse_csv"],
                            st.session_state.paths["demog_csv"],
                            st.session_state.paths["mlscores"],
                        )
                except:
                    st.warning(":material/thumb_up: ML scores calculation failed!")

        # Check out file
        if os.path.exists(st.session_state.paths["csv_mlscores"]):
            st.success(
                f"Data is ready ({st.session_state.paths['csv_mlscores']}).\n\n Output data includes harmonized ROIs, SPARE scores (AD, Age, Diabetes, Hyperlipidemia, Hypertension, Obesity, Smoking) and SurrealGAN subtype indices (R1-R5)",
                icon=":material/thumb_up:",
            )
            st.session_state.flags["csv_mlscores"] = True

            # Copy output to plots
            if not os.path.exists(st.session_state.paths["plots"]):
                os.makedirs(st.session_state.paths["plots"])
            os.system(
                f"cp {st.session_state.paths['csv_mlscores']} {st.session_state.paths['csv_plot']}"
            )
            st.session_state.flags["csv_plot"] = True
            p_plot = st.session_state.paths["csv_plot"]
            print(f"Data copied to {p_plot}")

            with st.expander("View output data with ROIs and ML scores"):
                df_ml = pd.read_csv(st.session_state.paths["csv_mlscores"])
                st.dataframe(df_ml)

        s_title = "ML Biomarkers"
        s_text = """
        - DLMUSE ROI volumes are harmonized to reference data.
        - SPARE scores are calculated using harmonized ROI values and pre-trained models
        - SurrealGAN scores are calculated using harmonized ROI values and pre-trained models
        - Final results, ROI values and ML scores, are saved in the result csv file
        """
        utilst.util_help_dialog(s_title, s_text)


def panel_download() -> None:
    """
    Panel for downloading results
    """
    with st.container(border=True):
        out_zip = bytes()
        if not os.path.exists(st.session_state.paths["download"]):
            os.makedirs(st.session_state.paths["download"])
        f_tmp = os.path.join(st.session_state.paths["download"], "MLScores.zip")
        out_zip = utilio.zip_folder(st.session_state.paths["mlscores"], f_tmp)

        st.download_button(
            "Download ML Scores",
            out_zip,
            file_name=f"{st.session_state.experiment}_MLScores.zip",
            disabled=False,
        )


st.markdown(
    """
    ### Machine Learning (ML)-Based Imaging Biomarkers
    - Application of pre-trained  machine learning (ML) models to derive imaging biomarkers.
    - ML biomarkers quantify brain changes related to aging and disease.
    - ML models were trained on ISTAGING reference data using DLMUSE ROIs after statistical harmonization with COMBAT.
    """
)

# Call all steps
t1, t2, t3, t4 = st.tabs(["Experiment", "Input ROIs", "Input Demog", "Run MLScores"])
if st.session_state.app_type == "cloud":
    t1, t2, t3, t4, t5 = st.tabs(
        ["Experiment", "Input ROIs", "Input Demog", "Run MLScores", "Download"]
    )

with t1:
    utilpn.util_panel_experiment()
with t2:
    status = st.session_state.flags["experiment"]
    utilpn.util_panel_input_single("dlmuse_csv", status)
with t3:
    status = st.session_state.flags["experiment"]
    utilpn.util_panel_input_single("demog_csv", status)
with t4:
    panel_run()
if st.session_state.app_type == "cloud":
    with t5:
        panel_download()
