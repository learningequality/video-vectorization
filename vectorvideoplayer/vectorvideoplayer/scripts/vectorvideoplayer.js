/*!
 * Vector Video Player 0.0.1
 */

/********************INIT & EVENT LISTENERS********************/

$(document).ready(function () {
    initialize();
    load_json();
    $(".vector_play_pause_btn").bind("click", function () {
        clicked_play_pause_btn();
    });
    $(".vector_replay_btn").bind("click", function () {
        clicked_replay_btn();
    });
    $(".vector_seeker").bind("input", function () {
        adjusted_seeker();
    });
    $(".vector_settings_btn").bind("click", function () {
        clicked_settings_btn();
    });
    $(".vector_playback_rate_item").bind("click", function () {
        clicked_playback_rate_item(event);
    });
    $(".vector_zoom_level_item").bind("click", function () {
        clicked_zoom_level_item(event);
    });
    $(".vector_cc_menu_item").bind("click", function () {
        clicked_cc_menu_item(event);
    });
    $(".vector_voice_menu_item").bind("click", function () {
        clicked_voice_menu_item(event);
    });
    $(".vector_volume_btn").bind("click", function () {
        clicked_volume_btn();
    });
    $(".vector_full_screen_btn").bind("click", function () {
        clicked_full_screen_btn();
    });
});

/********************EVENT HANDLERS********************/

/**
 * Handles clicking the play/pause button .
 */
function clicked_play_pause_btn() {
    toggle_audio_pause();
    cancel_voice();
    reset_voice_time_index();
}


/**
 * Handles clicking the replay button.
 */
function clicked_replay_btn() {
    var new_time = get_audio_position_in_sec() - 10;
    if (new_time < 0) {
        set_audio_position(0);
    } else {
        set_audio_position(new_time * 1000);
    }
}


/**
 * Handles adjusting the seeker.
 */
function adjusted_seeker() {
    set_audio_position_percent(document.querySelector('.vector_seeker').value / document.querySelector('.vector_seeker').max);
    reset_voice();
}

/**
 *
 */
function clicked_settings_btn() {
    $(".vector_settings").toggle();
    $(".vector_settings_btn").toggleClass("vector_settings_btn_exit");
}

/**
 * Handles clicking on playback rate item.
 * @param e - The playback rate selected.
 */
function clicked_playback_rate_item(e) {
    play_back_rate = parseFloat(e.target.dataset.rate);
    set_audio_playback_rate(play_back_rate);
}


/**
 * Handles clicking on the zoom button.
 */
function clicked_zoom_level_item(e) {
    var zoom_level = parseFloat(e.target.dataset.zoom);
    zoom_level = zoom_level;
    paper_scope.view.zoom = zoom_level;
    reset_canvas_center();
    resize_canvas();
    if (zoom_level == 1.0) {
        zoom_enabled = false;
        $('.vector_zoom_level_btn').removeClass('vector_zoom_level_btn_on');
    } else {
        zoom_enabled = true;
        $('.vector_zoom_level_btn').addClass('vector_zoom_level_btn_on');
    }
}


/**
 * Handles clicking on a cc language item.
 * @param e - The cc language element selected.
 */
function clicked_cc_menu_item(e) {
    var that = this;
    cc_lang = e.target.dataset.cc;
    document.querySelector('.vector_captions').innerHTML = "";
    if (cc_lang == "off") {
        cc_on = false;
        $('.vector_cc_btn').removeClass('vector_cc_btn_on');
    } else {
        cc_on = true;
        $('.vector_cc_btn').addClass('vector_cc_btn_on');

        var cc_vtt_file = "data/vtt/" + cc_lang + ".vtt";
        $.get(cc_vtt_file, function (vtt_file) {
            that.parse_captions(vtt_file, "cc");
        });
    }
}


/**
 * Handles clicking on a voice language item.
 * @param e - The voice language element selected.
 */
function clicked_voice_menu_item(e) {

    var that = this;
    var new_voice_lang = e.target.dataset.cc;

    if (new_voice_lang != voice_lang) {
        console.log("in here");
        voice_lang = new_voice_lang;
        cancel_voice();
        voice_queue = [];

        if (voice_lang == "original") {
            voice_on = false;
            set_audio_volume(100);

            $('.vector_voice_btn').removeClass('vector_voice_btn_on');
        } else {
            voice_on = true;
            set_audio_volume(0);

            $('.vector_voice_btn').addClass('vector_voice_btn_on');

            var voice_vtt_file = "data/vtt/" + voice_lang + ".vtt";
            $.get(voice_vtt_file, function (vtt_file) {
                that.parse_captions(vtt_file, "voice");
            });
        }
    }
}


/**
 * Handles clicking on the volume button.
 */
function clicked_volume_btn() {
    if ($(document.querySelector('.vector_volume_label')).hasClass('is-checked')) {
        voice_volume = 1;

        if (voice_on) {
            reset_voice();
        } else {
            set_audio_volume(100);
        }

        $('.vector_volume_btn').removeClass('vector_volume_btn_mute');
    }
    else {
        voice_volume = 0;
        reset_voice();
        set_audio_volume(0);

        $('.vector_volume_btn').addClass('vector_volume_btn_mute');
    }
}


/**
 * Handles clicking on the full screen button.
 */
function clicked_full_screen_btn() {
    if (!document.fullscreenElement && !document.mozFullScreenElement && !document.webkitFullscreenElement && !document.msFullscreenElement) {

        full_screen_enabled = true;
        $('.vector_full_screen_btn').addClass('vector_full_screen_btn_on');

        var el = document.querySelector('.vector_wrapper');

        if (el.requestFullscreen) {
            el.requestFullscreen();
        } else if (el.msRequestFullscreen) {
            el.msRequestFullscreen();
        } else if (el.mozRequestFullScreen) {
            el.mozRequestFullScreen();
        } else if (el.webkitRequestFullscreen) {
            el.webkitRequestFullscreen(Element.ALLOW_KEYBOARD_INPUT);
        }
    } else {

        full_screen_enabled = false;
        $('.vector_full_screen_btn').removeClass('vector_full_screen_btn_on');

        if (document.exitFullscreen) {
            document.exitFullscreen();
        } else if (document.msExitFullscreen) {
            document.msExitFullscreen();
        } else if (document.mozCancelFullScreen) {
            document.mozCancelFullScreen();
        } else if (document.webkitExitFullscreen) {
            document.webkitExitFullscreen();
        }
    }
}


/********************INITIALIZATION********************/

/**
 * Initializes.
 * @param options - Options.
 */
function initialize(options) {
    // ContentBaseView.prototype.initialize.call(this, options);
    // _.bindAll(this, "init_audio_object", "check_if_playing", "resize_canvas");
    // $el.html( template( data_model.attributes));
    init_vars();
    init_sound_manager();
    paper_scope = new paper.PaperScope();
}


function init_vars() {

    is_playing = false;
    latest_time = 0;
    latest_obj = 0;
    latest_stroke = 0;
    latest_sub_stroke = 0;

    zoom_enabled = false;
    zoom_level = 1;

    full_screen_enabled = false;

    cc_on = false;
    cc_cues = [];
    cc_current_cue_index = 0;
    cc_current_cue_end_time = 0;

    voice_on = false;
    voice_cues = [];
    voice_current_cue_index = 0;
    voice_current_cue_end_time = 0;
    voice_volume = 1;
    voice_queue = [];
    voice_lang = null;

    play_back_rate = 1.0;
}


/********************UI********************/


/**
 * Formats milliseconds into a h:m:s format.
 * @param ms Milliseconds
 * @return {string} - Time in a h:m:s format.
 */
function format_time(ms) {
    var ns = Math.floor(ms / 1000);
    var hr = Math.floor(ns / 3600);
    var min = Math.floor(ns / 60) - Math.floor(hr * 60);
    var sec = Math.floor(ns - (hr * 3600) - (min * 60));
    return (hr ? hr + ':' : '') + (hr && min < 10 ? '0' + min : min) + ':' + (sec < 10 ? '0' + sec : sec);
}


/********************AUDIO********************/

/**
 * Initializes sound manager.
 */
function init_sound_manager() {
    window.soundManager.setup({
        // url: window.sessionModel.get("STATIC_URL") + "soundmanager/",
        preferFlash: false,
        debugMode: false,
        html5PollingInterval: 15,
        onready: init_audio_object
    });
}


/**
 * Initializes audio.
 */
function init_audio_object() {
    window.audio_object = audio_object = soundManager.createSound({
        url: './data/audio.mp3',
        onload: audio_loaded.bind(this),
        onplay: audio_played.bind(this),
        onpause: audio_paused.bind(this),
        onresume: audio_played.bind(this),
        whileplaying: audio_playing.bind(this),
        onfinish: audio_finished.bind(this)
    });
}


/**
 * When the audio loads.
 */
function audio_loaded() {
    $(".vector_total_time").text(" / " + format_time(get_audio_duration()));
}


/**
 * When the audio is played.
 */
function audio_played() {
    is_playing = true;
    //data_model.set("is_playing", true);
    $('.vector_play_pause_btn').addClass('vector_play_pause_btn_pause');
    $('.vector_play_pause_btn_overlay').toggleClass('vector_hidden');
}

/**
 * Hides the controls.
 */
function hide_controls() {

}


/**
 * When the audio is paused.
 */
function audio_paused() {
    is_playing = false;
    //data_model.set("is_playing", false);
    $('.vector_play_pause_btn').removeClass('vector_play_pause_btn_pause');
    $('.vector_play_pause_btn_overlay').toggleClass('vector_hidden');
}


/**
 * While the audio is playing.
 */
function audio_playing() {
    $(".vector_current_time").text(format_time(get_audio_position()));
    document.querySelector('.vector_seeker').MaterialSlider.change(get_audio_position_percent() * document.querySelector('.vector_seeker').max);
}


/**
 * When the audio finishes.
 */
function audio_finished() {
    set_audio_position(0);
    audio_paused();
    reset_canvas_center();
}


/**
 * Gets the total duration of the audio.
 * @returns {number} - The total duration of the audio.
 */
function get_audio_duration() {
    return parseInt(audio_object.duration);
}


/**
 * Gets the current position of the audio.
 * @returns {number} - Current position of the audio.
 */
function get_audio_position() {
    return parseInt(audio_object.position);
}


/**
 * Gets the current position of the audio in seconds.
 * @returns {number} - The position of the audio in seconds.
 */
function get_audio_position_in_sec() {
    return ( get_audio_position()) / 1000;
}


/**
 * Sets the position of the audio.
 * @param val - The new desired position of the audio.
 */
function set_audio_position(val) {
    audio_object.setPosition(val);
}


/**
 * Gets the position of the audio in terms of percentage played.
 * @returns {number} - The percentage of the audio played.
 */
function get_audio_position_percent() {
    return get_audio_position() / get_audio_duration();
}


/**
 * Sets the position of the audio in terms of percentage played.
 * @param percent - The new desired position on therms of percentage.
 */
function set_audio_position_percent(percent) {
    set_audio_position(percent * get_audio_duration());
}


/**
 * Plays or paused the audio.
 */
function toggle_audio_pause() {
    audio_object.togglePause();
}


/**
 * Sets the playback rate of the audio.
 * @param val - The new desired playback rate.
 */
function set_audio_playback_rate(val) {
    audio_object.setPlaybackRate(val);
    if (val == 1.0) {
        $('.vector_playback_rate_btn').removeClass('vector_playback_rate_btn_on');
    } else {
        $('.vector_playback_rate_btn').addClass('vector_playback_rate_btn_on');
    }
}


/**
 * Sets the volume of the audio.
 * @param val - The new desired volume.
 */
function set_audio_volume(val) {
    audio_object.setVolume(val);
}


/********************CANVAS********************/

function load_json() {
    $.get('../vectorization/data.json', function (data) {
        init_canvas(data);
    });
}

/**
 * Initializes the canvas.
 */
function init_canvas(data) {

    json_data = data;
    modify_json();
    console.log(json_data);

    paper_scope.setup($(".vector_canvas")[0]);
    paper_scope.view.onFrame = check_if_playing;
    paper_scope.view.onResize = resize_canvas;
    resize_canvas();
}


/**
 * Checks if the audio is playing.
 */
function check_if_playing() {
    if (is_playing === true) {
        render_canvas();
        if (cc_on) {
            update_cc();
        }
        if (voice_on) {
            update_voice();
        }
    }
}


/**
 * When the audio is rewinded.
 */
function audio_rewinded() {
    reset_canvas();
    reset_cc();
    reset_voice();
}


/**
 * Resize the canvas.
 */
function resize_canvas() {
    reset_canvas();
    var vector_canvas_wrapper = $(".vector_canvas_wrapper");
    vector_canvas_wrapper_width = vector_canvas_wrapper.width();
    vector_canvas_wrapper_height = vector_canvas_wrapper.height();
    paper_scope.view.viewSize = new paper.Size(vector_canvas_wrapper_width, vector_canvas_wrapper_height);
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
    add_bg();
}


/**
 * Resets the canvas center.
 */
function reset_canvas_center() {
    paper_scope.view.center = new paper_scope.Point(paper_scope.view.viewSize.width / 2, paper_scope.view.viewSize.height / 2);
}


/**
 * Adds the background.
 */
function add_bg() {
    var that = this;
    var bg_img = new paper_scope.Raster({
        source: './data/img/background.png'
    });

    bg_img.onLoad = function () {
        bg_img.size = that.paper_scope.view.viewSize;
        bg_img.position = that.paper_scope.view.center;
    };
}


/**
 * Adds fps, cursor update rate, exact x and y values of every sub stroke, stroke time start and end times, and sub stroke start times.
 */
function modify_json() {
    var data = json_data;

    //TODO: ORIGINAL DIMENSIONS SHOULD BE IN THE JSON. HERE I AM ASSUMING 1280 x 720
    orig_width = 1280;
    orig_height = 720;


    //CALCULATE FPS AND HOW OFTEN, IN TERMS OF TIME, THE CURSOR SHOULD BE UPDATES
    data.actual_fps = data.cursor.length / parseFloat(data.total_time);
    data.cursor_update_rate = parseFloat(data.total_time) / data.cursor.length;


    //LOOP THROUGH ALL OBJECTS
    for (var obj = 0; obj < data.operations.length; obj++) {
        var obj_offset_x = parseInt(data.operations[obj].offset_x);
        var obj_offset_y = parseInt(data.operations[obj].offset_y);
        var obj_start_time = parseFloat(data.operations[obj].start);
        var obj_end_time = parseFloat(data.operations[obj].end);
        //TODO: ADJUST THE OBJECT DURATION BY DIVIDING OR SUBTRACTING BY SOMETHING 0.5 IS JUST A GUESS
        var obj_dur = (obj_end_time - obj_start_time) * 0.5;
        var obj_dist = 0;
        var stroke_distances = [];

        //LOOP THROUGH ALL STROKES IN ONE OBJECT
        for (var stroke = 0; stroke < data.operations[obj].strokes.length; stroke++) {
            var stroke_dist = 0;

            //LOOP THROUGH ALL SUB STROKES IN ONE STROKE
            for (var sub_stroke = 0; sub_stroke < data.operations[obj].strokes[stroke].length - 1; sub_stroke++) {

                var x_cord = parseInt(data.operations[obj].strokes[stroke][sub_stroke][0]);
                var y_cord = parseInt(data.operations[obj].strokes[stroke][sub_stroke][1]);
                var x_cord_nxt = parseInt(data.operations[obj].strokes[stroke][(sub_stroke + 1)][0]);
                var y_cord_nxt = parseInt(data.operations[obj].strokes[stroke][(sub_stroke + 1)][1]);
                var sub_stroke_dist = Math.sqrt(Math.pow((x_cord_nxt - x_cord), 2) + Math.pow((y_cord_nxt - y_cord), 2));
                stroke_dist += sub_stroke_dist;

                //ADD EXACT X AND Y COORDINATES TO EVERY SUB STROKE
                data.operations[obj].strokes[stroke][sub_stroke].x = obj_offset_x + x_cord;
                data.operations[obj].strokes[stroke][sub_stroke].y = obj_offset_y + y_cord;

            }

            stroke_distances.push(stroke_dist);
            obj_dist += stroke_dist;
        }

        //GO THROUGH ARRAY
        for (var i = 0; i < stroke_distances.length; i++) {
            var stroke_dur = (parseFloat(stroke_distances[i]) / obj_dist) * obj_dur;

            if (i === 0) {
                data.operations[obj].strokes[i].stroke_start_time = obj_start_time;
                data.operations[obj].strokes[i].stroke_end_time = obj_start_time + stroke_dur;
            }

            else {
                data.operations[obj].strokes[i].stroke_start_time = parseFloat(data.operations[obj].strokes[i - 1].stroke_end_time);
                data.operations[obj].strokes[i].stroke_end_time = parseFloat(data.operations[obj].strokes[i - 1].stroke_end_time) + stroke_dur;
            }

            //LOOP THROUGH ALL SUB STROKES AND ADD SUB STROKE START TIME
            for (var j = 0; j < data.operations[obj].strokes[i].length; j++) {
                var stroke_start_time = parseFloat(data.operations[obj].strokes[i].stroke_start_time);
                var ratio = j / parseFloat(data.operations[obj].strokes[i].length);
                var sub_stroke_start_time = stroke_dur * ratio;
                data.operations[obj].strokes[i][j].sub_stroke_start_time = stroke_start_time + sub_stroke_start_time;
            }
        }
    }
}


/**
 * Draws the appropriate strokes on the canvas.
 */
function render_canvas() {
    var curr_time = get_audio_position_in_sec();


    //GET CURRENT WIDTH AND HEIGHT
    var width_adjust = vector_canvas_wrapper_width / orig_width;
    var height_adjust = vector_canvas_wrapper_height / orig_height;


    //IF REWINDED
    if (curr_time < latest_time) {
        audio_rewinded();
    }

    else {
        latest_time = curr_time;

        render_cursor(width_adjust, height_adjust);

        //UPDATE STROKES
        //LOOP THROUGH OBJECTS
        for (var obj = latest_obj; obj < json_data.operations.length; obj++) {

            if ((parseFloat(json_data.operations[obj].start)) <= latest_time) {
                latest_obj = obj;

                var red = parseInt(json_data.operations[obj].color[0]) / 255;
                var green = parseInt(json_data.operations[obj].color[1]) / 255;
                var blue = parseInt(json_data.operations[obj].color[2]) / 255;

                //LOOP THROUGH STROKES
                for (var stroke = latest_stroke; stroke < json_data.operations[obj].strokes.length; stroke++) {

                    if (((parseFloat(json_data.operations[obj].strokes[stroke].stroke_start_time)) <= latest_time)) {
                        latest_stroke = stroke;

                        //LOOP THROUGH SUB STROKES
                        for (var sub_stroke = latest_sub_stroke; sub_stroke < json_data.operations[obj].strokes[stroke].length - 1; sub_stroke++) {

                            if (((parseFloat(json_data.operations[obj].strokes[stroke][sub_stroke].sub_stroke_start_time)) <= latest_time)) {

                                var curr_sub_stroke = json_data.operations[obj].strokes[stroke][sub_stroke];
                                var nxt_sub_stroke = json_data.operations[obj].strokes[stroke][sub_stroke + 1];
                                var curr_sub_stroke_x = parseFloat(curr_sub_stroke.x) * width_adjust;
                                var curr_sub_stroke_y = parseFloat(curr_sub_stroke.y) * height_adjust;
                                var nxt_sub_stroke_x = parseFloat(nxt_sub_stroke.x) * width_adjust;
                                var nxt_sub_stroke_y = parseFloat(nxt_sub_stroke.y) * height_adjust;

                                //DRAW
                                var sub_stroke_path = new paper_scope.Path.Line((new paper_scope.Point(curr_sub_stroke_x, curr_sub_stroke_y)), (new paper_scope.Point(nxt_sub_stroke_x, nxt_sub_stroke_y)));
                                sub_stroke_path.strokeColor = new paper_scope.Color(red, green, blue);
                                sub_stroke_path.strokeCap = 'round';
                                sub_stroke_path.strokeJoin = 'round';
                                sub_stroke_path.strokeWidth = 2;

                                //FOR USEFUL DEBUGGING PURPOSES
                                //console.log(obj,stroke,sub_stroke);

                                //IF LAST SUBSTROKE AND LAST STROKE
                                if ((sub_stroke == json_data.operations[obj].strokes[stroke].length - 2) && (stroke == json_data.operations[obj].strokes.length - 1)) {
                                    latest_sub_stroke = 0;
                                    latest_stroke = 0;
                                    latest_obj++;
                                }
                                //IF JUST LAST SUBSTROKE
                                else if (sub_stroke == json_data.operations[obj].strokes[stroke].length - 2) {
                                    latest_sub_stroke = 0;
                                    latest_stroke++;
                                }
                                else {
                                    latest_sub_stroke = sub_stroke + 1;
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}


/**
 * Renders the cursor on the canvas.
 * @param width_adjust - The adjusted width of the canvas.
 * @param height_adjust - The adjusted height of the canvas.
 */
function render_cursor(width_adjust, height_adjust) {
    var cursor_index = parseInt(( latest_time / parseFloat(json_data.total_time)) * json_data.cursor.length);

    if (cursor_index < json_data.cursor.length) {
        var cursor_x = (parseInt(json_data.cursor[cursor_index][0])) * width_adjust;
        var cursor_y = (parseInt(json_data.cursor[cursor_index][1])) * height_adjust;

        if (cursor) {
            cursor.position = new paper_scope.Point(cursor_x, cursor_y);
            if (zoom_enabled) {
                paper_scope.view.center = new paper_scope.Point(adjust_center_x(cursor_x), adjust_center_y(cursor_y));
            }
        } else {
            cursor = new paper_scope.Path.Circle(
                {
                    center: new paper_scope.Point(cursor_x, cursor_y),
                    radius: 2,
                    fillColor: 'white'
                }
            );
        }
    }
}

/**
 * Finds appropriate values when it comes to adjusting the center x value to pass on to adjust_center_point.
 * @param cursor_x - The new cursor position's x value.
 */
function adjust_center_x(cursor_x) {
    var curr_center_val = paper_scope.view.center.x;
    var total_length = paper_scope.view.viewSize.width;
    var view_port_length = paper_scope.view.bounds.width;
    return adjust_center_point(cursor_x, curr_center_val, total_length, view_port_length);
}


/**
 * Finds appropriate values when it comes to adjusting the center y value to pass on to adjust_center_point.
 * @param cursor_y - The new cursor position's y value.
 */
function adjust_center_y(cursor_y) {
    var curr_center_val = paper_scope.view.center.y;
    var total_length = paper_scope.view.viewSize.height;
    var view_port_length = paper_scope.view.bounds.height;
    return adjust_center_point(cursor_y, curr_center_val, total_length, view_port_length);
}


/**
 * Attempts to find the new best center value for x or y in order to smooth panning.
 * @param next_center_val - The new center value that needs to be adjusted.
 * @param curr_center_val
 * @param total_length
 * @param view_port_length
 * @returns {number} - The new adjusted center value.
 */
function adjust_center_point(next_center_val, curr_center_val, total_length, view_port_length) {
    // CALCULATES WHAT THE NEW CENTER VALUE SHOULD BE.
    // THE CLOSER THE NEXT CENTER VAL IS TO THE CURRENT CENTER VAL,
    // THE CLOSER THE NEW CENTER SHOULD BE TO THE CURRENT CENTER.
    var half_view_port_length = view_port_length / 2;
    var diff = next_center_val - curr_center_val;
    var abs_diff = Math.abs(diff);
    var ratio = abs_diff / view_port_length;
    var eased_ratio = ease_num(ratio);
    var eased_diff = diff * eased_ratio;
    var new_center_val = curr_center_val + eased_diff;
    var bounded_new_center_val = Math.min(Math.max(new_center_val, 0 + half_view_port_length), total_length - half_view_port_length);
    return bounded_new_center_val;
}


/**
 * Eases a number using the easeInCubic function.
 * @param t - The number to be eased.
 * @returns {number} The new eased number.
 */
function ease_num(t) {
    var threshold = 0.2;//JUST AN ESTIMATE
    if (t < threshold) {
        return 0;
    } else {
        t -= threshold;
        return t * t * t;
    }
}


/********************CLOSED CAPTIONS********************/

/**
 * Parses the vtt file.
 * @param captions The vtt file that contains the captions.
 * @param cc_or_voice - Whether the captions are for cc or voice.
 */
function parse_captions(captions, cc_or_voice) {
    var cues = [];
    var parser = new WebVTT.Parser(window, WebVTT.StringDecoder());
    parser.oncue = function (cue) {
        cues.push(cue);
    };
    parser.parse(captions);
    if (cc_or_voice == "cc") {
        cc_cues = cues;
        cc_current_cue_end_time = 0;
    } else {
        voice_cues = cues;
        reset_voice_time_index();
    }
}


/**
 * Renders the cc.
 */
function update_cc() {
    var curr_time = get_audio_position_in_sec();
    if (curr_time > cc_current_cue_end_time) {
        for (var i = cc_current_cue_index; i < cc_cues.length; i++) {
            if (cc_cues[i].startTime < curr_time &&
                cc_cues[i].endTime > curr_time) {
                document.querySelector('.vector_captions').innerHTML = cc_cues[i].text;
                cc_current_cue_end_time = cc_cues[i].endTime;
                cc_current_cue_index = i;
                return;
            }
        }
    }
}


/**
 * Resets the cc.
 */
function reset_cc() {
    cc_current_cue_index = 0;
    cc_current_cue_end_time = 0;
}


/********************VOICE********************/

function reset_voice_time_index() {
    voice_current_cue_end_time = 0;
    voice_current_cue_index = 0;
}


/**
 * Plays the voice.
 */
function update_voice() {
    var curr_time = get_audio_position_in_sec();

    if (curr_time > voice_current_cue_end_time) {
        for (var i = voice_current_cue_index; i < voice_cues.length; i++) {
            if (( voice_cues[i].startTime < curr_time) &&
                ( voice_cues[i].endTime > curr_time)) {
                var person;
                switch (voice_lang) {
                    case "en":
                        person = "US English Female";
                        break;
                    case "es":
                        person = "Spanish Female";
                        break;
                    default:
                        person = "US English Female";
                        break;
                }
                voice_queue.push({
                    text: voice_cues[i].text,
                    person: person
                });
                voice_current_cue_end_time = voice_cues[i].endTime;
                voice_current_cue_index = i;
                return;
            }
        }
    }

    //IF QUEUE IS NOT EMPTY AND NOTHING IS PLAY, THEN DEQUEUE AND PLAY
    if (( voice_queue.length > 0) && !is_voice_playing()) {
        var new_cue = voice_queue.shift();
        speak(new_cue['text'], new_cue['person'], {
            rate: (1.3 * play_back_rate),
            volume: voice_volume
        }); //SPEED IS JUST AN ESTIMATE
    }
}


/**
 * Resets the voice.
 */
function reset_voice() {
    cancel_voice();
    voice_queue = [];
    reset_voice_time_index();
}


/**
 * Stops the voice.
 */
function cancel_voice() {
    responsiveVoice.cancel();
}


/**
 * Checks whether the voice is playing.
 * @returns {boolean} Whether the voice is playing or not.
 */
function is_voice_playing() {
    return responsiveVoice.isPlaying();
}


/**
 *
 * @param text - The text to be spoken.
 * @param person - The person to be used to speak
 * @param settings - Object of other settings such as rate and volume.
 */
function speak(text, person, settings) {
    responsiveVoice.speak(text, person, settings);
}
