# ManiSkill-HAB

This is an anonymized version of the ManiSkill-HAB. Currently under double-blind review as a conference paper at ICLR 2025.

## Reproducibility

In this repo, we include the environment, training, evaluation, and dataset generation code. We also upload necessary data anonymously to HuggingFace.

However, at the time of this release, the demonstration dataset (~500GB) is uploading. In the meantime, users can generate their own data.

## Installation

To set up, please run the below steps. Please note that `git lfs` is needed for this version of the repo.
```
conda create -n mshab python=3.9
conda activate mshab

curl -L "https://huggingface.co/datasets/ms-hab/ManiSkill-fork/resolve/main/ms-fork.zip" -o ms-fork.zip && unzip ms-fork.zip && mv ms-fork ManiSkill && rm ms-fork.zip
pip install -e ManiSkill

pip install tensorboard \
    tensorboardX \
    gymnasium \
    omegaconf \
    dacite \
    wandb \
    mujoco \
    coacd \
    shortuuid \
    kornia \
    fast_kinematics==0.1.11 \
    IPython

bash anonymized_asset_download/download_asset.sh

git lfs pull
```

For benchmarking, please see the steps listed in [bench/README.md](./bench/README.md).