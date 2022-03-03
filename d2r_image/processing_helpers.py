import pkgutil
from typing import Union
import cv2
import io
import numpy as np
from PIL import Image
import re
import time
from d2r_image.data_models import D2Item, ItemQuality, ItemQualityKeyword, ItemText
from d2r_image.ocr import image_to_text
from d2r_image.processing_data import Runeword
import d2r_image.d2data_lookup as d2data_lookup
from d2r_image.processing_data import COLORS, EXPECTED_HEIGHT_RANGE, EXPECTED_WIDTH_RANGE, GAUS_FILTER, ITEM_COLORS, QUALITY_COLOR_MAP, UI_ROI, Runeword
from d2r_image.utils.misc import color_filter, erode_to_black


_hud_mask_data = pkgutil.get_data(__name__, "resources/templates/hud_mask.png")
image = Image.open(io.BytesIO(_hud_mask_data))
image_data = cv2.cvtColor(np.asarray(image), cv2.COLOR_RGB2GRAY)
HUD_MASK = cv2.threshold(image_data, 1, 255, cv2.THRESH_BINARY)[1]
gold_regex = re.compile(r'(^[0-9]+)\sGOLD')


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


def clean_img(inp_img: np.ndarray, black_thresh: int = 14) -> np.ndarray:
    img = inp_img[:, :, :]
    if img.shape[0] == HUD_MASK.shape[0] and img.shape[1] == HUD_MASK.shape[1]:
        img = cv2.bitwise_and(img, img, mask=HUD_MASK)
    # In order to not filter out highlighted items, change their color to black
    highlight_mask = color_filter(img, COLORS["item_highlight"])[0]
    img[highlight_mask > 0] = (0, 0, 0)
    img = erode_to_black(img, black_thresh)
    return img


def crop_result_is_loading_screen(crop_result: list[ItemText]):
    for crop in crop_result:
        if crop.color != 'gold':
            return
        if crop.ocr_result and crop.ocr_result.text == 'LOADING':
            return True
    return False


def get_items_by_quality(crop_result):
    items_by_quality = {}
    for quality in ItemQuality:
        items_by_quality[quality.value] = []
    for item in crop_result:
        quality = None
        if item.quality.value == ItemQuality.Orange.value:
            is_rune = 'RUNE' in item.ocr_result.text
            if is_rune:
                quality = ItemQuality.Rune
            else:
                quality = ItemQuality.Crafted
        elif item.quality.value == ItemQuality.Unique.value:
            is_runeword = False
            try:
                Runeword(item.ocr_result.text)
                is_runeword = True
            except:
                pass
            quality = ItemQuality.Runeword if is_runeword else item.quality
        elif item.quality.value == ItemQuality.Gray.value:
            quality = ItemQuality.Gray
        else:
            quality = item.quality
        items_by_quality[quality.value].append({
            'quality': quality,
            'x': item.roi[0],
            'y': item.roi[1],
            'w': item.roi[2],
            'h': item.roi[3],
            'text': item.ocr_result.text
        })
    return items_by_quality


def consolidate_clusters(items_by_quality):
    if len(items_by_quality) == 0:
        return
    cco_start = time.time()
    consolidate_overlapping_names(items_by_quality)
    cco_end = time.time()
    cco = round(cco_end-cco_start, 2)
    ccr_start = time.time()
    consolidate_rares(items_by_quality)
    ccr_end = time.time()
    ccr = round(ccr_end-ccr_start, 2)
    ccs_start = time.time()
    consolidate_quality(
        items_by_quality[ItemQuality.Set.value],
        items_by_quality[ItemQuality.Set.value])
    ccs_end = time.time()
    ccs = round(ccs_end-ccs_start, 2)
    ccu_start = time.time()
    consolidate_quality(
        items_by_quality[ItemQuality.Unique.value],
        items_by_quality[ItemQuality.Unique.value])
    ccu_end = time.time()
    ccu = round(ccu_end-ccu_start, 2)
    ccrw_start = time.time()
    consolidate_quality(
        items_by_quality[ItemQuality.Runeword.value],
        items_by_quality[ItemQuality.Gray.value])
    ccrw_end = time.time()
    ccrw = round(ccrw_end-ccrw_start, 2)
    # print(f'CCO: {cco}\tCCR: {ccr}\tCCS: {ccs}\tCCU: {ccu}\tCCRW: {ccrw}')


def consolidate_overlapping_names(items_by_quality):
    items_to_remove = {}
    for quality in items_by_quality:
        for item in items_by_quality[quality]:
            overlapping_item = None
            for item_to_check in items_by_quality[quality]:
                if item == item_to_check or abs(item['y'] - item_to_check['y']) > 3:
                    continue
                if quality in items_to_remove:
                    if item in items_to_remove[quality] or item_to_check in items_to_remove[quality]:
                        continue
                if item['x'] < item_to_check['x'] + item_to_check['w'] and\
                    item['x'] + item['w'] > item_to_check['x'] and\
                        item['y'] < item_to_check['y'] + item_to_check['h'] and\
                            item['y'] + item['h'] > item_to_check['y']:
                            overlapping_item = item_to_check
                            break
            if overlapping_item:
                first_item = item if item['x'] < overlapping_item['x'] else overlapping_item
                second_item = item if first_item == overlapping_item else overlapping_item
                first_item_text = first_item['text'].strip().replace('\'', '').replace(' ', '')
                second_item_text = second_item['text'].strip().replace('\'', '').replace(' ', '')
                new_text = f"{first_item_text}\' {second_item_text}"
                if quality == ItemQuality.Set.value:
                    if not d2data_lookup.find_set_item_by_name(new_text):
                        break
                elif quality == ItemQuality.Unique.value:
                    if not d2data_lookup.find_unique_item_by_name(new_text):
                        break
                first_item['text'] = new_text
                first_item['name'] = new_text
                first_item['x'] = first_item['x'] if second_item['x'] > first_item['x'] else second_item['x']
                first_item['y'] = first_item['y'] if second_item['y'] > first_item['y'] else second_item['y']
                first_item['w'] = second_item['x'] + second_item['w'] - first_item['x']
                first_item['h'] = first_item['h']
                if quality not in items_to_remove:
                    items_to_remove[quality] = []
                items_to_remove[quality].append(second_item)
    for quality in items_to_remove:
        for item in items_to_remove[quality]:
            items_by_quality[quality].remove(item)


def consolidate_rares(items_by_quality):
    for item in items_by_quality[ItemQuality.Rare.value]:
        closest_dist = 99999
        closest_base = None
        d2data_base = None
        if not d2data_lookup.is_base(item['text']):
            for base in items_by_quality[ItemQuality.Rare.value]:
                if d2data_lookup.is_base(base['text']):
                    base_item = d2data_lookup.get_base(base['text'])
                    dist = round(calculate_distance(
                        item['x'],
                        item['y'],
                        base['x'],
                        base['y']
                        ), 0)
                    if dist < closest_dist:
                        closest_dist = dist
                        closest_base = base
                        d2data_base = base_item
            if not closest_base:
                return
            item['x'] = item['x'] if closest_base['x'] > item['x'] else closest_base['x']
            item['y'] = item['y'] if closest_base['y'] > item['y'] else closest_base['y']
            item['w'] = item['w'] if closest_base['w'] < item['w'] else closest_base['w']
            item['h'] = item['h'] + closest_base['h']
            item['base'] = d2data_base
            item['item'] = d2data_base
            item['identified'] = True
            items_by_quality[ItemQuality.Rare.value].remove(closest_base)


def consolidate_quality(quality_items, potential_bases):
    bases_to_remove = []
    for item in quality_items:
        if not d2data_lookup.is_base(item['text']):
            # result = d2data_lookup.find_item_by_display_name(item['text'])
            result = d2data_lookup.find_item_by_display_name_and_quality(item['text'], item['quality'])
            if not result:
                continue
            closest_dist = 99999
            closest_base = None
            for base in potential_bases:
                if base['y'] > item['y'] and d2data_lookup.is_base(base['text']):
                    dist = round(calculate_distance(
                        item['x'],
                        item['y'],
                        base['x'],
                        base['y']
                        ), 0)
                    if dist < closest_dist:
                        closest_dist = dist
                        closest_base = base
            if not closest_base:
                continue
            item['x'] = item['x'] if closest_base['x'] > item['x'] else closest_base['x']
            item['y'] = item['y'] if closest_base['y'] > item['y'] else closest_base['y']
            item['w'] = item['w'] if closest_base['w'] < item['w'] else closest_base['w']
            item['h'] = item['h'] + closest_base['h']
            item['item'] = result
            item['base'] = d2data_lookup.get_base(closest_base['text'])
            item['identified'] = True
            bases_to_remove.append(closest_base)
    for base_to_remove in bases_to_remove:
        potential_bases.remove(base_to_remove)


def find_base_and_remove_items_without_a_base(items_by_quality) -> dict:
    items_to_remove = {}
    gray_normal_magic_removed = {}
    items_to_add = {}
    resolved_runewords = []
    for quality in items_by_quality:
        if quality in [ItemQuality.Gray.value, ItemQuality.Normal.value, ItemQuality.Magic]:
            gray_normal_magic_removed.update(set_gray_and_normal_and_magic_base_items(items_by_quality))
        for item in items_by_quality[quality]:
            if 'base' not in item:
                if quality == ItemQuality.Magic.value:
                    base = d2data_lookup.get_base(item['text'])
                    if base:
                        item['base'] = base
                elif quality == ItemQuality.Rune.value:
                    if d2data_lookup.is_rune(item['text']):
                        item['base'] = d2data_lookup.get_rune(item['text'])
                        item['item'] = d2data_lookup.get_rune(item['text'])
                        item['identified'] = True
                elif d2data_lookup.is_base(item['text']):
                    item['base'] = d2data_lookup.get_base(item['text'])
                else:
                    if quality not in items_to_remove:
                        items_to_remove[quality] = []
                    items_to_remove[quality].append(item)
    for quality in items_to_remove:
        for item in items_to_remove[quality]:
            if quality == ItemQuality.Unique.value:
                for unique_item in items_by_quality[quality]:
                    if 'item' not in unique_item and 'base' in unique_item and 'uniques' in unique_item['base']:
                        closest_dist = 99999
                        closest_base = None
                        closest_unique_name = None
                        for possible_unique in unique_item['base']['uniques']:
                            normalized_name = possible_unique.replace('_', ' ').upper()
                            if normalized_name in item['text']:
                                dist = round(calculate_distance(
                                    item['x'],
                                    item['y'],
                                    unique_item['x'],
                                    unique_item['y']
                                    ), 0)
                                if dist < closest_dist:
                                    closest_dist = dist
                                    closest_base = unique_item
                                    closest_unique_name = normalized_name
                        if  closest_base:
                            unique_name_width = len(closest_unique_name) * 11
                            offset = item['text'].find(closest_unique_name) * 11
                            unique_item['x'] = item['x'] + offset
                            unique_item['y'] -= item['h']
                            unique_item['w'] = unique_name_width if unique_name_width > item['w'] else item['w'] if item['w'] < unique_name_width * 1.4 else unique_name_width
                            unique_item['h'] += item['h']
                            unique_item['text'] = closest_unique_name
                            unique_item['item'] = d2data_lookup.find_unique_item_by_name(closest_unique_name)
                            unique_item['identified'] = True
            elif quality == ItemQuality.Runeword.value:
                if 'item' not in item:
                    closest_dist = 99999
                    closest_base = None
                    for possible_base in items_by_quality[ItemQuality.Gray.value]:
                        dist = round(calculate_distance(
                            item['x'],
                            item['y'],
                            possible_base['x'],
                            possible_base['y']
                        ), 0)
                        if dist < closest_dist:
                            closest_dist = dist
                            closest_base = possible_base
                    if closest_base:
                        closest_base['quality'] = ItemQuality.Runeword
                        closest_base['name'] = item['text']
                        closest_base['x'] = item['x'] if item['x'] < closest_base['x'] else closest_base['x']
                        closest_base['y'] = item['y']
                        closest_base['w'] = item['w'] if item['w'] > closest_base['w'] else closest_base['w']
                        closest_base['h'] += item['h']
                        closest_base['item'] = {}
                        closest_base['identified'] = True
                        if quality not in items_to_add:
                            items_to_add[quality] = []
                        items_to_add[quality].append(closest_base)
                        items_by_quality[ItemQuality.Gray.value].remove(closest_base)
                        resolved_runewords.append(item)
            items_by_quality[quality].remove(item)
    for quality in items_to_add:
        if quality not in items_by_quality:
            items_by_quality[quality] = []
        for item in items_to_add[quality]:
            items_by_quality[quality].append(item)
    for runeword in resolved_runewords:
        if runeword in items_to_remove[ItemQuality.Runeword.value]:
            items_to_remove[ItemQuality.Runeword.value].remove(runeword)
    for quality in gray_normal_magic_removed:
        for item in gray_normal_magic_removed[quality]:
            if item['quality'].value not in items_to_remove:
                items_to_remove[item['quality'].value] = []
            items_to_remove[item['quality'].value].append(item)
    # items_removed = items_to_remove.update(gray_normal_magic_removed)
    return items_to_remove


def get_normalized_normal_gray_item_text(item_text):
    found_keyword_text = None
    if item_text.startswith('OW QUALITY'):
        item_text = item_text.replace('OW QUALITY', ItemQualityKeyword.LowQuality.value)
    if ItemQualityKeyword.LowQuality.value in item_text:
        found_keyword_text = ItemQualityKeyword.LowQuality.value
    elif ItemQualityKeyword.Cracked.value in item_text:
        found_keyword_text = ItemQualityKeyword.Cracked.value
    elif ItemQualityKeyword.Crude.value in item_text:
        found_keyword_text = ItemQualityKeyword.Crude.value
    elif ItemQualityKeyword.Damaged.value in item_text:
        found_keyword_text = ItemQualityKeyword.Damaged.value
    elif ItemQualityKeyword.Superior.value in item_text:
        found_keyword_text = ItemQualityKeyword.Superior.value
    if found_keyword_text:
        return ItemQualityKeyword(found_keyword_text), item_text.replace(f'{found_keyword_text} ', '')
    return None, item_text


def set_gray_and_normal_and_magic_base_items(items_by_quality):
    items_to_remove = {
    }
    for quality in items_by_quality:
        if quality in [ItemQuality.Gray.value, ItemQuality.Normal.value]:
            for item in items_by_quality[quality]:
                quality_keyword, normalized_text = get_normalized_normal_gray_item_text(item['text'])
                result = d2data_lookup.get_base(normalized_text)
                if result:
                    item['base'] = result
                    item['item'] = result
                    item['identified'] = True
                    if quality_keyword:
                        item['qualityKeyword'] = quality_keyword
                else:
                    gold_match = gold_regex.search(item['text'])
                    if gold_match:
                        item['base'] = d2data_lookup.get_consumable('GOLD')
                        item['amount'] = gold_match.group(1)
                    elif d2data_lookup.is_consumable(item['text']):
                        item['base'] = d2data_lookup.get_consumable(item['text'])
                    elif d2data_lookup.is_gem(item['text']):
                        item['base'] = d2data_lookup.get_gem(item['text'])
                    else:
                        if quality not in items_to_remove:
                            items_to_remove[quality] = []
                        items_to_remove[quality].append(item)
        elif quality == ItemQuality.Magic.value:
            for item in items_by_quality[quality]:
                base = d2data_lookup.find_base_item_from_magic_item_text(item['text'])
                if base:
                    item['base'] = base
                    if len(item['text'].lower().replace(base['display_name'].lower(), '').replace(' ', '')) > 0:
                        item['item'] = base
                        item['identified'] = True
                else:
                    if quality not in items_to_remove:
                        items_to_remove[quality] = []
                    items_to_remove[quality].append(item)
    for quality in items_to_remove:
        for item in items_to_remove[quality]:
            items_by_quality[quality].remove(item)
    return items_to_remove


def set_set_and_unique_base_items(items_by_quality):
    for quality in items_by_quality:
        for item in items_by_quality[quality]:
            if 'item' in item:
                continue
            item['identified'] = False
            if quality == ItemQuality.Unique.value:
                if len(item['base']['uniques']) == 1:
                    unique_name = item['base']['uniques'][0].replace('_', ' ').upper()
                    item['item'] = d2data_lookup.find_unique_item_by_name(unique_name, True)
                else:
                    item['uniqueItems'] = []
                    for unique_item in item['base']['uniques']:
                        unique_name = unique_item.replace('_', ' ').upper()
                        item['uniqueItems'].append(d2data_lookup.find_unique_item_by_name(unique_name, True))
            elif quality == ItemQuality.Set.value:
                if len(item['base']['sets']) == 1:
                    set_name = item['base']['sets'][0].replace('_', ' ').upper()
                    item['item'] = d2data_lookup.find_set_item_by_name(set_name, ItemQuality.Set)
                else:
                    item['setItems'] = []
                    for unique_item in item['base']['sets']:
                        unique_name = unique_item.replace('_', ' ').upper()
                        item['setItems'].append(d2data_lookup.find_set_item_by_name(unique_name, True))


def build_d2_items(items_by_quality: dict) -> Union[list[D2Item], None]:
    d2_items = None
    for quality in items_by_quality:
        for item in items_by_quality[quality]:
            new_item = D2Item(
                boundingBox= {
                    'x': item['x'],
                    'y': item['y'],
                    'w': item['w'],
                    'h': item['h'],
                },
                name=item['name'] if 'name' in item else item['text'],
                quality=item['quality'].value,
                type=item['base']['type'],
                identified=item['identified'],
                amount=item['amount'] if item['base']['type'] == 'gold' else None,
                baseItem=item['base'],
                item=item['item'] if 'item' in item else None,
                uniqueItems=item['uniqueItems'] if 'uniqueItems' in item else None,
                setItems=item['setItems'] if 'setItems' in item else None,
                itemModifiers=None
            )
            if d2_items is None:
                d2_items = []
            d2_items.append(new_item)
    return d2_items


def calculate_distance(x1, y1, x2, y2):
    return ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** .5
