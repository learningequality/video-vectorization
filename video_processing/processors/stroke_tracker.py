"""Tracks strokes in indiviual objects.

Adds a stream containing individual added object images, along with their
extents, and a track of the location of the cursor around the time that the
object was drawn.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import copy
import itertools
import math
import numpy as np
from igraph import Graph
from six.moves import range
from video_processing import stream_processor
import cv2
import random


def object_to_binarized_sub_objects(image):
  """Takes an image of a character and splits into discontinuous sub-strokes.

  Sub strokes are returned as binary images each of the same dimensions as the
  original image.

  Args:
    image:

  Returns:
    List of images.
  """
  binary_threshold = 50
  _, bw_image = cv2.threshold(image, binary_threshold, 255, 0)
  contour_image = copy.deepcopy(bw_image)
  contours, _ = cv2.findContours(contour_image, cv2.RETR_EXTERNAL,
                                    cv2.CHAIN_APPROX_SIMPLE)
  masks = []
  for i in range(0, len(contours)):
    x, y, w, h = cv2.boundingRect(contours[i])
    mask = np.zeros(bw_image.shape, np.uint8)
    mask[y:y + h, x:x + w] = bw_image[y:y + h, x:x + w]
    masks.append(mask)
  return masks


def thinning_iteration(image, iteration):
  """One iteration of the thinning function."""
  image = image.astype(np.uint8)
  mask = np.zeros(image.shape, np.uint8)
  for i in range(1, image.shape[0] - 1):
    for j in range(1, image.shape[1] - 1):
      p2 = image[i - 1][j]
      p3 = image[i - 1][j + 1]
      p4 = image[i][j + 1]
      p5 = image[i + 1][j + 1]
      p6 = image[i + 1][j]
      p7 = image[i + 1][j - 1]
      p8 = image[i][j - 1]
      p9 = image[i - 1][j - 1]
      adjacent = (int(p2 == 0 and p3 > 0) + int(p3 == 0 and p4 > 0) +
                  int(p4 == 0 and p5 > 0) + int(p5 == 0 and p6 > 0) +
                  int(p6 == 0 and p7 > 0) + int(p7 == 0 and p8 > 0) +
                  int(p8 == 0 and p9 > 0) + int(p9 == 0 and p2 > 0))
      total = p2 + p3 + p4 + p5 + p6 + p7 + p8 + p9
      m1 = (p2 * p4 * p6) if iteration == 0 else (p2 * p4 * p8)
      m2 = (p4 * p6 * p8) if iteration == 0 else (p2 * p6 * p8)
      if adjacent == 1 and total >= 2 and total <= 6 and m1 == 0 and m2 == 0:
        mask[i][j] = 1
  return image & ~mask


def thin(src):
  """Thin elemets in src."""
  # First close small gaps.
  kernel = np.ones((3,3),np.uint8)
  closing = cv2.morphologyEx(src, cv2.MORPH_CLOSE, kernel)
  opening = cv2.morphologyEx(closing, cv2.MORPH_CLOSE, kernel)
  dst = opening.copy() / 255
  prev = np.zeros(src.shape[:2], np.uint8)

  while True:
    dst = thinning_iteration(dst, 0)
    dst = thinning_iteration(dst, 1)
    diff = np.absolute(dst - prev)
    prev = dst.copy()
    if np.sum(diff) == 0:
      break

  return dst * 255


def points_list_from_sub_image(binary_sub_image):
  """Returns a list of (x, y) coordinates of lit pixels in the thinned image."""
  thinned_img = thin(binary_sub_image)
  data_pts_thinned = np.nonzero(thinned_img)
  data_pts_thinned = list(zip(data_pts_thinned[1], data_pts_thinned[0]))
  return data_pts_thinned


def is_neighbor_text(x, y, image):
  kernel = np.ones((5, 5), np.uint8)
  dilation = cv2.dilate(image, kernel, iterations = 1)
  return dilation[y, x] > 0
  #i = image
  #d = dimensions
  #return ((i[y, x] > 0) or (y + 1 < d[1] and i[y + 1, x] > 0) or
  #        (y - 1 >= 0 and i[y - 1, x] > 0) or
  #        (x + 1 < d[0] and i[y, x + 1] > 0) or
  #        (x + 1 < d[0] and y + 1 < d[1] and i[y + 1, x + 1] > 0) or
  #        (y - 1 >= 0 and x + 1 < d[0] and i[y - 1, x + 1] > 0) or
  #        (x - 1 >= 0 and i[y, x - 1] > 0) or
  #        (y + 1 < d[1] and x - 1 >= 0 and i[y + 1, x - 1] > 0) or
  #        (y - 1 >= 0 and x - 1 >= 0 and i[y - 1, x - 1] > 0))


def find_closest_point(node, nodes):
  nodes = np.asarray(nodes)
  dist_2 = np.sum((nodes - node)**2, axis=1)
  return nodes[np.argmin(dist_2)]


def find_candidate_pen_locations(cursor_track, stroke_points_list,
                                 binary_stroke_image):
  """Args:

    cursor_track: Tracked cursor location (relative to the stroke image).
    stroke_points_list: List of points in the relevant stroke (relative to the
    stroke image).
    binary_stroke_image: Binarized image of the stroke.
  """
  valid_cursor_positions = []

  if not stroke_points_list:
    return valid_cursor_positions

  # Start the cursor at an arbitrary point far offscreen.
  last_x = -1000
  last_y = -1000

  for i in range(0, len(cursor_track)):
    x = int(cursor_track[i][0])
    y = int(cursor_track[i][1])
    dim = binary_stroke_image.shape[1::-1]
    # if a point is within the boundary box of the object
    if 0 <= x < dim[0] and 0 <= y < dim[1]:
      #if ((is_neighbor_text(x, y, binary_stroke_image)) and
      if ((abs(x - last_x) + abs(y - last_y)) > 3):
        # Map x, y to the closest point
        [mapped_x, mapped_y] = find_closest_point([x, y], stroke_points_list)
        valid_cursor_positions.append((mapped_x, mapped_y))
    last_x = x
    last_y = y
  return valid_cursor_positions


def compute_all_edges(data_pts):
  """Compute all edges."""
  graph_connections = []

  for current in range(0, len(data_pts)):
    adjacent = [
        data_pts.index(x)
        for x in data_pts
        if (abs(x[0] - data_pts[current][0]) < 2) and
        (abs(x[1] - data_pts[current][1]) < 2) and
        (x[0] != data_pts[current][0] or x[1] != data_pts[current][1])
    ]

    for a in adjacent:
      graph_connections.append((current, a))

  # Remove duplicates
  list_with_duplicates = sorted([sorted(x) for x in graph_connections])
  result = list(
      list_with_duplicates
      for list_with_duplicates, _ in itertools.groupby(list_with_duplicates))
  return result


def reconstruct_pen_track_from_stroke_points_and_cursor_track(
    points_list, cursor_positions):
  g = Graph()
  g.add_vertices(len(points_list))
  # Create an adjacency matrix of data points - based on
  # 8-connectivity
  g.add_edges(compute_all_edges(points_list))
  g.vs["point"] = points_list
  # Calculate Paths between cursor positions
  path_points_ordered = []  # contains the temporal information, this
  #  is used for in-between points as well
  path_points = []

  for index_cursor_point in range(1, len(cursor_positions)):
    start_vertex = g.vs.find(point=cursor_positions[index_cursor_point - 1])
    end_vertex = g.vs.find(point=cursor_positions[index_cursor_point])
    shortest_path = g.get_all_shortest_paths(start_vertex, end_vertex)

    if not shortest_path:
      path_points_ordered.append([])
    else:
      # Path exists.
      path_between_strokes = []

      for point in shortest_path[0]:
        path_points.append(g.vs[point]['point'])
        # Save path points so that we can delete them later on
        path_between_strokes.append(g.vs[point]['point'])

      path_points_ordered.append(path_between_strokes)

  # 1st pass:
  # Remove all points used in any path - except data points
  path_points = list(set(path_points))
  # Remove multiple entries first

  for i in path_points:
    if i not in cursor_positions:
      g.delete_vertices(g.vs.find(point=i))

  # 2nd pass:
  # Remove isolated points
  isolated_points = []
  for i in range(0, len(g.vs)):
    if len(g.incident(g.vs[i])) == 0:
      isolated_points.append(g.vs[i]['point'])

  for i in isolated_points:
    g.delete_vertices(g.vs.find(point=i))

  # 3rd pass:
  # Originating from the cursor_positions, DFS? overkill to all
  # possible positions
  # Take care of the timing of these auxiliary points - push other
  # boundaries to make room for these

  # Get List of cursor points that have something attached to them
  for cursor_no in range(0, len(cursor_positions)):
    if cursor_positions[cursor_no] not in g.vs['point']:
      continue

    paths = g.shortest_paths_dijkstra(source=g.vs.find(
      point=cursor_positions[cursor_no]))

    if not paths:
      continue

    # Result of shortest paths is a list of lists with one outermost element.
    paths = paths[0]
    missed_points = []

    for pt_in_path in range(0, len(paths)):
      if ((paths[pt_in_path] > 0) and not math.isinf(paths[pt_in_path])):
        missed_points.append(
            [paths[pt_in_path],
             g.vs[pt_in_path]['point']])

    # Add missed points to the path_points_ordered list
    # If first cursor position, put before cursor position
    #  in first list
    # If last cursor position, put after cursor position
    #  in last list
    # If btw first and last, put before cursor position
    #  in that list
    missed_points = sorted(missed_points)

    if ((cursor_no == len(cursor_positions) - 1) and
        (len(cursor_positions) > 1)):
      # Last and has more than one valid cursor
      for pt in range(0, len(missed_points)):
        path_points_ordered[cursor_no - 1].append(missed_points[pt][1])
        # 1 is the actual data
    else:  # First or any other except last
      for pt in range(0, len(missed_points)):
        if path_points_ordered:
          path_points_ordered[cursor_no].insert(
              0, missed_points[len(missed_points) - pt - 1][1])
        else:
          path_points_ordered.append([])

  return path_points_ordered


def relative_to_bounding_box(points, bounding_box):
  return [[p[0] - bounding_box[0], p[1] - bounding_box[1]] for p in points]


def relative_to_canvas(points, bounding_box):
  return [[p[0] + bounding_box[0], p[1] + bounding_box[1]] for p in points]


def sub_object_to_stroke(binary_stroke_image, bounding_box, cursor_track):
  # Get a list of the points in the stroke image (relative to the stroke image).
  local_points_list = points_list_from_sub_image(binary_stroke_image)
  # Use the list of points in the stroke and the track of where the cursor was
  # seen while the stroke was being drawn, and the original binarized image to
  # get a list of likely locations for the pen that drew the stroke over time.
  local_pen_locations = find_candidate_pen_locations(
      relative_to_bounding_box(cursor_track, bounding_box), local_points_list,
      binary_stroke_image)

  # Use the list of pen locations, and all the points in the stroke to infer an
  # ordered list of points that can be used to draw the stroke.
  local_stroke = reconstruct_pen_track_from_stroke_points_and_cursor_track(
      local_points_list, local_pen_locations)
  flatten = lambda l: [i for s in l for i in s]
  s = flatten(local_stroke)
  # s = local_pen_locations
  return relative_to_canvas(s, bounding_box)


class StrokeTracker(stream_processor.ProcessorBase):
  """Processor tracking pen strokes in regions."""

  def __init__(self, configuration):
    self._object_stream_name = configuration.get('object_stream_name',
                                                 'objects')
    self._stroke_stream_name = configuration.get('stroke_stream_name',
                                                 'strokes')

  def open(self, stream_set):
    stream_set.stream_headers[
        self._stroke_stream_name] = stream_processor.StreamHeader(
            frame_data_type={}, header_data=[])
    return stream_set

  def process(self, frame_set):
    if not frame_set.get(self._object_stream_name, False):
      return frame_set

    object_data = frame_set[self._object_stream_name].data
    frame_index = frame_set[self._object_stream_name].index
    object_image = object_data['crop']
    cursor_path = object_data['strokes'][0]
    bounding_box = object_data['bounding_box']
    if object_image.shape[0] > 0 and object_image.shape[1] > 0:
      object_image = cv2.cvtColor(object_image, cv2.COLOR_BGR2GRAY)
      sub_objects = object_to_binarized_sub_objects(object_image)
      sub_strokes = []
      for sub_object in sub_objects:
        stroke = sub_object_to_stroke(sub_object, bounding_box, cursor_path)
        sub_strokes.append(stroke)
      stroke_data = {
          'start': object_data['start'],
          'end': object_data['end'],
          'strokes': sub_strokes,
          'color': object_data['color']
      }
      frame_set[self._stroke_stream_name] = stream_processor.Frame(
          frame_index, stroke_data)
    return frame_set

  def close(self):
    return []
