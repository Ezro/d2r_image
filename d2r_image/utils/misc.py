import numpy as np
from copy import deepcopy
import cv2


def cut_roi(img, roi):
    x, y, w, h = roi
    return img[y:y+h, x:x+w]


def erode_to_black(img: np.ndarray, threshold: int = 14):
    # Cleanup image with erosion image as marker with morphological reconstruction
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    thresh = cv2.threshold(gray, threshold, 255, cv2.THRESH_BINARY)[1]
    kernel = np.ones((3, 3), np.uint8)
    marker = thresh.copy()
    marker[1:-1, 1:-1] = 0
    while True:
        tmp = marker.copy()
        marker = cv2.dilate(marker, kernel)
        marker = cv2.min(thresh, marker)
        difference = cv2.subtract(marker, tmp)
        if cv2.countNonZero(difference) <= 0:
            break
    mask_r = cv2.bitwise_not(marker)
    mask_color_r = cv2.cvtColor(mask_r, cv2.COLOR_GRAY2BGR)
    img = cv2.bitwise_and(img, mask_color_r)
    return img


def roi_center(roi: list[float] = None):
    x, y, w, h = roi
    return round(x + w/2), round(y + h/2)


def color_filter(img, color_range):
    color_ranges = []
    # ex: [array([ -9, 201,  25]), array([ 9, 237,  61])]
    if color_range[0][0] < 0:
        lower_range = deepcopy(color_range)
        lower_range[0][0] = 0
        color_ranges.append(lower_range)
        upper_range = deepcopy(color_range)
        upper_range[0][0] = 180 + color_range[0][0]
        upper_range[1][0] = 180
        color_ranges.append(upper_range)
    # ex: [array([ 170, 201,  25]), array([ 188, 237,  61])]
    elif color_range[1][0] > 180:
        upper_range = deepcopy(color_range)
        upper_range[1][0] = 180
        color_ranges.append(upper_range)
        lower_range = deepcopy(color_range)
        lower_range[0][0] = 0
        lower_range[1][0] = color_range[1][0] - 180
        color_ranges.append(lower_range)
    else:
        color_ranges.append(color_range)
    color_masks = []
    for color_range in color_ranges:
        hsv_img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv_img, color_range[0], color_range[1])
        color_masks.append(mask)
    color_mask = np.bitwise_or.reduce(color_masks) if len(
        color_masks) > 0 else color_masks[0]
    filtered_img = cv2.bitwise_and(img, img, mask=color_mask)
    return color_mask, filtered_img


def alpha_to_mask(img: np.ndarray):
    # create a mask from template where alpha == 0
    if img.shape[2] == 4:
        if np.min(img[:, :, 3]) == 0:
            _, mask = cv2.threshold(img[:, :, 3], 1, 255, cv2.THRESH_BINARY)
            return mask
    return None
