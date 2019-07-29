# Copyright 2019 Google LLC.
"""Tracks the cursor in a video.

Given a template image for a cursor, adds a stream containing coordinates of the
cursor in the video.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from video_processing import stream_processor
import cv2


class CursorTracker(stream_processor.ProcessorBase):
  """Processor tracking cursor in the video."""

  def __init__(self, configuration):
    self._video_stream_name = configuration.get('video_stream_name', 'video')
    self._cursor_stream_name = configuration.get('cursor_stream_name', 'cursor')
    self._background_stream_name = configuration.get('background_stream_name',
                                                     'background_image')
    self._cursor_file = configuration.get('cursor_template_file', '')
    self._background_image = None
    self._cursor_threshold = 0
    self._cursor_width = 0
    self._cursor_height = 0
    self._cursor_log = []

  def open(self, stream_set):
    self._cursor_template = cv2.imread(self._cursor_file, 0)
    self._cursor_width, self._cursor_height = self._cursor_template.shape[::-1]
    stream_set.stream_headers[
        self._cursor_stream_name] = stream_processor.StreamHeader(
            frame_data_type=str,
            header_data=stream_processor.CursorStreamHeader(
                self._cursor_file, self._cursor_width, self._cursor_height,
                self._cursor_log, self._cursor_template))
    return stream_set

  def process(self, frame_set):
    if (frame_set.get(self._background_stream_name, False) and
        self._background_image is None):
      self._background_image = cv2.cvtColor(
          frame_set[self._background_stream_name].data, cv2.COLOR_BGR2GRAY)
    if frame_set.get(self._video_stream_name, False):
      frame_index = frame_set[self._video_stream_name].index
      video_frame = frame_set[self._video_stream_name].data
      gray_frame = cv2.cvtColor(video_frame, cv2.COLOR_BGR2GRAY)
      if self._background_image is None:
        print('ERROR: No valid background image found.')
      frame = cv2.subtract(gray_frame, self._background_image)
      match = cv2.matchTemplate(frame, self._cursor_template, cv2.TM_CCOEFF)

      _, max_val, _, max_loc = cv2.minMaxLoc(match)

      # max_loc is best match when using TM_CCOEFF method
      #bottom_right = (max_loc[0] + self._cursor_width,
      #                max_loc[1] + self._cursor_height)

      if max_val > self._cursor_threshold:
        frame_set[self._cursor_stream_name] = stream_processor.Frame(
            frame_index, [
                int(max_loc[0] + self._cursor_width / 2),
                int(max_loc[1] + self._cursor_height / 2)
            ])
    return frame_set

  def close(self):
    return []
