# coding=utf-8
import copy
import itertools
import json
import math
import cv2
import numpy as np
import os
from igraph import Graph
from scipy import weave


def get_color(image):
    # ignore black color and get the median of red, green and blue

    threshold_black = 10
    reds = []
    greens = []
    blues = []

    for x in range(0, image.shape[0]):
        for y in range(0, image.shape[1]):

            if image[x, y][0] > threshold_black:
                blues.append(image[x, y][0])
            if image[x, y][1] > threshold_black:
                greens.append(image[x, y][1])
            if image[x, y][2] > threshold_black:
                reds.append(image[x, y][2])

    # return [np.median(np.array(reds)), np.median(np.array(greens)),
    # np.median(np.array(blues))]
    return [np.percentile(np.array(reds), 90),
            np.percentile(np.array(greens), 90),
            np.percentile(np.array(blues), 90)]


def remove_cursor(gray_input, template_mouse, template_mouse_w,
                  template_mouse_h, threshold_mouse):
    # Remove the cursor
    # - Use gray image created above method = 'cv2.TM_CCOEFF'
    method = 'cv2.TM_CCOEFF'
    # Apply template Matching - cursor
    res = cv2.matchTemplate(gray_input, template_mouse, cv2.TM_CCOEFF)
    # - one of the methods
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

    # If the method is TM_SQDIFF or TM_SQDIFF_NORMED, take minimum
    if method == 'cv2.TM_SQDIFF' or method == 'cv2.TM_SQDIFF_NORMED':
        top_left = min_loc
    else:
        top_left = max_loc

    bottom_right = (top_left[0] + template_mouse_w, top_left[1] +
                    template_mouse_h)

    if max_val > threshold_mouse:
        cv2.rectangle(gray_input, top_left, bottom_right, (0, 0, 0), -1)


def get_current_mouse_location(gray_input, frame_number, template_mouse,
                               template_mouse_w, template_mouse_h,
                               threshold_mouse):
    # Find the cursor
    # - Use gray image created above method = 'cv2.TM_CCOEFF'
    method = 'cv2.TM_CCOEFF'
    # Apply template Matching - cursor
    res = cv2.matchTemplate(gray_input, template_mouse, cv2.TM_CCOEFF)
    # - one of the methods
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

    # If the method is TM_SQDIFF or TM_SQDIFF_NORMED, take minimum
    if method == 'cv2.TM_SQDIFF' or method == 'cv2.TM_SQDIFF_NORMED':
        top_left = min_loc
    else:
        top_left = max_loc

    bottom_right = (top_left[0] + template_mouse_w, top_left[1] +
                    template_mouse_h)

    if max_val > threshold_mouse:
        # cv2.rectangle(gray_input,top_left, bottom_right, (0,0,0), -1)
        return frame_number, int((top_left[0] + bottom_right[0]) / 2), int(
            (top_left[1] + bottom_right[1]) / 2)

    return frame_number, -1, -1


def thinning_iteration(im, iter):
    I, M = im, np.zeros(im.shape, np.uint8)

    expr = """
    for (int i = 1; i < NI[0]-1; i++) {
        for (int j = 1; j < NI[1]-1; j++) {
            int p2 = I2(i-1, j);
            int p3 = I2(i-1, j+1);
            int p4 = I2(i, j+1);
            int p5 = I2(i+1, j+1);
            int p6 = I2(i+1, j);
            int p7 = I2(i+1, j-1);
            int p8 = I2(i, j-1);
            int p9 = I2(i-1, j-1);
            int A  = (p2 == 0 && p3 == 1) + (p3 == 0 && p4 == 1) +
                     (p4 == 0 && p5 == 1) + (p5 == 0 && p6 == 1) +
                     (p6 == 0 && p7 == 1) + (p7 == 0 && p8 == 1) +
                     (p8 == 0 && p9 == 1) + (p9 == 0 && p2 == 1);
            int B  = p2 + p3 + p4 + p5 + p6 + p7 + p8 + p9;
            int m1 = iter == 0 ? (p2 * p4 * p6) : (p2 * p4 * p8);
            int m2 = iter == 0 ? (p4 * p6 * p8) : (p2 * p6 * p8);
            if (A == 1 && B >= 2 && B <= 6 && m1 == 0 && m2 == 0) {
                M2(i,j) = 1;
            }
        }
    }
    """

    weave.inline(expr, ["I", "iter", "M"])
    return I & ~M


def thin(src):
    dst = src.copy() / 255
    prev = np.zeros(src.shape[:2], np.uint8)

    while True:
        dst = thinning_iteration(dst, 0)
        dst = thinning_iteration(dst, 1)
        diff = np.absolute(dst - prev)
        prev = dst.copy()
        if np.sum(diff) == 0:
            break

    return dst * 255


def is_neighbor_text(x, y, binary_threshold, img, dim):
    # return True # - just to show all cursor locations
    if ((img[y, x] > binary_threshold) or
            (y + 1 < dim[1] and img[y + 1, x] > binary_threshold) or
            (y - 1 >= 0 and img[y - 1, x] > binary_threshold) or
            (x + 1 < dim[0] and img[y, x + 1] > binary_threshold) or
            (x + 1 < dim[0] and y + 1 < dim[1] and img[y + 1, x + 1] >
                binary_threshold) or
            (y - 1 >= 0 and x + 1 < dim[0] and img[y - 1, x + 1] >
                binary_threshold) or
            (x - 1 >= 0 and img[y, x - 1] > binary_threshold) or
            (y + 1 < dim[1] and x - 1 >= 0 and img[y + 1, x - 1] >
                binary_threshold) or
            (y - 1 >= 0 and x - 1 >= 0 and img[y - 1, x - 1] >
                binary_threshold)):
        return True
    else:
        return False


def find_closest_point(node, nodes):
    nodes = np.asarray(nodes)
    dist_2 = np.sum((nodes - node) ** 2, axis=1)
    return nodes[np.argmin(dist_2)]


def compute_all_edges(data_pts):
    graph_connections = []

    for current in range(0, len(data_pts)):
        adjacent = [data_pts.index(_x) for _x in data_pts if
                    (abs(_x[0] - data_pts[current][0]) < 2) and
                    (abs(_x[1] - data_pts[current][1]) < 2) and
                    (_x[0] != data_pts[current][0] or _x[1] !=
                     data_pts[current][1])]

        for _a in adjacent:
            graph_connections.append((current, _a))
            # print "connection: " + str(current) + " : " + str(_a)

    # Remove duplicates
    list_with_duplicates = sorted([sorted(_x) for _x in graph_connections])
    result = list(list_with_duplicates for list_with_duplicates, _ in
                  itertools.groupby(list_with_duplicates))
    # print result
    return result


def check_if_collinear(a, b, c):
    diff = (((int(a[1]) - int(b[1])) * (int(a[0]) - int(c[0]))) -
            ((int(a[1]) - int(c[1])) * (int(a[0]) - int(b[0]))))
    return diff <= 1e-9


def reduce_points(unreduced_list):
    new_list = unreduced_list[:]

    for point in range(len(unreduced_list) - 2):
        if check_if_collinear(unreduced_list[point], unreduced_list[point + 1],
                              unreduced_list[point + 2]):
            new_list[point + 1] = ''

    return new_list


def part_one(input_video, cursor_filename, background_image,
             count_objects_for_saving_images, json_operation_log,
             json_cursor_log, template_mouse_w, template_mouse_h,
             total_frames, fps):
    output_video = 'output.avi'
    cap = cv2.VideoCapture(input_video)
    image_width = int(cap.get(cv2.cv.CV_CAP_PROP_FRAME_WIDTH))
    image_height = int(cap.get(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT))
    fps = int(cap.get(cv2.cv.CV_CAP_PROP_FPS))
    total_frames = int(cap.get(cv2.cv.CV_CAP_PROP_FRAME_COUNT))
    template_mouse = cv2.imread(cursor_filename, 0)
    template_mouse_w, template_mouse_h = template_mouse.shape[::-1]
    fourcc = cv2.cv.CV_FOURCC(*'DIVX')
    out = cv2.VideoWriter(output_video, fourcc, fps,
                          (image_width, image_height))
    threshold_mouse = 0
    black_threshold = 24
    last_value_frame = 0
    is_user_writing = False
    mouse_color_value = 0  # colored pixels in the cursor
    threshold_drawing = 10
    # extra colored pixels need in the next frame to qualify it as drawing
    max_connect_frames = 3
    # keep the drawing effect for next 5 frames, even if no drawing detected
    current_connected_frame = max_connect_frames + 1
    threshold_erasure = 50  # threshold to detect erasure operation
    debug_miss_frames = 50
    objects_drawn = 0
    starting_frame = 0  # - base frame, initialized when user starts drawing
    frame_before_starting_1 = 0
    frame_before_starting_2 = 0
    frame_before_starting_3 = 0
    frame_before_starting_4 = 0
    last_complete_image = 0
    font = cv2.FONT_HERSHEY_SIMPLEX
    # placing rectangles
    rect_start_x = []
    rect_start_y = []
    rect_width = []
    rect_height = []
    rect_time = []

    f_write_objects = open('object_list.txt', 'w')
    f_write_cursor_pos_for_order_points = open('cursor positions.txt', 'w')
    f_write_cursor_general = open('cursor_general.txt', 'w')
    cursor_pos_before_starting = []  # store as many as last 5 cursor positions
    # this stores a copy of cursor_pos_before_starting and uses that to write
    # to data
    saved_copy_of_cursor_pos_before_starting = []
    cursor_pos_for_ordering = []

    # Create Folders if not exists
    if not os.path.exists('objects'):
        os.makedirs('objects')
    if not os.path.exists('atomic objects'):
        os.makedirs('atomic objects')

    current_frame = 0
    first_frame = 0
    index_of_starting_frame = 0  # - used to get the starting timestamp
    gray = []
    current_mouse_position = (-1, -1)

    while cap.isOpened():
        ret, frame = cap.read()

        if ret:

            if current_frame == 0:
                first_frame = frame
                cv2.imwrite(background_image, first_frame)

            else:
                frame = cv2.subtract(frame, first_frame)

            ''' Missing Frames
            while (current_frame < debug_miss_frames):
                ret, frame = cap.read()
                current_frame += 1
            '''

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            if current_frame > 0:

                current_mouse_position = get_current_mouse_location(
                    gray, current_frame, template_mouse, template_mouse_w,
                    template_mouse_h, threshold_mouse)

                f_write_cursor_general.write(
                    str(current_mouse_position[1]) + " " +
                    str(current_mouse_position[2]) + ",")

                json_cursor_log.append([str(current_mouse_position[1]),
                                        str(current_mouse_position[2])])
                # colored_pixels = countNonBackGroundPixels(gray, black_
                # threshold, last_value_frame);
                ret, binary_image = cv2.threshold(gray, 50, 255,
                                                  cv2.THRESH_BINARY)
                colored_pixels = cv2.countNonZero(binary_image)
                # print(colored_pixels)

                if (colored_pixels > mouse_color_value) and (
                            (colored_pixels - last_value_frame) >
                            threshold_drawing):
                    current_connected_frame = 0

                else:
                    current_connected_frame += 1

                _erasure = last_value_frame - colored_pixels

                if _erasure > threshold_erasure:
                    cv2.putText(frame, 'Pixels Removed: ' + str(_erasure),
                                (5, 650), font, 1, (200, 50, 50), 1, cv2.CV_AA)

                if (((colored_pixels > mouse_color_value) and
                         ((colored_pixels - last_value_frame) >
                              threshold_drawing)) or
                        (current_connected_frame < max_connect_frames)):

                    # print("Drawing")
                    # - If user just started drawing: initialize stuff
                    if not is_user_writing:
                        starting_frame = frame_before_starting_4
                        # 5 frames old
                        index_of_starting_frame = current_frame
                        # Reset Cursor Positions
                        # - what about the last few cursor positions as well?
                        # if needed? - as in frame_before_starting
                        # _4,5
                        cursor_pos_for_ordering = []
                        saved_copy_of_cursor_pos_before_starting = list(
                            cursor_pos_before_starting)
                        # - start saving the new object

                    is_user_writing = True
                    cv2.putText(frame, 'Writing', (5, 700), font, 1,
                                (200, 50, 50), 1, cv2.CV_AA)
                    # Add Cursor Positions to List
                    cursor_pos_for_ordering.append(current_mouse_position)

                else:

                    # - If user just stopped: find out what user just drew
                    if is_user_writing:
                        # - Find the difference between current and starting
                        # frame
                        # - Full Final Frame
                        # cv2.imwrite('object ' + str(objects_drawn) + '.png',
                        # gray)
                        # - Difference Frame
                        # cv2.imwrite('object ' + str(objects_drawn) +
                        # ' diff.png', cv2.subtract(gray, starting_frame))
                        # Get the new imge - update binary image
                        bounding_image = cv2.subtract(gray, starting_frame)
                        remove_cursor(bounding_image, template_mouse,
                                      template_mouse_w, template_mouse_h,
                                      threshold_mouse)
                        ret, binary_difference = cv2.threshold(
                            bounding_image, 50, 255, cv2.THRESH_BINARY)
                        # Erode to get rid of small white blocks
                        kernel = np.ones((2, 2), np.uint8)
                        binary_difference = cv2.erode(
                            binary_difference, kernel, iterations=1)

                        objects_drawn += 1
                        # last_complete_image = frame
                        contours, hierarchy = cv2.findContours(
                            binary_difference, cv2.RETR_TREE,
                            cv2.CHAIN_APPROX_SIMPLE)

                        x1 = 1000  # - big value
                        y1 = 1000  # - big value
                        x2 = 0  # - small value
                        y2 = 0  # - small value

                        for i in range(0, len(contours)):

                            x, y, w, h = cv2.boundingRect(contours[i])
                            # cv2.rectangle(
                            # img,(x,y),(x + w,y + h),(255,0,0),1)
                            if x < x1:
                                x1 = x
                            if y < y1:
                                y1 = y
                            if x + w > x2:
                                x2 = x + w
                            if y + h > y2:
                                y2 = y + h

                        # cv2.rectangle(img,(x1,y1),(x2,y2),(0,255,0),1)

                        if ((x1 - 4 > 0) and
                                (x2 + 4 < image_width) and
                                (y1 - 4 > 0) and
                                (y2 + 4 < image_height) and
                                (x2 - x1 > 0) and
                                (y2 - y1 > 0)):

                            rect_start_x.append(x1 - 4)
                            rect_start_y.append(y1 - 4)
                            rect_width.append(x2 + 4)
                            rect_height.append(y2 + 4)

                            time = round(1.0 * current_frame / fps, 2)
                            starting_time = round(
                                1.0 * index_of_starting_frame / fps, 2)
                            # - to save the time when the first frame was
                            # registered
                            rect_time.append(time)
                            roi = frame[y1 - 4:y2 + 4, x1 - 4:x2 + 4]

                            # Get Color of Object
                            [r, g, b] = get_color(roi)
                            r = int(r)
                            g = int(g)
                            b = int(b)

                            cv2.imwrite('objects/' +
                                        str(count_objects_for_saving_images) +
                                        '.png', roi)

                            count_objects_for_saving_images += 1
                            f_write_objects.write(str(x1 - 4) + ' ' +
                                                  str(y1 - 4) + ' ' +
                                                  str(starting_time) + ' ' +
                                                  str(time) + ' ' +
                                                  str(r) + ' ' +
                                                  str(g) + ' ' + str(b) + '\n')

                            # Cursor positions before starting of the objects:
                            # in order to get the very starting points that are
                            #  missing otherwise
                            for i in saved_copy_of_cursor_pos_before_starting:
                                f_write_cursor_pos_for_order_points.write(
                                    str(i[0]) + " " + str(i[1] - (x1 - 4)) +
                                    " " + str(i[2] - (y1 - 4)) + ' ')
                                # print (str(i[0] - (x1 - 4)) + " " +
                                # str(i[1] - (y1 - 4)) + ' ')

                            for i in cursor_pos_for_ordering:
                                f_write_cursor_pos_for_order_points.write(
                                    str(i[0]) + " " + str(i[1] - (x1 - 4)) +
                                    " " + str(i[2] - (y1 - 4)) + ' ')

                            f_write_cursor_pos_for_order_points.write('\n')
                            # Reset Cursor Positions
                            cursor_pos_for_ordering = []

                    # Reset to false
                    cv2.putText(frame, 'Not Writing', (5, 700), font, 1,
                                (50, 50, 200), 1, cv2.CV_AA)

                    is_user_writing = False

            if current_frame > 0:

                last_value_frame = colored_pixels
                frame_before_starting_4 = frame_before_starting_3
                frame_before_starting_3 = frame_before_starting_2
                frame_before_starting_2 = frame_before_starting_1
                frame_before_starting_1 = gray

                # Storing the last few (5) cursor locations,
                # since we seem to miss that information when we realize that
                # new object has started
                if len(cursor_pos_before_starting) < 5:
                    cursor_pos_before_starting.append(current_mouse_position)

                else:
                    cursor_pos_before_starting.pop(0)
                    cursor_pos_before_starting.append(current_mouse_position)

                # - Drawing rectangles
                for i in range(0, len(rect_start_x)):
                    loc = ('x = ' + str(rect_start_x[i]) + ', y = ' +
                           str(rect_start_y[i]) + ', ')

                    size = ('width = ' + str(rect_width[i] - rect_start_x[i]) +
                            ', height = ' +
                            str(rect_height[i] - rect_start_y[i]) + ', ')

                    time = 'time: ' + str(rect_time[i])
                    cv2.rectangle(frame, (rect_start_x[i], rect_start_y[i]),
                                  (rect_width[i], rect_height[i]),
                                  (256, 0, 0), 2)
                    cv2.putText(frame, loc + size + time, (800, 20 + i * 13),
                                font, 0.45, (50, 50, 200), 1, cv2.CV_AA)

                final_frame = cv2.add(frame, first_frame)
                out.write(final_frame)
                # cv2.imshow('frame',gray)

            current_frame += 1
            # print current_frame
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        else:
            break

    f_write_objects.close()
    f_write_cursor_pos_for_order_points.close()
    f_write_cursor_general.close()
    cap.release()
    out.release()
    cv2.destroyAllWindows()

    return (count_objects_for_saving_images, json_operation_log,
            json_cursor_log, template_mouse_w, template_mouse_h, total_frames,
            fps)


def part_two(count_objects_for_saving_images):
    # Get total_objects from last part
    total_objects = count_objects_for_saving_images
    for object_number in range(0, total_objects):

        image = cv2.imread('objects/' + str(object_number) + '.png')
        gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        binary_threshold = 50
        ret, bw_image = cv2.threshold(gray_image, binary_threshold, 255, 0)
        contour_image = copy.deepcopy(bw_image)
        contours, hierarchy = cv2.findContours(
            contour_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        # cv2.drawContours(image,contours,-1,(0,255,0),3)

        for i in range(0, len(contours)):
            x, y, w, h = cv2.boundingRect(contours[i])
            # cv2.rectangle(image,(x,y),(x+w,y+h),(0,255,0),1)
            # cv2.imshow(str(i), image)
            mask = np.zeros(image.shape, np.uint8)
            mask[y:y + h, x:x + w] = image[y:y + h, x:x + w]
            cv2.imwrite('atomic objects/' + str(object_number) + '_' + str(i) +
                        '.png', mask)
            # cv2.imshow(str(i), mask);
            # print 'here'

    # color_img = cv2.cvtColor(bw_image, cv2.COLOR_GRAY2BGR)
    # enlarge = cv2.resize(image, (0,0), fx=4, fy=4)
    # cv2.imshow("image", enlarge);
    # cv2.waitKey(0)
    cv2.destroyAllWindows()


def part_three(total_objects, json_operation_log):
    # Read Cursor positions
    f = open('cursor positions.txt')
    data = f.read().split('\n')
    f.close()
    # Read Object List File
    f = open('object_list.txt')
    objects = f.read().split('\n')
    f.close()
    # Write Output File
    f_output = open('complete_strokes.txt', 'w')
    # I declared it here for debugging purposes
    g = Graph()
    # object_number = 16
    for object_number in range(0, total_objects):

        # if 1 == 1:
        valid_cursors = []
        valid_cursor_timestamps_global = []
        path_points_ordered_global = []  # contains all the data points that
        # are then written to file
        # Get cursor positions for this group of images
        cursor_pos = []
        obj1 = data[object_number].split(' ')

        for t, x, y in zip(obj1[0::3], obj1[1::3], obj1[2::3]):
            cursor_pos.append((t, x, y))

        prefixed = [filename for filename in os.listdir('atomic objects/') if
                    filename.startswith(str(object_number) + '_')]

        for connected_image in prefixed:

            valid_cursor_timestamps = []
            image = cv2.imread('atomic objects/' + connected_image)
            gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            binary_threshold = 50
            ret, bw_img = cv2.threshold(gray_image, binary_threshold, 255, 0)
            thinned_img = thin(bw_img)
            color_img = cv2.cvtColor(thinned_img, cv2.COLOR_GRAY2BGR)
            data_pts_thinned = np.nonzero(thinned_img)
            data_pts_thinned = zip(data_pts_thinned[0], data_pts_thinned[1])
            # print 'Total points: ' + str(len(cursor_pos))
            # Find Valid Cursor Positions
            count_valid_cursor_positions = 0
            # Append valid cursors in this local list
            valid_cursor_local = []
            # this list saves the unmapped, raw cursor positions so that the
            # order of the objects can be figured out
            valid_cursor_to_global = []

            for i in range(0, len(cursor_pos)):
                t = int(cursor_pos[i][0])
                x = int(cursor_pos[i][1])
                y = int(cursor_pos[i][2])
                last_t = -100
                last_x = -100
                last_y = -100

                if i > 0:
                    last_t = int(cursor_pos[i - 1][0])
                    last_x = int(cursor_pos[i - 1][1])
                    last_y = int(cursor_pos[i - 1][2])

                dim = bw_img.shape[1::-1]

                # if a point is within the boundary box of the object
                if 0 <= x < dim[0] and 0 <= y < dim[1]:
                    if ((is_neighbor_text(x, y, binary_threshold, bw_img,
                                          dim)) and
                            (len(data_pts_thinned) > 0) and
                            ((abs(x - last_x) + abs(y - last_y)) > 3)):
                        # Map y, x to the closest point
                        [mapped_x, mapped_y] = find_closest_point(
                            [y, x], data_pts_thinned)
                        # cv2.circle(color_img,(x, y), 1, (0,0,255))
                        color_img[mapped_x, mapped_y] = [255, 0, 0]
                        count_valid_cursor_positions += 1
                        # valid_cursor_local.append(cursor_pos[i]) # we also
                        # need to store the 'key' thinned points
                        valid_cursor_local.append((mapped_x, mapped_y))
                        valid_cursor_to_global.append((x, y))
                        # send values to global calculation to figure out the
                        # order of objects
                        valid_cursor_timestamps.append(t)
                        # print valid_cursor_local

            # print count_valid_cursor_positions
            # Get the thin of the image
            # Map valid neighbour points as skeleton points: snap to closest
            # Show the resulting image
            # Add Connected Object only if it has at least one valid cursor
            # position
            if len(valid_cursor_to_global) > 0:
                valid_cursors.append(valid_cursor_to_global)

            if len(valid_cursor_timestamps) > 0:
                valid_cursor_timestamps_global.append(valid_cursor_timestamps)

                # print 'global: ' + str(valid_cursor_to_global)
                # Here we have the all the cursor positions for this image.
                # Use these to find paths between the data point

            # Data points are in: data_pts_thinned, we can use this
            # datastructure to map data points to an index
            g = Graph()
            g.add_vertices(len(data_pts_thinned))
            # Create an adjacency matrix of data points - based on
            # 8-connectivity
            g.add_edges(compute_all_edges(data_pts_thinned))
            g.vs["point"] = data_pts_thinned
            # Calculate Paths between cursor positions
            path_points_ordered = []  # contains the temporal information, this
            #  is used for in-between points as well
            path_points = []

            for index_cursor_point in range(1, len(valid_cursor_local)):

                start_vertex = g.vs.find(
                    point=valid_cursor_local[index_cursor_point - 1])
                end_vertex = g.vs.find(
                    point=valid_cursor_local[index_cursor_point])
                shortest_path = g.get_all_shortest_paths(
                    start_vertex, end_vertex)

                if len(shortest_path) == 0:
                    print("In image: " + connected_image +
                          ", No path exists between: " +
                          str(data_pts_thinned[index_cursor_point - 1]) +
                          str(" and ") +
                          str(data_pts_thinned[index_cursor_point]))

                    path_points_ordered.append([])
                    # If no connection, still keep path_points_ordered same in
                    # size, need it at the end

                else:

                    # Path exists
                    path_between_strokes = []

                    for _path_points in shortest_path[0]:
                        # shortest path contains an array of shortest paths,
                        # meaning there could be more than one,
                        # I take the first one, doesn't make any difference
                        # color_img[g.vs[_path_points]['point']] = [0,0,0]
                        path_points.append(g.vs[_path_points]['point'])
                        # Save path points so that we can delete them later on
                        path_between_strokes.append(
                            g.vs[_path_points]['point'])
                        # print 'start: ' + str(start_vertex['point'])
                        # print 'end: ' + str(end_vertex['point'])
                        # print 'path: ' + str(path_points)

                    path_points_ordered.append(path_between_strokes)

            # 1st pass:
            # Remove all points used in any path - except data points
            path_points = list(set(path_points))
            # Remove multiple entries first

            for i in path_points:
                if i not in valid_cursor_local:
                    g.delete_vertices(g.vs.find(point=i))

            # 2nd pass:
            # Remove isolated points
            isolated_points = []
            for i in range(0, len(g.vs)):
                if len(g.incident(g.vs[i])) == 0:
                    isolated_points.append(g.vs[i]['point'])

            for i in isolated_points:
                g.delete_vertices(g.vs.find(point=i))
                # color_img[i] = [0,0,0]

            # 3rd pass:
            # Originating from the cursor_positions, DFS? overkill to all
            # possible positions
            # Take care of the timing of these auxilary points - push other
            # boundaries to make room for these

            # Get List of cursor points that have something attached to them
            for _cursor_no in range(0, len(valid_cursor_local)):
                if valid_cursor_local[_cursor_no] in g.vs['point']:

                    # print 'index: ' + str(_cursor_no) + ' ' +
                    # str(valid_cursor_local[_cursor_no])
                    paths = g.shortest_paths_dijkstra(source=g.vs.find(
                        point=valid_cursor_local[_cursor_no]))

                    if len(paths) > 0:  # result of shortest paths is a list of
                        #  list with one outermost element
                        paths = paths[0]
                        missed_points = []

                        for pt_in_path in range(0, len(paths)):
                            if ((paths[pt_in_path] > 0) and not
                            (math.isinf(paths[pt_in_path]))):
                                # print g.vs[pt_in_path]['point']
                                missed_points.append(
                                    [paths[pt_in_path],
                                     g.vs[pt_in_path]['point']])

                        # Add missed points to the path_points_ordered list
                        # If first cursor position, put before cursor position
                        #  in first list
                        # If last cursor position, put after cursor position
                        #  in last list
                        # If btw first and last, put before cursor position
                        #  in that list
                        missed_points = sorted(missed_points)
                        # print 'missed points: ' + str(missed_points)
                        # print paths

                        if ((_cursor_no == len(valid_cursor_local) - 1) and
                                (len(valid_cursor_local) > 1)):
                            # Last and has more than one valid cursor

                            for pt in range(0, len(missed_points)):
                                path_points_ordered[_cursor_no - 1].append(
                                    missed_points[pt][1])
                                # 1 is the actual data

                        else:  # First or any other except Last
                            for pt in range(0, len(missed_points)):
                                if len(path_points_ordered) > 0:
                                    path_points_ordered[_cursor_no].insert(
                                        0, missed_points[len(missed_points) -
                                                         pt - 1][1])
                                    # 1 is the actual data, #reversed order of
                                    # points

                                else:
                                    # no points are there in path_points_
                                    # ordered at all. So, add the first empty
                                    # list
                                    path_points_ordered.append([])

            # Submit local ordered points to global variable
            path_points_ordered_global.append(path_points_ordered)
            # color_img.fill(0) #remove everything drawn before
            # for i in range(0, len(g.vs)):
            #        color_img[g.vs[i]['point']] = [0,0,255]

            for i in range(0, len(path_points_ordered)):
                for j in range(0, len(path_points_ordered[i])):
                    color_img[path_points_ordered[i][j]] = [0, 255, 255]

                    # 4th pass:
                    # Start from 'pseudo' corner points and iterate until
                    # nothing is left
                    # Append everything at the end
                    # enlarge = cv2.resize(color_img, (0,0), fx=5, fy=5)
                    # cv2.imshow(connected_image, enlarge);
                    # cv2.imwrite('diet/' + connected_image, color_img)
                    # Find the order of the connected blocks among each other

        order = [0] * len(valid_cursors)
        counter = 0
        # Convert cursor_pos from string to int

        for i in range(0, len(cursor_pos)):
            cursor_pos[i] = map(int, cursor_pos[i])

        for i in cursor_pos:
            for j in range(0, len(valid_cursors)):
                if list(valid_cursors[j][0]) == i:
                    order[counter] = j
                    counter += 1
                    if counter == len(valid_cursors):
                        break

            if counter == len(valid_cursors):
                break

        '''
        #Write to output File
        f_output.write(objects[object_number] + '\n') # Object Information
        #f_output.write(str(len(path_points_ordered_global)) + '\n') # Number of Objects

        output = ""
        for obj_number in range(0, len(path_points_ordered_global)):
            #output += str(len(path_points_ordered_global[obj_number])) + '\n' # Number of Strokes in this object
            sum = 0
            for i in path_points_ordered_global:
                sum += len(i)
            output += str(sum) + '\n'
            for j in range(0, len(path_points_ordered_global[obj_number])):
                    if len(valid_cursor_timestamps_global) > obj_number + 1:
                            if len(valid_cursor_timestamps_global[obj_number]) > 1:
                                    output += str(valid_cursor_timestamps_global[obj_number][j + 1]
                                                  - valid_cursor_timestamps_global[obj_number][j]) + ' ';
                    else:
                            output += "1 "; #default: 1 frame time
                    for k in range(0, len(path_points_ordered_global[obj_number][j])):
                            output += (str(path_points_ordered_global[obj_number][j][k][0]) + " "
                                       + str(path_points_ordered_global[obj_number][j][k][1]) + " ")
                    output += '\n'


        f_output.write(output)'''

        # --- QUICK FIX --- Change later when done experimenting with
        # Fabric.js --- QUICK FIX --- #
        # Write to output File
        f_output.write(objects[object_number] + '\n')  # Object Information
        json_operation_log.append(objects[object_number])
        # f_output.write(str(len(path_points_ordered_global)) + '\n') #
        # Number of Objects
        sum = 0

        for i in path_points_ordered_global:
            sum += len(i)

        f_output.write(str(sum) + '\n')
        json_operation_log.append(str(sum))
        json_object_single = []
        output = ""

        for obj_number in range(0, len(path_points_ordered_global)):
            # output += str(len(path_points_ordered_global[obj_number])) +
            # '\n' # Number of Strokes in this object

            for j in range(0, len(path_points_ordered_global[obj_number])):
                '''if len(valid_cursor_timestamps_global) > obj_number + 1:
                        if len(valid_cursor_timestamps_global[obj_number]) > 1:
                                output += str(valid_cursor_timestamps_global[obj_number][j + 1]
                                              - valid_cursor_timestamps_global[obj_number][j]) + ' ';
                else:
                        output += "1 "; #default: 1 frame time'''
                json_operation_strokes = []

                for k in range(0,
                               len(path_points_ordered_global[obj_number][j])):
                    output += (
                        str(path_points_ordered_global[obj_number][j][k][1]) +
                        " " +
                        str(path_points_ordered_global[obj_number][j][k][0]) +
                        " ")
                    json_operation_strokes.append(
                        [str(path_points_ordered_global[obj_number][j][k][1]),
                         str(path_points_ordered_global[obj_number][j][k][0])])

                output += '\n'
                json_object_single.append(json_operation_strokes)

        f_output.write(output)
        json_operation_log.append(json_object_single)
    f_output.close()
    # cv2.waitKey(0)
    cv2.destroyAllWindows()


def generate_json(input_video, cursor_filename, template_mouse_w,
                  template_mouse_h, total_frames, fps, background_image,
                  json_cursor_log, json_operation_log):
    # - Create a JSON File
    j_filename = input_video
    j_interpolation = "interpolation"
    j_cursor_type = cursor_filename
    j_cursor_offset = [str(int(template_mouse_w / 2)),
                       str(int(template_mouse_h / 2))]
    j_duration = str(total_frames / fps)
    j_audio_file = "compressed_xyz.mp3"
    j_background_image = background_image
    j_frames_per_second = str(fps)
    j_cursor = json_cursor_log
    # - go one level deeper in operation
    j_operations = []

    for i in range(0, len(json_operation_log)):

        if i % 3 is 0:  # every third element
            info = json_operation_log[i].split(" ")
            info = map(float, info)
            reduced_list = []

            for list_points in json_operation_log[i + 2]:
                reduced_list = reduce_points(list_points)

            reduced_list = filter(None, reduced_list)

            my_object = {
                "offset_x": str(int(info[0])),
                "offset_y": str(int(info[1])),
                "start": str(info[2]),
                "end": str(info[3]),
                "color": [str(int(info[4])), str(int(info[5])),
                          str(int(info[6]))],
                "strokes": json_operation_log[i + 2]
            }

            j_operations.append(my_object)

    json_object = {
        "filename": j_filename,
        "interpolation": j_interpolation,
        "cursor_type": j_cursor_type,
        "cursor_offset": j_cursor_offset,
        "total_time": j_duration,
        "audio_file": j_audio_file,
        "background_image": j_background_image,
        "frames_per_second": j_frames_per_second,
        "cursor": j_cursor,
        "operations": j_operations
    }

    json_data = json.dumps(json_object)
    # - Write JSON to file
    f_json = open('data.json', 'w')
    f_json.write(json_data)
    f_json.close()
