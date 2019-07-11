"""A video encoder processor that uses OpenCV to write video frames to a file.

A wrapper around the OpenCV VideoWriter class.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from video_processing import stream_processor
import cv2


class OpenCVVideoEncoderProcessor(stream_processor.ProcessorBase):
  """Processor for encoding video using OpenCV."""

  def __init__(self, configuration):
    self._output_video_file = configuration.get('output_video_file', '')
    self._video_stream_name = configuration.get('video_stream_name', 'video')
    self._fourcc_string = configuration.get('fourcc', 'DIVX')
    self._index = 0

  def open(self, stream_set):
    fourcc = cv2.VideoWriter_fourcc(*self._fourcc_string)
    frame_rate = stream_set.frame_rate_hz
    header = stream_set.stream_headers[
        self._video_stream_name].header_data
    self._video_writer = cv2.VideoWriter(self._output_video_file, fourcc,
                                         frame_rate,
                                         (header.image_width,
                                          header.image_height))
    return stream_set

  def process(self, frame_set):
    if frame_set.get(self._video_stream_name, False):
      video_frame = frame_set[self._video_stream_name].data
      self._video_writer.write(video_frame)
    return frame_set

  def close(self):
    self._video_writer.release()
    return []
