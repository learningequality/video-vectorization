# Copyright 2019 Google LLC.
"""Renders a vectorized video to a video file."""

from absl import app
from absl import flags

from video_processing import processor_runner
from video_processing.processors import opencv_video_encoder
from video_processing.processors import vectorized_video_decoder

flags.DEFINE_string('input_json_file', '', 'Input file.')
flags.DEFINE_string('background_image_file', 'background.png',
                    'Background image to be used.')
flags.DEFINE_string('output_video_file', '', 'Output file.')

FLAGS = flags.FLAGS


def pipeline(input_json_file, background_image_file, output_video_file):
  return [
      vectorized_video_decoder.VectorizedVideoDecoderProcessor({
          'input_json_file': input_json_file,
          'background_image_file': background_image_file
      }),
      opencv_video_encoder.OpenCVVideoEncoderProcessor(
          {'output_video_file': output_video_file})
  ]


def main(unused_argv):
  processor_runner.run_processor_chain(
      pipeline(FLAGS.input_json_file, FLAGS.background_image_file,
               FLAGS.output_video_file))


if __name__ == '__main__':
  app.run(main)
