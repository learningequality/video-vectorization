# coding=utf-8
from __future__ import print_function
from defs import *

input_video = 'exponents.mp4'
cursor_filename = 'cursor_1.png'
background_image = "background.png"

count_objects_for_saving_images = 0
json_operation_log = []
json_cursor_log = []
templateMouse_w = None
templateMouse_h = None
total_frames = None
fps = None

# PART 1
print('part 1 started')
count_objects_for_saving_images, json_operation_log, json_cursor_log, templateMouse_w, templateMouse_h, total_frames, fps = part_one(
    input_video, cursor_filename, background_image,
    count_objects_for_saving_images, json_operation_log, json_cursor_log,
    templateMouse_w, templateMouse_h, total_frames, fps)
print('part 1 ended')

# PART 2
print('part 2 started')
part_two(count_objects_for_saving_images)
print('Part 2 Completed!')

# PART 3
print('part 3 started')
part_three(count_objects_for_saving_images, json_operation_log)
print('part 3 ended')

# PART 4
print('part 4 started')
generate_json(input_video, cursor_filename, templateMouse_w, templateMouse_h,
              total_frames, fps, background_image,
              json_cursor_log, json_operation_log)
print('part 4 done')
