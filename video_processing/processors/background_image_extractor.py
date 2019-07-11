# Lint as: python2, python3
"""Creates a new stream containing a background image for a video stream.

The implementation is currently very naive. It simply takes the first frame of a
video stream and copies it to a new stream.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import numpy as np

from video_processing import stream_processor
import cv2


class FirstFrameBackgroundImageExtractor(stream_processor.ProcessorBase):
  """Processor that copies the first frame to a background image stream.

  Optionally, if background_image_file_name is set, the image can also be
  written to a file.
  """

  def __init__(self, configuration):
    self._video_stream_name = configuration.get('video_stream_name', 'video')
    self._background_stream_name = configuration.get(
        'background_image_stream_name', 'background_image')
    self._background_file_name = configuration.get('background_image_file_name',
                                                   None)
    self._image_width = 0
    self._image_height = 0
    self._done = False

  def open(self, stream_set):
    headers = stream_set.stream_headers[self._video_stream_name].header_data
    self._image_width = headers.image_width
    self._image_height = headers.image_height
    self._num_frames = headers.num_frames
    stream_set.stream_headers[
        self._background_stream_name] = stream_processor.StreamHeader(
            frame_data_type=np.ndarray,
            header_data=stream_processor.VideoStreamHeader(
                self._image_width, self._image_height, self._num_frames))
    return stream_set

  def process(self, frame_set):
    # Grab the first valid frame in _video_stream_name.
    if frame_set.get(self._video_stream_name, False) and not self._done:
      video_frame_index = frame_set[self._video_stream_name].index
      video_frame = frame_set[self._video_stream_name].data
      frame_set[self._background_stream_name] = stream_processor.Frame(
          video_frame_index, video_frame)
      if self._background_file_name:
        cv2.imwrite(self._background_file_name, video_frame)
      self._done = True
    return frame_set

  def close(self):
    return []
