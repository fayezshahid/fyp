import os
import players, ball, shot, score
from ultralytics import YOLO
import re

parent_dir = r'C:\Users\USER\OneDrive - FAST National University\Desktop\object detection'
frames_directory = f'{parent_dir}/frames_output'  # Replace with your frames directory
frame_files = [os.path.join(frames_directory, filename) for filename in os.listdir(frames_directory) if filename.endswith(".jpg")]

def extract_frame_number(file_path):
    frame_number = file_path.split('_')[-1].split('.')[0]
    return int(frame_number) if frame_number else float('inf')  # Use infinity if no numeric part is found

# Sort the list using the custom key function
frame_files = sorted(frame_files, key=extract_frame_number)

# frame_files = frame_files[11:]

# squad1 = ['Fakhar', 'McCullum', 'Devcich']
# squad2 = ['Amir']

squad1 = ['Babar', 'Rizwan']
squad2 = ['Zampa']

striker, runner = '', ''

current_run = 0
current_out = 0
current_overs = ''

while True:
    for i in range(len(frame_files)):
        model = YOLO('scoreboard.pt')
        results = model.predict(frame_files[i])
        # print(results)
        # ls = results[0].boxes.cls.tolist()
        # print(float(results[0].boxes.conf[0]))

        try:
            # print(float(results[0].boxes.conf[0]))
            if float(results[0].boxes.conf[0]) > 0.57:
                frame_files = frame_files[i:]
                break
        except:
            pass

        # # model = YOLO('scoreboard.pt')
        # # results = model.predict('test2.jpg')
        # # # ls = results[0].boxes.cls.tolist()
        # # print(float(results[0].boxes.conf[0]))
        
        # quit()

    # print(frame_files[0])
    # quit()

    # manual_over_count = 0.0

    player1, player2, bowler = players.get_players(frame_files[0], squad1, squad2, current_run, current_out)

    striker2, runner2 = '', ''

    if current_run == 0 and current_out == 0 and current_overs == '':
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

    length, line, last_ball_frame, frame_files = ball.get_line_and_length(frame_files)

    # print(frame_files[0])

    shot_region = shot.get_shot_region(last_ball_frame)

    runs, out, overs, frame_files = score.get_score(frame_files, last_ball_frame, 0)
    
    print(runs, current_run, out, current_out, overs, current_overs)
    while runs == current_run and out == current_out and overs == current_overs:
        print('hello')
        runs, out, overs, frame_files = score.get_score(frame_files, last_ball_frame, 0)

    # if manual_over_count % 1 == 0.5:
    #     manual_over_count = round(manual_over_count)
    # else:
    #     manual_over_count += 0.1

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
    print(comm)

    #write comm in a file named comm.txt
    f = open("comm.txt", "a")
    f.write(comm)
    f.write("\n")
    f.close()

    current_run = runs
    current_out = out
    current_overs = overs

    striker = striker2
    runner = runner2

    if current_overs == '0.4':
        break
