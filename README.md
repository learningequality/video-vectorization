# Video Vectorization

## Running Vectorization Side
### Recommended Setup
1. Make sure you have Python 2.7 and pip installed.
2. Create a Python virtual enviornment with something like [virtualenvwrapper](https://virtualenvwrapper.readthedocs.io/en/latest/).
3. Install OpenCV 2 by follwing [this guide](https://medium.com/@manuganji/installation-of-opencv-numpy-scipy-inside-a-virtualenv-bf4d82220313#.m6i6da6er) to make sure it works with your virtual enviornment.
3. Run `pip install requirements.txt`
4. Run `python vectorization/vectorization.py`

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
