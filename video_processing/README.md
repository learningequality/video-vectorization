# Video stream processing for vectorization

A simple framework for processing video files using units called processors
that operate on streams of video frames and other objects.

##Setup on mac
Minimal footprint at the system level by using virtualenv.
```sh
sudo easy_install pip
pip install --user --upgrade virtualenv
~/Library/Python/2.7/bin/virtualenv video-vectorization
source video-vectorization/bin/activate
pip install --upgrade python-igraph numpy opencv-contrib-python six absl-py
```

## Setup on Debian-based Linux distros
```sh
sudo apt install virtualenv python3-venv libxml2-dev
pip install --user --upgrade virtualenv
virtualenv video_vectorization
source video-vectorization/bin/activate
pip install --upgrade python-igraph numpy opencv-contrib-python six absl-py
```

## Example run
```sh
cd video-vectorization
python video_processing/pipelines/vectorization_v1.py --input_video_file vectorization/exponents.mp4 --cursor_template_file vectorization/cursor_1.png
python video_processing/pipelines/render_vector_video.py --input_json_file data.json --background_image_file background.png --output_video_file test.avi
```
