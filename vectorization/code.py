'''
Inputs:
This script requires the following files to run: 
1) An .mp4 Khan Academy video file named 'input.mp4'
2) A .png cursor template named 'cursor_1.png' (We will replace this requirement by dynamically looking for cursor type in a given video)
'''

'''
Outputs:
The only output file used to recontruction is 'complete_strokes.txt'
Other than that, we output some other files for debugging purposes to see what's going on in different stages of the process. 
Other output files are:
1) folder named 'objects' contains objects detected by first pass
2) folder named 'atomic objects' contains the objects further divided by connectivity
3) file named 'background.png' contains the first frame of the video (We will augment this image once the scrolling function is written)
4) file named 'cursor_positions.txt' contains cursor position for every single frame of the video
5) file named 'object_list.txt' contains the bounding box, timestamp and color of every object detected in the first pass.
'''


import numpy as np
import cv2
import os
import copy
import time

##############
##First Pass##
##############

cap = cv2.VideoCapture('input.mp4')
imageWidth = int(cap.get(cv2.cv.CV_CAP_PROP_FRAME_WIDTH))
imageHeight = int(cap.get(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT))
FPS = int(cap.get(cv2.cv.CV_CAP_PROP_FPS))
TotalFrames = int(cap.get(cv2.cv.CV_CAP_PROP_FRAME_COUNT))
templateMouse = cv2.imread('cursor_1.png',0)
templateMouse_w, templateMouse_h = templateMouse.shape[::-1]

fourcc = cv2.cv.CV_FOURCC(*'DIVX')
out = cv2.VideoWriter('output.avi',fourcc, FPS, (imageWidth,imageHeight))

thresholdMouse = 0

BlackThreshold = 24


LastValueFrame = 0
IsUserWriting = False

MouseColorValue = 0 # colored pixels in the cursor
ThresholdDrawing = 10 # extra colored pixels need in the next frame to qualify it as drawing
MaxConnectFrames = 3 # keep the drawing effect for next 5 frames, even if no drawing detected
current_connected_frame = MaxConnectFrames + 1

_debug_MissFrames = 50

ObjectsDrawn = 0
StartingFrame = 0 # - base frame, initialized when user starts drawing
frame_before_starting_1 = 0
frame_before_starting_2 = 0
frame_before_starting_3 = 0
frame_before_starting_4 = 0

LastCompleteImage = 0


font = cv2.FONT_HERSHEY_SIMPLEX

#placing rectangles

rect_start_x = []
rect_start_y = []

rect_width = []
rect_height = []

rect_time = []

count_objects_for_saving_images = 0
f_write_objects = open('object_list.txt','w')

f_write_cursor_pos_for_order_points = open('cursor positions.txt','w')

cursor_pos_before_starting = [] # store as many as last 5 cursor positions
saved_copy_of_cursor_pos_before_starting = [] # this stores a copy of cursor_pos_before_starting and uses that to write to data
cursor_pos_for_ordering = []



def getColor(image):
    #ignore black color and get the median of red, green and blue

    threshold_black = 10
    
    reds = []
    greens = []
    blues = []

    for x in range(0, image.shape[0]):
        for y in range(0, image.shape[1]):

            if image[x,y][0] > threshold_black:
                blues.append(image[x,y][0])
            if image[x,y][1] > threshold_black:
                greens.append(image[x,y][1])
            if image[x,y][2] > threshold_black:
                reds.append(image[x,y][2])

    #return [np.median(np.array(reds)), np.median(np.array(greens)), np.median(np.array(blues))]
    return [np.percentile(np.array(reds), 90), np.percentile(np.array(greens), 90), np.percentile(np.array(blues), 90)]



def RemoveMouse(gray_input):
    #Remove the cursor

    # - Use gray image created above method = 'cv2.TM_CCOEFF'
    method = 'cv2.TM_CCOEFF'

    # Apply template Matching - cursor
    res = cv2.matchTemplate(gray_input,templateMouse,cv2.TM_CCOEFF) # - one of the methods
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

    # If the method is TM_SQDIFF or TM_SQDIFF_NORMED, take minimum
    if method == 'cv2.TM_SQDIFF' or method == 'cv2.TM_SQDIFF_NORMED':
        top_left = min_loc
    else:
        top_left = max_loc

    bottom_right = (top_left[0] + templateMouse_w, top_left[1] + templateMouse_h)
    if max_val > thresholdMouse:
        cv2.rectangle(gray_input,top_left, bottom_right, (0,0,0), -1)


def CurrentMouseLocation(gray_input):
    #Find the cursor

    # - Use gray image created above method = 'cv2.TM_CCOEFF'
    method = 'cv2.TM_CCOEFF'

    # Apply template Matching - cursor
    res = cv2.matchTemplate(gray_input,templateMouse,cv2.TM_CCOEFF) # - one of the methods
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

    # If the method is TM_SQDIFF or TM_SQDIFF_NORMED, take minimum
    if method == 'cv2.TM_SQDIFF' or method == 'cv2.TM_SQDIFF_NORMED':
        top_left = min_loc
    else:
        top_left = max_loc

    bottom_right = (top_left[0] + templateMouse_w, top_left[1] + templateMouse_h)
    if max_val > thresholdMouse:
        #cv2.rectangle(gray_input,top_left, bottom_right, (0,0,0), -1)
        return (int((top_left[0] + bottom_right[0]) / 2) , int((top_left[1] + bottom_right[1]) / 2))

    return (-1,-1)


#Create Folders if not exists
if not os.path.exists('objects'):
    os.makedirs('objects')

if not os.path.exists('atomic objects'):
    os.makedirs('atomic objects')


current_frame = 0
first_frame = 0

index_of_starting_frame = 0 # - used to get the starting timestamp

gray = []

current_mouse_position = (-1, -1)

while(cap.isOpened()):
    ret, frame = cap.read()

    if ret==True:

        if current_frame == 0:
            first_frame = frame
            cv2.imwrite('background.png', first_frame)
            

        else:
            frame = cv2.subtract(frame, first_frame)

        ''' Missing Frames
        while (current_frame < _debug_MissFrames):
            ret, frame = cap.read()
            current_frame += 1
        '''


        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        if current_frame > 0:

            current_mouse_position = CurrentMouseLocation(gray)
                
            #colored_pixels = countNonBackGroundPixels(gray, BlackThreshold, LastValueFrame);

            ret,binaryImage = cv2.threshold(gray,50,255,cv2.THRESH_BINARY)

            colored_pixels = cv2.countNonZero(binaryImage)
            
            #print(colored_pixels)

            if (colored_pixels > MouseColorValue and colored_pixels - LastValueFrame > ThresholdDrawing):
                current_connected_frame = 0
                
            else:
                current_connected_frame += 1
                

            if (colored_pixels > MouseColorValue and colored_pixels - LastValueFrame > ThresholdDrawing) or (current_connected_frame < MaxConnectFrames):
                #print("Drawing")
                
                # - If user just started drawing: initialize stuff
                if IsUserWriting == False:
                    StartingFrame = frame_before_starting_4 # 5 frames old
                    index_of_starting_frame = current_frame
                    
                    #Reset Cursor Positions
                    cursor_pos_for_ordering = [] # - what about the last few cursor positions as well? if needed? - as in frame_before_starting_4,5
                    saved_copy_of_cursor_pos_before_starting = list(cursor_pos_before_starting)


                    # - start saving the new object
                
                IsUserWriting = True
                cv2.putText(frame,'Writing',(5,700), font, 1,(200,50,50),1,cv2.CV_AA)

                #Add Cursor Positions to List
                cursor_pos_for_ordering.append(current_mouse_position)
                
            else:
                

                # - If user just stopped: find out what user just drew
                if IsUserWriting == True:
                    # - Find the difference between current and starting frame
                    # - Full Final Frame
                    #cv2.imwrite('object ' + str(ObjectsDrawn) + '.png', gray)
                    # - Difference Frame
                    #cv2.imwrite('object ' + str(ObjectsDrawn) + ' diff.png', cv2.subtract(gray, StartingFrame))

                    #Get the new imge - update binary image
                    bounding_image = cv2.subtract(gray, StartingFrame)
                    
                    
                    RemoveMouse(bounding_image)

                    
                    ret,binaryDifference = cv2.threshold(bounding_image,50,255,cv2.THRESH_BINARY)

                    #Erode to get rid of small white blocks
                    kernel = np.ones((2,2),np.uint8)
                    binaryDifference = cv2.erode(binaryDifference,kernel,iterations = 1)

                    
                    
                    ObjectsDrawn += 1
                    #LastCompleteImage = frame


                    contours, hierarchy = cv2.findContours(binaryDifference,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)

                    x1 = 1000 # - big value
                    y1 = 1000 # - big value

                    x2 = 0 # - small value
                    y2 = 0 # - small value

                    for i in range(0, len(contours)):
                        x,y,w,h = cv2.boundingRect(contours[i])
                        #cv2.rectangle(img,(x,y),(x + w,y + h),(255,0,0),1)
                        if x < x1:
                            x1 = x
                        if y < y1:
                            y1 = y
                        if x + w > x2:
                            x2 = x + w
                        if y + h > y2:
                            y2 = y + h
        

                    #cv2.rectangle(img,(x1,y1),(x2,y2),(0,255,0),1)

                    if x1 - 4 > 0 and x2 + 4 < imageWidth and y1 - 4 > 0 and y2 + 4 < imageHeight and x2 - x1 > 0 and y2 - y1 > 0:
                        
                        rect_start_x.append(x1 - 4)
                        rect_start_y.append(y1 - 4)

                        rect_width.append(x2 + 4)
                        rect_height.append(y2 + 4)

                        _time = round(1.0 * current_frame * FPS / TotalFrames, 2)
                        _starting_time = round(1.0 * index_of_starting_frame * FPS / TotalFrames, 2) # - to save the time when the first frame was registered
                        rect_time.append(_time)

                        
                        ROI = frame[y1 - 4:y2 + 4, x1 - 4:x2 + 4]

                        #Get Color of Object
                        [r, g, b] = getColor(ROI)
                        r = int(r)
                        g = int(g)
                        b = int(b)
                        
                        cv2.imwrite('objects/' + str(count_objects_for_saving_images) + '.png', ROI)
                        count_objects_for_saving_images += 1

                        f_write_objects.write(str(x1 - 4) + ' ' + str(y1 - 4) + ' ' + str(_starting_time) + ' ' + str(_time) + ' '  + str(r)  + ' '  + str(g) + ' ' + str(b) + '\n')

                        

                        #Cursor positions before starting of the objects: in order to get the very starting points that are missing otherwise
                        for i in saved_copy_of_cursor_pos_before_starting:
                            f_write_cursor_pos_for_order_points.write(str(i[0] - (x1 - 4)) + " " + str(i[1] - (y1 - 4)) + ' ')
                            #print (str(i[0] - (x1 - 4)) + " " + str(i[1] - (y1 - 4)) + ' ')

                        for i in cursor_pos_for_ordering:
                            f_write_cursor_pos_for_order_points.write(str(i[0] - (x1 - 4)) + " " + str(i[1] - (y1 - 4)) + ' ')

                        f_write_cursor_pos_for_order_points.write('\n')

                        #Reset Cursor Positions
                        cursor_pos_for_ordering = []



                # Reset to false
                cv2.putText(frame,'Not Writing',(5,700), font, 1,(50,50,200),1,cv2.CV_AA)
                IsUserWriting = False
        

        if current_frame > 0:

            LastValueFrame = colored_pixels
            frame_before_starting_4 = frame_before_starting_3
            frame_before_starting_3 = frame_before_starting_2
            frame_before_starting_2 = frame_before_starting_1
            frame_before_starting_1 = gray

            #Storing the last few (5) cursor locations, since we seem to miss that information when we realize that new object has started
            if (len(cursor_pos_before_starting) < 5):
                cursor_pos_before_starting.append(current_mouse_position)
            else:
                cursor_pos_before_starting.pop(0)
                cursor_pos_before_starting.append(current_mouse_position)


            

            # - Drawing rectangles
            for i in range(0, len(rect_start_x)):
                _loc = 'x = ' + str(rect_start_x[i]) + ', y = ' + str(rect_start_y[i]) + ', '
                _size = 'width = ' + str(rect_width[i] - rect_start_x[i]) + ', height = ' + str(rect_height[i] - rect_start_y[i]) + ', '
                _time = 'time: ' + str(rect_time[i])
                cv2.rectangle(frame,(rect_start_x[i],rect_start_y[i]),(rect_width[i],rect_height[i]),(256,0,0),2)
                cv2.putText(frame,_loc + _size + _time,(800,20 + i *13), font, 0.45,(50,50,200),1,cv2.CV_AA)
                


            final_frame = cv2.add(frame, first_frame)
            out.write(final_frame)
            #cv2.imshow('frame',gray)


            
            

        current_frame += 1

        #print current_frame

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    else:
        break

f_write_objects.close()
f_write_cursor_pos_for_order_points.close()

cap.release()
out.release()
cv2.destroyAllWindows()

print 'Part 1 Completed!'


###############
##Second Pass##
###############

# Get total_objects from last part
total_objects = count_objects_for_saving_images



for object_number in range(0, total_objects):

    image = cv2.imread('objects/' + str(object_number) + '.png')

    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    binary_threshold = 50
    ret,bw_image = cv2.threshold(gray_image,binary_threshold,255,0)
    contour_image = copy.deepcopy(bw_image)
    contours, hierarchy = cv2.findContours(contour_image,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)

    #cv2.drawContours(image,contours,-1,(0,255,0),3)

    for i in range(0, len(contours)):
        x,y,w,h = cv2.boundingRect(contours[i])
        #cv2.rectangle(image,(x,y),(x+w,y+h),(0,255,0),1)
        #cv2.imshow(str(i), image)
        mask = np.zeros(image.shape,np.uint8)
        mask[y:y+h,x:x+w] = image[y:y+h,x:x+w]
        cv2.imwrite('atomic objects/' + str(object_number) + '_' + str(i) + '.png', mask)
        #cv2.imshow(str(i), mask);
        #print 'here'


#color_img = cv2.cvtColor(bw_image, cv2.COLOR_GRAY2BGR)

#enlarge = cv2.resize(image, (0,0), fx=4, fy=4) 
#cv2.imshow("image", enlarge);

cv2.waitKey(0)
cv2.destroyAllWindows()

print 'Part 2 Completed!'

##############
##Third Pass##
##############

# Get total_objects from last part
total_objects = count_objects_for_saving_images

#Read Cursor positions
f = open('cursor positions.txt', 'r')
data = f.read().split('\n')
f.close()


#Read Object List File
f = open('object_list.txt', 'r')
objects = f.read().split('\n')
f.close()


#Write Output File
f_output = open('complete_strokes.txt', 'w')

object_number = 0
for object_number in range(0, total_objects):
#if 1 == 1:

    valid_cursors = []

    #Get cursor positions for this group of images
    cursor_pos = []
    obj1 = data[object_number].split(' ')
    for x,y in zip(obj1[0::2], obj1[1::2]):
        cursor_pos.append((x, y))

    prefixed = [filename for filename in os.listdir('atomic objects/') if filename.startswith(str(object_number) + '_')]

    for connected_image in prefixed:

        

        image = cv2.imread('atomic objects/' + connected_image)

        gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        binary_threshold = 50
        ret,img = cv2.threshold(gray_image,binary_threshold,255,0)

        color_img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)


        def IsNeighbourText(y, x, binary_threshold):
            if img[y, x] > binary_threshold or (y + 1 < dim[1] and img[y + 1, x] > binary_threshold) or (y - 1 >= 0 and img[y - 1, x] > binary_threshold) or (x + 1 < dim[0] and img[y, x + 1] > binary_threshold) or (x + 1 < dim[0] and y + 1 < dim[1] and img[y + 1, x + 1] > binary_threshold) or (y - 1 >= 0 and x + 1 < dim[0] and img[y - 1, x + 1] > binary_threshold) or (x - 1 >= 0 and img[y, x - 1] > binary_threshold) or (y + 1 < dim[1] and x - 1 >= 0 and img[y + 1, x - 1] > binary_threshold) or (y - 1 >=0 and x - 1 >= 0 and img[y - 1, x - 1] > binary_threshold):
                return True
            else:
                return False

        
        #Find Valid Cursor Positions
        count_valid_cursor_positions = 0
        #Append valid cursors in this local list
        valid_cursor_local = []
        for i in range(0, len(cursor_pos)):
            x = int(cursor_pos[i][0])
            y = int(cursor_pos[i][1])
            last_x = -100
            last_y = -100
            if i > 0:
                last_x = int(cursor_pos[i - 1][0])
                last_y = int(cursor_pos[i - 1][1])
                
            dim = img.shape[1::-1]

            if x >= 0 and y >= 0 and x < dim[0] and y < dim[1]:
                if IsNeighbourText(y, x, binary_threshold) and (abs(x - last_x) + abs(y - last_y)) > 3:
                    cv2.circle(color_img,(x, y), 1, (0,0,255))
                    count_valid_cursor_positions += 1
                    valid_cursor_local.append(cursor_pos[i])

        #print count_valid_cursor_positions

        #Add Connected Object only if it has at least one valid cursor position
        if len(valid_cursor_local) > 0:
            valid_cursors.append(valid_cursor_local)
        

        enlarge = cv2.resize(color_img, (0,0), fx=4, fy=4) 
        #cv2.imshow(connected_image, enlarge);


    #Find the order of the connected blocks among each other

    order = [0] * len(valid_cursors)
    counter = 0
    for i in cursor_pos:
            for j in range(0, len(valid_cursors)):
                    if valid_cursors[j][0] == i:
                            order[counter] = j
                            counter += 1
                            if counter == len(valid_cursors):
                                break
                            
            if counter == len(valid_cursors):
                break
                            

    #ordered_sub_objects contains the list of ordered sub objects
    ordered_sub_objects = []
    for i in order:
            ordered_sub_objects.append(valid_cursors[i])

    
    #Write to output File
    f_output.write(objects[object_number] + '\n')
    f_output.write(str(len(ordered_sub_objects)) + '\n')

    output = ""
    for i in range(0, len(ordered_sub_objects)):
        for j in range(0, len(ordered_sub_objects[i])):
            output += (ordered_sub_objects[i][j][0] + " " + ordered_sub_objects[i][j][1]) + " "
        output += '\n'

        
    f_output.write(output)
    

f_output.close()


cv2.waitKey(0)
cv2.destroyAllWindows()

print 'Part 3 Completed!'

print 'Done!'
