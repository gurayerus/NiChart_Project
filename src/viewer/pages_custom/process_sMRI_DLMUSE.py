import os

import pandas as pd
import streamlit as st
import utils.utils_io as utilio
import utils.utils_muse as utilmuse
import utils.utils_nifti as utilni
import utils.utils_st as utilst
from stqdm import stqdm

st.markdown(
    """
    - NiChart sMRI segmentation pipeline using DLMUSE.
    - DLMUSE segments raw T1 images into 145 regions of interest (ROIs) + 105 composite ROIs.

    ### Want to learn more?
    - Visit [DLMUSE GitHub](https://github.com/CBICA/NiChart_DLMUSE)
        """
)

# Panel for output (dataset name + out_dir)
utilst.util_panel_workingdir(st.session_state.app_type)

# Panel for selecting input image files
flag_disabled = not st.session_state.flags['dset']

if st.session_state.app_type == "CLOUD":
    with st.expander(":material/upload: Upload data", expanded=False):  # type:ignore
        utilst.util_upload_folder(
            st.session_state.paths["T1"], "T1 images", flag_disabled,
            "Nifti images can be uploaded as a folder, multiple files, or a single zip file"
        )
        if not flag_disabled:
            fcount = utilio.get_file_count(st.session_state.paths["T1"])
            if fcount > 0:
                st.session_state.flags['T1'] = True
                st.success(
                    f"Data is ready ({st.session_state.paths["T1"]}, {fcount} files)",
                    icon=":material/thumb_up:"
                )

else:  # st.session_state.app_type == 'DESKTOP'
    with st.expander(":material/upload: Select data", expanded=False):  # type:ignore
        utilst.util_select_folder(
            "selected_img_folder",
            "T1 nifti image folder",
            st.session_state.paths["T1"],
            st.session_state.paths["last_in_dir"],
            flag_disabled,
        )
        if not flag_disabled:
            fcount = utilio.get_file_count(st.session_state.paths["T1"])
            if fcount > 0:
                st.session_state.flags['T1'] = True
                st.success(
                    f"Data is ready ({st.session_state.paths["T1"]}, {fcount} files)",
                    icon=":material/thumb_up:"
                )

# Panel for running DLMUSE
with st.expander(":material/grid_on: Segment image", expanded=False):

    flag_disabled = not st.session_state.flags['T1']

    # Device type
    helpmsg = "Choose 'cuda' if your computer has an NVIDIA GPU, 'mps' if you have an Apple M-series chip, and 'cpu' if you have a standard CPU."
    device = utilst.user_input_select(
        "Device",
        "key_select_device",
        ["cuda", "cpu", "mps"],
        None,
        helpmsg, 
        flag_disabled
    )

    # Button to run DLMUSE
    btn_seg = st.button("Run DLMUSE", disabled = flag_disabled)
    if btn_seg:
        run_dir = os.path.join(st.session_state.paths["root"], "src", "NiChart_DLMUSE")
        if not os.path.exists(st.session_state.paths["DLMUSE"]):
            os.makedirs(st.session_state.paths["DLMUSE"])

        with st.spinner("Wait for it..."):
            dlmuse_cmd = f"NiChart_DLMUSE -i {st.session_state.paths['T1']} -o {st.session_state.paths['DLMUSE']} -d {device}"
            st.info(f"Running: {dlmuse_cmd}", icon=":material/manufacturing:")

            # FIXME : bypass dlmuse run
            print(f"About to run: {dlmuse_cmd}")
            os.system(dlmuse_cmd)

    if not flag_disabled:
        out_csv = f"{st.session_state.paths['DLMUSE']}/DLMUSE_Volumes.csv"
        num_dlmuse = utilio.get_file_count(st.session_state.paths["DLMUSE"], '.nii.gz')
        if os.path.exists(out_csv):
            st.session_state.paths["csv_dlmuse"] = out_csv
            st.session_state.flags["csv_dlmuse"] = True
            st.success(
                f"DLMUSE images are ready ({st.session_state.paths['DLMUSE']}, {num_dlmuse} scan(s))",
                icon=":material/thumb_up:",
        )


# Panel for viewing DLMUSE images
with st.expander(":material/visibility: View segmentations", expanded=False):

    flag_disabled = not st.session_state.flags['csv_dlmuse']

    # Selection of MRID
    try:
        df = pd.read_csv(st.session_state.paths["csv_dlmuse"])
        list_mrid = df.MRID.tolist()
    except:
        list_mrid = [""]
    sel_mrid = st.selectbox("MRID", list_mrid, key="selbox_mrid", index=None, disabled = flag_disabled)

    # Create combo list for selecting target ROI
    list_roi_names = utilmuse.get_roi_names(st.session_state.dicts["muse_sel"])
    sel_var = st.selectbox("ROI", list_roi_names, key="selbox_rois", index=None, disabled = flag_disabled)

    # Create a list of checkbox options
    list_orient = st.multiselect(
        "Select viewing planes:",
        utilni.img_views,
        utilni.img_views,
        disabled = flag_disabled
    )

    # View hide overlay
    is_show_overlay = st.checkbox("Show overlay", True, disabled = flag_disabled)

    # Crop to mask area
    crop_to_mask = st.checkbox("Crop to mask", True, disabled = flag_disabled)

    if not flag_disabled:

        # Detect list of ROI indices to display
        list_sel_rois = utilmuse.get_derived_rois(
            sel_var, st.session_state.dicts["muse_derived"]
        )

        # Select images
        flag_img = False
        if sel_mrid is not None:
            st.session_state.paths["sel_img"] = os.path.join(
                st.session_state.paths["T1"], sel_mrid + st.session_state.suff_t1img
            )
            st.session_state.paths["sel_seg"] = os.path.join(
                st.session_state.paths["DLMUSE"], sel_mrid + st.session_state.suff_seg
            )

            flag_img = os.path.exists(st.session_state.paths["sel_img"]) and os.path.exists(
                st.session_state.paths["sel_seg"]
            )

        if flag_img:
            with st.spinner("Wait for it..."):

                # Process image and mask to prepare final 3d matrix to display
                img, mask, img_masked = utilni.prep_image_and_olay(
                    st.session_state.paths["sel_img"],
                    st.session_state.paths["sel_seg"],
                    list_sel_rois,
                    crop_to_mask,
                )

                # Detect mask bounds and center in each view
                mask_bounds = utilni.detect_mask_bounds(mask)

                # Show images
                blocks = st.columns(len(list_orient))
                for i, tmp_orient in stqdm(
                    enumerate(list_orient),
                    desc="Showing images ...",
                    total=len(list_orient),
                ):
                    with blocks[i]:
                        ind_view = utilni.img_views.index(tmp_orient)
                        if is_show_overlay is False:
                            utilst.show_img3D(
                                img, ind_view, mask_bounds[ind_view, :], tmp_orient
                            )
                        else:
                            utilst.show_img3D(
                                img_masked, ind_view, mask_bounds[ind_view, :], tmp_orient
                            )

# Panel for downloading results
if st.session_state.app_type == "CLOUD":
    with st.expander(":material/download: Download Results", expanded=False):

        flag_disabled = not st.session_state.flags['DLMUSE']

        # Zip results and download
        out_zip = bytes()
        if not flag_disabled:
            if not os.path.exists(st.session_state.paths["OutZipped"]):
                os.makedirs(st.session_state.paths["OutZipped"])
            f_tmp = os.path.join(st.session_state.paths["OutZipped"], "DLMUSE.zip")
            out_zip = utilio.zip_folder(st.session_state.paths["DLMUSE"], f_tmp)

        st.download_button(
            "Download DLMUSE results",
            out_zip,
            file_name=f"{st.session_state.dset}_DLMUSE.zip",
            disabled=flag_disabled,
        )

if st.session_state.debug_show_state:
    with st.expander("DEBUG: Session state - all variables"):
        st.write(st.session_state)

if st.session_state.debug_show_paths:
    with st.expander("DEBUG: Session state - paths"):
        st.write(st.session_state.paths)

if st.session_state.debug_show_flags:
    with st.expander("DEBUG: Session state - flags"):
        st.write(st.session_state.flags)