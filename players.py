import pytesseract
from PIL import Image, ImageEnhance, ImageFilter, ImageOps
import os
import matplotlib.pyplot as plt
from ultralytics import YOLO
import cv2
import re

def get_players(image_path, squad1, squad2):
    model = YOLO('models/scoreboard.pt')
    results = model.predict(image_path)

    image = cv2.imread(image_path)
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
    players = []

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

        for player in squad1:
            if player.upper() in extracted_text.upper():
                if player not in players:
                    players.append(player)
                # print(player)
        
        for player in squad2:
            if player.upper() in extracted_text.upper():
                if player not in players:
                    players.append(player)
                # print(player)

        # print(extracted_text)

        # print(matches)

        if len(players) == 3 or contrastValue > 5:
            break

        # if contrastValue > 5:
        #     break
            
        contrastValue += 0.25

    # return players
    dic = {'team1': [], 'team2': []}
    for x in players:
        if x in squad1:
            dic['team1'].append(x)
        else:
            dic['team2'].append(x)

    # print(dic)

    # if current_run == 0 and current_out == 0:
        # striker = players_list[0]
        # non_striker = players_list[1]
        # bowler = players_list[2]
    if len(dic['team1']) == 2:
        index1 = squad1.index(dic['team1'][0])
        index2 = squad1.index(dic['team1'][1])
        if index1 < index2:
            striker = dic['team1'][0]
            non_striker = dic['team1'][1]
        else:
            striker = dic['team1'][1]
            non_striker = dic['team1'][0]

        bowler = dic['team2'][0] 
    else:
        index1 = squad2.index(dic['team2'][0])
        index2 = squad2.index(dic['team2'][1])
        if index1 < index2:
            striker = dic['team2'][0]
            non_striker = dic['team2'][1]
        else:
            striker = dic['team2'][1]
            non_striker = dic['team2'][0]

        bowler = dic['team1'][0]
    # else:
    #     striker = ''
    #     non_striker = ''
    #     bowler = ''

    return striker, non_striker, bowler
# print(players)
    
