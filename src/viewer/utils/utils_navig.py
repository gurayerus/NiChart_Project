import os
import shutil
import time
from typing import Any

import pandas as pd
import numpy as np
import nibabel as nib
from nibabel.orientations import axcodes2ornt, ornt_transform
from scipy import ndimage
import utils.utils_misc as utilmisc
import utils.utils_user_select as utiluser
import utils.utils_io as utilio

import utils.utils_session as utilses
import pandas as pd

import streamlit_antd_components as sac

import streamlit as st
from stqdm import stqdm
from typing import Optional

from utils.utils_logger import setup_logger
logger = setup_logger()

@st.dialog("Help Information", width="medium")
def my_help() -> None:
    st.write(
        """
        **Project Folder Help**
        - All processing steps are performed inside a project folder.
        - By default, NiChart will create and use a current project folder for you.
        - You may also create a new project folder using any name you choose.
        - If needed, you can reset the current project folder (this will remove all files inside it, but keep the folder itself), allowing you to start fresh.
        - You may also switch to an existing project folder.

        **Note:** If you are using the cloud version, stored files will be removed periodically, so previously used project folders might not remain available.
        """
    )

def main_navig(
    txt_back: Optional[str] = None,
    page_back: Optional[str] = None,
    txt_fwd: Optional[str] = None,
    page_fwd: Optional[str] = None,
    func_settings: Optional[Any] = None,
    func_help: Optional[Any] = None
) -> None:
    sac.divider()

    with st.container(horizontal=True, horizontal_alignment="center"):
        if page_back is not None:
            if st.button('', icon=':material/arrow_back:', help = txt_back):
                st.switch_page(page_back)

        if page_fwd is not None:
            if st.button('', icon=':material/arrow_forward:', help = txt_fwd):
                st.switch_page(page_fwd)

        if func_settings is not None:
            if st.button('', icon=':material/settings:', help = 'Settings'):
                func_settings()


        if func_help is not None:
            if st.button('', icon=':material/help:', help = 'Help'):
                func_help()

