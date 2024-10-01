"""
Asset sources and tooling for managing the assets
"""

import os
from dataclasses import dataclass
from typing import Dict, List, Optional

from mani_skill import ASSET_DIR, PACKAGE_ASSET_DIR
from mani_skill.utils import io_utils


@dataclass
class DataSource:
    source_type: str
    """what kind of data is this"""
    url: Optional[str] = None
    hf_repo_id: Optional[str] = None
    github_url: Optional[str] = None
    target_path: Optional[str] = None
    """the folder where the file will be downloaded to"""
    checksum: Optional[str] = None
    zip_dirname: Optional[str] = None
    """what to rename a zip files generated directory to"""
    filename: Optional[str] = None
    """name to change the downloaded file to. If None, will not change the name"""
    output_dir: str = ASSET_DIR


DATA_SOURCES: Dict[str, DataSource] = {}
"""Data sources map data source IDs to their respective DataSource objects which contain info on what the data is and where to download it"""
DATA_GROUPS: Dict[str, List[str]] = {}
"""Data groups map group ids (typically environment IDs) to a list of data source/group IDs for easy group management. data groups can be done hierarchicaly"""


def is_data_source_downloaded(data_source_id: str):
    data_source = DATA_SOURCES[data_source_id]
    return os.path.exists(data_source.output_dir / data_source.target_path)


def initialize_data_sources():
    DATA_SOURCES["ycb"] = DataSource(
        source_type="task_assets",
        url="https://huggingface.co/datasets/haosulab/ManiSkill2/resolve/main/data/mani_skill2_ycb.zip",
        target_path="assets/mani_skill2_ycb",
        checksum="174001ba1003cc0c5adda6453f4433f55ec7e804f0f0da22d015d525d02262fb",
    )
    DATA_SOURCES["pick_clutter_ycb_configs"] = DataSource(
        source_type="task_assets",
        url="https://storage1.ucsd.edu/datasets/ManiSkill2022-assets/pick_clutter/ycb_train_5k.json.gz",
        target_path="tasks/pick_clutter",
        checksum="70ec176c7036f326ea7813b77f8c03bea9db5960198498957a49b2895a9ec338",
    )
    # ---------------------------------------------------------------------------- #
    # Interactable Scene Datasets
    # ---------------------------------------------------------------------------- #
    DATA_SOURCES["ReplicaCAD"] = DataSource(
        source_type="scene",
        hf_repo_id="ms-hab/ReplicaCAD",
        target_path="scene_datasets/replica_cad_dataset",
    )

    DATA_SOURCES["ReplicaCADRearrange"] = DataSource(
        source_type="scene",
        url="https://huggingface.co/datasets/ms-hab/ReplicaCADRearrange/resolve/main/rearrange.zip",
        target_path="scene_datasets/replica_cad_dataset/rearrange",
    )


def expand_data_group_into_individual_data_source_ids(data_group_id: str):
    """Expand a data group into a list of individual data source IDs"""
    uids = []

    def helper(uid):
        nonlocal uids
        if uid in DATA_SOURCES:
            uids.append(uid)
        elif uid in DATA_GROUPS:
            [helper(x) for x in DATA_GROUPS[uid]]

    for uid in DATA_GROUPS[data_group_id]:
        helper(uid)
    uids = list(set(uids))
    return uids


initialize_data_sources()
