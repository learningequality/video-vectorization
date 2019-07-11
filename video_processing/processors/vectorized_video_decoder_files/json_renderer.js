$(document).ready(function() {
  latest_time = 0;
  latest_obj = 0;
  latest_stroke = 0;
  latest_sub_stroke = 0;
  paper_scope = new paper.PaperScope();

  $.get('data.json', function(data) {
    init_canvas(data);
  });
});


/**
 * Initializes the canvas.
 * @param {string} data - The JSON data to be rendered.
 */
function init_canvas(data) {
  json_data = data;
  // TODO: ORIGINAL DIMENSIONS SHOULD BE IN THE JSON.
  orig_width = 1280;
  orig_height = 720;
  frame_rate_hz = parseFloat(json_data.frames_per_second);
  modify_json();
  paper_scope.setup($('.vector_canvas')[0]);
  paper_scope.view.onFrame = increment_frame_and_render;
  reset_canvas();
}

/**
 * Increments the frame and renders the canvas.
 */
function increment_frame_and_render() {
  render_canvas();
  latest_time += 1.0 / frame_rate_hz;
}

/**
 * Resets the canvas.
 */
function reset_canvas() {
  latest_time = 0;
  latest_obj = 0;
  latest_stroke = 0;
  latest_sub_stroke = 0;
  cursor = null;
  paper_scope.project.clear();
  resize_canvas();
  add_bg();
}

/**
 * Resize the canvas.
 */
function resize_canvas() {
  var vector_canvas_wrapper = $('.vector_canvas_wrapper');
  vector_canvas_wrapper_width = vector_canvas_wrapper.width();
  vector_canvas_wrapper_height = vector_canvas_wrapper.height();
  paper_scope.view.viewSize =
      new paper.Size(vector_canvas_wrapper_width, vector_canvas_wrapper_height);
}


/**
 * Adds the background.
 */
function add_bg() {
  var that = this;
  var bg_img = new paper_scope.Raster({source: 'background.png'});

  bg_img.onLoad = function() {
    bg_img.size = that.paper_scope.view.viewSize;
    bg_img.position = that.paper_scope.view.center;
  };
}


/**
 * Adds fps, cursor update rate, exact x and y values of every sub stroke,
 * stroke time start and end times, and sub stroke start times.
 */
function modify_json() {
  var data = json_data;

  // CALCULATE FPS AND HOW OFTEN, IN TERMS OF TIME, THE CURSOR SHOULD BE UPDATED
  data.actual_fps = data.cursor.length / parseFloat(data.total_time);
  data.cursor_update_rate = parseFloat(data.total_time) / data.cursor.length;

  // LOOP THROUGH ALL OBJECTS
  for (var obj = 0; obj < data.operations.length; obj++) {
    // var obj_offset_x = parseInt(data.operations[obj].offset_x);
    // var obj_offset_y = parseInt(data.operations[obj].offset_y);
    var obj_start_time = parseFloat(data.operations[obj].start);
    var obj_end_time = parseFloat(data.operations[obj].end);
    // TODO: ADJUST THE OBJECT DURATION BY DIVIDING OR SUBTRACTING BY SOMETHING
    // 0.5 IS JUST A GUESS
    var obj_dur = (obj_end_time - obj_start_time) * 0.5;
    var obj_dist = 0;
    var stroke_distances = [];

    // LOOP THROUGH ALL STROKES IN ONE OBJECT
    for (var stroke = 0; stroke < data.operations[obj].strokes.length;
         stroke++) {
      var stroke_dist = 0;
      // LOOP THROUGH ALL SUB STROKES IN ONE STROKE
      for (var sub_stroke = 0;
           sub_stroke < data.operations[obj].strokes[stroke].length - 1;
           sub_stroke++) {
        var x_cord =
            parseInt(data.operations[obj].strokes[stroke][sub_stroke][0]);
        var y_cord =
            parseInt(data.operations[obj].strokes[stroke][sub_stroke][1]);
        var x_cord_nxt =
            parseInt(data.operations[obj].strokes[stroke][(sub_stroke + 1)][0]);
        var y_cord_nxt =
            parseInt(data.operations[obj].strokes[stroke][(sub_stroke + 1)][1]);
        var sub_stroke_dist = Math.sqrt(
            Math.pow((x_cord_nxt - x_cord), 2) +
            Math.pow((y_cord_nxt - y_cord), 2));
        stroke_dist += sub_stroke_dist;

        // ADD EXACT X AND Y COORDINATES TO EVERY SUB STROKE
        data.operations[obj].strokes[stroke][sub_stroke].x = x_cord;
        data.operations[obj].strokes[stroke][sub_stroke].y = y_cord;
      }

      stroke_distances.push(stroke_dist);
      obj_dist += stroke_dist;
    }

    // GO THROUGH ARRAY
    for (var i = 0; i < stroke_distances.length; i++) {
      var stroke_dur = (parseFloat(stroke_distances[i]) / obj_dist) * obj_dur;

      if (i === 0) {
        data.operations[obj].strokes[i].stroke_start_time = obj_start_time;
        data.operations[obj].strokes[i].stroke_end_time =
            obj_start_time + stroke_dur;
      } else {
        data.operations[obj].strokes[i].stroke_start_time =
            parseFloat(data.operations[obj].strokes[i - 1].stroke_end_time);
        data.operations[obj].strokes[i].stroke_end_time =
            parseFloat(data.operations[obj].strokes[i - 1].stroke_end_time) +
            stroke_dur;
      }

      // LOOP THROUGH ALL SUB STROKES AND ADD SUB STROKE START TIME
      for (var j = 0; j < data.operations[obj].strokes[i].length; j++) {
        var stroke_start_time =
            parseFloat(data.operations[obj].strokes[i].stroke_start_time);
        var ratio = j / parseFloat(data.operations[obj].strokes[i].length);
        var sub_stroke_start_time = stroke_dur * ratio;
        data.operations[obj].strokes[i][j].sub_stroke_start_time =
            stroke_start_time + sub_stroke_start_time;
      }
    }
  }
}



/**
 * Draws the appropriate strokes on the canvas based on the value of
 * latest_time.
 */
function render_canvas() {
  // GET CURRENT WIDTH AND HEIGHT

  var width_adjust = vector_canvas_wrapper_width / orig_width;
  var height_adjust = vector_canvas_wrapper_height / orig_height;

  render_cursor(width_adjust, height_adjust);

  // As we loop through the data structure below, this value is updated.
  var more_to_render = false;

  // UPDATE STROKES
  // LOOP THROUGH OBJECTS
  for (var obj = latest_obj; obj < json_data.operations.length; obj++) {
    if ((parseFloat(json_data.operations[obj].start)) > latest_time) {
      more_to_render = true;
      continue;
    }
    latest_obj = obj;

    var red = parseInt(json_data.operations[obj].color[0]) / 255;
    var green = parseInt(json_data.operations[obj].color[1]) / 255;
    var blue = parseInt(json_data.operations[obj].color[2]) / 255;

    // LOOP THROUGH STROKES
    for (var stroke = latest_stroke;
         stroke < json_data.operations[obj].strokes.length; stroke++) {
      if (((parseFloat(
               json_data.operations[obj].strokes[stroke].stroke_start_time)) >
           latest_time)) {
        more_to_render = true;
        continue;
      }
      latest_stroke = stroke;
      // LOOP THROUGH SUB STROKES
      for (var sub_stroke = latest_sub_stroke;
           sub_stroke < json_data.operations[obj].strokes[stroke].length - 1;
           sub_stroke++) {
        if (((parseFloat(json_data.operations[obj]
                             .strokes[stroke][sub_stroke]
                             .sub_stroke_start_time)) > latest_time)) {
          more_to_render = true;
          continue;
        }
        var curr_sub_stroke =
            json_data.operations[obj].strokes[stroke][sub_stroke];
        var nxt_sub_stroke =
            json_data.operations[obj].strokes[stroke][sub_stroke + 1];
        var curr_sub_stroke_x = parseFloat(curr_sub_stroke.x) * width_adjust;
        var curr_sub_stroke_y = parseFloat(curr_sub_stroke.y) * height_adjust;
        var nxt_sub_stroke_x = parseFloat(nxt_sub_stroke.x) * width_adjust;
        var nxt_sub_stroke_y = parseFloat(nxt_sub_stroke.y) * height_adjust;

        // DRAW
        var sub_stroke_path = new paper_scope.Path.Line(
            (new paper_scope.Point(curr_sub_stroke_x, curr_sub_stroke_y)),
            (new paper_scope.Point(nxt_sub_stroke_x, nxt_sub_stroke_y)));
        sub_stroke_path.strokeColor = new paper_scope.Color(red, green, blue);
        sub_stroke_path.strokeCap = 'round';
        sub_stroke_path.strokeJoin = 'round';
        sub_stroke_path.strokeWidth = 2;

        // IF LAST SUBSTROKE AND LAST STROKE
        if ((sub_stroke ==
             json_data.operations[obj].strokes[stroke].length - 2) &&
            (stroke == json_data.operations[obj].strokes.length - 1)) {
          latest_sub_stroke = 0;
          latest_stroke = 0;
          latest_obj++;
        }
        // IF JUST LAST SUBSTROKE
        else if (
            sub_stroke ==
            json_data.operations[obj].strokes[stroke].length - 2) {
          latest_sub_stroke = 0;
          latest_stroke++;
        } else {
          latest_sub_stroke = sub_stroke + 1;
        }
      }
    }
  }
  if (more_to_render) {
    var src = $('.vector_canvas')[0].toDataURL('image/png');
    var xhttp = new XMLHttpRequest();
    xhttp.open('POST', '\/', true);
    xhttp.send(src);
  } else {
    var xhttp = new XMLHttpRequest();
    xhttp.open('POST', '\/DONE', true);
    xhttp.send('Rendering complete!');
  }
}


/**
 * Renders the cursor on the canvas.
 * @param {float!} width_adjust - The adjusted width of the canvas.
 * @param {float!} height_adjust - The adjusted height of the canvas.
 */
function render_cursor(width_adjust, height_adjust) {
  var cursor_index = parseInt(
      (latest_time / parseFloat(json_data.total_time)) *
      json_data.cursor.length);

  if (cursor_index < json_data.cursor.length) {
    var cursor_x = (parseInt(json_data.cursor[cursor_index][0])) * width_adjust;
    var cursor_y =
        (parseInt(json_data.cursor[cursor_index][1])) * height_adjust;

    if (cursor) {
      cursor.position = new paper_scope.Point(cursor_x, cursor_y);
    } else {
      cursor = new paper_scope.Path.Circle({
        center: new paper_scope.Point(cursor_x, cursor_y),
        radius: 2,
        fillColor: 'white'
      });
    }
  }
}
