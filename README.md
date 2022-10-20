# repo-team5

### Out of Distribution NAS

Getting started:

1. SSH into pace cluster `[gt_userid]@coc-ice.pace.gatech.edu`
2. load anaconda `module load anaconda3` (default is latest)
3. if first time, create conda env: `conda create -n ood-nas`
4. activate conda env: `conda activate ood-nas`
5. install the following:
  - `conda install pytorch torchvision torchaudio cudatoolkit=11.6 -c pytorch -c
    conda-forge`
  - `conda install -c conda-forge cvxpy`
  - `conda install -c mosek mosek`
  - `conda install -c conda-forge tensorboardx`

6. change the account in `.pbs` file and submit job to cluster `qsub OoD-NAS/test_run.pbs`
7. check status of job & also check `test-pace-1.out` for stderr and stdout.

[pace cheatsheet](https://docs.pace.gatech.edu/gettingStarted/commands/)

[pace docs](https://docs.pace.gatech.edu/ice_cluster/ice-guide/)

----- From original readme

### Prerequisites

Python3.6. and the following packages are required to run the scripts:

- Python >= 3.7

- PyTorch >= 1.1 and torchvision

- CVXPY

- Mosek

### Code Structure

 - train_search_single.py
 - nas_ood_single
 - dataloader


### Demonstrations on NICO

bash main_search_onestage.sh


### References
```
@inproceedings{bai2021ood,
  title={Nas-ood: Neural architecture search for out-of-distribution generalization},
  author={Bai, Haoyue and Zhou, Fengwei and Hong, Lanqing and Ye, Nanyang and Chan, S-H Gary and Li, Zhenguo},
  booktitle={Proceedings of the IEEE/CVF International Conference on Computer Vision},
  year={2021}
}
```

