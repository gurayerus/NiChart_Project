import streamlit as st
import utils.utils_pages as utilpg
import utils.utils_io as utilio
import utils.utils_plots as utilpl
import utils.utils_mriview as utilmri
import utils.utils_data_view as utildv
import utils.utils_session as utilses
import pandas as pd
import os
from pathlib import Path
from utils.utils_logger import setup_logger

import streamlit_antd_components as sac

logger = setup_logger()
logger.debug('Page: View Results')

# Page config should be called for each page
utilpg.config_page()
utilpg.show_menu()
utilpg.set_global_style()

def view_project_folder():
    """
    Panel for viewing files in a project folder
    """
    with st.container(border=True):
        in_dir = st.session_state.paths['project']
        utildv.data_overview(in_dir)

def select_data_files():
    """
    Panel for merging selected data files
    """
    with st.container(border=True):
        in_dir = st.session_state.paths['project']
        utildv.select_files(in_dir)

def panel_data_merge():
    '''
    Detect all csv files and merge them
    '''
    in_dir = st.session_state.paths['project']
    utildv.data_merge(in_dir)

def plot_vars():
    """
    Panel for viewing dlmuse results
    """    
    st.session_state.plot_data['df_data'] = utilpl.read_data(st.session_state.paths['plot_data']) 
    var_groups_data = ['demog', 'roi']
    var_groups_hue = ['cat_vars']
    pipeline = 'dlmuse'

    utilpl.panel_set_params_plot(
        st.session_state.plot_params,
        var_groups_data,
        var_groups_hue,
        pipeline
    )

    utilpl.panel_show_plots()

def view_images():
    ulay = st.session_state.ref_data["t1"]
    olay = st.session_state.ref_data["dlmuse"]        
    #utilmri.panel_view_seg(ulay, olay, 'muse')

st.markdown(
    """
    ### View Results 
    """
)

tab = sac.tabs(
    items=[
        sac.TabsItem(label='View Project Folder'),
        sac.TabsItem(label='Select Data Files'),
        sac.TabsItem(label='Plot Data'),
        sac.TabsItem(label='View Images'),
    ],
    size='lg',
    align='left'
)


if tab == 'View Project Folder':
    view_project_folder()

elif tab == 'Select Data Files':
    select_data_files()

elif tab == 'Plot Data':
    plot_vars()

elif tab == 'View Images':
    view_images()

# Show selections
utilses.disp_selections()

# Show session state vars
if st.session_state.mode == 'debug':
    utilses.disp_session_state()

