# Video Vectorization

## Running Vectorization Side

### Setup
* OS: Ubuntu 14.04
* Video Card: NVIDIA 980 ti

### Basic Dependencies.
* Python 2.7
* pip

#### Install drivers.
* Add NVIDIA drivers PPA `sudo add-apt-repository ppa:graphics-drivers/ppa` and install the appropritate one, currently version 367.27.
* Install the [CUDA Toolkit](https://developer.nvidia.com/cuda-downloads) by following the [CUDA Quick Start Guide](http://developer.download.nvidia.com/compute/cuda/7.5/Prod/docs/sidebar/CUDA_Quick_Start_Guide.pdf). TLDR:
    1. Install the the CUDA toolkit by using the debian installer.
    2. Reboot.
    3. Modify the PATH and LD_LIBRARY_PATH BY running the following commands:
        * `export PATH=/usr/local/cuda-7.5/bin:$PATH`
        * `export LD_LIBRARY_PATH=/usr/local/cuda-7.5/lib64:$LD_LIBRARY_PATH`
    4. Test that the everything is installed correctly by running this [test script]().
#### Install OpenCV


1. Make sure you have Python 2.7 and pip installed.

3. Install OpenCV 2 by follwing [this guide](https://medium.com/@manuganji/installation-of-opencv-numpy-scipy-inside-a-virtualenv-bf4d82220313#.m6i6da6er) to make sure it works with your virtual environment.
3. Install dependencies by running `pip install requirements.txt`
4. Enter vectorization folder by running `cd vectorization/ `
4. Run `python vectorization.py`

Ubuntu 14.04
Did not work on 16.*
sudo add-apt-repository ppa:graphics-drivers/ppa
sudo apt-get update
Restart and select latest driver from the additonal drivers manager.
https://developer.nvidia.com/cuda-downloads
http://developer.download.nvidia.com/compute/cuda/7.5/Prod/docs/sidebar/CUDA_Quick_Start_Guide.pdf
run bash test.sh to check it cuda is installed
nvcc test.cu and run a.out

cmake -D MAKE_BUILD_TYPE=RELEASE -D CMAKE_INSTALL_PREFIX=$VIRTUAL_ENV/local/ -D PYTHON_EXECUTABLE=$VIRTUAL_ENV/bin/python -D PYTHON_PACKAGES_PATH=$VIRTUAL_ENV/lib/python2.7/site-packages ..\


Make sure ou have libxml2-dev installed

## Viewing Rendering Side
Open rendering/index.html in a browser.
[View a demo here.](https://rawgit.com/christianmemije/video-vectorization/master/rendering/index.html)

### Sample JSON File

```javascript
{
    "filename" : "video_xyz.json"
    "interpolation": "linear",
    "cursor_type": "cursor_type_A.png",
    "cursor_offset": [5,5],
    "duration" : "140",
    "audio_file" : "compressed_xyz.mp3",
    "background_image" : "background.png"
    "frames_per_second" : "15"
    "cursor":
    [
        [[3,3], [8,10], [-1, -1], ...for every frame, without timestamps
    ],
    "operations":  + (drawing and rest)
    [
        {
            "offset_x" : 30,
            "offset_y" : 100,
            "start": 5.3,
            "end": 7.4,
            "color": "#336699" or (r, g, b)
            "strokes":  [[[1,12], [1,41], [5,18]][[3,16], [31,12], [2,8]][[7,112], [151,6], [1,11]] ...]
        }

        {
            "offset_x" : 35,
            "offset_y" : 120,
            "start": 8.4,
            "end": 11.1,
            "color": "#FF0000"
            "strokes":  [[[11,22], [63,44], [52,65]][[13,23], [15,25], [1,18]] ...]
        }

    ]

}
```
