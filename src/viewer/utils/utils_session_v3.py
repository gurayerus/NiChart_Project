import os
import shutil
import time
import jwt
import yaml
from pathlib import Path
from typing import Any, Optional

import pandas as pd
import streamlit as st
from PIL import Image
import streamlit_antd_components as sac

import utils.utils_rois as utilroi
import utils.utils_toolloader as utiltl

def _get_headers() -> dict[str, str]:
    return st.context.headers or {}


def get_cloud_token() -> Optional[str]:
    return _get_headers().get("X-Amzn-Oidc-Data")


def get_cloud_user_id() -> Optional[str]:
    return _get_headers().get("X-Amzn-Oidc-Identity")


def get_cloud_user_email() -> Optional[str]:
    token = get_cloud_token()
    if not token:
        return None

    decoded = jwt.decode(
        token,
        algorithms=["ES256"],
        options={"verify_signature": False},
    )
    return decoded.get("email")

def init_cloud_state() -> None:
    st.session_state.cloud = {
        "forced": False,
        "app_type": "desktop",
        "has_session": False,
        "token": None,
        "user_id": None,
        "email": None,
    }

    if os.getenv("NICHART_FORCE_CLOUD") == "1":
        st.session_state.cloud["forced"] = True
        st.session_state.cloud["app_type"] = "cloud"

        token = get_cloud_token()
        if token:
            st.session_state.cloud.update({
                "has_session": True,
                "token": token,
                "user_id": get_cloud_user_id(),
                "email": get_cloud_user_email(),
            })

def init_system_state() -> None:
    st.session_state.system = {
        "mode": "debug",
        "skip_survey": True,
        "pipeline_colors": [
            "red","pink","grape","violet","indigo","blue",
            "cyan","teal","green","lime","yellow","orange",
        ],
        "pipeline_categories": utiltl.overall_pipeline_category_listing(),
        "pipeline_requirements": utiltl.overall_pipeline_requirements_listing(),
        "mean_icv": 1_430_000,
        "harm_min_samples": 30,
        "show_session": False,
        "icon_thumb": {
            False: ":material/thumb_down:",
            True: ":material/thumb_up:",
        },
        "nicon": Image.open("../resources/nichart1.png"),
    }

    st.session_state.system["harmonizable_pipelines"] = (
        st.session_state.system["pipeline_categories"]["harmonized"]
    )

def init_user_state() -> None:
    st.session_state.user = {
        "project": "user_default",
        "workflow": None,
        "pipeline": None,
        "harmonize": False,
        "mrid": None,
        "age": None,
        "sex": None,
        "roi": None,
    }

def init_paths() -> None:
    root = Path(__file__).resolve().parents[2]
    resources = root / "resources"

    if st.session_state.cloud["has_session"]:
        out_dir = Path("/fsx/fsx") / st.session_state.cloud["user_id"]
    else:
        out_dir = root / "output_folder"

    out_dir.mkdir(parents=True, exist_ok=True)

    project_dir = out_dir / st.session_state.user["project"]
    project_dir.mkdir(exist_ok=True)

    st.session_state.paths = {
        "root": root,
        "resources": resources,
        "out": out_dir,
        "project": project_dir,
        "centiles": resources / "reference_data" / "centiles",
        "pipelines": resources / "pipelines",
    }

def init_data_state() -> None:
    st.session_state.data = {}
    st.session_state.data["pipelines"] = pd.read_csv(
        st.session_state.paths["pipelines"] / "list_pipelines.csv"
    )

def init_muse_rois() -> None:
    muse_dir = st.session_state.paths["resources"] / "lists" / "MUSE"

    df = pd.read_csv(muse_dir / "MUSE_listROIs.csv")

    st.session_state.data["muse"] = {
        "roi": dict(zip(df["Index"].astype(str), df["Name"].astype(str))),
        "roi_inv": dict(zip(df["Name"].astype(str), df["Index"].astype(str))),
        "derived": utilroi.muse_derived_to_dict(muse_dir / "MUSE_mapping_derivedROIs.csv"),
        "df_derived": utilroi.muse_derived_to_df(muse_dir / "MUSE_mapping_derivedROIs.csv"),
        "df_groups": utilroi.muse_roi_groups_to_df(muse_dir / "MUSE_ROI_Groups_v1.csv"),
    }

def reset_dicoms() -> None:
    st.session_state.dicoms = {
        "series": None,
        "selected": None,
        "count": 0,
        "df": None,
    }

def update_project(name: Optional[str]) -> None:
    if not name or name == st.session_state.user["project"]:
        return

    project_dir = st.session_state.paths["out"] / name
    project_dir.mkdir(exist_ok=True)

    st.session_state.user["project"] = name
    st.session_state.paths["project"] = project_dir

    reset_dicoms()
    st.toast(f"Switched to project: {name}")

def show_session_debug() -> None:
    sac.divider(label="Debug", icon="gear", align="center", color="gray")

    st.checkbox(
        "Show Session State",
        key="ui_show_session",
        value=st.session_state.system["show_session"],
    )

    st.session_state.system["show_session"] = st.session_state.ui_show_session

    if st.session_state.system["show_session"]:
        with st.container(border=True):
            keys = sorted(k for k in st.session_state if not k.startswith("_"))
            sel = st.multiselect("State keys", keys)
            for k in sel:
                st.markdown(f"**{k}**")
                st.write(st.session_state[k])
