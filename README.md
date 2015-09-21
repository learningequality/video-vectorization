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


