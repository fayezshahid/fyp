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
import re
from dotenv import load_dotenv
import threading

load_dotenv('.evn')

def get_score(frame_files, jump_count):
    tesseract_path = os.getenv("TESSERACT_PATH")

    i = 0
    while i < len(frame_files):
        model = YOLO('models/scoreboard.pt')
        results = model.predict(frame_files[i])
        try:
            if float(results[0].boxes.conf[0]) > 0.57:
                frame_files = frame_files[i:]
                break
        except:
            pass

        i += jump_count

    # def process_frames(thread_id, frame_files=frame_files, jump_count=jump_count):
    #     i = thread_id
    #     while i < len(frame_files):
    #         model = YOLO('models/scoreboard.pt')
    #         results = model.predict(frame_files[i])
    #         try:
    #             if float(results[0].boxes.conf[0]) > 0.57:
    #                 with lock:
    #                     frame_files = frame_files[i:]
    #                     terminate_flag.set()
    #                 break
    #         except:
    #             pass
    #         i += jump_count

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

    # model = YOLO('models/scoreboard.pt')
    # results = model.predict(frame_files[0])

    image = cv2.imread(frame_files[0])
    height, width, _ = image.shape

    # Coordinates of the center of the bounding box
    center_x_normalized = results[0].boxes.xywhn[0][0]  # Replace with the actual x-coordinate
    center_y_normalized = results[0].boxes.xywhn[0][1]  # Replace with the actual y-coordinate

    # Height and width of the bounding box
    height_normalized = results[0].boxes.xywhn[0][3]  # Replace with the actual height
    width_normalized = results[0].boxes.xywhn[0][2]  # Replace with the actual width

    # Calculate the top-left and bottom-right coordinates of the bounding box
    top_left_x = int((center_x_normalized - width_normalized / 2) * width)
    top_left_y = int((center_y_normalized - height_normalized / 2) * height)
    bottom_right_x = int((center_x_normalized + width_normalized / 2) * width)
    bottom_right_y = int((center_y_normalized + height_normalized / 2) * height)

    # Crop the region of interest (ROI) from the image
    roi = image[top_left_y:bottom_right_y, top_left_x:bottom_right_x]

    # Invert the image to enhance white text on dark background
    # img = ImageOps.invert(img)

    contrastValue = -5

    while True:
        # Convert the ROI to PIL Image
        img = Image.fromarray(roi)

        # Upscale the image by a factor of 2
        img = img.resize((2 * img.width, 2 * img.height), Image.ANTIALIAS)

        # Enhance visibility
        img = ImageEnhance.Contrast(img).enhance(contrastValue)  # Increase contrast
        img = img.filter(ImageFilter.MedianFilter())  # Median blur

        # Display the enhanced image
        # img.show()

        # Use Tesseract for text extraction on the enhanced image
        pytesseract.pytesseract.tesseract_cmd = tesseract_path
        custom_config = r'--oem 3 --psm 6'
        extracted_text = pytesseract.image_to_string(img, lang='eng', config=custom_config)

        # print(extracted_text)

        # Extract numbers in the pattern "number-number"
        number_pattern = re.compile(r'\b\d+-\d+\b')
        matches = number_pattern.findall(extracted_text)

        # print(matches)

        if matches:
            matches2 = matches

        if len(matches) == 2 or contrastValue > 5:
            break
            
        contrastValue += 0.25

    # print(matches)
    matches = matches2
    runs = int(matches[0].split('-')[0])
    out = int(matches[0].split('-')[1])
    
    contrastValue = -5

    while True:
        # Convert the ROI to PIL Image
        img = Image.fromarray(roi)

        # Upscale the image by a factor of 2
        img = img.resize((2 * img.width, 2 * img.height), Image.ANTIALIAS)

        # Enhance visibility
        img = ImageEnhance.Contrast(img).enhance(contrastValue)  # Increase contrast
        img = img.filter(ImageFilter.MedianFilter())  # Median blur

        # Display the enhanced image
        # img.show()

        # Use Tesseract for text extraction on the enhanced image
        pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        custom_config = r'--oem 3 --psm 6'
        extracted_text = pytesseract.image_to_string(img, lang='eng', config=custom_config)

        # print(extracted_text)

        # Extract numbers in the pattern " number.number"
        over_pattern = re.compile(r'\b \d+\.\d+\b')
        matches = over_pattern.findall(extracted_text)

        # print(matches)

        if matches:
            matches2 = matches

        if len(matches) >= 2 or contrastValue > 5:
            break

        # if contrastValue > 5:
        #     break
            
        contrastValue += 0.25

    try:
        matches = matches2
        i = max(range(len(matches)), key=lambda x: float(matches[x].strip()))
        overs = matches[i].strip()
    except:
        overs = ''

    return runs, out, overs, frame_files
