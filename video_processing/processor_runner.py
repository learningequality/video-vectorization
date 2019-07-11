"""Utility function for running a chain of processors."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from video_processing import stream_processor


def run_processor_chain(processors_list):
  """Runs a chain of processors.

  Runs a chain of processors defined by processors_list.

  Args:
    processors_list: A list of instances of subclasses of
        stream_processor.ProcessorBase.
  """
  streams = stream_processor.StreamSet()
  for p in processors_list:
    streams = p.open(streams)
  done = False
  while not done:
    head = True
    frame_set = {}
    for p in processors_list:
      frame_set = p.process(frame_set)
      # If the processor at the head of the processors list does not return
      # anything, then we're done.
      if head and not frame_set:
        done = True
      head = False
    del frame_set
  for p in processors_list:
    # TODO(tomwalters): Deal with frames emitted on the call to close().
    # Will need to recurse through frames from each close call, and then pass
    # these to the process calls for the rest of the chain before calling close.
    p.close()
