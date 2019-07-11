"""Base stream processor and associated support.

Base class for video processing modules. Modules can be strung together into
chains, which can process zero or more input streams and add zero or more output
streams to be processed by downstream modules.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import collections

StreamHeader = collections.namedtuple('StreamHeader', ['frame_data_type',
                                                       'header_data'])

VideoStreamHeader = collections.namedtuple(
    'VideoStreamHeader', ['image_width', 'image_height', 'num_frames'])

CursorStreamHeader = collections.namedtuple(
    'CursorStreamHeader',
    ['cursor_file', 'cursor_width', 'cursor_height', 'cursor_log', 'cursor_image'])


class Frame(collections.namedtuple('FrameSet', ['index', 'data'])):
  """Container for a single frame of some stream."""

  def __new__(cls, index=0, data=None):
    return super(Frame, cls).__new__(cls, index, data)


class StreamSet(collections.namedtuple('StreamSet', ['frame_rate_hz',
                                                     'stream_headers'])):
  """Class containing metadata for a set of streams.
  """

  def __new__(cls, frame_rate_hz=-1):
    # stream_headers is an OrderedDict mapping strings of stream names to
    # StreamHeader objects containing information about the stream.
    stream_headers = collections.OrderedDict()
    return super(StreamSet, cls).__new__(
        cls, frame_rate_hz, stream_headers)


class ProcessorBase(object):
  """Base class for processing modules."""

  def __init__(self, configuration):
    """Initialize with a given configuration.

    Args:
      configuration: A configuration dictionary for this processor.
    """
    self.configuration = configuration

  def open(self, stream_set):
    """Prepares the filter for processing, updating stream_set.

    Args:
      stream_set: A StreamSet object which is modified to reflect the
        operations performed by process().
    Returns:
      The updated stream_set.

    When writing a decoder processor that that may run at the head of a
    processor chain, if the frame rate is not set already then it is acceptable
    to create a new stream_set and return that in order to set the global frame
    rate.
    """
    return stream_set

  def process(self, frame_set):
    """Process a frame set.

    Args:
      frame_set: A dictionary mapping stream names to a single instance of a
        frame from that stream. This dictionary is modified in place to update
        frames from streams that the processor is modifying and / or add new
        frames from streams that the filter is adding.
    Returns:
      The modified frame set.
    """
    return frame_set

  def close(self):
    """Close the processor, flushing any remaining data.

    Returns:
      List of output frame sets.
    """
    return []
