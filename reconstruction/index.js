var canvas = new fabric.Canvas('canvas');

//canvas.setBackgroundColor('rgba(0, 0, 0)', canvas.renderAll.bind(canvas));




//var video_original = document.getElementById("video_original");
var video_cursor = document.getElementById("video_cursor");

var cursor = new fabric.Circle({ radius: 3, fill: "#FF0000", top: 0, left: 0 });

var drawing_current_stroke = 0;
var drawing_current_substroke = 0;
var drawing_current_substroke_point = 0;

//Lines that represents the activity
function makeLine(coords, _color) {
    return new fabric.Line(coords, {
      fill: 'red',
      stroke: _color,
      strokeWidth: 1,
      selectable: true
    });
  }

var timeElapsed = 0;
var startTime;
var TimeMultiplier = 4235 / (15 * 15);

var color_drawing = "red";
var color_not_drawing = "green";

//canvas.add(cursor);

var width_normalizer = canvas.width / 1280;
var height_normalizer = canvas.height / 720;

canvas.setBackgroundImage(background_image, canvas.renderAll.bind(canvas), {
	
scaleX: width_normalizer,
scaleY: height_normalizer,
	
});


var cursor_x = 0;
var cursor_y = 0;

var current_cursor_index = 0;

//Hide the cursor in the start
x = -5; y = -5;

x_last_seen = x; y_last_seen = y; 

var IsPlaying = false;

var fps = 0;

//Get frames per second

 function animate() {
     
	 if (IsPlaying == false) return;	
	
	//-------------------
	
	//Check if it is time to display the next images
	timeElapsed =  new Date() - startTime;
	timeElapsed /= 1000; //get rid of the milliseconds
	
	
	//Feedback for the cursor position
	//get index of cursor data based on the timeElapsed
	
	//current_cursor_index is based on time: not a for loop
	current_cursor_index =  Math.round(timeElapsed * 15); //actual formula (timeElapsed * 1000) * (15 / 1000); 
	//x = cursor_data[current_cursor_index][0];
	//y = cursor_data[current_cursor_index][1];

	
	//-------------------
	
	x = data_list[current_cursor_index][0];
	y = data_list[current_cursor_index][1];
	
	if (x == -1)
	{
		x = x_last_seen;
		y = y_last_seen
	}
	
	else
	{
		x_last_seen = x;
		y_last_seen = y;
	}
	
	x *= width_normalizer;
	y *= height_normalizer;
	
	//Not drawing
	//if (data_list[current_cursor_index][2] == 0)
	if (IsDrawingUser(timeElapsed) == false) //check from the timestamp list if current index is drawn or not
	{
		cursor.setColor(color_not_drawing);
		//document.getElementById("txt_action").innerHTML = "No";
		//cursor.scale(parseFloat(0.5)).setCoords();
	}
	else 
	{
		cursor.setColor(color_drawing);
		//document.getElementById("txt_action").innerHTML = "Yes";
		//cursor.scale(parseFloat(1.5)).setCoords();
		
		//Draw a line joining the last point
		if (current_cursor_index > 0)
		{
		x1 = data_list[current_cursor_index][0] * width_normalizer;
		y1 = data_list[current_cursor_index][1] * height_normalizer;
		x2 = data_list[current_cursor_index - 1][0] * width_normalizer;
		y2 = data_list[current_cursor_index - 1][1] * height_normalizer;
		
		//Add a new stroke only if both current and last positions are defined
		if (data_list[current_cursor_index][0] != -1 && data_list[current_cursor_index - 1][0] != -1)
		{
		var line = makeLine([ x1, y1, x2, y2 ]);
		canvas.add(line);
		}
		
		}//if it is not the first point
		
	}//else drawing`
	
	cursor.animate({left:x, top:y}, { 
	onChange: canvas.renderAll.bind(canvas),
	duration: 36,
	onComplete: animate
	});
	
	//current_cursor_index++;
	fps++;
	
	//document.getElementById("txt_cursor").innerHTML = x + ", " + y;
	
	
	
  }//animate()



function startAnimation() {
	
	//DrawEverything();
	IsPlaying = true;
	DrawTimely();
	return;
	
	//This button should work only if video is not playing
	if (IsPlaying == false)
	{
	//loadCursorData();
	startTime = new Date() - new Date(timeElapsed * 1000);
	
	//Hide cursor when paused
	canvas.add(cursor);
	
	IsPlaying = true;
	//video_original.play();
	video_cursor.play();
	animate();
	}

}

function pauseAnimation() {
	
	//This button should work only if video is already playing
	if (IsPlaying == true)
	{
	IsPlaying = false;
	return;
	
	//Hide cursor when paused
	canvas.remove(cursor);
	//video_original.pause();
	video_cursor.pause();
	}
	
}

function IsDrawingUser(current){
	
	for (var i = 0; i < timestamps.length; i++)
	{
		if (current > timestamps[i][0] * TimeMultiplier && current < (timestamps[i][1]) * TimeMultiplier)
		{
			return true;
		}
	}
	
	return false;
	
	
	//if (timestamp > 100)
	//	return true;
	//else return false;
	
}




function DrawTimely()
{
	if (IsPlaying == false)
		return;
	
	current_stroke = strokes[drawing_current_stroke];
	current_start_pos = starting_pos[drawing_current_stroke];
	color = colors[drawing_current_stroke];
	_r = parseInt(color[0]);
	_g = parseInt(color[1]);
	_b = parseInt(color[2]);
	_color = 'rgb(' + _r + ',' + _g + ',' + _b + ')';
	
			local_x = strokes[drawing_current_stroke][drawing_current_substroke][drawing_current_substroke_point][0];
			local_y = strokes[drawing_current_stroke][drawing_current_substroke][drawing_current_substroke_point][1];
			
			if (drawing_current_substroke_point + 1 < strokes[drawing_current_stroke][drawing_current_substroke].length)
			{
				
			next_local_x = strokes[drawing_current_stroke][drawing_current_substroke][drawing_current_substroke_point + 1][0];
			next_local_y = strokes[drawing_current_stroke][drawing_current_substroke][drawing_current_substroke_point + 1][1];
			
			
			x1 = (parseInt(current_start_pos[0]) + parseInt(local_x)) * width_normalizer;
			y1 = (parseInt(current_start_pos[1]) + parseInt(local_y)) * height_normalizer;
			
			x2 = (parseInt(current_start_pos[0]) + parseInt(next_local_x)) * width_normalizer;
			y2 = (parseInt(current_start_pos[1]) + parseInt(next_local_y)) * height_normalizer;
			
			//console.log(x1 + ", " + y1 + "\n" + x2 + ", " + y2);
				
			var line = makeLine([ x1, y1, x2, y2 ], _color);
			canvas.add(line);
			}
			
	//Increment based on the state of the current variables.
	
	//Increment Point
	drawing_current_substroke_point++;
	
	if (drawing_current_substroke_point + 1 >= strokes[drawing_current_stroke][drawing_current_substroke].length)
	{
		drawing_current_substroke_point = 0;
		if (drawing_current_substroke == strokes[drawing_current_stroke].length - 1)
		{
			drawing_current_substroke = 0;
			drawing_current_stroke++;
		}
		else
		{
			drawing_current_substroke++;
		}
	}//if point is the last point in the current_substroke
	
	
	
	if (drawing_current_substroke < strokes.length)
	{
		
		x = 20;
		y = 20;
			cursor.animate({left:x, top:y}, { 
			onChange: canvas.renderAll.bind(canvas),
			duration: 36,
			onComplete: DrawTimely
			});
	}
	
	
}//DrawTimely




function DrawPartByPart()
{
	
	current_stroke = strokes[drawing_current_stroke];
	current_start_pos = starting_pos[drawing_current_stroke];
	color = colors[drawing_current_stroke];
	_r = parseInt(color[0]);
	_g = parseInt(color[1]);
	_b = parseInt(color[2]);
	_color = 'rgb(' + _r + ',' + _g + ',' + _b + ')';
	
			local_x = strokes[drawing_current_stroke][drawing_current_substroke][drawing_current_substroke_point][0];
			local_y = strokes[drawing_current_stroke][drawing_current_substroke][drawing_current_substroke_point][1];
			
			if (drawing_current_substroke_point + 1 < strokes[drawing_current_stroke][drawing_current_substroke].length)
			{
				
			next_local_x = strokes[drawing_current_stroke][drawing_current_substroke][drawing_current_substroke_point + 1][0];
			next_local_y = strokes[drawing_current_stroke][drawing_current_substroke][drawing_current_substroke_point + 1][1];
			
			
			x1 = (parseInt(current_start_pos[0]) + parseInt(local_x)) * width_normalizer;
			y1 = (parseInt(current_start_pos[1]) + parseInt(local_y)) * height_normalizer;
			
			x2 = (parseInt(current_start_pos[0]) + parseInt(next_local_x)) * width_normalizer;
			y2 = (parseInt(current_start_pos[1]) + parseInt(next_local_y)) * height_normalizer;
			
			//console.log(x1 + ", " + y1 + "\n" + x2 + ", " + y2);
				
			var line = makeLine([ x1, y1, x2, y2 ], _color);
			canvas.add(line);
			}
			
	//Increment based on the state of the current variables.
	
	//Increment Point
	drawing_current_substroke_point++;
	
	if (drawing_current_substroke_point + 1 >= strokes[drawing_current_stroke][drawing_current_substroke].length)
	{
		drawing_current_substroke_point = 0;
		if (drawing_current_substroke == strokes[drawing_current_stroke].length - 1)
		{
			drawing_current_substroke = 0;
			drawing_current_stroke++;
		}
		else
		{
			drawing_current_substroke++;
		}
	}//if point is the last point in the current_substroke
	
	
}//DrawPartByPart


function DrawEverything()
{

	
	
	//Drawing Stroke 0
	//stroke_number =0;
	
	for (stroke_number = 0; stroke_number < strokes.length; stroke_number++)
	{
		
	current_stroke = strokes[stroke_number];
	current_start_pos = starting_pos[stroke_number];
	color = colors[stroke_number];
	
	//console.log(color);
	_r = parseInt(color[0]);
	_g = parseInt(color[1]);
	_b = parseInt(color[2]);
	_color = 'rgb(' + _r + ',' + _g + ',' + _b + ')';
	
	for (_sub_stroke = 0; _sub_stroke < strokes[stroke_number].length; _sub_stroke++)
	{
		
		for (_point = 0; _point < strokes[stroke_number][_sub_stroke].length; _point++)
		{
			local_x = strokes[stroke_number][_sub_stroke][_point][0];
			local_y = strokes[stroke_number][_sub_stroke][_point][1];
			
			if (_point + 1 < strokes[stroke_number][_sub_stroke].length)
			{
				
			next_local_x = strokes[stroke_number][_sub_stroke][_point + 1][0];
			next_local_y = strokes[stroke_number][_sub_stroke][_point + 1][1];
			
			
			
			x1 = (parseInt(current_start_pos[0]) + parseInt(local_x)) * width_normalizer;
			y1 = (parseInt(current_start_pos[1]) + parseInt(local_y)) * height_normalizer;
			
			x2 = (parseInt(current_start_pos[0]) + parseInt(next_local_x)) * width_normalizer;
			y2 = (parseInt(current_start_pos[1]) + parseInt(next_local_y)) * height_normalizer;
			
			//console.log(x1 + ", " + y1 + "\n" + x2 + ", " + y2);
				
			var line = makeLine([ x1, y1, x2, y2 ], _color);
			canvas.add(line);
			}
			
		}//for all the consecutive points
		
		
	}//for all the substrokes
	
	}//for all the strokes
	
	
	console.log("Drawn");
	//canvas.add(cursor);
	//canvas.renderAll.bind(canvas);
	
}//DrawEverything


//Prvious Lists:
//data_list = [[cur_pos_x, cur_pos_y], ...]
//timestamps = [[start_time, end_time], ...]
