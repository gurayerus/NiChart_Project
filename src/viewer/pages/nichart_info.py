import os
from pathlib import Path
import streamlit as st
import streamlit_antd_components as sac

import utils.utils_pages as utilpg
import utils.utils_navig as utilnav

# ----------------------------
# Page setup
# ----------------------------
utilpg.set_global_style()
st.set_page_config(page_title="NiChart", layout="wide")

imgdir = os.path.join(
    st.session_state.paths["resources"],
    "images",
    "nichart_logo"
)

# ----------------------------
# Helpers
# ----------------------------
def imgfile_to_data(filepath: str | Path) -> str:
    import base64
    with open(filepath, "rb") as f:
        return "data:image/png;base64," + base64.b64encode(f.read()).decode()

# ----------------------------
# Module content registry
# ----------------------------
MODULES = [
    {
        "title": "NiChart",
        "image": "nichart_logo_v2_img1_v2.png",
        "short": "Neuroimaging Chart of **AI-based** imaging biomarkers",
        "full": """
        **NeuroImaging Chart of AI-based Imaging Biomarkers**

        A framework to:

        - Process MRI images
        - Harmonize scans to reference datasets
        - Apply and contribute machine learning models
        - Derive individualized neuroimaging biomarkers
        """
    },
    {
        "title": "MRI Segmentation",
        "image": "nichart_logo_v2_img4_v2.png",
        "short": "Fast **deep-learning** segmentation of **healthy** and **pathological** anatomy",
        "full": """
        **Segmentation of Brain Anatomy**

        - **DLICV:** Intra-cranial volume estimation
        - **DLMUSE:** ROI segmentation
        - **DLWMLS:** White-matter lesion segmentation
        """
    },
    {
        "title": "AI Biomarkers",
        "image": "nichart_logo_v2_img3_v2.png",
        "short": "AI-based biomarkers of **brain aging** and **neurodegeneration**",
        "full": """
        **Supervised ML models**

        - SPARE-BA / DeepSPARE-BA
        - SPARE-AD
        - SPARE cardiometabolic models
        - Depression & psychosis models
        """
    },
    {
        "title": "Brain Aging Dimensions",
        "image": "nichart_logo_v2_img5_v2.png",
        "short": "**Data-driven** indices of heterogeneous brain aging",
        "full": """
        **Semi-supervised models**

        - Surreal-GAN R1–R5 indices
        - CCL-NMF longitudinal patterns
        """
    },
    {
        "title": "Abnormality Maps",
        "image": "nichart_logo_v2_img6_v2.png",
        "short": "Voxelwise CSF abnormality maps of regional atrophy",
        "full": """
        **CSF Abnormalities (WIP)**

        - RAVENS-based tissue density maps
        - Subject-level voxelwise deviation patterns
        """
    }
]

# ----------------------------
# State
# ----------------------------
if "module_idx" not in st.session_state:
    st.session_state.module_idx = 0

# ----------------------------
# Header
# ----------------------------
st.markdown("## What can I do with NiChart?")
st.markdown("Browse the modules using the arrows or selector below.")

# ----------------------------
# Navigation controls
# ----------------------------
col_l, col_c, col_r = st.columns([1, 6, 1])

with col_l:
    if st.button("⬅️", use_container_width=True):
        st.session_state.module_idx = max(0, st.session_state.module_idx - 1)

with col_r:
    if st.button("➡️", use_container_width=True):
        st.session_state.module_idx = min(
            len(MODULES) - 1,
            st.session_state.module_idx + 1
        )

# Optional: direct selector
st.session_state.module_idx = sac.segmented(
    items=[m["title"] for m in MODULES],
    index=st.session_state.module_idx,
    align="center",
    size="large"
)

# ----------------------------
# Focused module card
# ----------------------------
module = MODULES[st.session_state.module_idx]

with st.container():
    st.markdown("---")

    c1, c2 = st.columns([2, 3], vertical_alignment="center")

    with c1:
        st.image(
            imgfile_to_data(os.path.join(imgdir, module["image"])),
            use_column_width=True
        )

    with c2:
        st.markdown(f"### {module['title']}")
        st.markdown(module["short"])

        with st.expander("Learn more"):
            st.markdown(module["full"])

    st.markdown("---")

# ----------------------------
# Footer navigation
# ----------------------------
utilnav.main_navig(
    None, None,
    "Home", "pages/nichart_home.py"
)
