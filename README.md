# Video Vectorization

## Running Vectorization Side
1. Make sure you have Python, pip, and OpenCV installed.
2. Create a Python virtual enviornment with something like [virtualenvwrapper](https://virtualenvwrapper.readthedocs.io/en/latest/).
3. Run `pip install requirements.txt`
4. Run `python vectorization/vectorization.py`

## Viewing Rendering Side
Open rendering/index.html in a browser.

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

## Notes
### TODO
* Comments about the JSON Structure
* bounding box of objects
* max min, bounding box of objects
* no commas
* no nested objects in cursor

### Inputs
Code.py script needs the following files as input: 

1. A .mp4 blackboard-style video file named 'input.mp4'

2. A .png cursor template named 'cursor_1.png' (We will replace this requirement by dynamically looking for cursor type in a given video)

### Outputs
The only output file used to recontruction is 'complete_strokes.txt'. Other than that, we output some other files for debugging purposes to see what's going on in different stages of the process. 
Other output files are:

1. folder named 'objects' contains objects detected by first pass

2. folder named 'atomic objects' contains the objects further divided by connectivity

3. file named 'background.png' contains the first frame of the video (We will augment this image once the scrolling function is written)

4. file named 'cursor_positions.txt' contains cursor position for every single frame of the video

5. file named 'object_list.txt' contains the bounding box, timestamp and color of every object detected in the first pass.

### Optimizations
1. Simple frame difference adds noise in the resulting image. Lossy codec distorts the pixel values. New Logic: Filter out any difference that is less than n (n = 20) on the grayscale [0-255].

2. Find the type of cursor in a video by looking at 3 consecutive frames and save the cursor image. Look at all the possible cursor types in the video. Will also be helpful for processing unknown video.

3. For cursor template matching stage, first look for the cursor within a small box in close vicinity to the cursor position in last frame. If the matching fails (below certain threshold), look in the complete frame
