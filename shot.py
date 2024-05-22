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

def get_shot_region(last_ball_frame):
    try:
        # Load the cricket pitch image with the batsman
        image_path = last_ball_frame  # Replace with the actual file path

        image = Image.open(image_path)
        image_width, image_height = image.size
        draw = ImageDraw.Draw(image)
        # print(image.size)
        # image.show()

        model = YOLO('stump.pt')
        results = model.predict(image_path)
        ls = results[0].boxes.cls.tolist()
        # try:
        #     idxls = [i for i, x in enumerate(ls) if x == 1]
        #     tmp = results[0].boxes.xywhn[idxls[0]][3]
        #     idx = idxls[0]
        #     for i in idxls:
        #         if results[0].boxes.xywhn[i][3] > tmp:
        #             tmp = results[0].boxes.xywhn[i][3]
        #             idx = i
        #     y_coordinate_stump = float(results[0].boxes.xywhn[idx][1] + results[0].boxes.xywhn[idx][3]/2)
        # except:
        #     idx = ls.index(0)
        #     y_coordinate_stump = float(results[0].boxes.xywhn[idx][1] + results[0].boxes.xywhn[idx][3]/2) - 0.05
        idx = ls.index(0)
        y_coordinate_stump = float(results[0].boxes.xywhn[idx][1])
        x_coordinate_stump = float(results[0].boxes.xywhn[idx][0])

        # Batsman stump coordinates in the image
        batsman_stump_x = x_coordinate_stump * image_width 
        batsman_stump_y = y_coordinate_stump * image_height

        # print(batsman_stump_x, batsman_stump_y)

        # batsman_stump_x = 642.1434020996094
        # batsman_stump_y = 404.31374073028564

        # Enlarged point size
        # point_radius = 5

        # Draw an enlarged point at the specified coordinates
        # draw.ellipse((batsman_stump_x - point_radius, batsman_stump_y - point_radius, batsman_stump_x + point_radius, batsman_stump_y + point_radius), fill="red")

        # # Field coordinates (relative to the batsman stump)
        # field_coordinates = {
        #     "Fine Leg": (0, 300),
        #     "Mid On": (0, -300),
        #     "Mid Off": (200, -300),
        #     "Cover": (200, -100),
        #     "Point": (300, 100),
        #     "Gully": (300, 200),
        # }

        # # Convert field coordinates to image coordinates
        # for region, (x, y) in field_coordinates.items():
        #     x_image = batsman_stump_x + x
        #     y_image = batsman_stump_y + y

        #     # Define the vertices for the triangular regions
        #     vertices = [
        #         (x_image, y_image),
        #         (x_image - 50, y_image + 50),
        #         (x_image + 50, y_image + 50)
        #     ]

        #     # Draw triangular regions
        #     draw.polygon(vertices, outline="black")

        #     # Label the regions
        #     font = ImageFont.load_default()
        #     draw.text((x_image - 40, y_image - 60), region, fill="black", font=font)

        # draw.line([(batsman_stump_x, batsman_stump_y), (image_width, batsman_stump_y)], fill="red", width=2)
        # draw.line([(batsman_stump_x, batsman_stump_y), (batsman_stump_x, image_height)], fill="red", width=2)
        # draw.line([(batsman_stump_x, batsman_stump_y), (-image_width, batsman_stump_y)], fill="red", width=2)
        # draw.line([(batsman_stump_x, batsman_stump_y), (batsman_stump_x, -image_height)], fill="red", width=2)

        # Define the length of the diagonal lines
        diagonal_length = max(image_width, image_height)

        # Calculate the endpoints for 45-degree diagonals
        end_x1 = batsman_stump_x + diagonal_length
        end_y1 = batsman_stump_y - diagonal_length

        end_x2 = batsman_stump_x - diagonal_length
        end_y2 = batsman_stump_y - diagonal_length

        end_x3 = batsman_stump_x - diagonal_length
        end_y3 = batsman_stump_y + diagonal_length

        end_x4 = batsman_stump_x + diagonal_length
        end_y4 = batsman_stump_y + diagonal_length

        # Draw the 45-degree diagonals in all quadrants
        # draw.line([(batsman_stump_x, batsman_stump_y), (end_x1, end_y1)], fill="red", width=2)
        # draw.line([(batsman_stump_x, batsman_stump_y), (end_x2, end_y2)], fill="red", width=2)
        # draw.line([(batsman_stump_x, batsman_stump_y), (end_x3, end_y3)], fill="red", width=2)
        # draw.line([(batsman_stump_x, batsman_stump_y), (end_x4, end_y4)], fill="red", width=2)

        # Save the image with the fielding regions overlaid
        # image.save("cricket_fielding_regions.png")
        # image.show()

        # field_coordinates = {
        #     "Fine Leg": [(batsman_stump_x, batsman_stump_y), (image_width, batsman_stump_y), (end_x4, end_y4)],
        #     "Mid On": [(batsman_stump_x, batsman_stump_y), (end_x4, end_y4), (batsman_stump_x, image_height)],
        #     "Mid Off": [(batsman_stump_x, batsman_stump_y), (batsman_stump_x, image_height), (end_x3, end_y3)],
        #     "Cover": [(batsman_stump_x, batsman_stump_y), (end_x3, end_x3), (-image_width, batsman_stump_y)],
        #     "Point": [(batsman_stump_x, batsman_stump_y), (-image_width, batsman_stump_y), (end_x2, end_y2)],
        #     "Gully": [(batsman_stump_x, batsman_stump_y), (end_x2, end_y2), (batsman_stump_x, -image_height)],
        #     "dadad": [(batsman_stump_x, batsman_stump_y), (batsman_stump_x, -image_height), (end_x1, end_y1)],
        #     "dadad": [(batsman_stump_x, batsman_stump_y), (end_x1, end_y1), (image_width, batsman_stump_y)],
        # }

        # Define your field_coordinates dictionary
        field_coordinates = {
            "Fine Leg": [(batsman_stump_x, batsman_stump_y), (image_width, batsman_stump_y), (end_x4, end_y4)],
            "Mid On": [(batsman_stump_x, batsman_stump_y), (end_x4, end_y4), (batsman_stump_x, image_height)],
            "Mid Off": [(batsman_stump_x, batsman_stump_y), (batsman_stump_x, image_height), (end_x3, end_y3)],
            "Cover": [(batsman_stump_x, batsman_stump_y), (end_x3, end_y3), (-image_width, batsman_stump_y)],
            "Point": [(batsman_stump_x, batsman_stump_y), (-image_width, batsman_stump_y), (end_x2, end_y2)],
            "Gully": [(batsman_stump_x, batsman_stump_y), (end_x2, end_y2), (batsman_stump_x, -image_height)],
            "Scoop": [(batsman_stump_x, batsman_stump_y), (batsman_stump_x, -image_height), (end_x1, end_y1)],
            "Hook": [(batsman_stump_x, batsman_stump_y), (end_x1, end_y1), (image_width, batsman_stump_y)],
        }

        # Loop through the field_coordinates dictionary
        for key, triangle_coords in field_coordinates.items():
            triangle_coords = [(int(x), int(y)) for x, y in triangle_coords]
            # print(triangle_coords)
            # Draw the triangle in blue outline
            draw.polygon(triangle_coords, outline="blue", fill=None)

            # Find the center of the triangle
            # x_coords, y_coords = zip(*triangle_coords)
            # center_x = int(sum(x_coords) / len(x_coords))
            # center_y = int(sum(y_coords) / len(y_coords))
            # # print(center_x, center_y)
            # # Draw the label at the center
            # draw.text((center_x, center_y), "key", fill='black')

            # # Enlarged point size
            # point_radius = 5

            # # Draw an enlarged point at the specified coordinates
            # draw.ellipse((center_x - point_radius, center_y - point_radius, center_x + point_radius, center_y + point_radius), fill="red")

        # Save or display the modified image
        # image.show()  # Display the image
        # image.save('output_image.jpg')  # Save the image if needed

        model = YOLO('batsman-bowler.pt')
        results = model.predict(image_path)
        # print(results[0].names)
        ls = results[0].boxes.cls.tolist()
        # print(ls)
        idx = ls.index(0)
        x_coordinate_ball = float(results[0].boxes.xywhn[idx][0]) * image_width
        y_coordinate_ball = float(results[0].boxes.xywhn[idx][1]) * image_height

        ball_point = Point(x_coordinate_ball, y_coordinate_ball)

        # Loop through the field_coordinates dictionary and check if the ball point is inside any triangle
        for key, triangle_coords in field_coordinates.items():
            triangle_coords = [(int(x), int(y)) for x, y in triangle_coords]

            # Create a polygon from the triangle's coordinates
            triangle_polygon = Polygon(triangle_coords)

            # Check if the ball point is inside the polygon
            if ball_point.within(triangle_polygon):
                field_region = f"{key}"
                break
                # You can break the loop or perform any other action here

        return field_region
    except:
        return 'missed the bat'