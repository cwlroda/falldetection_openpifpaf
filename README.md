# Fall Detection using Pose Estimation

## Introduction
Fall Detection model based on OpenPifPaf:

https://github.com/vita-epfl/openpifpaf

The detection can run on both GPU and CPU.

## Environment

- Ubuntu 18.04 x86_64
- Python 3.7.6
- USB Camera/Video/RTSP Stream

## Usage
```console
$ git clone https://github.com/cwlroda/falldetection_openpifpaf.git
$ cd falldetection_openpifpaf
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