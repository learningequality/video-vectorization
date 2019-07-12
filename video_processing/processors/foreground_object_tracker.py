# Copyright 2019 Google LLC.
"""Identifies objects in the foreground of a video.

Adds a stream containing coordinates of bounding boxes for non-stroke objects in
the video. Optionally writes best-guess images to numbered files in a directory.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from video_processing import stream_processor
import cv2


class ForegroundObjectTracker(stream_processor.ProcessorBase):
  """Processor tracking foreground objects in the video with bounding boxes."""

  def __init__(self, configuration):
    self._video_stream_name = configuration.get('video_stream_name', 'video')
    self._bbox_stream_name = configuration.get('bounding_box_stream_name',
                                               'object_bounding_boxes')
    self._object_image_output_directory = configuration.get(
        'object_image_output_directory', None)
    self._image_width = 0
    self._image_height = 0

  def open(self, stream_set):
    headers = stream_set.stream_headers[self._video_stream_name].header_data
    self._image_width = headers.image_width
    self._image_height = headers.image_height
    self._background_subtractor = cv2.bgsegm.createBackgroundSubtractorMOG()
    stream_set.stream_headers[
        self._bbox_stream_name] = stream_processor.StreamHeader(
            frame_data_type=list, header_data=[])
    return stream_set

  def process(self, frame_set):
    if frame_set.get(self._video_stream_name, False):
      frame_index = frame_set[self._video_stream_name].index
      video_frame = frame_set[self._video_stream_name].data
      foreground_mask = self._background_subtractor.apply(video_frame)
      contours, _ = cv2.findContours(foreground_mask,
                                        cv2.RETR_EXTERNAL,
                                        cv2.CHAIN_APPROX_SIMPLE)
      if contours:
        # TODO(tomwalters): Add more logic to merge bounding boxes that overlap.
        frame_data = []
        for contour in contours:
          frame_data.append(cv2.boundingRect(contour))
          frame_set[self._bbox_stream_name] = stream_processor.Frame(
              frame_index, frame_data)
    return frame_set

  def close(self):
    return []
