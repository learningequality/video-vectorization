"""Writes JSON format vectorized video to file."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import json
from video_processing import stream_processor


class JSONWriter(stream_processor.ProcessorBase):
  """Processor for generating json format stroke data."""

  def __init__(self, configuration):
    self._output_json_file = configuration.get('output_json_file', '')
    self._video_stream_name = configuration.get('video_stream_name', 'video')
    self._cursor_stream_name = configuration.get('cursor_stream_name', 'cursor')
    self._stroke_stream_name = configuration.get('stroke_stream_name',
                                                 'strokes')
    self._video_stream_name = configuration.get('video_stream_name', 'video')
    self._input_file_name = configuration.get('input_file_name', '')
    self._background_image_name = configuration.get('background_image_file', '')
    self._operations = []

  def open(self, stream_set):
    self._fps = stream_set.frame_rate_hz
    self._cursor_template_file = stream_set.stream_headers[
        self._cursor_stream_name].header_data.cursor_file
    self._cursor_width = stream_set.stream_headers[
        self._cursor_stream_name].header_data.cursor_width
    self._cursor_height = stream_set.stream_headers[
        self._cursor_stream_name].header_data.cursor_height
    self._cursor_log = []
    self._num_frames = stream_set.stream_headers[
        self._video_stream_name].header_data.num_frames
    return stream_set

  def process(self, frame_set):
    if frame_set.get(self._stroke_stream_name, False):
      object_data = frame_set[self._stroke_stream_name].data
      object_json = {
          'end': str(object_data.get('end') / self._fps),
          'strokes': object_data.get('strokes'),
          'color': [
              int(object_data.get('color')[0]),
              int(object_data.get('color')[1]),
              int(object_data.get('color')[2])
          ],
          'start': str(object_data.get('start') / self._fps),
      }
      self._operations.append(object_json)
    if frame_set.get(self._cursor_stream_name, False):
      self._cursor_log.append(frame_set[self._cursor_stream_name].data)

    return frame_set

  def close(self):
    cursor_offset = [
        str(int(self._cursor_width / 2)),
        str(int(self._cursor_height / 2))
    ]
    json_object = {
        'total_time': int(self._num_frames) / (self._fps),
        'total_frames': int(self._num_frames),
        'background_image': self._background_image_name,
        'cursor': self._cursor_log,
        'operations': self._operations,
        'frames_per_second': self._fps,
        'cursor_offset': cursor_offset,
        'interpolation': 'interpolation',
        'cursor_type': self._cursor_template_file,
        'filename': self._input_file_name,
        # TODO: Add automated extraction of audio.
        # 'audio_file': 'compressed_xyz.mp3',
    }

    json_data = json.dumps(json_object)
    json_file = open(self._output_json_file, 'w')
    json_file.write(json_data)
    json_file.close()
    return []
