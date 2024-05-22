from flask import Flask, render_template, request, jsonify
from frames import extract_frames
import shutil
import math
import os
import players, ball, shot, score
from ultralytics import YOLO

app = Flask(__name__)

comm_part = ''

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_commentary_part')
def get_commentary_part():
    global comm_part
    temp = comm_part
    if temp:
        comm_part = ''
    return jsonify(temp)
    
@app.route('/get_commentary', methods=['POST'])
def get_commentary():

    file = request.files['file']
    output_folder = 'frames_output'

    video_path = 'temp_video.mp4'
    file.save(video_path)

    extract_frames(video_path, output_folder)

    frames_directory = output_folder

    frame_files = [os.path.join(frames_directory, filename) for filename in os.listdir(frames_directory) if filename.endswith(".jpg")]

    def extract_frame_number(file_path):
        frame_number = file_path.split('_')[-1].split('.')[0]
        return int(frame_number) if frame_number else float('inf')  # Use infinity if no numeric part is found

    # Sort the list using the custom key function
    frame_files = sorted(frame_files, key=extract_frame_number)

    squad1 = ['Babar', 'Rizwan']
    squad2 = ['Zampa']

    striker, runner = '', ''

    current_run = 0
    current_out = 0
    current_overs = ''

    # print('Starting the commentary')
    current_run, current_out, current_overs, frame_files = score.get_score(frame_files, 1)

    i = 0

    while True:
        # for i in range(len(frame_files)):
        #     model = YOLO('models/scoreboard.pt')
        #     results = model.predict(frame_files[i])

        #     try:
        #         if float(results[0].boxes.conf[0]) > 0.57:
        #             frame_files = frame_files[i:]
        #             break
        #     except:
        #         pass

        player1, player2, bowler = players.get_players(frame_files[0], squad1, squad2)

        striker2, runner2 = '', ''

        if i == 0:
            striker = player1
            runner = player2
        else:
            if striker == player1:
                runner = player2
            elif striker == player2:
                runner = player1
            elif runner == player1:
                striker = player2
            elif runner == player2:
                striker = player1

        global comm_part

        converted_over = float(current_overs)
        if converted_over % 1 == 0.5:
            converted_over = '{:.1f}'.format(math.ceil(converted_over))
        else:
            converted_over = str(round(converted_over + 0.1, 1))

        comm_part = f'{converted_over} - {bowler} to {striker}, '

        length, line, last_ball_frame, frame_files = ball.get_line_and_length(frame_files, 3)
        comm_part = f'{length} length, {line} stump, '

        shot_region = shot.get_shot_region(last_ball_frame)
        comm_part = f'{striker} plays at {shot_region} region. '

        runs, out, overs, frame_files = score.get_score(frame_files, 1)
        # print('hello fayez')
        while runs == current_run and out == current_out and overs == current_overs:
            runs, out, overs, frame_files = score.get_score(frame_files[30:], 30)

        event = ''

        if runs == current_run and out == current_out:
            striker2 = striker
            runner2 = runner
            event = 'Dot Ball'
        elif runs == current_run and out != current_out:
            striker2 = ''
            runner2 = runner
            event = 'Wicket'
        elif runs != current_run and out == current_out and overs == current_overs:
            striker2 = striker
            runner2 = runner
            event = f'Wide or No Ball. Gave {str(runs - current_run)} runs in extra'
        elif runs != current_run and out == current_out:
            if runs - current_run == 6:
                striker2 = striker
                runner2 = runner
                event = 'Six'
            elif runs - current_run == 4:
                striker2 = striker
                runner2 = runner
                event = 'Four'
            else:
                if runs - current_run == 1 or runs - current_run == 3:
                    striker2 = runner
                    runner2 = striker
                else:
                    striker2 = striker
                    runner2 = runner
                event = f'{str(runs - current_run)} Runs'
        elif runs != current_run and out != current_out:
            if runs - current_run == 1:
                striker2 = ''
                runner2 = runner
            elif runs - current_run == 2:
                striker2 = runner
                runner2 = ''
            event = f'Tried for another one but lost wicket'

        comm = f'{bowler} to {striker}, {length} length, {line} stump, {striker} plays at {shot_region} region. {event}. Now {str(runs)} for {str(out)}'

        comm_part = f'{event}. Now {str(runs)} for {str(out)}'

        final_comm = comm
        comm_part = {'refined_commentary': final_comm}

        current_run = runs
        current_out = out
        current_overs = overs

        striker = striker2
        runner = runner2

        if current_overs == '0.4':
            return

    os.remove(video_path)
    shutil.rmtree(output_folder)

                       
if __name__ == '__main__':
    app.run()
