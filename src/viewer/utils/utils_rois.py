from dataclasses import dataclass, field
from typing import List, Optional, Dict
import pandas as pd
from pathlib import Path

@dataclass(frozen=True)
class ROI:
    index: int
    name: str
    components: Optional[List[int]] = None
    """
        [5, 8, 10]  → derived ROI composed of other ROI indices
    """

    @property
    def is_derived(self) -> bool:
        if not self.components:
            return False
        return len(self.components)>1

@dataclass
class RoiAtlas:
    name: str
    rois: Dict[int, ROI]                  # index → ROI
    name_to_index: Dict[str, int]          # name → index

    def get_by_index(self, index: int) -> ROI:
        try:
            return self.rois[index]
        except:
            return None

    def get_by_name(self, name: str) -> ROI:
        try:
            return self.rois[self.name_to_index[name]]
        except:
            return None

    def is_derived(self, index: int) -> bool:
        try:
            return self.rois[index].is_derived
        except:
            return False

def load_muse_atlas(roi_list_csv: Path, derived_csv: Path) -> RoiAtlas:
    '''
    Read ROI lists for MUSE to RoiAtlas object
    '''
    # --- Load base ROI list ---
    df_rois = pd.read_csv(roi_list_csv)
    rois: Dict[int, ROI] = {}
    name_to_index: Dict[str, int] = {}
    for _, row in df_rois.iterrows():
        idx = int(row["Index"])
        name = str(row["Name"])
        rois[idx] = ROI(index=idx, name=name)
        name_to_index[name] = idx

    # --- Load derived ROIs ---
    df_derived = pd.read_csv(derived_csv)
    for _, row in df_derived.iterrows():
        parent_idx = int(row[0])
        components = [int(x) for x in row[2:] if pd.notna(x)]
        rois[parent_idx] = ROI(index=parent_idx, name=rois[parent_idx].name, components=components)

    return RoiAtlas(
        name="MUSE",
        rois=rois,
        name_to_index=name_to_index,
    )
