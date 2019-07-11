"""Identifies new objects added to a video.

Adds a stream containing individual added object images, along with their
extents, and a track of the location of the cursor around the time that the
object was drawn.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import collections
import numpy as np
from six.moves import range
from video_processing import stream_processor
import cv2

MAX_PREVIOUS_CURSOR_POSITIONS = 4
MAX_PREVIOUS_FRAMES = 4
MAX_CONNECTED_FRAMES = 5


def remove_cursor(gray_input, cursor_template, threshold=0):
  img_dim = gray_input.shape[::-1]
  img_w = img_dim[0]
  img_h = img_dim[1]

  cursor_dim = cursor_template.shape[::-1]
  template_mouse_w = cursor_dim[0]
  template_mouse_h = cursor_dim[1]

  if (img_w < template_mouse_w or img_h < template_mouse_h):
    return
  # Remove the cursor
  # - Use gray image created above method = 'cv2.TM_CCOEFF'
  method = 'cv2.TM_CCOEFF'
  # Apply template Matching - cursor
  res = cv2.matchTemplate(gray_input, cursor_template, cv2.TM_CCOEFF)
  # - one of the methods
  min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

  # If the method is TM_SQDIFF or TM_SQDIFF_NORMED, take minimum
  if method == 'cv2.TM_SQDIFF' or method == 'cv2.TM_SQDIFF_NORMED':
      top_left = min_loc
  else:
      top_left = max_loc

  bottom_right = (top_left[0] + template_mouse_w, top_left[1] +
                  template_mouse_h)

  if max_val > threshold:
      cv2.rectangle(gray_input, top_left, bottom_right, (0, 0, 0), -1)


def find_enclosing_rectangle(contours):
  """Find the rectangle that encloses the points in a list of contours."""
  if not contours:
    return (0, 0, 0, 0)

  x1, y1, w, h = cv2.boundingRect(contours.pop(0))
  y2 = y1 + h
  x2 = x1 + w

  for contour in contours:
    x, y, w, h = cv2.boundingRect(contour)
    x1 = x if x < x1 else x1
    y1 = y if y < y1 else y1
    x2 = x + w if x + w > x2 else x2
    y2 = y + h if y + h > y2 else y2
  return (x1, y1, x2, y2)


def get_cropped_frame_difference(start_frame,
                                 end_frame,
                                 cursor_template=None,
                                 do_erode=True,
                                 border_pixels=4):
  """Crops out a changed region between images.

  Given a grayscale 'before' and 'after' frame, find the bounding box of the
  region that differs between the two frames, and crops a corresponding region
  from the given color image.
  Returns the cropped color image and the bounding box of the region within
  the full image.

  Args:
    start_frame: 'Before' frame. Grayscale.
    end_frame: 'After' frame. Grayscale.
    cursor_template: Grayscale cursor image to remove from frames.
    do_erode: Set true to erode the edges of shapes to remove small artifacts.
    border_pixels: Number of extra pixels to extend the bounding box in each
      direction.

  Returns:
   crop:
   bounding_box:
  """
  if cursor_template is not None:
    remove_cursor(start_frame, cursor_template)
  difference_image = cv2.subtract(end_frame, start_frame)
  _, binary_difference = cv2.threshold(
      cv2.cvtColor(difference_image, cv2.COLOR_BGR2GRAY), 50, 255,
      cv2.THRESH_BINARY)
  if do_erode:
    # Erode to get rid of small white blocks.
    binary_difference = cv2.erode(
        binary_difference, np.ones((2, 2), np.uint8), iterations=1)

  contours, _ = cv2.findContours(binary_difference, cv2.RETR_TREE,
                                    cv2.CHAIN_APPROX_SIMPLE)
  x1, y1, x2, y2 = find_enclosing_rectangle(contours)
  x1 = max(x1 - border_pixels, 0)
  y1 = max(y1 - border_pixels, 0)
  x2 = min(x2 + border_pixels, difference_image.shape[1])
  y2 = min(y2 + border_pixels, difference_image.shape[0])
  crop = difference_image[y1:y2, x1:x2]
  return crop, (x1, y1, x2 - x1, y2 - y1)


def get_color(image):
  """Get color of a contour."""
  threshold_black = 10
  reds = [0]
  greens = [0]
  blues = [0]

  for x in range(0, image.shape[0]):
    for y in range(0, image.shape[1]):

      if image[x, y][0] > threshold_black:
        blues.append(image[x, y][0])
      if image[x, y][1] > threshold_black:
        greens.append(image[x, y][1])
      if image[x, y][2] > threshold_black:
        reds.append(image[x, y][2])

  return [
      np.percentile(np.array(reds), 90),
      np.percentile(np.array(greens), 90),
      np.percentile(np.array(blues), 90)
  ]


class AddedObjectTracker(stream_processor.ProcessorBase):
  """Processor tracking pen strokes in the video."""

  def __init__(self, configuration):
    self._video_stream_name = configuration.get('video_stream_name', 'video')
    self._bbox_stream_name = configuration.get('bounding_box_stream_name',
                                               'object_bounding_boxes')
    self._background_stream_name = configuration.get(
        'background_image_stream_name', 'background_image')
    self._object_stream_name = configuration.get('object_stream_name',
                                                 'objects')
    self._cursor_stream_name = configuration.get('cursor_stream_name', 'cursor')
    self._cursor_image = None
    self._background_frame = None
    self._previous_num_lit_pixels = 0
    self._is_writing = False
    self._writing_threshold = 25
    self._erasure_threshold = 50
    self._connected_frame = 0
    self._object_start_frame = None
    self._cursor_path = []
    self._image_width = 0
    self._image_height = 0
    self._previous_cursor_positions = collections.deque(
        maxlen=MAX_PREVIOUS_CURSOR_POSITIONS)
    self._previous_frames = collections.deque(maxlen=MAX_PREVIOUS_FRAMES)

  def open(self, stream_set):
    headers = stream_set.stream_headers[self._video_stream_name].header_data
    self._image_width = headers.image_width
    self._image_height = headers.image_height
    stream_set.stream_headers[
        self._object_stream_name] = stream_processor.StreamHeader(
            frame_data_type={}, header_data=[])
    self._cursor_image = stream_set.stream_headers[
        self._cursor_stream_name].header_data.cursor_image
    return stream_set

  def process(self, frame_set):
    # Gets the current background frame, as provided by an upstream background
    # extractor such as the background_image_extractor.
    if frame_set.get(self._background_stream_name, False):
      self._background_frame = frame_set[self._background_stream_name].data

    # If there's no new video frame to process, don't do anything.
    if not frame_set.get(self._video_stream_name, False):
      return frame_set

    # Otherwise, we have a new frame to process.
    frame_index = frame_set[self._video_stream_name].index
    video_frame = frame_set[self._video_stream_name].data

    # Subtract out the background image, and create a grayscale version of the
    # remainder.
    frame = cv2.subtract(video_frame, self._background_frame)
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Retrieve the current cursor position, as extracted by an upstream
    # processor. If there isn't one, just place the cursor in the corner.
    if frame_set.get(self._cursor_stream_name, False):
      current_cursor_position = frame_set[self._cursor_stream_name].data
    else:
      current_cursor_position = [0, 0]

    # Count how many pixels are lit in the current frame.
    _, binary_frame = cv2.threshold(gray_frame, 50, 255, cv2.THRESH_BINARY)
    num_lit_pixels = cv2.countNonZero(binary_frame)

    if frame_index == 0:
      # If we're at the start, fill up the relevant buffers.
      self._previous_frames.extend(MAX_PREVIOUS_FRAMES * [frame])
      self._previous_cursor_positions.extend(MAX_PREVIOUS_CURSOR_POSITIONS *
                                             [current_cursor_position])
    else:
      # Otherwise, just add the current frame.
      self._previous_frames.append(frame)
      self._previous_cursor_positions.append(current_cursor_position)

    # Compute how many pixels have been added since the last frame.
    num_added_pixels = num_lit_pixels - self._previous_num_lit_pixels
    self._previous_num_lit_pixels = num_lit_pixels

    # if num_added_pixels < -self._erasure_threshold:
    # Some pixels have been erased since the last frame.
    # TODO: Mark erased regions for blanking.
    #   print('erasure')

    # Each time there's a positive addition to a stroke, we reset
    # 'connected_frame'. This allows us to keep tracking what happens for a few
    # frames after writing finishes.
    if num_added_pixels > self._writing_threshold:
      self._connected_frame = 0
    else:
      self._connected_frame += 1

    if (num_added_pixels > self._writing_threshold or
        self._connected_frame < MAX_CONNECTED_FRAMES):
      # Either some writing happened, or we're looking a bit further into
      # the future to check that no more writing is going to occur.
      if not self._is_writing:
        self._is_writing = True
        self._start_timestamp = frame_index
        # Grab the frame from the start of the historical frame queue as our
        # starting frame.
        self._object_start_image = self._previous_frames[0]
        # Reset the list of cursor positions for this new object to contain
        # the cursor positions that just preceded the presenter starting to
        # write this stroke.
        self._cursor_path = [a for a in self._previous_cursor_positions]
      else:
        self._cursor_path.append(current_cursor_position)
    else:
      # If the presenter was writing, we're now confident that they've stopped.
      if self._is_writing:
        self._is_writing = False

        # Now we find out what was added in the period since the presenter
        # started writing, by differencing the start and end frames.
        crop, bounding_box = get_cropped_frame_difference(
            start_frame=self._object_start_image, end_frame=frame,
            cursor_template=self._cursor_image)
        (r, g, b) = get_color(crop)

        # Pass this object on to downstream processors, along with the inferred
        # color, and the path that the cursor took, for future processing.

        # Note that this object data structure is compatible both with the
        # stroke_tracker processor, which will try to more accurately track the
        # strokes within the object, and with the json_writer directly, which
        # will use the tracked cursor locations directly to plot strokes. This
        # latter option is useful for debugging.
        object_data = {
            'start': self._start_timestamp,
            'end': frame_index,
            'strokes': [[list(e) for e in self._cursor_path]],
            'crop': crop,
            'bounding_box': bounding_box,
            'color': (r, g, b)
        }
        # DEBUG
        # cv2.imwrite('/tmp/' + str(frame_index) + '.png', crop)
        frame_set[self._object_stream_name] = stream_processor.Frame(
            frame_index, object_data)
        self._cursor_path = []
    return frame_set

  def close(self):
    return []
