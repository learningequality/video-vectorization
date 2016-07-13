# coding=utf-8
import itertools
import json
import cv2
import numpy as np
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

    # return [np.median(np.array(reds)), np.median(np.array(greens)), np.median(np.array(blues))]
    return [np.percentile(np.array(reds), 90), np.percentile(np.array(greens), 90), np.percentile(np.array(blues), 90)]


def remove_cursor(gray_input, template_mouse, template_mouse_w, template_mouse_h, threshold_mouse):
    # Remove the cursor
    # - Use gray image created above method = 'cv2.TM_CCOEFF'
    method = 'cv2.TM_CCOEFF'
    # Apply template Matching - cursor
    res = cv2.matchTemplate(gray_input, template_mouse, cv2.TM_CCOEFF)  # - one of the methods
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

    # If the method is TM_SQDIFF or TM_SQDIFF_NORMED, take minimum
    if method == 'cv2.TM_SQDIFF' or method == 'cv2.TM_SQDIFF_NORMED':
        top_left = min_loc
    else:
        top_left = max_loc

    bottom_right = (top_left[0] + template_mouse_w, top_left[1] + template_mouse_h)

    if max_val > threshold_mouse:
        cv2.rectangle(gray_input, top_left, bottom_right, (0, 0, 0), -1)


def get_current_mouse_location(gray_input, frame_number, template_mouse, template_mouse_w, template_mouse_h,
                               threshold_mouse):
    # Find the cursor
    # - Use gray image created above method = 'cv2.TM_CCOEFF'
    method = 'cv2.TM_CCOEFF'
    # Apply template Matching - cursor
    res = cv2.matchTemplate(gray_input, template_mouse, cv2.TM_CCOEFF)  # - one of the methods
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

    # If the method is TM_SQDIFF or TM_SQDIFF_NORMED, take minimum
    if method == 'cv2.TM_SQDIFF' or method == 'cv2.TM_SQDIFF_NORMED':
        top_left = min_loc
    else:
        top_left = max_loc

    bottom_right = (top_left[0] + template_mouse_w, top_left[1] + template_mouse_h)

    if max_val > threshold_mouse:
        # cv2.rectangle(gray_input,top_left, bottom_right, (0,0,0), -1)
        return frame_number, int((top_left[0] + bottom_right[0]) / 2), int((top_left[1] + bottom_right[1]) / 2)

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
    if img[y, x] > binary_threshold or (y + 1 < dim[1] and img[y + 1, x] > binary_threshold) or (
                        y - 1 >= 0 and img[y - 1, x] > binary_threshold) or (
                        x + 1 < dim[0] and img[y, x + 1] > binary_threshold) or (
                            x + 1 < dim[0] and y + 1 < dim[1] and img[y + 1, x + 1] > binary_threshold) or (
                            y - 1 >= 0 and x + 1 < dim[0] and img[y - 1, x + 1] > binary_threshold) or (
                        x - 1 >= 0 and img[y, x - 1] > binary_threshold) or (
                            y + 1 < dim[1] and x - 1 >= 0 and img[y + 1, x - 1] > binary_threshold) or (
                            y - 1 >= 0 and x - 1 >= 0 and img[y - 1, x - 1] > binary_threshold):
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
                    (abs(_x[0] - data_pts[current][0]) < 2) and (abs(_x[1] - data_pts[current][1]) < 2) and
                    (_x[0] != data_pts[current][0] or _x[1] != data_pts[current][1])]
        for _a in adjacent:
            graph_connections.append((current, _a))
            # print "connection: " + str(current) + " : " + str(_a)

    # Remove duplicates
    list_with_duplicates = sorted([sorted(_x) for _x in graph_connections])
    result = list(list_with_duplicates for list_with_duplicates, _ in itertools.groupby(list_with_duplicates))
    # print result
    return result


def check_if_collinear(a, b, c):
    diff = (((int(a[1]) - int(b[1])) * (int(a[0]) - int(c[0]))) - ((int(a[1]) - int(c[1])) * (int(a[0]) - int(b[0]))))
    return diff <= 1e-9


def reduce_points(unreduced_list):
    new_list = unreduced_list[:]

    for point in range(len(unreduced_list) - 2):
        if check_if_collinear(unreduced_list[point], unreduced_list[point + 1], unreduced_list[point + 2]):
            new_list[point + 1] = ''

    return new_list


def generate_json(input_video, cursor_filename, template_mouse_w, template_mouse_h, total_frames, fps,
                  background_image, json_cursor_log, json_operation_log):

    # - Create a JSON File
    j_filename = input_video
    j_interpolation = "interpolation"
    j_cursor_type = cursor_filename
    j_cursor_offset = [str(int(template_mouse_w / 2)), str(int(template_mouse_h / 2))]
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
                "color": [str(int(info[4])), str(int(info[5])), str(int(info[6]))],
                "strokes": reduced_list
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
    f_json = open('json.txt', 'w')
    f_json.write(json_data)
    f_json.close()
