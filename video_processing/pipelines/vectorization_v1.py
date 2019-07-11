"""Pipeline to decode and reencode a video using OpenCV."""
from absl import app
from absl import flags

from video_processing import processor_runner
from video_processing.processors import added_object_tracker
from video_processing.processors import background_image_extractor
from video_processing.processors import cursor_tracker
from video_processing.processors import json_writer
from video_processing.processors import opencv_video_decoder
from video_processing.processors import opencv_video_encoder
from video_processing.processors import stroke_tracker

flags.DEFINE_string('input_video_file', '', 'Input file.')
flags.DEFINE_string('output_video_file', '', 'Output file.')
flags.DEFINE_string('cursor_template_file', '', 'Cursor template file.')

flags.DEFINE_string('background_image_file', 'background.png',
                    'Background image file to be written for output.')
flags.DEFINE_string('output_json_file', 'data.json', 'Output json file.')

FLAGS = flags.FLAGS


def pipeline(input_video_file, output_video_file, cursor_template_file,
             background_image_file, output_json_file):
  return [
      opencv_video_decoder.OpenCVVideoDecoderProcessor(
          {'input_video_file': input_video_file}),
      background_image_extractor.FirstFrameBackgroundImageExtractor(
          {'background_image_file_name': background_image_file}),
      cursor_tracker.CursorTracker(
          {'cursor_template_file': cursor_template_file}),
      added_object_tracker.AddedObjectTracker({}),
      stroke_tracker.StrokeTracker({}),
      json_writer.JSONWriter({
          'output_json_file': output_json_file,
          'background_image_file': background_image_file
      }),
      opencv_video_encoder.OpenCVVideoEncoderProcessor(
          {'output_video_file': output_video_file})
  ]


def main(unused_argv):
  processor_runner.run_processor_chain(
      pipeline(FLAGS.input_video_file, FLAGS.output_video_file,
               FLAGS.cursor_template_file, FLAGS.background_image_file,
               FLAGS.output_json_file))


if __name__ == '__main__':
  app.run(main)
