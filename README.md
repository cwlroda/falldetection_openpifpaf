# Fall Detection using Pose Estimation

## Introduction
Fall Detection model based on OpenPifPaf:

https://github.com/vita-epfl/openpifpaf

https://pypi.org/project/openpifpaf/

https://openaccess.thecvf.com/content_CVPR_2019/html/Kreiss_PifPaf_Composite_Fields_for_Human_Pose_Estimation_CVPR_2019_paper.html

The detection can run on both GPU and CPU, but GPU has been intentionally disabled to run tests solely on CPU.

## Environment

- Ubuntu 18.04 x86_64
- Python 3.7.6
- Anaconda 3
- USB Camera/Video/RTSP Stream

## Usage
```console
$ git clone https://github.com/cwlroda/falldetection_openpifpaf.git
```
**Download OpenPifPaf 0.11.8 (PyPI)**
```console
$ pip3 install openpifpaf
```
**Copy Source Files**
```console
$ cd {home_dir}/anaconda3/lib/python3.7/site-packages/openpifpaf
Replace ALL files in that folder with the files in this repository
```
**Setup Conda Environment**
```console
$ conda create --name falldetection_openpifpaf python=3.7.6
$ conda activate falldetection_openpifpaf
```
**Prerequisites**
```console
$ pip3 install -r requirements.txt
```
**Execution**
```console
$ python3 -m openpifpaf.video --show
$ (use --help to see the full list of command line arguments)
```
