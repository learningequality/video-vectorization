/*
var canvas = new fabric.StaticCanvas('canvas', { 
      renderOnAddRemove: false,
    });
*/

var canvas = document.getElementById("canvas");
var canvasWidth = canvas.width;
var canvasHeight = canvas.height;
var ctx = canvas.getContext("2d");
var canvasData = ctx.getImageData(0, 0, canvasWidth, canvasHeight);	


//Background Image
var back_image = document.getElementById("back_image");
back_image.src = background_image;
back_image.width = canvasWidth;
back_image.height = canvasHeight;

//Video Set
var video_source = document.getElementById('video_source');
video_source.setAttribute('src', video_name);
	

var myTimerDrawing; //to draw the vectors
var myTimerRendering; //to render the frame at an independent rate
	
	
var video_feed = document.getElementById("video_feed");


var drawing_current_stroke = 0;
var drawing_current_substroke = 0;
var drawing_current_substroke_point = 0;
var points_drawn_in_current_stroke = 0;

var timeElapsed = 0;
var startTime;
//var TimeMultiplier = 4235 / (15 * 15);

var color_drawing = "red";
var color_not_drawing = "green";

var width_normalizer = canvas.width / 1280;
var height_normalizer = canvas.height / 720;


//Setting the background image
/*
canvas.setBackgroundImage(background_image, canvas.renderAll.bind(canvas), {
	
scaleX: width_normalizer,
scaleY: height_normalizer,
	
});
*/


// That's how you define the value of a pixel //
function drawPixel (x, y, r, g, b, a) {
    var index = (x + y * canvasWidth) * 4;

	
    canvasData.data[index + 0] = r;
    canvasData.data[index + 1] = g;
    canvasData.data[index + 2] = b;
    canvasData.data[index + 3] = a;
	
}

// That's how you update the canvas, so that your //
// modification are taken in consideration //
function updateCanvas() {
	
    ctx.putImageData(canvasData, 0, 0);
	
}


var cursor_x = 0;
var cursor_y = 0;

var current_cursor_index = 0;

//Hide the cursor in the start
x = -5; y = -5;

x_last_seen = x; y_last_seen = y; 

var IsPlaying = false;

var fps = 0;

//Get frames per second

function startAnimation() {
	
	//DrawEverything();
	/*IsPlaying = true;
	DrawTimely();
	return;
	*/
	
	//This button should work only if video is not playing
	if (IsPlaying == false)
	{

	startTime = new Date() - new Date(timeElapsed * 1000);
	IsPlaying = true;

	myTimerDrawing = setInterval(function(){DrawTimely()},5);
	myTimerRendering = setInterval(function(){RenderCanvas()},5);
	
	video_feed.play();
	
	//DrawTimely();

	}

}

function pauseAnimation() {
	
	//This button should work only if video is already playing
	if (IsPlaying == true)
	{
	IsPlaying = false;
	video_feed.pause();

	}
	
}


function RenderCanvas(){
	
	updateCanvas();
	
}


function DrawTimely()
{
	
	if (IsPlaying == false)
		return;
	
	
	//Check if it is time to display the next images
	timeElapsed =  new Date() - startTime;
	timeElapsed /= 1000; //get rid of the milliseconds
	
	//console.log(timeElapsed);
	//console.log('start: ' + timestamps[0][0]);
	//console.log('end: ' + timestamps[0][1]);
	
	var draw_points_till_index = 0; //last if drawing remaining points
	
	//Ignore empty strokes
	while (total_points_in_strokes[drawing_current_stroke] == 0)
	{
		drawing_current_stroke += 1;
		drawing_current_substroke = 0;
		drawing_current_substroke_point = 0;
	}
	
	while (strokes[drawing_current_stroke][drawing_current_substroke].length == 0)
	{
		drawing_current_substroke += 1;
	}
	
	var start_timestamp = timestamps[drawing_current_stroke][0];
	var end_timestamp = timestamps[drawing_current_stroke][1];
	
	//current object being drawn = drawing_current_stroke
	if (timeElapsed > start_timestamp && timeElapsed < end_timestamp)
	{
		//drawing the current object, great
		//calculate how many objects to draw
		
		draw_points_till_index = (timeElapsed - start_timestamp) / (end_timestamp - start_timestamp) * total_points_in_strokes[drawing_current_stroke];
		
	
	}//
	else if (timeElapsed > end_timestamp)
	{
		//We are passed this object
		//draw the remaining parts
		
		draw_points_till_index = total_points_in_strokes[drawing_current_stroke] - 1; //draw till last point
		
		
		
		
	}//if late already
	
		//Drawing enough points to come upto speed
		for (_drawing_current_pt = points_drawn_in_current_stroke; _drawing_current_pt < draw_points_till_index; _drawing_current_pt++)
		{
	
	
			//current_cursor_index is based on time: not a for loop
			//current_cursor_index =  Math.round(timeElapsed * 15); //actual formula (timeElapsed * 1000) * (15 / 1000); 
			
			//console.log(timeElapsed);
			
			current_stroke = strokes[drawing_current_stroke];
			current_start_pos = starting_pos[drawing_current_stroke];
			color = colors[drawing_current_stroke];
			timestamp = timestamps[drawing_current_stroke];
			total_points = total_points_in_strokes[drawing_current_stroke];
			_r = parseInt(color[0]);
			_g = parseInt(color[1]);
			_b = parseInt(color[2]);
			_color = 'rgb(' + _r + ',' + _g + ',' + _b + ')';
					
					
					local_x = strokes[drawing_current_stroke][drawing_current_substroke][drawing_current_substroke_point][0];
					local_y = strokes[drawing_current_stroke][drawing_current_substroke][drawing_current_substroke_point][1];
					
					
					if (drawing_current_substroke_point + 1 < strokes[drawing_current_stroke][drawing_current_substroke].length)
					{

					x1 = (parseInt(current_start_pos[0]) + parseInt(local_x)) * width_normalizer;
					y1 = (parseInt(current_start_pos[1]) + parseInt(local_y)) * height_normalizer;
					
					x1 = Math.round(x1);
					y1 = Math.round(y1);
					
					
					drawPixel(x1, y1, _r, _g, _b, 255);
					
					}//if drawing
					
			//Increment based on the state of the current variables.
			
			//Increment Point
			drawing_current_substroke_point++;
			points_drawn_in_current_stroke += 1; //increment
			
			if (drawing_current_substroke_point + 1 >= strokes[drawing_current_stroke][drawing_current_substroke].length)
			{
				drawing_current_substroke_point = 0;
				if (drawing_current_substroke == strokes[drawing_current_stroke].length - 1)
				{
					drawing_current_substroke = 0;
					drawing_current_stroke++;
					points_drawn_in_current_stroke = 0; //reset
				}
				else
				{
					drawing_current_substroke++;
				}
			}//if point is the last point in the current_substroke
			
			//Stop
			if (drawing_current_substroke > strokes.length - 1)
			{
				//Stop drawing when reached end of data
			}
	
	
		}//for "draw_points_till_index" Times: Draw these points
	
	
}//DrawTimely


//Prvious Lists:
//data_list = [[cur_pos_x, cur_pos_y], ...]
//timestamps = [[start_time, end_time], ...]
