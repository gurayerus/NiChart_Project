import json
import os
import re

import pandas as pd
import streamlit as st
import utils.utils_dataframe as utildf
import utils.utils_nifti as utilni
import utils.utils_pages as utilpg
import utils.utils_panels as utilpn
import utils.utils_plot as utilpl
import utils.utils_rois as utilroi
import utils.utils_session as utilss
import utils.utils_st as utilst
import utils.utils_viewimg as utilvi

# from stqdm import stqdm

# Page config should be called for each page
utilpg.config_page()
utilpg.show_menu()

def panel_load_data():
    # Load ROI data
    in_csv = st.session_state
    df = pd.read_csv('/home/guraylab/GitHub/gurayerus/NiChart_Project/output_folder/IXI/DLMUSE/DLMUSE_Volumes.csv')
    st.session_state.plot_var["df_data"] = df
    
    st.session_state.paths["dlmuse_csv"] = '/home/guraylab/GitHub/gurayerus/NiChart_Project/output_folder/IXI/DLMUSE/DLMUSE_Volumes.csv'

def panel_select() -> None:
    """
    Panel for selecting variables
    """
    with st.container(border=True):

        df = st.session_state.plot_var["df_data"]

        if "MRID" not in df.columns:
            st.warning(
                'The data file does not contain the required "MRID" column. The operation cannot proceed.'
            )
            return

        with open(st.session_state.dict_categories, "r") as f:
            dict_categories = json.load(f)

        # User selects a category to include
        cols_tmp = st.columns((1, 3, 1), vertical_alignment="bottom")
        with cols_tmp[0]:
            sel_cat = st.selectbox(
                "Select variable category",
                list(dict_categories.keys()),
                index=None,
                help="Variable categories group together related variables to facilitate selection of a subset of all data variables.",
            )

        if sel_cat is None:
            sel_vars_cat = []
        else:
            sel_vars_cat = dict_categories[sel_cat]
            sel_vars_cat = [x for x in sel_vars_cat if x in df.columns]

        with cols_tmp[1]:
            sel_vars_cat = st.multiselect(
                "Select variables from this category",
                sel_vars_cat,
                sel_vars_cat,
                help="The list shows variables that are present in the data file! If the list is empty, it means that none of the variables in this category are present in the data file.",
            )

        with cols_tmp[2]:
            if st.button("Add selected variables"):
                sel_vars_cat_uniq = [
                    v for v in sel_vars_cat if v not in st.session_state.plot_sel_vars
                ]
                st.session_state.plot_sel_vars += sel_vars_cat_uniq

        sel_vars_final = st.multiselect(
            "Select final variables to keep",
            st.session_state.plot_sel_vars,
            st.session_state.plot_sel_vars,
        )

        # Select the ones in current dataframe
        sel_vars_final = [x for x in sel_vars_final if x in df.columns]
        st.session_state.plot_sel_vars = sel_vars_final

        if st.button("Select variables"):
            if "MRID" not in st.session_state.plot_sel_vars:
                st.session_state.plot_sel_vars = [
                    "MRID"
                ] + st.session_state.plot_sel_vars
            sel_vars = st.session_state.plot_sel_vars
            st.success(f"Selected variables: {sel_vars}")

            # Add centile vars
            vars_cent = []
            for tmp_var in sel_vars:
                c_var = tmp_var + "_centiles"
                if c_var in df.columns and c_var not in sel_vars:
                    vars_cent.append(c_var)
            sel_vars_wcent = sel_vars + vars_cent

            df = df[sel_vars_wcent]
            st.session_state.plot_var["df_data"] = df

            with st.expander("Show selected data", expanded=False):
                st.dataframe(st.session_state.plot_var["df_data"])

        col1, col2 = st.columns([0.5, 0.1])
        with col2:
            if st.button("Revert to initial data", use_container_width=True):
                st.session_state.plot_var["df_data"] = utildf.read_dataframe(
                    st.session_state.paths["csv_plot"]
                )
                utilss.reset_plots()
                st.session_state.is_updated["csv_plot"] = False
                st.session_state.plot_sel_vars = []
                st.rerun()

        s_title = "Variable Selection"
        s_text = """
        - This step allows you to optionally select a subset of variables for analysis.
        - Variables are grouped into categories.
        - Select a category. The selection box displays variables from that category that are present in your data. An empty selection box signifies no overlap between the selected category and your dataset.
        - You can further refine your selection by choosing specific variables within each chosen category.
        - You can revert back to the initial data at any point.
        """
        utilst.util_help_dialog(s_title, s_text)

def show_img() -> None:
    """
    Show images
    """
    if st.session_state.sel_mrid == "":
        st.warning("Please select a subject on the plot!")
        return

    if st.session_state.sel_roi_img == "":
        st.warning("Please select an ROI!")
        return

    # Insert duplicate suffix fix
    sel_mrid = st.session_state.sel_mrid
    if sel_mrid is not None:
        st.session_state.paths["sel_img"] = os.path.join(
            # hardcoded fix for T1 suffix
            st.session_state.paths["T1"],
            re.sub(r"_T1$", "", sel_mrid) + st.session_state.suff_t1img,
        )

        st.session_state.paths["sel_seg"] = os.path.join(
            st.session_state.paths["dlmuse"],
            re.sub(r"_T1$", "", sel_mrid) + st.session_state.suff_seg,
        )

    if not os.path.exists(st.session_state.paths["sel_img"]):
        if not utilvi.check_image_underlay():
            st.warning("I'm having trouble locating the underlay image!")
            if st.button("Select underlay img path and suffix"):
                utilvi.update_ulay_image_path()
            return

    if not os.path.exists(st.session_state.paths["sel_seg"]):
        if not utilvi.check_image_overlay():
            st.warning("I'm having trouble locating the overlay image!")
            if st.button("Select overlay img path and suffix"):
                utilvi.update_olay_image_path()
            return

    with st.spinner("Wait for it..."):
        # Get indices for the selected var
        list_rois = utilroi.get_list_rois(
            st.session_state.sel_roi_img,
            st.session_state.rois["roi_dict_inv"],
            st.session_state.rois["roi_dict_derived"],
        )

        img, mask, img_masked = utilni.prep_image_and_olay(
            st.session_state.paths["sel_img"],
            st.session_state.paths["sel_seg"],
            list_rois,
            st.session_state.mriview_var["crop_to_mask"],
        )

        # Detect mask bounds and center in each view
        mask_bounds = utilni.detect_mask_bounds(mask)

        # Show images
        list_orient = st.session_state.mriview_var["list_orient"]
        blocks = st.columns(len(list_orient))
        for i, tmp_orient in enumerate(list_orient):
            with blocks[i]:
                ind_view = utilni.img_views.index(tmp_orient)
                size_auto = True
                if not st.session_state.mriview_var["show_overlay"]:
                    utilst.show_img3D(
                        img, ind_view, mask_bounds[ind_view, :], tmp_orient, size_auto
                    )
                else:
                    utilst.show_img3D(
                        img_masked,
                        ind_view,
                        mask_bounds[ind_view, :],
                        tmp_orient,
                        size_auto,
                    )


def show_plots(df: pd.DataFrame, btn_plots: bool) -> None:
    """
    Display plots
    """
    # Add a plot (a first plot is added by default; others at button click)
    if st.session_state.plots.shape[0] == 0 or btn_plots:
        # Select xvar and yvar, if not set yet
        num_cols = df.select_dtypes(include="number").columns
        if num_cols.shape[0] > 0:
            if st.session_state.plot_var["xvar"] == "":
                st.session_state.plot_var["xvar"] = num_cols[0]
                if st.session_state.plot_var["yvar"] == "":
                    if num_cols.shape[0] > 1:
                        st.session_state.plot_var["yvar"] = num_cols[1]
                    else:
                        st.session_state.plot_var["yvar"] = num_cols[0]
            utilpl.add_plot()
        else:
            st.warning("No numeric columns in data!")

    # Read plot ids
    df_p = st.session_state.plots
    list_plots = df_p.index.tolist()
    plots_per_row = st.session_state.plot_const["num_per_row"]

    # Render plots
    #  - iterates over plots;
    #  - for every "plots_per_row" plots, creates a new columns block, resets column index, and displays the plot

    if df.shape[0] == 0:
        st.warning("Dataframe is empty, skip plotting!")
        return

    plots_arr = []
    for i, plot_ind in enumerate(list_plots):
        column_no = i % plots_per_row
        if column_no == 0:
            blocks = st.columns(plots_per_row)
        with blocks[column_no]:
            plot_type = st.session_state.plots.loc[plot_ind, "plot_type"]
            if plot_type == "Scatter Plot":
                new_plot = utilpl.display_scatter_plot(
                    df,
                    plot_ind,
                    not st.session_state.plot_var["hide_settings"],
                    st.session_state.sel_mrid,
                )
            elif plot_type == "Distribution Plot":
                new_plot = utilpl.display_dist_plot(
                    df,
                    plot_ind,
                    not st.session_state.plot_var["hide_settings"],
                    st.session_state.sel_mrid,
                )
            plots_arr.append(new_plot)

    if st.session_state.plot_var["show_img"]:
        show_img()


def panel_plot() -> None:
    """
    Panel plot
    """
    # Read dataframe
    # if st.session_state.plot_var["df_data"].shape[0] == 0:
    #     st.session_state.plot_var["df_data"] = utildf.read_dataframe(
    #         st.session_state.paths["csv_plot"]
    #     )
    df = st.session_state.plot_var["df_data"]
    if df.shape[0] == 0:
        st.warning("Dataframe has 0 rows!")
        return

    # Add sidebar parameters
    with st.sidebar:
        # Button to add plot
        tmp_cols = st.columns((1, 1), vertical_alignment="bottom")
        with tmp_cols[0]:
            plot_type = st.selectbox(
                "Plot Type", ["Scatter Plot", "Distribution Plot"], index=0
            )
            if plot_type is not None:
                st.session_state.plot_var["plot_type"] = plot_type

        with tmp_cols[1]:
            btn_plots = st.button("Add plot", disabled=False)

        st.session_state.plot_const["num_per_row"] = st.slider(
            "Plots per row",
            st.session_state.plot_const["min_per_row"],
            st.session_state.plot_const["max_per_row"],
            st.session_state.plot_const["num_per_row"],
            disabled=False,
        )

        st.session_state.plot_var["h_coeff"] = st.slider(
            "Plot height",
            min_value=st.session_state.plot_const["h_coeff_min"],
            max_value=st.session_state.plot_const["h_coeff_max"],
            value=st.session_state.plot_const["h_coeff"],
            step=st.session_state.plot_const["h_coeff_step"],
            disabled=False,
        )

        # Checkbox to show/hide plot options
        st.session_state.plot_var["hide_settings"] = st.checkbox(
            "Hide plot settings",
            value=st.session_state.plot_var["hide_settings"],
            disabled=False,
        )

        # Checkbox to show/hide plot legend
        st.session_state.plot_var["hide_legend"] = st.checkbox(
            "Hide legend",
            value=st.session_state.plot_var["hide_legend"],
            disabled=False,
        )

        # Selected id
        list_mrid = df.MRID.sort_values().tolist()
        if st.session_state.sel_mrid == "":
            sel_ind = None
        else:
            sel_ind = list_mrid.index(st.session_state.sel_mrid)
        sel_mrid = st.selectbox(
            "Selected subject",
            list_mrid,
            sel_ind,
            help="Select a subject from the list, or by clicking on data points on the plots",
        )
        if sel_mrid is not None:
            st.session_state.sel_mrid = sel_mrid
            st.session_state.paths["sel_img"] = ""
            st.session_state.paths["sel_seg"] = ""

        st.divider()

        # Checkbox to show/hide mri image
        st.session_state.plot_var["show_img"] = st.checkbox(
            "Show image", value=st.session_state.plot_var["show_img"], disabled=False
        )

        if st.session_state.plot_var["show_img"]:

            # Selected roi rois
            list_roi = df.columns.sort_values().tolist()
            if st.session_state.sel_roi_img == "":
                sel_ind = None
            else:
                sel_ind = list_roi.index(st.session_state.sel_roi_img)
            sel_roi_img = st.selectbox(
                "Selected ROI", list_roi, sel_ind, help="Select an ROI from the list"
            )
            if sel_roi_img is not None:
                st.session_state.sel_roi_img = sel_roi_img

            # Create a list of checkbox options
            list_orient = st.multiselect(
                "Select viewing planes:", utilni.img_views, utilni.img_views
            )
            if list_orient is not None:
                st.session_state.mriview_var["list_orient"] = list_orient

            # View hide overlay
            st.session_state.mriview_var["show_overlay"] = st.checkbox(
                "Show overlay", True
            )

            # Crop to mask area
            st.session_state.mriview_var["crop_to_mask"] = st.checkbox(
                "Crop to mask", True
            )

            st.session_state.mriview_var["w_coeff"] = st.slider(
                "Img width",
                min_value=st.session_state.mriview_const["w_coeff_min"],
                max_value=st.session_state.mriview_const["w_coeff_max"],
                value=st.session_state.mriview_const["w_coeff"],
                step=st.session_state.mriview_const["w_coeff_step"],
                disabled=False,
            )

    # Show plot
    show_plots(df, btn_plots)

def panel_plot2():
    st.write('Hello')
    
    

with st.container(border=True):
    st.markdown(
        """
        ### View Brain Anatomy
        """
    )

    st.markdown("##### Select Task")
    list_tasks = ["Load Data", "Select Variables", "Plot"]
    sel_task = st.pills(
        "Select Task", list_tasks, selection_mode="single", label_visibility="collapsed"
    )
    if sel_task == "Load Data":
        panel_load_data()
    elif sel_task == "Select Variables":
        panel_select()
    elif sel_task == "Plot":
        list_rois = utilroi.get_roi_names(st.session_state.dicts["muse_sel"])
        config = {
            'list_roi': list_rois,
            'list_mrid': ['IXI313-HH-2241', 'IXI080-HH-1341'],
            'dir_ulay': '/home/guraylab/GitHub/gurayerus/NiChart_Project/output_folder/IXI/Nifti/T1',
            'dir_olay': '/home/guraylab/GitHub/gurayerus/NiChart_Project/output_folder/IXI/DLMUSE',
        }
        utilpn.panel_view_mri(config)
        #panel_plot()
