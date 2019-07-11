"""Video decoder that renders a vectorized JSON file to video frames.

Internally, this class brings up an HTTP server in a separate thread to serve
the JSON and javascript player to a headless Chrome instance, which then
writes image frames as PNGs back to the server. I know.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import atexit
import base64
import json
import os
import subprocess
import threading

import numpy
import six.moves.BaseHTTPServer
import six.moves.queue

from video_processing import stream_processor
import cv2

# TODO(tomwalters): Dynamically place these variables into the HTML and JS.
SERVER_PORT = 62061
CANVAS_WIDTH = 1280
CANVAS_HEIGHT = 720
NUM_FRAMES = 959
RENDERER_FILES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                  'vectorized_video_decoder_files')


class VectorizationServer(six.moves.BaseHTTPServer.HTTPServer):
  """Server with associated data, to be used with VectorizationServerHandler."""

  def setup(self,
            image_callback=None,
            json_data=None,
            background_image=None,
            index_html=None,
            player_js=None):
    """Set data to be served and POST callback function for images returned."""
    self.image_callback = image_callback
    self.json_data = json_data
    self.background_image = background_image
    self.index_html = index_html
    self.player_js = player_js
    self.rendering_started = False
    self.rendering_complete = False
    # Mapping of URLs to serve to data and associated MIME types.
    self.data_map = {
        '/': (index_html, 'text/html'),
        '/vectorvideoplayer.js': (player_js, 'application/javascript'),
        '/data.json': (json_data, 'application/json'),
        '/background.png': (background_image, 'image/png'),
    }


class VectorizationServerHandler(six.moves.BaseHTTPServer.BaseHTTPRequestHandler
                                ):
  """Handler sending and receiving content for the renderer process."""

  # Suppress log messages.
  def log_request(self, code):
    pass

  def do_GET(self):
    """Handle GET requests for content to be served."""
    response = self.server.data_map.get(self.path, None)
    self.protocol_version = 'HTTP/1.1'
    if response is None:
      self.send_response(404)
      self.end_headers()
      self.wfile.write(bytes('404: Not Found'))
    self.protocol_version = 'HTTP/1.1'
    self.send_response(200, 'OK')
    self.send_header('Content-type', response[1])
    self.end_headers()
    self.wfile.write(bytes(response[0]))
    self.server.rendering_started = True
    return

  def do_POST(self):
    """Handle POST requests of images back to the server."""
    if self.path != '/':
      self.server.rendering_complete = True
    elif self.server.image_callback is not None:
      content_length = int(self.headers['Content-Length'])
      post_data = self.rfile.read(content_length)
      image_base64 = post_data.split(b',')[1]
      image_data = base64.b64decode(image_base64)
      decoded_image = cv2.imdecode(
          numpy.fromstring(image_data, dtype='uint8'), 1)
      self.server.image_callback(decoded_image)
    self.send_response(200)
    self.end_headers()
    self.wfile.write(bytes('200'))


class ServerThread(threading.Thread):
  """Thread running a server to get content to and from the renderer."""

  def __init__(self, server):
    super(ServerThread, self).__init__()
    self.daemon = True
    self._server = server
    self.start()

  def run(self):
    # Because this is run in a daemon thread, the thread will be automatically
    # killed at program exit.
    self._server.serve_forever()


class VectorizedVideoDecoderProcessor(stream_processor.ProcessorBase):
  """Processor for decoding vectorized video."""

  def __init__(self, configuration):
    self._input_json_file = configuration.get('input_json_file', '')
    self._background_image_file = configuration.get('background_image_file', '')

    self._renderer_js_file = configuration.get(
        'renderer_js_file', RENDERER_FILES_DIR + '/json_renderer.js')
    self._renderer_html_file = configuration.get(
        'renderer_html_file', RENDERER_FILES_DIR + '/renderer.html')

    self._video_stream_name = configuration.get('video_stream_name', 'video')
    self._frame_queue = six.moves.queue.Queue()
    self._server_port = SERVER_PORT

    with open(self._background_image_file, 'r') as image_file:
      self._background_image_data = image_file.read()
    self._frame_width = CANVAS_WIDTH
    self._frame_height = CANVAS_HEIGHT
    self._num_frames = NUM_FRAMES

    with open(self._input_json_file, 'r') as json_file:
      self._json_string = json_file.read()

    self._json_data = json.loads(self._json_string)
    self._num_frames = int(self._json_data['total_frames'])

    with open(self._renderer_js_file, 'r') as js_file:
      js_string = js_file.read()
    with open(self._renderer_html_file, 'r') as html_file:
      html_string = html_file.read()

    self._server = VectorizationServer(('127.0.0.1', self._server_port),
                                       VectorizationServerHandler)
    self._server.setup(
        image_callback=self._frame_queue.put,
        json_data=self._json_string,
        background_image=self._background_image_data,
        index_html=html_string,
        player_js=js_string)

    self._server_thread = ServerThread(server=self._server)
    self._renderer_process = None
    self._frame_index = 0

  def open(self, stream_set):
    self._renderer_process = subprocess.Popen([
        'google-chrome',
        '--headless',
        '--remote-debugging-port=9222',
        'http://127.0.0.1:%s/' % self._server_port,
        '--window-size=1300,800',  # TODO(tomwalters): Plumb in correct dimensions.
        '--autoplay-policy=no-user-gesture-required',
        '--mute-audio'
    ])
    # Ensure this process gets terminated when the program ends.
    atexit.register(self._renderer_process.terminate)

    frame_rate_hz = float(self._json_data['frames_per_second'])
    if stream_set.frame_rate_hz < 0:
      # If the frame rate wasn't set, then we can assume that we're the top
      # of the processing chain and create a new stream set object to
      # contain the video stream.
      stream_set = stream_processor.StreamSet(frame_rate_hz=frame_rate_hz)
    else:
      if stream_set.frame_rate_hz != frame_rate_hz:
        raise Exception('Frame rate in additional video stream is not equal to '
                        'that of the original stream set.')
    stream_set.stream_headers[
        self._video_stream_name] = stream_processor.StreamHeader(
            frame_data_type=numpy.ndarray,
            header_data=stream_processor.VideoStreamHeader(
                self._frame_width, self._frame_height, self._num_frames))
    return stream_set

  def process(self, frame_set):
    block = True
    timeout = .25  # Wait up to 250ms for the next frame.
    # If the rendering process hasn't started rendering yet, give it a bit of
    # time to get going.
    if not self._server.rendering_started:
      timeout = 10.0  # 10 seconds of startup time for the browser.
    # If the rendering is done in the browser, we should not block on the frame
    # queue since nothing else is populating it.
    if self._server.rendering_complete:
      block = False
    try:
      frame_data = self._frame_queue.get(block=block, timeout=timeout)
      frame_set[self._video_stream_name] = stream_processor.Frame(
          self._frame_index, frame_data)
    except six.moves.queue.Empty:
      if not self._server.rendering_complete:
        print('Frame queue became empty before rendering completed. '
              'Possible loss of video frames.')
    self._frame_index += 1
    return frame_set

  def close(self):
    self._renderer_process.terminate()
    return []
