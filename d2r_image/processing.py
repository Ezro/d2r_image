from typing import Tuple, Union
from charset_normalizer import detect
import cv2
import numpy as np
from d2r_image import d2data_lookup
from d2r_image.data_models import D2Item, D2ItemList, ItemQuality, ItemText, ScreenObject
from d2r_image.utils.misc import color_filter, cut_roi
# from d2r_image.template_finder import TemplateFinder
from d2r_image.ocr import image_to_text
from d2r_image.processing_data import BOX_EXPECTED_WIDTH_RANGE, BOX_EXPECTED_HEIGHT_RANGE, COLORS, UI_ROI
from d2r_image.processing_helpers import build_d2_items, crop_result_is_loading_screen, crop_text_clusters, get_items_by_quality, consolidate_clusters, find_base_and_remove_items_without_a_base, set_set_and_unique_base_items
from d2r_image.screen_object_helpers import detect_screen_object
from d2r_image.d2data_ref_lookup import BELT_MAP, CONSUMABLES, LEFT_INVENTORY_MAP, RIGHT_INVENTORY_MAP
import numpy as np


def get_screen_object(image: np.ndarray, screen_object: ScreenObject):
    return detect_screen_object(screen_object, image)


def get_ground_loot(image: np.ndarray) -> Union[list[D2Item], None]:
    crop_result = crop_text_clusters(image)
    if crop_result_is_loading_screen(crop_result):
        return None
    items_by_quality = get_items_by_quality(crop_result)
    consolidate_clusters(items_by_quality)
    items_removed = find_base_and_remove_items_without_a_base(items_by_quality)
    set_set_and_unique_base_items(items_by_quality)
    return build_d2_items(items_by_quality)


def get_hovered_item(image: np.ndarray, all_results: bool = False, inventory_side: str = "right") -> ItemText:
    """
    Crops visible item description boxes / tooltips
    :inp_img: image from hover over item of interest.
    :param all_results: whether to return all possible results (True) or the first result (False)
    :inventory_side: enter either "left" for stash/vendor region or "right" for user inventory region
    """
    return None
    # results = []
    # black_mask, _ = color_filter(image, COLORS["black"])
    # contours = cv2.findContours(
    #     black_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    # contours = contours[0] if len(contours) == 2 else contours[1]
    # for cntr in contours:
    #     x, y, w, h = cv2.boundingRect(cntr)
    #     cropped_item = image[y:y+h, x:x+w]
    #     avg = np.average(cv2.cvtColor(cropped_item, cv2.COLOR_BGR2GRAY))
    #     mostly_dark = True if 0 < avg < 20 else False
    #     contains_black = True if np.min(cropped_item) < 14 else False
    #     contains_white = True if np.max(cropped_item) > 250 else False
    #     contains_orange = False
    #     if not contains_white:
    #         # check for orange (like key of destruction, etc.)
    #         orange_mask, _ = color_filter(cropped_item, COLORS["orange"])
    #         contains_orange = np.min(orange_mask) > 0
    #     expected_height = True if (
    #         BOX_EXPECTED_HEIGHT_RANGE[0] < h < BOX_EXPECTED_HEIGHT_RANGE[1]) else False
    #     expected_width = True if (
    #         BOX_EXPECTED_WIDTH_RANGE[0] < w < BOX_EXPECTED_WIDTH_RANGE[1]) else False
    #     box2 = UI_ROI.leftInventory if inventory_side == 'left' else UI_ROI.rightInventory
    #     # padded height because footer isn't included in contour
    #     overlaps_inventory = False if (
    #         x+w < box2[0] or box2[0]+box2[2] < x or y+h+28+10 < box2[1] or box2[1]+box2[3] < y) else True
    #     if contains_black and (contains_white or contains_orange) and mostly_dark and expected_height and expected_width and overlaps_inventory:
    #         footer_height_max = (720 - (y + h)) if (y + h + 35) > 720 else 35
    #         found_footer = TemplateFinder().search(
    #             ["TO_TOOLTIP"], image, threshold=0.8, roi=[x, y+h, w, footer_height_max]).valid
    #         if found_footer:
    #             ocr_result = image_to_text(cropped_item, psm=6)[0]
    #             results.append(ItemText(
    #                 color="black",
    #                 roi=[x, y, w, h],
    #                 data=cropped_item,
    #                 ocr_result=ocr_result
    #             ))
    #             if not all_results:
    #                 break
    # return results


def get_npc_coords(image: np.ndarray, npc: ScreenObject) -> Tuple[int, int]:
    match = detect_screen_object(npc, image)
    return match


def find_items_by_name(image: np.ndarray, name: str) -> list[Tuple[int, int]]:
    return (0, 0)


def get_health(image: np.ndarray) -> float:
    health_img = cut_roi(image, UI_ROI.healthSlice)
    mask, _ = color_filter(health_img, COLORS["health_globe_red"])
    health_percentage = (float(np.sum(mask)) / mask.size) * (1/255.0) * 100
    mask, _ = color_filter(health_img, COLORS["health_globe_green"])
    health_percentage_green = (float(np.sum(mask)) / mask.size) * (1/255.0) * 100
    health = round(max(health_percentage, health_percentage_green), 2)
    return health


def get_mana(image: np.ndarray) -> float:
    mana_img = cut_roi(image, UI_ROI.manaSlice)
    mask, _ = color_filter(mana_img, COLORS["mana_globe"])
    mana_percentage = (float(np.sum(mask)) / mask.size) * (1/255.0) * 100
    return round(mana_percentage, 2)


def get_stamina(image: np.ndarray) -> float:
    return 0


def get_experience(image: np.ndarray) -> float:
    return 0


def get_merc_health(image: np.ndarray) -> float:
    merc_health_img = cut_roi(image, UI_ROI.mercHealthSlice)
    merc_health_img = cv2.cvtColor(merc_health_img, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(merc_health_img, 5, 255, cv2.THRESH_BINARY)
    merc_health_percentage = (float(np.sum(thresh)) / thresh.size) * (1/255.0) * 100
    return round(merc_health_percentage, 2)


def get_belt(image: np.ndarray) -> D2ItemList:
    belt = D2ItemList([
            None, None, None, None,
            None, None, None, None,
            None, None, None, None,
            None, None, None, None
    ])
    for consumable in BELT_MAP:
        belt_roi = [722, 560, 166, 156]
        rects = detect_screen_object(ScreenObject(refs=BELT_MAP[consumable], threshold=0.95, roi=belt_roi), image)
        if rects:
            for rect in rects:
                column = int((rect[0]-belt_roi[0]) / 40)
                row = abs(3-round((rect[1]-belt_roi[1]) / 40))
                slot_index = row * 4 + column
                quality = None
                type = None
                base_item = None
                item = None
                if consumable != 'EMPTY BELT SLOT':
                    quality=ItemQuality.Normal.value
                    base_item = d2data_lookup.get_consumable(consumable)
                    type=base_item['type']
                    item=base_item
                belt.items[slot_index] = D2Item(
                    boundingBox= {
                        'x': rect[0],
                        'y': rect[1],
                        'w': rect[2],
                        'h': rect[3],
                    },
                    name=consumable,
                    quality=quality,
                    type=type,
                    identified=True,
                    baseItem=base_item,
                    item=item,
                    amount=None,
                    uniqueItems=None,
                    setItems=None,
                    itemModifiers=None
                )
    return belt


def get_inventory(image: np.ndarray) -> D2ItemList:
    d2_item_list = D2ItemList([])
    d2data_maps = [LEFT_INVENTORY_MAP, RIGHT_INVENTORY_MAP]
    for i in range(len(d2data_maps)):
        map = d2data_maps[i]
        roi = UI_ROI.leftInventory if i == 1 else UI_ROI.rightInventory
        for item in map:
            threshold = 0.95 if item not in ['PERFECT AMETHYST', 'PERFECT SAPPHIRE'] else 0.99
            rects = detect_screen_object(ScreenObject(refs=map[item], threshold=threshold, roi=roi), image)
            if rects:
                for rect in rects:
                    quality=ItemQuality.Normal.value
                    base_item = d2data_lookup.get_by_name(item)
                    type=base_item['type']
                    d2_item_list.items.append(D2Item(
                        boundingBox= {
                            'x': rect[0],
                            'y': rect[1],
                            'w': rect[2],
                            'h': rect[3],
                        },
                        name=item,
                        quality=quality,
                        type=type,
                        identified=True,
                        baseItem=base_item,
                        item=base_item,
                        amount=None,
                        uniqueItems=None,
                        setItems=None,
                        itemModifiers=None
                    ))
    return d2_item_list