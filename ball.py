from ultralytics import YOLO
import numpy as np
import cv2
import matplotlib.pyplot as plt
import os
import math
from PIL import Image, ImageDraw, ImageFont
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon
import pytesseract
from PIL import Image, ImageEnhance, ImageFilter
import threading


def get_line_and_length(frame_files, jump_count):
    i = 0
    while i < len(frame_files):
        model = YOLO('models/batsman-bowler.pt')
        results = model.predict(frame_files[i])
        ls = results[0].boxes.cls.tolist()
        try:
            if float(results[0].boxes.conf[ls.index(1)]) > 0.6:
                frame_files = frame_files[i:]
                break
        except:
            pass

        i += jump_count

    # def process_frames(thread_id, frame_files=frame_files, jump_count=jump_count):
    #     i = thread_id
    #     while i < len(frame_files):
    #         model = YOLO('models/batsman-bowler.pt')
    #         results = model.predict(frame_files[i])
    #         ls = results[0].boxes.cls.tolist()
    #         try:
    #             if float(results[0].boxes.conf[ls.index(1)]) > 0.6:
    #                 print('fayez', frame_files[i])
    #                 with lock:
    #                     frame_files = frame_files[i:]
    #                     terminate_flag.set()
    #                 break
    #         except:
    #             pass
    #         i += num_threads + jump_count

    # num_threads = 4

    # lock = threading.Lock()
    # terminate_flag = threading.Event()

    # threads = []
    # for i in range(num_threads):
    #     thread = threading.Thread(target=process_frames, args=(i,))
    #     thread.start()
    #     threads.append(thread)

    # for thread in threads:
    #     thread.join()    

    # model = YOLO('models/batsman-bowler.pt')
    # results = model.predict(frame_files[0])
    # ls = results[0].boxes.cls.tolist()
    
    min_y_coordinate_ball = -1
    min_x_coordinate_ball = -1
    last_ball_frame = None
    batsman_height = float(results[0].boxes.xywhn[ls.index(1)][3])
    min_frame_ball = None

    i = 0
    while i < len(frame_files):
        results = model.predict(frame_files[i])
        ls = results[0].boxes.cls.tolist()
        # print('fayez')
        try:    
            idx = ls.index(0)
            y_coordinate_ball = float(results[0].boxes.xywhn[idx][1])
            x_coordinate_ball = float(results[0].boxes.xywhn[idx][0])

            if batsman_height < float(results[0].boxes.xywhn[ls.index(1)][3]):
                batsman_height = float(results[0].boxes.xywhn[ls.index(1)][3])
            elif batsman_height - float(results[0].boxes.xywhn[ls.index(1)][3]) > 0.1:
                idx = frame_files.index(frame_files[i])
                frame_files = frame_files[idx:]
                break

            last_ball_frame = frame_files[i]

            if y_coordinate_ball > min_y_coordinate_ball:
                min_y_coordinate_ball = y_coordinate_ball
                min_x_coordinate_ball = x_coordinate_ball

                min_frame_ball = frame_files[i]
        except:
            pass

        i += jump_count

    model = YOLO('models/stump.pt')
    results = model.predict(min_frame_ball)
    ls = results[0].boxes.cls.tolist()
    try:
        idxls = [i for i, x in enumerate(ls) if x == 1]
        tmp = results[0].boxes.xywhn[idxls[0]][3]
        idx = idxls[0]
        for i in idxls:
            if results[0].boxes.xywhn[i][3] > tmp:
                tmp = results[0].boxes.xywhn[i][3]
                idx = i
        y_coordinate_stump = float(results[0].boxes.xywhn[idx][1] + results[0].boxes.xywhn[idx][3]/2)
    except:
        idx = ls.index(0)
        y_coordinate_stump = float(results[0].boxes.xywhn[idx][1] + results[0].boxes.xywhn[idx][3]/2) - 0.05
    x_coordinate_stump = float(results[0].boxes.xywhn[idx][0])

    img = Image.open(min_frame_ball)
    image_width, image_height = img.size

    # showImageForLength()
    # showImageForLine()

    # x_coordinate_stump_for_length = x_coordinate_ball
    distance = math.sqrt((y_coordinate_stump - min_y_coordinate_ball) ** 2)

    # Convert the distance to meters
    ball_length = (distance * image_height * 0.06) # Assuming the coordinates are in centimeters

    # print("Vertical distance of ball from stumps (Length):", ball_length, "meters")

    if ball_length <= 2:
        ball_length_in_region = 'Yorker'
        # print('Yorker')
    elif ball_length > 2 and ball_length <= 4:
        ball_length_in_region = 'Full'
        # print('Full')
    elif ball_length > 4 and ball_length <= 6:
        ball_length_in_region = 'Good'
        # print('Good')
    elif ball_length > 6:
        ball_length_in_region = 'Short'
        # print('Short')

    # x_coordinate_stump_for_length = x_coordinate_ball
    distance = math.sqrt((x_coordinate_stump - min_x_coordinate_ball) ** 2)

    # Convert the distance to meters
    ball_line = (distance * image_width * 0.06) # Assuming the coordinates are in centimeters

    # print("Horizontal distance of ball from stumps (Line):", ball_line, "meters")

    if x_coordinate_stump < min_x_coordinate_ball:
        ball_line_in_region = 'Off'
        # print('Off')
    elif x_coordinate_stump > min_x_coordinate_ball:
        ball_line_in_region = 'Leg'
        # print('Leg')

    return ball_length_in_region, ball_line_in_region, last_ball_frame, frame_files