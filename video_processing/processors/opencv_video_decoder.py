"""A video decoder processor that uses OpenCV to decode video into frames.

A wrapper around the OpenCV VideoCapture class to provide video frames to
downstream processors.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import numpy

from video_processing import stream_processor
import cv2


class OpenCVVideoDecoderProcessor(stream_processor.ProcessorBase):
  """Processor for decoding video using OpenCV."""

  def __init__(self, configuration):
    self._input_video_file = configuration.get('input_video_file', '')
    self._video_stream_name = configuration.get('video_stream_name', 'video')
    self._index = 0

  def open(self, stream_set):
    self._capture = cv2.VideoCapture(self._input_video_file)
    frame_rate_hz = self._capture.get(cv2.CAP_PROP_FPS)
    if stream_set.frame_rate_hz < 0:
      # If the frame rate wasn't set, then we can assume that we're the top
      # of the processing chain and create a new stream set object to
      # contain the video stream.
      stream_set = stream_processor.StreamSet(frame_rate_hz=frame_rate_hz)
    else:
      if stream_set.frame_rate_hz != frame_rate_hz:
        raise Exception('Frame rate in additional video stream is not equal to '
                        'that of the original stream set.')
    image_width = int(self._capture.get(cv2.CAP_PROP_FRAME_WIDTH))
    image_height = int(self._capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
    num_frames = int(self._capture.get(cv2.CAP_PROP_FRAME_COUNT))
    stream_set.stream_headers[
        self._video_stream_name] = stream_processor.StreamHeader(
            frame_data_type=numpy.ndarray,
            header_data=stream_processor.VideoStreamHeader(
                image_width, image_height, num_frames))
    return stream_set

  def process(self, frame_set):
    if not self._capture.isOpened():
      return frame_set
    ret, frame_data = self._capture.read()
    if not ret:
      return frame_set
    frame_set[self._video_stream_name] = stream_processor.Frame(self._index,
                                                                frame_data)
    self._index += 1
    return frame_set

  def close(self):
    self._capture.release()
    return []
