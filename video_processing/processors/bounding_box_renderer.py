"""Renders bounding boxes on a video stream.


"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from video_processing import stream_processor
import cv2


class BoundingBoxRenderer(stream_processor.ProcessorBase):
  """Processor that draws bounding boxes based on a bounding box stream."""

  def __init__(self, configuration):
    self._video_stream_name = configuration.get('video_stream_name', 'video')
    self._bbox_stream_name = configuration.get('bounding_box_stream_name',
                                               'object_bounding_boxes')
    self._image_width = 0
    self._image_height = 0

  def open(self, stream_set):
    headers = stream_set.stream_headers[self._video_stream_name].header_data
    self._image_width = headers.image_width
    self._image_height = headers.image_height
    return stream_set

  def process(self, frame_set):
    if frame_set.get(
        self._video_stream_name, False) and frame_set.get(
            self._bbox_stream_name, False):
      video_frame_index = frame_set[self._video_stream_name].index
      bbox_frame_index = frame_set[self._bbox_stream_name].index
      if bbox_frame_index != video_frame_index:
        raise Exception('Please align streams before running the bounding '
                        'box renderer processor.')
      video_frame = frame_set[self._video_stream_name].data
      bounding_boxes = frame_set[self._bbox_stream_name].data
      box_color = (0, 255, 0)
      for x, y, w, h in bounding_boxes:
        cv2.rectangle(video_frame, (x, y), (x + w, y + h), box_color)
    return frame_set

  def close(self):
    return []
