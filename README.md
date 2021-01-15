# AutoMatteProcessor

A script that makes it easier to run batch matte generation using the BackgroundMattingV2 repo

## Getting Started

### Dependencies

- [Python 3.7](https://www.python.org/downloads/release/python-379/)
- [CUDA 11.0](http://developer.download.nvidia.com/compute/cuda/11.0.2/local_installers/cuda_11.0.2_451.48_win10.exe)

### First Time Setup

- Install the above dependencies
- Clone the BackgroundMattingV2 submodule
	- `git submodule update --init`
- Install the python dependencies
	- `$ pip install -r ./requirements.txt -f https://download.pytorch.org/whl/torch_stable.html`

## Usage

This script processes *all* videos in a given directory containing a corresponding background PNG file.
For example, if a directory contains the video `foo.mp4` and the background image `foo.png` it will process these into `foo_matte.mp4`. If the background image is missing, or the matte video already exists, the video file will be skipped.

To run the script:

`$ python ProcessDirectory.py <input directory>`
