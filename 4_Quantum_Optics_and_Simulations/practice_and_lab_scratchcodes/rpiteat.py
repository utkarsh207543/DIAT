import cv2
from flirpy.camera.lepton import Lepton

import numpy as np
from PyQt5 import *
import datetime
from PIL import Image
import flirimageextractor
import os


def nothing(x):
    pass


ptemp = ""
xpoint = 0
ypoint = 0


# temp=""
def printpointertemp(event, xp, yp, flags, params):
    # print(x,' , ',y)
    # print('Pointer Temp.- ',round(img_r_resize[yp,xp],2))
    global ptemp
    global xpoint
    temp = round(img_r_resize[yp, xp], 2)
    xpoint = xp
    ypoint = yp

    ptemp = 'Pointer Temp.: ' + str(round(img_r_resize[yp, xp], 2))


#     print(type(ptemp),'  ',ptemp)
#     return yp,xp,ptemp


winname = "Thermal Imageing"
cv2.namedWindow("Thermal Imageing")
cv2.createTrackbar("T", "Thermal Imageing", 0, 255, nothing)
cv2.createTrackbar("I", "Thermal Imageing", 0, 2, nothing)


def merge_images(ir_image, rgb_image):
    # Normalize IR image to the same scale as RGB image
    ir_image_normalized = cv2.normalize(ir_image, None, 0, 255, cv2.NORM_MINMAX)

    # Convert the normalized IR image to a 3-channel image (grayscale to BGR)
    ir_image_bgr = cv2.cvtColor(ir_image_normalized, cv2.COLOR_GRAY2BGR)

    # Merge IR and RGB images
    merged_image = cv2.addWeighted(rgb_image, 0.7, ir_image_bgr, 0.3, 0)

    return merged_image


with Lepton() as camera:
    while True:
        img = camera.grab().astype(np.float32)
        x = np.random.randint(0, 5, (500, 500))
        img_r = img

        img_r = (img_r / 100) - 273
        img_r_resize = cv2.resize(img_r, (640, 480))
        tmax = round(img_r_resize.max(), 2)
        tmin = round(img_r_resize.min(), 2)

        th = cv2.getTrackbarPos("T", "Thermal Imageing")
        Image = cv2.getTrackbarPos("I", "Thermal Imageing")
        img = 255 * (img - img.min()) / (img.max() - img.min())

        img_col = cv2.applyColorMap(img.astype(np.uint8), cv2.COLORMAP_HOT)
        img_resize = cv2.resize(img_col, (640, 480))

        imggray = cv2.cvtColor(img_resize, cv2.COLOR_BGR2GRAY)
        thresh, image_black = cv2.threshold(imggray, th, 255, cv2.THRESH_BINARY)
        tttt = cv2.setMouseCallback("Thermal Imageing", printpointertemp)

        # Load your RGB image (replace 'rgb_image.jpg' with the actual file path)
        rgb_image = cv2.imread('rgb_image.jpg')
        if rgb_image is None:
            print("Error: Could not load RGB image.")
            break  # Terminate the loop or handle the error as needed

        # Merge IR and RGB images
        merged_image = merge_images(img_r_resize, rgb_image)

        if Image == 0:
            thermalimg = img_resize
        if Image == 1:
            thermalimg = imggray
        if Image == 2:
            thermalimg = cv2.applyColorMap(img_resize, cv2.COLORMAP_JET)

        contours = cv2.findContours(image_black, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        contours = contours[0] if len(contours) == 2 else contours[1]
        for cntr in contours:
            x, y, w, h = cv2.boundingRect(cntr)
            cv2.rectangle(thermalimg, (x, y), (x + w, y + h), (0, 0, 255), 2)

        # Print temperature information on the image
        text1 = 'Max Temp.: ' + str(tmax)
        text2 = 'Min Temp.: ' + str(tmin)
        text3 = ptemp

        # ... (rest of the code for adding text to the image)

        cv2.imshow('Thermal Imageing', thermalimg)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

cv2.destroyAllWindows()

