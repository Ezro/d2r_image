import cv2
import numpy as np
from d2r_image.data_models import ItemQuality, ItemText
from d2r_image.utils.misc import color_filter, erode_to_black
from d2r_image.utils.template_finder import TemplateFinder
from d2r_image.ocr import image_to_text
from d2r_image.processing_data import BOX_EXPECTED_WIDTH_RANGE, BOX_EXPECTED_HEIGHT_RANGE, COLORS, EXPECTED_HEIGHT_RANGE, EXPECTED_WIDTH_RANGE, GAUS_FILTER, ITEM_COLORS, QUALITY_COLOR_MAP, UI_ROI
import time
import pkgutil
import io
from PIL import Image
import numpy as np


_hud_mask_data = pkgutil.get_data(__name__, "resources/templates/hud_mask.png")
print(_hud_mask_data)
image = Image.open(io.BytesIO(_hud_mask_data))
image_data = cv2.cvtColor(np.asarray(image), cv2.COLOR_RGB2GRAY)
HUD_MASK = cv2.threshold(image_data, 1, 255, cv2.THRESH_BINARY)[1]


def clean_img(inp_img: np.ndarray, black_thresh: int = 14) -> np.ndarray:
    img = inp_img[:, :, :]
    if img.shape[0] == HUD_MASK.shape[0] and img.shape[1] == HUD_MASK.shape[1]:
        img = cv2.bitwise_and(img, img, mask=HUD_MASK)
    # In order to not filter out highlighted items, change their color to black
    highlight_mask = color_filter(img, COLORS["item_highlight"])[0]
    img[highlight_mask > 0] = (0, 0, 0)
    img = erode_to_black(img, black_thresh)
    return img


def crop_text_clusters(inp_img: np.ndarray, padding_y: int = 5) -> list[ItemText]:
    start = time.time()
    cleaned_img = clean_img(inp_img)
    debug_str = f" | clean: {time.time() - start}"
    # Cluster item names
    start = time.time()
    item_clusters = []
    for key in ITEM_COLORS:
        _, filtered_img = color_filter(cleaned_img, COLORS[key])
        filtered_img_gray = cv2.cvtColor(filtered_img, cv2.COLOR_BGR2GRAY)
        blured_img = np.clip(cv2.GaussianBlur(
            filtered_img_gray, GAUS_FILTER, cv2.BORDER_DEFAULT), 0, 255)
        contours = cv2.findContours(
            blured_img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        contours = contours[0] if len(contours) == 2 else contours[1]
        for cntr in contours:
            x, y, w, h = cv2.boundingRect(cntr)
            expected_height = 1 if (
                EXPECTED_HEIGHT_RANGE[0] < h < EXPECTED_HEIGHT_RANGE[1]) else 0
            # increase height a bit to make sure we have the full item name in the cluster
            y = y - padding_y if y > padding_y else 0
            h += padding_y * 2
            cropped_item = filtered_img[y:y+h, x:x+w]
            # save most likely item drop contours
            avg = int(np.average(filtered_img_gray[y:y+h, x:x+w]))
            contains_black = True if np.min(cropped_item) < 14 else False
            expected_width = True if (
                EXPECTED_WIDTH_RANGE[0] < w < EXPECTED_WIDTH_RANGE[1]) else False
            mostly_dark = True if 4 < avg < 25 else False
            if contains_black and mostly_dark and expected_height and expected_width:
                # double-check item color
                color_averages = []
                for key2 in ITEM_COLORS:
                    _, extracted_img = color_filter(cropped_item, COLORS[key2])
                    extr_avg = np.average(cv2.cvtColor(
                        extracted_img, cv2.COLOR_BGR2GRAY))
                    color_averages.append(extr_avg)
                max_idx = color_averages.index(max(color_averages))
                if key == ITEM_COLORS[max_idx]:
                    item_clusters.append(ItemText(
                        color=key,
                        quality=QUALITY_COLOR_MAP[key],
                        roi=[x, y, w, h],
                        data=cropped_item,
                        clean_img=cleaned_img[y:y+h, x:x+w]
                    ))
    debug_str += f" | cluster: {time.time() - start}"
    cluster_images = [key["clean_img"] for key in item_clusters]
    results = image_to_text(cluster_images, fast=True, psm=7)
    for count, cluster in enumerate(item_clusters):
        setattr(cluster, "ocr_result", results[count])
    return item_clusters


def get_hovered_item(inp_img: np.ndarray, all_results: bool = False, inventory_side: str = "right") -> ItemText:
    """
    Crops visible item description boxes / tooltips
    :inp_img: image from hover over item of interest.
    :param all_results: whether to return all possible results (True) or the first result (False)
    :inventory_side: enter either "left" for stash/vendor region or "right" for user inventory region
    """
    results = []
    black_mask, _ = color_filter(inp_img, COLORS["black"])
    contours = cv2.findContours(
        black_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours = contours[0] if len(contours) == 2 else contours[1]
    for cntr in contours:
        x, y, w, h = cv2.boundingRect(cntr)
        cropped_item = inp_img[y:y+h, x:x+w]
        avg = np.average(cv2.cvtColor(cropped_item, cv2.COLOR_BGR2GRAY))
        mostly_dark = True if 0 < avg < 20 else False
        contains_black = True if np.min(cropped_item) < 14 else False
        contains_white = True if np.max(cropped_item) > 250 else False
        contains_orange = False
        if not contains_white:
            # check for orange (like key of destruction, etc.)
            orange_mask, _ = color_filter(cropped_item, COLORS["orange"])
            contains_orange = np.min(orange_mask) > 0
        expected_height = True if (
            BOX_EXPECTED_HEIGHT_RANGE[0] < h < BOX_EXPECTED_HEIGHT_RANGE[1]) else False
        expected_width = True if (
            BOX_EXPECTED_WIDTH_RANGE[0] < w < BOX_EXPECTED_WIDTH_RANGE[1]) else False
        box2 = UI_ROI[f"{inventory_side}_inventory"]
        # padded height because footer isn't included in contour
        overlaps_inventory = False if (
            x+w < box2[0] or box2[0]+box2[2] < x or y+h+28+10 < box2[1] or box2[1]+box2[3] < y) else True
        if contains_black and (contains_white or contains_orange) and mostly_dark and expected_height and expected_width and overlaps_inventory:
            footer_height_max = (720 - (y + h)) if (y + h + 35) > 720 else 35
            found_footer = TemplateFinder().search(
                ["TO_TOOLTIP"], inp_img, threshold=0.8, roi=[x, y+h, w, footer_height_max]).valid
            if found_footer:
                ocr_result = image_to_text(cropped_item, psm=6)[0]
                results.append(ItemText(
                    color="black",
                    roi=[x, y, w, h],
                    data=cropped_item,
                    ocr_result=ocr_result
                ))
                if not all_results:
                    break
    return results
