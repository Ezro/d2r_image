import concurrent.futures
import copy
from typing import Union
import cv2
from dataclasses import dataclass
import io
import numpy as np
from PIL import Image
from pkg_resources import resource_listdir
import pkgutil
from d2r_image.data_models import ScreenObject
from d2r_image.utils.misc import cut_roi, alpha_to_mask


@dataclass
class TemplateMatch:
    name: str = None
    score: float = -1.0
    center: tuple[float, float] = None
    region: list[float] = None
    valid: bool = False


executor = concurrent.futures.ThreadPoolExecutor()
IMAGE_BY_REF_NAME = {}
pkg_paths = resource_listdir(__name__, 'resources/screen_objects')
for path in pkg_paths:
    for nested_path in resource_listdir(__name__, f'resources/screen_objects/{path}'):
        if nested_path is None:
            continue
        if nested_path.endswith('.png'):
            image_bytes = pkgutil.get_data(__name__, f"resources/screen_objects/{path}/{nested_path}")
            image = Image.open(io.BytesIO(image_bytes))
            image_data = cv2.resize(np.asarray(image), None, fx=1.0, fy=1.0, interpolation=cv2.INTER_NEAREST)
            IMAGE_BY_REF_NAME[nested_path.replace('.png', '').upper()] = {
                'image': image,
                'imageData': cv2.cvtColor(image_data, cv2.COLOR_RGBA2BGR),
                'grayscaleImageData': cv2.cvtColor(image_data, cv2.COLOR_BGRA2GRAY),
                'mask': alpha_to_mask(image_data)
            }


def detect_screen_object(
    screen_object: ScreenObject,
    image: np.ndarray
) -> Union[list[list[float]], None]:
    """
    Search for a template in an image
    :param screen_object: A list of cv2 images
    :param image: Image in which the template will be searched
    :return: Returns a list of rects (x, y, w, h) or None
    """
    refs = []
    for ref in screen_object.refs:
        if ref.upper() in IMAGE_BY_REF_NAME:
            refs.append(IMAGE_BY_REF_NAME[ref.upper()])
    rx, ry, rw, rh = screen_object.roi if screen_object.roi else [0, 0, image.shape[1], image.shape[0]] 
    cropped_image = cut_roi(image, (rx, ry, rw, rh))
    templates, templates_gray, masks = parse_ref(
        refs,
        screen_object.use_grayscale)
    future_list = []
    # cv2.imshow('cropped', cropped_image)
    # cv2.waitKey()
    for count, template in enumerate(templates):
        future = executor.submit(
            match_template,
            np.asarray(template),
            templates_gray[count] if templates_gray else None,
            cropped_image,
            screen_object.use_grayscale,
            masks[count],
            screen_object.threshold,
            rx,
            ry)
        future_list.append(future)
    rects = []
    for i in range(len(future_list)):
        return_value = future_list[i].result()
        if return_value:
            for matching_rect in return_value:
                rects.append(matching_rect)
    consolidated_rects = consolidate_overlapping_rects(rects)
    rects = []
    for rect in consolidated_rects:
        rects.append(rect)
    return rects


def parse_ref(refs, use_grayscale):
    templates = []
    templates_gray = None
    masks = []
    for ref in refs:
        templates.append(ref['imageData'])
        if use_grayscale:
            if not templates_gray:
                templates_gray = []
            templates_gray.append(ref['grayscaleImageData'])
        masks.append(ref['mask'])
    return templates, templates_gray, masks


def match_template(
        template,
        template_gray,
        image,
        use_grayscale,
        mask,
        threshold,
        rx,
        ry):
    if image.shape[0] > template.shape[0] and image.shape[1] > template.shape[1]:
        if use_grayscale:
            image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            template = template_gray
        res = cv2.matchTemplate(
            image,
            template,
            cv2.TM_CCOEFF_NORMED,
            mask=mask)
        np.nan_to_num(res, copy=False, nan=0.0, posinf=0.0, neginf=0.0)
        template_matches = None
        (yCoords, xCoords) = np.where(res >= threshold)
        for (x, y) in zip(xCoords, yCoords):
            if not template_matches:
                template_matches = []
            rect = [int(x + rx), int(y + ry), template.shape[1], template.shape[0]]
            template_matches.append(rect)
        return template_matches
    return None


def consolidate_overlapping_rects(rects):
    rects_to_return = copy.deepcopy(rects)
    rects_to_remove = []
    for i in range(len(rects_to_return)):
        if rects[i] in rects_to_remove:
            continue
        (x, y, w, h) = rects[i]
        for j in range(i+1, len(rects)):
            (n_x, n_y, n_w, n_h) = rects[j]
            if x < n_x + n_w and\
                x + w > n_x and\
                    y < n_y + n_h and\
                        y + h > n_y:
                        if rects[j] not in rects_to_remove:
                            if (x < n_x and x + w - n_x > 3) or\
                                (x > n_x and n_x + n_w - x > 3):
                                rects_to_remove.append(rects[j])
    for rect in rects_to_remove:
        rects_to_return.remove(rect)
    return rects_to_return