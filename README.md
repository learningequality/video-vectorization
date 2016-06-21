# video-vectorization

Python Code: 
For the actual code, open [vectorization/code.py]

##########
##Inputs##
##########

Code.py script needs the following files as input: 
1) A .mp4 blackboard-style video file named 'input.mp4'
2) A .png cursor template named 'cursor_1.png' (We will replace this requirement by dynamically looking for cursor type in a given video)

###########
##Outputs##
###########

The only output file used to recontruction is 'complete_strokes.txt'
Other than that, we output some other files for debugging purposes to see what's going on in different stages of the process. 
Other output files are:
1) folder named 'objects' contains objects detected by first pass
2) folder named 'atomic objects' contains the objects further divided by connectivity
3) file named 'background.png' contains the first frame of the video (We will augment this image once the scrolling function is written)
4) file named 'cursor_positions.txt' contains cursor position for every single frame of the video
5) file named 'object_list.txt' contains the bounding box, timestamp and color of every object detected in the first pass.

########
##Demo##
########

Small Demo: http://icanmakemyownapp.com/ka_lite
Updated Demo: icanmakemyownapp.com/ka_lite_updated/?id=1 


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


///////////////////////////////////
Comments about the JSON Structure//
bounding box of objects		 //
max min, bounding box of objects //
no commas			 //
no nested objects in cursor	 //
///////////////////////////////////
