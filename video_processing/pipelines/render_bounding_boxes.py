"""Pipeline to track objects and render their bounding boxes."""
from absl import app
from absl import flags

from video_processing import processor_runner
from video_processing.processors import bounding_box_renderer
from video_processing.processors import foreground_object_tracker
from video_processing.processors import opencv_video_decoder
from video_processing.processors import opencv_video_encoder

flags.DEFINE_string('input_video_file', '', 'Input file.')
flags.DEFINE_string('output_video_file', '', 'Output file.')

FLAGS = flags.FLAGS


def pipeline(input_video_file, output_video_file):
  return [
      opencv_video_decoder.OpenCVVideoDecoderProcessor(
          {'input_video_file': input_video_file}),
      foreground_object_tracker.ForegroundObjectTracker({}),
      bounding_box_renderer.BoundingBoxRenderer({}),
      opencv_video_encoder.OpenCVVideoEncoderProcessor(
          {'output_video_file': output_video_file})
  ]


def main(unused_argv):
  processor_runner.run_processor_chain(
      pipeline(FLAGS.input_video_file, FLAGS.output_video_file))


if __name__ == '__main__':
  app.run(main)
