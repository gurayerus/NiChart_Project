import os
import shutil
from typing import Any, Optional
import jwt
import time
import yaml
import pandas as pd
import streamlit as st
import utils.utils_rois as utilroi
import utils.utils_cmaps as utilcmap
import utils.utils_toolloader as utiltl
import os
from PIL import Image
import streamlit_antd_components as sac

#################################################
## Functions to update session info for the cloud

# Function to parse AWS login (if available)
def process_session_token() -> Any:
    # headers = _get_websocket_headers()
    headers = st.context.headers
    if not headers or "X-Amzn-Oidc-Data" not in headers:
        return ""
    return headers["X-Amzn-Oidc-Data"]

def process_session_user_id() -> Any:
    headers = st.context.headers
    if not headers or "X-Amzn-Oidc-Identity" not in headers:
        return "NO_USER_FOUND"
    return headers["X-Amzn-Oidc-Identity"]

def process_session_user_email() -> Any:
    headers = st.context.headers
    if not headers or "X-Amzn-Oidc-Data" not in headers:
        return "NO_EMAIL_FOUND"
    raw_token = headers['X-Amzn-Oidc-Data']
    decoded_token = jwt.decode(
        raw_token,
        algorithms=["ES256"],
        options={"verify_signature": False},
    )
    if not decoded_token or 'email' not in decoded_token:
        return "NO_EMAIL_FOUND"
    return decoded_token['email']

#################################################
## Functions to update session variables

def update_project(sel_project: Optional[str]) -> None:
    """
    Updates when project changes
    """
    if sel_project is None:
        return

    if sel_project == st.session_state.user_sel['prj_name']:
        return

    # Create project dir
    p_prj = os.path.join(
        st.session_state.paths['out_dir'], sel_project
    )

    try:
        if not os.path.exists(p_prj):
            os.makedirs(p_prj)
            st.toast(f'Created folder {sel_project}')
            time.sleep(1)
    except:
        st.error(f'Could not create project folder: {p_prj}')
        return

    # Set project name
    st.session_state.prj_name = sel_project
    st.session_state.paths['prj_dir'] = p_prj
    
    ## FIXME
    #reset_dicoms()
    #init_scan()
    #init_participant()
    
    st.toast(f'Updated project folder {sel_project}')
    st.session_state.user_sel['project'] = sel_project
    st.session_state.user_sel['project_selected_explicitly'] = True
    st.session_state.paths['project'] = p_prj

    st.session_state.paths['curr_data'] = st.session_state.paths['prj_dir']

#################################################
## Misc utility functions

def disp_session_state() -> None:
    '''
    Show session state variables
    '''
    if '_debug_flag_show' not in st.session_state:
        st.session_state['_debug_flag_show'] = st.session_state.system_vars['flag_show_session']

    def update_val() -> None:
        st.session_state.system_vars['flag_show_session'] = st.session_state['_debug_flag_show']

    sac.divider(label='Debug', icon = 'gear',  align='center', color='gray')
    st.checkbox(
        'Show Session State',
        key = '_debug_flag_show',
        on_change = update_val
    )

    if st.session_state.system_vars['flag_show_session']:
        with st.container(border=True):
            st.markdown('##### Session State:')
            list_items = sorted([x for x in st.session_state.keys() if not str(x).startswith('_')])
            #list_items = sorted([x for x in st.session_state.keys() if x.startswith('_')])
            st.pills(
                "Select Session State Variable(s) to View",
                list_items,
                selection_mode="multi",
                key='_debug_sel_vars',
                # default=st.session_state['debug']['sel_vars'],
                label_visibility="collapsed",
            )
            st.session_state.system_vars['sel_session_vars'] = st.session_state['_debug_sel_vars']

            for sel_var in st.session_state.system_vars['sel_session_vars']:
                st.markdown('➤ ' + sel_var + ':')
                st.write(st.session_state[sel_var])
    #print('FIXME: This is bypassed for now ...')

def copy_test_folders() -> None:
    '''
    Copy demo folders into user folders as needed
    '''
    if st.session_state.system_vars['has_cloud_session']:
        # Copy demo dirs to user folder (TODO: make this less hardcoded)
        demo_dir_paths = [
            os.path.join(
                st.session_state.paths["root"],
                "output_folder",
                "NiChart_Demo1",
            ),
            os.path.join(
                st.session_state.paths["root"],
                "output_folder",
                "NiChart_Demo2",
            ),
        ]
        for demo in demo_dir_paths:
            demo_name = os.path.basename(demo)
            destination_path = os.path.join(
                st.session_state.paths["out_dir"], demo_name
            )
            if os.path.exists(destination_path):
                shutil.rmtree(destination_path)
            shutil.copytree(demo, destination_path, dirs_exist_ok=True)

def reset_dicoms() -> None:
    '''
    Reset dicom variables
    '''
    st.session_state.dicoms = {
        'list_series': None,
        'sel_serie': None,
        'num_dicom_scans': 0,
        'df_dicoms': None
    }

#################################################
## Functions to initialize session variables

def init_paths() -> None:
    '''
    Set paths to pre-defined folders
    '''
    # Resources
    p_root = os.path.dirname(os.path.dirname(os.getcwd()))
    p_init = p_root
    p_resources = os.path.join(
        p_root, "resources"
    )
    p_centiles = os.path.join(
        p_resources, "reference_data", "centiles"
    )
    #p_sample = os.path.join(
        #p_root, "sample_datasets", "demo_dataset_IXI"
    #)    
    p_sample = os.path.join(
        p_root, "sample_datasets", "demo_dataset"
    )    
    p_proc_def = os.path.join(
        p_resources, "process_definitions"
    )
    
    # Output
    user_id = ''
    if st.session_state.cloud_vars['has_cloud_session']:
        user_id = st.session_state.cloud_user_id
        p_out = os.path.join(
            "/fsx/fsx/", user_id
        )
    else:
        p_out = os.path.join(
            p_root, 'output_folder', user_id
        )
    if not os.path.exists(p_out):
        os.makedirs(p_out)
    
    # Paths specific to project
    p_prj = os.path.join(
        p_out, st.session_state.user_sel['prj_name']
    )
    if not os.path.exists(p_prj):
        os.makedirs(p_prj)

    st.session_state.dicts = {
        "muse_derived": os.path.join(
            p_resources, "MUSE", "list_MUSE_mapping_derived.csv"
        ),
        "muse_all": os.path.join(p_resources, "MUSE", "list_MUSE_all.csv"),
        "muse_sel": os.path.join(p_resources, "MUSE", "list_MUSE_primary.csv"),
    }

    st.session_state.paths = {
        "root": p_root,
        "init": p_init,
        "resources": p_resources,
        "sample_data": p_sample,
        "centiles" : p_centiles,
        "proc_def": p_proc_def,
        "file_search_dir": "",
        "out_dir": p_out,
        "host_out_dir": None,
        "prj_dir": p_prj,
        "project": p_prj,
        'target': None,
        "curr_data": None
    }

    # Host-container dir mapping which can be useful for local nested containers
    # Code which relies on this should always check if it is None
    # And use local paths instead if so.
    host_out_dir = os.getenv("NICHART_HOST_DATA_DIR", None)
    if host_out_dir is not None:
        st.session_state.paths['host_out_dir'] = host_out_dir
    
    # List of output folders
    st.session_state.out_dirs = [
        'participants',
        'dicoms',
        't1', 't2', 'fl', 'fmri', 'dti',
        'dlmuse_seg', 'dlmuse_vol',
        'dlwmls', 'spare',
    ]
    
    ############
    # FIXME : set init folder to test folder outside repo
    st.session_state.paths["init"] = os.path.join(
        st.session_state.paths["root"], "test_data"
    )
    st.session_state.paths["file_search_dir"] = st.session_state.paths["init"]
    ############

def init_pipeline_definitions() -> None:
    plist = os.path.join(
        st.session_state.paths['resources'], 'pipelines', 'list_pipelines.csv'
    )
    st.session_state.pipelines = pd.read_csv(plist)
    
def init_reference_data() -> None:
    indir = os.path.join(
        st.session_state.paths['resources'], 'reference_data', 'sample1'
    )
    t1 = os.path.join(indir, 't1', 'sample1_T1.nii.gz')
    fl = os.path.join(indir, 'fl', 'sample1_FL.nii.gz')
    dlmuse = os.path.join(indir, 'dlmuse', 'sample1_T1_DLMUSE.nii.gz')
    dlwmls = os.path.join(indir, 'dlwmls', 'sample1_FL_DLWMLS.nii.gz')
    st.session_state.ref_data = {
        't1' : t1,
        'fl' : fl,
        'dlmuse' : dlmuse,
        'dlwmls' : dlwmls
    }

def init_var_groups() -> None:
    '''
    Read variable groups to a dataframe
    '''
    f_vars = os.path.join(
        st.session_state.paths['resources'], 'lists', 'dict_var_groups.yaml'
    )

    with open(f_vars, 'r') as file:
        data = yaml.safe_load(file)

    rows = []
    for group_name, group_info in data.items():
        raw_values = group_info.get('values', [])
        str_values = [str(v) for v in raw_values]  # ensure uniform type
        rows.append({
            'group': group_name,
            'category': group_info.get('category'),
            'vtype': group_info.get('vtype'),
            'atlas': group_info.get('atlas'),
            'values': str_values
        })

    df = pd.DataFrame(rows)
    st.session_state.dicts['df_var_groups'] = df

def init_dicts() -> None:
    '''
    Initialize all data dictionaries (atlas roi def.s etc.)
    '''
    # MUSE dictionaries
    muse = utilroi.read_muse_dicts()
    st.session_state.dicts = {
        'muse': muse
    }

def init_muse_roi_def() -> None:
    # Paths to roi lists
    muse: dict[str, Any]  = {
        'path': os.path.join(st.session_state.paths['resources'], 'lists', 'MUSE'),
        'list_rois' : 'MUSE_listROIs.csv',
        'list_derived' : 'MUSE_mapping_derivedROIs.csv',
        'list_groups' : 'MUSE_ROI_Groups_v1.csv',
    }
    
    # Read roi lists to dictionaries
    df_tmp = pd.read_csv(
        os.path.join(muse['path'], muse['list_rois']),
    )
    dict1 = dict(zip(df_tmp["Index"].astype(str), df_tmp["Name"].astype(str)))
    dict2 = dict(zip(df_tmp["Name"].astype(str), df_tmp["Index"].astype(str)))
    dict3 = utilroi.muse_derived_to_dict(
        os.path.join(muse['path'], muse['list_derived'])
    )
    df_derived = utilroi.muse_derived_to_df(
        os.path.join(muse['path'], muse['list_derived'])
    )
    df_groups = utilroi.muse_roi_groups_to_df(
        os.path.join(muse['path'], muse['list_groups'])
    )
    muse['dict_roi'] = dict1
    muse['dict_roi_inv'] = dict2
    muse['dict_derived'] = dict3
    muse['df_derived'] = df_derived
    muse['df_groups'] = df_groups
    
    # Read MUSE ROI lists
    st.session_state.rois = {
        'muse' : muse
    }

def init_cloud_vars() -> None:
    st.session_state.cloud_vars = {
        'forced_cloud': False,
        'app_type': 'desktop',
        'has_cloud_session': False,
        'cloud_session_token': None,
        'cloud_user_id': None,
        'cloud_user_email': None,
    }
    
    # Update cloud vars if app type is 'cloud'
    if os.getenv("NICHART_FORCE_CLOUD", "0") == "1":
        st.session_state.cloud_vars['forced_cloud'] = True
        st.session_state.cloud_vars['app_type'] = "cloud"
        st.session_state.cloud_vars['cloud_session_token'] = process_session_token()
        if st.session_state.cloud_vars['cloud_session_token']:
            st.session_state.cloud_vars['has_cloud_session'] = True
            st.session_state.cloud_vars['cloud_user_id'] = process_session_user_id()
            st.session_state.cloud_vars['cloud_user_email'] = process_session_user_email()

def init_system_vars() -> None:
    st.session_state.system_vars = {
        'mode': 'debug',                # 'release'
        'skip_survey': True,
        'pipeline_colors': [
            'red', 'pink', 'grape', 'violet', 'indigo', 'blue',
            'cyan', 'teal', 'green', 'lime', 'yellow', 'orange',
        ],
        'pipeline_categories': utiltl.overall_pipeline_category_listing(),
        'pipeline_requirements': utiltl.overall_pipeline_requirements_listing(),
        'do_harmonize': False,
        'nifti_dicom_upload_mode': None,
        'list_mods': ["T1", "T2", "FL", "DTI", "fMRI"],
        'mean_icv': 1430000,            # Average ICV estimated from a large sample
        'harm_min_samples': 30,
        'icon_thumb': {         # Icons for panels
            False: ":material/thumb_down:",
            True: ":material/thumb_up:",
        },
        'flag_show_session': False,
        'sel_session_vars': [],
        'nicon': Image.open("../resources/nichart1.png"),
        'forced_cloud0': None,
        'app_type': None,
        'has_cloud_session': False,
        'cloud_session_token': None,
        'cloud_user_id': None,
    }
    st.session_state.system_vars['harmonizable_pipelines'] = st.session_state.system_vars['pipeline_categories']['harmonized']

def set_defaults_user_sel() -> None:
    st.session_state.user_sel = {
        'layout_plots': 'Main',         # 'Sidebar'
        'workflow': None,
        'prj_name': 'user_default',
        'pipeline': None,
        'flag_harmonize': False,
        'mrid': None,
        'age': None,
        'sex': None,
        'roi': None,
    }

def init_session_state() -> None:
    '''
    Initialize Session State Values
    '''
    if "instantiated" not in st.session_state:
        
        # Set initial session variables
        init_cloud_vars()
        init_system_vars()
        init_user_sel()
        init_paths()
        init_dicts()
        init_var_groups()

        # Update project variables
        update_project(st.session_state.user_sel['prj_name'])

        # Copy test data to user folder
        copy_test_folders()

        # Init variables for different pages 
        init_muse_roi_def()
        init_reference_data()

        init_pipeline_definitions()
        reset_dicoms()
        
        # Set flag
        st.session_state.instantiated = True

