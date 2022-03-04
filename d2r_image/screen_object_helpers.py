import concurrent.futures
import cv2
from dataclasses import dataclass
import io
import numpy as np
from PIL import Image
from pkg_resources import resource_listdir
import pkgutil
from d2r_image.data_models import ScreenObject
from d2r_image.utils.misc import roi_center, alpha_to_mask


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
            print(nested_path)
            continue
        if nested_path.endswith('.png'):
            image_bytes = pkgutil.get_data(__name__, f"resources/screen_objects/{path}/{nested_path}")
            image = Image.open(io.BytesIO(image_bytes))
            image_data = cv2.resize(np.asarray(image), None, fx=1.0, fy=1.0, interpolation=cv2.INTER_NEAREST)
            # image_data = cv2.cvtColor(np.asarray(image), cv2.COLOR_RGB2BGR)
            # image_data = cv2.cvtColor(np.asarray(image), cv2.COLOR_RGB2GRAY)
            IMAGE_BY_REF_NAME[nested_path.replace('.png', '').upper()] = {
                'image': image,
                'imageData': cv2.cvtColor(image_data, cv2.COLOR_BGRA2BGR),
                'grayscaleImageData': cv2.cvtColor(image_data, cv2.COLOR_BGRA2GRAY),
                'mask': alpha_to_mask(image_data)
            }


def detect_screen_object(screen_object: ScreenObject, image: np.ndarray = None) -> TemplateMatch:
    return search(
        screen_object,
        image,
        threshold=screen_object.threshold,
        best_match=screen_object.best_match,
        use_grayscale=screen_object.use_grayscale)


def search(
    screen_object: ScreenObject,
    image: np.ndarray,
    threshold: float = 0.68,
    roi: list[float] = None,
    best_match: bool = False,
    use_grayscale: bool = False,
) -> TemplateMatch:
    """
    Search for a template in an image
    :param refs: A list of cv2 images
    :param inp_img: Image in which the template will be searched
    :param threshold: Threshold which determines if a template is found or not
    :param roi: Region of Interest of the inp_img to restrict search area. Format [left, top, width, height]
    :param normalize_monitor: If True will return positions in monitor coordinates. Otherwise in coordinates of the input image.
    :param best_match: If list input, will search for list of templates by best match. Default behavior is first match.
    :param use_grayscale: Use grayscale template matching for speed up
    :return: Returns a TempalteMatch object with a valid flag
    """
    refs = []
    for ref in screen_object.refs:
        if ref.upper() in IMAGE_BY_REF_NAME:
            refs.append(IMAGE_BY_REF_NAME[ref.upper()])
    if roi is None:
        # if no roi is provided roi = full inp_img
        roi = [0, 0, image.shape[1], image.shape[0]]
    rx, ry, rw, rh = roi
    image = image[ry:ry + rh, rx:rx + rw]
    templates, templates_gray, scales, masks = parse_ref(
        refs,
        use_grayscale)
    scores = [0] * len(templates)
    ref_points = [(0, 0)] * len(templates)
    recs = [[0, 0, 0, 0]] * len(templates)
    future_list = []
    for count, template in enumerate(templates):
        scale = scales[count]
        if scale != 1:
            img: np.ndarray = cv2.resize(
                image, None, fx=scale, fy=scale, interpolation=cv2.INTER_NEAREST)
            rx *= scale
            ry *= scale
            rw *= scale
            rh *= scale
        else:
            img: np.ndarray = image
        future = executor.submit(
            match_template,
            np.asarray(template),
            templates_gray[count] if templates_gray else None,
            img,
            use_grayscale,
            masks[count],
            threshold,
            scales[count],
            rx,
            ry)
        future_list.append(future)
    for i in range(len(future_list)):
        return_value = future_list[i].result()
        if return_value:
            # Logger.debug(return_value)
            scores[i] = return_value[0]
            ref_points[i] = return_value[1]
            recs[i] = return_value[2]
            if not best_match:
                break
        # else:
        #     Logger.error(f'{ref[i]} not found')
    template_match = TemplateMatch()
    if len(scores) > 0 and max(scores) > 0:
        idx = scores.index(max(scores))
        try:
            template_match.name = names[idx]
        except:
            pass
        template_match.center = ref_points[idx]
        template_match.score = scores[idx]
        template_match.region = recs[idx]
        template_match.valid = True
    return template_match


def parse_ref(refs, use_grayscale):
    templates = []
    templates_gray = None
    scales = []
    masks = []
    for ref in refs:
        templates.append(ref['imageData'])
        if use_grayscale:
            if not templates_gray:
                templates_gray = []
            templates_gray.append(ref['grayscaleImageData'])
        scales.append(1.0)
        masks.append(ref['mask'])
    masks = [None] * len(refs)
    return templates, templates_gray, scales, masks


def match_template(
        template,
        template_gray,
        image,
        use_grayscale,
        mask,
        threshold,
        scale,
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
        _, max_val, _, max_pos = cv2.minMaxLoc(res)
        if max_val > threshold:
            rec = [int((max_pos[0] + rx) // scale), int((max_pos[1] + ry) // scale),
                    int(template.shape[1] // scale), int(template.shape[0] // scale)]
            ref_point = roi_center(rec)
            return [max_val, ref_point, rec]
    return None